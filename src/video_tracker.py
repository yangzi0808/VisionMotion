"""
VisionMotion —— M3.3 视频逐帧追踪模块

本模块负责本项目第一次“视频 -> 时序坐标数据”的正式实现，严格按已验收的 M3.2 方案：

    打开视频
    -> 读取一帧
    -> detect_marker(frame)
    -> 记录 frame / time_s / 中心 / 面积
    -> 写 CSV
    -> 生成叠加可视化
    -> 读取下一帧
    -> 直到视频结束

本模块只做“测量与记录”：

    - 不做位移计算、不做毫米换算、不做振动频率、不做 FFT、不做 UI、不做自动报告
    - 不做平滑、不做插值、不做上一帧预测、不做 ROI 搜索、不做光流/卡尔曼/YOLO
    - 检测参数唯一来源是 src/marker_detector.py，
      本模块不重新定义 RED_LOWER_1 / RED_UPPER_1 / RED_LOWER_2 / RED_UPPER_2 /
      MORPH_KERNEL_SIZE / MIN_AREA

代码风格：普通函数 + 中文注释，不使用 class / 多线程 / 异步 / logging / pandas / scipy。
"""

import csv
import hashlib
import time
from pathlib import Path

import cv2
import numpy as np

from src.marker_detector import detect_marker

# ============================================================
# 常量
# ============================================================

# CSV 表头：第一行就是真正的表头，前面不加任何 metadata
CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]

# 叠加视频缩放倍数（0.5 倍，减小文件体积；只用于人工核查）
OVERLAY_SCALE = 0.5

# 叠加视频编码器候选：Windows 上 mp4v 一般可用，avc1 作为备选
OVERLAY_CODECS = ("mp4v", "avc1")

# 回退方案最多保存的代表性 PNG 数量
MAX_FALLBACK_PNGS = 5


# ============================================================
# 基础工具
# ============================================================


def compute_sha256(file_path):
    """
    计算文件的 SHA-256（只读，不会修改文件）。
    用于运行前 / 运行后对比原始视频是否被改动。
    """
    sha = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        while True:
            block = file_handle.read(1024 * 1024)
            if not block:
                break
            sha.update(block)
    return sha.hexdigest()


def save_png(path, image):
    """
    保存 PNG 图片。

    说明：Windows 上 cv2.imwrite 在含中文的路径下可能失败（本项目路径含中文），
    所以先用 cv2.imencode 编码，再把字节写入文件。
    """
    success, encoded = cv2.imencode(".png", image)
    if not success:
        return False
    encoded.tofile(str(path))
    return True


# ============================================================
# 视频读取
# ============================================================


def enable_orientation_auto(cap):
    """
    尝试显式开启 OpenCV 的自动方向处理（cv2.CAP_PROP_ORIENTATION_AUTO）。

    返回：
        True  —— 属性可用且已成功开启
        False —— 属性存在但开启失败
        None  —— 当前 OpenCV 构建不提供该属性

    注意：必须在读取第一帧之前调用；本模块不手工旋转画面，也不交换 x/y。
    """
    if not hasattr(cv2, "CAP_PROP_ORIENTATION_AUTO"):
        return None
    try:
        cap.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)
        value = cap.get(cv2.CAP_PROP_ORIENTATION_AUTO)
    except cv2.error:
        return False
    return value == 1


def open_video(video_path):
    """
    打开视频并读取基本信息。

    返回 (cap, video_info)；打开失败时返回 (None, None)。
    """
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None, None

    video_info = {}
    video_info["fps"] = float(cap.get(cv2.CAP_PROP_FPS))
    video_info["frame_count"] = int(round(cap.get(cv2.CAP_PROP_FRAME_COUNT)))

    # 文件内记录的旋转元数据（只读，用于报告，不用来手工旋转画面）
    if hasattr(cv2, "CAP_PROP_ORIENTATION_META"):
        video_info["orientation_meta"] = cap.get(cv2.CAP_PROP_ORIENTATION_META)
    else:
        video_info["orientation_meta"] = float("nan")

    # 必须在读取第一帧之前显式尝试开启自动方向处理
    video_info["orientation_auto"] = enable_orientation_auto(cap)

    return cap, video_info


def print_video_info(video_path, video_info, frame_shape):
    """
    打印视频基本信息，以及程序最终实际处理的画面宽度和高度。
    """
    height = frame_shape[0]
    width = frame_shape[1]

    print("视频文件：%s" % video_path)
    print("实际 FPS：%.6f（从当前视频文件读取，未硬编码）" % video_info["fps"])
    print("总帧数：%d（文件声明值）" % video_info["frame_count"])
    print("文件内旋转元数据：%.0f 度" % video_info["orientation_meta"])

    if video_info["orientation_auto"] is True:
        print("自动方向处理 CAP_PROP_ORIENTATION_AUTO：已开启")
    elif video_info["orientation_auto"] is False:
        print("自动方向处理 CAP_PROP_ORIENTATION_AUTO：属性存在但开启失败，"
              "画面方向可能不是显示方向")
    else:
        print("自动方向处理 CAP_PROP_ORIENTATION_AUTO：当前 OpenCV 构建不提供该属性，"
              "画面方向可能不是显示方向")

    print("程序实际处理的画面尺寸：宽 %d px，高 %d px" % (width, height))
    print("")


# ============================================================
# 叠加可视化
# ============================================================


def draw_tracking_frame(frame, frame_index, time_s, result, scale_x, scale_y):
    """
    在一个已经缩放好的画面副本上画追踪结果（不会修改原始帧）。

    检测成功：绿色外接矩形 + 中心点 + 中心坐标文字（坐标是原视频像素坐标）
    检测失败：只显示 DETECTION FAILED，不画任何虚假中心
    """
    overlay = frame.copy()

    # 左上角信息：帧号与时间
    cv2.putText(
        overlay,
        "frame=%d  t=%.3f s" % (frame_index, time_s),
        (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    if not result["success"]:
        cv2.putText(
            overlay,
            "DETECTION FAILED",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 0, 255),
            2,
            cv2.LINE_AA,
        )
        return overlay

    # 把原始像素坐标换算到缩放后的画面坐标
    bbox_x, bbox_y, bbox_w, bbox_h = result["bbox"]
    left = int(round(bbox_x * scale_x))
    top = int(round(bbox_y * scale_y))
    right = int(round((bbox_x + bbox_w) * scale_x))
    bottom = int(round((bbox_y + bbox_h) * scale_y))
    center = (
        int(round(result["cx"] * scale_x)),
        int(round(result["cy"] * scale_y)),
    )

    # 绿色外接矩形
    cv2.rectangle(overlay, (left, top), (right, bottom), (0, 255, 0), 2)

    # 中心点：圆圈 + 十字
    cv2.circle(overlay, center, 10, (0, 255, 0), 2)
    cv2.drawMarker(overlay, center, (255, 0, 0), cv2.MARKER_CROSS, 24, 2)

    # 中心坐标文字（使用原视频像素坐标，便于和 CSV 对照）
    cv2.putText(
        overlay,
        "center=(%.1f, %.1f) px" % (result["cx"], result["cy"]),
        (10, 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return overlay


def open_overlay_writer(overlay_path, fps, frame_size):
    """
    尝试打开叠加视频写入器，返回 (writer, codec_name)。
    所有候选编码器都失败时返回 (None, None)，由调用方走 PNG 回退方案。
    """
    width, height = frame_size
    if width <= 0 or height <= 0:
        return None, None

    for codec_name in OVERLAY_CODECS:
        fourcc = cv2.VideoWriter_fourcc(*codec_name)
        writer = cv2.VideoWriter(str(overlay_path), fourcc, fps, (width, height))
        if writer.isOpened():
            return writer, codec_name
        writer.release()

    return None, None


# ============================================================
# PNG 回退方案（VideoWriter 不可用时）
# ============================================================


def find_fastest_motion_frame(records):
    """
    找出“最快运动附近”的帧号。

    做法：只看相邻两帧都检测成功的情况，比较相邻帧之间的中心点距离，取最大者。
    说明：这里只是为了回退方案挑一张有代表性的画面，
          不输出位移序列，也不参与任何后续分析。
    最少需要两帧有效数据，否则返回 None。
    """
    fastest_frame = None
    fastest_distance = -1.0

    previous = None
    for record in records:
        if record["success"] and previous is not None:
            distance = float(
                np.hypot(record["cx"] - previous["cx"], record["cy"] - previous["cy"])
            )
            if distance > fastest_distance:
                fastest_distance = distance
                fastest_frame = record["frame"]
        if record["success"]:
            previous = record
        else:
            previous = None

    return fastest_frame


def find_blurriest_frame(sharpness_list):
    """
    找出“最模糊附近”的帧号：清晰度指标（拉普拉斯方差）最小的一帧。
    清晰度指标只在回退方案中使用，不写入 CSV。
    """
    if len(sharpness_list) == 0:
        return None
    return int(np.argmin(sharpness_list))


def read_frame_at(cap, frame_index):
    """
    把读取位置移动到指定帧号并读取一帧。失败返回 None。
    """
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    if not ret or frame is None:
        return None
    return frame


def save_fallback_frames(video_path, records, sharpness_list, result_dir,
                         file_stem, scale_x, scale_y):
    """
    VideoWriter 不可用时的回退方案：只保存少量代表性 PNG（最多 5 张）。

    选取：起始帧、中间帧、结束帧、最快运动附近的一帧、最模糊附近的一帧。
    这里会重新打开视频读取这些帧，不修改原始视频。
    """
    total = len(records)
    if total == 0:
        return []

    candidates = [
        ("start", 0),
        ("middle", total // 2),
        ("end", total - 1),
    ]

    fastest_frame = find_fastest_motion_frame(records)
    if fastest_frame is not None:
        candidates.append(("fastest_motion", fastest_frame))

    blurriest_frame = find_blurriest_frame(sharpness_list)
    if blurriest_frame is not None:
        candidates.append(("blurriest", blurriest_frame))

    # 去掉重复帧号，并限制总数
    selected = []
    used_frames = set()
    for tag, frame_index in candidates:
        if frame_index in used_frames:
            continue
        used_frames.add(frame_index)
        selected.append((tag, frame_index))
        if len(selected) >= MAX_FALLBACK_PNGS:
            break

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print("警告：回退方案无法重新打开视频，未保存 PNG")
        return []

    saved_paths = []
    for tag, frame_index in selected:
        frame = read_frame_at(cap, frame_index)
        if frame is None:
            print("警告：回退方案读取 frame=%d 失败，跳过" % frame_index)
            continue

        scaled_frame = cv2.resize(
            frame,
            (int(round(frame.shape[1] * OVERLAY_SCALE)),
             int(round(frame.shape[0] * OVERLAY_SCALE))),
            interpolation=cv2.INTER_AREA,
        )
        result = detect_marker(frame)
        time_s = records[frame_index]["time_s"]
        overlay = draw_tracking_frame(
            scaled_frame, frame_index, time_s, result, scale_x, scale_y
        )

        png_path = result_dir / ("%s_frame%04d_%s.png" % (file_stem, frame_index, tag))
        if save_png(png_path, overlay):
            saved_paths.append(png_path)
            print("已保存代表性 PNG（%s，frame=%d）：%s" % (tag, frame_index, png_path))
        else:
            print("警告：保存 PNG 失败：%s" % png_path)

    cap.release()
    return saved_paths


# ============================================================
# 逐帧追踪主流程
# ============================================================


def build_csv_row(frame_index, time_s, result):
    """
    构造一行 CSV 数据。

    检测成功：frame, time_s(6 位小数), x(2 位), y(2 位), area(1 位), True
    检测失败：frame, time_s(6 位小数), 空, 空, 空, False
    失败时绝不写 0 / -1 / nan / 字符串。
    """
    if result["success"]:
        return [
            frame_index,
            "%.6f" % time_s,
            "%.2f" % result["cx"],
            "%.2f" % result["cy"],
            "%.1f" % result["area"],
            "True",
        ]
    return [frame_index, "%.6f" % time_s, "", "", "", "False"]


def track_video(video_path, csv_path, overlay_path):
    """
    逐帧追踪主流程：读取完整视频 -> 每帧 detect_marker -> 写 CSV -> 生成可视化。

    返回统计字典；视频无法打开时返回 None。
    """
    video_path = Path(video_path)
    csv_path = Path(csv_path)
    overlay_path = Path(overlay_path)
    result_dir = overlay_path.parent

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)

    # 运行前记录原始视频指纹（只读，不修改原始视频）
    sha256_before = compute_sha256(video_path)

    start_time = time.perf_counter()

    cap, video_info = open_video(video_path)
    if cap is None:
        print("错误：视频无法打开：%s" % video_path)
        return None

    fps = video_info["fps"]
    if fps <= 0:
        print("错误：读取到的 FPS 非法（%.6f），停止处理" % fps)
        cap.release()
        return None

    # 先读第一帧，用于确定程序实际处理的画面尺寸（以及叠加视频尺寸）
    ret, first_frame = cap.read()
    if not ret or first_frame is None:
        print("错误：视频第一帧读取失败，停止处理")
        cap.release()
        return None

    print_video_info(video_path, video_info, first_frame.shape)

    height = first_frame.shape[0]
    width = first_frame.shape[1]

    # 叠加视频使用 0.5 倍缩放；宽高取偶数，避免编码器对奇数尺寸报错
    scaled_width = int(round(width * OVERLAY_SCALE))
    scaled_height = int(round(height * OVERLAY_SCALE))
    if scaled_width % 2 != 0:
        scaled_width -= 1
    if scaled_height % 2 != 0:
        scaled_height -= 1
    scale_x = scaled_width / float(width)
    scale_y = scaled_height / float(height)

    writer, codec_name = open_overlay_writer(
        overlay_path, fps, (scaled_width, scaled_height)
    )
    if writer is not None:
        print("叠加视频写入器已打开：%s（编码器 %s，尺寸 %d x %d，FPS %.6f）"
              % (overlay_path, codec_name, scaled_width, scaled_height, fps))
    else:
        print("警告：VideoWriter 无法打开，叠加视频不可用，改用代表性 PNG 回退方案")
    print("")

    # 逐帧处理：第一帧已经在上面读过，先处理它，再继续读后续帧
    records = []          # 每帧一条记录，用于统计与自检
    sharpness_list = []   # 每帧清晰度指标（只在回退方案中使用）
    detected_count = 0
    area_list = []
    current_frame = first_frame
    frame_index = 0

    csv_file = open(csv_path, "w", encoding="utf-8", newline="")
    csv_writer = csv.writer(csv_file, lineterminator="\n")
    csv_writer.writerow(CSV_FIELDNAMES)

    interrupted = False
    try:
        while True:
            # ---- 调用现有检测器（检测参数唯一来源：src/marker_detector.py）----
            result = detect_marker(current_frame)

            # ---- 时间轴：time_s = frame_index / fps（frame_index 从 0 开始）----
            time_s = frame_index / fps

            # ---- 写 CSV：每帧一行，检测失败也要写 ----
            csv_writer.writerow(build_csv_row(frame_index, time_s, result))

            record = {
                "frame": frame_index,
                "time_s": time_s,
                "success": bool(result["success"]),
            }
            if result["success"]:
                record["cx"] = result["cx"]
                record["cy"] = result["cy"]
                record["area"] = result["area"]
                detected_count += 1
                area_list.append(result["area"])
            records.append(record)

            # ---- 生成可视化 ----
            scaled_frame = cv2.resize(
                current_frame, (scaled_width, scaled_height),
                interpolation=cv2.INTER_AREA
            )
            if writer is not None:
                overlay = draw_tracking_frame(
                    scaled_frame, frame_index, time_s, result, scale_x, scale_y
                )
                writer.write(overlay)
            else:
                gray = cv2.cvtColor(scaled_frame, cv2.COLOR_BGR2GRAY)
                sharpness_list.append(float(cv2.Laplacian(gray, cv2.CV_64F).var()))

            # ---- 读取下一帧 ----
            ret, next_frame = cap.read()
            if not ret or next_frame is None:
                # 视频解码结束（ret=False）：正常结束，不因为单帧失败中断
                break
            frame_index += 1
            current_frame = next_frame

            if frame_index % 200 == 0:
                print("已处理 %d 帧 ..." % frame_index)
    except KeyboardInterrupt:
        interrupted = True
        print("")
        print("警告：收到中断信号，已处理的帧数据仍然保留在 CSV 与叠加视频中")
    finally:
        csv_file.close()
        cap.release()
        if writer is not None:
            writer.release()

    elapsed_seconds = time.perf_counter() - start_time

    # 回退方案：VideoWriter 不可用时保存少量代表性 PNG
    fallback_pngs = []
    if writer is None and len(records) > 0:
        file_stem = overlay_path.stem
        fallback_pngs = save_fallback_frames(
            video_path, records, sharpness_list, result_dir,
            file_stem, scale_x, scale_y
        )

    print("")
    print("CSV 已写入：%s" % csv_path)
    if writer is not None:
        print("叠加视频已写入：%s" % overlay_path)

    summary = {
        "video_path": video_path,
        "csv_path": csv_path,
        "overlay_path": overlay_path,
        "width": width,
        "height": height,
        "fps": fps,
        "declared_frame_count": video_info["frame_count"],
        "processed_frames": len(records),
        "detected_frames": detected_count,
        "missed_frames": len(records) - detected_count,
        "detection_rate": detected_count / float(len(records)) if records else 0.0,
        "longest_miss_run": compute_longest_miss_run(records),
        "area_min": min(area_list) if area_list else float("nan"),
        "area_median": float(np.median(area_list)) if area_list else float("nan"),
        "area_max": max(area_list) if area_list else float("nan"),
        "first_time_s": records[0]["time_s"] if records else float("nan"),
        "last_time_s": records[-1]["time_s"] if records else float("nan"),
        "elapsed_seconds": elapsed_seconds,
        "overlay_ok": writer is not None,
        "fallback_pngs": fallback_pngs,
        "interrupted": interrupted,
        "sha256_before": sha256_before,
        "sha256_after": compute_sha256(video_path),
    }

    return summary


def compute_longest_miss_run(records):
    """
    计算最长连续丢失帧数量。
    """
    longest = 0
    current = 0
    for record in records:
        if record["success"]:
            current = 0
        else:
            current += 1
            if current > longest:
                longest = current
    return longest


# ============================================================
# 统计打印
# ============================================================


def print_statistics(summary):
    """
    打印 M3.3 要求的基本统计信息。
    只做统计，不计算位移、不做毫米换算、不做频率分析。
    """
    print("")
    print("========== 本次逐帧追踪统计 ==========")
    print("1. 视频尺寸（程序实际处理）：宽 %d px，高 %d px"
          % (summary["width"], summary["height"]))
    print("2. FPS（从文件读取）：%.6f" % summary["fps"])
    print("3. 总帧数（文件声明）：%d" % summary["declared_frame_count"])
    print("4. 实际处理帧数：%d" % summary["processed_frames"])
    print("5. 检出帧数：%d" % summary["detected_frames"])
    print("6. 检出成功率：%.4f%%" % (summary["detection_rate"] * 100.0))
    print("7. 丢失帧数量：%d" % summary["missed_frames"])
    print("8. 最长连续丢失帧：%d" % summary["longest_miss_run"])
    # 说明：单位写成 px^2 而不是 px²，避免 GBK 控制台无法编码该符号
    print("9. area 最小值：%.1f px^2" % summary["area_min"])
    print("10. area 中位数：%.1f px^2" % summary["area_median"])
    print("11. area 最大值：%.1f px^2" % summary["area_max"])
    print("12. 第一帧时间：%.6f s" % summary["first_time_s"])
    print("13. 最后一帧时间：%.6f s" % summary["last_time_s"])
    print("14. 总运行耗时：%.2f s" % summary["elapsed_seconds"])
    print("======================================")


# ============================================================
# 数据完整性自检
# ============================================================


def check_csv_data(csv_path, expected_rows, frame_width, frame_height):
    """
    CSV 数据完整性自检（只读，不创建任何额外测试文件）。

    返回 (checks, passed)，其中 checks 是 [(说明, 是否通过), ...] 的列表。
    """
    checks = []
    csv_path = Path(csv_path)

    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        rows = list(reader)

    header = rows[0] if rows else []
    data_rows = rows[1:] if rows else []

    # 1. 表头
    checks.append(("CSV 第一行是标准表头 %s" % ",".join(CSV_FIELDNAMES),
                   header == CSV_FIELDNAMES))

    # 2. 数据行数
    checks.append(("CSV 数据行数 = 实际解码帧数（%d）" % expected_rows,
                   len(data_rows) == expected_rows))

    # 3. frame 连续且从 0 开始
    frame_numbers = []
    frame_format_ok = True
    for row in data_rows:
        if len(row) != len(CSV_FIELDNAMES):
            frame_format_ok = False
            break
        try:
            frame_numbers.append(int(row[0]))
        except ValueError:
            frame_format_ok = False
            break
    checks.append(("frame 列全部为合法整数", frame_format_ok))

    expected_frames = list(range(len(data_rows)))
    checks.append(("frame 从 0 到 %d 连续且无重复" % (len(data_rows) - 1),
                   frame_numbers == expected_frames))

    # 4. detected=True 的行必须有合法 x/y/area；detected=False 的行必须全空
    bad_detected_rows = []
    bad_missed_rows = []
    zero_zero_rows = []
    out_of_range_rows = []
    for row in data_rows:
        frame_number = int(row[0])
        x_text, y_text, area_text = row[2], row[3], row[4]
        detected_text = row[5]

        if detected_text == "True":
            values_ok = True
            x_value = y_value = area_value = None
            try:
                x_value = float(x_text)
                y_value = float(y_text)
                area_value = float(area_text)
            except ValueError:
                values_ok = False
            if not values_ok:
                bad_detected_rows.append(frame_number)
            else:
                if x_value == 0.0 and y_value == 0.0:
                    zero_zero_rows.append(frame_number)
                if not (0.0 <= x_value <= frame_width and 0.0 <= y_value <= frame_height):
                    out_of_range_rows.append(frame_number)
        elif detected_text == "False":
            if x_text != "" or y_text != "" or area_text != "":
                bad_missed_rows.append(frame_number)
        else:
            bad_detected_rows.append(frame_number)

    checks.append(("detected=True 的行 x/y/area 都是合法数值", len(bad_detected_rows) == 0))
    checks.append(("detected=False 的行 x/y/area 全部为空", len(bad_missed_rows) == 0))
    checks.append(("不存在 x=0, y=0 伪数据", len(zero_zero_rows) == 0))
    checks.append(("坐标全部落在 %d x %d 显示画面范围内" % (frame_width, frame_height),
                   len(out_of_range_rows) == 0))

    # 5. np.genfromtxt 直接读取
    genfromtxt_ok = False
    genfromtxt_note = "读取失败"
    try:
        data = np.genfromtxt(str(csv_path), delimiter=",", names=True)
        genfromtxt_ok = True
        names = list(data.dtype.names)
        if names == CSV_FIELDNAMES:
            nan_count = int(np.isnan(data["x_px"]).sum())
            detected_values = data["detected"]
            true_count = int(np.count_nonzero(detected_values))
            miss_count = len(data_rows) - true_count
            if nan_count == miss_count:
                genfromtxt_note = ("成功，失败字段读取为 NaN（NaN 行数 %d，"
                                   "与 detected=False 行数一致）" % nan_count)
            else:
                genfromtxt_ok = False
                genfromtxt_note = ("读取成功，但 NaN 行数 %d 与丢失帧数 %d 不一致"
                                   % (nan_count, miss_count))
        else:
            genfromtxt_ok = False
            genfromtxt_note = "读取成功，但列名与预期不一致：%s" % names
    except Exception as error:  # noqa: BLE001 - 自检要报告任何读取异常
        genfromtxt_note = "读取失败：%s" % error

    checks.append(("CSV 可被 np.genfromtxt(delimiter=',', names=True) 直接读取且失败字段为 NaN",
                   genfromtxt_ok))
    if not genfromtxt_ok:
        print("  说明：%s" % genfromtxt_note)

    passed = all(ok for _, ok in checks)
    return checks, passed


def print_check_results(checks, passed):
    """
    打印自检结果。
    """
    print("")
    print("========== CSV 数据完整性自检 ==========")
    for index, (description, ok) in enumerate(checks, start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    print("自检结论：%s" % ("全部通过" if passed else "存在未通过项，请人工检查"))
    print("=======================================")

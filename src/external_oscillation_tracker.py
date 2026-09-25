"""
VisionMotion —— M6.2-2C 外部公开视频正式振荡轨迹模块

本模块把 M6.2-2B 已经冻结的视觉规则，实现为“外部原始视频 -> 正式轨迹 CSV”的可复现流程。

数据性质（必须如实标注，不得写成自采实验）：
    External / Publicly available dataset
    ComPADRE / OSP — Teaching Harmonic Motion Online Using Tracker（ID=16081）
    权益持有人 / 作者：Kathleen Koenig，许可：CC BY-NC-SA 3.0

冻结视觉规则（唯一参数来源，本模块不得重新设计）：
    ROI            : x ∈ [690, 780)   y ∈ [380, 760)
    灰度阈值        : gray < 120
    暗带提取        : 8 邻域暗连通域（area ≥ 150 px）
                      -> 在连通域内逐行统计“该行属于本连通域的暗像素个数”
                         （实心暗带时该计数等于水平暗像素跨度）
                      -> 取最长连续“跨度 ≥ 35 px 且连续行数 ≥ 3”段
    几何条件        : 40 ≤ 暗带并集宽 w ≤ 75 px 且 暗带高 h ≤ 15 px
    正式位置特征    : B = 暗带上缘 y0
    正式帧区间      : frame 76–235（含，共 160 帧，连续）
    f74–75          : 保持缺失，不补值
    f0–73           : 仅作诊断/身份参考，不进入正式轨迹

本模块只做：
    1. 运行前校验输入视频 SHA-256（不一致立即停止，不继续处理）
    2. 逐帧读取指定正式帧区间
    3. 执行冻结检测，取正式位置特征 y0 并记录 QC 量
    4. 写正式轨迹 CSV（frame / time_s / detected / x_px / y0_px / bbox_w_px / bbox_h_px / area_px）
    5. 读取回 CSV 做独立质量检查并打印结果

本模块不做（M6.2-2C 明确禁止）：
    标定（px/mm）、位移换算、周期、频率、FFT、振幅、阻尼、弹簧常数、理论模型拟合、
    滤波、平滑、插值、去趋势、重采样、曲线拟合、overlay 视频、PNG 曲线、
    修改原始视频、调用红色目标检测器（src/marker_detector.py）。

代码风格：普通函数 + 中文注释，不使用 class / 多线程 / 异步 / logging / pandas / scipy。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m62_external_tracking.py
"""

import csv
import hashlib
from pathlib import Path

import cv2
import numpy as np

# ============================================================
# M6.2-2B 冻结常量（本模块唯一参数来源）
# ============================================================

# 外部数据来源标注（写入打印信息，避免与自采实验混淆）
EXTERNAL_DATASET_NAME = "ComPADRE / OSP - Teaching Harmonic Motion Online Using Tracker (ID=16081)"
EXTERNAL_DATASET_AUTHOR = "Kathleen Koenig"
EXTERNAL_DATASET_LICENSE = "CC BY-NC-SA 3.0"
EXTERNAL_VIDEO_SHA256 = "dbc81382e93d2b531b7390f1d52f275da5ea9731a9eec9aadb059667944e282d"

# 正式自由振荡帧区间（M6.2-2B 冻结）
START_FRAME = 76
END_FRAME = 235
EXPECTED_FRAME_ROWS = END_FRAME - START_FRAME + 1  # 160

# 冻结 ROI（右端为开区间）
ROI_X_MIN = 690
ROI_X_MAX = 780
ROI_Y_MIN = 380
ROI_Y_MAX = 760

# 冻结灰度阈值
GRAY_THRESHOLD = 120

# 冻结暗带提取条件
MIN_COMPONENT_AREA = 150
MIN_ROW_SPAN_PX = 35
MIN_BAND_ROWS = 3

# 冻结几何条件
MIN_BAND_WIDTH_PX = 40
MAX_BAND_WIDTH_PX = 75
MAX_BAND_HEIGHT_PX = 15

# 冻结正式位置特征（只作为文字标注，不参与计算）
POSITION_FEATURE_NAME = "y0_px = 暗带上缘（M6.2-2B 冻结）"

# CSV 表头（第一行就是真正的表头，前面不加任何 metadata）
CSV_FIELDNAMES = [
    "frame",
    "time_s",
    "detected",
    "x_px",
    "y0_px",
    "bbox_w_px",
    "bbox_h_px",
    "area_px",
]

# QC 常量
MAX_JUMP_PX = 30.0          # 单帧 y0 突跳判定阈值（只做 QC，不做任何补偿）
TIME_TOLERANCE_S = 1e-5     # time_s 与 frame / fps 的允许差（CSV 写 6 位小数）


# ============================================================
# 基础工具
# ============================================================


def compute_sha256(file_path):
    """
    计算文件的 SHA-256（只读，不会修改文件）。
    """
    digest = hashlib.sha256()
    with open(file_path, "rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_video_sha256(video_path, expected_sha256=EXTERNAL_VIDEO_SHA256):
    """
    运行前校验输入视频 SHA-256；不一致立即报错停止，不继续处理。

    返回实际 SHA-256（小写）。
    """
    actual_sha256 = compute_sha256(video_path)
    if actual_sha256.lower() != str(expected_sha256).lower():
        raise RuntimeError(
            "输入视频 SHA-256 不一致，已停止处理。\n"
            "  期望：%s\n  实际：%s\n  文件：%s"
            % (str(expected_sha256).lower(), actual_sha256, video_path)
        )
    return actual_sha256


def read_video_info(capture):
    """
    读取视频参数（分辨率 / fps / 总帧数）。这里读到的就是实际用于 time_s 的 fps。
    """
    return {
        "width": int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": float(capture.get(cv2.CAP_PROP_FPS)),
        "frame_count": int(capture.get(cv2.CAP_PROP_FRAME_COUNT)),
    }


# ============================================================
# 冻结检测：暗带提取
# ============================================================


def find_longest_span_run(row_spans):
    """
    在“逐行暗像素跨度”序列里，找最长连续满足 跨度 ≥ 35 px 的段。

    返回 (行数, 起始行, 结束行)，结束行为开区间；没有满足条件的段时返回 (0, 0, 0)。
    """
    best_rows, best_start, best_stop = 0, 0, 0
    run_start = None
    span_count = len(row_spans)
    for index in range(span_count + 1):
        is_wide = (index < span_count) and (row_spans[index] >= MIN_ROW_SPAN_PX)
        if is_wide and run_start is None:
            run_start = index
        if (not is_wide) and (run_start is not None):
            if index - run_start > best_rows:
                best_rows, best_start, best_stop = index - run_start, run_start, index
            run_start = None
    return best_rows, best_start, best_stop


def detect_dark_band(gray_frame):
    """
    在冻结 ROI 内执行冻结的暗带检测（不重新设计算法）。

    返回 dict：
        candidate_count : 面积达标的连通域里“找到暗带段”的个数（未加几何筛选）
        accepted_count  : 通过几何条件（40 ≤ w ≤ 75 且 h ≤ 15）的暗带个数
        band            : 本帧选中的暗带（面积最大者），没有则 None
                          band 字段：x_px（bbox 中心，仅 QC）/ y0_px（正式位置特征）/
                                    bbox_w_px / bbox_h_px / area_px（均为 QC）
    """
    roi = gray_frame[ROI_Y_MIN:ROI_Y_MAX, ROI_X_MIN:ROI_X_MAX]
    binary = (roi < GRAY_THRESHOLD).astype(np.uint8)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)

    candidate_count = 0
    accepted_bands = []

    for label_index in range(1, num_labels):
        comp_x = int(stats[label_index, cv2.CC_STAT_LEFT])
        comp_y = int(stats[label_index, cv2.CC_STAT_TOP])
        comp_w = int(stats[label_index, cv2.CC_STAT_WIDTH])
        comp_h = int(stats[label_index, cv2.CC_STAT_HEIGHT])
        comp_area = int(stats[label_index, cv2.CC_STAT_AREA])
        if comp_area < MIN_COMPONENT_AREA:
            continue

        comp_mask = labels[comp_y:comp_y + comp_h, comp_x:comp_x + comp_w] == label_index
        row_spans = comp_mask.sum(axis=1)
        band_rows, band_start, band_stop = find_longest_span_run(row_spans)
        if band_rows < MIN_BAND_ROWS:
            continue
        candidate_count += 1

        band_mask = comp_mask[band_start:band_stop]
        band_row_index, band_col_index = np.nonzero(band_mask)
        band_x_min = comp_x + int(band_col_index.min())
        band_x_max = comp_x + int(band_col_index.max())
        band_w = band_x_max - band_x_min + 1
        band_h = band_stop - band_start

        if not (MIN_BAND_WIDTH_PX <= band_w <= MAX_BAND_WIDTH_PX):
            continue
        if band_h > MAX_BAND_HEIGHT_PX:
            continue

        accepted_bands.append(
            {
                # x_px：暗带 bbox 中心，仅作为 QC 记录，不作为正式位置
                "x_px": (band_x_min + band_x_max) / 2.0 + ROI_X_MIN,
                # y0_px：正式位置特征（暗带上缘）
                "y0_px": float(band_start + comp_y + ROI_Y_MIN),
                "bbox_w_px": band_w,
                "bbox_h_px": band_h,
                "area_px": int(band_mask.sum()),
            }
        )

    selected_band = None
    if accepted_bands:
        selected_band = max(accepted_bands, key=lambda item: item["area_px"])
    return {
        "candidate_count": candidate_count,
        "accepted_count": len(accepted_bands),
        "band": selected_band,
    }


# ============================================================
# 正式逐帧追踪
# ============================================================


def track_external_oscillation(video_path, start_frame=START_FRAME, end_frame=END_FRAME,
                               expected_sha256=EXTERNAL_VIDEO_SHA256):
    """
    从外部原始视频逐帧运行冻结检测，得到正式自由振荡轨迹。

    重要：本函数不依赖任何历史的运行结果，全部数值都来自本次对原始视频的实际逐帧检测。

    返回 summary dict：
        video_path / sha256_before / sha256_after / video_info / start_frame / end_frame / rows
        rows 每一项：frame / time_s / detected / x_px / y0_px / bbox_w_px / bbox_h_px /
                     area_px / candidate_count / accepted_count
    """
    video_path = Path(video_path)
    if not video_path.exists():
        raise FileNotFoundError("找不到输入视频：%s" % video_path)

    sha256_before = verify_video_sha256(video_path, expected_sha256)

    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        raise RuntimeError("无法打开视频（OpenCV VideoCapture 失败）：%s" % video_path)

    video_info = read_video_info(capture)
    if video_info["fps"] <= 0.0:
        capture.release()
        raise RuntimeError("视频 fps 读数异常（%.6f），停止处理" % video_info["fps"])
    if end_frame >= video_info["frame_count"]:
        capture.release()
        raise RuntimeError(
            "正式帧区间超出视频范围：END_FRAME=%d，视频总帧数=%d"
            % (end_frame, video_info["frame_count"])
        )

    # 从头顺序解码，用“已解码帧计数”确定真实 frame 编号，
    # 不依赖 CAP_PROP_POS_FRAMES 的定位精度，保证 frame 与视频真实帧一一对应。
    rows = []
    decoded_index = 0
    while decoded_index < start_frame:
        ok, _ = capture.read()
        if not ok:
            capture.release()
            raise RuntimeError("跳帧阶段解码失败：视频在第 %d 帧提前结束" % decoded_index)
        decoded_index += 1

    while decoded_index <= end_frame:
        ok, frame = capture.read()
        if not ok:
            capture.release()
            raise RuntimeError("正式帧区间内解码失败：第 %d 帧无法读取" % decoded_index)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detection = detect_dark_band(gray_frame)
        band = detection["band"]

        rows.append(
            {
                "frame": decoded_index,
                # time_s 使用原视频绝对时间轴：frame / fps（不重新定义时间零点）
                "time_s": decoded_index / video_info["fps"],
                "detected": band is not None,
                "x_px": band["x_px"] if band else None,
                "y0_px": band["y0_px"] if band else None,
                "bbox_w_px": band["bbox_w_px"] if band else None,
                "bbox_h_px": band["bbox_h_px"] if band else None,
                "area_px": band["area_px"] if band else None,
                "candidate_count": detection["candidate_count"],
                "accepted_count": detection["accepted_count"],
            }
        )
        decoded_index += 1

    capture.release()

    # 只读校验：确认原始视频在整个流程中未被改动
    sha256_after = compute_sha256(video_path)

    return {
        "video_path": str(video_path),
        "sha256_before": sha256_before,
        "sha256_after": sha256_after,
        "video_info": video_info,
        "start_frame": start_frame,
        "end_frame": end_frame,
        "rows": rows,
    }


# ============================================================
# 正式 CSV：写入与读回
# ============================================================


def write_trajectory_csv(rows, csv_path):
    """
    写正式轨迹 CSV（只写正式自由振荡帧；表头一行）。

    detected=True  -> 写全字段；detected=False -> 写 detected=False，其余字段留空。
    """
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
        # 行尾使用 "\n"，与 results/ 下已有 CSV 保持一致（不写入 CRLF）
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            if row["detected"]:
                writer.writerow(
                    {
                        "frame": row["frame"],
                        "time_s": "%.6f" % row["time_s"],
                        "detected": "True",
                        "x_px": "%.2f" % row["x_px"],
                        "y0_px": "%.2f" % row["y0_px"],
                        "bbox_w_px": int(row["bbox_w_px"]),
                        "bbox_h_px": int(row["bbox_h_px"]),
                        "area_px": int(row["area_px"]),
                    }
                )
            else:
                writer.writerow(
                    {
                        "frame": row["frame"],
                        "time_s": "%.6f" % row["time_s"],
                        "detected": "False",
                        "x_px": "",
                        "y0_px": "",
                        "bbox_w_px": "",
                        "bbox_h_px": "",
                        "area_px": "",
                    }
                )
    return csv_path


def load_trajectory_csv(csv_path):
    """
    把正式轨迹 CSV 读回内存（独立复核用；只读，不修改文件）。

    返回 dict：header / rows / raw_line_count
    """
    csv_path = Path(csv_path)
    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        header = list(reader.fieldnames or [])
        rows = []
        for raw_row in reader:
            parsed = {
                "frame": int(raw_row["frame"]),
                "time_s": float(raw_row["time_s"]),
                "detected": raw_row["detected"] == "True",
            }
            for key in ("x_px", "y0_px", "bbox_w_px", "bbox_h_px", "area_px"):
                text = raw_row[key]
                parsed[key] = float(text) if text not in (None, "") else None
            rows.append(parsed)
    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        raw_line_count = sum(1 for line in csv_file if line.strip() != "")
    return {"header": header, "rows": rows, "raw_line_count": raw_line_count}


# ============================================================
# 独立质量检查（只做 QC 统计，不计算周期 / 频率 / 振幅）
# ============================================================


def _range_text(values, digits=2):
    """
    返回 (最小值, 最大值, 极差) 的文字描述。
    """
    minimum = min(values)
    maximum = max(values)
    return "min=%.*f / max=%.*f / range=%.*f" % (
        digits, minimum, digits, maximum, digits, maximum - minimum
    )


def check_trajectory_csv(csv_data, run_rows, fps, start_frame=START_FRAME, end_frame=END_FRAME):
    """
    独立质量检查：以“写出的 CSV 文件”为主要对象，运行期记录用于候选歧义等额外统计。

    返回 (checks, passed)，checks 为 [(说明, 是否通过), ...]。
    """
    checks = []
    expected_frames = list(range(start_frame, end_frame + 1))
    expected_rows = len(expected_frames)
    rows = csv_data["rows"]

    # 1. 表头
    checks.append(("CSV 表头 = %s" % ",".join(CSV_FIELDNAMES),
                   csv_data["header"] == CSV_FIELDNAMES))

    # 2. 行数（不含表头）
    checks.append(("CSV 数据行数 = %d（要求 %d 行）" % (len(rows), expected_rows),
                   len(rows) == expected_rows))

    # 3. frame 严格为 76–235
    frame_numbers = [row["frame"] for row in rows]
    checks.append(("frame 严格为 %d–%d" % (start_frame, end_frame),
                   frame_numbers == expected_frames))

    # 4. frame 连续无重复（与上一条互相印证）
    checks.append(
        ("frame 连续、无重复（%d 个帧号）" % len(set(frame_numbers)),
         frame_numbers == sorted(set(frame_numbers)) and len(frame_numbers) == len(set(frame_numbers)))
    )

    # 5. detected 全为 True
    detected_count = sum(1 for row in rows if row["detected"])
    checks.append(("detected 全为 True：%d / %d" % (detected_count, expected_rows),
                   detected_count == expected_rows))

    # 6. 是否存在空 y0
    missing_y0 = [row["frame"] for row in rows if row["y0_px"] is None]
    checks.append(("y0_px 空值数量 = %d" % len(missing_y0), len(missing_y0) == 0))

    y0_values = [row["y0_px"] for row in rows if row["y0_px"] is not None]
    x_values = [row["x_px"] for row in rows if row["x_px"] is not None]
    w_values = [row["bbox_w_px"] for row in rows if row["bbox_w_px"] is not None]
    h_values = [row["bbox_h_px"] for row in rows if row["bbox_h_px"] is not None]
    area_values = [row["area_px"] for row in rows if row["area_px"] is not None]

    # 7 ~ 11. 数值范围（信息项，用于人工核对；不作为“通过/不通过”判据）
    checks.append(("y0_px 范围（正式位置特征）：%s" % _range_text(y0_values), True))
    checks.append(("x_px 范围（仅 QC）：%s" % _range_text(x_values), True))
    checks.append(("bbox_w_px 范围（仅 QC）：%s" % _range_text(w_values), True))
    checks.append(("bbox_h_px 范围（仅 QC）：%s" % _range_text(h_values), True))
    checks.append(("area_px 范围（仅 QC）：%s" % _range_text(area_values, digits=0), True))

    # 12. 最大单帧 |Δy0|
    jumps = [abs(y0_values[index + 1] - y0_values[index])
             for index in range(len(y0_values) - 1)] if len(y0_values) >= 2 else []
    max_jump = max(jumps) if jumps else 0.0
    checks.append(("最大单帧 |Δy0_px| = %.2f px" % max_jump, True))

    # 13. >30 px 突跳次数
    big_jumps = [index for index, value in enumerate(jumps) if value > MAX_JUMP_PX]
    checks.append(("|Δy0_px| > %.0f px 的突跳次数 = %d" % (MAX_JUMP_PX, len(big_jumps)),
                   len(big_jumps) == 0))

    # 14. 候选数量歧义（运行期信息：通过几何条件的暗带数量 > 1 的帧）
    ambiguous_frames = [row["frame"] for row in run_rows if row["accepted_count"] > 1]
    multi_candidate_frames = [row["frame"] for row in run_rows if row["accepted_count"] == 0]
    checks.append(
        ("候选数量歧义帧数（合格暗带 > 1）= %d；无合格暗带帧数 = %d"
         % (len(ambiguous_frames), len(multi_candidate_frames)),
         len(ambiguous_frames) == 0)
    )

    # 15. time_s 严格满足 frame / fps
    time_errors = [abs(row["time_s"] - row["frame"] / fps) for row in rows]
    max_time_error = max(time_errors) if time_errors else 0.0
    checks.append(
        ("time_s 严格满足 frame / fps（fps=%.6f，最大偏差 %.2e s，容差 %.0e s）"
         % (fps, max_time_error, TIME_TOLERANCE_S),
         max_time_error <= TIME_TOLERANCE_S)
    )

    # 16. 原始视频未被改动（运行前后 SHA-256 一致）
    passed = all(ok for _, ok in checks)
    return checks, passed


def print_check_results(checks, passed):
    """
    打印质量检查结果。
    """
    print("")
    print("========== M6.2-2C 独立质量检查 ==========")
    for index, (description, ok) in enumerate(checks, start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    print("检查结论：%s" % ("全部通过" if passed else "存在未通过项，需人工处理"))
    print("=========================================")


# ============================================================
# 汇总打印
# ============================================================


def print_frozen_parameters():
    """
    打印本次实际使用的 M6.2-2B 冻结参数（只打印，不修改）。
    """
    print("")
    print("========== M6.2-2B 冻结参数（本次实际使用，未重新设计） ==========")
    print("数据来源：%s" % EXTERNAL_DATASET_NAME)
    print("作者 / 权益持有人：%s" % EXTERNAL_DATASET_AUTHOR)
    print("许可：%s（External / Publicly available dataset）" % EXTERNAL_DATASET_LICENSE)
    print("ROI：x ∈ [%d, %d)   y ∈ [%d, %d)" % (ROI_X_MIN, ROI_X_MAX, ROI_Y_MIN, ROI_Y_MAX))
    print("灰度阈值：gray < %d" % GRAY_THRESHOLD)
    print("暗带提取：8 邻域暗连通域（area ≥ %d px）→ 连续行跨度 ≥ %d px、连续行数 ≥ %d"
          % (MIN_COMPONENT_AREA, MIN_ROW_SPAN_PX, MIN_BAND_ROWS))
    print("几何条件：%d ≤ 带宽 w ≤ %d px，带高 h ≤ %d px"
          % (MIN_BAND_WIDTH_PX, MAX_BAND_WIDTH_PX, MAX_BAND_HEIGHT_PX))
    print("正式位置特征：%s" % POSITION_FEATURE_NAME)
    print("正式帧区间：frame %d–%d（含），共 %d 帧"
          % (START_FRAME, END_FRAME, EXPECTED_FRAME_ROWS))
    print("==================================================================")


def print_trajectory_summary(summary, csv_path, csv_data):
    """
    打印输入视频、CSV 与前几行 / 后几行核对信息。
    """
    video_info = summary["video_info"]
    rows = summary["rows"]

    print("")
    print("========== 输入视频 ==========")
    print("视频文件：%s" % summary["video_path"])
    print("分辨率：%d × %d" % (video_info["width"], video_info["height"]))
    print("fps：%.6f" % video_info["fps"])
    print("总帧数：%d" % video_info["frame_count"])
    print("运行前 SHA-256：%s" % summary["sha256_before"].lower())
    print("运行后 SHA-256：%s" % summary["sha256_after"].lower())
    print("原始视频是否被改动：%s"
          % ("否" if summary["sha256_before"] == summary["sha256_after"] else "是"))
    print("正式分析帧范围：frame %d–%d（共 %d 帧）"
          % (summary["start_frame"], summary["end_frame"], len(rows)))

    print("")
    print("========== 正式轨迹 CSV ==========")
    print("CSV 文件：%s" % csv_path)
    print("CSV 表头：%s" % ",".join(csv_data["header"]))
    print("CSV 数据行数（不含表头）：%d" % len(csv_data["rows"]))
    print("CSV 前 3 行 / 后 3 行：")
    preview_rows = csv_data["rows"][:3] + csv_data["rows"][-3:]
    for row in preview_rows:
        print("  frame=%d  time_s=%.6f  detected=%s  x_px=%s  y0_px=%s  w=%s  h=%s  area=%s"
              % (row["frame"], row["time_s"], row["detected"],
                 "None" if row["x_px"] is None else "%.2f" % row["x_px"],
                 "None" if row["y0_px"] is None else "%.2f" % row["y0_px"],
                 "None" if row["bbox_w_px"] is None else "%d" % int(row["bbox_w_px"]),
                 "None" if row["bbox_h_px"] is None else "%d" % int(row["bbox_h_px"]),
                 "None" if row["area_px"] is None else "%d" % int(row["area_px"])))


def run_external_tracking(video_path, csv_path, start_frame=START_FRAME, end_frame=END_FRAME,
                          expected_sha256=EXTERNAL_VIDEO_SHA256):
    """
    正式流程入口：校验 SHA -> 逐帧检测 -> 写 CSV -> 读回并做独立质量检查 -> 打印汇总。

    返回 (summary, csv_data, checks, passed)。
    """
    print_frozen_parameters()

    summary = track_external_oscillation(
        video_path, start_frame=start_frame, end_frame=end_frame, expected_sha256=expected_sha256
    )
    written_csv_path = write_trajectory_csv(summary["rows"], csv_path)
    csv_data = load_trajectory_csv(written_csv_path)
    checks, passed = check_trajectory_csv(
        csv_data, summary["rows"], summary["video_info"]["fps"], start_frame, end_frame
    )

    print_trajectory_summary(summary, written_csv_path, csv_data)
    print_check_results(checks, passed)

    detected_count = sum(1 for row in summary["rows"] if row["detected"])
    print("")
    print("========== M6.2-2C 结果摘要 ==========")
    print("检出率：%d / %d = %.1f%%"
          % (detected_count, len(summary["rows"]),
             100.0 * detected_count / len(summary["rows"]) if summary["rows"] else 0.0))
    print("正式位置特征：%s" % POSITION_FEATURE_NAME)
    print("是否包含周期 / 频率 / FFT / 振幅 / 滤波 / 插值 / 平滑 / 标定：否")
    print("是否通过 M6.2-2C 自检：%s" % ("是" if passed else "否"))
    print("=====================================")
    return summary, csv_data, checks, passed

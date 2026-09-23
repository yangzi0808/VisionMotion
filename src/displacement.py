"""
VisionMotion —— M4.3-2B 位移计算模块（按已冻结设计实现）

本模块只做一件事：把 M3 已经产出的 track CSV 变成位移数据 CSV。

正式数据链（本模块负责后半段）：

    原始视频
    -> M3 track_video()      （检测唯一来源，由 demo 调用）
    -> *_track.csv
    -> valid gate            （本模块，判据固定）
    -> project_point()       （直接复用 src/calibration.py）
    -> s0                    （前 0.5 s 有效帧的 s_px 平均值）
    -> ds_px / ds_mm
    -> *_ds.csv

严格边界（本阶段不允许越界）：

    - 不复制检测算法（检测唯一来源：src/marker_detector.py，由 M3 调用）
    - 不重新实现投影公式（投影唯一来源：src.calibration.project_point）
    - 不删除任何 track CSV 行，valid=False 的位移字段一律留空
    - 不做平滑 / 插值 / 预测 / 滤波 / 自适应阈值 / 运行时学习阈值
    - 不做 FFT、不做振动频率、不做相机标定、不做 UI
    - 不用 pandas / scipy / numpy 读 CSV，标准库 csv 足够

代码风格：普通函数 + 中文注释，不使用 class。
"""

import csv
import math
import re
from pathlib import Path

from src.calibration import compute_scale, project_point, unit_direction


# ============================================================
# 一、常量区（M4.3-2B 正式冻结，禁止改动）
# ============================================================

# ---- 像素尺度标定（已正式冻结）----
# 标定来源：EXP-003-STATIC-002.mp4，frame 900，
#           CAP_PROP_ORIENTATION_AUTO=1 之后的 1920 x 1080 坐标系。
#   P1（10 cm 刻线）：(1036.23, 490.58)
#   P2（16 cm 刻线）：(1381.64, 488.20)
#   两点真实距离：60.0 mm，方向约定 10 cm -> 16 cm
# 下面三个数值是这组标定点的正式冻结结果，本模块不做任何重新标定。
CALIB_P1_PX = (1036.23, 490.58)
CALIB_P2_PX = (1381.64, 488.20)
CALIB_REAL_DISTANCE_MM = 60.0

PX_PER_MM = 5.756961        # 像素/毫米，本阶段位移换算的主表达方式
MM_PER_PX = 0.173703        # 毫米/像素（= 1 / PX_PER_MM，只用于自检与报告）

U = (0.999976, -0.006894)   # 单位方向向量，方向为 10 cm -> 16 cm

# ---- M4 valid gate（本次 EXP-003 拍摄几何专属参数，不是通用视觉规则）----
# valid = True 当且仅当：detected == True
#                        且 AREA_MIN_PX <= area_px <= AREA_MAX_PX
#                        且 Y_MIN_PX <= y_px <= Y_MAX_PX
AREA_MIN_PX = 2000.0
AREA_MAX_PX = 15000.0
Y_MIN_PX = 400.0
Y_MAX_PX = 540.0

# ---- s0 规则（已正式拍板）----
S0_WINDOW_S = 0.5           # 只使用 time_s <= 0.5 的帧
MIN_S0_VALID_FRAMES = 10    # 窗口内有效帧少于 10 帧时不生成 ds CSV

# ---- CSV 规范 ----
TRACK_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]
DS_FIELDNAMES = [
    "frame",
    "time_s",
    "s_px",
    "ds_px",
    "ds_mm",
    "area_px",
    "detected",
    "valid",
]

# ds CSV 各字段允许的文本格式（自检时逐行核对小数位数）
FIELD_PATTERNS = {
    "time_s": r"^-?\d+\.\d{6}$",
    "s_px": r"^-?\d+\.\d{3}$",
    "ds_px": r"^-?\d+\.\d{3}$",
    "ds_mm": r"^-?\d+\.\d{4}$",
    "area_px": r"^-?\d+\.\d{1}$",
}


# ============================================================
# 二、冻结常量自检（可选，只读，不做任何重新标定）
# ============================================================


def check_calibration_constants(tolerance=1e-4):
    """
    检查本模块里的冻结常量是否自洽。

    只做两件事：
        1. 用冻结的两个标定点 + 60.0 mm 复算 PX_PER_MM / MM_PER_PX / u，
           看是否和冻结常量一致（用来发现手抄数字错误，不是重新标定）
        2. 检查 u 是单位向量、PX_PER_MM 与 MM_PER_PX 互为倒数

    返回 (checks, passed)，checks 是 [(说明, 是否通过), ...]。
    """
    checks = []

    scale = compute_scale(CALIB_P1_PX, CALIB_P2_PX, CALIB_REAL_DISTANCE_MM)
    direction = unit_direction(CALIB_P1_PX, CALIB_P2_PX)

    checks.append(
        (
            "PX_PER_MM 与冻结标定点一致（常量 %.6f / 复算 %.6f，容差 %g）"
            % (PX_PER_MM, scale["px_per_mm"], tolerance),
            abs(PX_PER_MM - scale["px_per_mm"]) <= tolerance,
        )
    )
    checks.append(
        (
            "MM_PER_PX 与冻结标定点一致（常量 %.6f / 复算 %.6f，容差 %g）"
            % (MM_PER_PX, scale["mm_per_px"], tolerance),
            abs(MM_PER_PX - scale["mm_per_px"]) <= tolerance,
        )
    )
    checks.append(
        (
            "u 与冻结标定点一致（常量 (%.6f, %.6f) / 复算 (%.6f, %.6f)，容差 %g）"
            % (U[0], U[1], direction["ux"], direction["uy"], tolerance),
            abs(U[0] - direction["ux"]) <= tolerance
            and abs(U[1] - direction["uy"]) <= tolerance,
        )
    )
    checks.append(
        (
            "u 是单位向量（|u| = %.8f）" % math.hypot(U[0], U[1]),
            abs(math.hypot(U[0], U[1]) - 1.0) <= tolerance,
        )
    )
    checks.append(
        (
            "PX_PER_MM x MM_PER_PX ≈ 1（当前 %.8f）" % (PX_PER_MM * MM_PER_PX),
            abs(PX_PER_MM * MM_PER_PX - 1.0) <= tolerance,
        )
    )

    passed = all(ok for _, ok in checks)
    return checks, passed


def rules_snapshot():
    """
    返回本次运行实际使用的全部规则常量的快照。

    用途：确认三个实验使用的 k / u / gate / s0 窗口规则完全一致。
    """
    return {
        "PX_PER_MM": PX_PER_MM,
        "MM_PER_PX": MM_PER_PX,
        "u": U,
        "area_px": (AREA_MIN_PX, AREA_MAX_PX),
        "y_px": (Y_MIN_PX, Y_MAX_PX),
        "s0_window_s": S0_WINDOW_S,
        "min_s0_valid_frames": MIN_S0_VALID_FRAMES,
    }


# ============================================================
# 三、valid gate
# ============================================================


def is_valid_frame(detected, area_px, y_px):
    """
    M4 valid gate（唯一判据）。

    valid = True 当且仅当：
        detected == True
        且 AREA_MIN_PX <= area_px <= AREA_MAX_PX
        且 Y_MIN_PX <= y_px <= Y_MAX_PX

    说明：
        - 绝不修改原始 detected，只在这里判断“这一帧能不能用”
        - 阈值是本次 EXP-003 拍摄几何专属参数，不做任何自适应
    """
    if not detected:
        return False

    # 检测成功却缺少坐标或面积，同样不能用（数据缺失，不填 0）
    if area_px is None or y_px is None:
        return False

    if not (AREA_MIN_PX <= area_px <= AREA_MAX_PX):
        return False

    if not (Y_MIN_PX <= y_px <= Y_MAX_PX):
        return False

    return True


# ============================================================
# 四、读取 M3 的 track CSV
# ============================================================


def _float_or_none(text):
    """
    把 CSV 里的文本转成 float；空字段返回 None（不写 0、不写 -1、不写 nan）。
    """
    text = text.strip()
    if text == "":
        return None
    return float(text)


def read_track_csv(track_csv_path):
    """
    读取 M3 生成的 track CSV（只读，不修改）。

    返回列表，每个元素是一行字典：
        frame / time_s / x_px / y_px / area_px / detected
        空字段一律读成 None。
    """
    track_csv_path = Path(track_csv_path)
    rows = []

    with open(track_csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.reader(csv_file)
        header = next(reader, None)
        if header != TRACK_FIELDNAMES:
            raise ValueError("track CSV 表头不符合 M3 规范：%s" % header)

        for line_number, record in enumerate(reader, start=2):
            if len(record) != len(TRACK_FIELDNAMES):
                raise ValueError(
                    "track CSV 第 %d 行列数不对（%d 列）"
                    % (line_number, len(record))
                )
            rows.append(
                {
                    "frame": int(record[0]),
                    "time_s": float(record[1]),
                    "x_px": _float_or_none(record[2]),
                    "y_px": _float_or_none(record[3]),
                    "area_px": _float_or_none(record[4]),
                    "detected": (record[5] == "True"),
                }
            )

    return rows


# ============================================================
# 五、逐行处理（顺序固定：valid -> s_px -> s0 -> ds）
# ============================================================


def add_valid_flags(rows):
    """
    第 2 步：逐行判断 valid。

    同时把 s_px / ds_px / ds_mm 三个输出字段初始化为 None，
    这样 valid=False 的行在后面始终留空，不会被填成 0。
    """
    for row in rows:
        row["valid"] = is_valid_frame(
            row["detected"], row["area_px"], row["y_px"]
        )
        row["s_px"] = None
        row["ds_px"] = None
        row["ds_mm"] = None


def add_projection(rows):
    """
    第 3 步：valid=True 的行计算 s_px = project_point((x_px, y_px), u)。

    投影公式直接复用 src/calibration.py 的 project_point()，本模块不重写公式。
    """
    for row in rows:
        if row["valid"]:
            row["s_px"] = project_point((row["x_px"], row["y_px"]), U)


def compute_s0(rows, window_s=S0_WINDOW_S, min_valid_frames=MIN_S0_VALID_FRAMES):
    """
    第 4 / 5 步：收集前 window_s 秒内 valid=True 的 s_px，并计算 s0。

    s0 = 只使用 time_s <= window_s 且 valid=True 的帧，取这些帧 s_px 的平均值。

    正式禁止：用 10 cm 代替 s0、用首帧代替均值、扩大窗口、
              插值、平滑、预测、按分位数自动调整。

    返回报告字典：
        window_s / window_total_frames / window_valid_frames
        window_missed_frames（窗口内 detected=False 数量）
        window_detected_invalid_frames（窗口内 detected=True 但 valid=False 数量）
        min_valid_frames / ok / s0
    窗口内有效帧不足时 ok=False，且 s0 保持 None（由调用方报错并停止写 ds CSV）。
    """
    window_rows = [row for row in rows if row["time_s"] <= window_s]
    valid_s_values = [row["s_px"] for row in window_rows if row["valid"]]

    report = {
        "window_s": window_s,
        "window_total_frames": len(window_rows),
        "window_valid_frames": len(valid_s_values),
        "window_missed_frames": sum(
            1 for row in window_rows if not row["detected"]
        ),
        "window_detected_invalid_frames": sum(
            1 for row in window_rows if row["detected"] and not row["valid"]
        ),
        "min_valid_frames": min_valid_frames,
        "ok": len(valid_s_values) >= min_valid_frames,
        "s0": None,
    }

    if report["ok"]:
        report["s0"] = sum(valid_s_values) / float(len(valid_s_values))

    return report


def add_displacement(rows, s0):
    """
    第 6 步：valid=True 的行计算 ds_px / ds_mm。

        ds_px = s_px - s0
        ds_mm = ds_px / PX_PER_MM

    valid=False 的行保持 None（写 CSV 时留空），绝不填 0。
    """
    for row in rows:
        if row["valid"]:
            row["ds_px"] = row["s_px"] - s0
            row["ds_mm"] = row["ds_px"] / PX_PER_MM


# ============================================================
# 六、写 ds CSV（第 7 步）
# ============================================================


def build_ds_row(row):
    """
    把一行数据格式化成 ds CSV 的文本列表（小数位数严格按冻结规范）：

        frame 整数 / time_s 6 位 / s_px 3 位 / ds_px 3 位 /
        ds_mm 4 位 / area_px 1 位 / detected / valid

    缺失数据一律写成空字符串（""），绝不写 0 / -1 / nan。
    """
    return [
        "%d" % row["frame"],
        "%.6f" % row["time_s"],
        "" if row["s_px"] is None else "%.3f" % row["s_px"],
        "" if row["ds_px"] is None else "%.3f" % row["ds_px"],
        "" if row["ds_mm"] is None else "%.4f" % row["ds_mm"],
        "" if row["area_px"] is None else "%.1f" % row["area_px"],
        "True" if row["detected"] else "False",
        "True" if row["valid"] else "False",
    ]


def write_ds_csv(ds_csv_path, rows):
    """
    写 ds CSV：UTF-8 无 BOM，换行只使用 \\n，第一行是真正的表头。
    """
    ds_csv_path = Path(ds_csv_path)
    ds_csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(ds_csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(DS_FIELDNAMES)
        for row in rows:
            writer.writerow(build_ds_row(row))

    return ds_csv_path


# ============================================================
# 七、统计
# ============================================================


def summarize(rows):
    """
    统计一个视频的 ds 数据。

    说明：ds_mm 的最小值 / 最大值 / 跨度只统计 valid=True 的行；
          如果一个有效行都没有，这些字段保持 None（打印时写“无”）。
    """
    total = len(rows)
    detected_count = sum(1 for row in rows if row["detected"])
    valid_count = sum(1 for row in rows if row["valid"])
    # s0 计算失败时不会写 ds，此时 valid 行的 ds 字段保持 None，不能参与 min / max
    ds_values = [
        row["ds_mm"] for row in rows if row["valid"] and row["ds_mm"] is not None
    ]

    longest_invalid_run = 0
    current_invalid_run = 0
    for row in rows:
        if row["valid"]:
            current_invalid_run = 0
        else:
            current_invalid_run += 1
            if current_invalid_run > longest_invalid_run:
                longest_invalid_run = current_invalid_run

    summary = {
        "frame_count": total,
        "detected_count": detected_count,
        "detected_rate": (detected_count / float(total)) if total else 0.0,
        "valid_count": valid_count,
        "valid_rate": (valid_count / float(total)) if total else 0.0,
        "invalid_count": total - valid_count,
        "missed_count": total - detected_count,
        "detected_invalid_count": detected_count - valid_count,
        "ds_min_mm": min(ds_values) if ds_values else None,
        "ds_max_mm": max(ds_values) if ds_values else None,
        "ds_span_mm": (max(ds_values) - min(ds_values)) if ds_values else None,
        "longest_invalid_run": longest_invalid_run,
        "first_time_s": rows[0]["time_s"] if rows else None,
        "last_time_s": rows[-1]["time_s"] if rows else None,
    }
    return summary


def print_check_results(checks, passed):
    """
    打印自检结果（[(说明, 是否通过), ...]）。
    """
    print("")
    print("========== M4.3-2B 自动自检 ==========")
    for index, (description, ok) in enumerate(checks, start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    print("自检结论：%s" % ("全部通过" if passed else "存在未通过项，请人工检查"))


def print_summary(report):
    """
    打印单个视频的全部统计信息（含 s0 报告与自检结果）。
    """
    video_name = report["video_name"]
    summary = report["summary"]
    s0_report = report["s0_report"]
    s0 = s0_report["s0"]

    print("")
    print("========== %s 统计 ==========" % video_name)
    print("1. 视频名称：%s" % video_name)
    print("2. 帧数：%d" % summary["frame_count"])
    print(
        "3. detected 成功率：%.4f%%（%d / %d）"
        % (summary["detected_rate"] * 100.0, summary["detected_count"], summary["frame_count"])
    )
    print(
        "4. valid 成功率：%.4f%%（%d / %d）"
        % (summary["valid_rate"] * 100.0, summary["valid_count"], summary["frame_count"])
    )
    print("5. invalid 总数：%d" % summary["invalid_count"])
    print("6. detected=False 数量：%d" % summary["missed_count"])
    print("7. detected=True 但 valid=False 数量：%d" % summary["detected_invalid_count"])
    print(
        "8. s0：%s"
        % ("无（窗口内有效帧不足）" if s0 is None else "%.3f px" % s0)
    )
    print("9. s0 窗口有效帧数：%d" % s0_report["window_valid_frames"])
    print("10. s0 窗口总帧数：%d" % s0_report["window_total_frames"])
    print(
        "11. ds_mm 最小值：%s"
        % ("无" if summary["ds_min_mm"] is None else "%.4f mm" % summary["ds_min_mm"])
    )
    print(
        "12. ds_mm 最大值：%s"
        % ("无" if summary["ds_max_mm"] is None else "%.4f mm" % summary["ds_max_mm"])
    )
    print(
        "13. ds_mm 跨度（max-min）：%s"
        % ("无" if summary["ds_span_mm"] is None else "%.4f mm" % summary["ds_span_mm"])
    )
    print("14. 最长连续 invalid 帧：%d" % summary["longest_invalid_run"])
    print(
        "15. 首帧时间：%s"
        % ("无" if summary["first_time_s"] is None else "%.6f s" % summary["first_time_s"])
    )
    print(
        "16. 末帧时间：%s"
        % ("无" if summary["last_time_s"] is None else "%.6f s" % summary["last_time_s"])
    )
    print("17. 输入 track CSV：%s" % report["track_csv_path"])
    print(
        "18. ds CSV：%s"
        % (
            report["ds_csv_path"]
            if report["ds_written"]
            else "未生成（s0 窗口有效帧不足，按规则不写 ds CSV）"
        )
    )

    # s0 窗口有效帧不足时的明确问题报告（不扩大窗口、不改阈值）
    if not s0_report["ok"]:
        print("")
        print("！！问题报告：%s 的 s0 窗口有效帧不足 ！！" % video_name)
        print("原因：s0 规则要求窗口内至少有 %d 帧 valid=True，"
              "当前只有 %d 帧。" % (s0_report["min_valid_frames"], s0_report["window_valid_frames"]))
        print("窗口总帧数：%d" % s0_report["window_total_frames"])
        print("窗口有效帧数：%d" % s0_report["window_valid_frames"])
        print("窗口内 detected=False 数量：%d" % s0_report["window_missed_frames"])
        print("窗口内 detected=True 但 valid=False 数量：%d"
              % s0_report["window_detected_invalid_frames"])
        print("处理方式：本视频不生成 ds CSV；不扩大窗口、不修改阈值、不做插值。")

    if report["ds_written"]:
        print_check_results(report["checks"], report["passed"])

    print("=====================================")


# ============================================================
# 八、ds CSV 自动自检
# ============================================================


def _ds_row_format_ok(ds_row):
    """
    检查一行 ds CSV 的字段格式：小数位数、布尔写法、空字段写法。
    """
    if len(ds_row) != len(DS_FIELDNAMES):
        return False

    if not re.match(r"^\d+$", ds_row[0]):
        return False

    if not re.match(FIELD_PATTERNS["time_s"], ds_row[1]):
        return False

    for index, key in ((2, "s_px"), (3, "ds_px"), (4, "ds_mm"), (5, "area_px")):
        text = ds_row[index]
        if text == "":
            continue
        if not re.match(FIELD_PATTERNS[key], text):
            return False

    if ds_row[6] not in ("True", "False"):
        return False

    if ds_row[7] not in ("True", "False"):
        return False

    return True


def read_ds_csv_lines(ds_csv_path):
    """
    按原始文本读取 ds CSV（只读，供自检逐行核对格式）。
    返回列表的列表，第一个元素是表头。
    """
    with open(ds_csv_path, "r", encoding="utf-8", newline="") as csv_file:
        return list(csv.reader(csv_file))


def check_ds_csv(report):
    """
    ds CSV 自动自检：重新从磁盘读取 track CSV 与 ds CSV，独立核对。

    检查内容：
        1. 文件是 UTF-8 无 BOM，换行只使用 \\n
        2. 第一行是标准表头
        3. ds CSV 行数 == track CSV 行数
        4. frame 列逐行完全一致
        5. valid 列与 M4 valid gate 逐行一致（用 track CSV 的 detected / area_px / y_px 复算）
        6. valid=False 的行：s_px / ds_px / ds_mm 全为空
        7. valid=True 的行：s_px / ds_px / ds_mm 都是有限数值
        8. detected=False 的行 area_px 为空；detected=True 的行 area_px 有值
        9. 字段小数位数符合规范
        10. s0 等于窗口内有效帧 s_px 的平均值（容差 0.002 px）
        11. ds_px = s_px - s0、ds_mm = ds_px / PX_PER_MM（按写入的舍入值核对）
        12. ds CSV 重新统计出的 detected 成功率 / valid 成功率与打印用的统计值一致

    返回 (checks, passed)。
    """
    checks = []
    track_csv_path = report["track_csv_path"]
    ds_csv_path = report["ds_csv_path"]
    summary = report["summary"]
    s0 = report["s0_report"]["s0"]

    with open(ds_csv_path, "rb") as binary_file:
        raw_bytes = binary_file.read()

    checks.append(
        ("ds CSV 为 UTF-8 无 BOM（开头没有 EF BB BF）",
         not raw_bytes.startswith(b"\xef\xbb\xbf"))
    )
    checks.append(
        ("ds CSV 换行只使用 \\n（文件中没有 \\r）", b"\r" not in raw_bytes)
    )

    ds_lines = read_ds_csv_lines(ds_csv_path)
    header = ds_lines[0] if ds_lines else []
    data_rows = ds_lines[1:] if ds_lines else []

    checks.append(
        ("ds CSV 第一行是标准表头（%s）" % ",".join(DS_FIELDNAMES),
         header == DS_FIELDNAMES)
    )

    track_rows = read_track_csv(track_csv_path)

    # 3. 行数一致
    checks.append(
        ("ds CSV 行数 == track CSV 行数（%d）" % len(track_rows),
         len(data_rows) == len(track_rows))
    )

    # 4. frame 列逐行一致
    frame_ok = len(data_rows) == len(track_rows)
    if frame_ok:
        for track_row, ds_row in zip(track_rows, data_rows):
            if len(ds_row) != len(DS_FIELDNAMES) or ds_row[0] != "%d" % track_row["frame"]:
                frame_ok = False
                break
    checks.append(("frame 列与 track CSV 逐行完全一致", frame_ok))

    # 5 ~ 9. 逐行核对
    gate_ok = len(data_rows) == len(track_rows)
    bad_invalid_rows = []
    bad_valid_rows = []
    bad_format_rows = []
    bad_area_rows = []
    detected_true_count = 0
    valid_true_count = 0

    if len(data_rows) == len(track_rows):
        for track_row, ds_row in zip(track_rows, data_rows):
            if not _ds_row_format_ok(ds_row):
                bad_format_rows.append(ds_row[0] if ds_row else "?")
                continue

            frame_text = ds_row[0]
            detected = ds_row[6]
            valid = ds_row[7]

            if detected == "True":
                detected_true_count += 1
            if valid == "True":
                valid_true_count += 1

            # valid 列必须与 valid gate 复算结果一致
            expected_valid = is_valid_frame(
                track_row["detected"], track_row["area_px"], track_row["y_px"]
            )
            if ("True" if expected_valid else "False") != valid:
                gate_ok = False

            # valid=False 的位移字段必须全空；valid=True 的必须是有限数值
            if valid == "False":
                if ds_row[2] != "" or ds_row[3] != "" or ds_row[4] != "":
                    bad_invalid_rows.append(frame_text)
            else:
                finite_ok = True
                for index in (2, 3, 4):
                    try:
                        if not math.isfinite(float(ds_row[index])):
                            finite_ok = False
                    except ValueError:
                        finite_ok = False
                if not finite_ok:
                    bad_valid_rows.append(frame_text)

            # area_px：detected=False 必须为空，detected=True 必须有值
            if detected == "False" and ds_row[5] != "":
                bad_area_rows.append(frame_text)
            if detected == "True" and ds_row[5] == "":
                bad_area_rows.append(frame_text)

    checks.append(
        ("valid 列与 M4 valid gate 逐行一致（detected / area_px / y_px 复算）", gate_ok)
    )
    checks.append(
        ("valid=False 的行 s_px / ds_px / ds_mm 全部为空（没有填 0 / -1 / nan）",
         len(bad_invalid_rows) == 0)
    )
    checks.append(
        ("valid=True 的行 s_px / ds_px / ds_mm 都是有限数值",
         len(bad_valid_rows) == 0)
    )
    checks.append(
        ("detected=False 的行 area_px 为空、detected=True 的行 area_px 有值",
         len(bad_area_rows) == 0)
    )
    checks.append(
        ("字段小数位数符合规范（time_s 6 / s_px 3 / ds_px 3 / ds_mm 4 / area_px 1）",
         len(bad_format_rows) == 0)
    )

    # 10. s0 规则复算：窗口内有效帧 s_px 的平均值
    s0_ok = True
    s0_note = "无有效行"
    if s0 is not None:
        window_s_values = []
        for ds_row in data_rows:
            if not _ds_row_format_ok(ds_row):
                continue
            if ds_row[7] == "True" and float(ds_row[1]) <= S0_WINDOW_S:
                window_s_values.append(float(ds_row[2]))
        if window_s_values:
            recheck_s0 = sum(window_s_values) / float(len(window_s_values))
            s0_ok = abs(recheck_s0 - s0) <= 0.002
            s0_note = "打印值 %.6f / 复算 %.6f" % (s0, recheck_s0)
        else:
            s0_ok = False
    checks.append(
        ("s0 等于 s0 窗口内有效帧 s_px 的平均值（容差 0.002 px，%s）" % s0_note,
         s0_ok)
    )

    # 11. ds 公式复算（按写入的舍入值核对）
    ds_formula_ok = s0 is not None
    if s0 is not None:
        for ds_row in data_rows:
            if not _ds_row_format_ok(ds_row) or ds_row[7] != "True":
                continue
            s_px = float(ds_row[2])
            ds_px = float(ds_row[3])
            ds_mm = float(ds_row[4])
            if abs(ds_px - (s_px - s0)) > 0.002:
                ds_formula_ok = False
                break
            if abs(ds_mm - ds_px / PX_PER_MM) > 0.0005:
                ds_formula_ok = False
                break
    checks.append(
        ("ds_px = s_px - s0（容差 0.002 px）且 ds_mm = ds_px / PX_PER_MM（容差 0.0005 mm）",
         ds_formula_ok)
    )

    # 12. 重新统计的成功率与打印用统计值一致
    total = len(data_rows)
    if total > 0:
        detected_rate = detected_true_count / float(total)
        valid_rate = valid_true_count / float(total)
        checks.append(
            ("ds CSV 重新统计的 detected 成功率与打印值一致（%.6f）" % detected_rate,
             abs(detected_rate - summary["detected_rate"]) < 1e-9)
        )
        checks.append(
            ("ds CSV 重新统计的 valid 成功率与打印值一致（%.6f）" % valid_rate,
             abs(valid_rate - summary["valid_rate"]) < 1e-9)
        )
    else:
        checks.append(("ds CSV 至少有一行数据", False))

    passed = all(ok for _, ok in checks)
    return checks, passed


# ============================================================
# 九、单视频流程与实验入口
# ============================================================


def build_ds_from_track_csv(track_csv_path, ds_csv_path, video_name=""):
    """
    完整数据链（M3 track CSV -> ds CSV），逐行处理顺序固定：

        1. 读取 frame / time_s / x_px / y_px / area_px / detected
        2. 判断 valid
        3. valid 时计算 s_px
        4. 收集前 0.5 s 内 valid 的 s_px
        5. 计算 s0
        6. valid 时计算 ds_px / ds_mm
        7. 写 ds CSV

    过程中不删除任何行；s0 窗口有效帧不足时不写 ds CSV。
    返回 report 字典（统计 summary、s0 报告、ds_written 等）。
    """
    track_csv_path = Path(track_csv_path)
    ds_csv_path = Path(ds_csv_path)

    rows = read_track_csv(track_csv_path)            # 1
    add_valid_flags(rows)                            # 2
    add_projection(rows)                             # 3
    s0_report = compute_s0(rows)                     # 4 / 5

    ds_written = False
    if s0_report["ok"]:
        add_displacement(rows, s0_report["s0"])      # 6
        write_ds_csv(ds_csv_path, rows)              # 7
        ds_written = True

    report = {
        "video_name": video_name if video_name else track_csv_path.stem,
        "track_csv_path": track_csv_path,
        "ds_csv_path": ds_csv_path,
        "track_frame_count": len(rows),
        "s0_report": s0_report,
        "summary": summarize(rows),
        "rows": rows,
        "ds_written": ds_written,
        "rules": rules_snapshot(),
        "checks": [],
        "passed": False,
    }
    return report


def run_experiment(track_csv_path, ds_csv_path, video_name=""):
    """
    运行一次 M4.3-2B 位移实验：M3 的 track CSV -> ds CSV，并自动自检。

    说明：
        “原始视频 -> track CSV”由 M3 的 track_video() 完成（demo 先调用它），
        本函数不重复检测、不读视频，只负责 valid gate 之后的部分。

    返回 report 字典；ds CSV 未生成时 checks 为空、passed=False。
    """
    report = build_ds_from_track_csv(track_csv_path, ds_csv_path, video_name)

    if report["ds_written"]:
        checks, passed = check_ds_csv(report)
        report["checks"] = checks
        report["passed"] = passed

    return report

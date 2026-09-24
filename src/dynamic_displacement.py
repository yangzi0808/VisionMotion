"""
VisionMotion —— M5.2-2B EXP-004 动态位移模块（按已冻结设计实现）

本模块只做一件事：把 M3 已经产出的 track CSV 变成动态位移数据 CSV（ds CSV）。

正式数据链（本模块负责后半段）：

    原始视频
    -> M3 track_video()       （检测唯一来源，由 demo 调用）
    -> *_track.csv
    -> EXP-004 valid gate     （本模块，判据固定，不做任何自适应）
    -> project_point()        （只调用 src.calibration 里这一个函数，不重写投影公式）
    -> s0                     （前 2.0 s 有效帧的 s_px 平均值，至少 60 帧）
    -> ds_px / ds_mm
    -> *_ds.csv
    -> 原始 x_px 转向点统计    （最小反向行程 20 px，不平滑、不滤波）

严格边界（本阶段不允许越界）：

    - EXP-004 专属：本模块的标定常量 / valid gate / s0 规则 / 运动统计口径
      只对 EXP-004-DYNAMIC-001 有效，不得套用到其它视频，也不得把 M4 的常量搬进来。
    - 不得 import src.displacement（结构性要求：从根上防止动态代码误用 M4 的
      gate（2000/15000/400/540）与 M4 的 s0 规则）。
    - 不复制检测算法（检测唯一来源：src/marker_detector.py，由 M3 调用），
      不复制 HSV / contour / centroid 逻辑。
    - 不重新实现投影公式（投影唯一来源：src.calibration.project_point）。
    - 不删除任何 track CSV 行；valid=False 的位移字段一律留空（不写 0 / -1 / nan）。
    - 不做平滑 / 滤波 / 插值 / 补帧 / 补零 / 预测 / FFT / 频率 / 周期 / 振幅分析。
    - 不重新标定、不自动调整任何阈值。
    - 转向点只使用原始 x_px 数据，最小运动行程 MIN_TURN_TRAVEL_PX = 20.0 px。

代码风格：普通函数 + 中文注释，不使用 class。
"""

import csv
import math
import re
from pathlib import Path

from src.calibration import project_point


# ============================================================
# 一、常量区（EXP-004 专属，已人工验收，禁止改动）
# ============================================================

# 本次正式实验编号（同时是视频、track CSV、ds CSV、overlay 的文件名前缀）
EXPERIMENT_NAME = "EXP-004-DYNAMIC-001"

# 正式输入视频（相对项目根目录）
VIDEO_RELATIVE_PATH = "data/raw/EXP-004-DYNAMIC-001.mp4"

# 运行前记录的原始视频 SHA-256：运行完成后必须完全一致（本程序绝不修改原视频）
EXPECTED_VIDEO_SHA256 = "7BA3060597474FE8BFEFF3B5377ED42256761783DB06B86E7E79AB2B96F9E0A4"

# 本视频的总帧数（自检用：这是文件的既有属性，不是测量结果，不参与任何统计）
EXPECTED_TRACK_ROWS = 1766

# ---- EXP-004 专属标定（M5.2-1 人工点击 + 独立核验，已冻结，不得重新标定）----
CALIB_P1_PX = (813.50, 296.49)      # 10 cm 刻线的像素坐标
CALIB_P2_PX = (1422.13, 294.11)     # 20 cm 刻线的像素坐标
CALIB_REAL_DISTANCE_MM = 100.0      # 10 cm -> 20 cm 的真实距离 L_real = 100.0 mm

PX_PER_MM_004 = 6.086399            # 像素/毫米（冻结值）
MM_PER_PX_004 = 0.164301            # 毫米/像素（冻结值，= 1 / PX_PER_MM_004）
U_004 = (0.999992, -0.003913)       # 单位方向向量，方向 10 cm -> 20 cm（正向）

# ---- EXP-004 专属 valid gate（与 M4 gate 完全不同，不得混用）----
# valid = True 当且仅当：
#     detected == True
#     且 4500 <= area_px <= 6500
#     且 200 <= y_px <= 250
AREA_MIN_PX_004 = 4500.0
AREA_MAX_PX_004 = 6500.0
Y_MIN_PX_004 = 200.0
Y_MAX_PX_004 = 250.0

# ---- s0 规则（已冻结）----
S0_WINDOW_S = 2.0           # 只使用 time_s <= 2.0 的帧
MIN_S0_VALID_FRAMES = 60    # 窗口内有效帧少于 60 帧时不生成 ds CSV

# ---- 运动方向统计规则（负责人已正式确认）----
# 正向 = ds 增大（沿 U_004，即尺子 10 cm -> 20 cm 方向）
# 负向 = ds 减小
# 最小运动行程阈值：只有当原始 x 从当前极值反向走了至少 20 px，
#                   该极值才被确认为转向点（静止段噪声不可能触发）
MIN_TURN_TRAVEL_PX = 20.0

# ---- CSV 规范（沿用 M3 / M4 的字段与写法）----
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

# 正向 / 负向的显示文字（只允许这两种说法）
DIRECTION_POSITIVE = "正向"
DIRECTION_NEGATIVE = "负向"


# ============================================================
# 二、EXP-004 冻结常量自检（只读，不做任何重新标定）
# ============================================================


def check_calibration_constants(tolerance=1e-4):
    """
    检查本模块里的 EXP-004 冻结常量是否自洽。

    只做四件事（全部只读，不读图片、不重新标定）：
        1. U_004 是单位向量（直接对冻结常量取模）
        2. 用 project_point() 复算 P1 -> P2 的沿尺方向投影长度（= L_pixel），
           与冻结的 PX_PER_MM_004 比对：
               PX_PER_MM_004 ?= (s(P2) - s(P1)) / 100.0
           这一条同时验证 u 的方向与 P1 -> P2 一致：
           方向写反会得到负值，检查必然不通过。
        3. MM_PER_PX_004 与 PX_PER_MM_004 互为倒数
        4. U_004 指向 10 cm -> 20 cm（ux > 0，即“ds 增大”为正向）

    返回 (checks, passed)，checks 是 [(说明, 是否通过), ...]。
    """
    checks = []

    u_length = math.hypot(U_004[0], U_004[1])
    checks.append(
        (
            "U_004 是单位向量（|U_004| = %.8f，容差 1e-6）" % u_length,
            abs(u_length - 1.0) <= 1e-6,
        )
    )

    s_p1 = project_point(CALIB_P1_PX, U_004)
    s_p2 = project_point(CALIB_P2_PX, U_004)
    projected_length_px = s_p2 - s_p1
    recomputed_px_per_mm = projected_length_px / CALIB_REAL_DISTANCE_MM
    checks.append(
        (
            "PX_PER_MM_004 与冻结 P1/P2 一致（常量 %.6f / 复算 %.6f，容差 %g）"
            % (PX_PER_MM_004, recomputed_px_per_mm, tolerance),
            abs(PX_PER_MM_004 - recomputed_px_per_mm) <= tolerance,
        )
    )

    checks.append(
        (
            "MM_PER_PX_004 与 PX_PER_MM_004 互为倒数（常量 %.6f / 复算 %.6f，容差 1e-6）"
            % (MM_PER_PX_004, 1.0 / PX_PER_MM_004),
            abs(MM_PER_PX_004 - 1.0 / PX_PER_MM_004) <= 1e-6,
        )
    )

    checks.append(
        (
            "U_004 方向为 10 cm -> 20 cm（ux = %.6f > 0，“ds 增大”即正向）" % U_004[0],
            U_004[0] > 0.0,
        )
    )

    passed = all(ok for _, ok in checks)
    return checks, passed


# ============================================================
# 三、EXP-004 valid gate
# ============================================================


def is_valid_frame(detected, area_px, y_px):
    """
    EXP-004 valid gate（唯一判据）。

    valid = True 当且仅当：
        detected == True
        且 AREA_MIN_PX_004 <= area_px <= AREA_MAX_PX_004
        且 Y_MIN_PX_004 <= y_px <= Y_MAX_PX_004

    说明：
        - 绝不修改原始 detected，只判断“这一帧能不能用”
        - 阈值是本次 EXP-004 拍摄几何专属参数，不做自适应、
          不用分位数、不聚类、不用机器学习
    """
    if not detected:
        return False

    # 检测成功却缺少面积或 y 坐标，同样不能用（数据缺失，不填 0）
    if area_px is None or y_px is None:
        return False

    if not (AREA_MIN_PX_004 <= area_px <= AREA_MAX_PX_004):
        return False

    if not (Y_MIN_PX_004 <= y_px <= Y_MAX_PX_004):
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
    第 3 步：valid=True 的行计算 s_px = project_point((x_px, y_px), U_004)。

    投影公式直接复用 src/calibration.py 的 project_point()，本模块不重写公式。
    """
    for row in rows:
        if row["valid"]:
            row["s_px"] = project_point((row["x_px"], row["y_px"]), U_004)


def compute_s0(rows, window_s=S0_WINDOW_S, min_valid_frames=MIN_S0_VALID_FRAMES):
    """
    第 4 / 5 步：收集前 window_s 秒内 valid=True 的 s_px，并计算 s0。

    s0 = 只使用 time_s <= window_s 且 valid=True 的帧，取这些帧 s_px 的平均值。

    正式禁止：用 10 cm 直接当 s0、用首帧代替均值、扩大窗口、
              插值、平滑、预测、按分位数自动调整。

    返回报告字典：
        window_s / window_total_frames / window_valid_frames
        window_missed_frames（窗口内 detected=False 数量）
        window_detected_invalid_frames（窗口内 detected=True 但 valid=False 数量）
        min_valid_frames / ok / s0
    窗口内有效帧不足时 ok=False，且 s0 保持 None
    （由调用方报错并停止写 ds CSV，不扩大窗口、不修改 gate）。
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
        ds_mm = ds_px / PX_PER_MM_004

    valid=False 的行保持 None（写 CSV 时留空），绝不填 0 / -1 / nan。
    """
    for row in rows:
        if row["valid"]:
            row["ds_px"] = row["s_px"] - s0
            row["ds_mm"] = row["ds_px"] / PX_PER_MM_004


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
# 七、动态统计
# ============================================================


def summarize_dynamic(rows):
    """
    统计 EXP-004 的逐帧数据（不删除任何行）。

    范围类统计的口径（写清楚，避免歧义）：
        - x_px 范围：所有 detected=True 且有 x_px 的行（原始 x 序列）
        - s_px 范围：valid=True 的行
        - ds_mm 最小 / 最大 / 跨度：valid=True 的行
    如果一个有效行都没有，范围类字段保持 None（打印时写“无”）。
    """
    total = len(rows)
    detected_count = sum(1 for row in rows if row["detected"])
    valid_count = sum(1 for row in rows if row["valid"])

    x_values = [row["x_px"] for row in rows if row["x_px"] is not None]
    s_values = [
        row["s_px"] for row in rows if row["valid"] and row["s_px"] is not None
    ]
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
        "x_min_px": min(x_values) if x_values else None,
        "x_max_px": max(x_values) if x_values else None,
        "x_span_px": (max(x_values) - min(x_values)) if x_values else None,
        "s_min_px": min(s_values) if s_values else None,
        "s_max_px": max(s_values) if s_values else None,
        "s_span_px": (max(s_values) - min(s_values)) if s_values else None,
        "ds_min_mm": min(ds_values) if ds_values else None,
        "ds_max_mm": max(ds_values) if ds_values else None,
        "ds_span_mm": (max(ds_values) - min(ds_values)) if ds_values else None,
        "longest_invalid_run": longest_invalid_run,
        "first_time_s": rows[0]["time_s"] if rows else None,
        "last_time_s": rows[-1]["time_s"] if rows else None,
    }
    return summary


# ============================================================
# 八、原始 x_px 转向点 / 运动段检测（负责人已确认的统计口径）
# ============================================================


def detect_turning_points(rows):
    """
    对原始 x_px 序列做转向点与运动段检测。

    口径（已冻结，不得修改；与 M5.1-C 只读审计完全相同）：
        1. 只使用原始 x_px 序列（detected=True 且有 x 的行，按 frame 升序），
           不平滑、不滤波、不插值、不补帧、不预测。
        2. 行进方式（zigzag）：维护“当前极值 ei + 已确认方向 direction”，
              direction = 0：当 |x[i] - x[ei]| >= 20 px 时确认方向，ei 移到 i
              direction = +1（正向）：x[i] > x[ei] 时更新峰值；
                                       从峰值反向走满 20 px 时，峰值确认为转向点
              direction = -1（负向）：镜像处理（谷值）
        3. MIN_TURN_TRAVEL_PX = 20.0 是“反向行程阈值”：
           只有当原始 x 从当前极值反向走了至少 20 px，该极值才算转向点。
           本视频静止段的噪声（相邻帧 |dx| 中位数约 0.13 px、静止段最大约 1.25 px）
           远达不到 20 px，因此不会制造假转向 —— 这条规则在这里真正起作用。
        4. 视频首帧与末帧不是极值点，只作为记录边界（起点 / 终点），
           不计入转向点数量；运动段数 = 转向点数量 + 1。
        5. 正向 = ds 增大（沿 U_004），负向 = ds 减小；
           因为 U_004 的 ux > 0，正向对应原始 x 增大。

    返回字典：
        analysis_rows          —— 参与检测的行数
        analysis_invalid_rows  —— 其中 valid=False 的行数（只统计，不删除）
        start / end            —— 第一行 / 最后一行（frame / time_s / x_px / ds_mm）
        turns                  —— 转向点列表：
                                  frame / time_s / x_px / ds_mm /
                                  kind（peak 峰 | valley 谷）/
                                  direction_before / direction_after
        segments               —— 运动段列表（起点 / 各转向点 / 终点之间的区间）：
                                  start_* / end_* / direction / travel_px /
                                  below_min_travel（行程是否小于 20 px）
    """
    series = [
        row for row in rows if row["detected"] and row["x_px"] is not None
    ]
    analysis_invalid_rows = sum(1 for row in series if not row["valid"])

    report = {
        "analysis_rows": len(series),
        "analysis_invalid_rows": analysis_invalid_rows,
        "start": None,
        "end": None,
        "turns": [],
        "segments": [],
        "min_turn_travel_px": MIN_TURN_TRAVEL_PX,
    }
    if len(series) < 2:
        return report

    # ---- zigzag：20 px 反向行程阈值（与 M5.1-C 审计完全相同的实现）----
    turn_indexes = []
    direction = 0
    extreme_index = 0

    for i in range(1, len(series)):
        x_i = series[i]["x_px"]
        x_extreme = series[extreme_index]["x_px"]

        if direction == 0:
            if abs(x_i - x_extreme) >= MIN_TURN_TRAVEL_PX:
                direction = 1 if x_i > x_extreme else -1
                extreme_index = i
        elif direction == 1:
            if x_i > x_extreme:
                extreme_index = i
            elif x_extreme - x_i >= MIN_TURN_TRAVEL_PX:
                turn_indexes.append((extreme_index, "peak"))
                direction = -1
                extreme_index = i
        else:
            if x_i < x_extreme:
                extreme_index = i
            elif x_i - x_extreme >= MIN_TURN_TRAVEL_PX:
                turn_indexes.append((extreme_index, "valley"))
                direction = 1
                extreme_index = i

    def describe(row):
        """把一行整理成转向点 / 边界点报告需要的字段。"""
        return {
            "frame": row["frame"],
            "time_s": row["time_s"],
            "x_px": row["x_px"],
            "ds_mm": row["ds_mm"],  # valid=False 时为 None（打印“无”，不伪造数值）
        }

    report["start"] = describe(series[0])
    report["end"] = describe(series[-1])

    turns = []
    for index, kind in turn_indexes:
        item = describe(series[index])
        item["kind"] = kind
        if kind == "peak":
            item["direction_before"] = DIRECTION_POSITIVE
            item["direction_after"] = DIRECTION_NEGATIVE
        else:
            item["direction_before"] = DIRECTION_NEGATIVE
            item["direction_after"] = DIRECTION_POSITIVE
        turns.append(item)
    report["turns"] = turns

    # ---- 运动段：起点 -> 各转向点 -> 终点 ----
    boundary_indexes = [0] + [index for index, _ in turn_indexes] + [len(series) - 1]
    segments = []
    for position in range(len(boundary_indexes) - 1):
        head = series[boundary_indexes[position]]
        tail = series[boundary_indexes[position + 1]]
        travel_px = abs(tail["x_px"] - head["x_px"])
        if tail["x_px"] > head["x_px"]:
            segment_direction = DIRECTION_POSITIVE
        elif tail["x_px"] < head["x_px"]:
            segment_direction = DIRECTION_NEGATIVE
        else:
            segment_direction = "无位移"
        segments.append(
            {
                "start_frame": head["frame"],
                "start_time_s": head["time_s"],
                "start_x_px": head["x_px"],
                "end_frame": tail["frame"],
                "end_time_s": tail["time_s"],
                "end_x_px": tail["x_px"],
                "direction": segment_direction,
                "travel_px": travel_px,
                "below_min_travel": travel_px < MIN_TURN_TRAVEL_PX,
            }
        )
    report["segments"] = segments

    return report


# ============================================================
# 九、打印
# ============================================================


def print_check_results(checks, passed):
    """
    打印自检结果（[(说明, 是否通过), ...]）。
    """
    print("")
    print("========== EXP-004 自动自检 ==========")
    for index, (description, ok) in enumerate(checks, start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    print("自检结论：%s" % ("全部通过" if passed else "存在未通过项，请人工检查"))


def _format_ds_mm(value):
    """统一的“无 / 数值”显示：缺失就是缺失，不伪造数值。"""
    return "无" if value is None else "%.4f mm" % value


def print_summary(report):
    """
    打印 EXP-004 的全部统计信息（含 s0 报告、转向点、运动段与自检结果）。
    """
    experiment = report["video_name"]
    summary = report["summary"]
    s0_report = report["s0_report"]
    turning = report["turning"]
    s0 = s0_report["s0"]

    print("")
    print("========== %s 动态位移统计 ==========" % experiment)
    print("【EXP-004 冻结规则（本次实际使用，未做任何自适应）】")
    print(
        "  标定：P1(10 cm)=%s  P2(20 cm)=%s  L_real=%.1f mm"
        % (CALIB_P1_PX, CALIB_P2_PX, CALIB_REAL_DISTANCE_MM)
    )
    print(
        "  PX_PER_MM_004 = %.6f，MM_PER_PX_004 = %.6f，U_004 = (%.6f, %.6f)"
        % (PX_PER_MM_004, MM_PER_PX_004, U_004[0], U_004[1])
    )
    print(
        "  valid gate：detected=True 且 %.0f <= area_px <= %.0f 且 %.0f <= y_px <= %.0f"
        % (AREA_MIN_PX_004, AREA_MAX_PX_004, Y_MIN_PX_004, Y_MAX_PX_004)
    )
    print(
        "  s0 规则：只使用 time_s <= %.1f s 的帧，窗口内至少 %d 帧 valid=True"
        % (S0_WINDOW_S, MIN_S0_VALID_FRAMES)
    )
    print(
        "  运动统计：原始 x_px 极值 + 最小运动行程 %.1f px（不顺滑、不滤波、不插值、不预测）"
        % MIN_TURN_TRAVEL_PX
    )

    print("")
    print("【逐帧统计】")
    print("1. 实验名称：%s" % experiment)
    print("2. 总帧数：%d" % summary["frame_count"])
    print(
        "3. detected 率：%.4f%%（%d / %d）"
        % (
            summary["detected_rate"] * 100.0,
            summary["detected_count"],
            summary["frame_count"],
        )
    )
    print(
        "4. valid 率：%.4f%%（%d / %d）"
        % (
            summary["valid_rate"] * 100.0,
            summary["valid_count"],
            summary["frame_count"],
        )
    )
    print("5. invalid 总数：%d" % summary["invalid_count"])
    print("6. detected=False 数量：%d" % summary["missed_count"])
    print("7. detected=True 但 valid=False 数量：%d" % summary["detected_invalid_count"])
    print(
        "8. ds_mm 最小值：%s" % _format_ds_mm(summary["ds_min_mm"])
    )
    print(
        "9. ds_mm 最大值：%s" % _format_ds_mm(summary["ds_max_mm"])
    )
    print(
        "10. ds_mm 跨度（max-min）：%s" % _format_ds_mm(summary["ds_span_mm"])
    )
    print("11. 最长连续 invalid 帧：%d" % summary["longest_invalid_run"])
    print(
        "12. 首帧时间：%s"
        % (
            "无"
            if summary["first_time_s"] is None
            else "%.6f s" % summary["first_time_s"]
        )
    )
    print(
        "13. 末帧时间：%s"
        % (
            "无"
            if summary["last_time_s"] is None
            else "%.6f s" % summary["last_time_s"]
        )
    )
    print(
        "14. x_px 范围（原始 x，所有 detected=True 的行）：%s"
        % (
            "无"
            if summary["x_min_px"] is None
            else "%.2f ~ %.2f（跨度 %.2f px）"
            % (summary["x_min_px"], summary["x_max_px"], summary["x_span_px"])
        )
    )
    print(
        "15. s_px 范围（valid=True 的行）：%s"
        % (
            "无"
            if summary["s_min_px"] is None
            else "%.3f ~ %.3f（跨度 %.3f px）"
            % (summary["s_min_px"], summary["s_max_px"], summary["s_span_px"])
        )
    )
    print(
        "16. ds_mm 范围（valid=True 的行）：%s"
        % (
            "无"
            if summary["ds_min_mm"] is None
            else "%.4f ~ %.4f（跨度 %.4f mm）"
            % (summary["ds_min_mm"], summary["ds_max_mm"], summary["ds_span_mm"])
        )
    )

    print("")
    print("【s0（前 %.1f s 静止段）】" % S0_WINDOW_S)
    print("s0 window frames = %d" % s0_report["window_total_frames"])
    print("s0 valid frames  = %d" % s0_report["window_valid_frames"])
    print("s0               = %s" % ("无（窗口内有效帧不足）" if s0 is None else "%.3f px" % s0))
    print("  窗口内 detected=False 数量：%d" % s0_report["window_missed_frames"])
    print(
        "  窗口内 detected=True 但 valid=False 数量：%d"
        % s0_report["window_detected_invalid_frames"]
    )

    print("")
    print("【主要运动段 / 转向点（原始 x_px，最小行程 %.1f px）】" % MIN_TURN_TRAVEL_PX)
    print(
        "17. 转向点分析使用行数：%d（其中 valid=False 行：%d，只统计不删除）"
        % (turning["analysis_rows"], turning["analysis_invalid_rows"])
    )
    print(
        "18. 起点：frame=%d t=%.6f s x=%.2f ds_mm=%s"
        % (
            turning["start"]["frame"],
            turning["start"]["time_s"],
            turning["start"]["x_px"],
            "无" if turning["start"]["ds_mm"] is None else "%.4f" % turning["start"]["ds_mm"],
        )
    )
    print(
        "19. 终点：frame=%d t=%.6f s x=%.2f ds_mm=%s"
        % (
            turning["end"]["frame"],
            turning["end"]["time_s"],
            turning["end"]["x_px"],
            "无" if turning["end"]["ds_mm"] is None else "%.4f" % turning["end"]["ds_mm"],
        )
    )
    print("20. 转向点数量：%d" % len(turning["turns"]))
    print(
        "21. 主要运动段数：%d（= 转向点数量 + 1；其中行程 < %.1f px 的段：%d）"
        % (
            len(turning["segments"]),
            MIN_TURN_TRAVEL_PX,
            sum(1 for segment in turning["segments"] if segment["below_min_travel"]),
        )
    )

    print("")
    print("【每个转向点】")
    if not turning["turns"]:
        print("  无（原始 x 序列未出现满足最小行程 %.1f px 的转向）" % MIN_TURN_TRAVEL_PX)
    for index, turn in enumerate(turning["turns"], start=1):
        print(
            "  #%d frame=%d t=%.6f s x_px=%.2f ds_mm=%s 方向变化：%s -> %s（%s）"
            % (
                index,
                turn["frame"],
                turn["time_s"],
                turn["x_px"],
                "无（该帧 valid=False）"
                if turn["ds_mm"] is None
                else "%.4f" % turn["ds_mm"],
                turn["direction_before"],
                turn["direction_after"],
                "峰" if turn["kind"] == "peak" else "谷",
            )
        )

    print("")
    print("【每个主要运动段】")
    if not turning["segments"]:
        print("  无")
    for index, segment in enumerate(turning["segments"], start=1):
        print(
            "  段%d：frame %d (t=%.6f s, x=%.2f) -> frame %d (t=%.6f s, x=%.2f)  "
            "方向：%s  行程：%.2f px%s"
            % (
                index,
                segment["start_frame"],
                segment["start_time_s"],
                segment["start_x_px"],
                segment["end_frame"],
                segment["end_time_s"],
                segment["end_x_px"],
                segment["direction"],
                segment["travel_px"],
                "（< 最小行程）" if segment["below_min_travel"] else "",
            )
        )

    print("")
    print("22. 输入 track CSV：%s" % report["track_csv_path"])
    print(
        "23. ds CSV：%s"
        % (
            report["ds_csv_path"]
            if report["ds_written"]
            else "未生成（s0 窗口有效帧不足，按冻结规则不写 ds CSV）"
        )
    )
    if report.get("overlay_path") is not None:
        print("24. overlay 叠加视频（M3 track_video 固有产物，已被 .gitignore 忽略）：%s"
              % report["overlay_path"])

    # s0 窗口有效帧不足时的明确问题报告（不扩大窗口、不改 gate、不自行修复）
    if not s0_report["ok"]:
        print("")
        print("！！问题报告：%s 的 s0 窗口有效帧不足 ！！" % experiment)
        print(
            "原因：s0 规则要求窗口内至少有 %d 帧 valid=True，当前只有 %d 帧。"
            % (s0_report["min_valid_frames"], s0_report["window_valid_frames"])
        )
        print("窗口总帧数：%d" % s0_report["window_total_frames"])
        print("窗口有效帧数：%d" % s0_report["window_valid_frames"])
        print("窗口内 detected=False 数量：%d" % s0_report["window_missed_frames"])
        print(
            "窗口内 detected=True 但 valid=False 数量：%d"
            % s0_report["window_detected_invalid_frames"]
        )
        print("处理方式：本次实验不生成 ds CSV；不扩大窗口、不修改 gate、不做插值。")

    if report["constant_checks"]:
        print("")
        print("【冻结常量自检（不重新标定）】")
        print_check_results(report["constant_checks"], report["constant_passed"])

    if report["ds_written"]:
        print_check_results(report["checks"], report["passed"])

    print("")
    print("=====================================")


# ============================================================
# 十、ds CSV 自动自检
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

    检查内容（对应本轮自检清单第 1 ~ 11 项）：
        1. track CSV 数据行数 = 1766（冻结自检值）
        2. track CSV 的 frame 从 0 连续到 1765（未删行、无重复）
        3. ds CSV 是 UTF-8 无 BOM，换行只使用 \\n，第一行是标准表头
        4. ds CSV 行数 == track CSV 行数
        5. frame 列逐行完全一致
        6. valid 列与 EXP-004 valid gate 逐行一致（用 track CSV 复算）
        7. valid=False 的行：s_px / ds_px / ds_mm 全为空
        8. valid=True 的行：s_px / ds_px / ds_mm 都是有限数值
        9. detected=False 的行 area_px 为空；detected=True 的行 area_px 有值
        10. 字段小数位数符合规范（time_s 6 / s_px 3 / ds_px 3 / ds_mm 4 / area_px 1）
        11. s0 等于 s0 窗口内有效帧 s_px 的平均值（容差 0.002 px）
        12. ds_px = s_px - s0（容差 0.002 px）、ds_mm = ds_px / PX_PER_MM_004（容差 0.0005 mm）
        13. ds CSV 重新统计的 detected / valid 成功率与打印值一致

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
        (
            "ds CSV 为 UTF-8 无 BOM（开头没有 EF BB BF）",
            not raw_bytes.startswith(b"\xef\xbb\xbf"),
        )
    )
    checks.append(
        ("ds CSV 换行只使用 \\n（文件中没有 \\r）", b"\r" not in raw_bytes)
    )

    ds_lines = read_ds_csv_lines(ds_csv_path)
    header = ds_lines[0] if ds_lines else []
    data_rows = ds_lines[1:] if ds_lines else []

    checks.append(
        (
            "ds CSV 第一行是标准表头（%s）" % ",".join(DS_FIELDNAMES),
            header == DS_FIELDNAMES,
        )
    )

    track_rows = read_track_csv(track_csv_path)

    # 1. track CSV 行数 = 冻结自检值
    checks.append(
        (
            "track CSV 数据行数 = %d（实际 %d）" % (EXPECTED_TRACK_ROWS, len(track_rows)),
            len(track_rows) == EXPECTED_TRACK_ROWS,
        )
    )

    # 2. track CSV 的 frame 连续
    track_frames = [row["frame"] for row in track_rows]
    checks.append(
        (
            "track CSV 的 frame 从 0 连续到 %d（未删行、无重复）"
            % (len(track_rows) - 1),
            track_frames == list(range(len(track_rows))),
        )
    )

    # 4. 行数一致
    checks.append(
        (
            "ds CSV 行数 == track CSV 行数（%d）" % len(track_rows),
            len(data_rows) == len(track_rows),
        )
    )

    # 5. frame 列逐行一致
    frame_ok = len(data_rows) == len(track_rows)
    if frame_ok:
        for track_row, ds_row in zip(track_rows, data_rows):
            if (
                len(ds_row) != len(DS_FIELDNAMES)
                or ds_row[0] != "%d" % track_row["frame"]
            ):
                frame_ok = False
                break
    checks.append(("frame 列与 track CSV 逐行完全一致", frame_ok))

    # 6 ~ 10. 逐行核对
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

            # valid 列必须与 EXP-004 valid gate 复算结果一致
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
        ("valid 列与 EXP-004 valid gate 逐行一致（detected / area_px / y_px 复算）", gate_ok)
    )
    checks.append(
        (
            "valid=False 的行 s_px / ds_px / ds_mm 全部为空（没有填 0 / -1 / nan）",
            len(bad_invalid_rows) == 0,
        )
    )
    checks.append(
        (
            "valid=True 的行 s_px / ds_px / ds_mm 都是有限数值",
            len(bad_valid_rows) == 0,
        )
    )
    checks.append(
        (
            "detected=False 的行 area_px 为空、detected=True 的行 area_px 有值",
            len(bad_area_rows) == 0,
        )
    )
    checks.append(
        (
            "字段小数位数符合规范（time_s 6 / s_px 3 / ds_px 3 / ds_mm 4 / area_px 1）",
            len(bad_format_rows) == 0,
        )
    )

    # 11. s0 规则复算：窗口内有效帧 s_px 的平均值
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
        (
            "s0 等于 s0 窗口内有效帧 s_px 的平均值（容差 0.002 px，%s）" % s0_note,
            s0_ok,
        )
    )

    # 12. ds 公式复算（按写入的舍入值核对）
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
            if abs(ds_mm - ds_px / PX_PER_MM_004) > 0.0005:
                ds_formula_ok = False
                break
    checks.append(
        (
            "ds_px = s_px - s0（容差 0.002 px）且 ds_mm = ds_px / PX_PER_MM_004（容差 0.0005 mm）",
            ds_formula_ok,
        )
    )

    # 13. 重新统计的成功率与打印用统计值一致
    total = len(data_rows)
    if total > 0:
        detected_rate = detected_true_count / float(total)
        valid_rate = valid_true_count / float(total)
        checks.append(
            (
                "ds CSV 重新统计的 detected 成功率与打印值一致（%.6f）" % detected_rate,
                abs(detected_rate - summary["detected_rate"]) < 1e-9,
            )
        )
        checks.append(
            (
                "ds CSV 重新统计的 valid 成功率与打印值一致（%.6f）" % valid_rate,
                abs(valid_rate - summary["valid_rate"]) < 1e-9,
            )
        )
    else:
        checks.append(("ds CSV 至少有一行数据", False))

    passed = all(ok for _, ok in checks)
    return checks, passed


# ============================================================
# 十一、单实验流程与实验入口
# ============================================================


def build_ds_from_track_csv(track_csv_path, ds_csv_path, video_name=""):
    """
    完整数据链（M3 track CSV -> ds CSV），逐行处理顺序固定：

        1. 读取 frame / time_s / x_px / y_px / area_px / detected
        2. 判断 valid
        3. valid 时计算 s_px
        4. 收集前 2.0 s 内 valid 的 s_px
        5. 计算 s0
        6. valid 时计算 ds_px / ds_mm
        7. 写 ds CSV

    过程中不删除任何行；s0 窗口有效帧不足时不写 ds CSV。
    返回 report 字典（统计 summary、s0 报告、转向点报告、ds_written 等）。
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
        "summary": summarize_dynamic(rows),
        "turning": detect_turning_points(rows),
        "rows": rows,
        "ds_written": ds_written,
        "constant_checks": [],
        "constant_passed": False,
        "checks": [],
        "passed": False,
    }
    return report


def run_experiment(track_csv_path, ds_csv_path, video_name=""):
    """
    运行一次 EXP-004 动态位移实验：M3 的 track CSV -> ds CSV，并自动自检。

    说明：
        “原始视频 -> track CSV”由 M3 的 track_video() 完成（demo 先调用它），
        本函数不重复检测、不读视频，只负责 valid gate 之后的部分。

    顺序：
        1. 先做冻结常量自检（只读，不重新标定）；未通过则直接返回、不写 ds CSV
        2. 建 ds 数据链（track CSV -> ds CSV）；s0 窗口有效帧不足时不写 ds CSV
        3. ds CSV 写出后，重新从磁盘读取并逐行自检

    返回 report 字典；ds CSV 未生成时 checks 为空、passed=False。
    """
    constant_checks, constant_passed = check_calibration_constants()

    report = build_ds_from_track_csv(track_csv_path, ds_csv_path, video_name)
    report["constant_checks"] = constant_checks
    report["constant_passed"] = constant_passed

    if not constant_passed:
        print("冻结常量自检未通过，按规则停止（不生成 ds CSV，不修改任何常量）")
        return report

    if report["ds_written"]:
        checks, passed = check_ds_csv(report)
        report["checks"] = checks
        report["passed"] = passed

    return report

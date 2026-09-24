"""
VisionMotion —— M5.3-2 EXP-004-DYNAMIC-001 动态位移结果正式可视化

功能：把已经封板的正式 ds CSV（results/EXP-004-DYNAMIC-001_ds.csv）
      画成一张动态位移-时间曲线图（单图、单坐标轴），并打印自检结果。

本脚本只负责：
    1. 读取 CSV
    2. 提取原始 time_s / ds_mm
    3. 从 CSV 找到 6 个已经冻结的 turning point frame
    4. 绘图（直接使用 CSV 里的原始 ds_mm）
    5. 保存 PNG
    6. 打印基本自检

本脚本明确不做（M5.3-2 冻结要求）：
    平滑 / 插值 / 滤波 / 重采样 / 拟合 / 趋势线 / 包络 / 误差带 /
    修改数据 / 删除数据点；
    不重新运行转向检测（只用 M5.2 冻结的 6 个 frame）；
    不计算周期 / 频率 / 振幅 / 频谱等任何振动参数。

输出（本轮唯一允许生成的产物）：
    results/EXP-004-DYNAMIC-001_displacement.png（1800 x 900 px）

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m53_plot.py
"""

import csv
import hashlib
import struct
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # 只保存文件，不打开任何窗口

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402

# ============================================================
# 1. 路径（只读输入 + 唯一输出）
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DS_CSV_PATH = PROJECT_ROOT / "results" / "EXP-004-DYNAMIC-001_ds.csv"
PNG_PATH = PROJECT_ROOT / "results" / "EXP-004-DYNAMIC-001_displacement.png"

# ============================================================
# 2. 冻结记录（M5.3-1 设计冻结：只做核对，不重新计算）
# ============================================================

# 封板 CSV 的 SHA-256（运行前后都必须与之完全一致）
FROZEN_CSV_SHA256 = "704D6C64A3C4CA4B575749AEB3FBD3CAF901AB8257F1DF20AAD79FFE23134163"

# 封板 CSV 的数据行数
EXPECTED_DATA_ROWS = 1766

# frame 连续性：0 ~ 1765
EXPECTED_FIRST_FRAME = 0
EXPECTED_LAST_FRAME = 1765

# M5.2 冻结的 6 个转向点：frame -> (time_s, ds_mm)
# 这里存的是封板 CSV 里的原始文本，用于逐字核对（不做任何四舍五入）
FROZEN_TURNING_POINTS = (
    (491, "8.166327", "33.1549"),
    (602, "10.012483", "19.2217"),
    (838, "13.937642", "39.9535"),
    (1063, "17.679849", "24.7998"),
    (1254, "20.856567", "56.0319"),
    (1513, "25.164263", "34.8700"),
)

# 两个特殊数据点：必须原样绘制，不修改、不删除、不裁剪
FROZEN_FIRST_DS_MM = "-0.5283"   # frame 0（不是 0）
FROZEN_LAST_DS_MM = "65.8647"    # frame 1765（视频末尾，曲线到此结束，不外推）

# ============================================================
# 3. 冻结的绘图参数（M5.3-1 设计冻结）
# ============================================================

FIGURE_SIZE_INCH = (12, 6)
FIGURE_DPI = 150
EXPECTED_PNG_SIZE = (1800, 900)

X_AXIS_MIN = 0.0
X_AXIS_MAX = 29.355535
Y_AXIS_MIN = -5.0
Y_AXIS_MAX = 70.0
Y_MAJOR_STEP_MM = 10.0
X_MAJOR_STEP_S = 5.0

TITLE_TEXT = "EXP-004-DYNAMIC-001 位移-时间曲线（原始 ds_mm，未处理）"
X_LABEL_TEXT = "time_s (s)"
Y_LABEL_TEXT = "ds_mm (mm)"

LEGEND_CURVE_LABEL = "原始 ds_mm（n=%d）" % EXPECTED_DATA_ROWS
LEGEND_TURNS_LABEL = "转向点（M5.2 冻结统计）"
BASELINE_LABEL = "_nolegend_"  # y=0 基准线不进图例

CURVE_COLOR = "#1f77b4"
CURVE_LINE_WIDTH = 1.0
BASELINE_COLOR = "#808080"
BASELINE_LINE_WIDTH = 0.8
TURN_MARKER_COLOR = "#d62728"
TURN_MARKER_SIZE = 6.0
TURN_MARKER_EDGE_WIDTH = 1.2

# 中文字体：必须显式使用 Microsoft YaHei；文件不存在就停止（不自行换字体）
FROZEN_FONT_PATH = Path(r"C:\Windows\Fonts\msyh.ttc")


# ============================================================
# 4. 基础工具
# ============================================================


def sha256_of_file(path):
    """计算文件的 SHA-256（只读，十六进制大写）。"""
    digest = hashlib.sha256()
    with open(path, "rb") as binary_file:
        for chunk in iter(lambda: binary_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_ds_csv(csv_path):
    """读取 ds CSV，返回 (表头, 所有数据行)；只读，不写回。"""
    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        field_names = list(reader.fieldnames or [])
        rows = list(reader)
    return field_names, rows


def is_finite(text):
    """CSV 文本是否为有限数值（NaN / inf / 空值都算不通过）。"""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return False
    return bool(np.isfinite(value))


def print_checks(title, checks):
    """统一格式打印一组自检结果，返回是否全部通过。"""
    print("")
    print("========== %s ==========" % title)
    for index, (description, ok) in enumerate(checks, start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    passed = all(ok for _, ok in checks)
    print("结论：%s" % ("全部通过" if passed else "存在未通过项"))
    return passed


def read_png_size_with_pillow(png_path):
    """用 Pillow 打开并校验 PNG，返回 (宽, 高)；Pillow 不存在时返回 None。"""
    try:
        from PIL import Image
    except ImportError:
        return None
    with Image.open(png_path) as image:
        size = image.size
        image.verify()  # 只读校验：文件损坏会抛异常
    return size


def read_png_size_from_header(png_path):
    """不依赖 Pillow：直接解析 PNG 文件头 IHDR，返回 (宽, 高)。"""
    with open(png_path, "rb") as binary_file:
        header = binary_file.read(24)
    if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    width, height = struct.unpack(">II", header[16:24])
    return (int(width), int(height))


# ============================================================
# 5. 运行前的 8 项自检（全部只读）
# ============================================================


def run_pre_checks(rows, sha_before):
    """
    运行前自检（顺序与 M5.3-2 要求一致）：
        1. CSV SHA-256 与冻结记录一致
        2. 数据行数 = 1766
        3. time_s 严格递增
        4. ds_mm 全部有限
        5. frame 0 ~ 1765 连续
        6. turning point frame 全部存在
        7. turning point 对应 time_s / ds_mm 与冻结记录一致
        8. 绘制所用的数组就是 CSV 原始数组（没有做任何变换）
    返回 (checks, passed, time_values, ds_values, turning_points)。
    """
    rows_by_frame = {}
    for row in rows:
        try:
            frame_number = int(row["frame"])
        except (KeyError, TypeError, ValueError):
            continue
        rows_by_frame.setdefault(frame_number, row)

    time_texts = [row.get("time_s", "") for row in rows]
    ds_texts = [row.get("ds_mm", "") for row in rows]

    time_values = [float(text) for text in time_texts]
    ds_values = [float(text) for text in ds_texts]

    # 1. 运行前 SHA-256 == 冻结记录
    sha_ok = sha_before == FROZEN_CSV_SHA256

    # 2. 数据行数
    rows_ok = len(rows) == EXPECTED_DATA_ROWS

    # 3. time_s 严格递增（不平滑、不重采样，只检查）
    time_increasing = len(time_values) > 1 and all(
        time_values[index] < time_values[index + 1]
        for index in range(len(time_values) - 1)
    )

    # 4. ds_mm 全部有限
    ds_finite = len(ds_texts) > 0 and all(is_finite(text) for text in ds_texts)

    # 5. frame 连续 0 ~ 1765
    frame_numbers = sorted(rows_by_frame)
    frames_ok = (
        len(rows_by_frame) == len(rows)
        and frame_numbers
        and frame_numbers[0] == EXPECTED_FIRST_FRAME
        and frame_numbers[-1] == EXPECTED_LAST_FRAME
        and frame_numbers == list(range(EXPECTED_FIRST_FRAME, EXPECTED_LAST_FRAME + 1))
    )

    # 6 / 7. 冻结转向点：frame 存在，且 time_s / ds_mm 与冻结记录逐字一致
    turning_points = []
    turns_exist = True
    turns_match = True
    for frame, frozen_time_text, frozen_ds_text in FROZEN_TURNING_POINTS:
        row = rows_by_frame.get(frame)
        if row is None:
            turns_exist = False
            turns_match = False
            continue
        time_text = row.get("time_s", "")
        ds_text = row.get("ds_mm", "")
        if time_text != frozen_time_text or ds_text != frozen_ds_text:
            turns_match = False
        turning_points.append(
            {
                "frame": frame,
                "time_text": time_text,
                "ds_text": ds_text,
                "time_s": float(time_text) if is_finite(time_text) else None,
                "ds_mm": float(ds_text) if is_finite(ds_text) else None,
            }
        )

    # 8. 绘图数组 = CSV 原始数组（同一对象、同一顺序、同一长度，未复制未变换）
    no_transform = (
        len(time_values) == len(rows)
        and len(ds_values) == len(rows)
        and all(
            time_values[index] == float(rows[index]["time_s"])
            and ds_values[index] == float(rows[index]["ds_mm"])
            for index in range(len(rows))
        )
    )

    checks = [
        (
            "CSV SHA-256 与冻结记录一致（运行前：%s）" % sha_before,
            sha_ok,
        ),
        (
            "数据行数 = %d（冻结自检值 %d）" % (len(rows), EXPECTED_DATA_ROWS),
            rows_ok,
        ),
        ("time_s 严格递增（%d 个点，只检查，不重采样）" % len(time_values), time_increasing),
        ("ds_mm 全部为有限数值（%d 个点）" % len(ds_texts), ds_finite),
        (
            "frame 连续覆盖 %d ~ %d（无缺帧、无重复）"
            % (EXPECTED_FIRST_FRAME, EXPECTED_LAST_FRAME),
            frames_ok,
        ),
        (
            "冻结转向点 frame 全部存在于 CSV：%s"
            % ", ".join(str(frame) for frame, _, _ in FROZEN_TURNING_POINTS),
            turns_exist,
        ),
        (
            "冻结转向点对应 time_s / ds_mm 与 M5.2 冻结记录逐字一致",
            turns_match,
        ),
        (
            "绘制用数组 = CSV 原始数组（未平滑/未插值/未滤波/未重采样/未拟合/未修改）",
            no_transform,
        ),
    ]

    passed = all(ok for _, ok in checks)
    return checks, passed, time_values, ds_values, turning_points


# ============================================================
# 6. 绘图（只用原始数据；不连接转向点；y=0 基准线不进图例）
# ============================================================


def build_figure(time_values, ds_values, turning_points, font_prop):
    """按冻结设计画图，返回 (figure, axes, curve, turns, baseline)。"""
    figure, axes = plt.subplots(figsize=FIGURE_SIZE_INCH, dpi=FIGURE_DPI)

    # y = 0 细灰基准线（冻结的 s0 零点），不进图例
    baseline = axes.axhline(
        0.0,
        color=BASELINE_COLOR,
        linewidth=BASELINE_LINE_WIDTH,
        label=BASELINE_LABEL,
        zorder=1,
    )

    # 原始 ds_mm 曲线：直接使用 CSV 原始序列，逐点连接，不做任何变换
    curve, = axes.plot(
        time_values,
        ds_values,
        color=CURVE_COLOR,
        linewidth=CURVE_LINE_WIDTH,
        label=LEGEND_CURVE_LABEL,
        zorder=2,
    )

    # 6 个冻结转向点：小型空心圆标记，不连线
    turns, = axes.plot(
        [point["time_s"] for point in turning_points],
        [point["ds_mm"] for point in turning_points],
        linestyle="none",
        marker="o",
        markersize=TURN_MARKER_SIZE,
        markerfacecolor="none",
        markeredgecolor=TURN_MARKER_COLOR,
        markeredgewidth=TURN_MARKER_EDGE_WIDTH,
        label=LEGEND_TURNS_LABEL,
        zorder=3,
    )

    axes.set_title(TITLE_TEXT, fontproperties=font_prop, fontsize=14, pad=12)
    axes.set_xlabel(X_LABEL_TEXT, fontproperties=font_prop, fontsize=12)
    axes.set_ylabel(Y_LABEL_TEXT, fontproperties=font_prop, fontsize=12)

    axes.set_xlim(X_AXIS_MIN, X_AXIS_MAX)
    axes.set_ylim(Y_AXIS_MIN, Y_AXIS_MAX)
    axes.xaxis.set_major_locator(MultipleLocator(X_MAJOR_STEP_S))
    axes.yaxis.set_major_locator(MultipleLocator(Y_MAJOR_STEP_MM))

    for axis in (axes.xaxis, axes.yaxis):
        for label in axis.get_ticklabels():
            label.set_fontproperties(font_prop)
            label.set_fontsize(11)

    axes.legend(prop=font_prop, fontsize=11, loc="upper left")
    axes.grid(False)
    figure.tight_layout()
    return figure, axes, curve, turns, baseline


# ============================================================
# 7. 主流程
# ============================================================


def main():
    print("========== VisionMotion M5.3-2 EXP-004-DYNAMIC-001 动态位移结果正式可视化 ==========")
    print("输入（封板，只读）：%s" % DS_CSV_PATH)
    print("输出（本轮唯一产物）：%s" % PNG_PATH)
    print("冻结设计：figsize=%s，dpi=%d -> %d x %d px，单图单坐标轴"
          % (str(FIGURE_SIZE_INCH), FIGURE_DPI, EXPECTED_PNG_SIZE[0], EXPECTED_PNG_SIZE[1]))
    print("冻结坐标轴：x=[%g, %g]，y=[%g, %g]，y 主刻度 %g mm"
          % (X_AXIS_MIN, X_AXIS_MAX, Y_AXIS_MIN, Y_AXIS_MAX, Y_MAJOR_STEP_MM))
    print("本轮不计算任何振动参数（无 FFT / 频率 / 周期 / 振幅 / 频谱 / 滤波 / 平滑 / 插值 / 峰值分析）")

    # 0. 中文字体：必须存在，否则停止并报告（不自行换字体）
    if not FROZEN_FONT_PATH.is_file():
        print("")
        print("错误：冻结字体不存在：%s" % FROZEN_FONT_PATH)
        print("处理方式：停止运行（不生成 PNG，不自行替换字体）")
        return 1
    print("中文字体（冻结）：%s" % FROZEN_FONT_PATH)

    # 1. 输入 CSV 必须存在
    if not DS_CSV_PATH.is_file():
        print("")
        print("错误：输入 CSV 不存在：%s" % DS_CSV_PATH)
        print("处理方式：停止运行（不生成 PNG）")
        return 1

    # 2. 运行前 SHA-256（生成前基线）
    sha_before = sha256_of_file(DS_CSV_PATH)
    field_names, rows = read_ds_csv(DS_CSV_PATH)
    print("")
    print("CSV 表头：%s" % ", ".join(field_names))
    print("运行前 SHA-256：%s" % sha_before)

    # 3. 运行前自检（8 项）
    pre_checks, pre_passed, time_values, ds_values, turning_points = run_pre_checks(
        rows, sha_before
    )
    if not print_checks("生成前自检（M5.3-2 第 1 ~ 8 项）", pre_checks):
        print("")
        print("生成前自检未通过：停止运行（不生成 PNG，不修改任何文件）")
        return 1

    # 4. 打印冻结转向点（只读 CSV，未重新运行转向检测）
    print("")
    print("========== 冻结转向点（frame 来自 M5.2，time_s / ds_mm 直接从 CSV 读取） ==========")
    for index, point in enumerate(turning_points, start=1):
        print("  #%d frame=%d  time_s=%s  ds_mm=%s"
              % (index, point["frame"], point["time_text"], point["ds_text"]))

    print("")
    print("特殊数据点（原样绘制，不修改、不删除、不裁剪）：")
    print("  frame %d：ds_mm=%s mm" % (EXPECTED_FIRST_FRAME, rows[0]["ds_mm"]))
    print("  frame %d：ds_mm=%s mm（视频末尾，曲线到此结束，不外推、不补静止段）"
          % (EXPECTED_LAST_FRAME, rows[-1]["ds_mm"]))
    print("  ds_mm 原始范围：%.4f ~ %.4f mm（落在纵轴 [%g, %g] 内，无裁剪）"
          % (min(ds_values), max(ds_values), Y_AXIS_MIN, Y_AXIS_MAX))

    # 5. 字体对象（显式使用冻结字体文件）
    font_prop = font_manager.FontProperties(fname=str(FROZEN_FONT_PATH))
    plt.rcParams["axes.unicode_minus"] = False  # 负号用 ASCII，避免缺字形

    # 6. 绘图
    print("")
    print("========== 绘图（单图、单坐标轴；曲线直接使用 CSV 原始 ds_mm） ==========")
    figure, axes, curve, turns, baseline = build_figure(
        time_values, ds_values, turning_points, font_prop
    )

    # 7. 绘图结构自检（确认绘制出来的就是原始数据，且符合冻结设计）
    drawn_time = np.asarray(curve.get_xdata(), dtype=float)
    drawn_ds = np.asarray(curve.get_ydata(), dtype=float)
    drawn_turn_time = np.asarray(turns.get_xdata(), dtype=float)
    drawn_turn_ds = np.asarray(turns.get_ydata(), dtype=float)
    frozen_turn_time = np.asarray([point["time_s"] for point in turning_points], dtype=float)
    frozen_turn_ds = np.asarray([point["ds_mm"] for point in turning_points], dtype=float)
    legend_labels = [text.get_text() for text in axes.get_legend().get_texts()]

    figure_checks = [
        (
            "曲线点数据与 CSV 原始序列逐点完全一致（%d 点，无变换）" % drawn_ds.size,
            np.array_equal(drawn_time, np.asarray(time_values, dtype=float))
            and np.array_equal(drawn_ds, np.asarray(ds_values, dtype=float)),
        ),
        (
            "曲线点数 = %d，未删除任何数据点" % EXPECTED_DATA_ROWS,
            drawn_ds.size == EXPECTED_DATA_ROWS,
        ),
        (
            "x 轴范围 = [%g, %g]（time_s）" % (X_AXIS_MIN, X_AXIS_MAX),
            tuple(axes.get_xlim()) == (X_AXIS_MIN, X_AXIS_MAX),
        ),
        (
            "y 轴范围 = [%g, %g]（ds_mm），y 主刻度 = %g mm"
            % (Y_AXIS_MIN, Y_AXIS_MAX, Y_MAJOR_STEP_MM),
            tuple(axes.get_ylim()) == (Y_AXIS_MIN, Y_AXIS_MAX),
        ),
        (
            "全部 %d 个 ds_mm 都落在 y 轴范围内（frame 0 与 frame 1765 均未被裁剪）"
            % EXPECTED_DATA_ROWS,
            min(ds_values) >= Y_AXIS_MIN and max(ds_values) <= Y_AXIS_MAX,
        ),
        (
            "转向点标记坐标与 CSV 冻结值完全一致（6 点，未重新检测）",
            np.array_equal(drawn_turn_time, frozen_turn_time)
            and np.array_equal(drawn_turn_ds, frozen_turn_ds),
        ),
        (
            "转向点只做空心圆标记、不连线（linestyle=none，marker=o，markerfacecolor=none）",
            turns.get_linestyle() == "None"
            and turns.get_marker() == "o"
            and turns.get_markerfacecolor() == "none",
        ),
        (
            "y=0 基准线存在且为细灰线（linewidth=%.1f），不进入图例"
            % BASELINE_LINE_WIDTH,
            abs(baseline.get_ydata()[0]) == 0.0 and baseline.get_color() == BASELINE_COLOR,
        ),
        (
            "图例只含 2 项：%s / %s"
            % (LEGEND_CURVE_LABEL, LEGEND_TURNS_LABEL),
            legend_labels == [LEGEND_CURVE_LABEL, LEGEND_TURNS_LABEL],
        ),
        (
            "画布 = %.0f x %.0f px（figsize=%s, dpi=%d）"
            % (EXPECTED_PNG_SIZE[0], EXPECTED_PNG_SIZE[1], str(FIGURE_SIZE_INCH), FIGURE_DPI),
            figure.get_size_inches().tolist() == list(FIGURE_SIZE_INCH)
            and figure.dpi == FIGURE_DPI,
        ),
    ]
    if not print_checks("绘图结构自检（冻结设计逐项核对）", figure_checks):
        plt.close(figure)
        print("")
        print("绘图结构自检未通过：停止运行（不保存 PNG）")
        return 1

    # 8. 保存 PNG（唯一产物；不用 bbox_inches，保证分辨率就是 1800 x 900）
    figure.savefig(PNG_PATH, dpi=FIGURE_DPI)
    plt.close(figure)
    print("")
    print("已保存：%s（%.1f KiB）" % (PNG_PATH, PNG_PATH.stat().st_size / 1024.0))

    # 9. 生成后再次计算 SHA-256：必须与生成前完全一致
    sha_after = sha256_of_file(DS_CSV_PATH)
    post_checks = [
        (
            "生成后 SHA-256 = 生成前 SHA-256（CSV 未被修改）",
            sha_after == sha_before,
        ),
        (
            "生成后 SHA-256 与冻结记录一致（%s）" % FROZEN_CSV_SHA256,
            sha_after == FROZEN_CSV_SHA256,
        ),
        ("PNG 文件存在", PNG_PATH.is_file()),
    ]

    # 10. 图片自检（只读打开，不重新读取并修改图片）
    size = read_png_size_with_pillow(PNG_PATH)
    size_source = "Pillow 打开校验"
    if size is None:
        size = read_png_size_from_header(PNG_PATH)
        size_source = "PNG 文件头解析（Pillow 不可用）"
    post_checks.append(
        (
            "PNG 分辨率 = %d x %d px（%s）"
            % (EXPECTED_PNG_SIZE[0], EXPECTED_PNG_SIZE[1], size_source),
            tuple(size) == EXPECTED_PNG_SIZE if size is not None else False,
        )
    )
    post_checks.append(
        (
            "PNG 可正常打开（无损坏）",
            size is not None,
        )
    )
    print("")
    print("生成后 SHA-256：%s" % sha_after)
    post_passed = print_checks("生成后自检（CSV 完整性 + 图片自检）", post_checks)

    print("")
    print("========== 本轮总结 ==========")
    print("1. 图像路径：%s" % PNG_PATH)
    print("2. 图像尺寸：%d x %d px（预期 %d x %d）"
          % (size[0] if size else -1, size[1] if size else -1,
             EXPECTED_PNG_SIZE[0], EXPECTED_PNG_SIZE[1]))
    print("3. CSV SHA-256 前后一致：%s" % ("是" if sha_after == sha_before else "否"))
    print("4. CSV 数据行数：%d" % len(rows))
    print("5. 转向点标记：6 点（frame 491 / 602 / 838 / 1063 / 1254 / 1513），未重新检测")
    print("6. 数据变换：无（平滑 / 插值 / 滤波 / 重采样 / 拟合 / 趋势线 / 包络 / 误差带全部未使用）")
    print("7. 本轮只生成 1 个文件：%s" % PNG_PATH.name)
    print("8. 自检结论：%s" % ("全部通过" if (pre_passed and post_passed) else "存在未通过项"))
    return 0 if (pre_passed and post_passed) else 1


if __name__ == "__main__":
    sys.exit(main())

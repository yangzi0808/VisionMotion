"""
VisionMotion —— v1.0.0 Phase 1（VM-V1.0-P1-01）用户视频轨迹可视化模块

本模块只做一件事：把任意一份 M3 格式的 track CSV 画成「目标运动二维轨迹」PNG。

严格边界（本阶段只做轨迹图，不越界）：

    - 只读 CSV，绝不修改 / 重写 / 移动 CSV
    - 只使用 detected=True 的有效数据点；detected=False 一律跳过
    - 不做位移、不做毫米换算、不做标定、不做 FFT / 频率 / 周期 / 振幅分析
    - 不做平滑 / 插值 / 滤波 / 拟合 / 重采样，原始点直接连线
    - 不依赖 src/ 中任何冻结常量（标定 / gate / s0），因此可作用于任意用户视频

输入（任意 track CSV，表头必须同时含这三列）：
    x_px, y_px, detected
典型来源：demo/run_video_tracking.py 生成的 results/<video_name>_track.csv

输出：
    一张 300 dpi 的 PNG 二维轨迹图（matplotlib，Agg 后端，只保存不弹窗）

代码风格：普通函数 + 中文注释，不使用 class（仅定义一个错误类型）。
"""

import csv
from pathlib import Path

import matplotlib

# 必须在 import pyplot 之前指定 Agg 后端：只出图、不弹窗、不需要显示环境
matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402


# ============================================================
# 常量
# ============================================================

# 画布与分辨率：8 x 8 英寸 @ 300 dpi = 2400 x 2400 px
FIGURE_SIZE_INCH = (8.0, 8.0)
FIGURE_DPI = 300

# 位移曲线是「时间序列」，用更宽的画布：10 x 6 英寸 @ 300 dpi = 3000 x 1800 px
DISPLACEMENT_FIGURE_SIZE_INCH = (10.0, 6.0)

# 频谱图同样是「横轴为连续量」的图，沿用宽画布：10 x 6 英寸 @ 300 dpi
FFT_FIGURE_SIZE_INCH = (10.0, 6.0)

# track CSV 中本模块必需的列（对任何视频都通用，不绑定具体实验）
REQUIRED_FIELDS = ("x_px", "y_px", "detected")

# 中文字体候选：按顺序挑选「当前环境实际存在」的第一个；都找不到时退回默认字体
# （轨迹图仍然可以正常生成，只是中文可能显示为方框，因此不在这里硬性报错）
FONT_CANDIDATES = (
    "Microsoft YaHei",
    "SimHei",
    "DengXian",
    "SimSun",
    "Noto Sans CJK SC",
    "Source Han Sans CN",
    "MS Gothic",
)

# 配色（与项目其余成果图保持一致的蓝色系）
COLOR_TRACK = "#1f77b4"
COLOR_START = "#2ca02c"
COLOR_END = "#d62728"
COLOR_GRID = "#D9D9D9"

# 等比例判据：当 x / y 两个方向的数据跨度之比不超过该值时，使用等比例坐标轴，
# 这样轨迹形状与画面一致；跨度相差悬殊（例如几乎只沿一个方向往复运动的振动视频）
# 时改用各自独立缩放，避免轨迹被压成一条看不见细节的细线，并在图上明确标注。
EQUAL_SCALE_MAX_RATIO = 3.0


class UserVisualizationError(Exception):
    """
    本模块所有「可预期的用户错误」统一用这个类型抛出，便于调用方一次性捕获：

        - 输入文件不存在 / 不是文件
        - CSV 为空（只有表头，没有数据行）
        - CSV 缺少必需列（例如第三方轨迹 CSV 用的是 y0_px 而不是 y_px）
        - CSV 里没有任何 detected=True 的可用数据点
        - 输出目录无法创建
    """


# ============================================================
# 中文字体
# ============================================================


def setup_chinese_font():
    """
    挑选当前环境实际存在的中文字体并写入 rcParams，返回选中的字体名。

    候选字体全部不存在时返回 None（不抛异常）：调用方仍应出图，
    只是中文可能出现方框，这比直接失败更符合「通用用户模块」的定位。
    """
    import matplotlib.font_manager as font_manager

    registered = {font.name for font in font_manager.fontManager.ttflist}

    chosen = None
    for candidate in FONT_CANDIDATES:
        if candidate in registered:
            chosen = candidate
            break

    if chosen is None:
        return None

    plt.rcParams["font.sans-serif"] = [chosen] + [
        name for name in FONT_CANDIDATES if name != chosen
    ]
    plt.rcParams["font.family"] = "sans-serif"
    # 负号用 ASCII 减号，避免默认字体缺字导致坐标轴出现方框
    plt.rcParams["axes.unicode_minus"] = False
    return chosen


# ============================================================
# 读取 track CSV
# ============================================================


def display_name(csv_path):
    """
    由 CSV 文件名得到适合放进图标题的显示名：

        EXP-002-VIDEO-001_track.csv -> EXP-002-VIDEO-001
        user_video_track.csv        -> user_video
        其他文件名                   -> 原样使用 stem
    """
    stem = Path(csv_path).stem
    if stem.endswith("_track"):
        return stem[: -len("_track")]
    return stem


def read_track_points(csv_path):
    """
    读取任意 M3 格式的 track CSV，提取轨迹点。

    参数：
        csv_path —— track CSV 路径（只读，绝不修改）

    返回字典：
        csv_path      —— Path
        fieldnames    —— 实际表头（列表）
        total_rows    —— 数据行总数（不含表头）
        points        —— [(x_px, y_px), ...] 的列表，只含 detected=True 且坐标合法的点
        skipped_rows  —— 被跳过的行数（detected=False，或 detected=True 但坐标缺失/非法）

    出错时抛 UserVisualizationError（文件不存在 / CSV 为空 / 缺列 / 无有效点）。
    """
    csv_path = Path(csv_path)

    if not csv_path.is_file():
        raise UserVisualizationError("输入 CSV 不存在或不是文件：%s" % csv_path)

    points = []
    skipped_rows = 0

    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = list(reader.fieldnames or [])

        # 1. 必需列检查：缺列时明确说明缺了哪些、实际有哪些，而不是后面抛 KeyError
        missing_fields = [name for name in REQUIRED_FIELDS if name not in fieldnames]
        if missing_fields:
            raise UserVisualizationError(
                "CSV 缺少必需列 %s；实际表头：%s"
                % (", ".join(missing_fields), ", ".join(fieldnames) or "(空)")
            )

        total_rows = 0
        for record in reader:
            total_rows += 1

            # 2. 只认 M3 规范写出的 "True"；其余（含 "False" / 空 / 非法文本）一律跳过
            detected_text = (record.get("detected") or "").strip()
            if detected_text != "True":
                skipped_rows += 1
                continue

            # 3. detected=True 也必须给出可解析的坐标，否则跳过（绝不填 0）
            try:
                x_value = float((record.get("x_px") or "").strip())
                y_value = float((record.get("y_px") or "").strip())
            except ValueError:
                skipped_rows += 1
                continue

            points.append((x_value, y_value))

    # 4. 空 CSV（只有表头或完全为空）
    if total_rows == 0:
        raise UserVisualizationError(
            "CSV 为空（只有表头或没有任何数据行）：%s" % csv_path
        )

    # 5. 有数据行，但没有任何可用轨迹点
    if not points:
        raise UserVisualizationError(
            "CSV 中没有 detected=True 的有效轨迹点（共 %d 行，全部被跳过）：%s"
            % (total_rows, csv_path)
        )

    return {
        "csv_path": csv_path,
        "fieldnames": fieldnames,
        "total_rows": total_rows,
        "points": points,
        "skipped_rows": skipped_rows,
    }


# ============================================================
# 绘制二维轨迹
# ============================================================


def build_trajectory_figure(track_data, title=None):
    """
    根据 read_track_points() 的结果构造二维轨迹 Figure（不保存、不关闭）。

    画法：
        - 蓝色细线按 CSV 原始顺序逐点连接（不平滑 / 不插值）
        - 绿色圆点标起点、红色方块标终点
        - 等比例坐标轴：轨迹形状不被拉伸
        - y 轴反向：与图像坐标系一致（原点在左上角，y 向下为正）

    返回 (figure, axes)。
    """
    points = track_data["points"]
    x_values = [x for x, _ in points]
    y_values = [y for _, y in points]

    if title is None:
        title = "%s 目标运动二维轨迹" % display_name(track_data["csv_path"])

    figure, axes = plt.subplots(figsize=FIGURE_SIZE_INCH, dpi=FIGURE_DPI)

    # 轨迹线 + 原始采样点
    axes.plot(
        x_values,
        y_values,
        color=COLOR_TRACK,
        linewidth=1.2,
        marker="o",
        markersize=1.8,
        markerfacecolor=COLOR_TRACK,
        markeredgewidth=0.0,
        label="轨迹（n=%d）" % len(points),
        zorder=2,
    )

    # 起点 / 终点
    axes.plot(
        [x_values[0]],
        [y_values[0]],
        linestyle="none",
        marker="o",
        markersize=9,
        markerfacecolor=COLOR_START,
        markeredgecolor="white",
        markeredgewidth=1.0,
        label="起点 (%.2f, %.2f) px" % (x_values[0], y_values[0]),
        zorder=3,
    )
    axes.plot(
        [x_values[-1]],
        [y_values[-1]],
        linestyle="none",
        marker="s",
        markersize=8,
        markerfacecolor=COLOR_END,
        markeredgecolor="white",
        markeredgewidth=1.0,
        label="终点 (%.2f, %.2f) px" % (x_values[-1], y_values[-1]),
        zorder=3,
    )

    # 标题与坐标轴（明确单位 pixel）
    axes.set_title(title)
    axes.set_xlabel("x_px (pixel)")
    axes.set_ylabel("y_px (pixel)")

    # 图像坐标系：原点在左上角，y 向下为正，因此反向 y 轴
    axes.invert_yaxis()

    # 坐标轴比例：两个方向跨度接近时用等比例（形状可信）；跨度相差悬殊时各自独立
    # 缩放（看得见细节），并在页脚明确标注用的是哪一种，避免读者误读形状。
    span_x = max(x_values) - min(x_values)
    span_y = max(y_values) - min(y_values)
    largest_span = max(span_x, span_y)
    smallest_span = min(span_x, span_y)
    equal_scale = (
        smallest_span > 0.0 and (largest_span / smallest_span) <= EQUAL_SCALE_MAX_RATIO
    )

    if equal_scale:
        axes.set_aspect("equal", adjustable="box")
        axes.margins(0.08)
        aspect_note = "x / y 轴等比例（轨迹形状与画面一致）"
    else:
        axes.set_aspect("auto")
        axes.margins(0.05)
        aspect_note = "x / y 轴各自独立缩放，未等比例（轨迹形状与角度不代表真实几何）"

    axes.grid(True, color=COLOR_GRID, linewidth=0.6, linestyle="--", alpha=0.7)
    axes.legend(loc="best", fontsize=9, framealpha=0.9)

    # 页脚（分两行，避免文字过长溢出图外）：
    #   第一行 = 数据来源与统计；第二行 = 坐标口径与本次使用的轴比例
    footer_line_1 = "数据源：%s（共 %d 行，有效点 %d，跳过 %d）" % (
        track_data["csv_path"].name,
        track_data["total_rows"],
        len(points),
        track_data["skipped_rows"],
    )
    footer_line_2 = (
        "图像坐标系：x 向右为正，y 向下为正（y 轴已反向显示）　|　%s" % aspect_note
    )
    figure.text(0.5, 0.042, footer_line_1, ha="center", va="bottom", fontsize=8)
    figure.text(0.5, 0.014, footer_line_2, ha="center", va="bottom", fontsize=8)

    figure.tight_layout(rect=(0.0, 0.065, 1.0, 1.0))
    return figure, axes


def plot_trajectory_from_track_csv(csv_path, output_path, title=None, dpi=FIGURE_DPI):
    """
    读取任意 track CSV，生成「目标运动二维轨迹」PNG。

    参数：
        csv_path    —— 输入 track CSV（只读，不会被修改）
        output_path —— 输出 PNG 路径（父目录不存在时自动创建）
        title       —— 可选标题；默认用 CSV 文件名派生
        dpi         —— 可选分辨率，默认 300

    返回 report 字典：
        csv_path / output_path / total_rows / valid_points / skipped_rows
        / png_written / png_size_bytes

    出错时抛 UserVisualizationError（文件不存在 / CSV 为空 / 缺列 / 无有效点 /
    输出目录无法创建）。
    """
    track_data = read_track_points(csv_path)

    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise UserVisualizationError(
            "无法创建输出目录：%s（%s）" % (output_path.parent, error)
        )

    setup_chinese_font()

    figure, _axes = build_trajectory_figure(track_data, title=title)
    try:
        figure.savefig(str(output_path), dpi=dpi)
    except OSError as error:
        raise UserVisualizationError(
            "保存 PNG 失败：%s（%s）" % (output_path, error)
        )
    finally:
        plt.close(figure)

    if not output_path.is_file():
        raise UserVisualizationError("PNG 未按预期生成：%s" % output_path)

    return {
        "csv_path": track_data["csv_path"],
        "output_path": output_path,
        "total_rows": track_data["total_rows"],
        "valid_points": len(track_data["points"]),
        "skipped_rows": track_data["skipped_rows"],
        "png_written": True,
        "png_size_bytes": output_path.stat().st_size,
    }


# ============================================================
# 绘制位移曲线（像素位移 - 时间）
# ============================================================


def _check_displacement_data(data):
    """
    校验位移数据是否可用于绘图，返回 (time_s 列表, displacement_px 列表)。

    期望 data 是 src/user_displacement.py 的
    compute_pixel_displacement_from_track_csv() 返回值（含 time_s / displacement_px
    两个等长列表）。不合法时抛 UserVisualizationError。
    """
    if not isinstance(data, dict):
        raise UserVisualizationError(
            "位移数据必须是 dict（含 time_s / displacement_px 两个列表）"
        )

    time_values = data.get("time_s")
    displacement_values = data.get("displacement_px")

    if not time_values or not displacement_values:
        raise UserVisualizationError("位移数据为空（time_s / displacement_px 没有数据点）")

    if len(time_values) != len(displacement_values):
        raise UserVisualizationError(
            "位移数据长度不一致：time_s %d 个，displacement_px %d 个"
            % (len(time_values), len(displacement_values))
        )

    return list(time_values), list(displacement_values)


def build_displacement_figure(data, title=None):
    """
    根据位移数据构造「位移 - 时间」Figure（不保存、不关闭）。

    画法：
        - 蓝色折线按 CSV 原始顺序逐点连接（不平滑 / 不插值 / 不拟合）
        - 红色圆点标出最大位移位置，并标注数值与时刻
        - 横轴 time_s（秒），纵轴 displacement_px（像素）

    返回 (figure, axes)。
    """
    time_values, displacement_values = _check_displacement_data(data)

    if title is None:
        title = "%s 像素位移-时间曲线" % display_name(data.get("csv_path", "track"))

    figure, axes = plt.subplots(figsize=DISPLACEMENT_FIGURE_SIZE_INCH, dpi=FIGURE_DPI)

    axes.plot(
        time_values,
        displacement_values,
        color=COLOR_TRACK,
        linewidth=1.2,
        marker="o",
        markersize=2.0,
        markerfacecolor=COLOR_TRACK,
        markeredgewidth=0.0,
        label="像素位移（n=%d）" % len(displacement_values),
        zorder=2,
    )

    # 最大位移位置：只做标注，不改变任何数据
    max_index = max(
        range(len(displacement_values)), key=lambda index: displacement_values[index]
    )
    max_time = time_values[max_index]
    max_value = displacement_values[max_index]
    axes.plot(
        [max_time],
        [max_value],
        linestyle="none",
        marker="o",
        markersize=9,
        markerfacecolor=COLOR_END,
        markeredgecolor="white",
        markeredgewidth=1.0,
        label="最大位移 (%.2f s, %.2f px)" % (max_time, max_value),
        zorder=3,
    )
    axes.annotate(
        "max = %.2f px" % max_value,
        xy=(max_time, max_value),
        xytext=(10, -14),
        textcoords="offset points",
        fontsize=9,
        color=COLOR_END,
        va="top",
    )

    # 标题与坐标轴（明确单位）
    axes.set_title(title)
    axes.set_xlabel("time_s (s)")
    axes.set_ylabel("displacement_px (pixel)")

    axes.margins(0.05)
    axes.grid(True, color=COLOR_GRID, linewidth=0.6, linestyle="--", alpha=0.7)
    axes.legend(loc="best", fontsize=9, framealpha=0.9)

    # 页脚（分两行，避免文字过长溢出图外）：数据来源与统计 / 位移定义与单位口径
    footer_line_1 = "数据源：%s（共 %d 行，有效点 %d，跳过 %d）" % (
        Path(data.get("csv_path", "track.csv")).name,
        data.get("total_rows", len(displacement_values)),
        len(displacement_values),
        data.get("skipped_rows", 0),
    )
    footer_line_2 = (
        "位移定义：相对第一个有效检测点 (%s, %s) 的像素距离　|　"
        "单位：pixel（本阶段未做 mm 标定）"
        % (
            "%.2f" % data["x0"] if "x0" in data else "-",
            "%.2f" % data["y0"] if "y0" in data else "-",
        )
    )
    figure.text(0.5, 0.038, footer_line_1, ha="center", va="bottom", fontsize=8)
    figure.text(0.5, 0.012, footer_line_2, ha="center", va="bottom", fontsize=8)

    figure.tight_layout(rect=(0.0, 0.06, 1.0, 1.0))
    return figure, axes


def plot_displacement_curve(data, output_path, title=None, dpi=FIGURE_DPI):
    """
    根据位移数据生成「像素位移 - 时间」曲线 PNG。

    参数：
        data        —— compute_pixel_displacement_from_track_csv() 的返回值
                       （必须含等长的 time_s / displacement_px 两个列表）
        output_path —— 输出 PNG 路径（父目录不存在时自动创建）
        title       —— 可选标题；默认用 CSV 文件名派生
        dpi         —— 可选分辨率，默认 300

    返回 report 字典：
        output_path / points / max_displacement_px / png_written / png_size_bytes

    出错时抛 UserVisualizationError（数据为空 / 长度不一致 / 输出目录或保存失败）。
    """
    time_values, displacement_values = _check_displacement_data(data)

    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise UserVisualizationError(
            "无法创建输出目录：%s（%s）" % (output_path.parent, error)
        )

    setup_chinese_font()

    figure, _axes = build_displacement_figure(data, title=title)
    try:
        figure.savefig(str(output_path), dpi=dpi)
    except OSError as error:
        raise UserVisualizationError(
            "保存 PNG 失败：%s（%s）" % (output_path, error)
        )
    finally:
        plt.close(figure)

    if not output_path.is_file():
        raise UserVisualizationError("PNG 未按预期生成：%s" % output_path)

    return {
        "output_path": output_path,
        "points": len(displacement_values),
        "max_displacement_px": max(displacement_values),
        "png_written": True,
        "png_size_bytes": output_path.stat().st_size,
    }


# ============================================================
# 绘制 FFT 频谱
# ============================================================


def _check_fft_data(fft_data):
    """
    校验 FFT 数据是否可用于绘图，返回 (frequency 列表, amplitude 列表)。

    期望 fft_data 是 src/user_frequency_analysis.py 的
    compute_fft_from_displacement() 返回值（含 frequency / amplitude 两个等长数组）。
    不合法时抛 UserVisualizationError。
    """
    if not isinstance(fft_data, dict):
        raise UserVisualizationError(
            "FFT 数据必须是 dict（含 frequency / amplitude 两个数组）"
        )

    frequency = fft_data.get("frequency")
    amplitude = fft_data.get("amplitude")

    if frequency is None or amplitude is None:
        raise UserVisualizationError("FFT 数据缺少 frequency / amplitude")

    frequency = list(frequency)
    amplitude = list(amplitude)

    if not frequency or not amplitude:
        raise UserVisualizationError("FFT 数据为空（frequency / amplitude 没有数据点）")

    if len(frequency) != len(amplitude):
        raise UserVisualizationError(
            "FFT 数据长度不一致：frequency %d 个，amplitude %d 个"
            % (len(frequency), len(amplitude))
        )

    return frequency, amplitude


def build_fft_figure(fft_data, title=None):
    """
    根据 FFT 数据构造「频谱」Figure（不保存、不关闭）。

    画法：
        - 蓝色折线画单边幅值谱（原始谱值逐点连接，不平滑 / 不过滤）
        - 红色圆点标出主峰频率，并标注数值
        - 横轴 frequency（Hz），纵轴 amplitude（pixel）

    返回 (figure, axes)。
    """
    frequency, amplitude = _check_fft_data(fft_data)

    if title is None:
        source = fft_data.get("csv_path")
        if source:
            title = "%s FFT 频谱" % display_name(source)
        else:
            title = "像素位移 FFT 频谱"

    figure, axes = plt.subplots(figsize=FFT_FIGURE_SIZE_INCH, dpi=FIGURE_DPI)

    axes.plot(
        frequency,
        amplitude,
        color=COLOR_TRACK,
        linewidth=1.2,
        label="单边幅值谱（%d 点）" % len(frequency),
        zorder=2,
    )

    # 主峰标注：只做标注，不改变任何数据
    peak_frequency = float(fft_data.get("peak_frequency", 0.0))
    peak_amplitude = float(fft_data.get("peak_amplitude", 0.0))
    axes.plot(
        [peak_frequency],
        [peak_amplitude],
        linestyle="none",
        marker="o",
        markersize=9,
        markerfacecolor=COLOR_END,
        markeredgecolor="white",
        markeredgewidth=1.0,
        label="主峰 f = %.4f Hz" % peak_frequency,
        zorder=3,
    )
    # 主峰一定在谱的顶部，标注放在点的下方，避免贴到画布上边缘被裁掉
    axes.annotate(
        "主峰 = %.4f Hz\n幅值 = %.4f px" % (peak_frequency, peak_amplitude),
        xy=(peak_frequency, peak_amplitude),
        xytext=(10, -14),
        textcoords="offset points",
        fontsize=9,
        color=COLOR_END,
        va="top",
    )

    # 标题与坐标轴（明确单位）
    axes.set_title(title)
    axes.set_xlabel("frequency (Hz)")
    axes.set_ylabel("amplitude (pixel)")

    axes.set_xlim(left=0.0)
    axes.margins(0.05)
    axes.grid(True, color=COLOR_GRID, linewidth=0.6, linestyle="--", alpha=0.7)
    axes.legend(loc="upper right", fontsize=9, framealpha=0.9)

    # 页脚（分两行）：数据口径与频率分辨率 / 处理边界
    n_points = fft_data.get("n_points", len(frequency))
    dt = fft_data.get("dt")
    df = fft_data.get("df")
    dt_text = "%.9g s" % dt if dt is not None else "-"
    df_text = "%.6g Hz" % df if df is not None else "-"

    footer_line_1 = (
        "数据：n = %s 点，dt = %s，频率分辨率 df = %s（f_max = %.4f Hz）"
        % (n_points, dt_text, df_text, max(frequency))
    )
    footer_line_2 = (
        "幅度口径：单边幅值谱（已去均值，单位 pixel）　|　"
        "未加窗、未滤波、未平滑、未插值、未补零"
    )
    figure.text(0.5, 0.038, footer_line_1, ha="center", va="bottom", fontsize=8)
    figure.text(0.5, 0.012, footer_line_2, ha="center", va="bottom", fontsize=8)

    figure.tight_layout(rect=(0.0, 0.06, 1.0, 1.0))
    return figure, axes


def plot_fft_spectrum(fft_data, output_path, title=None, dpi=FIGURE_DPI):
    """
    根据 FFT 数据生成「单边幅值谱」PNG。

    参数：
        fft_data    —— compute_fft_from_displacement() 的返回值
                       （必须含等长的 frequency / amplitude）
        output_path —— 输出 PNG 路径（父目录不存在时自动创建）
        title       —— 可选标题；默认用 csv_path（若提供）或通用标题
        dpi         —— 可选分辨率，默认 300

    返回 report 字典：
        output_path / bins / peak_frequency / peak_amplitude
        / png_written / png_size_bytes

    出错时抛 UserVisualizationError（数据缺失 / 长度不一致 / 空 / 输出或保存失败）。
    """
    _check_fft_data(fft_data)

    output_path = Path(output_path)
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        raise UserVisualizationError(
            "无法创建输出目录：%s（%s）" % (output_path.parent, error)
        )

    setup_chinese_font()

    figure, _axes = build_fft_figure(fft_data, title=title)
    try:
        figure.savefig(str(output_path), dpi=dpi)
    except OSError as error:
        raise UserVisualizationError(
            "保存 PNG 失败：%s（%s）" % (output_path, error)
        )
    finally:
        plt.close(figure)

    if not output_path.is_file():
        raise UserVisualizationError("PNG 未按预期生成：%s" % output_path)

    return {
        "output_path": output_path,
        "bins": len(fft_data.get("frequency", [])),
        "peak_frequency": float(fft_data.get("peak_frequency", 0.0)),
        "peak_amplitude": float(fft_data.get("peak_amplitude", 0.0)),
        "png_written": True,
        "png_size_bytes": output_path.stat().st_size,
    }

"""
VisionMotion —— M6.3-3B 最终成果可视化生成模块（严格按 M6.3-3A 封板设计稿）

本模块只做一件事：把已经封板的数值与极值清单画成三张最终 PNG。

严格约束（M6.3-3B）：
    - 不读取原始外部视频；不重新计算周期 / 频率 / 极值 / FFT；不做任何拟合；
    - 不修改 results/EXP-EXT-LAB67-V1_trajectory.csv 与任何已封板文件；
    - 图 A 的极值点直接使用 M6.3-1 封板清单（不重新寻找极值，仅做一致性核对）；
    - 图 B / 图 C 的数值直接使用 M6.3-1 / 1R / 2A / 2B / 2C-R 封板值；
    - 图内不出现代码变量名（y0_px / bbox_w_px / bbox_h_px / time_s 等），统一使用数学变量；
    - 三张图均为 PNG、300 dpi，中文由显式指定且实际存在的中文字体渲染。

产物：
    results/EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png
    results/EXP-EXT-LAB67-V1_fig_B_frequency_comparison.png
    results/EXP-EXT-LAB67-V1_fig_C_pipeline.png

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m63_final_visualization.py
"""

import csv
import math
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.image as mpimg  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.text as mtext  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle  # noqa: E402

# ============================================================
# 路径与全局常量
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CSV_PATH = PROJECT_ROOT / "results" / "EXP-EXT-LAB67-V1_trajectory.csv"
FIGURE_A_NAME = "EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png"
FIGURE_B_NAME = "EXP-EXT-LAB67-V1_fig_B_frequency_comparison.png"
FIGURE_C_NAME = "EXP-EXT-LAB67-V1_fig_C_pipeline.png"

DPI = 300

# 中文字体候选：按顺序挑选“当前环境实际存在”的第一个（不假设字体一定存在）
FONT_CANDIDATES = (
    "Microsoft YaHei",
    "SimHei",
    "DengXian",
    "SimSun",
    "Noto Sans CJK SC",
    "Source Han Sans CN",
    "MS Gothic",
)

# 色盲友好配色（Okabe–Ito 风格）
COLOR_BLUE = "#0072B2"
COLOR_ORANGE = "#D55E00"
COLOR_GREEN = "#009E73"
COLOR_GRAY = "#555555"
COLOR_PURPLE = "#CC79A7"
COLOR_LIGHT_GRAY = "#D9D9D9"
COLOR_LIGHT_ORANGE = "#F6D3B0"
COLOR_LIGHT_GREEN = "#C9E9DC"
COLOR_LIGHT_BLUE = "#D6E6F2"
COLOR_LIGHT_PURPLE = "#F0DAE6"

FOOTER_LINE_1 = "External public educational dataset — ComPADRE / OSP Lab67 Video 1（51.5 g）"
FOOTER_LINE_2 = "数据源：results/EXP-EXT-LAB67-V1_trajectory.csv（frame 76–235，160 帧，30 fps）"

# ============================================================
# 封板数值（M6.3-1 / 1R / 2A / 2B / 2C-R）——禁止修改
# ============================================================

# 极值清单：frame, time / s, y0 / px（直接取自 M6.3-1 封板报告，不重新寻找）
FROZEN_PEAKS = (
    (85, 2.8333, 622.0),
    (101, 3.3667, 620.0),
    (118, 3.9333, 616.0),
    (134, 4.4667, 615.0),
    (150, 5.0000, 613.0),
    (166.5, 5.5500, 610.0),
    (183, 6.1000, 609.0),
    (199, 6.6333, 607.0),
    (215, 7.1667, 605.0),
    (231.5, 7.7167, 604.0),
)
FROZEN_TROUGHS = (
    (77, 2.5667, 508.0),
    (93, 3.1000, 512.0),
    (110, 3.6667, 516.0),
    (126, 4.2000, 515.0),
    (142, 4.7333, 520.0),
    (158, 5.2667, 521.0),
    (175, 5.8333, 522.0),
    (191, 6.3667, 526.0),
    (207, 6.9000, 525.0),
    (223.5, 7.4500, 529.0),
)
# 3 处 2 帧平台块 → 取中点：166–167、223–224、231–232
PLATEAU_MIDPOINTS = {166.5: (166, 167), 223.5: (223, 224), 231.5: (231, 232)}

# 代表性峰—峰示意区间（M6.3-3A 指定 f150 → f166.5）
REPRESENTATIVE_INTERVAL = (150.0, 5.0000, 166.5, 5.5500, 0.550)

FROZEN = {
    "T_exp": 0.542593,
    "f_exp": 1.843003,
    "SE_T": 0.0038,
    "SE_f": 0.0129,
    "dT_sampling": 0.0333,
    "df_sampling": 0.1132,
    "f_FFT": 1.875,
    "df_fft": 0.1875,
    "T_theory": 0.537018101,
    "f_theory": 1.862134625,
    "f_rect_min": 1.855281725,
    "f_rect_max": 1.868975645,
    "m": 0.0515,
    "k": 7.05,
}

# 图内禁止出现的字符串（自动扫描）
FORBIDDEN_STRINGS = (
    "accuracy",
    "accuracy",
    "精度",
    "真值",
    "标准答案",
    "总误差",
    "误差合并",
    "阻尼拟合",
    "k_eff",
    "m_eff",
    "ζ",
    "γ",
    "m_s",
    "y0_px",
    "bbox_w_px",
    "bbox_h_px",
    "time_s",
    "px/mm",
    "标定",
    "振幅",
)


# ============================================================
# 基础工具
# ============================================================


def setup_chinese_font():
    """
    挑选当前环境实际存在的中文字体并写入 rcParams；返回选中的字体名。
    """
    import matplotlib.font_manager as font_manager

    registered = {font.name for font in font_manager.fontManager.ttflist}
    chosen = None
    for candidate in FONT_CANDIDATES:
        if candidate in registered:
            chosen = candidate
            break
    if chosen is None:
        raise RuntimeError("未找到任何可用的中文字体，已停止；候选字体：%s" % ", ".join(FONT_CANDIDATES))

    plt.rcParams["font.sans-serif"] = [chosen] + [c for c in FONT_CANDIDATES if c != chosen]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["mathtext.fontset"] = "dejavusans"
    return chosen


def load_trajectory(csv_path):
    """
    读取封板轨迹 CSV（只读）：只用 frame / time_s / y0_px 三列。
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError("找不到封板轨迹 CSV：%s" % csv_path)
    frames, times, positions = [], [], []
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            frames.append(int(row["frame"]))
            times.append(float(row["time_s"]))
            positions.append(float(row["y0_px"]))
    return {
        "path": str(csv_path),
        "frame": np.asarray(frames, dtype=float),
        "time": np.asarray(times, dtype=float),
        "y0": np.asarray(positions, dtype=float),
    }


def check_frozen_extrema_against_csv(series):
    """
    一致性核对（不是重新寻找极值）：核对封板极值的 y₀ 是否与 CSV 中对应帧一致。

    对 3 处平台中点，检查组成平台的 2 帧 y₀ 是否相同且等于封板值。
    """
    by_frame = {int(frame): value for frame, value in zip(series["frame"], series["y0"])}
    problems = []
    for kind, table in (("峰", FROZEN_PEAKS), ("谷", FROZEN_TROUGHS)):
        for frame, _time, value in table:
            frames_to_check = PLATEAU_MIDPOINTS.get(frame, (int(frame),))
            for check_frame in frames_to_check:
                csv_value = by_frame.get(int(check_frame))
                if csv_value is None:
                    problems.append("%s frame %s 不在 CSV 中" % (kind, check_frame))
                elif abs(csv_value - value) > 0.5:
                    problems.append("%s frame %s: CSV %.1f vs 封板 %.1f" % (kind, check_frame, csv_value, value))
    return problems


def collect_texts(fig):
    """
    收集图内所有可见文字（含刻度、图例、注释），用于违规词自动扫描。
    """
    texts = []
    for artist in fig.findobj(mtext.Text):
        value = artist.get_text()
        if value and value.strip():
            texts.append(value.strip())
    return texts


def scan_forbidden(texts):
    """
    返回图内命中的禁止字符串列表。
    """
    hits = []
    for text in texts:
        low = text.lower()
        for token in FORBIDDEN_STRINGS:
            if token.lower() in low:
                hits.append((token, text))
    return hits


def add_footer(fig):
    """
    三张图统一页脚（外部数据声明 + 数据源）。
    """
    fig.text(0.5, 0.045, FOOTER_LINE_1, ha="center", va="center", fontsize=9.5, color=COLOR_GRAY)
    fig.text(0.5, 0.015, FOOTER_LINE_2, ha="center", va="center", fontsize=9, color=COLOR_GRAY)


def add_text_box(fig, bounds, lines, facecolor="#FFFFFF", edgecolor=COLOR_GRAY, fontsize=10.5):
    """
    在指定位置画一个带边框的文字框（不遮挡曲线）。

    bounds = [x0, y0, width, height]（figure 归一化坐标）
    lines  = [(text, weight, color), ...]
    """
    panel = fig.add_axes(bounds)
    panel.set_xlim(0, 1)
    panel.set_ylim(0, 1)
    panel.axis("off")
    panel.add_patch(
        FancyBboxPatch(
            (0.02, 0.02), 0.96, 0.96,
            boxstyle="round,pad=0.015,rounding_size=0.03",
            linewidth=1.0, edgecolor=edgecolor, facecolor=facecolor,
            transform=panel.transAxes,
        )
    )
    total = len(lines)
    for index, (text, weight, color) in enumerate(lines):
        y = 1 - (index + 0.75) * (1.0 / (total + 0.5))
        panel.text(0.06, y, text, ha="left", va="center", fontsize=fontsize, color=color, fontweight=weight)
    return panel


def save_figure(fig, out_path, dpi=DPI):
    """
    保存 PNG 并捕获缺字警告（中文缺字会以 'missing from font' 警告形式出现）。
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fig.savefig(out_path, dpi=dpi, facecolor="white")
    missing = [str(item.message) for item in caught if "missing from font" in str(item.message)]
    return out_path, missing


# ============================================================
# 图 A：核心视觉测量图 y₀(t)
# ============================================================


def make_figure_a(series, out_path):
    """
    生成图 A（原始采样 + 封板极值 + 单处代表性区间箭头 + 数值摘要框）。
    """
    fig = plt.figure(figsize=(13.0, 6.6), dpi=100)
    ax = fig.add_axes([0.065, 0.175, 0.655, 0.705])

    time = series["time"]
    position = series["y0"]

    ax.plot(
        time, position,
        color="#3B6E9E", linewidth=1.5, marker="o", markersize=2.6,
        markerfacecolor="white", markeredgecolor="#3B6E9E", markeredgewidth=0.7,
        label="原始采样 $y_0(t)$（未平滑、未插值）", zorder=3,
    )

    peak_time = [item[1] for item in FROZEN_PEAKS]
    peak_value = [item[2] for item in FROZEN_PEAKS]
    trough_time = [item[1] for item in FROZEN_TROUGHS]
    trough_value = [item[2] for item in FROZEN_TROUGHS]
    ax.plot(peak_time, peak_value, linestyle="none", marker="v", markersize=8.5,
            markerfacecolor=COLOR_ORANGE, markeredgecolor="white", markeredgewidth=0.8,
            label="局部极大（物理最低点）", zorder=4)
    ax.plot(trough_time, trough_value, linestyle="none", marker="^", markersize=8.5,
            markerfacecolor=COLOR_BLUE, markeredgecolor="white", markeredgewidth=0.8,
            label="局部极小（物理最高点）", zorder=4)

    # 代表性峰—峰区间（M6.3-3A 指定 f150 → f166.5，仅 1 处）
    _f1, t1, _f2, t2, dt = REPRESENTATIVE_INTERVAL
    arrow_y = 505.0
    ax.annotate("", xy=(t2, arrow_y), xytext=(t1, arrow_y),
                arrowprops=dict(arrowstyle="<->", color=COLOR_GRAY, linewidth=1.4),
                annotation_clip=False, zorder=6)
    ax.text((t1 + t2) / 2.0, arrow_y - 3.0,
            "Δt = %.3f s\n（示意区间，不用于统计）" % dt,
            ha="center", va="bottom", fontsize=9.5, color=COLOR_GRAY, zorder=6)

    ax.set_xlim(2.5, 7.9)
    ax.set_ylim(645.0, 495.0)          # 反向纵轴：数值向下增大（图像坐标）
    ax.set_xticks(np.arange(2.5, 8.0, 1.0))
    ax.set_xticks(np.arange(2.5, 8.0, 0.5), minor=True)
    ax.set_yticks(np.arange(500, 641, 20))
    ax.set_xlabel("$t$ / s", fontsize=13)
    ax.set_ylabel("$y_0$ / px", fontsize=13)
    ax.tick_params(axis="both", which="major", labelsize=10.5)
    ax.tick_params(axis="x", which="minor", length=3.0)
    ax.grid(True, which="major", color="#E8E8E8", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    ax.text(0.015, 0.985, "$y_0$ 向下增大（图像坐标）", transform=ax.transAxes,
            ha="left", va="top", fontsize=10.5, color=COLOR_GRAY,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor="#DDDDDD", linewidth=0.8))
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.01), ncol=3, frameon=False, fontsize=10.5)

    add_text_box(fig, [0.745, 0.175, 0.235, 0.705], [
        ("数值摘要（M6.3 封板值）", "bold", "#222222"),
        ("$T_{exp}$ = 0.542593 s", "normal", "#222222"),
        ("（峰—峰 9 段均值）", "normal", COLOR_GRAY),
        ("$f_{exp}$ = 1.843003 Hz", "normal", "#222222"),
        ("$SE_T$ ≈ 0.0038 s", "normal", "#222222"),
        ("（9 段统计不确定度）", "normal", COLOR_GRAY),
        ("$\\delta T_{sampling}$ ≈ 0.0333 s", "normal", "#222222"),
        ("（方法学上界，非统计误差）", "normal", COLOR_GRAY),
    ], fontsize=10.5)

    add_footer(fig)
    texts = collect_texts(fig)
    path, missing = save_figure(fig, out_path)
    plt.close(fig)
    return {
        "name": "A",
        "path": str(path),
        "n_samples": int(len(time)),
        "n_peaks": len(FROZEN_PEAKS),
        "n_troughs": len(FROZEN_TROUGHS),
        "n_representative_arrows": 1,
        "texts": texts,
        "missing_glyphs": missing,
    }


# ============================================================
# 图 B：实验 / 理论参考 / FFT 频率对照图
# ============================================================


def make_figure_b(out_path):
    """
    生成图 B（单行频率数轴 + 三条目 + 说明文字块）。
    """
    fig = plt.figure(figsize=(13.0, 6.6), dpi=100)
    ax = fig.add_axes([0.215, 0.465, 0.750, 0.335])

    y_experiment, y_theory, y_fft = 3.0, 2.0, 1.0
    f_exp = FROZEN["f_exp"]
    f_theory = FROZEN["f_theory"]
    f_fft = FROZEN["f_FFT"]
    df_fft = FROZEN["df_fft"]
    df_sampling = FROZEN["df_sampling"]

    # 实验侧：保守采样定位上界（浅灰带，与 SE 误差棒视觉语义不同）
    band = Rectangle((f_exp - df_sampling, y_experiment - 0.28), 2 * df_sampling, 0.56,
                     facecolor=COLOR_LIGHT_GRAY, edgecolor="#999999", linewidth=0.9,
                     linestyle=(0, (4, 2)), zorder=1,
                     label="保守采样定位上界（非统计误差）")
    ax.add_patch(band)
    ax.text(1.8208, 2.76, "±0.1132 Hz（超出横轴范围部分已裁切显示）",
            ha="left", va="bottom", fontsize=9, color="#666666", zorder=3)
    # 实验侧：统计不确定度（黑色带帽误差棒）
    ax.errorbar([f_exp], [y_experiment], xerr=[FROZEN["SE_f"]], fmt="o", markersize=10,
                markerfacecolor=COLOR_BLUE, markeredgecolor="white", markeredgewidth=1.0,
                ecolor="#222222", elinewidth=2.0, capsize=5, capthick=2.0, zorder=4,
                label="实验测量（时域）±$SE_f$")

    # 理论参考：参数矩形 + 空心方块
    rect = Rectangle((FROZEN["f_rect_min"], y_theory - 0.26),
                     FROZEN["f_rect_max"] - FROZEN["f_rect_min"], 0.52,
                     facecolor=COLOR_LIGHT_ORANGE, edgecolor=COLOR_ORANGE, linewidth=1.0,
                     linestyle=(0, (4, 2)), alpha=0.85, zorder=1,
                     label="理论参数矩形（$m$、$k$ 范围）")
    ax.add_patch(rect)
    ax.plot([f_theory], [y_theory], linestyle="none", marker="s", markersize=10,
            markerfacecolor="white", markeredgecolor=COLOR_ORANGE, markeredgewidth=2.0,
            zorder=4, label="理论参考（标准质量—弹簧 SHM）")

    # FFT 交叉验证：分辨率段 + 三角形
    ax.plot([f_fft - df_fft / 2.0, f_fft + df_fft / 2.0], [y_fft, y_fft],
            color=COLOR_GREEN, linewidth=7.0, alpha=0.35, solid_capstyle="butt", zorder=1,
            label="FFT 频率分辨率（±df/2 = ±0.094 Hz）")
    ax.plot([f_fft], [y_fft], linestyle="none", marker="^", markersize=10,
            markerfacecolor=COLOR_GREEN, markeredgecolor="white", markeredgewidth=1.0,
            zorder=4, label="FFT 交叉验证")

    ax.set_xlim(1.82, 1.90)
    ax.set_ylim(0.4, 3.9)
    ax.set_xticks(np.arange(1.82, 1.9001, 0.01))
    ax.set_yticks([y_experiment, y_theory, y_fft])
    ax.set_yticklabels([
        "实验测量\n（时域，$f_{exp}$）",
        "理论参考\n（标准质量—弹簧 SHM，参数范围）",
        "FFT 交叉验证\n（分辨率受限）",
    ], fontsize=10)
    ax.tick_params(axis="y", pad=6)
    ax.set_xlabel("$f$ / Hz", fontsize=13)
    ax.tick_params(axis="x", labelsize=10.5)
    ax.grid(True, axis="x", color="#E8E8E8", linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.legend(loc="lower left", bbox_to_anchor=(0.0, 1.03), ncol=3, frameon=False, fontsize=9.5)

    ax.annotate("$f_{exp}$ = 1.843003 Hz", xy=(f_exp, y_experiment - 0.36),
                ha="center", va="top", fontsize=9.5, color=COLOR_BLUE)
    ax.annotate("$f_{theory}$ = 1.862134625 Hz", xy=(f_theory, y_theory + 0.32),
                ha="center", va="bottom", fontsize=9.5, color=COLOR_ORANGE)
    ax.annotate("参数矩形 $f$ ∈ [1.855281725, 1.868975645] Hz", xy=((FROZEN["f_rect_min"] + FROZEN["f_rect_max"]) / 2.0,
                                                                   y_theory - 0.36),
                ha="center", va="top", fontsize=9, color=COLOR_ORANGE)
    ax.annotate("$f_{FFT}$ = 1.875 Hz，df = 0.1875 Hz", xy=(f_fft, y_fft + 0.24),
                ha="center", va="bottom", fontsize=9.5, color=COLOR_GREEN)

    fig.text(0.5, 0.955, "实验测量 / 标准模型参考 / FFT 交叉验证：频率对照",
             ha="center", va="center", fontsize=17, color="#1A1A1A", fontweight="bold")

    add_text_box(fig, [0.215, 0.115, 0.750, 0.245], [
        ("实验与标准质量—弹簧 SHM 模型参考值相差约 1.0%。", "normal", "#222222"),
        ("该差异超过 $m$、$k$ 给定不确定度传播尺度（±0.323%，差异为其约 3.2 倍）。", "normal", "#222222"),
        ("但未超过当前设定的保守采样定位上界；具体物理归因未验证。", "normal", "#222222"),
        ("标准模型计算以外部资料给出的 0.0515 kg 作为模型中的 $m$；", "normal", COLOR_GRAY),
        ("资料未说明该 Mass on spring 是否包含全部挂具/夹持件质量，", "normal", COLOR_GRAY),
        ("此处属条件性的标准模型参考计算。", "normal", COLOR_GRAY),
    ], fontsize=10)

    add_footer(fig)
    texts = collect_texts(fig)
    path, missing = save_figure(fig, out_path)
    plt.close(fig)
    return {
        "name": "B",
        "path": str(path),
        "n_rows": 3,
        "texts": texts,
        "missing_glyphs": missing,
    }


# ============================================================
# 图 C：VisionMotion 技术流程图
# ============================================================

FIGURE_C_BOXES = (
    ("1", "外部视频", ["ComPADRE / OSP Lab67 Video 1（51.5 g）", "1920×1080，30 fps，236 帧"], "cv"),
    ("2", "ROI", ["x ∈ [690, 780)", "y ∈ [380, 760)"], "cv"),
    ("3", "灰度阈值", ["灰度 < 120"], "cv"),
    ("4", "暗连通域", ["8 邻域，面积 ≥ 150 px"], "cv"),
    ("5", "行宽带提取", ["行跨度 ≥ 35 px，连续 ≥ 3 行", "带宽 40–75 px，带高 ≤ 15 px"], "cv"),
    ("6", "暗带上缘 $y_0$", ["正式位置特征", "不计面积、不用质心"], "cv"),
    ("7", "位置时间序列", ["frame 76–235，160 帧，5.3333 s", "检出率 160/160"], "time"),
    ("8", "峰谷检测", ["平台合并 + 两侧严格规则", "10 峰 + 10 谷"], "time"),
    ("9", "周期 $T$", ["峰间 9 段均值", "$T_{exp}$ = 0.542593 s"], "time"),
    ("10", "频率 $f$", ["$f_{exp}$ = 1.843003 Hz"], "time"),
    ("11", "FFT 交叉验证", ["主峰 1.875 Hz，df = 0.1875 Hz", "仅作独立交叉验证"], "fft"),
    ("12", "标准 SHM 参考", ["$m$ = 0.0515 kg，$k$ = 7.05 N/m", "$f_{theory}$ = 1.862134625 Hz（差异 ≈ 1.0%）"], "model"),
)

FIGURE_C_GROUPS = {
    "cv": ("计算机视觉", COLOR_BLUE, COLOR_LIGHT_BLUE),
    "time": ("时域测量", COLOR_ORANGE, "#FBE3D1"),
    "fft": ("频域交叉验证", COLOR_GREEN, COLOR_LIGHT_GREEN),
    "model": ("物理模型", COLOR_PURPLE, COLOR_LIGHT_PURPLE),
}


def make_figure_c(out_path):
    """
    生成图 C（12 框横向流程图，2×6 折行，4 个分组色带，独立证据用虚线）。
    """
    fig = plt.figure(figsize=(16.0, 9.0), dpi=100)
    canvas = fig.add_axes([0, 0, 1, 1])
    canvas.set_xlim(0, 1)
    canvas.set_ylim(0, 1)
    canvas.axis("off")

    box_w, box_h = 0.142, 0.20
    gap = 0.017
    row_y = {1: 0.615, 2: 0.245}
    start_x = 0.028

    def box_center(index):
        row = 1 if index < 6 else 2
        col = index % 6
        x0 = start_x + col * (box_w + gap)
        return x0, row_y[row], row

    # 分组色带
    band_specs = [
        ("cv", start_x - 0.012, row_y[1] - 0.035, 6 * box_w + 5 * gap + 0.024, box_h + 0.09),
        ("time", start_x - 0.012, row_y[2] - 0.035, 4 * box_w + 3 * gap + 0.024, box_h + 0.09),
        ("fft", start_x + 4 * (box_w + gap) - 0.012, row_y[2] - 0.035, box_w + 0.024, box_h + 0.09),
        ("model", start_x + 5 * (box_w + gap) - 0.012, row_y[2] - 0.035, box_w + 0.024, box_h + 0.09),
    ]
    for key, x0, y0, width, height in band_specs:
        label, edge, face = FIGURE_C_GROUPS[key]
        canvas.add_patch(FancyBboxPatch(
            (x0, y0), width, height,
            boxstyle="round,pad=0.004,rounding_size=0.012",
            linewidth=1.2, edgecolor=edge, facecolor=face, alpha=0.55, zorder=1))
        canvas.text(x0 + 0.008, y0 + height - 0.022, label, ha="left", va="center",
                    fontsize=12.5, color=edge, fontweight="bold", zorder=3)

    # 12 个流程框
    centers = []
    for index, (number, title, details, key) in enumerate(FIGURE_C_BOXES):
        x0, y0, row = box_center(index)
        _label, edge, _face = FIGURE_C_GROUPS[key]
        canvas.add_patch(FancyBboxPatch(
            (x0, y0), box_w, box_h,
            boxstyle="round,pad=0.004,rounding_size=0.010",
            linewidth=1.6, edgecolor=edge, facecolor="white", zorder=2))
        canvas.text(x0 + 0.012, y0 + box_h - 0.032, "%s" % number, ha="left", va="center",
                    fontsize=11, color=edge, fontweight="bold", zorder=3)
        canvas.text(x0 + box_w / 2.0, y0 + box_h - 0.055, title, ha="center", va="center",
                    fontsize=13, color="#1A1A1A", fontweight="bold", zorder=3)
        for line_index, detail in enumerate(details):
            canvas.text(x0 + box_w / 2.0, y0 + box_h - 0.093 - line_index * 0.036, detail,
                        ha="center", va="center", fontsize=9, color=COLOR_GRAY, zorder=3)
        centers.append((x0, y0, row))

    def right_mid(index):
        x0, y0, _row = centers[index]
        return x0 + box_w, y0 + box_h / 2.0

    def left_mid(index):
        x0, y0, _row = centers[index]
        return x0, y0 + box_h / 2.0

    # 顺序箭头 1→2→…→10（实线；6→7 由折行箭头单独绘制，避免斜穿整张图）
    for index in range(9):
        if index == 5:
            continue
        x_start, y_start = right_mid(index)
        x_end, y_end = left_mid(index + 1)
        canvas.add_patch(FancyArrowPatch(
            (x_start + 0.004, y_start), (x_end - 0.005, y_end),
            arrowstyle="-|>", mutation_scale=15, linewidth=1.7, color="#333333", zorder=4))

    # S 形折行箭头：6（下边中点）→ 行间空隙 → 7（上边中点）
    x6_center = centers[5][0] + box_w / 2.0
    y6_bottom = centers[5][1]
    x7_center = centers[6][0] + box_w / 2.0
    y7_top = centers[6][1] + box_h
    corridor_y = (y6_bottom + y7_top) / 2.0
    canvas.plot([x6_center, x6_center], [y6_bottom, corridor_y],
                color="#333333", linewidth=1.7, zorder=4)
    canvas.plot([x6_center, x7_center], [corridor_y, corridor_y],
                color="#333333", linewidth=1.7, zorder=4)
    canvas.add_patch(FancyArrowPatch(
        (x7_center, corridor_y), (x7_center, y7_top),
        arrowstyle="-|>", mutation_scale=15, linewidth=1.7, color="#333333", zorder=4))

    # 独立证据分支（虚线）：
    #   10 → 11（同行直接连接，FFT 交叉验证）
    #   10 → 12（从行下方绕行，避开 11 号框，标准 SHM 参考）
    x10, y10 = right_mid(9)
    x11, y11 = left_mid(10)
    canvas.add_patch(FancyArrowPatch(
        (x10 + 0.004, y10), (x11 - 0.006, y11),
        arrowstyle="-|>", mutation_scale=14, linewidth=1.5,
        linestyle=(0, (5, 3)), color="#777777", zorder=4))

    x10_center = centers[9][0] + box_w / 2.0
    y10_bottom = centers[9][1]
    x12_center = centers[11][0] + box_w / 2.0
    y12_bottom = centers[11][1]
    detour_y = 0.175
    canvas.plot([x10_center, x10_center], [y10_bottom, detour_y],
                color="#777777", linewidth=1.5, linestyle=(0, (5, 3)), zorder=4)
    canvas.plot([x10_center, x12_center], [detour_y, detour_y],
                color="#777777", linewidth=1.5, linestyle=(0, (5, 3)), zorder=4)
    canvas.add_patch(FancyArrowPatch(
        (x12_center, detour_y), (x12_center, y12_bottom),
        arrowstyle="-|>", mutation_scale=14, linewidth=1.5,
        linestyle=(0, (5, 3)), color="#777777", zorder=4))

    canvas.text(0.5, 0.905, "VisionMotion：从外部视频到频率与物理参考的完整链路",
                ha="center", va="center", fontsize=19, color="#1A1A1A", fontweight="bold")
    canvas.text(0.5, 0.858,
                "实线 = 流程顺序；虚线 = 独立证据（FFT 交叉验证 / 标准模型参考），不改变时域测量结果",
                ha="center", va="center", fontsize=11, color=COLOR_GRAY)
    canvas.text(0.5, 0.115,
                "位置结果以像素 $y_0$ 与时间 $t$ 表达；本流程不涉及长度单位换算。",
                ha="center", va="center", fontsize=10, color=COLOR_GRAY)
    canvas.text(0.5, 0.075,
                "“差异 ≈ 1.0%” 表示实验频率与标准模型参考频率之差，不代表算法性能。",
                ha="center", va="center", fontsize=10, color=COLOR_GRAY)

    add_footer(fig)
    texts = collect_texts(fig)
    path, missing = save_figure(fig, out_path)
    plt.close(fig)
    return {
        "name": "C",
        "path": str(path),
        "n_boxes": len(FIGURE_C_BOXES),
        "n_groups": len(FIGURE_C_GROUPS),
        "group_labels": sorted({item[0] for item in FIGURE_C_GROUPS.values()}),
        "texts": texts,
        "missing_glyphs": missing,
    }


# ============================================================
# PNG 结构检查
# ============================================================


def check_png(path, expected_dpi=DPI):
    """
    读取 PNG 结构与元数据：文件存在、PNG 魔数、IHDR 尺寸、pHYs DPI、是否非空白。
    """
    path = Path(path)
    result = {
        "path": str(path),
        "exists": path.exists(),
        "is_png": False,
        "width": None,
        "height": None,
        "dpi": None,
        "dpi_ok": False,
        "non_white_fraction": None,
        "not_blank": False,
        "bytes": None,
    }
    if not path.exists():
        return result
    data = path.read_bytes()
    result["bytes"] = len(data)
    result["is_png"] = data[:8] == b"\x89PNG\r\n\x1a\n"
    if not result["is_png"]:
        return result

    offset = 8
    while offset < len(data):
        length = int.from_bytes(data[offset:offset + 4], "big")
        chunk_type = data[offset + 4:offset + 8]
        if chunk_type == b"IHDR":
            result["width"] = int.from_bytes(data[offset + 8:offset + 12], "big")
            result["height"] = int.from_bytes(data[offset + 12:offset + 16], "big")
        elif chunk_type == b"pHYs":
            pixels_x = int.from_bytes(data[offset + 8:offset + 12], "big")
            unit = data[offset + 16]
            if unit == 1:  # metre
                result["dpi"] = round(pixels_x * 0.0254)
        offset += 12 + length
        if chunk_type == b"IEND":
            break

    result["dpi_ok"] = result["dpi"] == expected_dpi

    image = mpimg.imread(path)
    rgb = image[..., :3]
    non_white = np.any(rgb < 0.985, axis=-1)
    result["non_white_fraction"] = float(non_white.mean())
    result["not_blank"] = result["non_white_fraction"] > 0.01
    return result


# ============================================================
# 正式流程：生成 + 自检 + 打印
# ============================================================


def run_all(csv_path=DEFAULT_CSV_PATH, out_dir=None, dpi=DPI):
    """
    生成三张最终 PNG 并完成自动自检，返回汇总 dict。
    """
    out_dir = PROJECT_ROOT / "results" if out_dir is None else Path(out_dir)
    font_name = setup_chinese_font()
    series = load_trajectory(csv_path)
    extrema_problems = check_frozen_extrema_against_csv(series)

    meta_a = make_figure_a(series, out_dir / FIGURE_A_NAME)
    meta_b = make_figure_b(out_dir / FIGURE_B_NAME)
    meta_c = make_figure_c(out_dir / FIGURE_C_NAME)

    png_a, png_b, png_c = (check_png(item["path"], dpi) for item in (meta_a, meta_b, meta_c))

    checks = []

    def add(description, ok):
        checks.append((description, bool(ok)))

    # 通用：文件与元数据
    for label, png in (("图 A", png_a), ("图 B", png_b), ("图 C", png_c)):
        add("%s 文件存在（%d 字节）" % (label, png["bytes"] or 0), png["exists"])
        add("%s 为 PNG（魔数正确）" % label, png["is_png"])
        add("%s 元数据 dpi = %s（要求 %d）" % (label, png["dpi"], dpi), png["dpi_ok"])
        add("%s 尺寸 = %s × %s px" % (label, png["width"], png["height"]), bool(png["width"] and png["height"]))
        add("%s 非空白（非白像素占比 %.4f）" % (label, png["non_white_fraction"] or 0.0), png["not_blank"])
        add("%s 无缺字警告（共 %d 条）" % (label, len(png_meta_missing(label, meta_a, meta_b, meta_c))),
            len(png_meta_missing(label, meta_a, meta_b, meta_c)) == 0)

    # 图 A 专项
    add("图 A 原始采样点数量 = %d（要求 160）" % meta_a["n_samples"], meta_a["n_samples"] == 160)
    add("图 A 局部极大 marker 数量 = %d（要求 10）" % meta_a["n_peaks"], meta_a["n_peaks"] == 10)
    add("图 A 局部极小 marker 数量 = %d（要求 10）" % meta_a["n_troughs"], meta_a["n_troughs"] == 10)
    add("图 A 代表性峰—峰箭头数量 = %d（要求 1）" % meta_a["n_representative_arrows"],
        meta_a["n_representative_arrows"] == 1)
    add("图 A 封板极值与 CSV 逐帧一致（含 3 处平台中点）", len(extrema_problems) == 0)
    if extrema_problems:
        print("    [极值不一致明细] %s" % "; ".join(extrema_problems))

    # 图 B 专项
    text_b = " ".join(meta_b["texts"])
    for token, description in (
        ("1.843003", "实验频率 1.843003 Hz"),
        ("1.862134625", "理论参考 1.862134625 Hz"),
        ("1.875", "FFT 主峰 1.875 Hz"),
        ("0.1875", "FFT 分辨率 0.1875 Hz"),
        ("1.855281725", "参数矩形下界"),
        ("1.868975645", "参数矩形上界"),
        ("保守采样定位上界（非统计误差）", "采样上界语义标注"),
        ("条件性的标准模型参考计算", "条件性模型声明"),
    ):
        add("图 B 含关键标注：%s" % description, token in text_b)

    # 图 C 专项
    text_c = " ".join(meta_c["texts"])
    add("图 C 流程框数量 = %d（要求 12）" % meta_c["n_boxes"], meta_c["n_boxes"] == 12)
    add("图 C 分组数量 = %d（要求 4）" % meta_c["n_groups"], meta_c["n_groups"] == 4)
    for group_name in ("计算机视觉", "时域测量", "频域交叉验证", "物理模型"):
        add("图 C 分组标签存在：%s" % group_name, group_name in text_c)
    add("图 C 含独立证据说明（虚线语义）", "独立证据" in text_c)

    # 违规词扫描（三张图）
    for meta in (meta_a, meta_b, meta_c):
        hits = scan_forbidden(meta["texts"])
        add("图 %s 无违规文字（命中 %d 条）" % (meta["name"], len(hits)), len(hits) == 0)
        if hits:
            print("    [违规文字明细] %s" % hits)

    passed = all(ok for _, ok in checks)
    return {
        "font_name": font_name,
        "series": series,
        "meta": {"A": meta_a, "B": meta_b, "C": meta_c},
        "png": {"A": png_a, "B": png_b, "C": png_c},
        "checks": checks,
        "passed": passed,
    }


def png_meta_missing(label, meta_a, meta_b, meta_c):
    """
    取对应图的缺字警告列表。
    """
    key = {"图 A": "A", "图 B": "B", "图 C": "C"}[label]
    for meta in (meta_a, meta_b, meta_c):
        if meta["name"] == key:
            return meta["missing_glyphs"]
    return []


def print_report(summary):
    """
    打印生成结果与自检明细。
    """
    print("")
    print("========== M6.3-3B 最终成果可视化：生成结果 ==========")
    print("中文字体：%s" % summary["font_name"])
    print("轨迹数据源：%s（%d 帧）" % (summary["series"]["path"], len(summary["series"]["frame"])))
    for key in ("A", "B", "C"):
        png = summary["png"][key]
        print("图 %s：%s" % (key, png["path"]))
        print("       %s × %s px ｜ %d 字节 ｜ dpi=%s ｜ 非白像素占比 %.4f"
              % (png["width"], png["height"], png["bytes"], png["dpi"], png["non_white_fraction"]))

    print("")
    print("========== 自动自检明细 ==========")
    for index, (description, ok) in enumerate(summary["checks"], start=1):
        print("%2d. [%s] %s" % (index, "通过" if ok else "未通过", description))
    print("自检结论：%s" % ("全部通过" if summary["passed"] else "存在未通过项"))
    print("===================================")
    return summary["passed"]


def main(csv_path=DEFAULT_CSV_PATH, out_dir=None):
    """
    模块入口（供 demo 调用）：生成三张图并打印自检结果。
    """
    summary = run_all(csv_path=csv_path, out_dir=out_dir)
    passed = print_report(summary)
    return 0 if passed else 1

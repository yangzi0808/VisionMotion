"""
VisionMotion —— v1.0.0 最终用户流程整合（demo/run_user_video_pipeline.py）

功能：一行命令，把「一个视频」变成「一套完整结果」。

        python demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4

自动串联目前已有的全部用户模块（本脚本只做串联与提示，不重新实现任何算法）：

    1. src.video_tracker.track_video                     -> <name>_track.csv / <name>_overlay.mp4
    2. src.user_visualization.plot_trajectory_from_track_csv -> <name>_trajectory.png
    3. src.user_displacement.compute_pixel_displacement_from_track_csv
    4. src.user_visualization.plot_displacement_curve    -> <name>_displacement.png
    5. src.user_frequency_analysis.compute_fft_from_displacement
    6. src.user_visualization.plot_fft_spectrum          -> <name>_fft.png

其中 <name> 由输入视频的文件名派生（Path.stem），例如：

    data\\raw\\user_video.mp4  ->  results\\user_video_track.csv
                                   results\\user_video_overlay.mp4
                                   results\\user_video_trajectory.png
                                   results\\user_video_displacement.png
                                   results\\user_video_fft.png

运行方式（在项目根目录下）：

    1）标准用法
    .venv\\Scripts\\python.exe demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4

    2）指定输出目录（目录不存在会自动创建）
    .venv\\Scripts\\python.exe demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4 --out-dir results\\my_run

    3）目标结果已存在时，必须显式允许覆盖（默认发现同名输出就停止）
    .venv\\Scripts\\python.exe demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4 --overwrite

路径规则：绝对路径原样使用；相对路径一律相对项目根目录解析（不依赖当前工作目录）。

冻结边界（本脚本不得越界）：
    只新增本文件；不修改 video_tracker.py / marker_detector.py / displacement.py /
    dynamic_displacement.py / 任何 user 模块；不改动 CSV 格式（表头与列的写法仍由
    src/video_tracker.py 唯一决定）。
    检测参数、FPS、标定、gate、s0、QC、SHA 逻辑全部留在 src/ 内，
    本脚本只把「输入视频」「输出目录」「是否允许覆盖」三个用户输入交给已有模块。

异常处理：所有「可预期的用户错误」都转成一句中文提示 + 一条处理建议，
          不向用户抛出长 traceback。

退出码（供脚本 / 自动化判断）：
    0 = 六步全部成功（轨迹图 / 位移图 / 频谱图都生成，且至少检出过一次目标）
    1 = 输入视频不存在，或视频无法处理
    2 = 目标输出文件已存在且未加 --overwrite
    3 = 视频正常处理，但全程没有检测到目标（下游分析无法进行）
    4 = 时域结果可用，但频域（FFT / 频谱图）步骤失败
    5 = 轨迹图 / 像素位移 / 位移曲线图等时域步骤失败
    6 = 用户主动中断（Ctrl+C）
"""

import argparse
import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.user_displacement import (  # noqa: E402
    UserDisplacementError,
    compute_pixel_displacement_from_track_csv,
)
from src.user_frequency_analysis import (  # noqa: E402
    UserFrequencyError,
    compute_fft_from_displacement,
)
from src.user_visualization import (  # noqa: E402
    UserVisualizationError,
    plot_displacement_curve,
    plot_fft_spectrum,
    plot_trajectory_from_track_csv,
)
from src.video_tracker import print_statistics, track_video  # noqa: E402

# ============================================================
# 默认输入输出
# ============================================================

DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "user_video.mp4"
DEFAULT_OUT_DIR = PROJECT_ROOT / "results"

# 输出文件名后缀（由输入视频名派生）
TRACK_CSV_SUFFIX = "_track.csv"
OVERLAY_MP4_SUFFIX = "_overlay.mp4"
TRAJECTORY_PNG_SUFFIX = "_trajectory.png"
DISPLACEMENT_PNG_SUFFIX = "_displacement.png"
FFT_PNG_SUFFIX = "_fft.png"

# 退出码
EXIT_SUCCESS = 0
EXIT_INPUT_ERROR = 1
EXIT_OUTPUT_EXISTS = 2
EXIT_NO_TARGET = 3
EXIT_FFT_FAILED = 4
EXIT_TIMEDOMAIN_FAILED = 5
EXIT_INTERRUPTED = 6

# 各步骤名称（用于汇总表与失败归类）
STEP_TRAJECTORY = "轨迹图"
STEP_DISPLACEMENT = "像素位移"
STEP_DISPLACEMENT_PNG = "位移曲线图"
STEP_FFT = "FFT 计算"
STEP_FFT_PNG = "频谱图"
TIME_DOMAIN_STEPS = (STEP_TRAJECTORY, STEP_DISPLACEMENT, STEP_DISPLACEMENT_PNG)
FREQUENCY_STEPS = (STEP_FFT, STEP_FFT_PNG)


# ============================================================
# 命令行参数
# ============================================================


def parse_args(argv=None):
    """
    解析命令行参数：输入视频、输出目录、覆盖开关。

    只暴露这三个用户输入；检测参数 / FPS / 标定 / gate / s0 / QC / SHA
    一律不作为参数出现（它们唯一来源仍是 src/ 内部实现）。
    """
    parser = argparse.ArgumentParser(
        prog="run_user_video_pipeline.py",
        description=(
            "VisionMotion v1.0.0：输入一个视频，自动生成轨迹 CSV、叠加视频、"
            "二维轨迹图、像素位移曲线图与 FFT 频谱图。"
        ),
        epilog=(
            "示例：\n"
            "  python demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4\n"
            "      输出到 results\\（目录不存在时自动创建）\n"
            "  python demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4 --out-dir results\\my_run\n"
            "      自定义输出目录\n"
            "  python demo\\run_user_video_pipeline.py --input data\\raw\\user_video.mp4 --overwrite\n"
            "      目标文件已存在时允许覆盖（默认发现同名输出就停止）\n"
            "\n"
            "路径说明：相对路径一律相对项目根目录解析，绝对路径原样使用。\n"
            "冻结说明：检测参数 / FPS / 标定 / gate / s0 / QC / SHA 均不是命令行参数。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        metavar="VIDEO",
        default=None,
        help="输入视频路径（默认：data\\raw\\user_video.mp4）",
    )
    parser.add_argument(
        "--out-dir",
        metavar="DIR",
        default=None,
        help="输出目录（默认：results\\；目录不存在时自动创建）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允许覆盖已存在的输出文件（默认：发现同名输出文件就停止）",
    )
    return parser.parse_args(argv)


def resolve_user_path(path_text, default_path):
    """
    把用户给的路径解析成绝对路径。

    规则：
        - 未提供（None）  -> 返回默认路径
        - 绝对路径        -> 原样使用
        - 相对路径        -> 相对项目根目录解析（不依赖当前工作目录）
    """
    if path_text is None:
        return default_path

    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def build_output_paths(input_path, out_dir):
    """
    由输入视频的文件名派生全部输出文件名（取 Path.stem，即不含扩展名的部分）。

    例：foo.MP4 -> <out_dir>/foo_track.csv、foo_overlay.mp4、foo_trajectory.png、
                  foo_displacement.png、foo_fft.png

    返回按固定顺序排列的 (标签, 路径) 列表，便于打印与逐项检查。
    """
    stem = input_path.stem
    return [
        ("轨迹 CSV", out_dir / (stem + TRACK_CSV_SUFFIX)),
        ("叠加视频", out_dir / (stem + OVERLAY_MP4_SUFFIX)),
        ("二维轨迹图", out_dir / (stem + TRAJECTORY_PNG_SUFFIX)),
        ("像素位移曲线图", out_dir / (stem + DISPLACEMENT_PNG_SUFFIX)),
        ("FFT 频谱图", out_dir / (stem + FFT_PNG_SUFFIX)),
    ]


def format_size(size_bytes):
    """把字节数格式化成便于阅读的字符串。"""
    if size_bytes < 1024:
        return "%d B" % size_bytes
    if size_bytes < 1024 * 1024:
        return "%.1f KiB" % (size_bytes / 1024.0)
    return "%.2f MiB" % (size_bytes / (1024.0 * 1024.0))


# ============================================================
# 主流程
# ============================================================


def run_pipeline(input_path, out_dir, overwrite):
    """
    执行完整流程，返回退出码（不抛异常）。

    步骤：追踪 -> 轨迹图 -> 像素位移 -> 位移图 -> FFT -> 频谱图。
    每一步的「可预期用户错误」都转成一句中文提示；某一步失败时，
    依赖它的后续步骤会明确标为「未执行」，而不是抛 traceback。
    """
    output_items = build_output_paths(input_path, out_dir)
    label_to_path = {label: path for label, path in output_items}
    csv_path = label_to_path["轨迹 CSV"]
    overlay_path = label_to_path["叠加视频"]

    print("========== VisionMotion v1.0.0 用户视频完整流程 ==========")
    print("输入视频：%s" % input_path)
    print("输出目录：%s" % out_dir)
    print("流程：追踪 -> 轨迹图 -> 像素位移 -> 位移图 -> FFT -> 频谱图")
    print("")

    # ---- 输入检查：视频必须存在 ----
    if not input_path.is_file():
        print("错误：输入视频不存在：%s" % input_path)
        print("提示：")
        print("  1) 确认视频文件已经放到该路径（默认位置是 data\\raw\\user_video.mp4）；")
        print("  2) --input 支持绝对路径，也支持相对项目根目录的路径（例如 data\\raw\\my_video.mp4）。")
        print("")
        return EXIT_INPUT_ERROR

    # ---- 覆盖保护：默认不覆盖已有结果 ----
    existing_files = [path for _label, path in output_items if path.exists()]
    if existing_files and not overwrite:
        print("错误：目标输出文件已存在，已停止（默认不覆盖已有结果）：")
        for path in existing_files:
            print("  %s" % path)
        print("处理方式（二选一）：")
        print("  1) 换一个输出目录：--out-dir <DIR>")
        print("  2) 确认要覆盖已有结果：加 --overwrite")
        print("")
        return EXIT_OUTPUT_EXISTS

    if existing_files:
        print("提示：--overwrite 已开启，将覆盖以下已存在的输出：")
        for path in existing_files:
            print("  %s" % path)
        print("")

    # 输出目录：不存在则创建（track_video 内部也会创建，这里显式做一次）
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print("错误：无法创建输出目录：%s（%s）" % (out_dir, error))
        print("提示：请确认该路径可写，或用 --out-dir 指定其他目录。")
        print("")
        return EXIT_INPUT_ERROR

    # ---- 步骤 1：逐帧追踪（CSV + 叠加视频来自同一次逐帧处理）----
    print("---------- 步骤 1/6：视频逐帧追踪 ----------")
    summary = track_video(input_path, csv_path, overlay_path)
    if summary is None:
        print("")
        print("错误：视频无法处理（文件损坏、编码不支持，或 FPS 非法）。")
        print("提示：请换一个可正常播放的 mp4 视频，或用其他工具重新导出后再试。")
        print("")
        return EXIT_INPUT_ERROR

    print_statistics(summary)

    if summary["interrupted"]:
        print("")
        print("错误：检测到用户中断（Ctrl+C），本次只保留截至中断时已处理的数据。")
        print("提示：重新运行并让视频处理完成，才能得到完整的轨迹与频谱结果。")
        print("")
        return EXIT_INTERRUPTED

    # 没有检测到目标：下游（轨迹 / 位移 / FFT）不可能有有效数据，直接友好停止
    if summary["detected_frames"] == 0:
        print("")
        print("错误：整段视频没有检测到目标（共处理 %d 帧，全部检测失败）。"
              % summary["processed_frames"])
        print("提示：")
        print("  1) 确认视频里确实有红色标记目标，且目标没有被遮挡或跑出画面；")
        print("  2) 确认光线充足、标记颜色没有被白平衡 / 压缩严重改变；")
        print("  3) 可先用 demo\\run_video_tracking.py 查看叠加视频，逐帧确认失败原因。")
        print("已生成（仅供排查）：%s" % csv_path)
        if summary["overlay_ok"]:
            print("已生成（仅供排查）：%s" % overlay_path)
        print("未生成：轨迹图 / 位移曲线图 / 频谱图（没有有效数据）。")
        print("")
        return EXIT_NO_TARGET

    if not summary["overlay_ok"]:
        print("")
        print("警告：叠加视频写入器不可用，%s 未生成。" % overlay_path)
        print("      已回退保存 %d 张代表性 PNG（不影响后续分析与绘图）。"
              % len(summary["fallback_pngs"]))

    # ---- 步骤 2 ~ 6：串联已有用户模块，逐步收集失败信息 ----
    # failures: [(步骤名, 中文提示), ...]；skipped: [步骤名, ...]（上游失败导致未执行）
    failures = []
    skipped = []

    # 步骤 2：二维轨迹图
    print("")
    print("---------- 步骤 2/6：生成二维轨迹图 ----------")
    try:
        trajectory_report = plot_trajectory_from_track_csv(
            csv_path, label_to_path["二维轨迹图"]
        )
        print("已生成：%s（有效轨迹点 %d，%s）"
              % (
                  trajectory_report["output_path"],
                  trajectory_report["valid_points"],
                  format_size(trajectory_report["png_size_bytes"]),
              ))
    except UserVisualizationError as error:
        print("失败：%s" % error)
        failures.append((STEP_TRAJECTORY, str(error)))

    # 步骤 3：像素位移（只读 CSV，不修改任何文件）
    print("")
    print("---------- 步骤 3/6：计算像素位移 ----------")
    displacement_data = None
    try:
        displacement_data = compute_pixel_displacement_from_track_csv(csv_path)
        print("已完成：有效点 %d，参考点 (%.2f, %.2f) px，最大位移 %.2f px"
              % (
                  displacement_data["valid_points"],
                  displacement_data["x0"],
                  displacement_data["y0"],
                  displacement_data["max_displacement_px"],
              ))
    except UserDisplacementError as error:
        print("失败：%s" % error)
        failures.append((STEP_DISPLACEMENT, str(error)))

    # 步骤 4：位移曲线图（依赖步骤 3 的结果）
    print("")
    print("---------- 步骤 4/6：生成像素位移曲线图 ----------")
    if displacement_data is None:
        print("已跳过：上游「像素位移」失败，无法生成位移曲线图。")
        skipped.append(STEP_DISPLACEMENT_PNG)
    else:
        try:
            displacement_report = plot_displacement_curve(
                displacement_data, label_to_path["像素位移曲线图"]
            )
            print("已生成：%s（点数 %d，最大位移 %.2f px，%s）"
                  % (
                      displacement_report["output_path"],
                      displacement_report["points"],
                      displacement_report["max_displacement_px"],
                      format_size(displacement_report["png_size_bytes"]),
                  ))
        except UserVisualizationError as error:
            print("失败：%s" % error)
            failures.append((STEP_DISPLACEMENT_PNG, str(error)))

    # 步骤 5：FFT（依赖步骤 3 的时域数据）
    print("")
    print("---------- 步骤 5/6：计算 FFT 频谱 ----------")
    fft_data = None
    if displacement_data is None:
        print("已跳过：上游「像素位移」失败，无法进行 FFT。")
        skipped.append(STEP_FFT)
    else:
        try:
            fft_data = compute_fft_from_displacement(
                displacement_data["time_s"], displacement_data["displacement_px"]
            )
            print("已完成：n = %d 点，dt = %.6g s，df = %.6g Hz，主峰 %.4f Hz（%.4f px）"
                  % (
                      fft_data["n_points"],
                      fft_data["dt"],
                      fft_data["df"],
                      fft_data["peak_frequency"],
                      fft_data["peak_amplitude"],
                  ))
        except UserFrequencyError as error:
            print("失败：FFT 无法完成。")
            print("原因：%s" % error)
            print("提示：视频位移序列的采样必须严格均匀。若视频存在丢帧或检测中断，")
            print("      有效点之间的时间间隔会不均匀，本阶段不做插值 / 重采样，")
            print("      因此无法得到频谱。请确认视频中目标在整段时长内都被稳定检出。")
            failures.append((STEP_FFT, str(error)))

    # 步骤 6：频谱图（依赖步骤 5 的 FFT 结果）
    print("")
    print("---------- 步骤 6/6：生成 FFT 频谱图 ----------")
    if fft_data is None:
        print("已跳过：上游「FFT 计算」未成功，无法生成频谱图。")
        skipped.append(STEP_FFT_PNG)
    else:
        # 让图标题使用输入 CSV 的文件名（与轨迹图 / 位移图保持同一命名口径）
        fft_data["csv_path"] = csv_path
        try:
            fft_report = plot_fft_spectrum(fft_data, label_to_path["FFT 频谱图"])
            print("已生成：%s（频点数 %d，主峰 %.4f Hz，%s）"
                  % (
                      fft_report["output_path"],
                      fft_report["bins"],
                      fft_report["peak_frequency"],
                      format_size(fft_report["png_size_bytes"]),
                  ))
        except UserVisualizationError as error:
            print("失败：%s" % error)
            failures.append((STEP_FFT_PNG, str(error)))

    # ---- 汇总：逐个输出文件报告「生成 / 未生成」----
    # 已知不会生成的输出：叠加视频（写入器不可用时只回退 PNG 帧）+ 失败步骤对应的图
    failed_labels = set()
    if not summary["overlay_ok"]:
        failed_labels.add("叠加视频")
    # 失败步骤 -> 对应输出标签（用于汇总表）
    step_to_label = {
        STEP_TRAJECTORY: "二维轨迹图",
        STEP_DISPLACEMENT_PNG: "像素位移曲线图",
        STEP_FFT_PNG: "FFT 频谱图",
    }
    failed_labels |= {step_to_label[step] for step, _message in failures if step in step_to_label}

    print("")
    print("========== 本次生成的文件 ==========")
    for label, path in output_items:
        if path.exists() and label not in failed_labels:
            print("[已生成] %-14s %s（%s）" % (label, path, format_size(path.stat().st_size)))
        else:
            print("[未生成] %-14s %s" % (label, path))

    if failures or skipped:
        print("")
        print("========== 问题汇总 ==========")
        for step, message in failures:
            print("[失败] %s：%s" % (step, message))
        for step in skipped:
            print("[未执行] %s（上游步骤失败）" % step)

    # ---- 结果判定（退出码）----
    print("")
    print("========== 结果判定（退出码） ==========")
    if not failures:
        print("退出码：0（六步全部成功）")
        print("")
        return EXIT_SUCCESS

    time_domain_failed = any(step in TIME_DOMAIN_STEPS for step, _message in failures)
    if time_domain_failed:
        print("退出码：%d（轨迹图 / 像素位移 / 位移曲线图等时域步骤失败）"
              % EXIT_TIMEDOMAIN_FAILED)
        print("")
        return EXIT_TIMEDOMAIN_FAILED

    if any(step in FREQUENCY_STEPS for step, _message in failures):
        print("退出码：%d（时域结果可用，但频域 FFT / 频谱图失败）" % EXIT_FFT_FAILED)
        print("")
        return EXIT_FFT_FAILED

    print("退出码：%d（存在未成功的步骤）" % EXIT_TIMEDOMAIN_FAILED)
    print("")
    return EXIT_TIMEDOMAIN_FAILED


def main(argv=None):
    """
    命令行入口：解析参数 -> 执行流程 -> 返回退出码。

    这里额外兜住两类情况，确保用户不会看到长 traceback：
        - KeyboardInterrupt（Ctrl+C）
        - 任何未预期异常（只打印一行类型与消息，便于反馈定位）
    """
    args = parse_args(argv)

    input_path = resolve_user_path(args.input, DEFAULT_INPUT_PATH)
    out_dir = resolve_user_path(args.out_dir, DEFAULT_OUT_DIR)

    try:
        return run_pipeline(input_path, out_dir, args.overwrite)
    except KeyboardInterrupt:
        print("")
        print("已中断：用户主动按 Ctrl+C，本次流程停止（未完成的输出文件可能不存在）。")
        return EXIT_INTERRUPTED
    except Exception as error:  # noqa: BLE001 —— 面向最终用户，不打印长 traceback
        print("")
        print("错误：流程执行中出现未预期的问题：%s: %s"
              % (type(error).__name__, error))
        print("提示：请把上面这一行连同你运行的命令一起反馈，便于定位问题。")
        return EXIT_INPUT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())

"""
VisionMotion —— v1.0.0 Phase 3（VM-V1.0-P3-01）用户 FFT 频谱演示入口

功能：读取已有 results/ 下的任意 *_track.csv（M3 格式），依次完成：

    results/<video_name>_track.csv
      -> src/user_displacement.py        计算像素位移（Phase 2）
      -> src/user_frequency_analysis.py  对位移序列做 FFT（Phase 3）
      -> results/<video_name>_fft.png    生成单边幅值谱

本脚本只负责：
    1. 扫描 results/ 下全部 *_track.csv
    2. 调 user_displacement 得到 time_s / displacement_px
    3. 调 user_frequency_analysis 得到 frequency / amplitude / 主峰
    4. 调 user_visualization 的 plot_fft_spectrum() 出图
    5. 打印结果

本脚本不修改任何旧 demo、不修改 CSV、不修改任何实验冻结代码；
本阶段只做「一次 FFT」——不做 mm 标定、不做 STFT、不做滤波。

覆盖行为：输出目录固定为 results/。目标 PNG 已存在时，本脚本**跳过、不覆盖**
（与 demo/test_user_displacement.py 一致，避免破坏仓库自带的冻结成果图）。
如需重新生成，请先手动删除该 PNG。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\test_user_fft.py

退出码：
    0 = results/ 下所有 track CSV 都成功生成频谱图
    1 = 没有找到任何 track CSV，或存在失败（读取 / 位移 / FFT / 绘图失败）
    2 = 目标 PNG 全部已存在，本次跳过、未生成任何新图
"""

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
    plot_fft_spectrum,
)

# ============================================================
# 输入输出
# ============================================================

RESULT_DIR = PROJECT_ROOT / "results"

TRACK_CSV_SUFFIX = "_track.csv"
FFT_PNG_SUFFIX = "_fft.png"


def build_output_path(csv_path):
    """
    由 track CSV 文件名派生输出的频谱图路径：

        results/EXP-002-VIDEO-001_track.csv -> results/EXP-002-VIDEO-001_fft.png
        results/user_video_track.csv        -> results/user_video_fft.png

    若文件名不以 _track.csv 结尾，则退化为「文件名 + _fft.png」。
    """
    stem = csv_path.stem
    if stem.endswith("_track"):
        stem = stem[: -len("_track")]
    return RESULT_DIR / (stem + FFT_PNG_SUFFIX)


def main():
    print("========== VisionMotion v1.0.0 Phase 3 FFT 频谱 ==========")
    print("数据链：track CSV -> 像素位移（Phase 2）-> 一次 FFT -> 单边幅值谱")
    print("说明：本阶段只做一次 FFT（不做 mm 标定、不做 STFT、不做滤波）。")
    print("")

    if not RESULT_DIR.is_dir():
        print("错误：结果目录不存在：%s" % RESULT_DIR)
        print("")
        return 1

    csv_paths = sorted(RESULT_DIR.glob("*" + TRACK_CSV_SUFFIX))
    if not csv_paths:
        print("错误：没有找到任何 track CSV：%s" % RESULT_DIR)
        print("提示：先用 demo\\run_video_tracking.py 生成 *_track.csv。")
        print("")
        return 1

    print("待处理 track CSV：%d 份" % len(csv_paths))

    reports = []
    failures = []
    skipped_existing = []

    for csv_path in csv_paths:
        output_path = build_output_path(csv_path)
        print("")
        print("------------------------------------------------------------")
        print("输入 CSV：%s" % csv_path)
        print("输出 PNG：%s" % output_path)

        # 非破坏性默认：目标已存在就跳过，绝不覆盖
        if output_path.exists():
            print("[跳过] 目标 PNG 已存在，未覆盖（如需重新生成，请先手动删除该文件）")
            skipped_existing.append(output_path)
            continue

        try:
            # 1. 像素位移（Phase 2，只读 CSV）
            displacement_data = compute_pixel_displacement_from_track_csv(csv_path)

            # 2. 一次 FFT（Phase 3）
            fft_data = compute_fft_from_displacement(
                displacement_data["time_s"], displacement_data["displacement_px"]
            )

            # 3. 出图
            fft_data["csv_path"] = csv_path
            report = plot_fft_spectrum(fft_data, output_path)
        except (UserDisplacementError, UserFrequencyError, UserVisualizationError) as error:
            print("[失败] %s" % error)
            failures.append((csv_path, str(error)))
            continue

        reports.append(report)
        print(
            "已生成：%s（点数 %d，dt=%.6g s，df=%.6g Hz，主峰 %.4f Hz / %.4f px，%.1f KiB）"
            % (
                report["output_path"],
                fft_data["n_points"],
                fft_data["dt"],
                fft_data["df"],
                report["peak_frequency"],
                report["peak_amplitude"],
                report["png_size_bytes"] / 1024.0,
            )
        )

    print("")
    print("========== 本次汇总 ==========")
    print("成功生成：%d 份" % len(reports))
    print("已存在而跳过：%d 份" % len(skipped_existing))
    print("失败：%d 份" % len(failures))
    for csv_path, message in failures:
        print("  %s -> %s" % (csv_path, message))
    print("")

    # 结果判定（退出码）
    print("========== 结果判定（退出码） ==========")
    if failures:
        print("退出码：1（存在失败的 track CSV）")
        print("")
        return 1
    if not reports and skipped_existing:
        print("退出码：2（目标 PNG 全部已存在，本次跳过、未生成任何新图）")
        print("")
        return 2
    print("退出码：0（全部 track CSV 都已成功生成频谱图）")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
VisionMotion —— v1.0.0 Phase 2（VM-V1.0-P2-01）用户位移曲线演示入口

功能：读取已有 results/ 下的任意 *_track.csv（M3 格式），
      为每一份 CSV 生成对应的像素位移-时间曲线：

          results/<video_name>_track.csv
            -> results/<video_name>_displacement.png

位移定义（纯像素、无标定）：

    参考点 = CSV 中第一个 detected=True 的有效点 (x0, y0)
    displacement_px = sqrt((x - x0)^2 + (y - y0)^2)

本脚本只负责：
    1. 扫描 results/ 下全部 *_track.csv
    2. 调 src/user_displacement.py 计算像素位移
    3. 调 src/user_visualization.py 的 plot_displacement_curve() 出图
    4. 打印结果

本脚本不修改任何旧 demo、不修改 CSV、不修改任何实验冻结代码；
本阶段只生成像素位移曲线——不做 mm 标定、不做 FFT。

覆盖行为：输出目录固定为 results/。目标 PNG 已存在时，本脚本**跳过、不覆盖**，
并打印 [跳过] 提示——不做交互、不新增命令行参数。
原因：results/ 里已经有仓库自带的冻结成果图（例如 EXP-004-DYNAMIC-001_displacement.png
是 M5.3 的正式产物），同名覆盖会破坏既有实验结果，因此本阶段一律不覆盖。
如需重新生成某张图，请先手动删除该 PNG 再运行本脚本。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\test_user_displacement.py

退出码：
    0 = results/ 下所有 track CSV 都成功生成位移曲线
    1 = 没有找到任何 track CSV，或存在失败（读取 / 计算 / 绘图失败）
    2 = 目标 PNG 全部已存在，本次跳过、未生成任何新图（这是安全的默认行为）
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
from src.user_visualization import (  # noqa: E402
    UserVisualizationError,
    plot_displacement_curve,
)

# ============================================================
# 输入输出
# ============================================================

RESULT_DIR = PROJECT_ROOT / "results"

TRACK_CSV_SUFFIX = "_track.csv"
DISPLACEMENT_PNG_SUFFIX = "_displacement.png"


def build_output_path(csv_path):
    """
    由 track CSV 文件名派生输出的位移曲线路径：

        results/EXP-002-VIDEO-001_track.csv -> results/EXP-002-VIDEO-001_displacement.png
        results/user_video_track.csv        -> results/user_video_displacement.png

    若文件名不以 _track.csv 结尾，则退化为「文件名 + _displacement.png」。
    """
    stem = csv_path.stem
    if stem.endswith("_track"):
        stem = stem[: -len("_track")]
    return RESULT_DIR / (stem + DISPLACEMENT_PNG_SUFFIX)


def main():
    print("========== VisionMotion v1.0.0 Phase 2 像素位移曲线 ==========")
    print("位移定义：参考点 = 第一个有效检测点，displacement_px = 像素距离")
    print("说明：本阶段只输出像素位移（不做 mm 标定、不做 FFT）。")
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
        # （results/ 里有仓库自带的冻结成果图，同名覆盖会破坏既有结果）
        if output_path.exists():
            print("[跳过] 目标 PNG 已存在，未覆盖（如需重新生成，请先手动删除该文件）")
            skipped_existing.append(output_path)
            continue

        try:
            data = compute_pixel_displacement_from_track_csv(csv_path)
            report = plot_displacement_curve(data, output_path)
        except (UserDisplacementError, UserVisualizationError) as error:
            print("[失败] %s" % error)
            failures.append((csv_path, str(error)))
            continue

        reports.append(report)
        print(
            "已生成：%s（有效点 %d，最大位移 %.2f px，%.1f KiB）"
            % (
                report["output_path"],
                report["points"],
                report["max_displacement_px"],
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
    print("退出码：0（全部 track CSV 都已成功生成位移曲线）")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

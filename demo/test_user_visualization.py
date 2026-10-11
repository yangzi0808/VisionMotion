"""
VisionMotion —— v1.0.0 Phase 1（VM-V1.0-P1-01）用户轨迹可视化演示入口

功能：读取已有 results/ 下的任意 *_track.csv（M3 格式），
      为每一份 CSV 生成对应的轨迹图：

          results/<video_name>_track.csv
            -> results/<video_name>_trajectory.png

本脚本只负责：
    1. 决定要处理哪些 track CSV（默认扫描 results/ 下全部 *_track.csv）
    2. 决定输出 PNG 路径（由 CSV 文件名派生）
    3. 调 src/user_visualization.py 的 plot_trajectory_from_track_csv()
    4. 打印结果

绘图算法全部在 src/user_visualization.py 里，本脚本不重复实现；
本脚本不修改任何旧 demo、不修改 CSV、不修改 src/ 中任何冻结常量。

本阶段只生成轨迹图 trajectory.png——不做位移、不做标定、不做 FFT。

运行方式（在项目根目录下）：

    1）无参数：处理 results/ 下所有 *_track.csv
    .venv\\Scripts\\python.exe demo\\test_user_visualization.py

    2）只处理指定的一份 CSV
    .venv\\Scripts\\python.exe demo\\test_user_visualization.py --input results\\EXP-002-VIDEO-001_track.csv

    3）指定输出目录（不存在会自动创建）
    .venv\\Scripts\\python.exe demo\\test_user_visualization.py --out-dir results\\my_video

    4）目标 PNG 已存在时，必须显式允许覆盖
    .venv\\Scripts\\python.exe demo\\test_user_visualization.py --overwrite

路径规则：绝对路径原样使用；相对路径一律相对项目根目录解析。

退出码：
    0 = 所有待处理的 track CSV 都成功生成轨迹图
    1 = 存在错误（没有找到任何 track CSV / 读取或绘图失败）
    2 = 目标 PNG 已存在且未加 --overwrite，本次全部跳过（没有生成任何新图）
"""

import argparse
import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.user_visualization import (  # noqa: E402
    UserVisualizationError,
    plot_trajectory_from_track_csv,
)

# ============================================================
# 默认输入输出
# ============================================================

DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"

# 默认扫描的 track CSV 文件名后缀
TRACK_CSV_SUFFIX = "_track.csv"

# 输出 PNG 文件名后缀
TRAJECTORY_PNG_SUFFIX = "_trajectory.png"


def parse_args(argv=None):
    """解析命令行参数：一份可选输入 CSV、输出目录、覆盖开关。"""
    parser = argparse.ArgumentParser(
        prog="test_user_visualization.py",
        description=(
            "VisionMotion v1.0.0 Phase 1：读取 track CSV，生成目标运动二维轨迹图（PNG）。"
        ),
        epilog=(
            "示例：\n"
            "  python demo\\test_user_visualization.py\n"
            "      处理 results\\ 下全部 *_track.csv\n"
            "  python demo\\test_user_visualization.py --input results\\EXP-002-VIDEO-001_track.csv\n"
            "      只处理指定的一份 CSV\n"
            "  python demo\\test_user_visualization.py --out-dir results\\my_video\n"
            "      输出目录不存在时自动创建\n"
            "  python demo\\test_user_visualization.py --overwrite\n"
            "      目标 PNG 已存在时允许覆盖\n"
            "\n"
            "说明：本阶段只生成轨迹图，不做位移 / 标定 / FFT。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        metavar="CSV",
        default=None,
        help="输入 track CSV（默认：扫描 results\\ 下全部 *_track.csv）",
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
        help="允许覆盖已存在的轨迹图（默认：已存在就跳过，不覆盖）",
    )
    return parser.parse_args(argv)


def resolve_user_path(path_text, default_path):
    """
    把用户给的路径解析成绝对路径：
    未提供（None）-> 默认路径；绝对路径 -> 原样使用；相对路径 -> 相对项目根目录。
    """
    if path_text is None:
        return default_path

    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def build_output_path(csv_path, out_dir):
    """
    由 track CSV 文件名派生输出 PNG 路径：

        results/EXP-002-VIDEO-001_track.csv -> <out_dir>/EXP-002-VIDEO-001_trajectory.png
        results/user_video_track.csv        -> <out_dir>/user_video_trajectory.png

    若文件名不以 _track.csv 结尾，则退化为「文件名 + _trajectory.png」。
    """
    stem = csv_path.stem
    if stem.endswith("_track"):
        stem = stem[: -len("_track")]
    return out_dir / (stem + TRAJECTORY_PNG_SUFFIX)


def discover_track_csvs(input_path):
    """
    决定本次要处理的 track CSV 列表：

        - 显式给了 --input：只处理这一份（存在性由绘图模块负责报错）
        - 没给 --input：扫描 results/ 下全部 *_track.csv（按文件名排序）

    返回 Path 列表（可能为空）。
    """
    if input_path is not None:
        return [input_path]

    if not DEFAULT_RESULTS_DIR.is_dir():
        return []

    return sorted(DEFAULT_RESULTS_DIR.glob("*" + TRACK_CSV_SUFFIX))


def main():
    args = parse_args()

    input_path = resolve_user_path(args.input, None)
    out_dir = resolve_user_path(args.out_dir, DEFAULT_RESULTS_DIR)

    print("========== VisionMotion v1.0.0 Phase 1 用户轨迹可视化 ==========")
    print("说明：本阶段只生成二维轨迹图（trajectory.png）；不做位移 / 标定 / FFT。")
    print("")

    csv_paths = discover_track_csvs(input_path)
    if not csv_paths:
        print("错误：没有找到任何 track CSV。")
        print("提示：先用 demo\\run_video_tracking.py 生成 *_track.csv，"
              "或用 --input 指定一份 CSV。")
        print("")
        return 1

    print("输出目录：%s" % out_dir)
    print("待处理 track CSV：%d 份" % len(csv_paths))
    print("")

    reports = []
    failures = []
    skipped_existing = []

    for csv_path in csv_paths:
        output_path = build_output_path(csv_path, out_dir)
        print("------------------------------------------------------------")
        print("输入 CSV：%s" % csv_path)
        print("输出 PNG：%s" % output_path)

        # 覆盖保护：目标已存在且未显式允许覆盖时跳过，不静默覆盖
        if output_path.exists() and not args.overwrite:
            print("[跳过] 目标 PNG 已存在（加 --overwrite 可覆盖）")
            skipped_existing.append(output_path)
            continue

        try:
            report = plot_trajectory_from_track_csv(csv_path, output_path)
        except UserVisualizationError as error:
            print("[失败] %s" % error)
            failures.append((csv_path, str(error)))
            continue

        reports.append(report)
        print(
            "已生成：%s（数据行 %d，有效点 %d，跳过 %d，%.1f KiB）"
            % (
                report["output_path"],
                report["total_rows"],
                report["valid_points"],
                report["skipped_rows"],
                report["png_size_bytes"] / 1024.0,
            )
        )

    print("")
    print("========== 本次汇总 ==========")
    print("成功生成：%d 份" % len(reports))
    print("因已存在而跳过：%d 份" % len(skipped_existing))
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
        print("退出码：2（目标 PNG 全部已存在且未加 --overwrite，本次未生成任何新图）")
        print("")
        return 2
    print("退出码：0（全部待处理的 track CSV 都已成功生成轨迹图）")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""
VisionMotion —— M3.3 演示脚本

功能：读取真实视频，逐帧调用现有检测器，生成时序坐标 CSV 与叠加可视化。

本脚本只负责：
    1. 决定输入视频路径（命令行参数，或向后兼容的默认值）
    2. 决定输出目录，并由输入视频的文件名派生输出文件名
    3. 启动 src/video_tracker.py 里的追踪流程
    4. 打印最终结果

运行方式（在项目根目录下）：

    1）无参数：完全保持旧行为
    .venv\\Scripts\\python.exe demo\\run_video_tracking.py
       -> 输入 data/raw/EXP-002-VIDEO-001.mp4
       -> 输出 results/EXP-002-VIDEO-001_track.csv
                 results/EXP-002-VIDEO-001_overlay.mp4

    2）指定输入视频：输出文件名自动跟随输入文件名
    .venv\\Scripts\\python.exe demo\\run_video_tracking.py --input data\\raw\\my_video.mp4
       -> 输出 results/my_video_track.csv
                 results/my_video_overlay.mp4

    3）指定输出目录（目录不存在会自动创建）
    .venv\\Scripts\\python.exe demo\\run_video_tracking.py --input data\\raw\\my_video.mp4 --out-dir results\\my_video
       -> 输出 results/my_video/my_video_track.csv
                 results/my_video/my_video_overlay.mp4

    4）目标文件已存在时，必须显式允许覆盖
    .venv\\Scripts\\python.exe demo\\run_video_tracking.py --input data\\raw\\my_video.mp4 --overwrite

路径规则：
    绝对路径原样使用；相对路径一律相对项目根目录解析（不依赖当前工作目录），
    因此在任何工作目录下运行，上面这些示例命令都能照抄使用。

冻结边界（本脚本不提供、也不得新增对应命令行参数）：
   检测器参数（HSV / MIN_AREA）、FPS、标定、valid gate、s0、QC、SHA 逻辑
   全部留在 src/ 内。本脚本只把「输入视频」与「输出目录」两个用户输入
    交给 track_video()，其余一律沿用原有实现。

退出码（供脚本 / 自动化判断；终端输出仍保留全部统计与自检细节）：
    0 = 视频处理正常完成（轨迹完整性 complete）、至少检出过一次目标、且 CSV 自检通过
    1 = 输入 / 视频处理错误；CSV 自检未通过也属于此类
    2 = 输出文件已存在（未加 --overwrite）；argparse 参数用法错误默认也是 2
    3 = 视频处理正常完成（轨迹完整性 complete）、CSV 自检通过，但全程没有检出到任何目标
    4 = 用户主动按 Ctrl+C 中断逐帧视频处理；通常只保留截至中断时已处理的数据
    5 = 轨迹完整性存疑或未验证（track_integrity 为 suspect / unverified）；
        不是崩溃、不是输入错误、不是 QC 失败、也不是用户中断
"""

import argparse
import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.video_tracker import (  # noqa: E402
    check_csv_data,
    print_check_results,
    print_statistics,
    track_video,
)

# ============================================================
# 默认输入输出（只用于「无参数运行」，保持旧行为）
# ============================================================

DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-002-VIDEO-001.mp4"
DEFAULT_OUT_DIR = PROJECT_ROOT / "results"


def parse_args(argv=None):
    """
    解析命令行参数。

    只暴露两个用户输入（输入视频、输出目录）和一个输出覆盖开关；
    检测参数 / FPS / 标定 / gate / s0 / QC / SHA 一律不作为参数出现。
    """
    parser = argparse.ArgumentParser(
        prog="run_video_tracking.py",
        description=(
            "VisionMotion M3.3：读取一个视频，逐帧检测红色标记，"
            "生成像素坐标时序 CSV 与叠加可视化。"
        ),
        epilog=(
            "示例：\n"
            "  python demo\\run_video_tracking.py\n"
            "      无参数运行（保持旧行为）：输入 data\\raw\\EXP-002-VIDEO-001.mp4，输出到 results\\\n"
            "  python demo\\run_video_tracking.py --input data\\raw\\my_video.mp4\n"
            "      输出 results\\my_video_track.csv 与 results\\my_video_overlay.mp4\n"
            "  python demo\\run_video_tracking.py --input data\\raw\\my_video.mp4 --out-dir results\\my_video\n"
            "      输出目录不存在时自动创建\n"
            "  python demo\\run_video_tracking.py --input data\\raw\\my_video.mp4 --overwrite\n"
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
        help="输入视频路径（默认：data\\raw\\EXP-002-VIDEO-001.mp4）",
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
    由输入视频的文件名派生输出文件名（取 Path.stem，即不含扩展名的部分）。

    例：foo.MP4 -> <out_dir>/foo_track.csv、<out_dir>/foo_overlay.mp4
    这样换输入视频时，输出名会自动跟着变，不会再冒充 EXP-002-VIDEO-001。
    """
    stem = input_path.stem
    return out_dir / ("%s_track.csv" % stem), out_dir / ("%s_overlay.mp4" % stem)


def main():
    args = parse_args()

    input_path = resolve_user_path(args.input, DEFAULT_INPUT_PATH)
    out_dir = resolve_user_path(args.out_dir, DEFAULT_OUT_DIR)
    csv_path, overlay_path = build_output_paths(input_path, out_dir)

    # 用户是否显式给出了新的输入 / 输出位置。
    # 两者都没给 = 旧的无参数运行方式：旧的 EXP-002 输出本来就在 results/ 里，
    # 必须继续允许运行，否则会破坏 README / USER_GUIDE 里已有的教程命令。
    user_gave_new_paths = (args.input is not None) or (args.out_dir is not None)

    print("========== VisionMotion M3.3 视频逐帧追踪 ==========")
    print("输入视频：%s" % input_path)
    print("输出目录：%s" % out_dir)
    print("输出 CSV：%s" % csv_path)
    print("输出叠加视频：%s" % overlay_path)
    if not user_gave_new_paths:
        print("运行方式：无参数（保持旧行为：固定 EXP-002 视频，输出到 results/）")
    print("")

    # 1. 输入视频必须存在（保留原来清晰的错误提示，不让 CLI 吞掉）
    if not input_path.is_file():
        print("错误：输入视频不存在：%s" % input_path)
        print("提示：--input 可用绝对路径，或写相对项目根目录的路径（例如 data\\raw\\my_video.mp4）。")
        return 1

    # 2. 覆盖保护：只在用户显式换了输入 / 输出位置时启用。
    #    目的：换视频时不会静默覆盖上一次的结果；旧的无参数运行不受影响。
    if user_gave_new_paths and not args.overwrite:
        existing_files = [item for item in (csv_path, overlay_path) if item.exists()]
        if existing_files:
            print("错误：目标输出文件已存在，已停止（不覆盖已有结果）：")
            for item in existing_files:
                print("  %s" % item)
            print("处理方式（二选一）：")
            print("  1) 换一个输出目录：--out-dir <DIR>")
            print("  2) 确认要覆盖已有结果：加 --overwrite")
            print("说明：--overwrite 只决定是否覆盖输出文件，与 SHA / QC / 冻结参数无关。")
            return 2

    # 3. 输出目录：不存在则创建（track_video() 内部也会创建，这里显式做一次）
    out_dir.mkdir(parents=True, exist_ok=True)

    # 4. 启动逐帧追踪（CSV 与叠加可视化来自同一次逐帧处理）
    summary = track_video(input_path, csv_path, overlay_path)
    if summary is None:
        print("M3.3 运行失败：视频无法处理")
        return 1

    # 5. 打印统计信息
    print_statistics(summary)

    # 6. CSV 数据完整性自检
    checks, passed = check_csv_data(
        summary["csv_path"],
        summary["processed_frames"],
        summary["width"],
        summary["height"],
        summary["fps"],
    )
    print_check_results(checks, passed)

    # 7. 原始视频完整性（只读对比，程序不会写入 data/raw/）
    print("")
    print("========== 原始视频完整性 ==========")
    print("运行前 SHA-256：%s" % summary["sha256_before"].upper())
    print("运行后 SHA-256：%s" % summary["sha256_after"].upper())
    print("原始视频是否被改动：%s"
          % ("否" if summary["sha256_before"] == summary["sha256_after"] else "是"))

    # 8. 最终结果
    print("")
    print("========== M3.3 最终结果 ==========")
    print("CSV 文件：%s" % summary["csv_path"])
    print("CSV 行数（不含表头）：%d" % summary["processed_frames"])
    if summary["overlay_ok"]:
        print("叠加视频：%s" % summary["overlay_path"])
        print("叠加视频是否成功：是")
    else:
        print("叠加视频是否成功：否（VideoWriter 不可用，已回退保存 %d 张代表性 PNG）"
              % len(summary["fallback_pngs"]))
        for png_path in summary["fallback_pngs"]:
            print("  %s" % png_path)
    print("是否中断：%s" % ("是" if summary["interrupted"] else "否"))
    integrity = summary["track_integrity"]
    if integrity == "complete":
        print("轨迹完整性：complete")
    elif integrity == "suspect":
        print("轨迹完整性：suspect（完整性存疑：处理帧数未达到文件声明值，且声明末帧无法再次解码）")
    elif integrity == "unverified":
        print("轨迹完整性：unverified（完整性未验证：证据不足或互相矛盾）")
    else:
        print("轨迹完整性：not_evaluated（用户主动中断，未评估）")
    print("")

    # 9. 结果判定（退出码）：优先级 QC 未通过 > 用户主动中断 > 完整性未确认 > 全程零检出 > 成功
    #    上面的统计 / 原始视频 SHA / QC 明细 / 最终结果都已经打印完毕，
    #    退出码只是追加的机器可读信号，不替代任何终端输出。
    print("========== 结果判定（退出码） ==========")
    if not passed:
        print("退出码：1（CSV 数据完整性自检未通过：处理结果不合格）")
        print("")
        return 1
    if summary["interrupted"]:
        print("退出码：4（用户主动中断逐帧视频处理：不是程序崩溃；"
              "CSV / overlay 通常只覆盖截至中断时已处理的帧，不应直接当作完整视频结果）")
        print("")
        return 4
    if summary["track_integrity"] != "complete":
        print("退出码：5（轨迹完整性未确认：不是程序崩溃，不是输入错误，"
              "不是 QC 失败，也不是用户中断；本次输出不能可靠地当作已确认完整的视频轨迹）")
        print("")
        return 5
    if summary["detected_frames"] == 0:
        print("退出码：3（流程完成，但全程没有检出到任何目标）")
        print("")
        return 3
    print("退出码：0（流程成功，且至少检出过一次目标）")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

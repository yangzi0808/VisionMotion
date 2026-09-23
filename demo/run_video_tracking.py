"""
VisionMotion —— M3.3 演示脚本

功能：读取真实视频，逐帧调用现有检测器，生成时序坐标 CSV 与叠加可视化。

本脚本只负责：
    1. 指定输入视频路径
    2. 指定输出路径（CSV 与叠加视频）
    3. 启动 src/video_tracker.py 里的追踪流程
    4. 打印最终结果

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_video_tracking.py
"""

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
# 输入输出路径
# ============================================================

VIDEO_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-002-VIDEO-001.mp4"
RESULT_DIR = PROJECT_ROOT / "results"
CSV_PATH = RESULT_DIR / "EXP-002-VIDEO-001_track.csv"
OVERLAY_PATH = RESULT_DIR / "EXP-002-VIDEO-001_overlay.mp4"


def main():
    # 1. 启动逐帧追踪（CSV 与叠加可视化来自同一次逐帧处理）
    summary = track_video(VIDEO_PATH, CSV_PATH, OVERLAY_PATH)
    if summary is None:
        print("M3.3 运行失败：视频无法处理")
        return

    # 2. 打印统计信息
    print_statistics(summary)

    # 3. CSV 数据完整性自检
    checks, passed = check_csv_data(
        summary["csv_path"],
        summary["processed_frames"],
        summary["width"],
        summary["height"],
    )
    print_check_results(checks, passed)

    # 4. 原始视频完整性（只读对比，程序不会写入 data/raw/）
    print("")
    print("========== 原始视频完整性 ==========")
    print("运行前 SHA-256：%s" % summary["sha256_before"].upper())
    print("运行后 SHA-256：%s" % summary["sha256_after"].upper())
    print("原始视频是否被改动：%s"
          % ("否" if summary["sha256_before"] == summary["sha256_after"] else "是"))

    # 5. 最终结果
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
    print("")


if __name__ == "__main__":
    main()

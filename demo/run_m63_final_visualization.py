"""
VisionMotion —— M6.3-3B 最终成果可视化演示脚本

功能：按 M6.3-3A 已封板的设计稿，生成三张最终 PNG 并打印自动自检结果。

产物（只新增，不修改任何既有文件）：
    results/EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png
    results/EXP-EXT-LAB67-V1_fig_B_frequency_comparison.png
    results/EXP-EXT-LAB67-V1_fig_C_pipeline.png

本脚本只负责：
    1. 指定输入 CSV 与输出目录
    2. 调 src/m63_final_visualization.py 的 main()
    3. 返回自检是否通过（退出码 0 / 1）

本脚本不做：
    不读取原始外部视频；不重新计算周期 / 频率 / 极值 / FFT；不修改任何封板文件。

数据性质：External public educational dataset（ComPADRE / OSP Lab67 Video 1，51.5 g）。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m63_final_visualization.py
"""

import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.m63_final_visualization import main  # noqa: E402

# ============================================================
# 输入输出路径（本轮唯一允许新增的产物目录）
# ============================================================

CSV_PATH = PROJECT_ROOT / "results" / "EXP-EXT-LAB67-V1_trajectory.csv"
OUTPUT_DIR = PROJECT_ROOT / "results"


def run():
    """
    运行最终可视化生成流程。
    """
    print("")
    print("========== M6.3-3B 最终成果可视化 ==========")
    print("输入（封板轨迹）：%s" % CSV_PATH)
    print("输出目录：%s" % OUTPUT_DIR)
    print("说明：本脚本不读取原始外部视频，不重新计算周期 / 频率 / 极值 / FFT。")

    if not CSV_PATH.exists():
        print("")
        print("运行失败：找不到封板轨迹 CSV %s" % CSV_PATH)
        return 1

    return main(csv_path=CSV_PATH, out_dir=OUTPUT_DIR)


if __name__ == "__main__":
    sys.exit(run())

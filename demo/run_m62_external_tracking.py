"""
VisionMotion —— M6.2-2C 外部公开视频正式轨迹演示脚本

功能：对 ComPADRE / OSP（ID=16081）公开的 Lab 67 Video 1（51.5 g）外部视频，
      运行 M6.2-2B 冻结的视觉规则，生成正式自由振荡轨迹 CSV，并打印全部自检结果。

正式数据链：

    外部原始视频（SHA-256 校验）
    -> src/external_oscillation_tracker.py（冻结检测，唯一实现来源）
    -> results/EXP-EXT-LAB67-V1_trajectory.csv
    -> 读回 CSV 做独立质量检查

本脚本只负责：
    1. 指定输入视频路径与输出 CSV 路径
    2. 写出 M6.2-2B 冻结参数（START_FRAME / END_FRAME 等）
    3. 调 run_external_tracking()（校验 SHA -> 逐帧检测 -> 写 CSV -> 自检 -> 打印）

本脚本不生成 overlay 视频、不生成 PNG、不修改原始视频。

数据性质：External / Publicly available dataset（不是本项目自采实验）。
许可：CC BY-NC-SA 3.0；作者 / 权益持有人：Kathleen Koenig（ComPADRE / OSP）。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m62_external_tracking.py
"""

import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.external_oscillation_tracker import (  # noqa: E402
    END_FRAME,
    EXTERNAL_VIDEO_SHA256,
    START_FRAME,
    run_external_tracking,
)

# ============================================================
# 输入输出路径（本轮唯一允许的正式产物）
# ============================================================

# 外部候选视频（本轮不移动、不重命名、不修改原文件）。
# 正式命名建议（后续阶段再执行）：data/external/EXT-HM-001-Video01.mp4
VIDEO_PATH = (
    PROJECT_ROOT / "_external" / "_candidates" / "candidate_comPADRE_Lab67_01_Video1_51p5g.mp4"
)

# 正式轨迹 CSV（只包含自由振荡帧 76–235）
CSV_PATH = PROJECT_ROOT / "results" / "EXP-EXT-LAB67-V1_trajectory.csv"

# 冻结帧区间（来自 src/external_oscillation_tracker.py，此处只做显式声明便于核对）
FORMAL_START_FRAME = START_FRAME  # 76
FORMAL_END_FRAME = END_FRAME      # 235

# 冻结视频身份（SHA-256 不一致时立即停止）
EXPECTED_VIDEO_SHA256 = EXTERNAL_VIDEO_SHA256


def main():
    """
    运行 M6.2-2C 正式流程，并根据自检结果返回退出码。
    """
    print("")
    print("========== M6.2-2C 正式外部视频轨迹实现 ==========")
    print("外部数据：ComPADRE / OSP ID=16081 — Lab 67 Video 1（51.5 g）")
    print("性质：External / Publicly available dataset（非自采）")
    print("输入视频：%s" % VIDEO_PATH)
    print("输出 CSV：%s" % CSV_PATH)
    print("正式帧范围：frame %d–%d" % (FORMAL_START_FRAME, FORMAL_END_FRAME))
    print("期望视频 SHA-256：%s" % EXPECTED_VIDEO_SHA256)
    print("说明：本脚本不生成 overlay 视频、不生成 PNG、不修改原始视频。")

    if not VIDEO_PATH.exists():
        print("")
        print("运行失败：找不到外部候选视频 %s" % VIDEO_PATH)
        return 1

    try:
        _, _, _, passed = run_external_tracking(
            VIDEO_PATH,
            CSV_PATH,
            start_frame=FORMAL_START_FRAME,
            end_frame=FORMAL_END_FRAME,
            expected_sha256=EXPECTED_VIDEO_SHA256,
        )
    except Exception as error:  # 校验失败 / 解码失败等：打印原因并停止
        print("")
        print("运行失败：%s" % error)
        return 1

    print("")
    print("M6.2-2C 运行结束：%s" % ("通过自检（未进入 M6.3）" if passed else "自检未通过，请人工检查"))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())

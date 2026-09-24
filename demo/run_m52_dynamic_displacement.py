"""
VisionMotion —— M5.2-2B EXP-004 动态位移演示脚本

功能：对正式实验 EXP-004-DYNAMIC-001 跑完整的动态位移数据链，
      并打印统计与全部自检结果。

正式数据链：

    原始视频
    -> M3 track_video()      （检测唯一来源）
    -> *_track.csv
    -> EXP-004 valid gate
    -> project_point()
    -> s0
    -> ds_px / ds_mm
    -> *_ds.csv
    -> 原始 x_px 转向点统计（最小行程 20 px）

本脚本只负责：
    1. 定义 EXP-004 的输入路径与三个输出路径
    2. 检查原始视频存在、并核对运行前 SHA-256
    3. 调 track_video()（原始视频 -> track CSV + overlay 叠加视频）
    4. 调 dynamic_displacement 模块（track CSV -> ds CSV + 统计 + 自检）
    5. 打印最终统计与自检结果

算法（检测、gate、投影、s0、位移、转向点）全部在 src/ 里，本脚本不重复实现。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m52_dynamic_displacement.py
"""

import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.dynamic_displacement import (  # noqa: E402
    AREA_MAX_PX_004,
    AREA_MIN_PX_004,
    CALIB_P1_PX,
    CALIB_P2_PX,
    CALIB_REAL_DISTANCE_MM,
    EXPECTED_TRACK_ROWS,
    EXPECTED_VIDEO_SHA256,
    EXPERIMENT_NAME,
    MIN_S0_VALID_FRAMES,
    MIN_TURN_TRAVEL_PX,
    MM_PER_PX_004,
    PX_PER_MM_004,
    S0_WINDOW_S,
    U_004,
    Y_MAX_PX_004,
    Y_MIN_PX_004,
    print_summary,
    run_experiment,
)
from src.video_tracker import track_video  # noqa: E402

# ============================================================
# 1 ~ 4. EXP-004 的输入与输出路径（本阶段唯一允许的正式产物）
# ============================================================

VIDEO_PATH = PROJECT_ROOT / "data" / "raw" / ("%s.mp4" % EXPERIMENT_NAME)
TRACK_CSV_PATH = PROJECT_ROOT / "results" / ("%s_track.csv" % EXPERIMENT_NAME)
DS_CSV_PATH = PROJECT_ROOT / "results" / ("%s_ds.csv" % EXPERIMENT_NAME)
OVERLAY_PATH = PROJECT_ROOT / "results" / ("%s_overlay.mp4" % EXPERIMENT_NAME)


def print_frozen_constants():
    """
    打印本次实验实际使用的全部冻结常量（只打印，不修改）。
    """
    print("")
    print("========== EXP-004 冻结常量（本次实际使用，未重新标定） ==========")
    print(
        "标定：P1(10 cm)=%s  P2(20 cm)=%s  L_real=%.1f mm"
        % (CALIB_P1_PX, CALIB_P2_PX, CALIB_REAL_DISTANCE_MM)
    )
    print("PX_PER_MM_004 = %.6f" % PX_PER_MM_004)
    print("MM_PER_PX_004 = %.6f" % MM_PER_PX_004)
    print("U_004 = (%.6f, %.6f)（单位方向，方向 10 cm -> 20 cm）" % U_004)
    print(
        "valid gate：detected=True 且 %.0f <= area_px <= %.0f 且 %.0f <= y_px <= %.0f"
        % (AREA_MIN_PX_004, AREA_MAX_PX_004, Y_MIN_PX_004, Y_MAX_PX_004)
    )
    print(
        "s0 规则：只使用 time_s <= %.1f s 的帧，窗口内至少 %d 帧 valid=True"
        % (S0_WINDOW_S, MIN_S0_VALID_FRAMES)
    )
    print(
        "运动统计：原始 x_px 极值 + 最小运动行程 %.1f px（不平滑、不滤波、不插值、不预测）"
        % MIN_TURN_TRAVEL_PX
    )
    print("原始视频 SHA-256（运行前已记录）：%s" % EXPECTED_VIDEO_SHA256)
    print("自检基准：track CSV 数据行数 = %d" % EXPECTED_TRACK_ROWS)


def print_final_checks(report, track_summary):
    """
    打印本轮自检清单的最后两项（常量自检与原始视频 SHA-256），
    并把 M3 track_video() 的帧数 / 检查结果汇总进来。
    """
    print("")
    print("========== 运行完整性自检（命令行整体核对） ==========")

    print(
        "[%s] 冻结常量自检通过（P1/P2/100mm 复算 PX_PER_MM_004 与 U_004，只读，不重新标定）"
        % ("通过" if report["constant_passed"] else "未通过")
    )

    sha_before = track_summary["sha256_before"]
    sha_after = track_summary["sha256_after"]
    # M3 的 track_video() 在运行前后各算一次 SHA-256，这里只做对比：
    # 运行前 == 冻结记录，运行后 == 运行前（原始视频未被修改）
    # 注意：只比较十六进制大小写不同（M3 返回小写，冻结记录是大写），不是数值差异
    sha_ok = (
        sha_before.upper() == EXPECTED_VIDEO_SHA256.upper()
        and sha_after.upper() == EXPECTED_VIDEO_SHA256.upper()
        and sha_before.upper() == sha_after.upper()
    )
    print("  运行前 SHA-256：%s" % sha_before)
    print("  运行后 SHA-256：%s" % sha_after)
    print(
        "[%s] 原始视频 SHA-256 运行前后一致，且与冻结记录一致（原始视频未被修改）"
        % ("通过" if sha_ok else "未通过")
    )

    frames_ok = track_summary["processed_frames"] == EXPECTED_TRACK_ROWS
    print(
        "[%s] M3 实际处理帧数 = %d（冻结自检值 %d）"
        % ("通过" if frames_ok else "未通过", track_summary["processed_frames"], EXPECTED_TRACK_ROWS)
    )

    rows_ok = report["track_frame_count"] == EXPECTED_TRACK_ROWS
    print(
        "[%s] track CSV 数据行数 = %d（冻结自检值 %d）"
        % ("通过" if rows_ok else "未通过", report["track_frame_count"], EXPECTED_TRACK_ROWS)
    )

    if report["ds_written"]:
        print(
            "[%s] ds CSV 自动自检（行数 / frame / valid gate / 空字段 / 小数位 / s0 / ds 公式 / 成功率）"
            % ("通过" if report["passed"] else "未通过")
        )
    else:
        print("[注意] ds CSV 未生成（s0 窗口有效帧不足，按冻结规则不写），本轮不做 ds 自检")

    print("=====================================================")


def main():
    print("========== VisionMotion M5.2-2B EXP-004 动态位移实验 ==========")
    print("正式数据链：原始视频 -> M3 track_video() -> *_track.csv -> EXP-004 valid gate")
    print("            -> project_point() -> s0 -> ds_px / ds_mm -> *_ds.csv")
    print("            -> 原始 x_px 转向点统计（最小运动行程 20 px）")
    print("实验编号：%s" % EXPERIMENT_NAME)
    print("输入视频：%s" % VIDEO_PATH)
    print("track CSV：%s" % TRACK_CSV_PATH)
    print("ds CSV：%s" % DS_CSV_PATH)
    print("overlay MP4：%s" % OVERLAY_PATH)

    # 0. 冻结常量打印（只打印，不做任何重新标定）
    print_frozen_constants()

    # 1. 检查原始视频存在
    if not VIDEO_PATH.is_file():
        print("")
        print("错误：原始视频不存在：%s" % VIDEO_PATH)
        print("处理方式：停止运行（不生成任何结果文件）")
        return

    # 2. M3 负责检测与记录：原始视频 -> track CSV + 叠加视频
    print("")
    print("========== 第 1 步：M3 逐帧追踪（原始视频 -> track CSV + overlay） ==========")
    track_summary = track_video(VIDEO_PATH, TRACK_CSV_PATH, OVERLAY_PATH)
    if track_summary is None:
        print("错误：视频无法处理：%s" % VIDEO_PATH)
        print("处理方式：停止运行（不生成 ds CSV）")
        return

    # 3. dynamic_displacement 模块负责 valid gate / 投影 / s0 / ds / 转向点：track CSV -> ds CSV
    print("")
    print("========== 第 2 步：EXP-004 动态位移（track CSV -> ds CSV + 统计 + 自检） ==========")
    report = run_experiment(TRACK_CSV_PATH, DS_CSV_PATH, EXPERIMENT_NAME)

    # 4. 把视频与 overlay 信息挂到报告上（只读，不参与任何计算）
    report["video_path"] = VIDEO_PATH
    report["overlay_path"] = OVERLAY_PATH
    report["track_frames_processed"] = track_summary["processed_frames"]
    report["sha256_before"] = track_summary["sha256_before"]
    report["sha256_after"] = track_summary["sha256_after"]

    # 5. 打印最终统计与自检结果
    print_summary(report)
    print_final_checks(report, track_summary)


if __name__ == "__main__":
    main()

"""
VisionMotion —— M4.3-2B 演示脚本

功能：对三个静态实验视频跑完整的 M4.3-2B 数据链，并打印统计与自检结果。

正式数据链：

    原始视频
    -> M3 track_video()      （检测唯一来源）
    -> *_track.csv
    -> valid gate
    -> project_point()
    -> s0
    -> ds_px / ds_mm
    -> *_ds.csv

本脚本只负责：
    1. 列出三个实验
    2. 检查原始视频存在
    3. 调 track_video()
    4. 调 displacement 模块生成 ds CSV
    5. 打印每个视频统计
    6. 打印最后三视频汇总

算法（检测、投影、位移）全部在 src/ 里，本脚本不重复实现。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_m43_displacement.py
"""

import sys
from pathlib import Path

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.displacement import (  # noqa: E402
    AREA_MAX_PX,
    AREA_MIN_PX,
    MIN_S0_VALID_FRAMES,
    MM_PER_PX,
    PX_PER_MM,
    S0_WINDOW_S,
    U,
    Y_MAX_PX,
    Y_MIN_PX,
    check_calibration_constants,
    print_check_results,
    print_summary,
    run_experiment,
)
from src.video_tracker import track_video  # noqa: E402

# ============================================================
# 三个静态实验（本阶段只处理这三个视频）
# ============================================================

DATA_DIR = PROJECT_ROOT / "data" / "raw"
RESULT_DIR = PROJECT_ROOT / "results"

EXPERIMENT_NAMES = [
    "EXP-003-STATIC-001",
    "EXP-003-STATIC-002",
    "EXP-003-STATIC-003",
]


def run_one_experiment(video_name):
    """
    处理一个视频：原始视频 -> track CSV -> ds CSV。

    原始视频不存在或无法处理时返回 None。
    """
    video_path = DATA_DIR / ("%s.mp4" % video_name)
    track_csv_path = RESULT_DIR / ("%s_track.csv" % video_name)
    ds_csv_path = RESULT_DIR / ("%s_ds.csv" % video_name)
    overlay_path = RESULT_DIR / ("%s_overlay.mp4" % video_name)

    # 2. 检查原始视频存在
    if not video_path.is_file():
        print("错误：原始视频不存在：%s" % video_path)
        return None

    # 3. M3 负责检测与记录：原始视频 -> track CSV + 叠加视频
    track_summary = track_video(video_path, track_csv_path, overlay_path)
    if track_summary is None:
        print("错误：视频无法处理：%s" % video_path)
        return None

    # 4. displacement 模块负责 valid gate / 投影 / s0 / ds：track CSV -> ds CSV
    report = run_experiment(track_csv_path, ds_csv_path, video_name)

    # 原始视频完整性：M3 在运行前后各算一次 SHA-256，这里只做对比，不重复计算
    report["video_path"] = video_path
    report["overlay_path"] = overlay_path
    report["track_frames_processed"] = track_summary["processed_frames"]
    report["sha256_before"] = track_summary["sha256_before"]
    report["sha256_after"] = track_summary["sha256_after"]
    report["video_untouched"] = (
        track_summary["sha256_before"] == track_summary["sha256_after"]
    )

    return report


def print_final_summary(reports):
    """
    6. 打印三个视频的汇总表，并确认三个视频共用同一套常量与规则。
    """
    print("")
    print("========== 三视频汇总 ==========")
    if not reports:
        print("没有任何视频被成功处理。")
        return

    print(
        "%-20s %8s %13s %13s %12s %s"
        % ("视频", "帧数", "detected率", "valid率", "s0(px)", "ds_mm 范围")
    )
    for report in reports:
        summary = report["summary"]
        s0 = report["s0_report"]["s0"]
        s0_text = "无" if s0 is None else "%.3f" % s0
        if summary["ds_min_mm"] is None:
            ds_text = "无"
        else:
            ds_text = "%.4f ~ %.4f（跨度 %.4f）" % (
                summary["ds_min_mm"],
                summary["ds_max_mm"],
                summary["ds_span_mm"],
            )
        print(
            "%-20s %8d %12.4f%% %12.4f%% %12s %s"
            % (
                report["video_name"],
                summary["frame_count"],
                summary["detected_rate"] * 100.0,
                summary["valid_rate"] * 100.0,
                s0_text,
                ds_text,
            )
        )

    print("")
    print("三个视频共用同一套冻结标定与规则：")
    print("  PX_PER_MM = %.6f" % PX_PER_MM)
    print("  MM_PER_PX = %.6f" % MM_PER_PX)
    print("  u = (%.6f, %.6f)（单位方向，方向 10 cm -> 16 cm）" % U)
    print(
        "  valid gate：detected=True 且 %.0f <= area_px <= %.0f 且 %.0f <= y_px <= %.0f"
        % (AREA_MIN_PX, AREA_MAX_PX, Y_MIN_PX, Y_MAX_PX)
    )
    print(
        "  s0 规则：只使用 time_s <= %.1f s 的帧，窗口内至少 %d 帧 valid=True"
        % (S0_WINDOW_S, MIN_S0_VALID_FRAMES)
    )

    print("")
    print("========== 三视频整体自检 ==========")

    # 自检：三个实验使用完全相同的 k / u / gate / s0 窗口规则
    rule_snapshots = [report["rules"] for report in reports]
    rules_same = all(snapshot == rule_snapshots[0] for snapshot in rule_snapshots)
    print(
        "[%s] 三个实验使用的 k / u / gate / s0 窗口规则完全相同"
        % ("通过" if rules_same else "未通过")
    )

    # 自检：data/raw/ 原始视频在运行前后完全一致
    untouched = all(report["video_untouched"] for report in reports)
    track_rows_match = all(
        report["track_frame_count"] == report["track_frames_processed"]
        for report in reports
    )
    for report in reports:
        print("  %s 运行前 SHA-256：%s" % (report["video_name"], report["sha256_before"]))
        print("  %s 运行后 SHA-256：%s" % (report["video_name"], report["sha256_after"]))
        print(
            "  %s 原始视频是否被改动：%s"
            % (report["video_name"], "否" if report["video_untouched"] else "是")
        )
    print(
        "[%s] data/raw/ 原始视频在运行前后完全一致（本程序未修改原始数据）"
        % ("通过" if untouched else "未通过")
    )
    print(
        "[%s] 每个视频的 track CSV 行数 == M3 实际解码帧数（未删行）"
        % ("通过" if track_rows_match else "未通过")
    )

    # 每个视频的 ds CSV 自检结论
    for report in reports:
        if report["ds_written"]:
            print(
                "[%s] %s 的 ds CSV 自动自检（行数 / frame / valid gate / 空字段 / 小数位 / 成功率）"
                % ("通过" if report["passed"] else "未通过", report["video_name"])
            )
        else:
            print(
                "[注意] %s 未生成 ds CSV（s0 窗口有效帧不足，按冻结规则不写）"
                % report["video_name"]
            )

    print("===================================")


def main():
    print("========== VisionMotion M4.3-2B 位移实验 ==========")
    print("正式数据链：原始视频 -> M3 track_video() -> *_track.csv -> valid gate")
    print("            -> project_point() -> s0 -> ds_px / ds_mm -> *_ds.csv")
    print("待处理实验：%s" % "、".join(EXPERIMENT_NAMES))

    # 0. 冻结常量自检（只读，不做任何重新标定）
    print("")
    print("========== 冻结常量自检（不重新标定） ==========")
    checks, passed = check_calibration_constants()
    print_check_results(checks, passed)
    if not passed:
        print("冻结常量自检未通过，停止运行（不生成任何 ds CSV）")
        return

    reports = []
    for video_name in EXPERIMENT_NAMES:
        print("")
        print("############################################################")
        print("# 实验：%s" % video_name)
        print("############################################################")

        report = run_one_experiment(video_name)
        if report is None:
            continue

        reports.append(report)

        # 5. 打印每个视频的统计信息（含 s0 报告与 ds CSV 自检结果）
        print_summary(report)

    # 6. 打印三视频汇总
    print_final_summary(reports)


if __name__ == "__main__":
    main()

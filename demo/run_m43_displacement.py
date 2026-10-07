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

覆盖行为（默认允许重算，只做显式提示）：
    输出目录固定为 results/（与仓库内冻结结果同目录）。目标文件已存在时，
    本脚本会在真正写盘之前打印 [警告] 并继续执行——不拒绝覆盖、不做交互、
    不新增命令行参数。运行前若需要保护本地冻结结果，请先确认 git status。

退出码（供脚本 / 自动化判断；终端输出仍保留全部统计与自检明细）：
    0 = 本次入口要求执行的三个实验全部成功完成，且每个预期生成的 _ds.csv 均已落盘
    1 = 存在阻断性失败，例如：
          输入视频不存在 / 视频无法处理 /
          冻结常量自检未通过 /
          上游轨迹完整性 not_evaluated（用户主动中断）导致该实验被跳过 /
          预期生成的 _ds.csv 未落盘
    说明：按冻结 s0 规则"窗口内有效帧不足因此不写 _ds.csv"属于预期结果
         （终端打印为 [注意] ... 按冻结规则不写），不计入阻断性失败。
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


def warn_if_outputs_exist(targets):
    """
    在真正写盘之前，明确提示哪些目标文件已存在、将被重新写入。

    M4 是仓库内冻结实验的"重放入口"，默认允许重算；本函数只把"隐式覆盖"
    变成"显式提示"，不拒绝覆盖、不做交互（无 input()）、不影响实验流程。
    返回本次已存在的目标路径列表（没有则返回空列表，且不打印任何内容）。
    """
    existing = [Path(target) for target in targets if Path(target).exists()]
    if not existing:
        return []

    print("")
    print("[警告] 输出文件已存在，将重新写入冻结结果：")
    for path in existing:
        print("  %s" % path)
    print("")
    return existing


def run_one_experiment(video_name):
    """
    处理一个视频：原始视频 -> track CSV -> ds CSV。

    原始视频不存在或无法处理时返回 None。
    上游轨迹完整性未评估（用户主动中断）时返回跳过标记字典（含 "skipped": True），
    不调用 run_experiment()、不生成 _ds.csv。
    """
    video_path = DATA_DIR / ("%s.mp4" % video_name)
    track_csv_path = RESULT_DIR / ("%s_track.csv" % video_name)
    ds_csv_path = RESULT_DIR / ("%s_ds.csv" % video_name)
    overlay_path = RESULT_DIR / ("%s_overlay.mp4" % video_name)

    # 2. 检查原始视频存在
    if not video_path.is_file():
        print("错误：原始视频不存在：%s" % video_path)
        return None

    # 2.5 覆盖提示（只提示，不拒绝、不交互）：在真正写盘之前让用户知道
    #     results/ 下这些冻结结果会被重新写入。
    warn_if_outputs_exist((track_csv_path, overlay_path, ds_csv_path))

    # 3. M3 负责检测与记录：原始视频 -> track CSV + 叠加视频
    track_summary = track_video(video_path, track_csv_path, overlay_path)
    if track_summary is None:
        print("错误：视频无法处理：%s" % video_path)
        return None

    # 3.5 上游轨迹完整性：M3 的 track_video() 已在同一进程内给出结论，直接使用，
    #     不从 _track.csv 反推（CSV 自洽不等于视频完整）。
    integrity = track_summary["track_integrity"]
    if integrity == "not_evaluated":
        print("")
        print("警告：上游轨迹完整性未评估（用户主动中断），"
              "本次跳过位移计算，不生成 _ds.csv：%s" % video_name)
        return {"video_name": video_name, "track_integrity": integrity, "skipped": True}
    if integrity == "suspect":
        print("")
        print("警告：上游轨迹完整性存疑，将继续计算位移；使用结果前请人工核对轨迹完整性。")
    elif integrity == "unverified":
        print("")
        print("警告：上游轨迹完整性未验证，将继续计算位移；使用结果前请人工核对。")

    # 4. displacement 模块负责 valid gate / 投影 / s0 / ds：track CSV -> ds CSV
    report = run_experiment(track_csv_path, ds_csv_path, video_name)

    # 原始视频完整性：M3 在运行前后各算一次 SHA-256，这里只做对比，不重复计算
    report["video_path"] = video_path
    report["overlay_path"] = overlay_path
    report["track_frames_processed"] = track_summary["processed_frames"]
    report["track_integrity"] = integrity
    report["sha256_before"] = track_summary["sha256_before"]
    report["sha256_after"] = track_summary["sha256_after"]
    report["video_untouched"] = (
        track_summary["sha256_before"] == track_summary["sha256_after"]
    )

    return report


def ds_csv_not_landed(report):
    """
    判断"程序认为已写出、磁盘上却找不到"的 ds CSV（只读的防御性检查）。

    注意：ds CSV 未生成本身不一定算失败——当 s0 窗口内有效帧不足时，
    冻结规则要求不写 ds CSV（print_final_summary 会打印为 [注意] ... 按冻结规则不写），
    这属于预期结果，不计入阻断性失败。
    真正算阻断性失败的是：report 认为已写出（ds_written=True），但目标文件实际不存在。
    """
    if not report["ds_written"]:
        return False
    return not Path(report["ds_csv_path"]).is_file()


def print_final_summary(reports, skipped):
    """
    6. 打印三个视频的汇总表，并确认三个视频共用同一套常量与规则。

    reports     —— 正常完成位移计算的视频报告
    skipped     —— 因上游轨迹完整性未评估而被跳过的视频（未生成 ds CSV）
    """
    print("")
    print("========== 三视频汇总 ==========")

    if skipped:
        print("")
        print("以下视频因上游轨迹完整性未评估而被跳过（未调用位移计算，未生成 ds CSV）：")
        for entry in skipped:
            print(
                "  %-20s track_integrity=%-14s 跳过=是"
                % (entry["video_name"], entry["track_integrity"])
            )

    if not reports:
        print("没有任何视频被成功处理。")
        return

    print(
        "%-20s %8s %13s %13s %12s %-11s %s"
        % ("视频", "帧数", "detected率", "valid率", "s0(px)", "完整性", "ds_mm 范围")
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
            "%-20s %8d %12.4f%% %12.4f%% %12s %-11s %s"
            % (
                report["video_name"],
                summary["frame_count"],
                summary["detected_rate"] * 100.0,
                summary["valid_rate"] * 100.0,
                s0_text,
                report["track_integrity"],
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
        print("")
        print("========== 结果判定（退出码） ==========")
        print("退出码：1（冻结常量自检未通过）")
        print("")
        return 1

    reports = []
    skipped = []
    blocked = []   # 本次运行判定为"阻断性失败"的实验名（只用于最终退出码）
    for video_name in EXPERIMENT_NAMES:
        print("")
        print("############################################################")
        print("# 实验：%s" % video_name)
        print("############################################################")

        report = run_one_experiment(video_name)
        if report is None:
            # 输入视频不存在 / 视频无法处理：阻断性失败
            blocked.append(video_name)
            continue
        if report.get("skipped"):
            # 上游轨迹完整性 not_evaluated（用户主动中断）：按 Phase 5-1 语义跳过，
            # 属于"明确没有完成完整性评价"，同样计为阻断性失败
            skipped.append(report)
            blocked.append(video_name)
            continue

        reports.append(report)

        # 5. 打印每个视频的统计信息（含 s0 报告与 ds CSV 自检结果）
        print_summary(report)

        # 5.5 预期生成的 ds CSV 必须真的落盘（防御性检查；s0 规则判定不写的情形不算失败）
        if ds_csv_not_landed(report):
            print("错误：ds CSV 未按预期落盘：%s" % report["ds_csv_path"])
            blocked.append(video_name)

    # 6. 打印三视频汇总（含被跳过的视频）
    print_final_summary(reports, skipped)

    # 7. 结果判定（退出码）：只追加机器可读信号，不替代上面任何终端输出。
    #    只要有一个本次计划执行的实验失败 / 被阻断 / 预期输出未落盘，整体就判 1，
    #    不因为其余实验成功而降级为 0。
    print("")
    print("========== 结果判定（退出码） ==========")
    if blocked:
        print("退出码：1（存在阻断性失败：%s）" % "、".join(blocked))
        print("")
        return 1
    print("退出码：0（全部预期实验成功完成，预期生成的 ds CSV 均已落盘）")
    print("")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

覆盖行为（默认允许重算，只做显式提示）：
    输出目录固定为 results/（与仓库内冻结结果同目录）。目标文件已存在时，
    本脚本会在真正写盘之前打印 [警告] 并继续执行——不拒绝覆盖、不做交互、
    不新增命令行参数。运行前若需要保护本地冻结结果，请先确认 git status。

退出码（供脚本 / 自动化判断；终端输出仍保留全部统计与自检明细）：
    0 = EXP-004 实验成功完成，且预期生成的 _ds.csv 已落盘
    1 = 实验失败 / 被阻断 / 预期生成的 _ds.csv 未生成，例如：
          输入视频不存在 / 视频无法处理 /
          上游轨迹完整性 not_evaluated（用户主动中断）导致跳过位移计算 /
          冻结常量自检未通过导致 ds CSV 未生成 /
          预期生成的 _ds.csv 未落盘
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


def warn_if_outputs_exist(targets):
    """
    在真正写盘之前，明确提示哪些目标文件已存在、将被重新写入。

    M5 是仓库内冻结实验的"重放入口"，默认允许重算；本函数只把"隐式覆盖"
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

    print("  上游轨迹完整性（来自 M3 track_video()）：%s" % report["track_integrity"])

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


def final_exit_code(report):
    """
    根据 EXP-004 正式实验的报告判定机器可读退出码。

    返回 (exit_code, 说明文字)。

    规则（本轮最小契约，不新增业务规则）：
        0 = 实验成功完成，且预期生成的 _ds.csv 已落盘
        1 = 实验失败 / 被阻断 / 预期生成的 _ds.csv 未生成

    说明：EXP-004 的 _ds.csv 是本阶段唯一允许的正式产物，
    因此"未生成"在这里按退出码契约判为 1（与 M4 的多实验情形不同——
    M4 存在"冻结 s0 规则判定不写"的预期情形）。
    """
    if not report["ds_written"]:
        return 1, "预期生成的 _ds.csv 未生成（冻结常量自检未通过或 s0 窗口有效帧不足）"
    if not Path(report["ds_csv_path"]).is_file():
        return 1, "ds CSV 未按预期落盘：%s" % report["ds_csv_path"]
    return 0, "实验成功完成，ds CSV 已落盘"


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
        print("退出码：1（输入视频不存在，本次未执行任何实验）")
        return 1

    # 1.5 覆盖提示（只提示，不拒绝、不交互）：在真正写盘之前让用户知道
    #     results/ 下这三个冻结结果会被重新写入。
    warn_if_outputs_exist((TRACK_CSV_PATH, OVERLAY_PATH, DS_CSV_PATH))

    # 2. M3 负责检测与记录：原始视频 -> track CSV + 叠加视频
    print("")
    print("========== 第 1 步：M3 逐帧追踪（原始视频 -> track CSV + overlay） ==========")
    track_summary = track_video(VIDEO_PATH, TRACK_CSV_PATH, OVERLAY_PATH)
    if track_summary is None:
        print("错误：视频无法处理：%s" % VIDEO_PATH)
        print("处理方式：停止运行（不生成 ds CSV）")
        print("退出码：1（视频无法处理）")
        return 1

    # 2.5 上游轨迹完整性：直接使用 M3 在同一进程内给出的结论，不从 _track.csv 反推
    #     （CSV 自洽不等于视频完整）。
    integrity = track_summary["track_integrity"]
    if integrity == "not_evaluated":
        print("")
        print("警告：上游轨迹完整性未评估（用户主动中断），"
              "本次跳过位移计算，不生成 _ds.csv。")
        print("      按规则不伪造任何 displacement metrics，也不把跳过当作 0 位移。")
        print("退出码：1（上游轨迹完整性 not_evaluated，本次位移计算被跳过）")
        return 1
    if integrity == "suspect":
        print("")
        print("警告：上游轨迹完整性存疑，将继续计算位移；使用结果前请人工核对轨迹完整性。")
    elif integrity == "unverified":
        print("")
        print("警告：上游轨迹完整性未验证，将继续计算位移；使用结果前请人工核对。")

    # 3. dynamic_displacement 模块负责 valid gate / 投影 / s0 / ds / 转向点：track CSV -> ds CSV
    print("")
    print("========== 第 2 步：EXP-004 动态位移（track CSV -> ds CSV + 统计 + 自检） ==========")
    report = run_experiment(TRACK_CSV_PATH, DS_CSV_PATH, EXPERIMENT_NAME)

    # 4. 把视频与 overlay 信息挂到报告上（只读，不参与任何计算）
    report["video_path"] = VIDEO_PATH
    report["overlay_path"] = OVERLAY_PATH
    report["track_frames_processed"] = track_summary["processed_frames"]
    report["track_integrity"] = integrity
    report["sha256_before"] = track_summary["sha256_before"]
    report["sha256_after"] = track_summary["sha256_after"]

    # 5. 打印最终统计与自检结果
    print_summary(report)
    print_final_checks(report, track_summary)

    # 6. 结果判定（退出码）：只追加机器可读信号，不替代上面任何终端输出
    exit_code, reason = final_exit_code(report)
    print("")
    print("========== 结果判定（退出码） ==========")
    print("退出码：%d（%s）" % (exit_code, reason))
    print("")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

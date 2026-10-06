"""
VisionMotion —— 冻结结果一致性测试（Phase 2B-2，TEST 15 ~ TEST 16；Phase 2B-3E，TEST 17）

TEST 15：M4 / M5 的冻结标定常量、gate 与 s0 规则自洽（只读自检，不重新标定）。
TEST 16：M6.3 封板轨迹 CSV 与封板极值清单 / 周期 T_exp / 频率 f_exp 的一致性。
TEST 17：M6.2 视频 SHA-256 完整性检查真正进入最终 QC（正确 SHA 通过、错误 SHA 拉低 passed）。

原则：只核对已经封板的数值；不重新挑选极值、不重新标定、不修改任何 results/ 文件。
"""

import hashlib
from pathlib import Path

import pytest

from src import displacement as m4
from src import dynamic_displacement as m5
from src import external_oscillation_tracker as m62
from src import m63_final_visualization as m63

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TRAJECTORY_CSV = PROJECT_ROOT / "results" / "EXP-EXT-LAB67-V1_trajectory.csv"
TRAJECTORY_SHA256 = "2604e9af7c34f3ea6198117716ef2b43d352469687b3670d26e4e02a153b4e67"


def test_m4_m5_frozen_constants_self_check():
    """TEST 15 —— M4 / M5 冻结常量：模块自检通过，且与封板数值逐项一致、互不混用。"""
    checks4, passed4 = m4.check_calibration_constants()
    checks5, passed5 = m5.check_calibration_constants()

    assert passed4 is True and all(ok for _, ok in checks4)
    assert passed5 is True and all(ok for _, ok in checks5)

    # M4（EXP-003）封板值
    assert m4.CALIB_REAL_DISTANCE_MM == 60.0
    assert m4.PX_PER_MM == pytest.approx(5.756961, abs=1e-9)
    assert m4.MM_PER_PX == pytest.approx(0.173703, abs=1e-9)
    assert m4.U == pytest.approx((0.999976, -0.006894), abs=1e-6)
    assert (m4.AREA_MIN_PX, m4.AREA_MAX_PX) == (2000.0, 15000.0)
    assert (m4.Y_MIN_PX, m4.Y_MAX_PX) == (400.0, 540.0)
    assert (m4.S0_WINDOW_S, m4.MIN_S0_VALID_FRAMES) == (0.5, 10)

    # M5（EXP-004）封板值
    assert m5.CALIB_REAL_DISTANCE_MM == 100.0
    assert m5.PX_PER_MM_004 == pytest.approx(6.086399, abs=1e-9)
    assert m5.MM_PER_PX_004 == pytest.approx(0.164301, abs=1e-9)
    assert m5.U_004 == pytest.approx((0.999992, -0.003913), abs=1e-6)
    assert (m5.AREA_MIN_PX_004, m5.AREA_MAX_PX_004) == (4500.0, 6500.0)
    assert (m5.Y_MIN_PX_004, m5.Y_MAX_PX_004) == (200.0, 250.0)
    assert (m5.S0_WINDOW_S, m5.MIN_S0_VALID_FRAMES) == (2.0, 60)
    assert m5.MIN_TURN_TRAVEL_PX == 20.0

    # 两套冻结常量不得互相混用
    assert m4.U != m5.U_004
    assert m4.PX_PER_MM != m5.PX_PER_MM_004

    # M4 rules_snapshot 记录的规则与模块当前常量一致
    snapshot = m4.rules_snapshot()
    assert snapshot["PX_PER_MM"] == m4.PX_PER_MM
    assert snapshot["MM_PER_PX"] == m4.MM_PER_PX
    assert snapshot["u"] == m4.U
    assert snapshot["area_px"] == (m4.AREA_MIN_PX, m4.AREA_MAX_PX)
    assert snapshot["y_px"] == (m4.Y_MIN_PX, m4.Y_MAX_PX)
    assert snapshot["s0_window_s"] == m4.S0_WINDOW_S
    assert snapshot["min_s0_valid_frames"] == m4.MIN_S0_VALID_FRAMES


def _extrema_with_plateau_rule(series):
    """按封板规则复算极值：相邻相同 y0 合并为平台块取帧中点，再用两侧严格不等号判定。"""
    frames = [int(value) for value in series["frame"]]
    times = [float(value) for value in series["time"]]
    values = [float(value) for value in series["y0"]]

    blocks = []
    current = [0]
    for index in range(1, len(values)):
        if values[index] == values[index - 1]:
            current.append(index)
        else:
            blocks.append(current)
            current = [index]
    blocks.append(current)

    merged = [
        (
            sum(frames[i] for i in block) / len(block),
            sum(times[i] for i in block) / len(block),
            values[block[0]],
        )
        for block in blocks
    ]

    peaks, troughs = [], []
    for index in range(1, len(merged) - 1):
        before = merged[index - 1][2]
        point = merged[index]
        after = merged[index + 1][2]
        if point[2] > before and point[2] > after:
            peaks.append(point)
        elif point[2] < before and point[2] < after:
            troughs.append(point)
    return peaks, troughs


def test_m63_frozen_trajectory_extrema_and_period():
    """TEST 16 —— M6.3 封板结果：轨迹 CSV 结构、20 个极值、T_exp / f_exp 与报告完全一致。"""
    assert TRAJECTORY_CSV.exists(), "封板轨迹 CSV 必须随仓库提供：%s" % TRAJECTORY_CSV

    raw = TRAJECTORY_CSV.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    normalized = raw.replace(b"\r\n", b"\n")  # 与换行风格无关的内容校验
    assert hashlib.sha256(normalized).hexdigest() == TRAJECTORY_SHA256

    series = m63.load_trajectory(TRAJECTORY_CSV)
    frames = series["frame"].astype(int).tolist()
    assert frames == list(range(76, 236))  # frame 76~235，共 160 帧
    assert series["y0"].min() == 508.0 and series["y0"].max() == 622.0

    # 封板清单中的每个极值都必须能在 CSV 对应帧（或平台块）上复现
    assert m63.check_frozen_extrema_against_csv(series) == []

    peaks, troughs = _extrema_with_plateau_rule(series)
    assert [frame for frame, _, _ in peaks] == [frame for frame, _, _ in m63.FROZEN_PEAKS]
    assert [frame for frame, _, _ in troughs] == [frame for frame, _, _ in m63.FROZEN_TROUGHS]
    assert [value for _, _, value in peaks] == [value for _, _, value in m63.FROZEN_PEAKS]
    assert [value for _, _, value in troughs] == [value for _, _, value in m63.FROZEN_TROUGHS]

    # 周期 / 频率：9 段峰—峰间隔均值，与封板值一致（M6.3 报告 5.3）
    peak_times = [time for _, time, _ in peaks]
    intervals = [peak_times[i + 1] - peak_times[i] for i in range(len(peak_times) - 1)]
    period = sum(intervals) / len(intervals)
    frequency = 1.0 / period

    assert len(intervals) == 9
    assert period == pytest.approx(0.542593, abs=1e-6)
    assert period == pytest.approx(m63.FROZEN["T_exp"], abs=1e-6)
    assert frequency == pytest.approx(1.843003, abs=1e-6)
    assert frequency == pytest.approx(m63.FROZEN["f_exp"], abs=1e-6)

    # 一致性交叉检查：谷—谷间隔与半周期法（2x）互差 ≤ 0.09%（报告中三种方法一致）
    trough_times = [time for _, time, _ in troughs]
    trough_periods = [
        trough_times[i + 1] - trough_times[i] for i in range(len(trough_times) - 1)
    ]
    trough_period = sum(trough_periods) / len(trough_periods)
    extrema_times = sorted(peak_times + trough_times)
    half_gaps = [extrema_times[i + 1] - extrema_times[i] for i in range(len(extrema_times) - 1)]
    half_period_method = 2.0 * sum(half_gaps) / len(half_gaps)

    assert trough_period == pytest.approx(period, abs=1e-5)
    assert half_period_method == pytest.approx(0.542105, abs=1e-5)
    assert abs(half_period_method - period) < 0.001


# ============================================================
# Phase 2B-3E：M6.2 视频 SHA-256 完整性检查必须真正进入最终 QC
#
# 缺陷：src/external_oscillation_tracker.py 的 check_trajectory_csv() 里曾有一条
# “# 16. 原始视频未被改动（运行前后 SHA-256 一致）”注释，却没有把它 append 进 checks，
# 于是 SHA 只被计算 / 打印，不影响最终 passed。
# ============================================================


M62_VIDEO = (
    PROJECT_ROOT / "_external" / "_candidates"
    / "candidate_comPADRE_Lab67_01_Video1_51p5g.mp4"
)
SHA256_SAMPLE_BYTES = b"VisionMotion SHA test\n"
SHA256_SAMPLE_DIGEST = hashlib.sha256(SHA256_SAMPLE_BYTES).hexdigest()
WRONG_SHA256 = "0" * 64


def _m62_all_other_checks_pass():
    """
    构造“除 SHA 外全部通过”的 M6.2 QC 输入（只喂 check_trajectory_csv，不写任何文件）：
    160 帧、y0 恒定（无突跳）、accepted_count=1（无候选歧义）、time_s = frame / fps。
    """
    fps = 30.0
    frames = range(m62.START_FRAME, m62.END_FRAME + 1)
    rows = [
        {
            "frame": frame,
            "time_s": frame / fps,
            "detected": True,
            "x_px": 723.0,
            "y0_px": 560.0,
            "bbox_w_px": 57.0,
            "bbox_h_px": 8.0,
            "area_px": 400.0,
        }
        for frame in frames
    ]
    run_rows = [{"frame": frame, "accepted_count": 1} for frame in frames]
    csv_data = {"header": m62.CSV_FIELDNAMES, "rows": rows, "raw_line_count": len(rows) + 1}
    return csv_data, run_rows, fps


def _m62_sha_checks(checks):
    """取出 checks 里唯一一条 SHA-256 完整性判据（True / False）。"""
    return [ok for description, ok in checks if "SHA-256 完整性" in description]


def test_m62_video_sha256_ok_unit_with_small_temp_file(tmp_path):
    """TEST 17a —— 单元层：临时小文件已知 SHA，正确 / 错误 / 被改动 / 缺值四种判据。"""
    sample = tmp_path / "sha_sample.bin"
    sample.write_bytes(SHA256_SAMPLE_BYTES)
    actual = m62.compute_sha256(sample)
    assert actual == SHA256_SAMPLE_DIGEST

    assert m62.video_sha256_ok(actual, actual, actual) is True
    assert m62.video_sha256_ok(actual.upper(), actual, actual) is True  # 仅十六进制大小写差异
    assert m62.video_sha256_ok(actual, actual, WRONG_SHA256) is False  # 预期基线错误
    assert m62.video_sha256_ok(actual, "f" * 64, actual) is False      # 运行后被改动
    assert m62.video_sha256_ok(None, None, actual) is False            # 无法证明完整 -> 不放行


def test_m62_sha256_check_is_included_in_final_passed():
    """TEST 17b —— QC 层：其它检查全通过时，SHA 错误仍必须把最终 passed 拉成 False。"""
    csv_data, run_rows, fps = _m62_all_other_checks_pass()

    # Case A：正确 SHA -> SHA 检查通过 -> 总体 passed=True
    checks, passed = m62.check_trajectory_csv(
        csv_data, run_rows, fps,
        sha256_before=m62.EXTERNAL_VIDEO_SHA256,
        sha256_after=m62.EXTERNAL_VIDEO_SHA256,
        expected_sha256=m62.EXTERNAL_VIDEO_SHA256,
    )
    assert _m62_sha_checks(checks) == [True]
    assert passed is True

    # Case B：expected SHA 错误 -> SHA 检查失败；其它检查仍全通过，但 overall passed=False
    checks, passed = m62.check_trajectory_csv(
        csv_data, run_rows, fps,
        sha256_before=m62.EXTERNAL_VIDEO_SHA256,
        sha256_after=m62.EXTERNAL_VIDEO_SHA256,
        expected_sha256=WRONG_SHA256,
    )
    assert _m62_sha_checks(checks) == [False]
    assert all(ok for description, ok in checks if "SHA-256 完整性" not in description)
    assert passed is False

    # Case B'：视频在运行中被改动（before != after）-> 同样必须拉低 passed
    checks, passed = m62.check_trajectory_csv(
        csv_data, run_rows, fps,
        sha256_before=m62.EXTERNAL_VIDEO_SHA256,
        sha256_after="f" * 64,
        expected_sha256=m62.EXTERNAL_VIDEO_SHA256,
    )
    assert _m62_sha_checks(checks) == [False]
    assert passed is False


@pytest.mark.skipif(not M62_VIDEO.exists(), reason="正式外部视频未随仓库分发（_external/ 未被 git 跟踪）")
def test_m62_formal_video_sha256_integrity_passes(tmp_path):
    """TEST 17c —— 集成层：正式 M6.2 视频（只读）通过 SHA 检查，最终 passed=True。"""
    csv_path = tmp_path / "EXP-EXT-LAB67-V1_trajectory.csv"
    summary, _, checks, passed = m62.run_external_tracking(
        M62_VIDEO, csv_path, expected_sha256=m62.EXTERNAL_VIDEO_SHA256
    )

    assert summary["sha256_before"] == m62.EXTERNAL_VIDEO_SHA256
    assert summary["sha256_after"] == m62.EXTERNAL_VIDEO_SHA256
    assert _m62_sha_checks(checks) == [True]
    assert passed is True


@pytest.mark.skipif(not M62_VIDEO.exists(), reason="正式外部视频未随仓库分发（_external/ 未被 git 跟踪）")
def test_m62_formal_video_wrong_expected_sha256_is_blocked(tmp_path):
    """TEST 17d —— 集成层：expected SHA 错误时正式流程被阻断，不得静默通过、不得产出 CSV。"""
    csv_path = tmp_path / "blocked.csv"
    with pytest.raises(RuntimeError):
        m62.run_external_tracking(M62_VIDEO, csv_path, expected_sha256=WRONG_SHA256)
    assert not csv_path.exists()

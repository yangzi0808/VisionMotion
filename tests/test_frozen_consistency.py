"""
VisionMotion —— 冻结结果一致性测试（Phase 2B-2，TEST 15 ~ TEST 16）

TEST 15：M4 / M5 的冻结标定常量、gate 与 s0 规则自洽（只读自检，不重新标定）。
TEST 16：M6.3 封板轨迹 CSV 与封板极值清单 / 周期 T_exp / 频率 f_exp 的一致性。

原则：只核对已经封板的数值；不重新挑选极值、不重新标定、不修改任何 results/ 文件。
"""

import hashlib
from pathlib import Path

import pytest

from src import displacement as m4
from src import dynamic_displacement as m5
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

"""
VisionMotion —— 转向点与运动段规则测试（Phase 2B-2，TEST 12 ~ TEST 14）

保护对象：src/dynamic_displacement.py 的 detect_turning_points()
    - 只使用原始 x_px 序列（detected=True 的行），不平滑 / 不滤波 / 不插值；
    - 反向行程阈值 MIN_TURN_TRAVEL_PX = 20 px；
    - 视频首尾只作记录边界；valid=False 的行只统计不删除。
"""

import pytest

from src import dynamic_displacement as m5


def _dynamic_rows(xs, missed=(), invalid=()):
    """
    合成 EXP-004 行：
        - valid 行带 ds_mm（相对首帧 x）；
        - invalid 行：detected=True 但 valid=False，ds_mm 保持 None（不伪造数值）；
        - missed 帧：整帧未检出（x=None）。
    """
    rows = []
    for index, x in enumerate(xs):
        detected = index not in missed
        valid = detected and index not in invalid
        row = {
            "frame": index,
            "time_s": index / 30.0,
            "x_px": float(x) if detected else None,
            "y_px": 220.0 if detected else None,
            "area_px": 5000.0 if detected else None,
            "detected": detected,
            "valid": valid,
            "s_px": None,
            "ds_px": None,
            "ds_mm": None,
        }
        if valid:
            row["ds_px"] = float(x) - float(xs[0])
            row["ds_mm"] = row["ds_px"] / m5.PX_PER_MM_004
        rows.append(row)
    return rows


def test_turning_points_zigzag_peak_valley_and_segments():
    """TEST 12 —— 一维往复序列：峰 / 谷转向点与运动段切分完全符合冻结规则。"""
    xs = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0, 40.0, 30.0, 20.0, 10.0, 0.0, 10.0, 20.0, 30.0, 40.0]
    report = m5.detect_turning_points(_dynamic_rows(xs))

    assert report["analysis_rows"] == 15
    assert report["analysis_invalid_rows"] == 0
    assert report["min_turn_travel_px"] == m5.MIN_TURN_TRAVEL_PX == 20.0
    assert report["start"]["frame"] == 0 and report["start"]["x_px"] == 0.0
    assert report["end"]["frame"] == 14 and report["end"]["x_px"] == 40.0

    assert [turn["frame"] for turn in report["turns"]] == [5, 10]
    assert [turn["kind"] for turn in report["turns"]] == ["peak", "valley"]
    assert [turn["x_px"] for turn in report["turns"]] == [50.0, 0.0]

    # 方向文字是冻结说法：正向 = ds 增大，负向 = ds 减小
    peak, valley = report["turns"]
    assert peak["direction_before"] == "正向" and peak["direction_after"] == "负向"
    assert valley["direction_before"] == "负向" and valley["direction_after"] == "正向"

    # 首尾只是边界：运动段数 = 转向点数 + 1
    assert [segment["start_frame"] for segment in report["segments"]] == [0, 5, 10]
    assert [segment["end_frame"] for segment in report["segments"]] == [5, 10, 14]
    assert [segment["direction"] for segment in report["segments"]] == ["正向", "负向", "正向"]
    assert [segment["travel_px"] for segment in report["segments"]] == [50.0, 50.0, 40.0]
    assert all(segment["below_min_travel"] is False for segment in report["segments"])


def test_turning_points_min_travel_threshold_rejects_noise():
    """TEST 13 —— 20 px 反向行程阈值：静止噪声与 19.5 px 波动不误判；恰好 20 px 生效。"""
    # 静止段噪声（波动 < 20 px）：不产生任何转向点
    noise = [100.0, 100.8, 99.4, 100.9, 99.3, 100.7, 99.5, 100.6, 99.6]
    report = m5.detect_turning_points(_dynamic_rows(noise))
    assert report["turns"] == []
    assert len(report["segments"]) == 1
    assert report["segments"][0]["below_min_travel"] is True
    assert report["segments"][0]["travel_px"] < m5.MIN_TURN_TRAVEL_PX

    # 差一点点（19.5 px < 20 px）：仍不确认方向，不产生转向点
    report = m5.detect_turning_points(_dynamic_rows([0.0, 19.5, 0.5, 19.4, 0.6]))
    assert report["turns"] == []

    # 恰好 20 px（阈值判定为 >= 20 px 生效）：峰与谷都被确认
    report = m5.detect_turning_points(_dynamic_rows([0.0, 20.0, 0.0, 20.0]))
    assert [turn["frame"] for turn in report["turns"]] == [1, 2]
    assert [turn["kind"] for turn in report["turns"]] == ["peak", "valley"]


def test_turning_points_count_invalid_rows_without_deleting():
    """TEST 14 —— valid=False 的行只统计不删除；转向点落在无效帧时 ds_mm 保持 None。"""
    xs = [
        100.0, 110.0, 120.0, 130.0, 140.0, 150.0, 140.0, 130.0,
        120.0, 110.0, 100.0, 110.0, 120.0, 130.0, 140.0,
    ]
    rows = _dynamic_rows(xs, missed={3}, invalid={5})
    report = m5.detect_turning_points(rows)

    assert report["analysis_rows"] == 14  # detected=False 的行不参与分析
    assert report["analysis_invalid_rows"] == 1  # 只统计，不删除
    assert report["start"]["frame"] == 0 and report["end"]["frame"] == 14

    assert [turn["frame"] for turn in report["turns"]] == [5, 10]
    peak = report["turns"][0]
    assert peak["kind"] == "peak" and peak["x_px"] == 150.0
    assert peak["ds_mm"] is None  # valid=False：不伪造位移数值
    valley = report["turns"][1]
    assert valley["ds_mm"] == pytest.approx(0.0)  # frame 10 与首帧同位置

    assert len(report["segments"]) == len(report["turns"]) + 1

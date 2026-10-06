"""
VisionMotion —— M4 / M5 位移规则测试（Phase 2B-2，TEST 08 ~ TEST 11）

保护对象：
    src/displacement.py          （M4，EXP-003：gate 2000~15000 px² / y 400~540，s0 窗口 0.5 s / 10 帧）
    src/dynamic_displacement.py  （M5，EXP-004：gate 4500~6500 px² / y 200~250，s0 窗口 2.0 s / 60 帧）

覆盖：gate 真值表与两套 gate 不混用 / s0 窗口与帧数下限 / ds 行格式与端到端产出 /
      畸形 track CSV 与非法 detected 文本的防护（已知 bug 用 strict xfail 标记，本阶段不改 src/）。
"""

import math

import pytest

from src import displacement as m4
from src import dynamic_displacement as m5
from src.calibration import project_point


def _track_rows(xs, *, valid_y, valid_area, invalid_y, missed=(), invalid=()):
    """
    合成 M3 track 行：
        - 默认行：detected=True、y=valid_y、area=valid_area（有效）；
        - missed 帧：整帧未检出（x / y / area 全空，detected=False）；
        - invalid 帧：detected=True 但 y=invalid_y（出 gate）。
    """
    rows = []
    for index, x in enumerate(xs):
        detected = index not in missed
        row = {
            "frame": index,
            "time_s": index / 30.0,
            "x_px": float(x) if detected else None,
            "y_px": None,
            "area_px": None,
            "detected": detected,
        }
        if detected:
            row["y_px"] = invalid_y if index in invalid else valid_y
            row["area_px"] = valid_area
        rows.append(row)
    return rows


def test_valid_gates_m4_m5_truth_table_and_isolation():
    """TEST 08 —— M4 / M5 gate 真值表：边界含端点、缺数据不可用、两套阈值不得混用。"""
    # M4（EXP-003）：area 2000~15000、y 400~540，边界含端点
    assert m4.is_valid_frame(True, m4.AREA_MIN_PX, m4.Y_MIN_PX) is True
    assert m4.is_valid_frame(True, m4.AREA_MAX_PX, m4.Y_MAX_PX) is True
    assert m4.is_valid_frame(True, 3000.0, 450.0) is True
    assert m4.is_valid_frame(False, 3000.0, 450.0) is False
    assert m4.is_valid_frame(True, m4.AREA_MIN_PX - 1.0, 450.0) is False
    assert m4.is_valid_frame(True, m4.AREA_MAX_PX + 1.0, 450.0) is False
    assert m4.is_valid_frame(True, 3000.0, m4.Y_MIN_PX - 1.0) is False
    assert m4.is_valid_frame(True, 3000.0, m4.Y_MAX_PX + 1.0) is False
    assert m4.is_valid_frame(True, None, 450.0) is False
    assert m4.is_valid_frame(True, 3000.0, None) is False

    # M5（EXP-004）：area 4500~6500、y 200~250，边界含端点
    assert m5.is_valid_frame(True, m5.AREA_MIN_PX_004, m5.Y_MIN_PX_004) is True
    assert m5.is_valid_frame(True, m5.AREA_MAX_PX_004, m5.Y_MAX_PX_004) is True
    assert m5.is_valid_frame(True, 5000.0, 220.0) is True
    assert m5.is_valid_frame(False, 5000.0, 220.0) is False
    assert m5.is_valid_frame(True, m5.AREA_MIN_PX_004 - 1.0, 220.0) is False
    assert m5.is_valid_frame(True, m5.AREA_MAX_PX_004 + 1.0, 220.0) is False
    assert m5.is_valid_frame(True, 5000.0, m5.Y_MIN_PX_004 - 1.0) is False
    assert m5.is_valid_frame(True, 5000.0, m5.Y_MAX_PX_004 + 1.0) is False
    assert m5.is_valid_frame(True, None, 220.0) is False
    assert m5.is_valid_frame(True, 5000.0, None) is False

    # 两套 gate 不混用：同一个 (area, y) 在 M4 有效、在 M5 无效，反之亦然
    assert m4.is_valid_frame(True, 3000.0, 450.0) is True
    assert m5.is_valid_frame(True, 3000.0, 450.0) is False
    assert m4.is_valid_frame(True, 6000.0, 220.0) is False
    assert m5.is_valid_frame(True, 6000.0, 220.0) is True


def test_s0_window_rules_for_m4_and_m5(write_track_csv, tmp_path):
    """TEST 09 —— s0 规则：只用窗口内 valid 帧求平均；帧数不足时 ok=False / s0=None / 不写 ds。"""
    # --- M4：窗口 0.5 s（含端点），有效帧下限 10 ---
    xs = [1000.0 + 5.0 * i for i in range(20)]
    rows = _track_rows(
        xs, valid_y=450.0, valid_area=3000.0, invalid_y=300.0, missed={5}, invalid={8}
    )
    m4.add_valid_flags(rows)
    m4.add_projection(rows)
    report = m4.compute_s0(rows)

    assert report["window_s"] == m4.S0_WINDOW_S == 0.5
    assert report["window_total_frames"] == 16  # frame 0~15：time_s <= 0.5（含 0.5）
    assert report["window_valid_frames"] == 14  # 1 帧未检出 + 1 帧出 gate
    assert report["window_missed_frames"] == 1
    assert report["window_detected_invalid_frames"] == 1
    assert report["min_valid_frames"] == m4.MIN_S0_VALID_FRAMES == 10
    assert report["ok"] is True

    expected_values = [
        project_point((xs[i], 450.0), m4.U) for i in range(16) if i not in (5, 8)
    ]
    assert report["s0"] == pytest.approx(
        sum(expected_values) / len(expected_values), abs=1e-9
    )

    # 窗口外（frame 16~19）即使出现极端 x 也不参与 s0（不扩大窗口）
    for row in rows[16:]:
        row["x_px"] = 99999.0
    m4.add_valid_flags(rows)
    m4.add_projection(rows)
    report_after = m4.compute_s0(rows)
    assert report_after["s0"] == pytest.approx(report["s0"], abs=1e-9)

    # 有效帧不足 10 帧：ok=False、s0 保持 None，且不生成 ds CSV（不插值、不改阈值）
    short_rows = _track_rows(
        [1000.0 + i for i in range(12)],
        valid_y=450.0,
        valid_area=3000.0,
        invalid_y=300.0,
        missed={1, 2, 3},
    )
    track_path = write_track_csv(short_rows)
    ds_path = tmp_path / "out" / "EXP-SHORT_ds.csv"
    short_report = m4.build_ds_from_track_csv(track_path, ds_path)
    assert short_report["s0_report"]["window_valid_frames"] == 9
    assert short_report["s0_report"]["ok"] is False
    assert short_report["s0_report"]["s0"] is None
    assert short_report["ds_written"] is False
    assert not ds_path.exists()

    # --- M5：窗口 2.0 s，有效帧下限 60 ---
    xs5 = [2000.0 + 3.0 * i for i in range(66)]
    xs5[61] = 99999.0  # frame 61 在窗口外（t≈2.033 s），不得影响 s0
    rows5 = _track_rows(
        xs5, valid_y=220.0, valid_area=5000.0, invalid_y=90.0, missed={3}
    )
    m5.add_valid_flags(rows5)
    m5.add_projection(rows5)
    report5 = m5.compute_s0(rows5)

    assert report5["window_s"] == m5.S0_WINDOW_S == 2.0
    assert report5["window_total_frames"] == 61  # frame 0~60：time_s <= 2.0
    assert report5["window_valid_frames"] == 60
    assert report5["min_valid_frames"] == m5.MIN_S0_VALID_FRAMES == 60
    assert report5["ok"] is True
    expected_values5 = [
        project_point((xs5[i], 220.0), m5.U_004) for i in range(61) if i != 3
    ]
    assert report5["s0"] == pytest.approx(
        sum(expected_values5) / len(expected_values5), abs=1e-9
    )

    # 再少一帧就低于下限：ok=False、s0=None
    rows5b = [dict(row) for row in rows5]
    rows5b[4]["y_px"] = 90.0
    m5.add_valid_flags(rows5b)
    m5.add_projection(rows5b)
    report5b = m5.compute_s0(rows5b)
    assert report5b["window_valid_frames"] == 59
    assert report5b["ok"] is False
    assert report5b["s0"] is None


def test_ds_row_format_and_m4_pipeline_end_to_end(write_track_csv, tmp_path):
    """TEST 10 —— ds 行格式：小数位数 / 空字段 / 布尔文本；M4 端到端产出通过模块自检。"""
    # --- 行格式：严格按冻结规范格式化，缺失字段留空（绝不写 0 / -1 / nan）---
    valid_row = {
        "frame": 7,
        "time_s": 0.2333333,
        "s_px": 1234.5678,
        "ds_px": -1.2341,
        "ds_mm": -0.2144,
        "area_px": 3000.0,
        "detected": True,
        "valid": True,
    }
    assert m4.build_ds_row(valid_row) == [
        "7",
        "0.233333",
        "1234.568",
        "-1.234",
        "-0.2144",
        "3000.0",
        "True",
        "True",
    ]

    invalid_row = {
        "frame": 9,
        "time_s": 0.3,
        "s_px": None,
        "ds_px": None,
        "ds_mm": None,
        "area_px": None,
        "detected": False,
        "valid": False,
    }
    assert m4.build_ds_row(invalid_row) == [
        "9",
        "0.300000",
        "",
        "",
        "",
        "",
        "False",
        "False",
    ]

    # --- 端到端：合成 track CSV -> build_ds -> write_ds_csv -> 模块自检 ---
    xs = [1000.0 + 10.0 * i for i in range(20)]
    rows = _track_rows(
        xs, valid_y=450.0, valid_area=3000.0, invalid_y=300.0, missed={5}, invalid={8}
    )
    track_path = write_track_csv(rows)
    ds_path = tmp_path / "EXP-TEST-DYNAMIC_ds.csv"

    report = m4.run_experiment(track_path, ds_path)

    assert report["ds_written"] is True
    assert report["passed"] is True, [
        item for item in report["checks"] if not item[1]
    ]

    raw = ds_path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in raw

    lines = m4.read_ds_csv_lines(ds_path)
    assert lines[0] == m4.DS_FIELDNAMES
    assert len(lines) - 1 == len(rows)
    assert [ds_row[0] for ds_row in lines[1:]] == [
        "%d" % row["frame"] for row in rows
    ]

    s0 = report["s0_report"]["s0"]
    for track_entry, ds_row in zip(rows, lines[1:]):
        if ds_row[7] == "False":
            assert ds_row[2] == ds_row[3] == ds_row[4] == ""
        else:
            s_px = float(ds_row[2])
            ds_px = float(ds_row[3])
            ds_mm = float(ds_row[4])
            assert math.isfinite(s_px) and math.isfinite(ds_px) and math.isfinite(ds_mm)
            assert ds_px == pytest.approx(s_px - s0, abs=0.002)
            assert ds_mm == pytest.approx(ds_px / m4.PX_PER_MM, abs=0.0005)
        if track_entry["detected"]:
            assert ds_row[5] != ""
        else:
            assert ds_row[5] == ""


@pytest.mark.xfail(
    strict=True,
    reason=(
        "已知 bug（本阶段禁止修改 src/）：(1) detected=True 但 x_px 缺失的行按模块自述应判 invalid，"
        "当前会进入投影流程；(2) detected 列文本不是 True/False 时当前被静默解析为 False，"
        "按 M3 / M4 / M5 的 CSV 规范应先明确报错。"
    ),
)
def test_malformed_track_csv_and_illegal_detected_are_rejected(tmp_path, write_track_csv):
    """TEST 11 —— track CSV 防护：结构畸形必须明确报错；缺失 / 非法 detected 不得静默当 False。"""
    good_row = {
        "frame": 0,
        "time_s": 0.0,
        "x_px": 1000.0,
        "y_px": 450.0,
        "area_px": 3000.0,
        "detected": True,
    }

    # (a) 表头不符 / 列数不对：应明确抛 ValueError，而不是继续产出数据
    bad_header = tmp_path / "bad_header.csv"
    bad_header.write_text(
        "frame,time,px,py,area,detected\n0,0.0,1.0,1.0,1.0,True\n", encoding="utf-8"
    )
    with pytest.raises(ValueError):
        m4.read_track_csv(bad_header)

    bad_columns = tmp_path / "bad_columns.csv"
    bad_columns.write_text(
        "frame,time_s,x_px,y_px,area_px,detected\n0,0.000000,1000.00\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        m4.read_track_csv(bad_columns)
    with pytest.raises(ValueError):
        m5.read_track_csv(bad_columns)

    # (b) detected=True 但 x_px 为空：属于数据缺失，应判 invalid（不填 0、不进入投影）
    missing_x_rows = [
        good_row,
        {
            "frame": 1,
            "time_s": 1 / 30,
            "x_px": None,
            "y_px": 450.0,
            "area_px": 3000.0,
            "detected": True,
        },
    ]
    track_path = write_track_csv(missing_x_rows)
    parsed = m4.read_track_csv(track_path)
    m4.add_valid_flags(parsed)
    assert parsed[1]["valid"] is False, (
        "detected=True 但 x_px 缺失的行必须判为 invalid（数据缺失不能用）"
    )
    m4.add_projection(parsed)  # 不得因缺失 x 崩溃

    # (c) detected 列只能写 True / False；'1' / 'yes' / 'true' / 空 这类文本必须报错
    for illegal_text in ("1", "yes", "true", ""):
        illegal = tmp_path / ("illegal_%s.csv" % (illegal_text or "empty"))
        illegal.write_text(
            "frame,time_s,x_px,y_px,area_px,detected\n"
            "0,0.000000,1000.00,450.00,3000.0,%s\n" % illegal_text,
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            m4.read_track_csv(illegal)
        with pytest.raises(ValueError):
            m5.read_track_csv(illegal)

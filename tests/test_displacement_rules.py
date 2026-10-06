"""
VisionMotion —— M4 / M5 位移规则测试（Phase 2B-2，TEST 08 ~ TEST 11）

保护对象：
    src/displacement.py          （M4，EXP-003：gate 2000~15000 px² / y 400~540，s0 窗口 0.5 s / 10 帧）
    src/dynamic_displacement.py  （M5，EXP-004：gate 4500~6500 px² / y 200~250，s0 窗口 2.0 s / 60 帧）

覆盖：gate 真值表与两套 gate 不混用 / s0 窗口与帧数下限 / ds 行格式与端到端产出 /
      畸形 / 截断 CSV 的防护（M3 check_csv_data 已做防御性最小修复，TEST 11A 必须通过）/
      非法 detected 文本必须被拒绝（TEST 11B：M4 / M5 两个读取器都已修复）/
      detected=True 但 x_px / y_px / area_px 缺任一必须判 invalid（TEST 17，M4 / M5 都锁定）/
      detected=True 但 x_px 为 NaN / inf / -inf 必须判 invalid（TEST 19 / TEST 20，
      Phase 2B-5A：M4 / M5 都锁定，且不得误伤有限值 / detected=False + None）。
"""

import math
from pathlib import Path

import pytest

from src import displacement as m4
from src import dynamic_displacement as m5
from src.calibration import project_point
from src.video_tracker import check_csv_data


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
    """TEST 08 —— M4 / M5 gate 真值表：边界含端点、缺任一必要字段不可用、两套阈值不得混用。"""
    # M4（EXP-003）：area 2000~15000、y 400~540，边界含端点
    assert m4.is_valid_frame(True, 1000.0, m4.Y_MIN_PX, m4.AREA_MIN_PX) is True
    assert m4.is_valid_frame(True, 1000.0, m4.Y_MAX_PX, m4.AREA_MAX_PX) is True
    assert m4.is_valid_frame(True, 1000.0, 450.0, 3000.0) is True
    assert m4.is_valid_frame(False, 1000.0, 450.0, 3000.0) is False
    assert m4.is_valid_frame(True, 1000.0, 450.0, m4.AREA_MIN_PX - 1.0) is False
    assert m4.is_valid_frame(True, 1000.0, 450.0, m4.AREA_MAX_PX + 1.0) is False
    assert m4.is_valid_frame(True, 1000.0, m4.Y_MIN_PX - 1.0, 3000.0) is False
    assert m4.is_valid_frame(True, 1000.0, m4.Y_MAX_PX + 1.0, 3000.0) is False
    # 三个必要数值字段缺任何一个都不可用（x_px / y_px / area_px）
    assert m4.is_valid_frame(True, None, 450.0, 3000.0) is False
    assert m4.is_valid_frame(True, 1000.0, None, 3000.0) is False
    assert m4.is_valid_frame(True, 1000.0, 450.0, None) is False

    # M5（EXP-004）：area 4500~6500、y 200~250，边界含端点
    assert m5.is_valid_frame(True, 1000.0, m5.Y_MIN_PX_004, m5.AREA_MIN_PX_004) is True
    assert m5.is_valid_frame(True, 1000.0, m5.Y_MAX_PX_004, m5.AREA_MAX_PX_004) is True
    assert m5.is_valid_frame(True, 1000.0, 220.0, 5000.0) is True
    assert m5.is_valid_frame(False, 1000.0, 220.0, 5000.0) is False
    assert m5.is_valid_frame(True, 1000.0, 220.0, m5.AREA_MIN_PX_004 - 1.0) is False
    assert m5.is_valid_frame(True, 1000.0, 220.0, m5.AREA_MAX_PX_004 + 1.0) is False
    assert m5.is_valid_frame(True, 1000.0, m5.Y_MIN_PX_004 - 1.0, 5000.0) is False
    assert m5.is_valid_frame(True, 1000.0, m5.Y_MAX_PX_004 + 1.0, 5000.0) is False
    # 三个必要数值字段缺任何一个都不可用（x_px / y_px / area_px）
    assert m5.is_valid_frame(True, None, 220.0, 5000.0) is False
    assert m5.is_valid_frame(True, 1000.0, None, 5000.0) is False
    assert m5.is_valid_frame(True, 1000.0, 220.0, None) is False

    # 两套 gate 不混用：同一个 (x, y, area) 在 M4 有效、在 M5 无效，反之亦然
    assert m4.is_valid_frame(True, 1000.0, 450.0, 3000.0) is True
    assert m5.is_valid_frame(True, 1000.0, 450.0, 3000.0) is False
    assert m4.is_valid_frame(True, 1000.0, 220.0, 6000.0) is False
    assert m5.is_valid_frame(True, 1000.0, 220.0, 6000.0) is True


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


def test_malformed_csv_is_reported_not_raised(tmp_path):
    """TEST 11A —— M3 check_csv_data：畸形 / 截断 CSV 必须返回“未通过”，而不是抛 IndexError / ValueError。

    原 TEST 11 把“畸形 CSV 解析异常”和“非法 detected 文本被静默接受”两个彼此独立的缺陷
    绑在同一个测试里：缺陷 A 修好后会让整个测试意外通过，从而掩盖仍然存在的缺陷 B；
    因此按任务要求拆分为 TEST 11A（本测试，必须通过）与 TEST 11B（已修复，正常通过）。
    """
    header = "frame,time_s,x_px,y_px,area_px,detected"

    malformed_cases = {
        # ① 截断行（列数不足）：旧实现第二次遍历时 row[3] / row[5] 越界 -> IndexError
        "truncated_row": header + "\n0,0.000000,1000.00\n",
        # ② frame 不是整数：旧实现第二次遍历 int(row[0]) -> ValueError
        "non_integer_frame": header + "\nabc,0.000000,1000.00,450.00,3000.0,True\n",
        # ③ detected=True 但必需数值字段为空（必需字段不存在）
        "missing_required_field": header + "\n0,0.000000,,450.00,3000.0,True\n",
        # ④ 数值字段无法转 float
        "non_numeric_measurement": header + "\n0,0.000000,oops,450.00,3000.0,True\n",
    }

    for name, text in malformed_cases.items():
        csv_path = tmp_path / ("malformed_%s.csv" % name)
        csv_path.write_text(text, encoding="utf-8")
        # 关键：必须“正常运行 + 返回失败结果”，绝不向外抛 IndexError / ValueError
        checks, passed = check_csv_data(
            csv_path, expected_rows=1, frame_width=640, frame_height=480
        )
        assert checks, name
        assert passed is False, name

    # 读者侧的结构畸形防护（原 TEST 11(a)，本身无缺陷、保持通过）：
    # 表头不符 / 列数不对必须明确抛 ValueError，而不是继续产出数据
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


def test_illegal_detected_values_are_rejected(tmp_path):
    """TEST 11B —— illegal detected 文本必须被拒绝（M4 与 M5 两个读取器都要锁定）。

    使用同一个最小合法 CSV 模板，只替换 detected 字段，从而证明出问题的确实只有
    detected 格式，而不是其他字段。合法值 True / False 仍按原语义读取（不改变合法
    输入）；非法文本必须明确抛 ValueError，而不是被静默解释成 False。
    """
    header = "frame,time_s,x_px,y_px,area_px,detected\n"
    valid_template = header + "0,0.000000,1000.00,450.00,3000.0,%s\n"

    # 合法值 True / False：两个读取器都必须按原语义读成布尔值（证明只增加严格性）
    for valid_text, expected in (("True", True), ("False", False)):
        legal = tmp_path / ("legal_%s.csv" % valid_text)
        legal.write_text(valid_template % valid_text, encoding="utf-8")
        for reader in (m4.read_track_csv, m5.read_track_csv):
            rows = reader(legal)
            assert len(rows) == 1
            assert rows[0]["detected"] is expected

    # 非法值：M4 与 M5 两个读取器都必须明确拒绝，绝不静默变成 False
    for illegal_text in ("1", "yes", "true", ""):
        illegal = tmp_path / ("illegal_%s.csv" % (illegal_text or "empty"))
        illegal.write_text(valid_template % illegal_text, encoding="utf-8")
        with pytest.raises(ValueError):
            m4.read_track_csv(illegal)
        with pytest.raises(ValueError):
            m5.read_track_csv(illegal)


def test_detected_true_with_missing_required_field_is_invalid(write_track_csv):
    """TEST 17 —— detected=True 但 x_px / y_px / area_px 缺任一：判 invalid（M4 与 M5 都锁定）。

    Case A：detected=True 且 x_px 缺失（y / area 正常）-> valid=False，且投影不崩溃；
    Case B：detected=True 且 y_px 缺失（x / area 正常）-> valid=False；
    Case C：detected=True 且 area_px 缺失（x / y 正常）-> valid=False；
    Case D：detected=False 且 x / y / area 全缺失 -> 仍属合法输入（读取不报错），valid=False；
    对照组：detected=True 且 x / y / area 全齐 -> valid=True（合法输入行为不变）。

    说明：detected=True 时“缺字段”属于数据缺失，必须判 invalid（不填 0、不插值）；
    这里连同 add_projection 一起跑，证明该行不会再被当成 valid 送进投影。
    """
    cases = {
        "A_true_missing_x": (True, False, True, True),
        "B_true_missing_y": (True, True, False, True),
        "C_true_missing_area": (True, True, True, False),
        "D_false_missing_all": (False, False, False, False),
        "E_true_complete": (True, True, True, True),
    }

    for tag, (detected, has_x, has_y, has_area) in cases.items():
        for name, module, valid_y, valid_area in (
            ("M4", m4, 450.0, 3000.0),
            ("M5", m5, 220.0, 5000.0),
        ):
            row = {
                "frame": 0,
                "time_s": 0.0,
                "x_px": 1000.0 if (detected and has_x) else None,
                "y_px": valid_y if (detected and has_y) else None,
                "area_px": valid_area if (detected and has_area) else None,
                "detected": detected,
            }
            track_path = write_track_csv([row], name="%s_%s.csv" % (tag, name))

            rows = module.read_track_csv(track_path)
            module.add_valid_flags(rows)
            # 缺字段的行若仍被误判 valid，这里会在 project_point() 处抛 TypeError
            module.add_projection(rows)

            expected_valid = detected and has_x and has_y and has_area
            assert rows[0]["valid"] is expected_valid, (tag, name)
            assert (rows[0]["s_px"] is not None) is expected_valid, (tag, name)


# ============================================================
# 非有限 x_px 的 gate 缺口（Phase 2B-5A，TEST 19 / TEST 20）
# 保护对象：src/displacement.py、src/dynamic_displacement.py —— is_valid_frame()
# 不变量：detected=True 时 x/y/area 必须是可用于计算的有限数值；
#         任何不可用值（None / NaN / inf / -inf）都必须在 gate 层判 invalid。
# ============================================================


_NON_FINITE_VALUES = [float("nan"), float("inf"), float("-inf")]


@pytest.mark.parametrize(
    "module, valid_y_px, valid_area_px",
    [(m4, 450.0, 3000.0), (m5, 220.0, 5000.0)],
    ids=["M4", "M5"],
)
def test_detected_true_non_finite_x_px_is_invalid(module, valid_y_px, valid_area_px):
    """TEST 19 —— detected=True 但 x_px 为 NaN / inf / -inf：必须判 invalid（M4 与 M5 都锁定）。

    Phase 2B-5A 修复的缺口：gate 只在 x_px is None 时判 invalid，却从不校验 x_px 是否有限。
    NaN / inf / -inf 会绕过 None 守卫，而且两个区间比较（area / y）都不涉及 x_px，
    于是被错误放行成 valid=True，随后 project_point() 才抛 ValueError。

    Case A / B / C（M4）+ Case D / E / F（M5）：x_px = NaN / inf / -inf 全部无效。
    同时锁定“修复不误伤”：
        - detected=True + 有限 x/y/area -> valid=True（合法输入行为不变）；
        - detected=False + x/y/area 全 None -> valid=False（合法未检测语义不变，
          NaN 与 None 绝不混为一谈）。
    """
    # Cases A–F：x_px = NaN / inf / -inf 全部必须 invalid
    for bad_x in _NON_FINITE_VALUES:
        assert (
            module.is_valid_frame(True, bad_x, valid_y_px, valid_area_px) is False
        ), bad_x

    # 同一条不变量：detected=True 时 y_px / area_px 也必须是有限数值
    # （这两项此前已因区间比较自然判 invalid，此处锁定不被回退）
    assert module.is_valid_frame(True, 1000.0, float("nan"), valid_area_px) is False
    assert module.is_valid_frame(True, 1000.0, float("inf"), valid_area_px) is False
    assert module.is_valid_frame(True, 1000.0, valid_y_px, float("nan")) is False
    assert module.is_valid_frame(True, 1000.0, valid_y_px, float("inf")) is False

    # 不误伤：正常有限 x/y/area 仍必须 valid=True
    assert module.is_valid_frame(True, 1000.0, valid_y_px, valid_area_px) is True

    # 不误伤：detected=False + 全 None 仍属合法未检测（valid=False，但读取不报错）
    assert module.is_valid_frame(False, None, None, None) is False


def test_nan_x_px_is_not_sent_into_projection(write_track_csv):
    """TEST 20 —— 真实链路 read_track_csv -> add_valid_flags -> add_projection：
    x_px=NaN 的行必须被判 invalid，不会再因错误的 valid=True 进入投影并抛下游异常。

    缺陷风险链条：x_px=NaN -> 原先 valid=True -> project_point() -> ValueError。
    修复后：x_px=NaN -> valid=False -> 不进入投影有效路径（s_px 保持 None）。
    """
    nan = float("nan")
    for name, module, valid_y, valid_area in (
        ("M4", m4, 450.0, 3000.0),
        ("M5", m5, 220.0, 5000.0),
    ):
        track_path = write_track_csv(
            [
                {
                    "frame": 0,
                    "time_s": 0.0,
                    "x_px": nan,
                    "y_px": valid_y,
                    "area_px": valid_area,
                    "detected": True,
                }
            ],
            name="nonfinite_nan_%s.csv" % name,
        )

        rows = module.read_track_csv(track_path)
        module.add_valid_flags(rows)
        # 修复前：valid=True -> project_point((nan, y)) -> ValueError（测试在此报错）
        module.add_projection(rows)

        assert rows[0]["valid"] is False, name
        assert rows[0]["s_px"] is None, name


# ============================================================
# M3 时间轴一致性（Phase 2B-3D-R，TEST 18）
# 保护对象：src/video_tracker.py —— check_csv_data() 的 time_s / frame / fps 一致性检查。
# 当前项目时间定义：time_s = frame_index / fps（frame 从 0 开始）。
# 关键设计：fps 必须来自真实视频读取（外部锚点），不得从待验证的 CSV 反推；
# 否则整条时间轴被统一缩放（真实 24 fps 却按 30 fps 写入）时无法检出。
# ============================================================


def _minimal_m3_rows(count=6, fps=24.0, time_override=None):
    """
    构造最小合法 M3 track 行：frame 从 0 连续、time_s = frame / fps、
    detected=True 且 x / y / area 均有效。time_override 用于“只改 time_s”。
    """
    rows = []
    for index in range(count):
        time_s = index / fps
        if time_override and index in time_override:
            time_s = time_override[index]
        rows.append(
            {
                "frame": index,
                "time_s": time_s,
                "x_px": 1000.0 + index,
                "y_px": 450.0,
                "area_px": 3000.0,
                "detected": True,
            }
        )
    return rows


def _time_axis_check(checks):
    """从 checks 里取出唯一一项与时间轴一致性相关的检查结果。"""
    matches = [ok for description, ok in checks if "时间轴一致" in description]
    assert len(matches) == 1, checks
    return matches[0]


def test_m3_csv_time_axis_case_a_real_fps_matching_timeline_passes(write_track_csv):
    """TEST 18A —— 真实 24 fps + 正确 time_s（frame / 24）必须通过。"""
    rows = _minimal_m3_rows(count=6, fps=24.0)
    path = write_track_csv(rows, name="axis_caseA_legal.csv")

    checks, passed = check_csv_data(
        path, expected_rows=len(rows), frame_width=1920, frame_height=1080, fps=24.0
    )
    assert passed is True
    assert _time_axis_check(checks) is True


def test_m3_csv_time_axis_case_b_wrong_fps_timeline_is_rejected(write_track_csv):
    """TEST 18B（关键回归）—— 真实 24 fps，但 CSV 整条时间轴按 30 fps 写入，必须判未通过。

    frame 1 写成 1/30 ≈ 0.033333，而真实应为 1/24 ≈ 0.041667。
    这一条证明：校验真正锚定到外部视频 FPS，能抓住“整条时间轴被统一缩放”的错误，
    而不是只看 CSV 自身是否自洽（CSV 按 30 fps 写入时其内部仍然自洽）。
    """
    rows = _minimal_m3_rows(count=6, fps=30.0)  # 错误：真实视频是 24 fps
    path = write_track_csv(rows, name="axis_caseB_scaled.csv")

    checks, passed = check_csv_data(
        path, expected_rows=len(rows), frame_width=1920, frame_height=1080, fps=24.0
    )
    assert passed is False
    assert _time_axis_check(checks) is False


def test_m3_csv_time_axis_case_c_single_bad_time_is_rejected(write_track_csv):
    """TEST 18C —— 单行 time_s 被明显改错（frame=3 应约 0.125，却写成 1.5）必须判未通过。"""
    rows = _minimal_m3_rows(count=6, fps=24.0, time_override={3: 1.5})
    path = write_track_csv(rows, name="axis_caseC_bad_time.csv")

    checks, passed = check_csv_data(
        path, expected_rows=len(rows), frame_width=1920, frame_height=1080, fps=24.0
    )
    assert passed is False
    assert _time_axis_check(checks) is False


def test_m3_csv_time_axis_case_d_correct_csv_wrong_qc_fps_is_rejected(write_track_csv):
    """TEST 18D —— CSV 时间轴正确（frame / 24），但 QC 传入错误的 fps=30，必须判未通过。

    用于确认：QC 真的依赖外部 FPS 锚点，而不是只要 CSV 自洽就放行。
    """
    rows = _minimal_m3_rows(count=6, fps=24.0)  # CSV 本身正确
    path = write_track_csv(rows, name="axis_caseD_wrong_qc_fps.csv")

    checks, passed = check_csv_data(
        path, expected_rows=len(rows), frame_width=1920, frame_height=1080, fps=30.0
    )
    assert passed is False
    assert _time_axis_check(checks) is False


def test_m3_csv_time_axis_case_e_real_baseline_csv_passes():
    """TEST 18E —— 当前正式 M3 CSV（1920x1080 / 24 fps）在 fps=24.0 下必须继续通过。

    只读取 results/EXP-002-VIDEO-001_track.csv，不修改它，也不重新运行 demo。
    """
    csv_path = (
        Path(__file__).resolve().parents[1]
        / "results"
        / "EXP-002-VIDEO-001_track.csv"
    )
    assert csv_path.exists(), csv_path

    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        data_row_count = sum(1 for _ in csv_file) - 1  # 去掉表头

    checks, passed = check_csv_data(
        csv_path,
        expected_rows=data_row_count,
        frame_width=1920,
        frame_height=1080,
        fps=24.0,
    )
    assert passed is True
    assert _time_axis_check(checks) is True


def test_m3_csv_time_axis_without_fps_is_unverifiable(write_track_csv):
    """TEST 18F —— 未提供真实 fps（fps=None）时，时间轴检查必须明确判“无法验证”，不得放行。

    核心原则：绝不能偷偷从 CSV 自身估计 FPS 后把时间轴检查判通过。
    """
    rows = _minimal_m3_rows(count=6, fps=24.0)  # CSV 本身完全合法
    path = write_track_csv(rows, name="axis_no_fps.csv")

    checks, passed = check_csv_data(
        path, expected_rows=len(rows), frame_width=1920, frame_height=1080
    )
    assert passed is False
    assert _time_axis_check(checks) is False
    labels = [description for description, _ in checks if "时间轴一致" in description]
    assert "无法验证" in labels[0]

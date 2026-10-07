"""
VisionMotion —— M4 / M5 入口退出码契约测试（Phase 5-2 Step 3）

保护对象：
    1. demo/run_m43_displacement.py 的 main()：0 = 全部预期实验成功；
       1 = 只要有一个实验失败 / 被阻断 / 预期 ds CSV 未落盘；
    2. demo/run_m52_dynamic_displacement.py 的 main()：0 / 1 的最小契约。

原则：
    - 不真的重跑完整位移实验：只把 demo 的输入输出依赖换成轻量 monkeypatch；
    - 只断言退出码（本轮新增的契约），不重复断言 src/ 内部算法；
    - 打印函数替换为 no-op，避免构造与退出码无关的完整 report 结构。
"""

import importlib.util
from pathlib import Path

from src import dynamic_displacement as m5_src

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_demo(module_name, file_name):
    """按文件路径导入 demo/ 下的入口脚本（demo/ 不是包，不能直接 import）。"""
    path = PROJECT_ROOT / "demo" / file_name
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m4 = _load_demo("vm_demo_run_m43_displacement", "run_m43_displacement.py")
m5 = _load_demo("vm_demo_run_m52_dynamic_displacement", "run_m52_dynamic_displacement.py")


# ============================================================
# 测试辅助
# ============================================================


def _make_report(ds_csv_path, ds_written=True):
    """
    构造 demo 的 main() 在判定退出码时真正读取的那几个字段。

    退出码只取决于 ds_written 与 ds CSV 是否真的在磁盘上，与统计 / 打印无关。
    """
    return {
        "video_name": "FAKE-EXP",
        "ds_csv_path": Path(ds_csv_path),
        "ds_written": ds_written,
    }


def _silence(monkeypatch, module, function_names):
    """把纯打印函数换成 no-op：既不产生测试噪音，也不需要构造完整 report 结构。"""
    for name in function_names:
        monkeypatch.setattr(module, name, lambda *args, **kwargs: None)


def _write_existing_ds_csv(tmp_path, name="ds.csv"):
    """造一个"已经落盘"的 ds CSV，返回它的路径。"""
    path = tmp_path / name
    path.write_text("frame,time_s\n0,0.0\n", encoding="utf-8")
    return path


def _make_track_summary(integrity, processed_frames=1766):
    """构造 M5 的 main() 会读取的最小 track_summary。"""
    return {
        "track_integrity": integrity,
        "processed_frames": processed_frames,
        "sha256_before": "0" * 64,
        "sha256_after": "0" * 64,
    }


def _allow_all_experiments(monkeypatch, module, report_factory):
    """冻结常量自检通过 + 每个实验都返回 report_factory 给出的报告。"""
    monkeypatch.setattr(module, "check_calibration_constants",
                        lambda: ([("常量自检", True)], True))
    monkeypatch.setattr(module, "run_one_experiment", report_factory)


# ============================================================
# M4：0 = 全部预期实验成功完成
# ============================================================


def test_m4_main_returns_0_when_all_experiments_succeed(tmp_path, monkeypatch):
    """三个实验都成功、且预期 ds CSV 都已落盘 -> 退出码 0。"""
    ds_file = _write_existing_ds_csv(tmp_path)
    visited = []

    def run_one(video_name):
        visited.append(video_name)
        return _make_report(ds_file)

    _allow_all_experiments(monkeypatch, m4, run_one)
    _silence(monkeypatch, m4, ["print_summary", "print_final_summary"])

    assert m4.main() == 0
    assert visited == list(m4.EXPERIMENT_NAMES)  # 三个实验都真的被执行了


# ============================================================
# M4：1 = 存在阻断性失败（含"一个失败不能因为其它成功而变回 0"）
# ============================================================


def test_m4_main_returns_1_when_one_experiment_fails_while_others_succeed(tmp_path, monkeypatch):
    """实验 A 成功、实验 B 失败（输入视频不存在 -> 返回 None）、实验 C 成功 -> 整体仍是 1。"""
    ds_file = _write_existing_ds_csv(tmp_path)
    failing = m4.EXPERIMENT_NAMES[1]

    def run_one(video_name):
        if video_name == failing:
            return None
        return _make_report(ds_file)

    _allow_all_experiments(monkeypatch, m4, run_one)
    _silence(monkeypatch, m4, ["print_summary", "print_final_summary"])

    assert m4.main() == 1


def test_m4_main_returns_1_when_integrity_not_evaluated_skips_experiment(tmp_path, monkeypatch):
    """上游轨迹完整性 not_evaluated（用户中断）导致实验被跳过 -> 退出码 1。"""
    ds_file = _write_existing_ds_csv(tmp_path)
    skipped_name = m4.EXPERIMENT_NAMES[0]

    def run_one(video_name):
        if video_name == skipped_name:
            return {
                "video_name": video_name,
                "track_integrity": "not_evaluated",
                "skipped": True,
            }
        return _make_report(ds_file)

    _allow_all_experiments(monkeypatch, m4, run_one)
    _silence(monkeypatch, m4, ["print_summary", "print_final_summary"])

    assert m4.main() == 1


def test_m4_main_returns_1_when_expected_ds_csv_not_landed(tmp_path, monkeypatch):
    """实验流程跑完、report 认为已写出 ds CSV，但磁盘上找不到该文件 -> 退出码 1。"""
    never_written = tmp_path / "not_on_disk.csv"  # 故意不创建

    _allow_all_experiments(
        monkeypatch, m4, lambda video_name: _make_report(never_written, ds_written=True)
    )
    _silence(monkeypatch, m4, ["print_summary", "print_final_summary"])

    assert m4.main() == 1


def test_m4_main_returns_1_when_frozen_constant_check_fails(monkeypatch):
    """冻结常量自检未通过 -> 直接退出码 1，且不执行任何实验。"""
    visited = []
    monkeypatch.setattr(m4, "check_calibration_constants",
                        lambda: ([("常量自检", False)], False))
    monkeypatch.setattr(m4, "run_one_experiment",
                        lambda video_name: visited.append(video_name) or None)
    _silence(monkeypatch, m4, ["print_summary", "print_final_summary"])

    assert m4.main() == 1
    assert visited == []


# ============================================================
# M5：0 = 实验成功完成且 ds CSV 已落盘
# ============================================================


def test_m5_main_returns_0_when_experiment_succeeds(tmp_path, monkeypatch):
    """完整轨迹 + 位移计算成功 + 预期 ds CSV 已落盘 -> 退出码 0。"""
    video = tmp_path / "EXP-004-DYNAMIC-001.mp4"
    video.write_bytes(b"fake video placeholder")
    ds_file = _write_existing_ds_csv(tmp_path, "EXP-004_ds.csv")

    monkeypatch.setattr(m5, "VIDEO_PATH", video)
    monkeypatch.setattr(m5, "track_video",
                        lambda *args, **kwargs: _make_track_summary("complete"))
    monkeypatch.setattr(m5, "run_experiment",
                        lambda *args, **kwargs: _make_report(ds_file))
    _silence(monkeypatch, m5, ["print_frozen_constants", "print_summary", "print_final_checks"])

    assert m5.main() == 0


# ============================================================
# M5：1 = 失败 / 被阻断 / 预期 ds CSV 未生成
# ============================================================


def test_m5_main_returns_1_when_input_video_missing(tmp_path, monkeypatch):
    """输入视频不存在 -> 退出码 1，且不进入逐帧追踪。"""
    visited = []
    monkeypatch.setattr(m5, "VIDEO_PATH", tmp_path / "does_not_exist.mp4")
    monkeypatch.setattr(m5, "track_video",
                        lambda *args, **kwargs: visited.append("track_video") or None)
    _silence(monkeypatch, m5, ["print_frozen_constants"])

    assert m5.main() == 1
    assert visited == []


def test_m5_main_returns_1_when_integrity_not_evaluated(tmp_path, monkeypatch):
    """上游轨迹完整性 not_evaluated（用户中断）-> 跳过位移计算，退出码 1。"""
    video = tmp_path / "EXP-004-DYNAMIC-001.mp4"
    video.write_bytes(b"fake video placeholder")
    visited = []

    monkeypatch.setattr(m5, "VIDEO_PATH", video)
    monkeypatch.setattr(
        m5, "track_video",
        lambda *args, **kwargs: _make_track_summary("not_evaluated", processed_frames=3),
    )
    monkeypatch.setattr(m5, "run_experiment",
                        lambda *args, **kwargs: visited.append("run_experiment") or None)
    _silence(monkeypatch, m5, ["print_frozen_constants", "print_summary", "print_final_checks"])

    assert m5.main() == 1
    assert visited == []  # not_evaluated 时必须跳过位移计算


def test_m5_main_returns_1_when_expected_ds_csv_not_generated(tmp_path, monkeypatch):
    """EXP-004 的正式 ds CSV 未生成 -> 退出码 1（M5 的该文件是预期产物）。"""
    video = tmp_path / "EXP-004-DYNAMIC-001.mp4"
    video.write_bytes(b"fake video placeholder")

    monkeypatch.setattr(m5, "VIDEO_PATH", video)
    monkeypatch.setattr(m5, "track_video",
                        lambda *args, **kwargs: _make_track_summary("complete"))
    monkeypatch.setattr(
        m5, "run_experiment",
        lambda *args, **kwargs: _make_report(tmp_path / "never.csv", ds_written=False),
    )
    _silence(monkeypatch, m5, ["print_frozen_constants", "print_summary", "print_final_checks"])

    assert m5.main() == 1


# ============================================================
# M5 run_experiment()：冻结常量自检失败时不得写入 ds CSV（Phase 5-2 Step 4）
#
# 原缺陷：run_experiment() 先调用 build_ds_from_track_csv()（其内部会写出 _ds.csv），
# 之后才判断 constant_passed 并打印"不生成 ds CSV"——文件已落盘，提示却相反。
# ============================================================


def test_m5_run_experiment_does_not_touch_ds_chain_when_constants_fail(
    write_track_csv, tmp_path, monkeypatch
):
    """
    常量自检失败 -> run_experiment() 必须直接返回：
    不调用 build_ds_from_track_csv()，且目标 _ds.csv 一定不存在。
    """
    track_csv = write_track_csv(
        [
            {
                "frame": index,
                "time_s": index / 30.0,
                "x_px": 800.0 + index,
                "y_px": 220.0,
                "area_px": 5000.0,
                "detected": True,
            }
            for index in range(3)
        ]
    )
    ds_csv = tmp_path / "must_not_exist_ds.csv"

    monkeypatch.setattr(m5_src, "check_calibration_constants",
                        lambda: ([("常量自检", False)], False))

    def explode(*args, **kwargs):
        raise AssertionError("常量自检未通过时不允许调用 build_ds_from_track_csv()")

    monkeypatch.setattr(m5_src, "build_ds_from_track_csv", explode)

    report = m5_src.run_experiment(track_csv, ds_csv, "FAKE-EXP")

    assert report["constant_passed"] is False
    assert report["ds_written"] is False
    assert not ds_csv.exists()
    # 返回的 report 仍与正常路径同构（打印层需要的字段都在，不会 KeyError）
    for key in ("video_name", "track_csv_path", "ds_csv_path", "track_frame_count",
                "s0_report", "summary", "turning",
                "constant_checks", "constant_passed", "checks", "passed"):
        assert key in report
    assert report["track_frame_count"] == 3
    assert report["summary"]["frame_count"] == 3


def test_m5_run_experiment_builds_ds_chain_when_constants_pass(tmp_path, monkeypatch):
    """常量自检通过 -> 正常进入 ds 数据链（build_ds_from_track_csv() 被调用一次），语义不变。"""
    calls = []

    def fake_build(track_csv_path, ds_csv_path, video_name=""):
        calls.append(video_name)
        return {
            "video_name": video_name,
            "track_csv_path": Path(track_csv_path),
            "ds_csv_path": Path(ds_csv_path),
            "track_frame_count": 0,
            "s0_report": {"ok": False, "s0": None},
            "summary": {},
            "turning": {},
            "rows": [],
            "ds_written": False,
            "checks": [],
            "passed": False,
        }

    monkeypatch.setattr(m5_src, "check_calibration_constants",
                        lambda: ([("常量自检", True)], True))
    monkeypatch.setattr(m5_src, "build_ds_from_track_csv", fake_build)

    report = m5_src.run_experiment(tmp_path / "t.csv", tmp_path / "d.csv", "FAKE-EXP")

    assert calls == ["FAKE-EXP"]
    assert report["constant_passed"] is True
    assert report["ds_written"] is False
    assert report["checks"] == []
    assert report["passed"] is False


# ============================================================
# M4 / M5 的覆盖提示（Phase 5-2 Step 5）
#
# 行为契约：目标文件不存在 -> 不打印覆盖警告；
#           目标文件已存在 -> 写盘前打印 [警告]，然后继续正常执行。
# 仍然是"默认允许重算"，不拒绝覆盖、不交互、不新增命令行参数。
# ============================================================


def _prepare_m4_tmp_dirs(tmp_path, video_name):
    """把 M4 的 DATA_DIR / RESULT_DIR 指向 tmp_path，并放一个假的输入视频。"""
    data_dir = tmp_path / "data"
    result_dir = tmp_path / "results"
    data_dir.mkdir()
    result_dir.mkdir()
    (data_dir / ("%s.mp4" % video_name)).write_bytes(b"fake video placeholder")
    return data_dir, result_dir


def test_m4_run_one_experiment_warns_before_overwriting_existing_outputs(
    tmp_path, monkeypatch, capsys
):
    """目标 track CSV 已存在 -> 写盘之前打印覆盖警告，并且继续跑完整流程。"""
    video_name = m4.EXPERIMENT_NAMES[0]
    data_dir, result_dir = _prepare_m4_tmp_dirs(tmp_path, video_name)
    existing_track_csv = result_dir / ("%s_track.csv" % video_name)
    existing_track_csv.write_text(
        "frame,time_s,x_px,y_px,area_px,detected\n", encoding="utf-8"
    )

    monkeypatch.setattr(m4, "DATA_DIR", data_dir)
    monkeypatch.setattr(m4, "RESULT_DIR", result_dir)

    calls = []
    monkeypatch.setattr(
        m4, "track_video",
        lambda *args, **kwargs: calls.append("track_video") or _make_track_summary("complete"),
    )
    monkeypatch.setattr(
        m4, "run_experiment",
        lambda *args, **kwargs: calls.append("run_experiment")
        or _make_report(tmp_path / "ds.csv", ds_written=False),
    )

    report = m4.run_one_experiment(video_name)

    captured = capsys.readouterr().out
    assert "[警告] 输出文件已存在，将重新写入冻结结果：" in captured
    assert str(existing_track_csv) in captured
    assert calls == ["track_video", "run_experiment"]  # 警告之后照常继续执行
    assert report is not None


def test_m4_run_one_experiment_is_silent_when_outputs_absent(tmp_path, monkeypatch, capsys):
    """目标文件都不存在 -> 不打印覆盖警告，流程照常执行。"""
    video_name = m4.EXPERIMENT_NAMES[0]
    data_dir, result_dir = _prepare_m4_tmp_dirs(tmp_path, video_name)

    monkeypatch.setattr(m4, "DATA_DIR", data_dir)
    monkeypatch.setattr(m4, "RESULT_DIR", result_dir)

    calls = []
    monkeypatch.setattr(
        m4, "track_video",
        lambda *args, **kwargs: calls.append("track_video") or _make_track_summary("complete"),
    )
    monkeypatch.setattr(
        m4, "run_experiment",
        lambda *args, **kwargs: calls.append("run_experiment")
        or _make_report(tmp_path / "ds.csv", ds_written=False),
    )

    report = m4.run_one_experiment(video_name)

    captured = capsys.readouterr().out
    assert "[警告]" not in captured
    assert calls == ["track_video", "run_experiment"]
    assert report is not None


def test_m5_main_warns_before_overwriting_existing_outputs(tmp_path, monkeypatch, capsys):
    """M5：目标文件已存在 -> 打印覆盖警告，并继续正常执行到退出码 0。"""
    video = tmp_path / "EXP-004-DYNAMIC-001.mp4"
    video.write_bytes(b"fake video placeholder")
    existing_track_csv = tmp_path / "EXP-004-DYNAMIC-001_track.csv"
    existing_track_csv.write_text(
        "frame,time_s,x_px,y_px,area_px,detected\n", encoding="utf-8"
    )
    existing_ds_csv = tmp_path / "EXP-004-DYNAMIC-001_ds.csv"
    existing_ds_csv.write_text("frame,time_s\n0,0.000000\n", encoding="utf-8")

    monkeypatch.setattr(m5, "VIDEO_PATH", video)
    monkeypatch.setattr(m5, "TRACK_CSV_PATH", existing_track_csv)
    monkeypatch.setattr(m5, "DS_CSV_PATH", existing_ds_csv)
    monkeypatch.setattr(m5, "OVERLAY_PATH", tmp_path / "EXP-004-DYNAMIC-001_overlay.mp4")
    monkeypatch.setattr(m5, "track_video",
                        lambda *args, **kwargs: _make_track_summary("complete"))
    monkeypatch.setattr(m5, "run_experiment",
                        lambda *args, **kwargs: _make_report(existing_ds_csv))
    _silence(monkeypatch, m5, ["print_frozen_constants", "print_summary", "print_final_checks"])

    exit_code = m5.main()

    captured = capsys.readouterr().out
    assert "[警告] 输出文件已存在，将重新写入冻结结果：" in captured
    assert str(existing_track_csv) in captured
    assert str(existing_ds_csv) in captured
    assert exit_code == 0  # 警告之后继续跑完，仍是正常的成功退出码

"""
VisionMotion —— Phase 5-1 轨迹完整性逻辑回归测试（Phase 5-2 Step 2）

保护对象：src/video_tracker.py 中 Phase 5-1 新增的轨迹完整性逻辑
    1. evaluate_track_integrity()：完整 / 存疑 / 未验证 三态判定；
    2. track_video()：完整性结论写进 summary，以及用户中断时保持 not_evaluated。

原则：
    - 不编码任何真实 MP4，也不读写 data/ 与 results/；全部使用轻量测试替身 + pytest tmp_path；
    - 替身只实现生产代码实际用到的行为（set / read / release），
      断言的是真实函数的输出，而不是在测试里重写一份相同判定公式；
    - 不修改任何 src/ 生产逻辑。
"""

import csv

import cv2
import numpy as np

from src import video_tracker as vt


# ============================================================
# 测试替身（只实现生产代码实际调用的最小行为）
# ============================================================


class FakeVideoCapture:
    """
    cv2.VideoCapture 的最小替身。

    只实现 evaluate_track_integrity() / track_video() 实际用到的三个方法：
        - read()    ：按给定帧序列依次吐帧；序列耗尽后返回 (False, None)；
        - set()     ：记录调用并返回 seek_set_ok；其后的一次 read() 用来模拟
                      “seek 到声明末帧后重新解码一次”这条独立证据；
        - release() ：只记录是否已释放。
    """

    def __init__(self, frames=(), seek_set_ok=True, seek_read_ok=True):
        self._frames = list(frames)
        self._seek_set_ok = seek_set_ok
        self._seek_read_ok = seek_read_ok
        self._seek_read_pending = False
        self._last_frame = object()  # 非 None 即代表“声明末帧可以再次解码”
        self.set_calls = []
        self.released = False

    def set(self, prop, value):
        self.set_calls.append((prop, value))
        self._seek_read_pending = True
        return self._seek_set_ok

    def read(self):
        if self._seek_read_pending:
            self._seek_read_pending = False
            if self._seek_read_ok:
                return True, self._last_frame
            return False, None
        if self._frames:
            return True, self._frames.pop(0)
        return False, None

    def release(self):
        self.released = True


class FakeVideoWriter:
    """cv2.VideoWriter 的最小替身：只记录写帧次数与是否 release。"""

    def __init__(self):
        self.frames_written = 0
        self.released = False

    def write(self, frame):
        self.frames_written += 1

    def release(self):
        self.released = True


# ============================================================
# 测试辅助
# ============================================================


def make_frame():
    """返回一张很小的合成 BGR 帧，只用于让 track_video() 走完尺寸与可视化分支。"""
    return np.zeros((48, 64, 3), dtype=np.uint8)


def patch_track_video_dependencies(monkeypatch, cap, video_info, writer, detect):
    """
    把 track_video() 的 4 个外部依赖换成替身，避免真实视频 / 文件 / 编码器：
        compute_sha256 / open_video / open_overlay_writer / detect_marker
    只替换依赖，不触碰任何生产逻辑。
    """
    monkeypatch.setattr(vt, "compute_sha256", lambda path: "0" * 64)
    monkeypatch.setattr(vt, "open_video", lambda path: (cap, video_info))
    monkeypatch.setattr(vt, "open_overlay_writer",
                        lambda path, fps, frame_size: (writer, "mp4v"))
    monkeypatch.setattr(vt, "detect_marker", detect)


def read_csv_rows(csv_path):
    """按 M3 的写法读回 CSV，返回全部行（含表头）。"""
    with open(csv_path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))


# ============================================================
# A. complete + summary 报告字段
# ============================================================


def test_track_video_reports_complete_integrity_and_summary_fields(tmp_path, monkeypatch):
    """
    正常完整轨迹：未中断、声明帧数有效、已处理帧数达到声明值、seek 后末帧读取成功
    -> summary["track_integrity"] == "complete"，且相关报告字段与本次处理一致。
    """
    frame_count = 6
    cap = FakeVideoCapture(
        frames=[make_frame() for _ in range(frame_count)],
        seek_set_ok=True,
        seek_read_ok=True,
    )
    writer = FakeVideoWriter()
    video_info = {
        "fps": 30.0,
        "frame_count": frame_count,
        "orientation_meta": 0.0,
        "orientation_auto": True,
    }
    patch_track_video_dependencies(
        monkeypatch, cap, video_info, writer,
        lambda frame: {"success": False, "mask": None},
    )

    summary = vt.track_video(
        tmp_path / "video.mp4", tmp_path / "track.csv", tmp_path / "overlay.mp4"
    )

    assert summary is not None
    assert summary["track_integrity"] == "complete"
    assert summary["interrupted"] is False
    assert summary["declared_frame_count"] == frame_count
    assert summary["processed_frames"] == frame_count
    assert summary["detected_frames"] == 0
    assert summary["missed_frames"] == frame_count
    assert summary["overlay_ok"] is True

    # complete 结论确实来自“seek 到声明末帧（frame_count - 1）”这一次独立证据
    assert cap.set_calls == [(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)]
    assert cap.released is True
    assert writer.released is True

    # CSV 逐帧写满：表头 + 每帧一行
    rows = read_csv_rows(summary["csv_path"])
    assert len(rows) == frame_count + 1
    assert [int(row[0]) for row in rows[1:]] == list(range(frame_count))


# ============================================================
# B. suspect：数量不足 + 末帧不可读，两个证据一致指向“不完整”
# ============================================================


def test_evaluate_track_integrity_suspect_when_short_and_last_frame_unreadable():
    """已处理帧数 < 声明值，且 seek 本身失败 -> suspect（证据一致指向完整性存疑）。"""
    cap = FakeVideoCapture(seek_set_ok=False)

    status = vt.evaluate_track_integrity(
        cap, processed_frames=99, declared_frame_count=100
    )

    assert status == "suspect"
    # seek 目标必须是“声明末帧”（declared - 1）；set 失败后不再调用 read()
    assert cap.set_calls == [(cv2.CAP_PROP_POS_FRAMES, 99)]


# ============================================================
# C / D. unverified：两类证据互相矛盾
# ============================================================


def test_evaluate_track_integrity_unverified_when_short_but_last_frame_readable():
    """已处理帧数 < 声明值，但声明末帧能再次解码：两个证据互相矛盾 -> unverified。"""
    cap = FakeVideoCapture(seek_set_ok=True, seek_read_ok=True)

    assert vt.evaluate_track_integrity(cap, 99, 100) == "unverified"


def test_evaluate_track_integrity_unverified_when_reached_but_last_frame_unreadable():
    """已处理帧数 >= 声明值，但声明末帧无法再次解码：两个证据互相矛盾 -> unverified。"""
    cap = FakeVideoCapture(seek_set_ok=True, seek_read_ok=False)

    assert vt.evaluate_track_integrity(cap, 100, 100) == "unverified"


# ============================================================
# E. 非法 / 无效的声明帧数
# ============================================================


def test_evaluate_track_integrity_unverified_when_declared_frame_count_invalid():
    """声明帧数 <= 0：没有可对照的基准 -> 判据不可用，直接 unverified（连 seek 都不做）。"""
    for declared in (0, -1, -100):
        cap = FakeVideoCapture(seek_set_ok=True, seek_read_ok=True)

        assert vt.evaluate_track_integrity(cap, 0, declared) == "unverified"
        assert cap.set_calls == []


# ============================================================
# F. 用户中断：保持 not_evaluated，且不进行完整性 seek
# ============================================================


def test_track_video_keyboard_interrupt_marks_not_evaluated_without_seek(tmp_path, monkeypatch):
    """
    用户在逐帧处理中按 Ctrl+C：track_video() 必须捕获中断、保留已写出的数据，
    并保持 track_integrity == "not_evaluated"（不做完整性 seek、不给出 complete/suspect/unverified）。
    """
    cap = FakeVideoCapture(frames=[make_frame()], seek_set_ok=True, seek_read_ok=True)
    writer = FakeVideoWriter()
    video_info = {
        "fps": 30.0,
        "frame_count": 1,
        "orientation_meta": 0.0,
        "orientation_auto": True,
    }

    def interrupt_on_first_frame(frame):
        raise KeyboardInterrupt

    patch_track_video_dependencies(
        monkeypatch, cap, video_info, writer, interrupt_on_first_frame
    )

    summary = vt.track_video(
        tmp_path / "video.mp4", tmp_path / "track.csv", tmp_path / "overlay.mp4"
    )

    assert summary is not None
    assert summary["interrupted"] is True
    assert summary["track_integrity"] == "not_evaluated"
    # 中断路径不做完整性评估：没有 seek，也没有把本次运行伪装成三态中的任何一种
    assert cap.set_calls == []
    assert cap.released is True
    # CSV 仍然落盘（表头 + 中断前已处理的行；本用例在写入任何数据行之前中断）
    assert read_csv_rows(summary["csv_path"]) == [vt.CSV_FIELDNAMES]

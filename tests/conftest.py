"""
VisionMotion —— pytest 公共夹具（Phase 2B-2 最小自动化测试体系）

本文件只做三件事：
    1. 把项目根目录加入 sys.path，使测试可以 import src.*（与 demo/ 脚本同样做法）；
    2. 提供合成测试图夹具：在内存里用 HSV 指定色相块 -> 转 BGR，不生成任何图片文件；
    3. 提供 M3 track 行的构造与写入夹具：只写 pytest tmp_path，不碰 results/ 与 data/。

夹具保持简单；具体断言全部放在各测试文件里。
"""

import csv
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TRACK_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]


@pytest.fixture
def hsv_patch_image():
    """
    返回“合成 BGR 图像”的工厂函数。

    用法：hsv_patch_image(size_hw=(高, 宽), patches=[(hue, sat, val, x, y, 宽, 高), ...])
    图像先在 HSV 空间合成（便于精确指定红色色相 H≈5 / H≈175），再整体转成 BGR。
    """
    import cv2
    import numpy as np

    def _make(size_hw=(240, 320), patches=(), background_hsv=(0, 0, 0)):
        height, width = size_hw
        hsv = np.zeros((height, width, 3), dtype=np.uint8)
        hsv[:, :] = background_hsv
        for hue, sat, val, x, y, patch_w, patch_h in patches:
            hsv[y : y + patch_h, x : x + patch_w] = (hue, sat, val)
        return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    return _make


@pytest.fixture
def write_track_csv(tmp_path):
    """
    返回写 M3 track CSV 的工厂函数（严格 M3 表头与文本写法，只写 tmp_path）。
    """

    def _write(rows, name="track.csv"):
        path = Path(tmp_path) / name
        with open(path, "w", encoding="utf-8", newline="") as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            writer.writerow(TRACK_FIELDNAMES)
            for row in rows:
                writer.writerow(
                    [
                        "%d" % row["frame"],
                        "%.6f" % row["time_s"],
                        "" if row["x_px"] is None else "%.2f" % row["x_px"],
                        "" if row["y_px"] is None else "%.2f" % row["y_px"],
                        "" if row["area_px"] is None else "%.1f" % row["area_px"],
                        "True" if row["detected"] else "False",
                    ]
                )
        return path

    return _write

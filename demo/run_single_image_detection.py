"""
VisionMotion —— M2.3 演示脚本

功能：读取一张真实图片，调用 src/marker_detector.py 检测红色标记，
      在终端打印检测结果，并把可视化结果保存到 results/ 目录。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\run_single_image_detection.py
"""

import sys
from pathlib import Path

import cv2
import numpy as np

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.marker_detector import detect_marker  # noqa: E402

# ============================================================
# 输入输出路径
# ============================================================

IMAGE_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-001-IMAGE-001.jpg"
RESULT_DIR = PROJECT_ROOT / "results"
OVERLAY_PATH = RESULT_DIR / "EXP-001-IMAGE-001_overlay.png"
MASK_PATH = RESULT_DIR / "EXP-001-IMAGE-001_mask.png"


def read_image(path):
    """
    读取一张图片。

    说明：Windows 上 cv2.imread 无法读取含中文的路径（本项目路径里有中文），
    所以先用 np.fromfile 把文件读成字节，再用 cv2.imdecode 解码。
    读取失败时返回 None。
    """
    file_bytes = np.fromfile(str(path), dtype=np.uint8)
    if file_bytes.size == 0:
        return None
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


def save_image(path, image):
    """
    保存一张图片。

    说明：与 read_image 同理，cv2.imwrite 在中文路径下会失败，
    所以先用 cv2.imencode 编码，再把字节写入文件。
    """
    success, encoded = cv2.imencode(path.suffix, image)
    if not success:
        return False
    encoded.tofile(str(path))
    return True


def draw_overlay(image_bgr, result):
    """
    在原图的副本上画出检测结果。

    画三样东西：外接矩形、目标中心点（圆圈 + 十字）、中心坐标文字。
    注意：这里操作的是副本，原图不会被修改。
    """
    overlay = image_bgr.copy()

    x, y, w, h = result["bbox"]
    cx = result["cx"]
    cy = result["cy"]
    center = (int(round(cx)), int(round(cy)))

    # 外接矩形（绿色）
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 3)

    # 中心点：圆圈 + 十字（绿色）
    cv2.circle(overlay, center, 12, (0, 255, 0), 3)
    cv2.drawMarker(overlay, center, (255, 0, 0), cv2.MARKER_CROSS, 40, 3)

    # 中心坐标文字（写在矩形上方，注意别超出图像顶部）
    text = "center = (%.1f, %.1f) px" % (cx, cy)
    text_y = y - 20
    if text_y < 30:
        text_y = y + h + 40
    cv2.putText(
        overlay,
        text,
        (x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return overlay


def main():
    # 1. 读取图片
    image = read_image(IMAGE_PATH)
    if image is None:
        print("错误：无法读取图像")
        return

    height, width = image.shape[0], image.shape[1]
    print("已读取图像：%s" % IMAGE_PATH)
    print("图像尺寸：宽 %d px，高 %d px" % (width, height))
    print()

    # 2. 检测红色标记
    result = detect_marker(image)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)

    if not result["success"]:
        print("检测失败：未检测到红色目标")
        # 保存掩膜，方便查看是哪个环节出了问题
        save_image(MASK_PATH, result["mask"])
        return

    # 3. 打印检测结果
    x, y, w, h = result["bbox"]
    print("检测成功")
    print("中心坐标：")
    print("x = %.1f px" % result["cx"])
    print("y = %.1f px" % result["cy"])
    print()
    print("面积：")
    print("%.1f px" % result["area"])
    print()
    print("外接矩形：")
    print("x = %d px" % x)
    print("y = %d px" % y)
    print("w = %d px" % w)
    print("h = %d px" % h)
    print()

    # 4. 生成并保存可视化结果
    overlay = draw_overlay(image, result)
    save_image(OVERLAY_PATH, overlay)
    save_image(MASK_PATH, result["mask"])

    print("已保存结果图片：")
    print(OVERLAY_PATH)
    print(MASK_PATH)


if __name__ == "__main__":
    main()

"""
VisionMotion —— 红色标记检测核心行为测试（Phase 2B-2，TEST 05 ~ TEST 07）

保护对象：src/marker_detector.py 的检测链
    合成 BGR 图 -> create_red_mask() -> find_target_contour() -> detect_marker()

原则：
    - 测试图全部在内存里用 numpy 合成（HSV 指定色相再转 BGR），不生成任何图片文件；
    - 只验证本项目自己的检测规则（双红区、最小面积、取最大轮廓、质心），不测试 OpenCV；
    - 固定使用红色系色相 H≈5 / H≈175，非红色用 H≈60 作反例。
"""

import numpy as np
import pytest

import src.marker_detector as md


def test_red_mask_covers_both_hsv_red_zones(hsv_patch_image):
    """TEST 05 —— HSV 双红区边界：H≈5 与 H≈175 都进入掩膜，非红色不进入。"""
    image = hsv_patch_image(
        size_hw=(240, 320),
        patches=[
            (5, 255, 255, 20, 20, 40, 40),  # 低色相端红色
            (175, 255, 255, 120, 20, 40, 40),  # 高色相端红色
            (60, 255, 255, 220, 20, 40, 40),  # 绿色：不是红色
        ],
    )

    mask = md.create_red_mask(image)

    assert mask.dtype == np.uint8
    assert mask.shape == image.shape[:2]
    assert set(np.unique(mask).tolist()) <= {0, 255}
    assert (mask[20:60, 20:60] == 255).all()  # H≈5 整块保留
    assert (mask[20:60, 120:160] == 255).all()  # H≈175 整块保留
    assert (mask[20:60, 220:260] == 0).all()  # 非红色被排除


def test_detector_rejects_no_red_and_sub_min_area_blob(hsv_patch_image):
    """TEST 06 —— 拒绝规则：无红色返回 success=False；面积低于 MIN_AREA 的红色块同样拒绝。"""
    # 纯灰图：没有任何红色，掩膜全零，detect_marker 返回失败（只带 mask）
    gray = hsv_patch_image(size_hw=(100, 120), background_hsv=(0, 0, 128))
    result = md.detect_marker(gray)
    assert result["success"] is False
    assert set(result) == {"success", "mask"}
    assert not result["mask"].any()

    # 一块红色小方块：轮廓面积低于 MIN_AREA 时直接拒绝（掩膜非空，但不是合格目标）
    side = int(md.MIN_AREA ** 0.5)  # 200 -> 14；方块外轮廓面积 13*13=169 < 200
    image = hsv_patch_image(
        size_hw=(120, 120), patches=[(5, 255, 255, 50, 50, side, side)]
    )
    result = md.detect_marker(image)
    assert result["success"] is False
    assert result["mask"].any()  # 掩膜里有红色，只是面积不够


def test_detector_picks_largest_red_blob_centroid_and_bbox(hsv_patch_image):
    """TEST 07 —— 多目标取最大轮廓：大红色块的质心与 bbox 正确，小红色块被忽略。"""
    image = hsv_patch_image(
        size_hw=(200, 340),
        patches=[
            (0, 255, 255, 70, 50, 60, 60),  # 大块：bbox (70, 50, 60, 60)
            (0, 255, 255, 250, 120, 20, 20),  # 小块：轮廓面积 19*19=361，仍大于 MIN_AREA
        ],
    )

    result = md.detect_marker(image)

    assert result["success"] is True
    assert result["bbox"] == (70, 50, 60, 60)
    # 实心方块的质心 = bbox 中心 = (99.5, 79.5)
    assert result["cx"] == pytest.approx(99.5, abs=1.0)
    assert result["cy"] == pytest.approx(79.5, abs=1.0)
    assert result["area"] == pytest.approx(59 * 59, abs=5.0)  # findContours 外轮廓面积
    assert result["mask"].dtype == np.uint8

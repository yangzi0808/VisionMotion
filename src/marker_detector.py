"""
VisionMotion —— 红色标记检测模块（M2.3 第一次业务代码实现）

本模块只负责“检测逻辑”，不做任何图像读写和文件保存。
检测流程严格按照已验收的 M2.2 设计：

    原图 -> BGR 转 HSV -> 红色双区间掩膜 -> 3x3 开运算
         -> 外部轮廓 -> 按面积取最大轮廓 -> 检查最小面积
         -> 轮廓矩 -> 目标中心 (cx, cy)

所有可调参数都集中在下面的“核心参数”区域，方便调试时统一修改。
"""

import cv2
import numpy as np

# ============================================================
# 核心参数（集中定义，便于调试）
# ============================================================

# 红色掩膜区间 1：色相靠近 0 度的一端
RED_LOWER_1 = np.array([0, 100, 70])
RED_UPPER_1 = np.array([10, 255, 255])

# 红色掩膜区间 2：色相靠近 179 度的一端
RED_LOWER_2 = np.array([170, 100, 70])
RED_UPPER_2 = np.array([179, 255, 255])

# 形态学开运算的核大小（3x3）
MORPH_KERNEL_SIZE = 3

# 候选轮廓的最小面积（单位：像素），小于它的候选直接忽略
MIN_AREA = 200


# ============================================================
# 检测函数
# ============================================================


def create_red_mask(image_bgr):
    """
    把 BGR 原图转换成红色二值掩膜。

    返回的掩膜是单通道 8 位图：红色区域为 255，其他区域为 0。
    """
    # 1. BGR 转 HSV，HSV 更容易把“红色”单独分离出来
    hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)

    # 2. 分别提取两个红色区间（红色在 HSV 色环上位于两端）
    mask_low = cv2.inRange(hsv_image, RED_LOWER_1, RED_UPPER_1)
    mask_high = cv2.inRange(hsv_image, RED_LOWER_2, RED_UPPER_2)

    # 3. 合并两个红色区间
    mask = cv2.bitwise_or(mask_low, mask_high)

    # 4. 3x3 开运算：先腐蚀再膨胀，去掉零散噪点但保留主体形状
    kernel = cv2.getStructuringElement(
        cv2.MORPH_RECT, (MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE)
    )
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    return mask


def find_target_contour(mask):
    """
    在掩膜中寻找红色目标的外轮廓。

    做法：找所有外部轮廓 -> 按面积从大到小排序 -> 取最大轮廓。
    如果没有任何轮廓，或者最大轮廓的面积小于 MIN_AREA，返回 None。
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None

    # 按面积排序，面积最大的排在最前面
    contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
    biggest_contour = contours_sorted[0]

    # 面积太小，说明不是我们想要的目标
    if cv2.contourArea(biggest_contour) < MIN_AREA:
        return None

    return biggest_contour


def calculate_centroid(contour):
    """
    用图像矩计算轮廓质心。

    返回 (cx, cy)；如果轮廓面积为 0（无法计算质心），返回 None。
    """
    moments = cv2.moments(contour)

    if moments["m00"] == 0:
        return None

    cx = moments["m10"] / moments["m00"]
    cy = moments["m01"] / moments["m00"]
    return cx, cy


def detect_marker(image_bgr):
    """
    完整的红色标记检测流程。

    输入：
        image_bgr —— 用 cv2.imread 读进来的 BGR 图像

    输出：
        一个字典。检测成功时：
            {
                "success": True,
                "cx": 目标中心 x（浮点数，单位像素）,
                "cy": 目标中心 y（浮点数，单位像素）,
                "area": 目标轮廓面积（浮点数，单位像素）,
                "bbox": 外接矩形 (x, y, w, h)（整数）,
                "contour": 目标轮廓,
                "mask": 红色二值掩膜,
            }
        检测失败时：
            {
                "success": False,
                "mask": 红色二值掩膜,
            }
    """
    mask = create_red_mask(image_bgr)

    contour = find_target_contour(mask)
    if contour is None:
        return {"success": False, "mask": mask}

    centroid = calculate_centroid(contour)
    if centroid is None:
        return {"success": False, "mask": mask}

    cx, cy = centroid
    area = cv2.contourArea(contour)
    x, y, w, h = cv2.boundingRect(contour)

    return {
        "success": True,
        "cx": cx,
        "cy": cy,
        "area": area,
        "bbox": (x, y, w, h),
        "contour": contour,
        "mask": mask,
    }

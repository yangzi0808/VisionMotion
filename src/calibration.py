"""
VisionMotion —— M4.3-1 像素尺度标定模块（纯数学计算）

本模块只做一件事：把“图像上的两个点 + 已知真实距离”换算成像素尺度 k 和方向 u。

它不读视频、不读图片、不保存文件、不使用 OpenCV，只依赖标准库 math，
因此可以单独用小脚本或单元测试验证。

坐标系（与实际视频追踪使用的坐标系完全一致）：
    点写作 (x, y)，单位是像素；原点在画面左上角，x 向右增大，y 向下增大。

本阶段固定定义：
    P1 = 10 cm 刻线的像素坐标（起点）
    P2 = 16 cm 刻线的像素坐标（终点）
    L_real_mm = 60.0 mm（10 cm 到 16 cm 的真实距离）
    L_pixel   = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    k         = L_pixel / L_real_mm     单位：像素/毫米（px/mm）
    1 / k     = L_real_mm / L_pixel     单位：毫米/像素（mm/px）
    u         = (P2 - P1) / |P2 - P1|   单位方向向量，方向约定“从 10 cm 指向 16 cm”

代码风格：普通函数 + 中文注释，不使用 class、不使用第三方库。
"""

import math


# ============================================================
# 内部工具函数：参数检查
# ============================================================


def _to_float(value, name):
    """
    把 value 转成 float，转不了就报错并说明是哪个参数出的问题。
    """
    # 布尔值虽然是数字的一种，但当坐标用没有意义，直接拒绝
    if isinstance(value, bool):
        raise TypeError("%s 不能是布尔值（True / False）" % name)

    try:
        return float(value)
    except (TypeError, ValueError):
        raise TypeError("%s 必须是数字，当前收到 %r" % (name, value))


def _check_point(point, name):
    """
    检查一个点是否合法，返回 (x, y) 两个 float。

    合法要求：
        1. 是长度为 2 的序列（例如 (x, y) 或 [x, y]）
        2. 两个元素都是数字
        3. 两个元素都是有限数值（不能是 nan 或 inf）
    """
    # 字符串虽然有长度，但不能当坐标用
    if isinstance(point, (str, bytes)) or not hasattr(point, "__len__"):
        raise TypeError("%s 必须是形如 (x, y) 的两个数字" % name)

    if len(point) != 2:
        raise ValueError(
            "%s 必须正好有 2 个数字（x 和 y），当前有 %d 个" % (name, len(point))
        )

    x = _to_float(point[0], "%s 的 x 坐标" % name)
    y = _to_float(point[1], "%s 的 y 坐标" % name)

    if not (math.isfinite(x) and math.isfinite(y)):
        raise ValueError("%s 必须是有限数值（不能是 nan 或 inf）" % name)

    return x, y


def _check_direction(direction):
    """
    从 direction 里取出 (ux, uy) 两个分量。

    允许两种写法：
        1. 字典 {"ux": ..., "uy": ...}，也就是 unit_direction() 的返回值
        2. 长度为 2 的序列，例如 (ux, uy)
    """
    if isinstance(direction, dict):
        if "ux" not in direction or "uy" not in direction:
            raise ValueError("direction 字典里必须同时有 ux 和 uy 两个键")
        ux = _to_float(direction["ux"], "direction['ux']")
        uy = _to_float(direction["uy"], "direction['uy']")
    else:
        ux, uy = _check_point(direction, "direction")

    if not (math.isfinite(ux) and math.isfinite(uy)):
        raise ValueError("direction 必须是有限数值（不能是 nan 或 inf）")

    return ux, uy


# ============================================================
# 对外接口
# ============================================================


def compute_scale(point1, point2, real_distance_mm):
    """
    计算像素尺度。

    参数：
        point1 —— P1（10 cm 刻线）的像素坐标，例如 (1043.8, 559.3)
        point2 —— P2（16 cm 刻线）的像素坐标，例如 (1403.0, 559.3)
        real_distance_mm —— P1 到 P2 的真实距离，单位毫米（本阶段固定 60.0）

    返回（字典）：
        pixel_distance —— L_pixel，两点之间的像素距离
        px_per_mm      —— k = L_pixel / real_distance_mm，单位 px/mm
        mm_per_px      —— 1/k = real_distance_mm / L_pixel，单位 mm/px

    报错情况：
        参数不是数字 / 点不是两个数字 -> TypeError
        点长度不对 / 两点重合 / real_distance_mm <= 0 -> ValueError
    """
    x1, y1 = _check_point(point1, "point1（P1）")
    x2, y2 = _check_point(point2, "point2（P2）")
    real_distance_mm = _to_float(real_distance_mm, "real_distance_mm")

    if not math.isfinite(real_distance_mm):
        raise ValueError("real_distance_mm 必须是有限数值（不能是 nan 或 inf）")

    if real_distance_mm <= 0:
        raise ValueError("real_distance_mm 必须大于 0，当前是 %g" % real_distance_mm)

    # L_pixel = sqrt((x2 - x1)^2 + (y2 - y1)^2)
    dx = x2 - x1
    dy = y2 - y1
    pixel_distance = math.hypot(dx, dy)

    # 两点重合就没有长度，尺度无从谈起
    if pixel_distance == 0:
        raise ValueError("P1 和 P2 不能重合（像素距离为 0），无法计算像素尺度")

    px_per_mm = pixel_distance / real_distance_mm
    mm_per_px = real_distance_mm / pixel_distance

    return {
        "pixel_distance": pixel_distance,
        "px_per_mm": px_per_mm,
        "mm_per_px": mm_per_px,
    }


def unit_direction(point1, point2):
    """
    计算单位方向向量 u：从 P1（10 cm）指向 P2（16 cm）。

    u = (P2 - P1) / |P2 - P1|，所以一定满足 ux^2 + uy^2 = 1。

    参数：
        point1 —— P1 的像素坐标
        point2 —— P2 的像素坐标

    返回（字典）：
        ux —— 水平方向分量
        uy —— 垂直方向分量（图像坐标系里 y 向下为正，所以尺子略微向下倾斜时 uy 为正）

    两个点重合时报 ValueError。
    """
    x1, y1 = _check_point(point1, "point1（P1）")
    x2, y2 = _check_point(point2, "point2（P2）")

    dx = x2 - x1
    dy = y2 - y1
    length = math.hypot(dx, dy)

    if length == 0:
        raise ValueError("P1 和 P2 不能重合（长度为 0），无法计算方向向量")

    return {"ux": dx / length, "uy": dy / length}


def project_point(point, direction):
    """
    把一个点投影到 direction 方向上，返回一维投影坐标（一个浮点数）。

    投影公式：s = x * ux + y * uy

    参数：
        point —— 像素坐标 (x, y)
        direction —— 方向向量，可以是 unit_direction() 返回的字典，
                     也可以是 (ux, uy) 这样的长度 2 序列

    说明：
        如果传入的 direction 不是单位向量（长度不是 1），函数会先把它归一化，
        这样返回的 s 才真的是“沿这个方向走了多远”的一维坐标。

    方向向量长度为 0 时报 ValueError。
    """
    x, y = _check_point(point, "point")
    ux, uy = _check_direction(direction)

    length = math.hypot(ux, uy)
    if length == 0:
        raise ValueError("direction 的长度不能为 0（必须是一个方向向量）")

    # 归一化，让 s 的单位和 point 一样是像素
    ux = ux / length
    uy = uy / length

    return x * ux + y * uy

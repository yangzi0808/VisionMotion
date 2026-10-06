"""
VisionMotion —— 标定数学单元测试（Phase 2B-2，TEST 01 ~ TEST 04）

保护对象：src/calibration.py 的三个对外函数
    compute_scale() / unit_direction() / project_point()

原则：
    - 只用可直接手算验证的例子（3-4-5 三角形等），不依赖 OpenCV / 视频 / 文件；
    - 非法输入用 pytest.raises() 明确到异常类型；
    - 不测试第三方库本身，也不复制实现公式。
"""

import math

import pytest

from src.calibration import compute_scale, project_point, unit_direction


def test_compute_scale_3_4_5():
    """TEST 01 —— compute_scale：3-4-5 输入得到 5 px / 1 px_per_mm / 1 mm_per_px。"""
    result = compute_scale((0, 0), (3, 4), 5.0)

    assert set(result) == {"pixel_distance", "px_per_mm", "mm_per_px"}
    assert result["pixel_distance"] == pytest.approx(5.0, abs=1e-12)
    assert result["px_per_mm"] == pytest.approx(1.0, abs=1e-12)
    assert result["mm_per_px"] == pytest.approx(1.0, abs=1e-12)
    assert result["px_per_mm"] * result["mm_per_px"] == pytest.approx(1.0, abs=1e-12)


def test_unit_direction_3_4():
    """TEST 02 —— unit_direction：(0,0)->(3,4) 得到 ux=0.6、uy=0.8、模长为 1。"""
    direction = unit_direction((0, 0), (3, 4))

    assert set(direction) == {"ux", "uy"}
    assert direction["ux"] == pytest.approx(0.6, abs=1e-12)
    assert direction["uy"] == pytest.approx(0.8, abs=1e-12)
    assert math.hypot(direction["ux"], direction["uy"]) == pytest.approx(1.0, abs=1e-12)


def test_project_point_normalizes_non_unit_direction():
    """TEST 03 —— project_point：非单位方向 (6,8) 先归一化，(3,4) 投影应为 5.0。"""
    s = project_point((3, 4), (6, 8))

    assert s == pytest.approx(5.0, abs=1e-12)
    # 同一方向写成单位向量或字典形式，结果必须一致
    assert project_point((3, 4), (0.6, 0.8)) == pytest.approx(5.0, abs=1e-12)
    assert project_point((3, 4), unit_direction((0, 0), (3, 4))) == pytest.approx(
        5.0, abs=1e-12
    )


def test_calibration_illegal_inputs():
    """TEST 04 —— 非法输入：布尔 / 字符串 / None / 长度错误 / nan / 重合点 / 非正距离 / 零方向。"""
    # 布尔值不能当坐标或距离用
    with pytest.raises(TypeError):
        compute_scale((True, 0), (3, 4), 5.0)
    with pytest.raises(TypeError):
        compute_scale((0, 0), (3, 4), True)
    with pytest.raises(TypeError):
        unit_direction((0, 0), (True, 4))

    # 不可转换为数字的字符串、None 不能当坐标用
    with pytest.raises(TypeError):
        compute_scale(("abc", "0"), (3, 4), 5.0)
    with pytest.raises(TypeError):
        compute_scale((0, 0), (3, 4), "60mm")
    with pytest.raises(TypeError):
        compute_scale(None, (3, 4), 5.0)

    # 长度错误（不是 2 个数字）
    with pytest.raises(ValueError):
        compute_scale((0, 0, 0), (3, 4), 5.0)
    with pytest.raises(ValueError):
        project_point((3, 4), (1.0,))
    with pytest.raises(ValueError):
        project_point((3, 4), {"ux": 1.0})  # 字典缺 uy 键

    # nan / inf 不是有限数值
    with pytest.raises(ValueError):
        compute_scale((float("nan"), 0.0), (3, 4), 5.0)
    with pytest.raises(ValueError):
        compute_scale((0, 0), (3, 4), float("inf"))
    with pytest.raises(ValueError):
        project_point((3, 4), (float("nan"), 1.0))

    # 两点重合：无法定义长度与方向
    with pytest.raises(ValueError):
        compute_scale((1, 1), (1, 1), 5.0)
    with pytest.raises(ValueError):
        unit_direction((1, 1), (1, 1))

    # real_distance_mm <= 0
    with pytest.raises(ValueError):
        compute_scale((0, 0), (3, 4), 0.0)
    with pytest.raises(ValueError):
        compute_scale((0, 0), (3, 4), -1.0)

    # 零方向向量
    with pytest.raises(ValueError):
        project_point((3, 4), (0.0, 0.0))
    with pytest.raises(ValueError):
        project_point((3, 4), {"ux": 0.0, "uy": 0.0})

"""
VisionMotion —— v1.0.0 Phase 2（VM-V1.0-P2-01）用户视频位移计算模块

本模块只做一件事：把任意一份 M3 格式的 track CSV 变成「像素位移 - 时间」数据。

位移定义（本阶段，纯像素、无标定）：

    1. 只使用 detected=True 且坐标可解析的有效点
    2. 取 CSV 中「第一个有效点」作为参考点 (x0, y0)
    3. 每个有效点相对参考点的像素位移：
           displacement_px = sqrt((x - x0)^2 + (y - y0)^2)

严格边界（本阶段只做像素位移，不越界）：

    - 只读 CSV，绝不修改 / 重写 CSV
    - 不做 mm 标定、不做方向投影、不做 valid gate、不做 s0、不做 FFT / 频率 / 周期
    - 不做平滑 / 插值 / 滤波 / 拟合，位移按有效点逐个直接计算
    - 不依赖 src/ 中任何冻结常量，也不改动 displacement.py / dynamic_displacement.py

输入（任意 track CSV，表头必须同时含这四列）：
    time_s, x_px, y_px, detected
典型来源：demo/run_video_tracking.py 生成的 results/<video_name>_track.csv

代码风格：普通函数 + 中文注释，不使用 class（仅定义一个错误类型）。
"""

import csv
import math
from pathlib import Path


# ============================================================
# 常量
# ============================================================

# track CSV 中本模块必需的列（对任何视频都通用，不绑定具体实验）
REQUIRED_FIELDS = ("time_s", "x_px", "y_px", "detected")


class UserDisplacementError(Exception):
    """
    本模块所有「可预期的用户错误」统一用这个类型抛出，便于调用方一次性捕获：

        - 输入文件不存在 / 不是文件
        - CSV 为空（只有表头，没有数据行）
        - CSV 缺少必需列
        - CSV 里没有任何 detected=True 的可用数据点
    """


# ============================================================
# 读取 track CSV
# ============================================================


def read_track_samples(csv_path):
    """
    读取任意 M3 格式的 track CSV，提取「有效位移样本」。

    参数：
        csv_path —— track CSV 路径（只读，绝不修改）

    返回 (samples, total_rows, skipped_rows)：
        samples       —— [(time_s, x_px, y_px), ...]，只含 detected=True 且三个字段
                         都能解析成有限数值的行，顺序与 CSV 一致（不排序）
        total_rows    —— 数据行总数（不含表头）
        skipped_rows  —— 被跳过的行数（detected=False，或字段缺失 / 非法）

    出错时抛 UserDisplacementError（文件不存在 / CSV 为空 / 缺列）。
    """
    csv_path = Path(csv_path)

    if not csv_path.is_file():
        raise UserDisplacementError("输入 CSV 不存在或不是文件：%s" % csv_path)

    samples = []
    skipped_rows = 0

    with open(csv_path, "r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = list(reader.fieldnames or [])

        # 1. 必需列检查：缺列时明确说明缺了哪些、实际有哪些，而不是后面抛 KeyError
        missing_fields = [name for name in REQUIRED_FIELDS if name not in fieldnames]
        if missing_fields:
            raise UserDisplacementError(
                "CSV 缺少必需列 %s；实际表头：%s"
                % (", ".join(missing_fields), ", ".join(fieldnames) or "(空)")
            )

        total_rows = 0
        for record in reader:
            total_rows += 1

            # 2. 只认 M3 规范写出的 "True"；其余（含 "False" / 空 / 非法文本）一律跳过
            detected_text = (record.get("detected") or "").strip()
            if detected_text != "True":
                skipped_rows += 1
                continue

            # 3. detected=True 也必须给出可解析的三个数值，否则跳过（绝不填 0）
            try:
                time_value = float((record.get("time_s") or "").strip())
                x_value = float((record.get("x_px") or "").strip())
                y_value = float((record.get("y_px") or "").strip())
            except ValueError:
                skipped_rows += 1
                continue

            if not (
                math.isfinite(time_value)
                and math.isfinite(x_value)
                and math.isfinite(y_value)
            ):
                skipped_rows += 1
                continue

            samples.append((time_value, x_value, y_value))

    # 4. 空 CSV（只有表头或完全为空）
    if total_rows == 0:
        raise UserDisplacementError(
            "CSV 为空（只有表头或没有任何数据行）：%s" % csv_path
        )

    return samples, total_rows, skipped_rows


# ============================================================
# 计算像素位移
# ============================================================


def compute_pixel_displacement_from_track_csv(csv_path):
    """
    读取任意 track CSV，计算每个有效点相对「第一个有效点」的像素位移。

    参数：
        csv_path —— 输入 track CSV（只读，不会被修改）

    返回 report 字典：
        csv_path              —— Path
        total_rows            —— 数据行总数（不含表头）
        valid_points          —— 有效点数（= len(time_s)）
        skipped_rows          —— 被跳过的行数
        x0 / y0               —— 参考点（第一个有效点的像素坐标）
        reference_time_s      —— 参考点对应的 time_s
        time_s                —— [float, ...]，每个有效点的时刻
        displacement_px       —— [float, ...]，与 time_s 一一对应的像素位移
        max_displacement_px   —— 最大位移
        final_displacement_px —— 最后一个有效点的位移

    出错时抛 UserDisplacementError（文件不存在 / CSV 为空 / 缺列 / 无有效点）。
    """
    csv_path = Path(csv_path)
    samples, total_rows, skipped_rows = read_track_samples(csv_path)

    # 有数据行，但没有任何可用点：明确说明，不返回空曲线
    if not samples:
        raise UserDisplacementError(
            "CSV 中没有 detected=True 的有效数据点（共 %d 行，全部被跳过）：%s"
            % (total_rows, csv_path)
        )

    # 参考点 = CSV 中第一个有效点（按文件顺序，不按时间排序）
    reference_time_s, x0, y0 = samples[0]

    time_list = []
    displacement_list = []
    for time_value, x_value, y_value in samples:
        time_list.append(time_value)
        displacement_list.append(math.hypot(x_value - x0, y_value - y0))

    return {
        "csv_path": csv_path,
        "total_rows": total_rows,
        "valid_points": len(samples),
        "skipped_rows": skipped_rows,
        "x0": x0,
        "y0": y0,
        "reference_time_s": reference_time_s,
        "time_s": time_list,
        "displacement_px": displacement_list,
        "max_displacement_px": max(displacement_list),
        "final_displacement_px": displacement_list[-1],
    }

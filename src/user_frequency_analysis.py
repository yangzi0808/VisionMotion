"""
VisionMotion —— v1.0.0 Phase 3（VM-V1.0-P3-01）用户视频频域分析模块

本模块只做一件事：把「像素位移 - 时间」序列做一次 FFT，得到单边幅值谱与主峰频率。

处理步骤（严格按本阶段设计，不越界）：

    1. 检查数据长度（两个列表必须等长、且点数足够）
    2. 检查时间采样间隔（必须严格递增、且近似均匀——rFFT 只对均匀采样成立）
    3. 去除平均值：signal = displacement - mean(displacement)
    4. 用 numpy.fft.rfft 做实数 FFT，得到 frequency / amplitude
    5. 返回 frequency / amplitude / peak_frequency / peak_amplitude / n_points / dt

严格边界（本阶段只做「一次 FFT」，不做别的）：

    - 不加窗函数、不做滤波、不做平滑、不做插值、不补零、不做 STFT
    - 不做 mm 标定（振幅单位就是 pixel）
    - 不依赖 src/ 中任何冻结常量，也不改动任何既有模块

幅度口径（重要，写报告时必须说明）：
    amplitude 是「单边幅值谱」：amplitude[k] = 2 * |X[k]| / N（DC 与 Nyquist 频点不乘 2）。
    因此当某个频率正好落在频率格点上时，amplitude 就等于该分量的峰值振幅（单位：pixel）。
    频率分辨率 df = 1 / (N * dt)；不落格点的频率会发生频谱泄漏（本阶段不做加窗抑制）。

代码风格：普通函数 + 中文注释，不使用 class（仅定义一个错误类型）。
"""

import numpy as np


# ============================================================
# 常量
# ============================================================

# 做一次有意义的 FFT 至少需要的点数：3 点以内 rfft 只有 DC / Nyquist，
# 没有可用的内部频点，找不到主峰，因此这里保守要求 4 点。
MIN_POINTS = 4

# 采样间隔均匀性判据：所有相邻 dt 必须落在
# dt_mean 的 DT_RTOL 相对误差 + DT_ATOL 绝对误差之内。
DT_RTOL = 1e-3
DT_ATOL = 1e-9


class UserFrequencyError(Exception):
    """
    本模块所有「可预期的用户错误」统一用这个类型抛出，便于调用方一次性捕获：

        - 输入不是两个可比较长度的序列
        - 两个列表长度不一致
        - 数据点太少（少于 MIN_POINTS）
        - 数值无法解析成浮点数 / 含 NaN / inf
        - 时间轴不是严格递增（存在重复或倒退）
        - 时间采样间隔不均匀（例如视频丢帧造成的空洞）
    """


# ============================================================
# 输入检查
# ============================================================


def _to_float_array(values, name):
    """
    把输入转成 float 类型的一维 numpy 数组；转不了或含非有限值时抛 UserFrequencyError。
    """
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError):
        raise UserFrequencyError("%s 必须是数值序列（无法解析成浮点数）" % name)

    if array.ndim != 1:
        raise UserFrequencyError("%s 必须是一维序列" % name)

    if not np.all(np.isfinite(array)):
        raise UserFrequencyError("%s 含 NaN / inf，无法做 FFT" % name)

    return array


def check_sampling_interval(time_values):
    """
    检查时间采样间隔，返回 (dt, dt_min, dt_max)。

    要求：
        1. time_s 严格递增（相邻间隔 > 0，不允许重复或倒退）
        2. 所有相邻间隔近似相等（均匀采样）——rFFT 的频率轴只在均匀采样下成立

    不满足时抛 UserFrequencyError，并在消息里给出实际的 dt 范围与非均匀步数，
    便于定位「视频丢帧」这类原因。dt 取所有相邻间隔的平均值。
    """
    diffs = np.diff(time_values)

    if diffs.size == 0:
        raise UserFrequencyError("时间轴至少需要 2 个点才能判断采样间隔")

    if np.any(diffs <= 0.0):
        raise UserFrequencyError(
            "time_s 必须严格递增（存在重复或倒退的时间点），无法确定采样间隔"
        )

    dt_mean = float(diffs.mean())
    dt_min = float(diffs.min())
    dt_max = float(diffs.max())

    uniform = np.allclose(diffs, dt_mean, rtol=DT_RTOL, atol=DT_ATOL)
    if not uniform:
        irregular_steps = int(np.count_nonzero(~np.isclose(
            diffs, dt_mean, rtol=DT_RTOL, atol=DT_ATOL
        )))
        raise UserFrequencyError(
            "时间采样间隔不均匀（rFFT 只对均匀采样成立）："
            "dt 范围 %.9g ~ %.9g s，非均匀步数 %d / %d；"
            "常见原因是视频丢帧造成的空洞。本阶段不做插值 / 重采样，"
            "请先确认该视频的检测是否出现丢失帧。"
            % (dt_min, dt_max, irregular_steps, int(diffs.size))
        )

    return dt_mean, dt_min, dt_max


# ============================================================
# FFT 计算
# ============================================================


def compute_fft_from_displacement(time_s, displacement_px):
    """
    对「像素位移 - 时间」序列做一次 FFT，返回单边幅值谱与主峰。

    参数：
        time_s          —— 时间序列（秒），必须严格递增且近似均匀
        displacement_px —— 与 time_s 等长的像素位移序列

    返回 dict：
        frequency        —— numpy 数组，rfft 的频率轴（Hz），范围 0 ~ Nyquist
        amplitude        —— numpy 数组，单边幅值谱（pixel），与 frequency 一一对应
        peak_frequency   —— 除 DC 外幅值最大处的频率（Hz）
        peak_amplitude   —— 对应的幅值（pixel）
        n_points         —— 参与 FFT 的点数
        dt               —— 采样间隔（秒），取相邻间隔平均值
        df               —— 频率分辨率 1 / (n_points * dt)（Hz）

    出错时抛 UserFrequencyError（长度不一致 / 点数太少 / 非数值 / 时间轴非法 /
    采样间隔不均匀）。
    """
    # 1. 检查数据长度
    try:
        n_time = len(time_s)
        n_displacement = len(displacement_px)
    except TypeError:
        raise UserFrequencyError(
            "输入必须是两个等长序列（time_s / displacement_px）"
        )

    if n_time != n_displacement:
        raise UserFrequencyError(
            "time_s 与 displacement_px 长度不一致：%d 个 vs %d 个"
            % (n_time, n_displacement)
        )

    if n_time < MIN_POINTS:
        raise UserFrequencyError(
            "数据点太少（%d 个，至少需要 %d 个）才能做有意义的 FFT"
            % (n_time, MIN_POINTS)
        )

    time_values = _to_float_array(time_s, "time_s")
    displacement_values = _to_float_array(displacement_px, "displacement_px")

    # 2. 检查时间采样间隔（必须均匀）
    dt, _dt_min, _dt_max = check_sampling_interval(time_values)

    # 3. 去除平均值（只去均值，不加窗、不滤波）
    signal = displacement_values - displacement_values.mean()

    # 4. 实数 FFT
    spectrum = np.fft.rfft(signal)
    frequency = np.fft.rfftfreq(n_time, d=dt)
    amplitude = np.abs(spectrum) * (2.0 / n_time)

    # DC 与 Nyquist 频点在单边谱里不乘 2（否则这两个频点的幅值会翻倍）
    amplitude[0] = np.abs(spectrum[0]) / n_time
    if n_time % 2 == 0:
        amplitude[-1] = np.abs(spectrum[-1]) / n_time

    # 5. 主峰：只看除 DC 以外的频点（已去均值，DC 理论上接近 0）
    peak_index = int(np.argmax(amplitude[1:])) + 1

    return {
        "frequency": frequency,
        "amplitude": amplitude,
        "peak_frequency": float(frequency[peak_index]),
        "peak_amplitude": float(amplitude[peak_index]),
        "n_points": int(n_time),
        "dt": float(dt),
        "df": float(1.0 / (n_time * dt)),
    }

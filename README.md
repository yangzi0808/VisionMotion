# VisionMotion

**基于计算机视觉的低成本、非接触式位移与振动监测项目**

## 1. 项目简介

VisionMotion 是一个基于计算机视觉的低成本、非接触式位移与振动监测项目：用普通摄像设备拍摄机械目标的运动视频，通过可解释的图像处理得到目标位置的时间序列，并据此测量振动周期与频率、做频域交叉验证，最后与基础物理模型作条件性对照。

核心链路：

```text
视频 → 目标视觉特征 → 位置时间序列 y₀(t) → 周期 T → 频率 f → FFT 交叉验证 → 标准 SHM 条件性参考
```

本项目**不使用深度学习或复杂跟踪算法**，重点在于：整条测量链路能够跑通、每一步都能解释清楚、结果可以复现。

📖 [正式用户使用指南](docs/USER_GUIDE.md)（面向第一次使用的普通用户）
🛠️ [开发者 / 科研使用指南](docs/DEVELOPER_GUIDE.md)（面向替换数据、复现实验与二次开发）
🎓 [源码学习课程索引](docs/learning/COURSE_INDEX.md)（面向源码与课程化学习）

## 2. 为什么做这个项目

- 普通摄像头的视频里，能否提取出**可重复**的运动位置特征？
- 如何从像素位置序列中测量出振动的**周期与频率**？
- 如何用独立的频域方法（FFT）对时域测量做**交叉验证**？
- 如何把视觉测量结果与基础物理模型（质量—弹簧简谐振动）联系起来，并**诚实说明差异与证据边界**？

## 3. 当前项目状态

**M0–M6.3 已完成**，当前处于最终交付整理阶段。

| 里程碑 | 内容 | 状态 |
| --- | --- | --- |
| M2 | 单张图片视觉目标检测 | 已完成 |
| M3 | 视频目标逐帧跟踪与时序坐标提取 | 已完成 |
| M4 | 静态 px/mm 标定与静态位移测量 | 已完成 |
| M5 | 动态位移与运动轨迹实验 | 已完成 |
| M6.2 | 外部公开教育视频的视觉特征选择与正式轨迹提取 | 已完成 |
| M6.3 | 周期 / 频率测量、FFT 交叉验证、标准 SHM 条件性参考、不确定度与证据边界、最终可视化 | 已完成 |

## 4. 数据来源

本项目的**外部验证数据**为公开教育数据集：

| 项目 | 内容 |
| --- | --- |
| 来源 | ComPADRE / Open Source Physics（OSP），条目 ID **16081** |
| 标题 | Teaching Harmonic Motion Online Using Tracker |
| 使用资源 | **Lab67 Video 1**（质量标签 51.5 g = 0.0515 kg） |
| 视频参数 | 1920 × 1080，30 fps，236 帧（总长约 7.87 s） |
| 正式分析区间 | **frame 76–235**（160 帧，5.3333 s） |
| 数据性质 | **External public educational dataset**（外部公开教育数据，**不是**本项目自行采集） |
| 视频 SHA-256 | `dbc81382e93d2b531b7390f1d52f275da5ea9731a9eec9aadb059667944e282d` |

作者 / 权益持有人与许可（CC BY-NC-SA 3.0）详见 [`docs/ATTRIBUTION.md`](docs/ATTRIBUTION.md)。

## 5. 核心方法

```text
外部视频 → ROI → 灰度阈值 → 暗连通域 → 行宽带 → 暗带上缘 y₀ → y₀(t) → 峰谷检测 → T → f
```

正式检测规则（M6.2-2B 冻结，M6.2-2C 实现）：

| 环节 | 规则 |
| --- | --- |
| ROI | x ∈ [690, 780)，y ∈ [380, 760) |
| 灰度阈值 | gray < 120 |
| 暗连通域 | 8 邻域连通，面积 ≥ 150 px |
| 行宽带 | 行跨度 ≥ 35 px，连续 ≥ 3 行 |
| 几何筛选 | 带宽 40–75 px，带高 ≤ 15 px |
| **正式位置特征** | **暗带上缘 y₀**（不是面积、质心或下缘） |

- 正式区间检出率 **160 / 160**，无缺口、无锁错帧；
- frame 74–75 在冻结规则下无法形成合格暗带 → **保持缺失**，未通过放宽规则强行补值；
- frame 0–73 为释放前/过渡阶段，仅作诊断参考，不进入正式轨迹。

## 6. 主要结果

| 量 | 结果 |
| --- | --- |
| 周期（时域，峰—峰 9 段均值） | **T_exp = 0.542593 s** |
| 频率 | **f_exp = 1.843003 Hz** |
| FFT 交叉验证 | 主峰 **1.875 Hz**，频率分辨率 **df = 0.1875 Hz**（仅作独立交叉验证，不替代时域测量） |
| 标准 SHM 条件性参考 | m = 0.0515 kg、k = 7.05 N/m → **f_theory = 1.862134625 Hz**（T_theory = 0.537018101 s） |
| 实验值与参考值差异 | **约 1.0%**（周期 +1.0381%、频率 −1.0274%） |

说明：该差异**超过** m、k 给定不确定度的传播尺度（±0.3228%），但**未超过**本项目设定的保守采样定位上界（周期 ±0.0333 s、频率 ±0.1132 Hz）；由于缺少弹簧自身质量、挂具/夹持件总质量与阻尼参数等独立测量，**当前不能将该差异归因于某一个具体物理因素**。

（"约 1.0%" 指实验频率与标准模型参考频率之间的差异，**不代表**算法性能指标。该标准模型为**项目采用**的标准质量—弹簧 SHM 模型，非外部实验资料明文给出。）

## 7. 最终成果图

| 图 | 文件 | 用途 |
| --- | --- | --- |
| 图 A | [`results/EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png`](results/EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png) | 回答"我到底测到了什么"：160 个原始采样点、10 个局部极大与 10 个局部极小、单处代表性峰—峰区间 |
| 图 B | [`results/EXP-EXT-LAB67-V1_fig_B_frequency_comparison.png`](results/EXP-EXT-LAB67-V1_fig_B_frequency_comparison.png) | 回答"测出来的结果与物理模型一致到什么程度"：实验测量 / 标准模型参考 / FFT 交叉验证的对照 |
| 图 C | [`results/EXP-EXT-LAB67-V1_fig_C_pipeline.png`](results/EXP-EXT-LAB67-V1_fig_C_pipeline.png) | 回答"我是怎么从视频走到这个结果的"：完整技术流程（计算机视觉 → 时域测量 → 频域交叉验证 → 物理模型） |

## 8. 如何运行

全部 demo 均为**无命令行参数**脚本（输入输出路径在各脚本内部定义）。在项目根目录下执行：

| 阶段 | 命令 | 是否需要仓库之外的本地数据 |
| --- | --- | --- |
| M2 | `.venv\Scripts\python.exe demo\run_single_image_detection.py` | 是（`data/raw/EXP-001-IMAGE-001.jpg`） |
| M3 | `.venv\Scripts\python.exe demo\run_video_tracking.py` | 是（`data/raw/EXP-002-VIDEO-001.mp4`） |
| M4 | `.venv\Scripts\python.exe demo\pick_calibration_points.py`（交互式取点）<br>`.venv\Scripts\python.exe demo\run_m43_displacement.py` | 是（`data/raw/EXP-003-*.mp4`） |
| M5 | `.venv\Scripts\python.exe demo\run_m52_dynamic_displacement.py`<br>`.venv\Scripts\python.exe demo\run_m53_plot.py` | 前者需要 `data/raw/EXP-004-DYNAMIC-001.mp4`；后者只需仓库内已有的 `results/EXP-004-DYNAMIC-001_ds.csv` |
| M6.2 | `.venv\Scripts\python.exe demo\run_m62_external_tracking.py` | 是（`_external/_candidates/candidate_comPADRE_Lab67_01_Video1_51p5g.mp4`） |
| M6.3 | `.venv\Scripts\python.exe demo\run_m63_final_visualization.py` | **否**（只需仓库内 `results/EXP-EXT-LAB67-V1_trajectory.csv`） |
| M7.3 | `.venv\Scripts\python.exe src\m73_presentation.py`（位于 `src/`，**不是 demo**；生成最终 PPT） | 否（使用仓库内成果图与冻结结果） |

说明：

- `data/raw/` 的自采原始视频与 `_external/` 的第三方公开视频**均未随仓库分发**（体积大 / 第三方数据），因此 M2–M6.2 的 demo 需要本地具备相应文件才能重跑；**M6.3 只需仓库内的封板轨迹 CSV 即可重跑**。
- 在已激活虚拟环境的终端中，上述命令亦可简写为 `python demo\run_xxx.py`。
- `M7.3` 的入口是 `src/m73_presentation.py`（**不在 `demo/` 下**），用于生成最终展示材料 `docs/VisionMotion_Final_Presentation.pptx`；本表其余条目均为 `demo/` 下的脚本。
- M4 的 `run_m43_displacement.py` 会按冻结规则为每个视频生成 `_ds.csv`；若某段视频起始窗口（`S0_WINDOW_S`）内的有效帧不足 `MIN_S0_VALID_FRAMES`，则**不会写出该视频的 `_ds.csv`**——这是正常的冻结行为，不代表程序失败（例如当前 `EXP-003-STATIC-001` 只有 `_track.csv` 与 overlay，没有 `_ds.csv`）。

### 标定说明（重要）

`demo/pick_calibration_points.py` 是**交互式人工标定工具**：它打开 `data/raw/EXP-003-STATIC-002.mp4` 的第 900 帧，由用户依次点选 10 cm / 16 cm 刻线，然后调用 `src/calibration.py` 计算并**只在终端打印** `k`（px/mm）与单位方向 `u`（该脚本不保存结果图片、不写 CSV、不写配置文件）。

**它不会把标定结果写入任何文件，也不会自动传给后续 M4 / M5 管线。** 后续位移计算使用的是写死在源码里的"冻结标定常量"：

- `src/displacement.py`（EXP-003，60 mm 标定）：`CALIB_P1_PX`、`CALIB_P2_PX`、`CALIB_REAL_DISTANCE_MM`、`PX_PER_MM`、`MM_PER_PX`、`U`（当前位于该文件第 48–55 行附近），以及配套的 valid gate 与 s0 规则。
- `src/dynamic_displacement.py`（EXP-004，100 mm 标定）：`CALIB_P1_PX`、`CALIB_P2_PX`、`CALIB_REAL_DISTANCE_MM`、`PX_PER_MM_004`、`MM_PER_PX_004`、`U_004`（当前位于该文件第 60–66 行附近），以及 EXP-004 专属 gate 与 s0 规则。

因此，普通用户不要以为"点选两个点 → 后面就会自动完成毫米位移"。**更换实验视频后，若要进行新的 M4 / M5 位移计算，高级用户需要根据新的标定结果人工更新对应模块中的冻结标定常量**（及相应的 gate / s0 规则），然后重新执行脚本内置的 QC 自检。本项目当前**没有**把标定做成命令行参数或配置文件，本阶段也不做这类通用化改造。

## 9. 环境

依赖见 [`requirements.txt`](requirements.txt)（当前共五项：核心运行期库为 opencv-python / numpy / matplotlib，另有 Pillow 与 python-pptx 用于结果图片与 PPT 归档输出；未引入额外框架）：

| 库 | 用途 |
| --- | --- |
| `opencv-python` | 视频读取、图像预处理、阈值分割、轮廓检测 |
| `numpy` | 数组运算、质心与基础统计 |
| `matplotlib` | 位移-时间曲线与最终成果图 |
| `Pillow` | 结果 PNG 的读回校验（尺寸 / 可打开性）与 PPTX 图片素材处理 |
| `python-pptx` | M7.3A 最终展示材料（`.pptx`）的生成 |

建立环境（Windows PowerShell）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Windows CMD 用户把中间一行换成：

```bat
.venv\Scripts\activate.bat
```

说明：PowerShell 的激活脚本是 `Activate.ps1`，必须带 `.\` 前缀；若提示"禁止运行脚本"，属于执行策略限制，本项目的既有做法是把**当前用户**执行策略设为 `RemoteSigned`（还原命令见 §17），不要为此放宽到 `Unrestricted`，也不要改动计算机级策略。

本项目在 Python 3.14.1 + opencv-python 5.0.0.93 + numpy 2.5.3 + matplotlib 3.11.2 环境下验证通过（M1）。

若需运行测试，请额外安装 `requirements-dev.txt`（`pip install -r requirements-dev.txt`）；pytest 不属于项目运行期依赖。

## 10. 输出文件

| 类型 | 文件 |
| --- | --- |
| 正式轨迹（外部公开视频） | [`results/EXP-EXT-LAB67-V1_trajectory.csv`](results/EXP-EXT-LAB67-V1_trajectory.csv)（frame 76–235，160 行） |
| 最终成果图 | `results/EXP-EXT-LAB67-V1_fig_A_y0_timeseries.png`、`..._fig_B_frequency_comparison.png`、`..._fig_C_pipeline.png` |
| 最终报告 | [`docs/M6.3_FINAL_REPORT.md`](docs/M6.3_FINAL_REPORT.md) |
| 早期阶段结果 | `results/EXP-00X-*_track.csv`、`*_ds.csv`、`EXP-004-DYNAMIC-001_displacement.png`、`EXP-001-IMAGE-001_mask.png` 等 |

## 11. 项目局限

1. 本阶段使用**外部公开教育视频**，不是自主采集的实验数据；
2. 当前仅有**单一视频、单一质量**（51.5 g），未做跨视频 / 跨质量的一致性验证；
3. 该外部视频为 **30 fps**，限制了极值时刻的时间定位精度（单帧 0.0333 s）；
4. 正式位置结果以**像素位置 y₀** 表达；
5. 本阶段**未为该外部公开视频建立并应用有效的动态 px/mm 标定**，因此暂不能给出毫米位移与振幅；
6. 正式数据记录长度仅 **5.3333 s**，FFT 频率分辨率有限（df = 0.1875 Hz）；
7. 未进行阻尼、有效质量等物理参数的**独立测量**；
8. 实验值与标准模型参考值之间约 1.0% 差异的**具体物理原因未验证**。

## 12. 最终报告

[`docs/M6.3_FINAL_REPORT.md`](docs/M6.3_FINAL_REPORT.md) 包含：数据源、视觉测量方法、位置信号 y₀(t)、峰谷与周期、FFT 交叉验证、标准 SHM 条件性参考、实验—参考差异、三层不确定度与证据边界、未验证因素、技术链、项目限制与结论。

## 13. 数据与来源说明

第三方数据来源、作者、条目 ID、许可与视频哈希：见 [`docs/ATTRIBUTION.md`](docs/ATTRIBUTION.md)。

## 14. 作者

深圳大学 光电信息科学与工程专业本科生（个人简介将在最终交付阶段单独完善）。

## 15. License

本项目代码采用 **MIT License**（Copyright (c) 2026 yangzi0808），全文见仓库根目录 [`LICENSE`](LICENSE)。第三方公开数据（ComPADRE / OSP Lab67 Video 1）的许可为 **CC BY-NC-SA 3.0**，详见 [`docs/ATTRIBUTION.md`](docs/ATTRIBUTION.md)。

## 16. GitHub Repository

本项目仓库地址：<https://github.com/yangzi0808/VisionMotion>

（项目内容位于该仓库的 `master` 分支；仓库默认分支如需切换，请在 GitHub 仓库设置中手动将默认分支设为 `master`。）

## 18. 常见问题 / FAQ（排错入口）

### 1. 提示"原始图片 / 视频不存在"，找不到输入文件

- 自采实验素材放在 `data/raw/`（图片与视频均可），例如 `data/raw/EXP-002-VIDEO-001.mp4`。
- 外部公开视频放在当前实际使用的 `_external/_candidates/` 下，例如 M6.2 读取的 `_external/_candidates/candidate_comPADRE_Lab67_01_Video1_51p5g.mp4`。
- 当前所有 demo 都是**无命令行参数**脚本，输入路径**硬编码在脚本内部**（例如 `demo/run_video_tracking.py` 固定读 `data/raw/EXP-002-VIDEO-001.mp4`）。文件缺失时脚本会打印"错误：原始视频不存在"并停止。若要换成自己的文件，需按 §17 放到对应路径并改成脚本期望的文件名，或直接修改脚本内的路径常量。

### 2. 中文字体缺失导致出图失败

- 需要中文字体的入口是 `demo/run_m53_plot.py` 与 `demo/run_m63_final_visualization.py`（后者调用 `src/m63_final_visualization.py`）。
- `run_m53_plot.py` **固定**使用 `C:\Windows\Fonts\msyh.ttc`（Microsoft YaHei）；文件不存在时会打印"错误：冻结字体不存在"并停止，不会自行换字体。
- `m63_final_visualization.py` 会按 `Microsoft YaHei → SimHei → DengXian → SimSun → …` 的顺序自动挑选**实际存在**的中文字体；一个都找不到时会报错并停止。
- 解决办法（Windows）：安装微软雅黑，或让上述候选字体之一可用即可，无需改动代码。本项目当前**未声明支持 Linux / macOS 的字体路径**。

### 3. OpenCV 窗口打不开（涉及 `demo/pick_calibration_points.py`）

- 只有 `demo/pick_calibration_points.py` 这一步需要弹出 OpenCV 交互窗口（用鼠标点选 P1 / P2）。
- 在无图形界面的环境（远程 / 无桌面会话）里窗口无法弹出，该步骤无法完成：程序会卡在或错过"等用户点击 / 按 Enter 确认"的环节，不会计算 `k`、`u`，也不会写任何文件。
- 其它 demo（M2 / M3 / M5 / M6.2 / M6.3）不需要 GUI 窗口，可在无界面环境运行。

### 4. SHA-256 校验不匹配（视频 / CSV 不是对应冻结版本）

- 项目对关键输入做 SHA-256 校验，用于确认你手上的文件**与冻结记录完全一致**（例如 M5.2 的原始视频、M6.2 的外部视频、M5.3 的封板 ds CSV）。
- 常见失败原因：文件被替换 / 重新导出 / 重新生成（字节不同）、下载来源不同、或文件被移动混用。
- **不要通过删除代码里的 SHA 校验来"绕过"**：校验失败通常意味着输入不是对应的冻结版本，删掉校验会让结果失去可追溯性。
- 正确做法：核对你手上的文件是否就是该阶段记录的对应版本（外部视频哈希见 §4；各脚本运行时也会打印期望值），放回正确文件后重试。

### 5. 叠加视频失败、输出回退为代表性 PNG（`demo/run_video_tracking.py`）

- 正常情况下，M3 会生成叠加视频 `results/EXP-002-VIDEO-001_overlay.mp4`。
- 若所有候选编码器（`mp4v`、`avc1`）都无法打开 VideoWriter，程序会**回退**为保存最多 5 张代表性 PNG，命名形如 `results/EXP-002-VIDEO-001_overlay_frame%04d_<tag>.png`（`tag` 为 `start` / `middle` / `end` / `fastest_motion` / `blurriest`）。
- 判断是否仍然成功：只要 `results/EXP-002-VIDEO-001_track.csv` 正常生成、终端打印"叠加视频是否成功：否（…已回退保存 N 张代表性 PNG）"、且 CSV 自检通过，这次追踪即算成功完成——回退只影响叠加可视化，不影响时序坐标 CSV。

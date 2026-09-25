# ATTRIBUTION — 第三方数据来源与署名说明

本文件记录 VisionMotion 项目中使用的**第三方公开数据**的来源、作者、许可与身份标识，
用于满足署名（attribution）与可追溯（traceability）要求。

## External dataset

| 项目 | 内容 |
| --- | --- |
| Provider | ComPADRE / Open Source Physics (OSP) |
| Entry ID | **16081** |
| Title | **Teaching Harmonic Motion Online Using Tracker** |
| Author / Rights holder | **Kathleen Koenig** |
| Used resource | **Lab67 Video 1**（质量标签 51.5 g） |
| License | **CC BY-NC-SA 3.0** |

本项目使用该公开教育数据作为 VisionMotion 的**外部验证数据**。
本项目**没有**把该视频声明为自主采集数据。

## 正式使用的视频文件

| 项目 | 内容 |
| --- | --- |
| 本地文件（未随仓库分发） | `_external/_candidates/candidate_comPADRE_Lab67_01_Video1_51p5g.mp4` |
| SHA-256 | `dbc81382e93d2b531b7390f1d52f275da5ea9731a9eec9aadb059667944e282d` |
| 视频参数 | 1920 × 1080，30 fps，236 帧（总长约 7.87 s） |
| 正式分析区间 | frame 76–235（160 帧，5.3333 s） |

## 该数据集附带的其他资料（同一归档）

以下资料同样来自 ComPADRE / OSP 的 Lab67 归档，本项目中仅用于**参数核验与实验背景理解**：

| 文件 | 用途 | SHA-256 |
| --- | --- | --- |
| `Equipment values - IV is Amount of Mass on Srping.pdf` | 参数来源：k = 7.05 N/m（±0.045 N/m）；video 1 → mass on spring = 0.0515 kg（±0.00005 kg）；释放前下拉距离 0.05 m（±0.005 m） | `180587ec6a31b494453d7635ca5985b48bfc1de07675c4f3cdaf34378eb3d49a` |
| `FS20 - Labs 06 and 07 -Simple Harmonic Motion.pdf` | 实验指导资料（研究问题为“质量对弹簧振子周期的影响”；资料要求学生自行查找与陈述理论模型） | `223125d064f6c55c5a4b501c9536807e3bcffc0209868973daa5866c13b95467` |

## 使用与分发说明

- 本项目将上述公开视频用于**方法验证与交叉对比**，未用于任何商业用途。
- 项目最终交付 ZIP **不默认包含**第三方原始视频；正式报告（`docs/M6.3_FINAL_REPORT.md`）中保留来源、作者、许可与哈希记录。
- 如需再分发该第三方数据，请遵循 **CC BY-NC-SA 3.0** 的署名（BY）、非商业（NC）与相同方式共享（SA）条款。
- 本项目代码采用 MIT License，详见仓库根目录 `LICENSE` 文件。

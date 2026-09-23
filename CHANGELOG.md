# CHANGELOG — 版本更新记录

本文件记录项目每一步的变化。规则很简单：

- 每次改代码或改文档都在"未发布"下面加一条记录。
- 记录三件事：**做了什么、为什么做、影响了哪些文件**。
- 版本号规则：开发阶段用 `v0.x.y`；第一版功能全部完成并验证通过后发布 `v1.0.0`。
- 发布一个版本时，把"未发布"里的内容移到新的版本号下面，并写上日期。

## 未发布

### 新增

- 建立项目目录骨架：`src/`、`data/raw/`、`data/processed/`、`results/`、`tests/`、`docs/`、`demo/`
- 添加 `README.md`（项目简介与当前状态）、`PROJECT_SPEC.md`（项目说明书）、`EXPERIMENT_PROTOCOL.md`（实验记录模板）
- 添加 `requirements.txt`，列出第一阶段依赖：OpenCV、NumPy、Matplotlib
- 添加 `.gitignore`，排除虚拟环境、Python 缓存、临时文件与大型视频
- 原因：先固定项目范围与记录方式，再开始写代码，避免边写边改需求
- **M1 开发环境**：创建项目专用虚拟环境 `.venv`（Python 3.14.1），只安装本阶段需要的库
- **M1 开发环境**：在 `.venv` 中安装并验证 `opencv-python` 5.0.0.93（`import cv2` 成功）
- **M1 开发环境**：在 `.venv` 中安装并验证 `numpy` 2.5.3（`import numpy` 成功）
- **M1 开发环境**：在 `.venv` 中安装并验证 `matplotlib` 3.11.2（`import matplotlib` 成功）
- 原因（M1）：只建立并验证开发环境，不写任何业务代码

### 变更

- 无

### 修复

- 无

### 说明

- 当前只有文档、配置与开发环境，`src/` 下尚无任何业务代码

## [v0.2.0] - 2026-09-23

### 新增

- **M2.3 单张图片视觉检测**：新增 `src/marker_detector.py`，完成对真实原始图片 `data/raw/EXP-001-IMAGE-001.jpg` 的红色目标检测
- HSV 红色双区间分割：红色在 HSV 色环上位于两端，用 `[0,100,70]~[10,255,255]` 与 `[170,100,70]~[179,255,255]` 两个区间分别取掩膜再合并
- 3×3 开运算去除零散噪点，保留目标主体形状
- 外部轮廓检测（`RETR_EXTERNAL`）并按面积筛选最大轮廓，面积小于阈值的候选直接忽略
- 用图像矩计算轮廓质心，输出目标中心像素坐标、轮廓面积与外接矩形
- 新增 `demo/run_single_image_detection.py`，生成并保存 `results/EXP-001-IMAGE-001_overlay.png`（标注图）与 `results/EXP-001-IMAGE-001_mask.png`（分割掩膜）

### 变更

- 无

### 修复

- 处理 Windows 中文路径读取问题：`cv2.imread` / `cv2.imwrite` 在含中文的路径下会失败，改用 `np.fromfile` + `cv2.imdecode` 读取、`cv2.imencode` + `tofile` 保存

### 说明

- 用真实拍摄图片完成人工验收：overlay、mask 与中心位置均正确
- 未引入额外第三方依赖，仍只使用 OpenCV、NumPy、Matplotlib
- 本次回归实测结果：中心坐标 (512.7, 964.5) px，面积 1278.5 px，外接矩形 (494, 940, 37, 51)

## 版本记录模板（复制此块用于新版本）

```text
## [v0.x.y] - YYYY-MM-DD

### 新增

- 

### 变更

- 

### 修复

- 

### 说明

- 
```

# VisionMotion 课程总目录

本文件是 VisionMotion 学习课程的**总目录**，用来记录每一节课的编号、标题、学习目标、核心概念、对应的项目文件和学习状态。
每学完一节课，就在本文件中新增（或更新）一条记录，保持长期可追溯。

配套文件：

- 课程笔记：`docs\learning\` 下的 `Lxx_*.md` 文件（每节课一份）；
- 专业术语表：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md)（所有学过的术语）；
- 易错知识库：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md)（所有踩过的坑）。

## 课程总览

| 课程编号 | 课程标题 | 学习状态 | 笔记文件 |
| --- | --- | --- | --- |
| L01 | VisionMotion项目、CSV与时间序列 | 已完成 | [`L01_VisionMotion项目_CSV与时间序列.md`](L01_VisionMotion项目_CSV与时间序列.md) |
| L02 | marker_detector.py：从图片到目标中心 | 已完成 | [`L02_marker_detector_目标检测.md`](L02_marker_detector_目标检测.md) |
| L03 | 像素、颜色空间与 Mask 的实际运算 | 已完成 | [`L03_像素_颜色空间与Mask.md`](L03_像素_颜色空间与Mask.md) |
| L04 | Contour、Moments 与 Centroid | 已完成 | [`L04_Contour_Moments_Centroid.md`](L04_Contour_Moments_Centroid.md) |
| L05 | 从单张图片到视频：逐帧处理 | 已完成 | [`L05_从单张图片到视频_逐帧处理.md`](L05_从单张图片到视频_逐帧处理.md) |
| L06 | 从逐帧结果到 CSV：数据记录、字段设计与时间序列 | 已完成 | [`L06_CSV与时间序列.md`](L06_CSV与时间序列.md) |
| L07 | 检测失败、质量检查与鲁棒性 | 已完成 | [`L07_检测失败与鲁棒性.md`](L07_检测失败与鲁棒性.md) |
| L08 | 为什么像素不能直接当毫米（像素与毫米标定） | 已完成 | [`L08_像素与毫米标定.md`](L08_像素与毫米标定.md) |
| L09 | 标定、方向向量与一维投影 | 已完成 | [`L09_标定方向向量与一维投影.md`](L09_标定方向向量与一维投影.md) |
| L10 | 从一维位置到位移：s0、ds_px 与 ds_mm | 已完成 | [`L10_从一维位置到位移.md`](L10_从一维位置到位移.md) |
| L11 | 位移数据、正负号与运动方向 | 已完成 | [`L11_位移正负与运动方向.md`](L11_位移正负与运动方向.md) |
| L12 | 转向点检测与运动段切分 | 已完成 | [`L12_转向点检测与运动段切分.md`](L12_转向点检测与运动段切分.md) |
| L13 | 从运动段到往复运动——为什么可以开始讨论周期、频率与重复运动 | 已完成 | [`L13_从运动段到往复运动.md`](L13_从运动段到往复运动.md) |

（L14 及以后的课程将在学习完成后陆续补充。）

---

## L01 VisionMotion项目、CSV与时间序列

- **课程编号**：L01
- **课程标题**：VisionMotion 项目、CSV 与时间序列
- **学习状态**：已完成
- **记录日期**：2026-09-28
- **笔记文件**：[`L01_VisionMotion项目_CSV与时间序列.md`](L01_VisionMotion项目_CSV与时间序列.md)

### 本节课目标

- 理解 VisionMotion 项目总体上在做什么；
- 理解视频为什么可以看成连续的一张张图片，以及 Frame 是什么；
- 理解 FPS 的含义，以及它为什么决定时间分辨率；
- 理解 frame 与 time_s 的关系（time_s ≈ frame / 30）；
- 理解 CSV，以及"一行 CSV 代表一个时刻的一次视觉测量结果"；
- 理解 y0_px（暗带上缘的竖直像素位置）和图像坐标系中 y 轴的方向；
- 理解 y0_px 为什么可以形成时间序列 y0(t)；
- 理解 trajectory.csv 在整个项目数据链中的位置。

### 核心概念

1. 视频在计算机中是"一帧一帧的图片序列"，每一帧代表一个时间瞬间；
2. FPS = 每秒帧数；本视频 30 fps，相邻帧间隔 Δt = 1/30 s ≈ 0.033333 s；
3. frame 是帧编号，time_s 是时间，两者关系 time_s ≈ frame / 30；
4. CSV 是逗号分隔的纯文本表格；trajectory.csv 有 160 行数据、8 列；
5. 一行 CSV = 一个时刻的一次视觉测量结果；
6. y0_px 是暗带上缘的竖直像素位置，是本阶段的核心运动信号；
7. 图像坐标系 y 轴向下增加：y0_px 越大越靠下，越小越靠上；
8. y0_px = y0(t)：位置测量按时间排列，形成时间序列；
9. 检测质量字段（detected、bbox_w_px、bbox_h_px、area_px）不等于运动测量量；
10. trajectory.csv 位于"视频 → 目标位置 → 时间序列"数据链的中间位置。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 正式轨迹数据 | `results\EXP-EXT-LAB67-V1_trajectory.csv` | 160 行、8 列；表头 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`；正式分析区间 frame 76–235 |
| 产生该数据的程序 | `src\external_oscillation_tracker.py` | 外部视频逐帧检测与正式轨迹 CSV 的实现（源码细节属于后续课程） |
| 项目说明 | `README.md` | 视频参数（1920 × 1080，30 fps，236 帧）与项目总体介绍 |
| 本节课笔记 | `docs\learning\L01_VisionMotion项目_CSV与时间序列.md` | 15 节完整笔记（含自测题） |

### 本节课确认的数据事实

- 正式数据从 frame 76 到 frame 235，共 160 行；
- 160 / 160 帧 detected = True；
- 第一个局部极小值出现在 frame 77，y0_px = 508；
- 第一个局部极大值出现在 frame 85，y0_px = 622；
- y0_px 整体呈往复变化，形成运动轨迹的时间序列。

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L01 VisionMotion项目、CSV与时间序列"（Frame、FPS、CSV、Time Series、Pixel、frame、time_s、x_px、y0_px、Trajectory 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L01 VisionMotion项目、CSV与时间序列"（y 轴方向、frame 与 time_s 的区别、y0_px 是运动信号、检测质量字段、视频的离散性）。

### 本节课暂未学习的内容

~~marker_detector.py 源码 / BGR / HSV / Mask / Morphology / Contour / Moments / Centroid~~（已在 L02 学习，见下一节）/ ~~视频逐帧检测代码~~（已在 L05 学习，见后续小节）/ ~~逐帧结果写入 CSV 的源码细节（CSV_FIELDNAMES、build_csv_row、records、check_csv_data）~~（已在 L06 学习，见后续小节）/ Calibration / 周期 / 频率 / FFT

（以上内容属于后续课程；本节只登记名称，不展开。）

---

## L02 marker_detector.py：从图片到目标中心

- **课程编号**：L02
- **课程标题**：marker_detector.py：从图片到目标中心
- **学习状态**：已完成
- **记录日期**：2026-09-28
- **笔记文件**：[`L02_marker_detector_目标检测.md`](L02_marker_detector_目标检测.md)

### 本节课目标

- 理解 VisionMotion 是如何从一张彩色图片中找到红色目标，并最终得到目标位置坐标 (cx, cy) 的；
- 理解 `marker_detector.py` 的项目定位：只负责"在一张图片中找到红色目标并返回检测信息"，不读文件、不存文件、不画图、不弹窗口；
- 理解 BGR 与 HSV 两种颜色描述方式的差别，以及为什么检测红色要转成 HSV；
- 理解红色为什么需要两个 H 区间，以及两张 mask 如何用 `bitwise_or` 合并；
- 理解 Mask、Contour、Centroid 三个层次的区别：像素级规则结果 → 候选形状 → 代表点；
- 理解最大轮廓 + `MIN_AREA` 门槛这条项目规则及其局限；
- 理解质心公式 `cx = m10 / m00`、`cy = m01 / m00`，并能区分质心与外接矩形中心；
- 能默写完整 Pipeline：BGR 彩色图片 → HSV → 红色双区间 Mask → 3×3 开运算 → Contour → 最大轮廓 → 面积门槛 → Moments → Centroid → (cx, cy)。

### 核心概念

1. 完整 Pipeline：BGR 彩色图片 → HSV → 红色双区间 Mask → 3×3 开运算 → Contour → 最大轮廓 → 面积门槛 → Moments → Centroid → (cx, cy)；
2. BGR：OpenCV 读取彩色图片的默认通道顺序，一个像素是 `[B, G, R]`，与常见的 RGB 顺序不同；
3. HSV：H = Hue 色相（是什么颜色）、S = Saturation 饱和度（颜色有多浓）、V = Value 明度（有多亮）；OpenCV 8 位图中 H ∈ [0, 179]（不是 0° ~ 360°），S、V ∈ [0, 255]；
4. 红色双区间：`[0,100,70]~[10,255,255]` 与 `[170,100,70]~[179,255,255]`；红色跨过 HSV 色环的 0°/360° 接缝，必须拆成两段，再用 `cv2.bitwise_or` 合并；
5. Mask：与原图逐像素对应的单通道 8 位黑白图，255 = 满足红色条件、0 = 不满足，是"逐像素的是/否判断表"，由 `cv2.inRange` 生成；
6. 3×3 开运算：先腐蚀再膨胀，用一个 3×3 矩形核去掉零散小噪点、同时尽量保留主体目标；它不是模糊；
7. Contour：`cv2.findContours` 从 Mask 中找白色区域的边界；Mask 只是"哪里符合规则"，Contour 才把像素区域表示成一个个候选形状；
8. 最大轮廓与面积门槛：项目假设"最大的红色区域就是目标"，按 `cv2.contourArea` 降序取最大；`MIN_AREA = 200`，最大轮廓面积小于它则检测失败并返回 `None` / `success=False`；
9. Moments：`cv2.moments(contour)` 得到图像矩，本项目主要使用 `m00`、`m10`、`m01`；
10. Centroid：质心，`cx = m10 / m00`、`cy = m01 / m00`；本项目用 (cx, cy) 表示红色目标的中心位置；质心 ≠ 外接矩形中心，`boundingRect` 的 (x, y, w, h) 主要用于框选与辅助检查；
11. 核心检测函数不负责文件读写，因此单图检测（M2）与视频逐帧检测（M3）可以复用同一个 `detect_marker`。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 检测模块（本节主角） | `src\marker_detector.py` | 检测算法与参数的唯一来源：`create_red_mask` / `find_target_contour` / `calculate_centroid` / `detect_marker`；全部可调参数集中在文件顶部 |
| M2 单图检测调用方 | `demo\run_single_image_detection.py` | 读取 `data\raw\EXP-001-IMAGE-001.jpg`，调用 `detect_marker(image)`，保存 overlay 与 mask 到 `results\` |
| M3 视频逐帧检测调用方 | `src\video_tracker.py` | 逐帧 `detect_marker(frame)`，写 track CSV 与叠加视频；文件头明确"检测参数唯一来源是 src\marker_detector.py" |
| 本节课笔记 | `docs\learning\L02_marker_detector_目标检测.md` | 19 节完整笔记（含自测题 15 道） |

### 本节课确认的代码事实

- `RED_LOWER_1 = [0, 100, 70]`、`RED_UPPER_1 = [10, 255, 255]`、`RED_LOWER_2 = [170, 100, 70]`、`RED_UPPER_2 = [179, 255, 255]`；
- `MORPH_KERNEL_SIZE = 3`（3×3 矩形核 `cv2.MORPH_RECT`）；`MIN_AREA = 200`；
- `create_red_mask`：`cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)` → 两次 `cv2.inRange` → `cv2.bitwise_or` → `cv2.morphologyEx(..., cv2.MORPH_OPEN, kernel)`；
- `find_target_contour`：`cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)` → 按 `cv2.contourArea` 降序取最大 → 面积 < `MIN_AREA` 返回 `None`；
- `calculate_centroid`：`cv2.moments(contour)`；`m00 == 0` 返回 `None`；否则 `cx = m10 / m00`、`cy = m01 / m00`；
- `detect_marker`：成功返回 `{"success": True, "cx", "cy", "area", "bbox": (x, y, w, h), "contour", "mask"}`；失败返回 `{"success": False, "mask": mask}`；
- 历史已记录的实跑结果示例（非本次运行）：`data/raw/EXP-001-IMAGE-001.jpg` 上中心 (512.7, 964.5) px、面积 1278.5 px²、外接矩形 (494, 940, 37, 51)。

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L02 marker_detector.py：从图片到目标中心"（BGR、HSV、Hue、Saturation、Value、Mask、Threshold、Morphological Opening、Erosion、Dilation、Contour、Moments、Centroid、Bounding Rectangle）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L02 marker_detector.py：从图片到目标中心"（BGR/RGB 顺序、H 取值 0~179、红色双区间、mask 不是原图、mask 不等于目标、contour 不等于质心、质心不等于外接矩形中心、最大轮廓只是项目规则、开运算不是模糊）。

### 本节课暂未学习的内容

~~视频逐帧检测代码细节（M3）~~（已在 L05 学习，见后续小节）/ Calibration 与毫米换算 / 周期 / 频率 / FFT

（以上内容属于后续课程；本节只登记名称，不展开。）

---

## L03 像素、颜色空间与 Mask 的实际运算

- **课程编号**：L03
- **课程标题**：像素、颜色空间与 Mask 的实际运算
- **学习状态**：已完成
- **记录日期**：2026-09-28
- **笔记文件**：[`L03_像素_颜色空间与Mask.md`](L03_像素_颜色空间与Mask.md)

### 本节课目标

- 理解像素与"离散化"：计算机为什么把连续视觉世界变成像素与数字；
- 理解图片在 Python/OpenCV 中是 NumPy 数组：`(100, 80, 3)` 三个维度的含义、`img[y, x]` 的下标顺序、`uint8` 与 0～255；
- 理解 OpenCV 默认 BGR，以及它与 RGB 的区别；
- 理解颜色空间（BGR / HSV）是"描述颜色的坐标方式"；H/S/V 各自回答什么问题；
- 记住 OpenCV 8 位 HSV 中 H ∈ [0, 179]（≈ 色相角度 ÷ 2），并能换算 0°、340°、358°；
- 理解"同一个红色物体在不同光照下 BGR 会变化"，以及 HSV 为什么更适合按颜色筛选（但不能理解为完全消除光照影响）；
- 理解阈值与条件：同一区间内 H/S/V 是"并且"（AND），两个红色区间之间是"或者"（OR）；
- 理解 `cv2.inRange` 逐像素输出 255/0，`cv2.bitwise_or` 合并两张 Mask；
- 理解 Mask 是"逐像素回答要不要保留"的单通道黑白图，是颜色筛选的中间结果；
- 会用三个手算像素案例与 3×3 玩具图复现 Mask 结果；
- 知道 Mask 是 Contour 的输入（第 73 行），但不展开 Contour 内部。

### 核心概念

1. 像素是数字图像最基本的数据单位；计算机把连续视觉世界离散成像素和数字后才能存储、计算与复现；
2. 图片是 NumPy 数组：100×80 彩色图 shape 为 `(100, 80, 3)`（高、宽、通道）；访问是 `img[y, x]`（先行后列）；8 位图像用 `uint8`、单通道 0～255；
3. OpenCV 默认 BGR：一个像素 `(B, G, R)`，与 RGB 顺序相反；`(0,0,255)` 纯红、`(255,0,0)` 纯蓝、`(0,0,128)` 暗红；第 110 行附近的输入说明写明 `image_bgr` 是 `cv2.imread` 读进来的 BGR 图像；
4. 颜色空间是"描述颜色的坐标 / 记账方式"：BGR 用蓝绿红强度，HSV 用色相 / 饱和度 / 明度；颜色空间改变的是表示方法，不是物体本身；
5. 同一红色物体不同光照下 BGR 会变化（亮 ≈ `(40,40,220)`、暗 ≈ `(20,20,140)`）；HSV 更适合按颜色种类筛选，但不能理解为完全消除光照影响；
6. HSV：H = 是什么颜色（色环位置）、S = 多浓、V = 多亮；OpenCV 8 位 H ∈ [0, 179]（≈ 角度 ÷ 2；340°→170、358°→179）；
7. VisionMotion 红色定义（真实源码第 22～27 行）：区间 1 `[0,100,70]~[10,255,255]`、区间 2 `[170,100,70]~[179,255,255]`，通道顺序 `[H, S, V]`；红色跨色环接缝所以要两段；
8. 条件关系：同一区间内 H、S、V 三个条件是 AND（同时成立）；两个区间之间是 OR（`cv2.bitwise_or` 逐像素合并，任一通过即保留）；
9. `cv2.inRange`（第 51～52 行）逐像素检查 H/S/V 是否都在区间内：全满足 → 255，任一不满足 → 0；输出 H×W 单通道黑白图；
10. `cv2.bitwise_or`（第 55 行）：0 OR 0 = 0，其余三种组合 = 255；
11. Mask 是逐像素回答"要不要保留"的黑白图（255 保留 / 0 不保留）；它不是原图，也不是目标本身，而是颜色筛选的中间结果；
12. Mask 把"颜色问题"转换成"黑白区域问题"，是后续 Contour 的输入（第 73 行 `cv2.findContours`）；
13. "教学示例（手算像素、3×3 玩具图）不是项目实际数据"；项目事实必须用 文件 + 函数 + 行号 定位。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 检测模块（本节源码主角） | `src\marker_detector.py` | 红色 HSV 阈值常量与 `create_red_mask` / `find_target_contour` 的实现（本节引用第 22～27、48、51～52、55、73、110 行） |
| M2 单图检测调用方 | `demo\run_single_image_detection.py` | 读取图片后调用 `detect_marker(image)`（第 115 行），走的就是本节的红色 Mask 流程 |
| M3 视频逐帧检测调用方 | `src\video_tracker.py` | 逐帧调用 `detect_marker(frame)`（`track_video()` 第 491 行；2026-10-07 复核，行号以当前源码为准），检测参数唯一来源写在文件头注释里（`src\marker_detector.py`） |
| 本节课笔记 | `docs\learning\L03_像素_颜色空间与Mask.md` | 22 节完整笔记（含自测题 20 道，均不附答案） |

### 本节课确认的源码事实

- 第 22～27 行：`RED_LOWER_1 = np.array([0, 100, 70])`、`RED_UPPER_1 = np.array([10, 255, 255])`、`RED_LOWER_2 = np.array([170, 100, 70])`、`RED_UPPER_2 = np.array([179, 255, 255])`（通道顺序 `[H, S, V]`）；
- 第 48 行（`create_red_mask`）：`hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)`；
- 第 51～52 行：`mask_low = cv2.inRange(hsv_image, RED_LOWER_1, RED_UPPER_1)`、`mask_high = cv2.inRange(hsv_image, RED_LOWER_2, RED_UPPER_2)`；
- 第 55 行：`mask = cv2.bitwise_or(mask_low, mask_high)`；
- 第 73 行（`find_target_contour`）：`contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`；
- 第 110 行附近：`detect_marker` 文档字符串说明输入 `image_bgr` 是用 `cv2.imread` 读进来的 BGR 图像；
- （第 57～61 行的 3×3 开运算属于 L02 已学内容；L03 只确认它在 `bitwise_or` 之后、Mask 返回之前执行，不展开。）

### L03 源码地图

| 位置（`src\marker_detector.py`） | 内容 |
| --- | --- |
| 第22～27行 | 红色 HSV 阈值常量（`RED_LOWER_1` / `RED_UPPER_1` / `RED_LOWER_2` / `RED_UPPER_2`） |
| 第48行 | BGR → HSV（`cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)`） |
| 第51～52行 | `cv2.inRange` → 两个 Mask（`mask_low` / `mask_high`） |
| 第55行 | `cv2.bitwise_or` → 合并 Mask |
| 第73行 | Mask → Contour（`cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`） |

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L03 像素、颜色空间与 Mask 的实际运算"（Pixel、NumPy Array、Image、BGR、RGB、HSV、Hue、Saturation、Value、Color Space、Threshold、Mask、Binary Image、cv2.cvtColor、cv2.inRange、bitwise_or、Contour）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L03 像素、颜色空间与 Mask 的实际运算"（BGR/RGB、`img[y,x]`、H 0～179、红色双区间、区间内 AND、区间间 OR、Mask 不是原图/不是目标、255/0 含义、inRange 逐像素、bitwise_or 逐像素、教学示例 ≠ 项目数据、源码定位）。

### 本节课暂未学习的内容

Contour 的内部细节 / ~~视频追踪~~（已在 L05 学习，见后续小节）/ Calibration / 周期 / 频率 / FFT

（本节只学到"Mask 可以作为 Contour 的输入"；以上内容属于后续课程，本节只登记名称，不展开。）

---

## L04 Contour、Moments 与 Centroid

- **课程编号**：L04
- **课程标题**：Contour、Moments 与 Centroid：从目标区域到目标中心
- **学习状态**：已完成
- **记录日期**：2026-09-29
- **笔记文件**：[`L04_Contour_Moments_Centroid.md`](L04_Contour_Moments_Centroid.md)

### 本节课目标

- 用一句话区分 Mask（像素层）与 Contour（区域 / 几何层）；
- 理解从 Mask 到目标中心的完整知识链：Mask → Contour → 最大轮廓 → 面积门槛 → Moments → Centroid → (cx, cy)；
- 读懂 `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`（第 73 行）：输入 mask、输出 contours 列表（不是单个轮廓）；`RETR_EXTERNAL` 只关注外部轮廓，`CHAIN_APPROX_SIMPLE` 对轮廓点进行简化；
- 理解项目"按 `contourArea` 从大到小排序、取最大轮廓"的规则（第 78～80 行），并能说明"最大轮廓 = 目标"是项目人为设计的规则，不是通用目标识别方法；
- 理解 `cv2.contourArea(contour)` 计算的是轮廓包围出的几何面积，不等于"Mask 中 255 像素的简单计数"；
- 记住真实参数 `MIN_AREA = 200`（第 33 行）与面积门槛逻辑（第 82～84 行），理解它是"噪声保护 / 失败判断"；
- 理解 Moments 是对目标形状的统计描述（第 95 行 `cv2.moments`），本项目重点使用 m00 / m10 / m01；
- 记住质心公式 `cx = moments["m10"] / moments["m00"]`、`cy = moments["m01"] / moments["m00"]`（第 100～101 行），理解其本质是面积加权平均；
- 理解 `m00 == 0` 防护（第 97～98 行）与"使用前检查数据是否有效"的工程编程思想；
- 区分钟心（Centroid）与外接矩形（boundingRect）：外接矩形中心是 (x + w/2, y + h/2)，与质心不一定相同（第 141 行得到 bbox）；
- 理解 `detect_marker()`（第 105 行起）是总调度函数：组织完整 Pipeline、处理失败分支、组装结果字典。

### 核心概念

1. 层次观：Mask 是像素层（逐像素的 0/255 判断表），Contour 是区域 / 几何层（白色区域的边界点集）；"目标"这个概念是在几何层才出现的；
2. `cv2.findContours`（第 73 行）的输入是 mask，输出是 `contours`（轮廓列表）与本项目丢弃的第二个返回值；`contours, _ = ...` 中的 `_` 表示"这个返回值不用"；
3. `contours` 是列表不是单个轮廓：一张 Mask 可以有多个轮廓；判断有没有轮廓看 `len(contours) == 0`（第 75～76 行），取某一个轮廓用下标（第 80 行 `contours_sorted[0]`）；
4. `RETR_EXTERNAL`（检索模式）决定"要哪些轮廓"：只关注最外层轮廓，不单独处理内部孔洞边界；
5. `CHAIN_APPROX_SIMPLE`（点存储方式）决定"轮廓点怎么记录"：对直线段只保留端点、丢掉冗余点；简化的是表示用的点，不是轮廓形状；
6. 项目按 `cv2.contourArea` 从大到小排序（`reverse=True`），取第一个作为最大轮廓（第 78～80 行）；因第 75～76 行先判空，`[0]` 是安全的；
7. **"最大轮廓 = 目标"是项目人为设计的规则**，依赖"受控场景里最大的红色区域就是标记"这一前提，不是通用目标识别方法；
8. `cv2.contourArea(contour)` 计算轮廓包围出的几何面积（浮点数，像素面积单位）；它不等于"数 Mask 中 255 像素个数"，后者是像素层统计；
9. `MIN_AREA = 200`（第 33 行定义、第 82～84 行使用）是"噪声保护 / 失败判断"：最大轮廓面积小于 200 时返回 `None`，由上层转成 `success=False`；条件是"小于"（<），单位是面积不是长度；
10. `cv2.moments(contour)`（第 95 行）返回一组统计量（dict），本项目重点用 m00 / m10 / m01；Moments 不是"直接返回中心点"；
11. `m00` 是面积总量、`m10` 是 x 方向加权总量、`m01` 是 y 方向加权总量；`cx = m10 / m00`、`cy = m01 / m00`（第 100～101 行）本质是面积加权平均；`m10` 配 x、`m01` 配 y，写反会让 cx / cy 互换且不报错；
12. `m00 == 0` 防护（第 97～98 行）：防止除零，体现"使用前检查数据是否有效"的基本工程编程思想；无效时返回 `None` 而不是崩溃；
13. Centroid 与 Bounding Rectangle：`cv2.boundingRect` 给出 (x, y, w, h) 形成包住目标的矩形框；质心描述目标实际形状的中心位置，两者不一定相同（不规则形状下可能相差明显）；
14. `detect_marker()`（第 105 行起）是总调度函数：`create_red_mask()` → `find_target_contour()` → `calculate_centroid()` → area → bbox → 结果字典（`success` / `cx` / `cy` / `area` / `bbox` / `contour` / `mask`）；底层函数各负责一个清晰的小任务，上层函数负责组织整个 Pipeline。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 检测模块（本节源码主角） | `src\marker_detector.py` | `MIN_AREA` 与 `find_target_contour` / `calculate_centroid` / `detect_marker` 的实现（本节引用第 33、66、73、75～76、78～80、82～84、86、89、95、97～98、100～101、102、105、129、131、135、140、141、143～151 行） |
| M2 单图检测调用方 | `demo\run_single_image_detection.py` | 第 115 行 `result = detect_marker(image)`，走的就是本节"Mask → Contour → 质心"的完整流程 |
| M3 视频逐帧检测调用方 | `src\video_tracker.py` | `track_video()` 第 491 行 `result = detect_marker(current_frame)`（2026-10-07 复核，行号以当前源码为准；详见 L05 小节），逐帧复用本节的检测流程（逐帧追踪实现细节已在 L05 学习） |
| 本节课笔记 | `docs\learning\L04_Contour_Moments_Centroid.md` | 20 节完整笔记（含自测题 18 道，均不附答案） |

### 本节课确认的源码事实

- 第 33 行：`MIN_AREA = 200`（文件顶部"核心参数"区域）；
- 第 73 行（`find_target_contour`）：`contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`；
- 第 75～76 行：`if len(contours) == 0: return None`；
- 第 78～80 行：`contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)`、`biggest_contour = contours_sorted[0]`；
- 第 82～84 行：`if cv2.contourArea(biggest_contour) < MIN_AREA: return None`（面积门槛）；
- 第 86 行：`return biggest_contour`；
- 第 95 行（`calculate_centroid`）：`moments = cv2.moments(contour)`；
- 第 97～98 行：`if moments["m00"] == 0: return None`（防除零）；
- 第 100～101 行：`cx = moments["m10"] / moments["m00"]`、`cy = moments["m01"] / moments["m00"]`；第 102 行 `return cx, cy`；
- 第 105 行：`def detect_marker(image_bgr):`；第 129 / 131 / 135 行依次调用 `create_red_mask` / `find_target_contour` / `calculate_centroid`；第 140 行 `cv2.contourArea(contour)`；第 141 行 `cv2.boundingRect(contour)`；第 143～151 行返回结果字典（失败时为第 132～133、136～137 行的 `{"success": False, "mask": mask}`）。

### L04 源码地图

| 位置（`src\marker_detector.py`） | 内容 |
| --- | --- |
| 第33行 | `MIN_AREA`（候选轮廓最小面积门槛，真实值 200） |
| 第73行 | `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)` |
| 第78～80行 | 最大轮廓选择（按 `cv2.contourArea` 从大到小排序，取 `contours_sorted[0]`） |
| 第82～84行 | 面积门槛（`cv2.contourArea(biggest_contour) < MIN_AREA` → `return None`） |
| 第95行 | `cv2.moments(contour)` |
| 第97～98行 | `m00 == 0` 保护（防止除零） |
| 第100～101行 | 质心计算（`cx = m10 / m00`、`cy = m01 / m00`） |
| 第105行开始 | `detect_marker`（总调度函数） |

（行号按 2026-09-29 当前源码 `src\marker_detector.py`（共 151 行）逐行核对；如果实际源码行号发生变化，以当前真实源码为准。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L04 Contour、Moments 与 Centroid"（Contour、findContours、RETR_EXTERNAL、CHAIN_APPROX_SIMPLE、Contour Area、Moments、m00、m10、m01、Centroid、Bounding Rectangle、MIN_AREA）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L04 Contour、Moments 与 Centroid"（Mask 与 Contour 不是一回事、contours 是列表、最大轮廓是项目规则、contourArea 不是数 255、Centroid 不等于 bbox 中心、Moments 不是直接返回中心点、m00 有效性检查、输入 / 处理 / 输出要分开理解）。

### 本节课暂未学习的内容

~~视频逐帧追踪（`video_tracker.py` 的实现细节）~~（已在 L05 学习，见下一节）/ Calibration / 周期 / 频率 / FFT

（本节只学到"单张图从 Mask 到目标中心"的这条链；以上内容属于后续课程，本节只登记名称，不展开。）

---

## L05 从单张图片到视频：逐帧处理

- **课程编号**：L05
- **课程标题**：从单张图片到视频：逐帧处理与 video_tracker.py
- **学习状态**：已完成
- **记录日期**：2026-09-29
- **笔记文件**：[`L05_从单张图片到视频_逐帧处理.md`](L05_从单张图片到视频_逐帧处理.md)

### 本节课目标

- 用一句话说清视频与 Frame 的关系：视频可以理解成按时间顺序排列的一系列静态图片，每一帧是一个 Frame；
- 理解"视频不是一张巨大图片"：视频处理采用"一次拿一帧 → 处理 → 换下一帧"的方式；
- 理解 FPS（每秒多少帧）与时间采样：30 fps 时相邻帧间隔 1/30 s ≈ 0.033333 s，视频数据是离散采样，时间分辨率为 1/fps；
- 读懂 `time_s = frame_index / fps`（`track_video()` 第 494 行），理解 fps 从视频文件读取、未硬编码（第 130、153 行），并知道 fps <= 0 时程序停止处理（第 438～441 行）；
- 理解 `cv2.VideoCapture`（`open_video()` 第 125 行）的作用（从视频文件中读取帧的对象），以及 `cap.get()` 读取 fps、总帧数等属性（第 130～131 行）；
- 读懂 `cap.read()` 返回的两个值（第 444、527 行）：`ret` 表示是否成功读取，`frame` 是当前一张图像（BGR NumPy 数组）；
- 理解 `current_frame`（第 480 行初始化、第 532 行更新）表示"当前正在处理的那一帧"，不是整个视频，每次循环结束后被新的下一帧替换；
- 读懂 `track_video()` 的逐帧主循环（第 489～535 行）：检测 → 时间 → 写 CSV → 生成可视化 → 读取下一帧 → 判断结束 → 更新状态；
- 记住本节最重要的一句话："单张图片检测升级为视频处理，本质上是把同一个检测函数放进逐帧循环中"；
- 说清 `marker_detector.py` 与 `video_tracker.py` 的分工：前者回答"这一张图片里目标在哪里"，后者负责"视频什么时候读哪一帧、如何循环、如何记录结果、如何输出"（第 34 行导入、第 491 行调用）；
- 理解"处理当前帧 → 读取下一帧 → 判断是否结束"（第 491、497、527、528～530 行）的顺序保证最后一帧也被正常处理；
- 理解检测失败的规范：`detected=False`、坐标字段留空，绝不写 0 / -1 / nan / 字符串（第 399、410 行），即"测不到，就明确标记缺失，而不是制造一个假测量"；
- 理解 VideoWriter（`open_overlay_writer()` 第 252～253 行）与 Overlay Video 的用途（第 513～521 行写入）：人工检查检测框有没有跑偏、中心点有没有跟着目标、哪些帧检测失败；
- 理解 `release()` 与 `try / finally`（第 540～544 行）：即使中途异常或 Ctrl+C，也尽量完成资源清理（第 536～539 行）。

### 核心概念

1. 视频 = 按时间顺序排列的一系列静态图片；每一帧是一个 Frame；Frame 是实际的图像数组（BGR NumPy 数组），不是抽象概念；视频不是"一张巨大图片"；
2. 逐帧处理节奏："一次拿一帧 → 处理 → 换下一帧"；处理视频 = 对每一帧重复做单张图片能做的一切；
3. FPS 决定相邻帧的时间间隔：30 fps → 1/30 s ≈ 0.033333 s；视频数据是离散采样，只能在帧时刻取值，时间分辨率 = 1/fps；
4. `time_s = frame_index / fps`（第 494 行）：把帧号翻译成时间；frame_index 从 0 开始（第 481 行），所以第 0 帧 time_s = 0；CSV 中 time_s 写 6 位小数（第 404、410 行）；
5. fps 从文件读取（第 130 行）、未硬编码（第 153 行打印说明）；非法 fps（<= 0）时第 438～441 行释放资源并停止；
6. `cv2.VideoCapture(str(video_path))`（第 125 行）创建视频读取对象；打开失败明确返回 `(None, None)`（第 126～127 行）；`cap.get()` 可读 fps（第 130 行）、总帧数（第 131 行）、旋转元数据（第 134～137 行）；
7. `cap.read()` 返回 `(ret, frame)`：`ret` 是"是否成功读取"的布尔标志，`frame` 才是图像数据；判断结束看 ret（第 557 行），检测用 frame（第 491 行）；
8. 第一帧单独读取（第 444 行）用于确定程序实际处理的画面尺寸（第 456～463 行）；随后第 480 行 `current_frame = first_frame` 让第一帧直接进入循环处理，不浪费；
9. `current_frame` 是"当前正在处理的那一帧"：第 480 行初始化为 first_frame，第 532 行被替换为 next_frame；它不是整个视频，也不携带历史（历史靠 CSV 与 records 记账，第 497、499～510 行）；
10. 逐帧主循环（第 489 行 `while True`）：第 491 行 `detect_marker(current_frame)` → 第 494 行 `time_s` → 第 497 行写 CSV（每帧一行、失败也写）→ 第 513～521 行写叠加帧 → 第 527 行读下一帧 → 第 528～530 行判断结束 → 第 531～532 行更新 frame_index 与 current_frame；
11. 本节最重要的一句话："单张图片检测升级为视频处理，本质上是把同一个检测函数放进逐帧循环中"——`detect_marker()` 本身一行未改（复用 L02～L04）；
12. 模块化分工：`marker_detector.py` 负责"这一张图片里目标在哪里"；`video_tracker.py` 负责"视频什么时候读哪一帧、如何循环、如何记录结果、如何输出"；检测参数唯一来源是 `marker_detector.py`（第 19～21 行模块说明，第 34 行导入，第 491 行调用）；
13. 视频结束：第 527～530 行"读取下一帧 → 读不到就 break"；"处理当前帧 → 读取下一帧 → 判断是否结束"的顺序保证最后一帧也被处理；视频结束是正常终止，不是检测失败；
14. 检测失败：`detected=False`、坐标字段为空（第 399、410 行）；不写 0 / -1 / nan / 字符串；`check_csv_data()`（第 643 行起）用多条检查项验证这一点（第 736～740、794～818 行）；
15. VideoWriter：`open_overlay_writer()`（第 242～258 行）用第 252～253 行创建写入器，编码器候选 mp4v / avc1（第 47 行）；主流程第 513～521 行写入叠加帧；全部编码器失败时走代表性 PNG 回退（第 472、548～555 行）；
16. Overlay Video 的用途：人工检查检测框有没有跑偏、中心点有没有跟着目标、哪些帧检测失败（失败帧只显示 DETECTION FAILED，第 196～207 行）；它是检查工具，不是新的测量数据；
17. 资源清理：第 540～544 行 `finally` 中 `csv_file.close()` / `cap.release()` / `writer.release()`；配合 `try`（第 488 行）与 `except KeyboardInterrupt`（第 536～539 行），保证异常或中断时也尽量完成清理。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 视频追踪模块（本节源码主角） | `src\video_tracker.py` | `open_video` / `track_video` / `open_overlay_writer` / `build_csv_row` / `check_csv_data` 等实现（本节引用第 34、41、44、47、125～131、145、175、242～256、393～410、413、432～467、480～485、489～544、562～586、591、612、643 行） |
| 检测模块（被复用，未修改） | `src\marker_detector.py` | 提供 `detect_marker()`；检测参数的唯一来源（对应 L02～L04） |
| M3 视频追踪调用方 | `demo\run_video_tracking.py` | 第 35、37、38 行指定输入输出路径，第 43 行调用 `track_video()`，第 49 行打印统计，第 52～58 行 CSV 自检，第 63～66 行 SHA-256 对比 |
| 本节课笔记 | `docs\learning\L05_从单张图片到视频_逐帧处理.md` | 19 节完整笔记（含自测题 18 道，均不附答案） |
| 已存在的真实产物（只登记，未重新生成） | `results\EXP-002-VIDEO-001_track.csv` | 逐帧测量结果 CSV（表头 `frame,time_s,x_px,y_px,area_px,detected`） |
| 已存在的真实产物（只登记，未重新生成） | `results\EXP-002-VIDEO-001_overlay.mp4` | 叠加标注视频 |

### 本节课确认的源码事实

- 第 34 行：`from src.marker_detector import detect_marker`（模块分工与函数复用的入口）；
- 第 41 行：`CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`；
- 第 44、47、50 行：`OVERLAY_SCALE = 0.5`、`OVERLAY_CODECS = ("mp4v", "avc1")`、`MAX_FALLBACK_PNGS = 5`；
- 第 119 行：`def open_video(video_path):`；第 125 行：`cap = cv2.VideoCapture(str(video_path))`；第 126～127 行：打开失败返回 `(None, None)`；
- 第 130 行：`video_info["fps"] = float(cap.get(cv2.CAP_PROP_FPS))`；第 131 行：`video_info["frame_count"] = int(round(cap.get(cv2.CAP_PROP_FRAME_COUNT)))`；第 134～137 行：旋转元数据；第 140 行：`enable_orientation_auto(cap)`；
- 第 145 行：`def print_video_info(...)`；第 153 行：打印"实际 FPS：…（从当前视频文件读取，未硬编码）"；
- 第 175 行：`def draw_tracking_frame(...)`；第 196～207 行：检测失败时只显示 DETECTION FAILED，不画任何虚假中心；
- 第 242 行：`def open_overlay_writer(overlay_path, fps, frame_size):`；第 252 行：`fourcc = cv2.VideoWriter_fourcc(*codec_name)`；第 253 行：`writer = cv2.VideoWriter(str(overlay_path), fourcc, fps, (width, height))`；第 254～255 行：`writer.isOpened()` 后返回 `(writer, codec_name)`；第 256 行：失败候选 `writer.release()`；
- 第 305～313 行：`read_frame_at()`（PNG 回退时用 `cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)` 跳帧读取）；第 400 行：回退方案中 `result = detect_marker(frame)`；
- 第 393 行：`def build_csv_row(frame_index, time_s, result):`；第 399 行：文档字符串"失败时绝不写 0 / -1 / nan / 字符串"；第 401～409 行：成功行；第 410 行：失败行 `return [frame_index, "%.6f" % time_s, "", "", "", "False"]`；
- 第 413 行：`def track_video(video_path, csv_path, overlay_path):`；第 428 行：`sha256_before = compute_sha256(video_path)`；第 432 行：`cap, video_info = open_video(video_path)`；第 438～441 行：fps 非法时释放并停止；
- 第 444 行：`ret, first_frame = cap.read()`（第一次读取第一帧）；第 456～463 行：叠加视频 0.5 倍缩放与 `scale_x / scale_y`；第 465～467 行：`open_overlay_writer(...)`；
- 第 480～481 行：`current_frame = first_frame`、`frame_index = 0`；第 483～485 行：打开 CSV 并写表头；第 488 行：`try:`；
- 第 489 行：`while True:`；第 491 行：`result = detect_marker(current_frame)`；第 494 行：`time_s = frame_index / fps`；第 497 行：`csv_writer.writerow(build_csv_row(frame_index, time_s, result))`；第 499～510 行：每帧 `record` 记账；
- 第 513～521 行：`cv2.resize` → `draw_tracking_frame` → `writer.write(overlay)`（写叠加帧）；第 523～524 行：PNG 回退时累计清晰度指标；
- 第 527 行：`ret, next_frame = cap.read()`；第 528～530 行：`if not ret or next_frame is None: break`；第 531～532 行：`frame_index += 1`、`current_frame = next_frame`；第 534～535 行：每 200 帧打印进度；
- 第 536～539 行：`except KeyboardInterrupt:`（提示已处理数据仍保留）；第 540～544 行：`finally:` 中 `csv_file.close()` / `cap.release()` / `writer.release()`；
- 第 562～586 行：`summary` 统计字典；第 620 行：`compute_longest_miss_run`；第 612 行：`print_statistics`；第 643 行：`check_csv_data`（第 736～740、794～818 行的检查项验证"失败不伪造坐标"）。

### L05 源码地图

| 位置（`src\video_tracker.py`） | 内容 |
| --- | --- |
| 第34行 | 导入 `detect_marker`（`from src.marker_detector import detect_marker`） |
| `open_video()` 第125行 | `cv2.VideoCapture(str(video_path))` |
| 第130行 | 读取 FPS（`cap.get(cv2.CAP_PROP_FPS)`） |
| 第444行 | 读取第一帧（`ret, first_frame = cap.read()`） |
| 第480～481行 | 初始化 `current_frame = first_frame` 与 `frame_index = 0` |
| `track_video()` 第489行 | `while True:`（逐帧循环开始） |
| 第491行 | `result = detect_marker(current_frame)` |
| 第494行 | `time_s = frame_index / fps` |
| 第497行 | 记录当前帧（`csv_writer.writerow(...)`） |
| 第527行 | 读取下一帧（`ret, next_frame = cap.read()`） |
| 第528～530行 | 视频结束判断（`if not ret or next_frame is None: break`） |
| 第531～532行 | 更新帧号和 `current_frame`（`frame_index += 1`、`current_frame = next_frame`） |
| 第540～544行 | `release`（`finally` 中 `csv_file.close()` / `cap.release()` / `writer.release()`） |
| `open_overlay_writer()` 第252～253行 | VideoWriter（`VideoWriter_fourcc` / `cv2.VideoWriter`） |
| 第513～521行 | 写叠加帧（`cv2.resize` → `draw_tracking_frame` → `writer.write`） |

（行号按 2026-10-07 当前源码 `src\video_tracker.py`（共 836 行）逐行核对；如果实际源码行号发生变化，以当前真实源码为准。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L05 从单张图片到视频：逐帧处理"（Video、Frame、FPS、VideoCapture、cap.read、ret、current_frame、VideoWriter、Overlay Video、release、Frame Loop、Function Reuse、Module）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L05 从单张图片到视频：逐帧处理"（视频不是一张巨大图片、Frame 是实际的图像数组、FPS 决定时间间隔、ret 与 frame 不是一回事、current_frame 不等于整个视频、video_tracker 不重新发明检测算法、marker_detector 与 video_tracker 职责不同、检测失败不能伪造坐标、VideoWriter 是写不是读、用完资源要 release，以及循环顺序与"结束 ≠ 失败"）。

### 本节课暂未学习的内容

~~CSV 字段设计、records 记账与 check_csv_data 自检的细节~~（已在 L06 学习，见后续小节）/ Calibration（相机标定）/ 位移计算与毫米换算细节 / 周期 / 频率 / FFT

（本节只学到"视频 → 逐帧检测 → CSV 与叠加视频"这条链；以上内容属于后续课程，本节只登记名称，不展开。）

---

## L06 从逐帧结果到 CSV：数据记录、字段设计与时间序列

- **课程编号**：L06
- **课程标题**：从逐帧结果到 CSV：数据记录、字段设计与时间序列
- **学习状态**：已完成
- **记录日期**：2026-10-02
- **笔记文件**：[`L06_CSV与时间序列.md`](L06_CSV与时间序列.md)

### 本节课目标

- 说清"为什么逐帧结果不能只留在单个 `result` 变量里"：第 491 行每轮覆盖 `result`，没有历史、不能持久化、无法复核；
- 说出两条记录通道：磁盘 CSV（第 483～485 行打开并写表头、第 497 行每帧写一行）与内存 `records`（第 476、499～510 行）；
- 说清 CSV 的基本结构（纯文本、逗号分隔、一行一条记录、第一行是表头、表头前不加 metadata，第 40 行）；
- 用真实 CSV 讲清 row / column / header / cell，并在源码里定位写表头（第 485 行）、写行（第 497 行）、读表头与数据行（第 666～667 行）；
- 默写 `CSV_FIELDNAMES`（第 41 行）的 6 个字段与顺序，并说出每个字段的含义、来源与格式；
- 读懂 `build_csv_row()`（第 393～410 行）：输入 `frame_index` / `time_s` / `result`，输出一行 6 个 cell；成功行第 402～409 行、失败行第 410 行；
- 复述失败检测的 CSV 表达：`frame` / `time_s` 照写，`x_px` / `y_px` / `area_px` 留空，`detected=False`；理解为什么不是 0、-1、nan 或上一帧坐标（第 399 行；自检第 726～727、738、794～818 行）；
- 区分 `records` 与 CSV（内存工作副本 vs 磁盘正式产物；键名 `success` 第 502 行 vs 列名 `detected` 第 41 行）；
- 说清 CSV 怎样形成离散时间序列（每帧一行 + frame 连续 + `time_s = frame_index / fps` 均匀步长 + 失败行占位）；
- 说出 M3 `_track.csv` 与 M6 `_trajectory.csv` 的共同设计思想与字段差异（第 41 行 / 第 393～410 行 vs `src\external_oscillation_tracker.py` 第 87～96 行 / 第 337～377 行）；
- 会区分 VisionMotion 真实源码、教学概念伪代码与教学举例，不把后两者当作项目真实代码。

### 核心概念

1. **`result` 是单帧快照**：第 491 行每轮被重新赋值；历史必须另找容器保存；
2. **两条记录通道**：CSV 文件（第 483～485、497、541 行）与 `records` 列表（第 476、499～510 行），在同一逐帧循环里同步产生；
3. **CSV 基本结构**：纯文本、逗号分隔、一行一条记录、第一行是表头、表头前不加 metadata（第 40、483～485 行）；
4. **row / column / header / cell**：行 = 一条记录、列 = 一个字段、表头 = 第一行列名、cell = 行列交叉处一个值；读文件时 `header = rows[0]`（第 666 行）、`data_rows = rows[1:]`（第 667 行）；
5. **`CSV_FIELDNAMES`（第 41 行）**：`["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`，表头与列顺序的唯一来源；被第 485 行写表头、第 670～671 行校验表头、第 681 / 704 行校验每行列数依赖；
6. **`frame`**：帧编号从 0 开始（第 481 行），每轮 +1（第 531 行），成功 / 失败行都照写（第 403、410 行）；自检要求 0～N-1 连续（第 692～693 行）；
7. **`time_s`**：`time_s = frame_index / fps`（第 494 行），写 6 位小数（第 404、410 行）；fps 从视频文件读取（第 130 行），不是硬编码；
8. **`x_px` / `y_px`**：来自质心 `cx` / `cy`（第 405～406 行；源自 L04 的 `cx = m10 / m00`、`cy = m01 / m00`），2 位小数；失败时留空；
9. **`area_px`**：来自轮廓面积（第 407 行），1 位小数；是检测质量字段，不是运动测量量；
10. **`detected`**：写文本 `"True"` / `"False"`（第 408、410 行）；自检按字符串判断（第 736～737 行），第 10 项再用文本视角对空字段与 `detected=False` 对账（第 794～818 行）；
11. **`build_csv_row()`（第 393～410 行）**：一行 CSV 的"装配工"；成功行返回 5 个格式化字符串 + 1 个整数，失败行返回 `[frame_index, "%.6f" % time_s, "", "", "", "False"]`；
12. **失败表达原则（第 399 行）**："失败时绝不写 0 / -1 / nan / 字符串"；失败行三个测量字段留空，`detected=False`（第 410 行）；"测不到，就明确标记缺失，而不是制造一个假测量"；
13. **为什么不能用 0 / -1 / 上一帧坐标**：0 是合法坐标（自检第 726～727、738 行专门查 (0,0) 伪数据）；-1 / nan 会被当数值参与计算；上一帧坐标是伪造测量，事后无法分辨；
14. **`records` vs CSV**：内存列表 vs 磁盘文件；字典键可多可少 vs 固定 6 列；原始数值 vs 格式化文本；统计 / 回退用 vs 正式数据用；`success`（第 502 行）对应 `detected`（第 41 行）；
15. **离散时间序列**：一行 = 一个离散时刻的一次测量；每帧一行（第 497 行）+ frame 连续（第 692～693 行）+ 均匀步长 `1/fps`（第 494 行）+ 失败行占位 = 可继续分析的离散时间序列；
16. **M3 与 M6 的共同设计与差异**：共同点是"模块级 `CSV_FIELDNAMES` 单一来源、表头前无 metadata、每帧一行、失败留空 + False、时间格式 `%.6f`、行尾 `\n`、有表头自检"；差异在字段选择（`y_px` vs `y0_px`、M6 多 `bbox_w_px` / `bbox_h_px`、`detected` 列位置、覆盖区间、`csv.writer` vs `csv.DictWriter`）。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 数据记录模块（本节源码主角） | `src\video_tracker.py` | `CSV_FIELDNAMES`（第 41 行）、`build_csv_row()`（第 393～410 行）、`track_video()`（第 413 行起）、`records`（第 476、499～510 行）、`compute_longest_miss_run()`（第 591～604 行）、`check_csv_data()`（第 643～824 行） |
| M3 数据产物（只读引用，未重新生成） | `results\EXP-002-VIDEO-001_track.csv` | 表头 `frame,time_s,x_px,y_px,area_px,detected`；170 行数据（frame 0～169）；时间步 0.041667 s（24 fps）；170/170 全 True |
| M6 字段设计对比对象 | `src\external_oscillation_tracker.py` | `CSV_FIELDNAMES`（第 87～96 行）、`write_trajectory_csv()`（第 337～377 行）；本课只做字段设计对比，不展开其算法 |
| M6 数据产物（只读引用，未重新生成） | `results\EXP-EXT-LAB67-V1_trajectory.csv` | 表头 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`；160 行数据（frame 76～235）；时间步 0.033333 s（30 fps）；160/160 全 True |
| 检测结果来源（被复用，未修改） | `src\marker_detector.py` | `detect_marker()`（第 105 行）返回 `success` / `cx` / `cy` / `area` / `bbox`（第 143～150 行）；`cx` / `cy` 公式（第 100～102 行） |
| 本节课笔记 | [`L06_CSV与时间序列.md`](L06_CSV与时间序列.md) | 19 节完整笔记（含自测题 18 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- 第 41 行：`CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`；
- 第 393～410 行：`build_csv_row()`（第 397～399 行格式说明与失败规则、第 401～409 行成功行、第 410 行失败行）；
- 第 413 行：`def track_video(video_path, csv_path, overlay_path):`；第 428 行：运行前 SHA-256；第 432 行：`open_video()`；
- 第 476 行：`records = []`；第 477 行：`sharpness_list = []`（仅回退方案使用）；
- 第 483 行：`csv_file = open(csv_path, "w", encoding="utf-8", newline="")`；第 484 行：`csv_writer = csv.writer(csv_file, lineterminator="\n")`；第 485 行：`csv_writer.writerow(CSV_FIELDNAMES)`；
- 第 489 行：`while True:`；第 491 行：`result = detect_marker(current_frame)`；第 494 行：`time_s = frame_index / fps`；第 497 行：`csv_writer.writerow(build_csv_row(frame_index, time_s, result))`；
- 第 499～510 行：`record` 字典（第 499～503 行）、成功时补 `cx` / `cy` / `area`（第 504～509 行）、`records.append(record)`（第 510 行）；
- 第 527～532 行：读下一帧（第 527 行）、结束判断（第 528～530 行）、`frame_index += 1`（第 531 行）、`current_frame = next_frame`（第 532 行）；
- 第 536～539 行：`except KeyboardInterrupt:`；第 540～544 行：`finally:` 中 `csv_file.close()`（第 541 行）、`cap.release()`（第 542 行）、`writer.release()`（第 544 行）；
- 第 562～586 行：`summary` 统计（帧数、检出率、最长连续丢失、面积统计、首末时间等）；第 591～604 行：`compute_longest_miss_run()`；
- 第 643～824 行：`check_csv_data()`（第 666～667 行 header / data_rows、第 670～671 行表头、第 674～675 行行数、第 678～689 行 frame 整数、第 692～693 行 frame 连续、第 700～740 行成功行 / 失败行 / (0,0) 伪数据 / 坐标范围、第 742～783 行 `time_s` 时间轴一致性、第 794～818 行空测量字段与 `detected=False` 语义对账）；
- M6 对照：`src\external_oscillation_tracker.py` 第 86～96 行表头、第 337～377 行 `write_trajectory_csv()`（第 341 行失败留空说明、第 348～349 行 `DictWriter` / `writeheader()`、第 350～363 行成功行、第 364～376 行失败行）、第 434～435 行表头自检。

### L06 源码地图

| 位置（`src\video_tracker.py`） | 内容 |
| --- | --- |
| 第41行 | `CSV_FIELDNAMES`（表头与列顺序的唯一来源） |
| 第393～410行 | `build_csv_row()`（一行 CSV 的装配；成功行第 401～409 行，失败行第 410 行） |
| 第413行 | `track_video()` 定义 |
| 第476行 | `records = []`（每帧一条记录） |
| 第483～485行 | 打开 CSV、创建 writer、写表头 |
| 第489行 | `while True:`（逐帧循环） |
| 第491行 | `result = detect_marker(current_frame)` |
| 第494行 | `time_s = frame_index / fps` |
| 第497行 | `csv_writer.writerow(build_csv_row(...))`（每帧一行） |
| 第499～510行 | `record` 记账与 `records` 追加 |
| 第527～532行 | 读下一帧、结束判断、更新 `frame_index` / `current_frame` |
| 第541行 | `csv_file.close()`（`finally`，与第 542、544 行同组） |
| 第562～586行 | `summary` 统计字典 |
| 第591～604行 | `compute_longest_miss_run()` |
| 第643～824行 | `check_csv_data()`（CSV 完整性自检，10 项） |

（行号按 2026-10-07 当前源码 `src\video_tracker.py`（共 836 行）逐行核对；如果实际源码行号发生变化，以当前真实源码为准。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L06 从逐帧结果到 CSV：数据记录、字段设计与时间序列"（Row、Column、Header、Cell、CSV_FIELDNAMES、build_csv_row、writerow、lineterminator、records、Missing Value、Discrete Time Series、Field Design、csv.DictWriter 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L06 从逐帧结果到 CSV：数据记录、字段设计与时间序列"（result 每轮覆盖、CSV 不是 Excel、表头与数据行、失败写 0 / -1 / 上一帧坐标、失败行跳过、records 与 CSV 混用、time_s 硬编码、字段随意改动、M3 / M6 字段混用、教学示例与真实源码不分等）。

### 本节课暂未学习的内容

Calibration（相机标定）/ 位移计算与毫米换算 / FFT / 频率 / 周期 / `external_oscillation_tracker.py` 的算法细节 / pandas / 数据库 / 高级数据分析（平滑、插值、拟合等）

（本节只学到"逐帧结果 → CSV 记录 → 字段设计 → 离散时间序列"这条链；以上内容属于后续课程或本阶段刻意不引入的工具，本节只登记名称，不展开。）

---

## L07 检测失败、质量检查与鲁棒性

- **课程编号**：L07
- **课程标题**：检测失败、质量检查与鲁棒性
- **学习状态**：已完成
- **记录日期**：2026-10-02
- **笔记文件**：[`L07_检测失败与鲁棒性.md`](L07_检测失败与鲁棒性.md)

### 本节课目标

- 用一句话说清"检测成功"与"检测失败"的区别：成功 = 测到了并给出测量值；失败 = 这一帧没有可用的测量值；
- 说清"检测失败 ≠ 程序崩溃"：失败是 `detect_marker()` 的正常返回值，程序不抛异常、不中断整段视频，只把这一帧如实标记为缺失；
- 按顺序说出 `src\marker_detector.py` 的三道失败判定：无轮廓（第 75～76 行）、最大轮廓面积 < `MIN_AREA`（第 83～84 行）、`m00 == 0` 无法算质心（第 97～98 行）；
- 区分三种"失败的返回"：`find_target_contour()` / `calculate_centroid()` 的 `None`（第 76、84、98 行）、`detect_marker()` 的 `{"success": False, "mask": mask}`（第 133、137 行）、CSV 失败行（第 410 行）；
- 解释为什么失败返回结构里没有 `cx` / `cy` / `area` / `bbox` / `contour`：这些键只在成功分支（第 143～151 行）写入；使用方必须先看 `success` 再取字段；
- 说出 `detected=False` 与 CSV 空字段的对应（第 401、410 行），并解释为什么缺失不能用 `0` / `-1` / `nan` / 上一帧坐标代替（第 399 行；自检第 726～727、738、794～818 行）；
- 说出 `records` 如何记录失败：三条固定键 `frame` / `time_s` / `success`，成功才追加 `cx` / `cy` / `area`（第 499～510 行，`append` 在 `if` 外）；
- 说出 `draw_tracking_frame()`（第 175～239 行）失败帧只显示 "DETECTION FAILED"（第 196～207 行）、不画虚假中心；成功帧画绿框 + 圆圈 + 十字 + 坐标文字（第 209～237 行）；
- 解释"中间坏帧为什么不会让整个视频处理停止"：循环里没有因 `success=False` 而退出的路径；唯一 `break` 是"读不到下一帧"（第 527～530 行）；
- 读懂 `compute_longest_miss_run()`（第 591～604 行）：最长连续丢失帧数；返回 0 ⇔ 整段无失败帧；
- 说出 `detection_rate` 的来源（第 570～573 行，打印于第 625 行）与局限：不反映失败分布、不校验数值合理性（要配合 `longest_miss_run` 与十项检查）；
- 逐条说出 `check_csv_data()` 的十项检查（第 643～824 行）：表头（第 670～671 行）、行数（第 674～675 行）、frame 合法（第 678～689 行）与连续（第 692～693 行）、成功行数值（第 736 行）、失败行留空（第 737 行）、无 (0,0) 伪数据（第 726～727、738 行）、坐标范围（第 728～729、739～740 行）、`time_s` 时间轴一致性（第 742～783 行，第 9 项）、CSV 空测量字段与 `detected=False` 语义对账（第 794～818 行，第 10 项）；第 823 行十项全过才算通过；
- 解释 `area_px` 的质量意义：`MIN_AREA = 200` 是进门门槛（第 33、83～84 行）；运行期统计 min / median / max（第 575～577 行）并打印（第 629～631 行）；面积异常是"测量可疑"的线索；
- 说出 M3 与 M6 对失败的不同质量门槛：M3 允许失败但要求诚实（第 730～732、737、794～818 行）；M6 的 `check_trajectory_csv()` 把 "detected 全为 True"（`external_oscillation_tracker.py` 第 452～455 行）、空值 0（第 457～459 行）、无 >30 px 突跳（第 480～483 行）、无候选歧义（第 485～492 行）、时间严格（第 494～501 行）列为硬性门槛；
- 给出"质量检查"与"鲁棒性"的定义；理解本项目"鲁棒 ≠ 检出率 100%"：鲁棒 = 坏情况被如实记录、可被发现、不伪造数据；
- 解释"证据边界"：哪些结论由源码支持、哪些由真实 CSV 支持、哪些不能声称；养成诚实记录实验数据的习惯；
- 永远分清五类材料：真实源码、真实 CSV 数据、概念解释、教学示例、概念伪代码。

### 核心概念

1. **检测成功**：`detect_marker()` 返回 `success=True` + `cx` / `cy` / `area` / `bbox` / `contour` / `mask`（`marker_detector.py` 第 143～151 行）；含义 = "这一帧有可用测量值"；
2. **检测失败**：三道判定（第 75～76、83～84、97～98 行）任一触发，返回 `{"success": False, "mask": mask}`（第 133、137 行）；含义 = "这一帧没有可用测量值"，不是崩溃；
3. **三道失败判定**：无外部轮廓（第 75～76 行）；最大轮廓面积 < `MIN_AREA = 200`（第 33、83～84 行）；`m00 == 0` 质心不可算（第 97～98 行）；
4. **失败的三种表达**：函数级 `None`（第 76、84、98 行）→ 模块级 `success=False` 字典（第 133、137 行）→ 文件级失败行（第 410 行）；逐级翻译；
5. **失败返回没有测量键**：`cx` / `cy` / `area` / `bbox` / `contour` 只在成功分支存在；`mask` 保留（与第 129 行同一次计算，可作诊断）；调用方"先看 success，再取字段"（第 401、196～207 行两处示范）；
6. **CSV 失败行（第 410 行）**：`[frame_index, "%.6f" % time_s, "", "", "", "False"]`；frame / time_s 照写、三个测量字段留空、`detected=False`；
7. **缺失不伪造原则（第 399 行）**："失败时绝不写 0 / -1 / nan / 字符串"；0/-1 会被当数值污染统计；nan 文本分不清来源；上一帧坐标是假测量；自检第 726～727、738 行查 (0,0)，第 794～818 行查空字段与 `detected=False` 对账；
8. **为什么 (0,0) 可疑（第 726～727 行）**：图像原点在左上角，真实目标恰在 (0,0) 概率极低；它是"没算出来却写默认值"的典型痕迹；
9. **records 的失败记录（第 499～510 行）**：`record` 固定三键 `frame` / `time_s` / `success`；成功才补 `cx` / `cy` / `area`（第 504～509 行）；`records.append(record)` 在 `if` 外（第 510 行）→ 失败帧同样占一条；
10. **draw_tracking_frame()（第 175～239 行）**：失败分支（第 196～207 行）只写红色 "DETECTION FAILED" 并 `return overlay`；成功分支（第 209～237 行）画绿框、圆圈、十字、`center=(cx, cy) px`；
11. **坏帧不中断**：逐帧循环不按 `success` 决定去留；写 CSV（第 497 行）→ 记 records（第 499～510 行）→ 画帧（第 512～524 行）→ 读下一帧（第 527 行）；唯一 `break` 在第 528～530 行（读不到下一帧）；
12. **compute_longest_miss_run()（第 591～604 行）**：成功清零、失败累加并刷新最大值；返回"最长连续丢失帧数"；`0` ⇔ 没有失败帧；被 `summary` 使用（第 574 行）、第 627 行打印；
13. **detection_rate（第 570～573 行）**：`detected_count / len(records)`；第 625 行以 `%.4f%%` 打印；局限 = 不反映失败分布、不校验数值合理性；
14. **check_csv_data() 十项检查（第 643～824 行）**：①表头（第 670～671 行）②行数（第 674～675 行）③frame 合法（第 678～689 行）④frame 连续（第 692～693 行）⑤成功行数值（第 736 行）⑥失败行留空（第 737 行）⑦无 (0,0)（第 726～727、738 行）⑧坐标范围（第 728～729、739～740 行）⑨`time_s` 与 `frame / fps` 时间轴一致性（第 742～783 行）⑩CSV 空测量字段与 `detected=False` 语义对账（第 794～818 行）；第 823 行 `passed = all(...)`；
15. **坐标范围检查（第 728～729 行）**：`0 ≤ x ≤ frame_width` 且 `0 ≤ y ≤ frame_height`；尺寸由调用方传入（`demo\run_video_tracking.py` 第 55～56 行），不是硬编码；
16. **空测量字段与 detected=False 对应（第 794～818 行）**：`detected=False` 的行测量字段必须全空、空 `x_px` 行数必须等于 `detected=False` 行数（第 817 行判定），否则自检不通过；现行实现不再使用 `np.genfromtxt`；
17. **area 质量意义**：进门门槛 `MIN_AREA = 200`（第 33、83～84 行）；成功帧面积写入 CSV（第 407 行）；`summary` 统计 min / median / max（第 575～577 行）、第 629～631 行打印；面积偏离平时水平 = 遮挡 / 距离 / 模糊 / 干扰的线索；本课不做自动异常检测，只提示人工核对；
18. **M3 与 M6 的不同质量门槛**：M3（记录型）= 允许失败但要求诚实（第 730～732、737、794～818 行）；M6（分析型）= 要求 100% 检出 + 无空值 + 无突跳 + 无歧义 + 时间严格（`external_oscillation_tracker.py` 第 452～501 行）；差异来自下游用途不同；
19. **质量检查定义**：以磁盘上的产物为对象、只读、逐项规则验证、给出显式通过 / 不通过（第 645、662～664、823 行）；
20. **鲁棒性定义**：坏情况来临时"不崩溃、不伪造、不丢时间轴、不被坏帧拖垮、把问题暴露出来"；鲁棒 ≠ 检出率 100%；
21. **证据边界**：本课两份真实 CSV 都是 100% 检出、0 失败帧（第 16 节统计），所以失败处理是"设计可核对、实测未触发"；诚实记录 = 不把"设计上支持"写成"实测已发生"。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 检测器（三道失败判定的源码主角） | `src\marker_detector.py` | `find_target_contour()`（第 66～86 行；第 75～76、83～84 行失败）、`calculate_centroid()`（第 89～102 行；第 97～98 行失败）、`detect_marker()`（第 105～151 行；第 132～133、136～137 行失败返回） |
| 记录与检查模块（本节第二主角） | `src\video_tracker.py` | `draw_tracking_frame()`（第 175～239 行；DETECTION FAILED 第 196～207 行）、`build_csv_row()`（第 393～410 行；原则第 399 行、失败行第 410 行）、`records`（第 476、499～510 行）、`summary`（第 562～586 行）、`compute_longest_miss_run()`（第 591～604 行）、`print_statistics()`（第 612～635 行）、`check_csv_data()`（第 643～824 行；`time_s` 时间轴第 742～783 行、失败字段语义对账第 794～818 行、汇总第 823 行） |
| 调用方 | `demo\run_video_tracking.py` | 第 49 行 `print_statistics()`；第 52～58 行 `check_csv_data()` 与 `print_check_results()`（传入 `summary["width"]` / `["height"]`） |
| M6 质量门槛对照 | `src\external_oscillation_tracker.py` | `check_trajectory_csv()`（第 422～505 行；100% 检出第 452～455 行、空值第 457～459 行、突跳第 480～483 行、歧义第 485～492 行、时间第 494～501 行）；本课不展开其检测算法 |
| M3 数据产物（只读核对，未重新生成） | `results\EXP-002-VIDEO-001_track.csv` | 表头 6 列；170 行（frame 0～169）；170/170 全 True、0 失败行、0 空字段；时间 0.000000～7.041667 s（24 fps）；x 618.28～1195.0、y 91.74～351.89；area 24409.0 / 64846.25 / 105163.5 |
| M6 数据产物（只读核对，未重新生成） | `results\EXP-EXT-LAB67-V1_trajectory.csv` | 表头 8 列；160 行（frame 76～235）；160/160 全 True、0 失败行、0 空字段；时间 2.533333～7.833333 s（≈ 30 fps）；x 718.5～728.0、y0_px 508.0～622.0；area 226 / 508.5 / 658 |
| 本节课笔记 | [`L07_检测失败与鲁棒性.md`](L07_检测失败与鲁棒性.md) | 24 节完整笔记（含自测题 18 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- 第 33 行：`MIN_AREA = 200`；
- 第 66～86 行：`find_target_contour()`；第 73 行 `findContours`；第 75～76 行无轮廓 `return None`；第 79～80 行按面积降序取最大；第 83～84 行 `< MIN_AREA` 则 `return None`；第 86 行返回最大轮廓；
- 第 89～102 行：`calculate_centroid()`；第 95 行 `cv2.moments`；第 97～98 行 `m00 == 0` 则 `return None`；第 100～102 行 `cx = m10 / m00`、`cy = m01 / m00`；
- 第 105～151 行：`detect_marker()`；第 129 行生成掩膜；第 131～133 行轮廓失败返回 `{"success": False, "mask": mask}`；第 135～137 行质心失败同样返回；第 139～141 行成功路径算 `cx` / `cy` / `area` / `bbox`；第 143～151 行成功字典；
- `src\video_tracker.py` 第 175～239 行：`draw_tracking_frame()`；第 182 行 `copy()`；第 185～194 行帧号 / 时间；第 196～207 行失败分支 "DETECTION FAILED" + `return overlay`；第 210～218 行坐标缩放；第 221～225 行绿框 / 圆圈 / 十字；第 228～237 行坐标文字；
- 第 393～410 行：`build_csv_row()`；第 397～399 行格式与"失败时绝不写 0 / -1 / nan / 字符串"；第 401～409 行成功行；第 410 行失败行 `[frame_index, "%.6f" % time_s, "", "", "", "False"]`；
- 第 476 行：`records = []`；第 496 行注释"每帧一行，检测失败也要写"；第 497 行 `csv_writer.writerow(...)`；第 499～510 行 `record` 组装与追加（第 504～509 行成功补键；第 510 行 `records.append` 在 `if` 外）；
- 第 527～530 行：读下一帧；读不到才 `break`（唯一按设计的循环退出路径）；第 536～539 行 `KeyboardInterrupt`；
- 第 562～586 行：`summary`（第 570～573 行四个帧数 / 率统计；第 574 行 `longest_miss_run`；第 575～577 行 area 统计）；
- 第 591～604 行：`compute_longest_miss_run()`；第 612～635 行：`print_statistics()`（第 624～627 行检出统计、第 629～631 行 area 统计）；
- 第 643～824 行：`check_csv_data()` 十项检查（第 670～671、674～675、678～689、692～693 行四项结构与 frame 检查；第 700～740 行成功 / 失败行遍历与第 726～727 行 (0,0)、第 728～729 行范围、第 730～732 行失败行留空；第 736～740 行四项判定；第 742～783 行第 9 项 `time_s` 时间轴一致性；第 794～818 行第 10 项空测量字段与 `detected=False` 语义对账；第 823 行汇总）；
- `src\external_oscillation_tracker.py`：第 87～96 行 8 列字段；第 99～100 行 `MAX_JUMP_PX = 30.0` / `TIME_TOLERANCE_S = 1e-5`；第 119～132 行 `verify_video_sha256()`；第 337～377 行 `write_trajectory_csv()`（失败行第 364～376 行）；第 380～403 行 `load_trajectory_csv()`（空字段 → `None` 第 397～399 行）；第 422～505 行 `check_trajectory_csv()`（第 452～455、457～459、467～472、475～478、480～492、494～501 行；第 503 行注释与第 504 行汇总）。

### L07 源码地图

| 位置 | 内容 |
| --- | --- |
| `src\marker_detector.py` 第 66～86 行 | `find_target_contour()`（失败第 75～76、83～84 行） |
| `src\marker_detector.py` 第 89～102 行 | `calculate_centroid()`（失败第 97～98 行） |
| `src\marker_detector.py` 第 105～151 行 | `detect_marker()`（失败返回第 132～133、136～137 行；成功字典第 143～151 行） |
| `src\video_tracker.py` 第 175～239 行 | `draw_tracking_frame()`（失败显示第 196～207 行） |
| `src\video_tracker.py` 第 393～410 行 | `build_csv_row()`（原则第 399 行、失败行第 410 行） |
| `src\video_tracker.py` 第 476、499～510 行 | `records` 初始化与成功 / 失败记账 |
| `src\video_tracker.py` 第 527～530 行 | 唯一的循环退出：读不到下一帧 |
| `src\video_tracker.py` 第 562～586 行 | `summary`（第 570～574 行检测统计） |
| `src\video_tracker.py` 第 591～604 行 | `compute_longest_miss_run()` |
| `src\video_tracker.py` 第 612～635 行 | `print_statistics()` |
| `src\video_tracker.py` 第 643～824 行 | `check_csv_data()`（十项检查；第 726～729、730～737、742～783、794～818、823 行） |
| `src\external_oscillation_tracker.py` 第 422～505 行 | M6 独立质量检查（100% 检出第 452～455 行等） |

（行号按 2026-10-07 当前源码 `src\marker_detector.py`（共 151 行）、`src\video_tracker.py`（共 836 行）、`src\external_oscillation_tracker.py`（共 614 行）逐行核对；如果实际源码行号发生变化，以当前真实源码为准。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L07 检测失败、质量检查与鲁棒性"（Detection Failure、DETECTION FAILED、detection_rate、longest_miss_run、Quality Check、Robustness、(0,0) 伪数据、Evidence Boundary 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L07 检测失败、质量检查与鲁棒性"（把失败当崩溃、以为失败字典里有 cx/cy 键、伪造缺失值、把 DETECTION FAILED 当装饰、以为坏帧会中断视频、只看 detection_rate、把 NaN 当写文件标记、M3 / M6 检查口径混用、把设计当实测等）。

### 本节课暂未学习的内容

Kalman filter / 深度学习 / YOLO / 复杂跟踪算法（ROI 搜索、光流）/ 高级异常检测 / 复杂统计学习；~~位移计算、Calibration~~（已在 L08 学习，见下一节）；FFT、频率 / 周期仍属于后续课程。

（本节只学到"失败判定 → 失败表达 → 统计与质量检查 → 鲁棒性与证据边界"这条链；以上内容属于后续课程或本阶段刻意不引入的工具，本节只登记名称，不展开。）

---

## L08 为什么像素不能直接当毫米（像素与毫米标定）

- **课程编号**：L08
- **课程标题**：为什么像素不能直接当毫米（像素与毫米标定）
- **学习状态**：已完成
- **记录日期**：2026-10-02
- **笔记文件**：[`L08_像素与毫米标定.md`](L08_像素与毫米标定.md)

### 本节课目标

- 说清图像坐标系（单位 px、原点左上、x 向右、y 向下）与物理世界坐标系（单位 mm、由现实测量约定方向）的区别；
- 写出并区分四个单位：`px`、`mm`、`px/mm`（每毫米多少像素）、`mm/px`（每像素多少毫米）；
- 解释"为什么一个像素不能被视为固定的现实长度"：像素是采样格子，尺度由本次拍摄几何决定；
- 说出四类影响像素尺度的因素：拍摄距离、镜头（视场 / 焦距）、分辨率（画幅）、图像缩放（重采样 / 裁剪 / 数码变焦）；
- 解释"为什么必须使用已知真实长度做 calibration"：只有两个像素点只能得到像素距离；尺度必须由 `L_real` 确定；
- 说出 `src\calibration.py` 的模块性质：纯数学模块，不读视频、不读图片、不写文件、不使用 OpenCV，只 `import math`（第 6、24 行）；
- 说出 `compute_scale()` 的作用（第 100～144 行）：两点 + 真实距离 → `pixel_distance` / `px_per_mm` / `mm_per_px`；
- 说出 `pixel_distance`、`px_per_mm`、`mm_per_px` 的关系（互为倒数；`pixel_distance = px_per_mm × real_distance_mm`）；
- 说出 `unit_direction()`（第 147～173 行）与 `project_point()`（第 176～204 行）的最小认识；完整推导留到 L09；
- 背出 M4 的 `PX_PER_MM = 5.756961`、`MM_PER_PX = 0.173703`（`src\displacement.py` 第 52～53 行）；
- 背出 M5 的 `PX_PER_MM_004 = 6.086399`、`MM_PER_PX_004 = 0.164301`（`src\dynamic_displacement.py` 第 64～65 行）；
- 解释 M4 与 M5 为什么必须分开使用（尺度差约 5.72%；专属常量 + 禁止 import + 专属 gate）；
- 写出 `ds_px → ds_mm` 换算（`ds_mm = ds_px / PX_PER_MM`，M5 用 `PX_PER_MM_004`）与双重舍入细节；
- 解释 M6 外部视频为什么没有 mm 列（模块禁止标定与位移换算；没有已知真实长度）；
- 执行原则"没有有效标定就只能停留在像素层面"；
- 说清字段命名事实：不存在 `x0_px`；`y0_px` 里的 `0` 是字段名的一部分；
- 永远分清五类材料：真实源码 / 真实数据 / 教学示例 / 概念解释 / 概念伪代码。

### 核心概念

1. **两套坐标系**：图像坐标系（px，原点左上，x 向右、y 向下，`src\calibration.py` 第 9～10 行）与物理世界坐标系（mm，由标定用的已知真实长度定义）；
2. **四个单位**：`px` 画面上格子数；`mm` 现实长度；`px/mm = k` 每毫米多少像素；`mm/px = 1 / k` 每像素多少毫米；
3. **像素不是固定长度**：像素覆盖的是角度范围；同样的现实长度在不同拍摄条件下占不同像素数（M4 与 M5 的尺度相差约 5.72%）；
4. **四个影响因素**：拍摄距离、镜头（视场 / 焦距）、分辨率（M4 标定绑定 `1920 × 1080`，`src\displacement.py` 第 42～43 行）、图像缩放；
5. **标定 = 两点 + 已知真实长度**：`compute_scale()`（第 100～144 行）输入 `point1` / `point2` / `real_distance_mm`，输出三个量；`real_distance_mm <= 0` 报错（第 125～126 行）；两点重合报错（第 134～135 行）；
6. **像素距离公式**（第 128～131 行）：`dx = x2 - x1`、`dy = y2 - y1`、`pixel_distance = math.hypot(dx, dy)`；
7. **两个尺度互为倒数**（第 137～138 行）：`px_per_mm = pixel_distance / real_distance_mm`、`mm_per_px = real_distance_mm / pixel_distance`；
8. **`src\calibration.py` 是纯数学模块**：只 `import math`（第 24 行），无 OpenCV、无文件读写；
9. **M4 标定**（`src\displacement.py` 第 41～55 行）：来源 EXP-003-STATIC-002 frame 900 的 1920×1080 坐标系；P1 (1036.23, 490.58)、P2 (1381.64, 488.20)、60.0 mm；`PX_PER_MM = 5.756961`、`MM_PER_PX = 0.173703`、`U = (0.999976, -0.006894)`；
10. **M5 标定**（`src\dynamic_displacement.py` 第 59～66 行）：EXP-004 专属（人工点击 + 独立核验）；P1 (813.50, 296.49)、P2 (1422.13, 294.11)、100.0 mm；`PX_PER_MM_004 = 6.086399`、`MM_PER_PX_004 = 0.164301`、`U_004 = (0.999992, -0.003913)`；
11. **M4 与 M5 必须分开**：两次拍摄几何不同；`src\dynamic_displacement.py` 第 20～23 行禁止把 M4 常量搬进来、禁止 `import src.displacement`；第 68～76 行专属 gate 写明"与 M4 gate 完全不同，不得混用"；
12. **ds_px → ds_mm**：`src\displacement.py` 第 368～369 行、`src\dynamic_displacement.py` 第 378～379 行；`ds_mm` 是换算结果，不是另一次测量；
13. **双重舍入**：文件里的 `ds_mm` 由未舍入的 `ds_px` 算出再舍入；用已舍入的 `ds_px` 反算可能出现 ±0.0001 的差（自检容差 0.0005 mm，第 736 / 1143 行）；
14. **M6 无 mm 列**：`src\external_oscillation_tracker.py` 第 31～34 行明文禁止标定与位移换算；8 列表头（第 87～96 行）没有 `s_px` / `ds_px` / `ds_mm`；
15. **原则**：没有有效标定就只能停留在像素层面；有标定也要说清是哪一次拍摄；
16. **字段事实**：不存在 `x0_px`；存在 `x_px`、`y_px`、`s_px`、`ds_px`、`ds_mm`、`y0_px`；`y0_px` 的 `0` 是字段名的一部分；
17. **L09 边界**：本课只登记 `unit_direction()` / `project_point()` 的名称与作用；标定点选择、方向推导、归一化细节、投影几何留到 L09。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 标定模块（本课主角，纯数学） | `src\calibration.py` | 第 1～22 行模块说明与公式；第 24 行 `import math`；第 32～43 行 `_to_float()`；第 46～70 行 `_check_point()`；第 73～92 行 `_check_direction()`；第 100～144 行 `compute_scale()`（第 125～126 行真实距离 > 0；第 128～131 行 `dx` / `dy` / `pixel_distance`；第 134～135 行两点重合；第 137～138 行两个尺度；第 140～144 行返回）；第 147～173 行 `unit_direction()`；第 176～204 行 `project_point()`（第 180 行公式说明；第 204 行 `return x * ux + y * uy`） |
| M4 常量与 mm 换算 | `src\displacement.py` | 第 41～47 行标定来源说明（第 44～46 行 P1 / P2 / 真实距离）；第 48～50 行常量；第 52～53 行 `PX_PER_MM` / `MM_PER_PX`；第 55 行 `U`；第 57～64 行 M4 gate；第 72～81 行 `DS_FIELDNAMES`；第 98～150 行冻结常量自检；第 357～369 行 `add_displacement()`（第 368～369 行换算公式）；第 759～777 行 ds 公式复算 |
| M5 常量与 mm 换算 | `src\dynamic_displacement.py` | 第 20～23 行 EXP-004 专属与"不得 import src.displacement"；第 40 行只 import `project_point`；第 59 行冻结说明；第 60～62 行 P1 / P2 / 100.0 mm；第 64～66 行常量；第 68～76 行专属 gate；第 121～174 行冻结常量自检；第 367～379 行 `add_displacement()`（第 378～379 行换算公式）；第 1132～1151 行 ds 公式复算 |
| M6 边界对照（无 mm 列的原因） | `src\external_oscillation_tracker.py` | 第 4～9 行外部数据集标注；第 19～20 行正式位置特征与帧区间；第 31～34 行"不做：标定（px/mm）、位移换算…"；第 84 行 `POSITION_FEATURE_NAME`；第 87～96 行 8 列表头；第 337～377 行写 CSV |
| 调用方 | `demo\run_m43_displacement.py`、`demo\run_m52_dynamic_displacement.py` | 第 63～67、146～158、215～222 行（M4 三视频共用常量与冻结自检）；第 72～98、165～166 行（M5 冻结常量打印与运行） |
| M4 数据产物（只读核对，未重新生成） | `results\EXP-003-STATIC-002_ds.csv` | 表头 8 列；1961 行（frame 0～1960）；valid 1050 / 911；ds_px -1.249～350.268；ds_mm -0.2170～60.8426 |
| M4 数据产物（只读核对，未重新生成） | `results\EXP-003-STATIC-003_ds.csv` | 表头 8 列；1984 行（frame 0～1983）；valid 1192 / 792；ds_px -0.311～346.530；ds_mm -0.0540～60.1932 |
| M5 数据产物（只读核对，未重新生成） | `results\EXP-004-DYNAMIC-001_ds.csv` | 表头 8 列；1766 行（frame 0～1765）；valid 1766 / 0；ds_px -3.215～402.715；ds_mm -0.5283～66.1663 |
| M6 数据产物（只读核对，未重新生成） | `results\EXP-EXT-LAB67-V1_trajectory.csv` | 表头 8 列 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`（无 mm 列）；160 行（frame 76～235）；x_px 718.5～728.0；y0_px 508～622 |
| 本节课笔记 | [`L08_像素与毫米标定.md`](L08_像素与毫米标定.md) | 24 节完整笔记（含自测题 17 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- `src\calibration.py` 第 1～22 行：模块说明与公式；第 4 行"只做一件事"；第 6 行"不读视频、不读图片、不保存文件、不使用 OpenCV，只依赖标准库 math"；第 9～10 行坐标系约定；第 12～19 行全部公式；第 21 行代码风格；
- 第 24 行：`import math`——全文件唯一 import（无 `cv2` / `numpy` / `pandas`；无文件读写）；
- 第 32～43 行 `_to_float()`；第 46～70 行 `_check_point()`；第 73～92 行 `_check_direction()`；
- 第 100～144 行 `compute_scale()`：第 118～123 行参数检查；**第 125～126 行真实距离 > 0 检查**；**第 128～131 行 `dx` / `dy` / `pixel_distance = math.hypot(dx, dy)`**；**第 134～135 行两点不能重合**；**第 137～138 行 `px_per_mm` / `mm_per_px`**；**第 140～144 行返回三个键的字典**；
- 第 147～173 行 `unit_direction()`：第 149 行方向约定 10 cm → 16 cm；第 151 行定义式 `u = (P2 - P1) / |P2 - P1|`；第 170～171 行重合报错；第 173 行返回 `{"ux", "uy"}`；
- 第 176～204 行 `project_point()`：第 180 行公式说明；第 193～198 行参数与零长度检查；第 200～202 行归一化；**第 204 行 `return x * ux + y * uy`（实现上面第 180 行的公式 `s = x * ux + y * uy`）**；
- `src\displacement.py` 第 41～47 行标定来源说明（第 42～43 行来源视频 / frame 900 / `1920 x 1080` 坐标系；第 44～46 行 P1 / P2 / 真实距离；第 47 行"不做任何重新标定"）；第 48～50 行 `CALIB_P1_PX` / `CALIB_P2_PX` / `CALIB_REAL_DISTANCE_MM`；**第 52～53 行 `PX_PER_MM = 5.756961`、`MM_PER_PX = 0.173703`**；第 55 行 `U = (0.999976, -0.006894)`；第 57～64 行 M4 gate；
- `src\displacement.py` 第 72～81 行 `DS_FIELDNAMES`（含 `s_px` / `ds_px` / `ds_mm`）；第 84～90 行格式规范；第 98～150 行 `check_calibration_constants()`（第 142～147 行互为倒数自检）；第 306～314 行 `add_projection()`；第 317～354 行 `compute_s0()`；**第 357～369 行 `add_displacement()`（第 368～369 行 `ds_px = s_px - s0`、`ds_mm = ds_px / PX_PER_MM`）**；第 377～411 行 `build_ds_row()` / `write_ds_csv()`；
- `src\dynamic_displacement.py` 第 20～23 行 EXP-004 专属声明与"不得 import src.displacement"；第 26 行"不重新实现投影公式"；第 40 行只 `from src.calibration import project_point`；**第 59 行 EXP-004 标定冻结说明**；第 60～62 行 P1 (813.50, 296.49) / P2 (1422.13, 294.11) / 100.0 mm；**第 64～65 行 `PX_PER_MM_004 = 6.086399`、`MM_PER_PX_004 = 0.164301`**；第 66 行 `U_004`；第 68～76 行专属 gate（第 68 行"与 M4 gate 完全不同，不得混用"；阈值 4500 / 6500 / 200 / 250）；**第 367～379 行 `add_displacement()`（第 378～379 行公式，除数用 `PX_PER_MM_004`）**；第 1132～1151 行 ds 公式复算；
- `src\external_oscillation_tracker.py` 第 31～34 行"本模块不做：标定（px/mm）、位移换算…"；第 84 行 `POSITION_FEATURE_NAME`；第 87～96 行 `CSV_FIELDNAMES`（8 列，无 mm 列）；
- 只读复算（不重新标定）：M4 用冻结 P1 / P2 复算 `pixel_distance ≈ 345.418199 px`、`px_per_mm ≈ 5.7569700`（与冻结 5.756961 差 ≈ 9.0e-6）、`mm_per_px ≈ 0.1737025`（差 ≈ 5.1e-7），均在自检容差 1e-4 内；M5 复算 `hypot ≈ 608.634653 px`、投影法 `s(P2) - s(P1) ≈ 608.634444 px`，除以 100.0 得 ≈ 6.086347 / 6.086344（与冻结 6.086399 差 ≈ 5.2e-5 / 5.5e-5），在容差内。

### L08 源码地图

| 位置 | 内容 |
| --- | --- |
| `src\calibration.py` 第 1～22 行 | 模块说明与公式（第 6 行"不读视频 / 不读图片 / 不保存文件 / 不使用 OpenCV"） |
| `src\calibration.py` 第 24 行 | `import math`（唯一 import） |
| `src\calibration.py` 第 32～43、46～70、73～92 行 | `_to_float()` / `_check_point()` / `_check_direction()` |
| `src\calibration.py` 第 100～144 行 | `compute_scale()`（第 125～126、128～131、134～135、137～138、140～144 行） |
| `src\calibration.py` 第 147～173 行 | `unit_direction()` |
| `src\calibration.py` 第 176～204 行 | `project_point()`（第 180 行公式说明；第 204 行 `return x * ux + y * uy`） |
| `src\displacement.py` 第 41～55 行 | M4 标定来源、P1 / P2 / 60.0 mm、`PX_PER_MM` / `MM_PER_PX` / `U` |
| `src\displacement.py` 第 357～369 行 | `add_displacement()`（第 368～369 行 `ds_mm = ds_px / PX_PER_MM`） |
| `src\dynamic_displacement.py` 第 20～23、68～76 行 | EXP-004 专属边界与专属 gate（不得与 M4 混用） |
| `src\dynamic_displacement.py` 第 59～66 行 | M5 标定来源、P1 / P2 / 100.0 mm、`PX_PER_MM_004` / `MM_PER_PX_004` / `U_004` |
| `src\dynamic_displacement.py` 第 367～379 行 | `add_displacement()`（第 378～379 行 `ds_mm = ds_px / PX_PER_MM_004`） |
| `src\external_oscillation_tracker.py` 第 31～34、87～96 行 | "不做标定 / 位移换算"；8 列表头（无 mm 列） |

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L08 为什么像素不能直接当毫米（像素与毫米标定）"（Calibration、像素尺度、px/mm、mm/px、pixel_distance、compute_scale、unit_direction、project_point、s_px、ds_px、ds_mm、real distance、已知真实长度、M4 / M5 标定常量、标定边界 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L08 为什么像素不能直接当毫米（像素与毫米标定）"（把像素当固定长度、px/mm 与 mm/px 乘反、把 M4 常量套到 M5、把 ds_mm 当直接测量、给外部视频配 mm 系数、以为 calibration.py 会读视频 / 图片、把 x0_px 当存在的字段、双重舍入误判等）。

### 本节课暂未学习的内容

标定点的具体选择方法；方向向量的完整推导；`project_point()` 归一化的数学细节（第 196～202 行）；投影几何推导；`calibration.py` 的完整逐行教学；相机内参 / 外参标定与畸变校正（本项目明确不做）；周期、频率、FFT 仍属于后续课程。

（本节只学到"两套坐标系 → 四个单位 → 为什么像素不是固定长度 → 已知真实长度与标定常量 → ds_mm 换算 → 无标定就停在像素层面"这条链；以上内容属于后续课程，本节只登记名称，不展开。）

---

## L09 标定、方向向量与一维投影

- **课程编号**：L09
- **课程标题**：标定、方向向量与一维投影
- **学习状态**：已完成
- **记录日期**：2026-10-02
- **笔记文件**：[`L09_标定方向向量与一维投影.md`](L09_标定方向向量与一维投影.md)

### 本节课目标

- 逐行说清 `compute_scale()`（`src\calibration.py` 第 100～144 行）的六个步骤：参数检查（第 118～120 行）、`real_distance_mm` 合法性检查（第 122～126 行）、`dx` / `dy` / `pixel_distance`（第 128～131 行）、两点重合检查（第 134～135 行）、`px_per_mm` / `mm_per_px`（第 137～138 行）、返回结果（第 140～144 行）；
- 写出并解释三个量与量纲关系：`L_pixel = sqrt(dx² + dy²)`、`px_per_mm = L_pixel / L_real_mm`、`mm_per_px = L_real_mm / L_pixel = 1 / px_per_mm`；
- 区分**原始方向向量** `v = P2 - P1 = (dx, dy)` 与**单位方向向量** `u = v / |v|`，并说清 `unit_direction()`（第 147～173 行）的三步：`dx` / `dy` / `length`（第 166～168 行）、零长度检查（第 170～171 行）、返回单位向量（第 173 行）；
- 用三条理由解释**为什么必须归一化**：单位一致（只有 `|u| = 1`，`s` 的单位才是像素）、表示唯一（同一条方向只有一种写法、同一个 `s`）、几何可读（`ux` / `uy` 才能读作 cos / sin）；
- 说出 `ux`、`uy` 的几何意义：`u = (cos θ, sin θ)`；图像坐标系 y 向下为正，所以 `uy < 0` 表示方向"略向上"；M4 的 `U` 约 -0.395°，M5 的 `U_004` 约 -0.224°；
- 写出投影公式 `s = x·ux + y·uy`（第 180 行 docstring、第 204 行实现），并说明它就是二维点与方向 `u` 的**点积**；
- 说清 `project_point()`（第 176～204 行）的步骤：读取 `point` / `direction`（第 193～194 行）、零方向检查与**再次归一化**（第 196～202 行）、返回 `s`（第 204 行）；
- 解释 `project_point()` 为什么"再次"归一化方向：函数不假设调用方传入的是单位向量；项目里两个冻结方向常量只保留 6 位小数，本身不是精确单位向量（`|U| = 0.999999763906`、`|U_004| = 0.999999655816`）；
- 用正交分解解释投影为什么**保留沿运动方向的分量、削弱垂直方向分量**：`v = (v·u)u + (v - (v·u)u)`，垂直分量与 `u` 的点积恒为 0——这是有意的降维，不是"算丢了"；
- 背出两组真实方向常量及其来源行：M4 `U = (0.999976, -0.006894)`（`src\displacement.py` 第 55 行；标定来源第 48～50 行）、M5 `U_004 = (0.999992, -0.003913)`（`src\dynamic_displacement.py` 第 66 行；标定来源第 60～62 行）；
- 说明用真实 CSV 复核 `s_px = x·ux + y·uy` 的口径与结论：track CSV 与 ds CSV 逐行配对、只取 `s_px` 非空的行、把再次归一化算进去后，M4 的 1050 行与 M5 的 1766 行最大偏差分别为 `4.974e-4 px` / `4.998e-4 px`，正好落在 `s_px` 写 3 位小数的舍入上界 `5e-4 px` 之内；
- 说出 **L08 → L09 → L10 的完整知识连接**：L08 定"尺度"，L09 定"方向 + 一维坐标"，L10 才把 `s_px` 变成相对基线的位移 `ds_px` / `ds_mm`；
- 说出本课**不展开**的内容：`s0` 如何选、valid gate 的完整规则、`ds_px` / `ds_mm` 的完整位移流程、`displacement.py` / `dynamic_displacement.py` 的完整逻辑——全部留到 L10；
- 永远分清六类材料：**VisionMotion 真实源码 / 真实项目常数 / 真实数据 / 数学公式 / 教学示例 / 概念伪代码**。

### 核心概念

1. **`compute_scale()` 六个步骤**：参数检查（第 118～120 行，`_check_point()` / `_to_float()`）→ 真实距离合法性（第 122～126 行，有限且 > 0）→ `dx` / `dy` / `pixel_distance = math.hypot(dx, dy)`（第 128～131 行）→ 两点重合检查（第 134～135 行）→ `px_per_mm` / `mm_per_px`（第 137～138 行）→ 返回三个键的字典（第 140～144 行）；
2. **`L_pixel`（`pixel_distance`）**：两点之间的欧氏像素距离 `hypot(dx, dy)`，单位 px；返回字典的 `pixel_distance` 键（第 141 行）就是它；
3. **`px_per_mm` 与 `mm_per_px` 互为倒数**：`px_per_mm = L_pixel / L_real_mm`（第 137 行）、`mm_per_px = L_real_mm / L_pixel`（第 138 行）；量纲检查可以防乘除写反；
4. **原始方向向量 `v = (dx, dy) = P2 - P1`**：同时携带方向与长度，长度 `|v| = L_pixel`（`unit_direction()` 第 166～168 行与 `compute_scale()` 用同一个 `hypot`）；
5. **单位方向向量 `u = v / |v| = (dx/|v|, dy/|v|)`**：`|u| = 1`，只保留方向（第 173 行返回 `{"ux", "uy"}`）；
6. **为什么必须归一化（三条理由）**：① 单位一致——`s = x·ux + y·uy` 里只有 `|u| = 1` 时 `s` 的单位才是像素；② 表示唯一——同方向写成 `(1,0)` 或 `(2,0)` 会给出不同的 `s`；③ 几何可读——只有 `|u| = 1` 时 `s = |v|·cos θ`，`ux` / `uy` 才是方向余弦；教学反例：`u_raw = (2, 0)`、点 `(10, 0)` 不归一化得 20、归一化后得 10；
7. **`ux` / `uy` 的几何意义**：`u = (cos θ, sin θ)`；`ux > 0` 指向画面右侧，`uy > 0` 指向画面下方（y 轴向下），`uy < 0` 表示"略向上"；交换 P1 / P2 会得到 `(-ux, -uy)`，投影坐标的增大方向随之反转；
8. **点积（dot product）**：`a·b = ax·bx + ay·by = |a||b|cos θ`；`s = v·u = x·ux + y·uy`，`|u| = 1` 时是有号投影长度；`s` 的符号表示投影落在 `u` 正方向一侧还是反方向一侧；
9. **一维投影 `s_px`**：把二维像素坐标压成沿 `u` 的一维坐标（`project_point()` 第 204 行）；`s_px` 是**坐标**不是位移；
10. **`project_point()` 再次归一化**：`length = hypot(ux, uy)`、零长度报 `ValueError`、`ux /= length`、`uy /= length`（第 196～202 行）；再次归一化把冻结常量的截断误差抹掉：跳过归一化时与 CSV 的最大差为 `8.299e-4 px`（M4）/ `9.235e-4 px`（M5），算上归一化后降到 `4.974e-4 px` / `4.998e-4 px`；
11. **正交分解与降维取舍**：`v = (v·u)u + (v - (v·u)u)`；沿 `u` 移动 1 px → `Δs = 1 px`（1:1 保留），垂直移动 10 px → `Δs = 0`（垂直分量不进入 `s`）；教学算术：用 M4 方向时沿 x 轴移动 10 px → `Δs = 9.99976 px`，沿 y 轴移动 10 px → `Δs = -0.068940 px`（只"漏"进不到 0.07 px）；
12. **M4 的方向常量 `U`**：`src\displacement.py` 第 55 行 `U = (0.999976, -0.006894)`，方向 10 cm → 16 cm；与 +x 轴夹角约 -0.395°；`|U| = 0.999999763906`；自检：第 128～135 行（与冻结标定点一致，容差 1e-4）、第 136～141 行（是单位向量）；
13. **M5 的方向常量 `U_004`**：`src\dynamic_displacement.py` 第 66 行 `U_004 = (0.999992, -0.003913)`，方向 10 cm → 20 cm；与 +x 轴夹角约 -0.224°；`|U_004| = 0.999999655816`；自检：第 139～144 行（容差 1e-6）、第 147～157 行（用 `project_point()` 复算投影长度）、第 167～172 行（`ux > 0` 锁定正方向）；
14. **两组方向常量绑定各自实验、不能混用**：`src\dynamic_displacement.py` 第 20～23 行禁止 import `src.displacement`，第 68～76 行写明专属 gate"与 M4 gate 完全不同，不得混用"；
15. **真实数据验证（只读）**：`results\EXP-003-STATIC-002_track.csv` 与 `_ds.csv` 各 1961 行、`s_px` 非空 1050 行（= `valid=True`，911 行为空）；`results\EXP-004-DYNAMIC-001_track.csv` 与 `_ds.csv` 各 1766 行、`s_px` 全部有值；最小二乘反推的系数与 `U / |U|` 一致到 `1e-7` 量级（M4 差 `(-2.54e-8, +9.61e-8)`，M5 差 `(-9.56e-8, +4.89e-7)`）；
16. **末位差来自文本舍入**：`s_px` 写 3 位小数（上界 `5e-4 px`）、`x_px` / `y_px` 写 2 位小数；偏差不是算法差异，也不是数据错误；
17. **与 L08、L10 的分工**：L08 = 尺度（`px/mm`、`mm/px`、`L_pixel`）；L09 = 方向 + 一维坐标（`v`、`u`、`ux` / `uy`、`s_px`）；L10 = 基线与位移（`s0`、valid gate、`ds_px`、`ds_mm`）；
18. **本课边界**：`s0` 如何选（`src\displacement.py` 第 317 行起 `compute_s0()`）、valid gate 的完整规则（第 57～64 行 / `src\dynamic_displacement.py` 第 68～76 行）、`ds_px` / `ds_mm` 流程（第 357～369 行 / 第 367～379 行）本课只登记名称与位置，不展开；
19. **六类材料**：VisionMotion 真实源码 / 真实项目常数 / 真实数据 / 数学公式 / 教学示例 / 概念伪代码；引用项目事实必须能指出文件 + 函数 + 行号。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 标定模块（本课主角，纯数学） | `src\calibration.py` | 第 100～144 行 `compute_scale()`（第 118～120 行参数检查；第 122～126 行真实距离合法性；第 128～131 行 `dx` / `dy` / `pixel_distance`；第 134～135 行两点重合；第 137～138 行两个尺度；第 140～144 行返回）；第 147～173 行 `unit_direction()`（第 166～168 行 `dx` / `dy` / `length`；第 170～171 行零长度；第 173 行返回单位向量）；第 176～204 行 `project_point()`（第 193～194 行读取参数；第 196～202 行零方向检查与再次归一化；第 204 行 `return x * ux + y * uy`） |
| M4 方向常量与投影调用 | `src\displacement.py` | 第 48～50 行标定点与真实长度；第 52～53 行 `PX_PER_MM` / `MM_PER_PX`；**第 55 行 `U = (0.999976, -0.006894)`**；第 128～141 行冻结常量自检；第 306～314 行 `add_projection()`（第 314 行调用 `project_point((x_px, y_px), U)`） |
| M5 方向常量与投影调用 | `src\dynamic_displacement.py` | 第 60～62 行标定点与真实长度；第 64～65 行 `PX_PER_MM_004` / `MM_PER_PX_004`；**第 66 行 `U_004 = (0.999992, -0.003913)`**；第 139～144 行单位向量自检；第 147～157 行投影复算；第 167～172 行方向正负自检 |
| 真实数据（只读核对，未重新生成） | `results\EXP-003-STATIC-002_track.csv`、`results\EXP-003-STATIC-002_ds.csv` | 各 1961 行（frame 0～1960）；表头 6 / 8 列；`s_px` 非空 1050 行（= `valid=True`），911 行为空；第 1 行数据 `0,0.000000,1083.63,464.97,4783.0,True` / `0,0.000000,1080.399,4.335,0.7530,4783.0,True,True`；`s_px` 范围 1074.814～1426.332 |
| 真实数据（只读核对，未重新生成） | `results\EXP-004-DYNAMIC-001_track.csv`、`results\EXP-004-DYNAMIC-001_ds.csv` | 各 1766 行（frame 0～1765）；表头 6 / 8 列；`s_px` 全部有值；第 1 行数据 `0,0.000000,852.81,208.63,5713.0,True` / `0,0.000000,851.987,-3.215,-0.5283,5713.0,True,True`；`s_px` 范围 851.987～1257.917 |
| 本节课笔记 | [`L09_标定方向向量与一维投影.md`](L09_标定方向向量与一维投影.md) | 15 节完整笔记（含自测题 17 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- `src\calibration.py` 第 100～144 行 `compute_scale()`：第 118～120 行参数检查（`_check_point()` 两次 + `_to_float()`）；第 122～126 行 `real_distance_mm` 必须有限且 > 0（报错信息带当前值 `%g`）；第 128～131 行 `dx = x2 - x1`、`dy = y2 - y1`、`pixel_distance = math.hypot(dx, dy)`；第 134～135 行 `pixel_distance == 0` 报 `ValueError`；第 137～138 行 `px_per_mm` / `mm_per_px`；第 140～144 行返回 `{"pixel_distance", "px_per_mm", "mm_per_px"}`；
- `src\calibration.py` 第 147～173 行 `unit_direction()`：第 149 行方向约定"从 P1（10 cm）指向 P2（16 cm）"；第 151 行 `u = (P2 - P1) / |P2 - P1|`；第 166～168 行 `dx` / `dy` / `length = math.hypot(dx, dy)`；第 170～171 行 `length == 0` 报 `ValueError`；第 173 行 `return {"ux": dx / length, "uy": dy / length}`；
- `src\calibration.py` 第 176～204 行 `project_point()`：第 180 行公式说明 `s = x * ux + y * uy`；第 182～185 行 `direction` 可传字典或长度 2 序列；第 187～189 行说明"不是单位向量会先归一化"；第 193～194 行 `_check_point` / `_check_direction`；第 196～198 行 `length = hypot(ux, uy)` 与零长度报错；第 200～202 行"归一化，让 s 的单位和 point 一样是像素"；第 204 行 `return x * ux + y * uy`；
- `src\displacement.py` 第 48～50 行 `CALIB_P1_PX = (1036.23, 490.58)`、`CALIB_P2_PX = (1381.64, 488.20)`、`CALIB_REAL_DISTANCE_MM = 60.0`；第 52～53 行 `PX_PER_MM = 5.756961`、`MM_PER_PX = 0.173703`；**第 55 行 `U = (0.999976, -0.006894)`**；第 306～314 行 `add_projection()` 只在 `row["valid"]` 为真时写入 `s_px`；
- `src\dynamic_displacement.py` 第 60～62 行 `CALIB_P1_PX = (813.50, 296.49)`、`CALIB_P2_PX = (1422.13, 294.11)`、`CALIB_REAL_DISTANCE_MM = 100.0`；第 64～65 行 `PX_PER_MM_004 = 6.086399`、`MM_PER_PX_004 = 0.164301`；**第 66 行 `U_004 = (0.999992, -0.003913)`**；第 40 行只 `from src.calibration import project_point`；
- 只读复算（不重新标定）：M4 `L_pixel = hypot(345.41, -2.38) ≈ 345.418199 px`、`u ≈ (0.999976262, -0.006890199)`、`s(P2) - s(P1) ≈ 345.418199 px`；M5 `L_pixel = hypot(608.63, -2.38) ≈ 608.634653 px`、`u ≈ (0.999992354, -0.003910392)`、`s(P2) - s(P1) ≈ 608.634653 px`（含再次归一化口径，与 `L_pixel` 一致到 `1e-9 px`）；
- 只读数据复核（只读读取，未运行任何程序 / demo、未生成或覆盖任何文件）：M4 的 1050 行 `s_px` 与 `(x·ux + y·uy) / |U|` 最大差 `4.974e-4 px`（平均 `2.499e-4`）；M5 的 1766 行最大差 `4.998e-4 px`（平均 `2.500e-4`）；不除模时分别为 `8.299e-4 px` / `9.235e-4 px`——说明 CSV 里实际执行了 `project_point()` 的再次归一化。

### L09 源码地图

| 位置 | 内容 |
| --- | --- |
| `src\calibration.py` 第 100～144 行 | `compute_scale()`（第 118～120、122～126、128～131、134～135、137～138、140～144 行） |
| `src\calibration.py` 第 147～173 行 | `unit_direction()`（第 166～168、170～171、173 行） |
| `src\calibration.py` 第 176～204 行 | `project_point()`（第 193～194、196～202、204 行） |
| `src\displacement.py` 第 48～55 行 | M4 标定点、真实长度、`PX_PER_MM` / `MM_PER_PX`、`U` |
| `src\displacement.py` 第 128～141 行 | M4 冻结常量自检（u 与标定点一致；u 是单位向量） |
| `src\displacement.py` 第 306～314 行 | `add_projection()`（第 314 行调用 `project_point`） |
| `src\dynamic_displacement.py` 第 60～66 行 | M5 标定点、真实长度、`PX_PER_MM_004` / `MM_PER_PX_004`、`U_004` |
| `src\dynamic_displacement.py` 第 139～157、167～172 行 | M5 自检：单位向量、投影复算、方向正负 |

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L09 标定、方向向量与一维投影"（单位向量、归一化、原始方向向量、单位方向向量与方向余弦、点积、一维投影 / 标量投影、正交分解、M4 / M5 方向常量、只读复算、六类材料 等；另含 `unit_direction` / `project_point` / `s_px` / `compute_scale` 的 L09 补充视角）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L09 标定、方向向量与一维投影"（用原始方向向量直接算 s、以为冻结常量是精确单位向量、把 s_px 当位移、把方向取反、把 ux / uy 与 cos / sin 记反、把点积当逐元素相乘、以为投影丢掉 y 信息、把教学示例当项目数据、混用 M4 / M5 方向常量等）。

### 本节课暂未学习的内容

`s0` 如何选（`src\displacement.py` 第 317 行起 `compute_s0()` 的窗口与最少帧数规则）；valid gate 的完整规则（`src\displacement.py` 第 57～64 行、`src\dynamic_displacement.py` 第 68～76 行）；`ds_px` / `ds_mm` 的完整位移流程（`src\displacement.py` 第 357～369 行、`src\dynamic_displacement.py` 第 367～379 行）；`displacement.py` / `dynamic_displacement.py` 的完整逻辑（统计、报告、自检的其余部分）；周期 / 频率 / FFT 仍属于后续课程。

（本节学到"两点的像素距离与尺度 → 原始方向向量 → 单位方向向量与归一化 → 点积投影出 s_px → 真实 CSV 复核 → L08 / L09 / L10 分工"这条链；`s0`、valid gate、位移流程只登记名称与位置，留到 L10 展开。）

---

## L10 从一维位置到位移：s0、ds_px 与 ds_mm

- **课程编号**：L10
- **课程标题**：从一维位置到位移：s0、ds_px 与 ds_mm
- **学习状态**：已完成
- **记录日期**：2026-10-02
- **笔记文件**：[`L10_从一维位置到位移.md`](L10_从一维位置到位移.md)

### 本节课目标

- 说清 **`s_px` 是一维位置、`ds_px` 是相对 `s0` 的位移**：`s_px` 回答"沿尺方向现在在哪"，`ds_px = s_px - s0` 回答"相对基线走了多少"；
- 用三条理由解释**为什么 position ≠ displacement**：位置有零点从哪来的问题、`s_px` 绝对值不能跨实验比较、只有差值对应物理位移；
- 写出 `compute_s0()`（`src\displacement.py` 第 317～354 行）的定义与意义：`s0` = `time_s <= window_s` 且 `valid=True` 的帧的 `s_px` 平均值；
- 背出 M4 参数：`S0_WINDOW_S = 0.5`、`MIN_S0_VALID_FRAMES = 10`（第 66～68 行）；M5 参数：`S0_WINDOW_S = 2.0`、`MIN_S0_VALID_FRAMES = 60`（`src\dynamic_displacement.py` 第 78～80 行）；
- 解释为什么 `s0` 不是首帧、也不是标尺 10 cm 位置（源码第 294 行明文"正式禁止：用 10 cm 代替 s0、用首帧代替均值"）；
- 解释为什么第 0 帧的 `ds_px` 不一定为 0（真实数据：+4.335 / +0.164 / −3.215 px）；
- 区分 detected 与 valid（第一道 / 第二道筛选），并背出 M4 valid 门限（area 2000～15000、y 400～540）与 M5 valid 门限（area 4500～6500、y 200～250）；
- 说清无效帧的处理：不删除、`valid=False`、`s_px` / `ds_px` / `ds_mm` 留空（绝不写 0 / -1 / nan）；
- 写出位移公式：`ds_px = s_px - s0`（第 339 / 378 行）、`ds_mm = ds_px / PX_PER_MM`（第 340 / 379 行，等价 `ds_px × MM_PER_PX`）；
- 用三份真实 ds CSV 复核统计、`s0`、公式与空值（第 7 节）；
- 解释为什么 M4 与 M5 的参数绝对不能混用（标定差约 5.72%、gate 不同、`s0` 窗口不同；源码第 20～23、68 行结构性禁止）；
- 记住"检测到"不等于"可用于物理计算"，并能默写数据依赖链 `detected → valid → s_px → ds_px → ds_mm`；
- 说出 L09 → L10 → 后续运动分析的连接（本课不展开峰值 / 谷值、转向点、周期、频率、FFT、简谐振动理论）；
- 分清五类材料：项目真实源码 / 真实数据 / 数学公式 / 教学示例 / 概念伪代码。

### 核心概念

1. **位置 ≠ 位移**：`s_px` 是沿尺方向的一维位置坐标（零点由图像原点与方向 `u` 共同决定）；`ds_px = s_px - s0` 才是相对基线 `s0` 的位移；
2. **valid 是第二道数据筛选**：detected（M3）回答"看到没有"，valid（本模块 `is_valid_frame()`）回答"这一帧能不能用"；只有 valid=True 才有 `s_px` / `ds_px` / `ds_mm`；
3. **M4 valid 门限**（`src\displacement.py` 第 57～64、175～213 行）：`detected=True` 且 `2000 <= area_px <= 15000` 且 `400 <= y_px <= 540`；注释原文"本次 EXP-003 拍摄几何专属参数，不是通用视觉规则"；
4. **M5 valid 门限**（`src\dynamic_displacement.py` 第 68～76、183～222 行）：`detected=True` 且 `4500 <= area_px <= 6500` 且 `200 <= y_px <= 250`；标题原文"与 M4 gate 完全不同，不得混用"；
5. **缺数据也判 False**：detected=True 但 area / y 为 None 时同样 `valid=False`（第 191～193 行）——数据缺失不填 0；
6. **无效帧不删除**：ds CSV 行数 = track CSV 行数（第 781 行"不删除任何行"）；`s_px` / `ds_px` / `ds_mm` 初始化为 None（第 272～274 行）、写 CSV 时空字符串（第 360～363 行）；绝不写 0 / -1 / nan（第 355 行）；
7. **`s0` 的定义**（第 288～325 行）：只使用 `time_s <= window_s` 且 `valid=True` 的帧（第 304～305 行），取这些帧 `s_px` 的平均值（第 322～323 行）；窗口参数默认 `S0_WINDOW_S`、最少帧数 `MIN_S0_VALID_FRAMES`；
8. **M4 的 s0 参数**：0.5 s 窗口、最少 10 帧（第 66～68 行）；**M5 的 s0 参数**：2.0 s 窗口、最少 60 帧（M5 第 78～80 行）；第 318 行"最少有效帧检查"不达标则 `ok=False`、`s0=None`；
9. **`s0` 不是首帧**：源码第 294 行正式禁止；真实数据里 frame 0 的 `ds_px` = +4.335 / +0.164 / −3.215，直接证明基线不是首帧取值；
10. **`s0` 不是标尺 10 cm 位置**：10 cm 是标定点 P1（第 44 行 / M5 第 60 行）；`s0` 是数据窗口平均值；只读复算 M4 `s(P1) ≈ 1032.823 px`、M5 `s(P1) ≈ 812.334 px`，都不是对应视频的 `s0`；
11. **`s0` 不达标不写 ds CSV**（第 781、793 行 / M5 第 1194、1206～1209 行）：不扩大窗口、不修改阈值、不做插值（第 517 行）；M5 还有冻结常量自检前置（第 1250～1252 行）；
12. **位移公式**：`ds_px = s_px - s0`（第 339 / 378 行）；`ds_mm = ds_px / PX_PER_MM`（第 340 行）/ `PX_PER_MM_004`（第 379 行）；等价 `ds_px × MM_PER_PX`；写反会差约 33 倍（5.756961² ≈ 33.14）；
13. **双重舍入**：`ds_mm` 由未舍入的 `ds_px` 算出再写 4 位小数；ds_px / s_px 各写 3 位小数（`FIELD_PATTERNS`：第 84～90 / 103～109 行）；反算出现 ~1e-4 mm 的差正常，自检容差 0.0005 mm（第 736～740 行 / M5 第 1140～1148 行）；
14. **真实 ds CSV 统计**：STATIC-002 = 1961 行、valid 1050/911、`s0` = 1076.063871 px；STATIC-003 = 1984 行、valid 1192/792、`s0` = 1077.364097 px；EXP-004 = 1766 行、全部 valid、`s0` = 855.202603 px；
15. **真实公式复核**：`ds_px = s_px - s0` 最大偏差 ≤ 0.000904 px（容差 0.002）；`ds_mm` 最大偏差 ≤ 0.000151 mm（容差 0.0005）；无效行位移字段非空 0 例、有效行缺字段 0 例；
16. **detected=True 但 valid=False 真实存在**：STATIC-002 有 911 帧、STATIC-003 有 792 帧（例：STATIC-002 frame 52，area 12439.0、y 35.44 被 y 门限拒绝）；EXP-004 为 0 帧；
17. **M4 与 M5 参数不能混用**：尺度（5.756961 vs 6.086399，差约 5.72%）、gate（2000/15000/400/540 vs 4500/6500/200/250）、`s0`（0.5/10 vs 2.0/60）、方向（`U` vs `U_004`）；M5 第 20～23 行禁止 import `src.displacement`；
18. **混用的真实后果（推演）**：EXP-004 的 y 全部落在 208.63～220.61，若用 M4 的 y 门限（400～540）会被全部拒绝 → 不写 ds CSV；STATIC 的 y 上限 470 / 464，也基本落在 M5 的 200～250 之外；
19. **统计口径**：`valid_rate`（第 420 / 466 行）、`invalid_count`（第 421 / 438 行）、`detected_invalid_count`（第 423 / 469 行）、`longest_invalid_run`（第 427 / 479 行）；真实值：valid_rate ≈ 53.54% / 60.08% / 100%，longest_invalid_run = 180 / 147 / 0；
20. **数据依赖链**：`detected → valid → s_px → ds_px → ds_mm`，每一环只依赖上一环；
21. **本课边界**：峰值 / 谷值、转向点完整算法（`detect_turning_points()`，M5 第 487～623 行）、周期、频率、FFT、简谐振动理论均留到后续课程，本课只登记名称与位置。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| M4 位移模块（本课主角） | `src\displacement.py` | 第 57～68 行 gate / s0 常量；第 175～213 行 `is_valid_frame()`（有限值校验约第 204 行）；第 290～303 行 `add_valid_flags()`；第 306～314 行 `add_projection()`；第 317～354 行 `compute_s0()`；第 357～369 行 `add_displacement()`；第 377～395 行 `build_ds_row()`；第 419～460 行 `summarize()`；第 535～546 行 s0 不足报告；第 804～846 行 `build_ds_from_track_csv()` |
| M5 位移模块 | `src\dynamic_displacement.py` | 第 68～76 行专属 gate；第 78～80 行 s0 规则；第 183～222 行 `is_valid_frame()`；第 315～323 行 `add_projection()`；第 326～364 行 `compute_s0()`；第 367～379 行 `add_displacement()`；第 387～405 行 `build_ds_row()`；第 429～483 行 `summarize_dynamic()`；第 1182～1226 行 `build_ds_from_track_csv()`；第 1229～1259 行 `run_experiment()` |
| 上游数据链（L05～L09 已学） | `src\calibration.py`、`src\video_tracker.py` | `project_point()`（calibration.py 第 176～204 行）提供 `s_px`；M3 `track_video()` 提供 track CSV 与 detected |
| 真实数据（只读核对，未重新生成） | `results\EXP-003-STATIC-002_ds.csv`、`results\EXP-003-STATIC-002_track.csv` | 各 1961 行；valid 1050 / invalid 911；`s0` = 1076.063871 px；frame 0 行 `0,0.000000,1080.399,4.335,0.7530,4783.0,True,True`；frame 52 为 detected=True 但 valid=False 实例 |
| 真实数据（只读核对，未重新生成） | `results\EXP-003-STATIC-003_ds.csv`、`results\EXP-003-STATIC-003_track.csv` | 各 1984 行；valid 1192 / invalid 792；`s0` = 1077.364097 px；frame 0 行 `0,0.000000,1077.528,0.164,0.0284,4394.5,True,True`；frame 35 实例 |
| 真实数据（只读核对，未重新生成） | `results\EXP-004-DYNAMIC-001_ds.csv`、`results\EXP-004-DYNAMIC-001_track.csv` | 各 1766 行；valid 1766 / invalid 0；`s0` = 855.202603 px；frame 0 行 `0,0.000000,851.987,-3.215,-0.5283,5713.0,True,True` |
| 调用方 | `demo\run_m43_displacement.py`、`demo\run_m52_dynamic_displacement.py` | M4 / M5 的入口脚本（本课未运行） |
| 本节课笔记 | [`L10_从一维位置到位移.md`](L10_从一维位置到位移.md) | 16 节完整笔记（含自测题 20 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- `src\displacement.py` 第 57～64 行 M4 gate：`AREA_MIN_PX = 2000.0`、`AREA_MAX_PX = 15000.0`、`Y_MIN_PX = 400.0`、`Y_MAX_PX = 540.0`；第 66～68 行 `S0_WINDOW_S = 0.5`、`MIN_S0_VALID_FRAMES = 10`；
- 第 175～213 行 `is_valid_frame()`：第 194～195 行 `if not detected: return False`；第 197～205 行 area / y 为 None 返回 False；第 207～211 行两个范围判断；第 187 行注释"绝不修改原始 detected"；
- 第 290～303 行 `add_valid_flags()`：写过 valid 后把 `s_px` / `ds_px` / `ds_mm` 初始化为 None；第 306～314 行 `add_projection()` 只在 `row["valid"]` 时计算 `s_px`；
- 第 317～354 行 `compute_s0()`：第 333 行 `window_rows`（`time_s <= window_s`）；第 334 行 `valid_s_values`；第 336～349 行报告字典（`window_total_frames` / `window_valid_frames` / `window_missed_frames` / `window_detected_invalid_frames` / `ok` / `s0`）；第 347 行最少帧检查；第 351～352 行平均值；第 323 行"正式禁止：用 10 cm 代替 s0、用首帧代替均值……"；
- 第 357～369 行 `add_displacement()`：**第 368 行 `row["ds_px"] = row["s_px"] - s0`**；**第 369 行 `row["ds_mm"] = row["ds_px"] / PX_PER_MM`**；
- 第 377～395 行 `build_ds_row()`：第 389～392 行无效数据写空字符串；第 384 行注释"绝不写 0 / -1 / nan"；第 84～90 行 `FIELD_PATTERNS`（time_s 6 / s_px 3 / ds_px 3 / ds_mm 4 / area_px 1 位小数）；
- 第 419～460 行 `summarize()`：第 449 行 `valid_rate`；第 479 行 `invalid_count`；第 452 行 `detected_invalid_count`；第 456 行 `longest_invalid_run`（循环第 434～442 行）；
- 第 535～546 行：s0 窗口有效帧不足时打印问题报告；第 546 行原文"本视频不生成 ds CSV；不扩大窗口、不修改阈值、不做插值"；
- 第 597～796 行 `check_ds_csv()`：第 721～724 行空值检查；第 738～757 行 s0 复算（容差 0.002 px，第 750 行）；第 759～777 行 ds 公式复算（ds_px 容差 0.002 px、ds_mm 容差 0.0005 mm，第 768、800 行）；
- 第 804～846 行 `build_ds_from_track_csv()`：第 816 行"过程中不删除任何行；s0 窗口有效帧不足时不写 ds CSV"；第 828 行 `if s0_report["ok"]` 才写；
- `src\dynamic_displacement.py` 第 20～23 行 EXP-004 专属声明与"不得 import src.displacement"；第 27 行"不删除任何 track CSV 行；valid=False 的位移字段一律留空（不写 0 / -1 / nan）"；第 68～76 行专属 gate（4500～6500 / 200～250）；第 78～80 行 s0 规则（2.0 s / 60 帧）；第 183～222 行 `is_valid_frame()`；第 326～364 行 `compute_s0()`；第 367～379 行 `add_displacement()`（第 378～379 行公式，除数 `PX_PER_MM_004`）；第 429～483 行 `summarize_dynamic()`（第 466～479 行统计字段）；第 1182～1226 行 `build_ds_from_track_csv()`（第 1194、1206～1209 行）；第 1229～1259 行 `run_experiment()`（第 1250～1252 行常量自检前置）。

### L10 源码地图

| 位置（`src\displacement.py`，共 866 行） | 内容 |
| --- | --- |
| 第 21～22、41～68 行 | 边界声明；标定来源与常量；M4 gate；s0 规则 |
| 第 72～90 行 | `DS_FIELDNAMES` / `FIELD_PATTERNS` |
| 第 175～213 行 | `is_valid_frame()` |
| 第 248～282 行 | `read_track_csv()` |
| 第 290～303、306～314 行 | `add_valid_flags()` / `add_projection()` |
| 第 317～354 行 | `compute_s0()`（第 333～334、347、351～352 行） |
| 第 357～369、377～395、398～411 行 | `add_displacement()` / `build_ds_row()` / `write_ds_csv()` |
| 第 419～460、535～546 行 | `summarize()` / s0 不足报告 |
| 第 597～796 行 | `check_ds_csv()`（第 721～724、738～757、759～777 行） |
| 第 804～846、849～866 行 | `build_ds_from_track_csv()` / `run_experiment()` |

| 位置（`src\dynamic_displacement.py`，共 1259 行） | 内容 |
| --- | --- |
| 第 6～33 行 | 数据链与边界（第 16、20～23、27 行） |
| 第 59～80 行 | EXP-004 标定、专属 gate、s0 规则 |
| 第 91～109 行 | `DS_FIELDNAMES` / `FIELD_PATTERNS` |
| 第 183～222 行 | `is_valid_frame()` |
| 第 270～294 行 | `add_valid_flags()` / `add_projection()` |
| 第 326～364 行 | `compute_s0()`（第 343～344、357、361～362 行） |
| 第 367～379、387～405 行 | `add_displacement()` / `build_ds_row()` |
| 第 429～483 行 | `summarize_dynamic()` |
| 第 487～623 行 | `detect_turning_points()`（后续课程内容，本课不展开） |
| 第 931～1174 行 | `check_ds_csv()`（第 1083～1088、1108～1129、1131～1151 行） |
| 第 1182～1226、1229～1259 行 | `build_ds_from_track_csv()` / `run_experiment()` |

（行号按 2026-10-02 当前源码逐行核对；如果实际源码行号发生变化，以当前真实源码为准。全部数据为只读核对，未重新生成。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L10 从一维位置到位移：s0、ds_px 与 ds_mm"（valid gate、is_valid_frame、第二道筛选、s0、基线、compute_s0、s0 窗口、MIN_S0_VALID_FRAMES、位置与位移、ds_px、ds_mm、无效帧留空、双重舍入、valid_rate / invalid_count / detected_invalid_count / longest_invalid_run、数据依赖链 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L10 从一维位置到位移：s0、ds_px 与 ds_mm"（把 s_px 当位移、以为第 0 帧 ds_px 一定为 0、用首帧代替 s0、把 10 cm 位置当基线、把 detected 当 valid、删行 / 填 0、混用 M4 / M5 参数、双重舍入误判等）。

### 本节课暂未学习的内容

~~位移的符号语义（ds 的正负与大小）、运动方向判据（Δds）与 `MIN_TURN_TRAVEL_PX` 的最小认识~~（已在 L11 学习，见下一节）/ ~~峰值 / 谷值、转向点完整算法（`src\dynamic_displacement.py` 第 487～623 行 `detect_turning_points()` 的内部逻辑与最小反向行程 20 px 规则的完整语义）、运动段完整切分~~（已在 L12 学习，见后文）/ 周期、频率、FFT、简谐振动理论——仍属于后续课程，本课只登记名称与位置，不展开。

（本节学到"track CSV → valid gate → s_px → s0 → ds_px / ds_mm → ds CSV → 只读复核"这条完整链；位移的符号与运动方向语义已在 L11 学习；峰值 / 谷值、转向点完整算法与运动段切分已在 L12 学习；周期 / 频率 / FFT 只登记名称，留到后续课程。）

---

## L11 位移数据、正负号与运动方向

- **课程编号**：L11
- **课程标题**：位移数据、正负号与运动方向
- **学习状态**：已完成
- **记录日期**：2026-10-04
- **笔记文件**：[`L11_位移正负与运动方向.md`](L11_位移正负与运动方向.md)

### 本节课目标

- 说清 `ds` 的正负只是**位置方向记号**：正号表示这一帧落在参考位置 `s0` 的正侧、负号表示负侧，不代表好坏、不代表快慢；
- 说清 `ds` 的大小 `|ds|` 表示**离参考位置 `s0` 多远**（沿尺方向的投影距离，不是二维欧氏距离、不是速度）；
- 说清 `s0` 是**参考位置、不带方向**；正负来自 `s_px` 与 `s0` 的相对关系（`ds_px = s_px - s0`，第 339 行）；
- 说出 VisionMotion 的正方向来自**标定点 P1 → P2 的人为约定**：M4 是 10 cm → 16 cm（第 46、55 行）、M5 是 10 cm → 20 cm（`src\dynamic_displacement.py` 第 60～66 行）；
- 写出并使用 **Δds = ds[i+1] − ds[i]**：Δds > 0 = 向正方向运动；Δds < 0 = 向负方向运动；Δds = 0 = 该间隔读数不变；
- 记住 Δds 的两个前提：**两帧都 valid**、**不跨空洞计算**；并说清 **Δds 不是速度**（速度 = Δds / Δt，本项目没有速度字段）；
- 用两条真实例子说明"符号侧 ≠ 运动方向"：M5 f237 → f313（负侧、向正方向运动）、M5 f963 → f1015（正侧、向负方向运动）；
- 背出三份真实数据的关键统计：STATIC-002（valid 1050 / invalid 911、`ds_mm` −0.2170～60.8426、正/负/零 = 1016/34/0）、STATIC-003（valid 1192 / invalid 792、−0.0540～60.1932、1174/18/0）、EXP-004（valid 1766/1766、−0.5283～66.1663、1605/161/0）；
- 描述 M4 静态数据的**"平台 + 台阶 + 空洞"**形态（7 个平台、约每 10 mm 一级）与 M5 动态数据的**"连续往返"**形态（无空洞、数值多次上升下降）；
- 说清 `valid=False` 时 `s_px` / `ds_px` / `ds_mm` **均留空**（第 272～274、284～285、338～340、360～363 行），Δds 在空洞处断开；
- 说出 `MIN_TURN_TRAVEL_PX = 20.0` 的**最小认识**（反向行程阈值、抗静止段噪声；完整算法留给 L12）；
- 说出 L10 → L11 → L12 的知识连接，并分清五类材料：项目真实源码 / 真实数据 / 教学示例 / 概念解释 / 概念伪代码。

### 核心概念

1. **`ds` 的正负 = 位置方向记号**：正号 = 这一帧在参考位置的正侧（沿 `U` / `U_004` 指向的一侧），负号 = 负侧；不代表好坏、不代表快慢；
2. **`ds` 的大小 = 离参考位置多远**：`|ds_px|` / `|ds_mm|` 是沿尺方向的投影距离；大小与快慢无关（快慢需要 Δds / Δt）；
3. **`s0` 是参考位置、不带方向**：`s0` 是 L10 的窗口内有效帧 `s_px` 平均值；正负来自 `s_px` 与 `s0` 的相对关系；
4. **正方向来自 P1 → P2 的人为约定**：M4 = 10 cm → 16 cm（第 46 行约定、第 55 行 `U`）；M5 = 10 cm → 20 cm（第 66 行 `U_004`）；约定反转会让所有符号整体反号（不会报错）；
5. **运动方向由 Δds 决定**：`Δds = ds[i+1] − ds[i]`；Δds > 0 = 向正方向运动、Δds < 0 = 向负方向运动、Δds = 0 = 该相邻间隔读数不变；
6. **Δds 的两个前提**：两端都 valid（`ds` 非空）才能相减；空洞处 Δds 断开（M4 的平台之间就是空洞）；
7. **Δds 不是速度**：速度 = Δds / Δt（30 fps 时 Δt ≈ 0.033333 s）；本项目没有速度字段，本课也不算速度；
8. **源码里没有 Δds 字段**：源码把规则写成文字"正向 = ds 增大 / 负向 = ds 减小"（M5 第 83～84、480 行）；Δds 是本课引入的概念量；转向点算法用的是原始 `x_px`（第 496、524～526 行）；`ux > 0 ⇒ 正向对应原始 x 增大`（第 481 行）；
9. **M4 静态形态 = 平台 + 台阶 + 空洞**：STATIC-002 / STATIC-003 各有 7 个平台（约 0、10、20、30、40、50、60 mm；台阶间隔约 10 mm），平台之间是长段 valid=False 的空洞；
10. **M5 动态形态 = 连续往返**：1766/1766 全部 valid、无空洞；`ds_mm` −0.5283（frame 0）～66.1663（frame 1701）；数值多次上升、下降；
11. **真实例子（负侧向正）**：M5 f237 → f313，`ds_mm` 从 −0.0046 增大到 +27.1660（Δds = +27.1706 mm）；
12. **真实例子（正侧向负）**：M5 f963 → f1015，`ds_mm` 从 +39.7894 减小到 +26.1587（Δds = −13.6307 mm）；
13. **正 / 负 / 零计数是符号侧统计**：按 `ds_mm` 非空（valid）行计数；1016/34/0、1174/18/0、1605/161/0；"零 0 例"只表示 4 位小数里没有恰好 0.0000 的行；
14. **无效帧留空、不删除**：第 272～274 行初始化为 None；第 284～285 行仅 valid 算 `s_px`；第 338～340 行仅 valid 算 `ds_px` / `ds_mm`；第 360～363 行写空字符串；第 355 行注释"绝不写 0 / -1 / nan"；
15. **`MIN_TURN_TRAVEL_PX = 20.0` 的最小认识**（第 30、85～87、503～506 行）：反向行程阈值——原始 `x_px` 从当前极值反向走满 20 px 才承认转向；静止段噪声（中位数约 0.13 px、最大约 1.25 px）触发不了；
16. **本课边界**：`detect_turning_points()` 完整算法、峰谷完整判定、运动段完整切分、周期、频率、FFT 全部留到 L12 及以后，本课只登记名称与位置。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| M4 位移模块（源码主角） | `src\displacement.py` | 第 46 行正方向约定；第 55 行 `U`；第 301～303 行初始化位移字段；第 313～314 行仅 valid 算 `s_px`；第 367～369 行仅 valid 算 `ds_px` / `ds_mm`；第 389～392 行无效值写空 |
| M5 位移模块（源码主角） | `src\dynamic_displacement.py` | 第 66 行 `U_004`；第 83～84 行正向 / 负向定义；第 87 行 `MIN_TURN_TRAVEL_PX = 20.0`；第 111～113 行方向文字常量；第 133 行 `U_004` 方向说明；第 462 行起 `detect_turning_points()`（本课只做最小介绍） |
| 真实数据（只读核对，未重新生成） | `results\EXP-003-STATIC-002_ds.csv`、`results\EXP-003-STATIC-002_track.csv` | 各 1961 行；valid 1050 / invalid 911；`ds_mm` −0.2170～60.8426；正/负/零 = 1016/34/0；形态：平台 + 台阶 + 空洞 |
| 真实数据（只读核对，未重新生成） | `results\EXP-003-STATIC-003_ds.csv`、`results\EXP-003-STATIC-003_track.csv` | 各 1984 行；valid 1192 / invalid 792；`ds_mm` −0.0540～60.1932；正/负/零 = 1174/18/0；形态：平台 + 台阶 + 空洞 |
| 真实数据（只读核对，未重新生成） | `results\EXP-004-DYNAMIC-001_ds.csv`、`results\EXP-004-DYNAMIC-001_track.csv` | 各 1766 行；valid 1766 / invalid 0；`ds_mm` −0.5283～66.1663；正/负/零 = 1605/161/0；形态：连续往返 |
| 本节课笔记 | [`L11_位移正负与运动方向.md`](L11_位移正负与运动方向.md) | 17 节完整笔记（含自测题 21 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- `src\displacement.py` 第 46 行（原文）："两点真实距离：60.0 mm，方向约定 10 cm -> 16 cm"；第 55 行：`U = (0.999976, -0.006894)`（单位方向向量，方向为 10 cm → 16 cm）；
- 第 301～303 行：`row["s_px"] = None`、`row["ds_px"] = None`、`row["ds_mm"] = None`（无效行保持留空）；
- 第 313～314 行：`if row["valid"]: row["s_px"] = project_point((row["x_px"], row["y_px"]), U)`；
- 第 367～369 行：`if row["valid"]: row["ds_px"] = row["s_px"] - s0`（第 368 行）；`row["ds_mm"] = row["ds_px"] / PX_PER_MM`（第 369 行）；
- 第 389～392 行：`s_px` / `ds_px` / `ds_mm` / `area_px` 为 None 时写成空字符串；第 384 行注释"缺失数据一律写成空字符串（""），绝不写 0 / -1 / nan"；
- `src\dynamic_displacement.py` 第 66 行：`U_004 = (0.999992, -0.003913)`（方向 10 cm → 20 cm（正向））；
- 第 83～84 行："正向 = ds 增大（沿 U_004，即尺子 10 cm -> 20 cm 方向）"；"负向 = ds 减小"；
- 第 87 行：`MIN_TURN_TRAVEL_PX = 20.0`；第 85～86 行说明："只有当原始 x 从当前极值反向走了至少 20 px，该极值才被确认为转向点（静止段噪声不可能触发）"；
- 第 111～113 行：`DIRECTION_POSITIVE = "正向"`、`DIRECTION_NEGATIVE = "负向"`（注释："只允许这两种说法"）；
- 第 133 行："U_004 指向 10 cm -> 20 cm（ux > 0，即"ds 增大"为正向）"；
- 第 462 行起 `detect_turning_points()`（docstring 第 503～506、509～510 行；内部算法第 512～594 行属于 L12，本课不展开）。

### L11 源码地图

| 位置（`src\displacement.py`，共 866 行） | 内容 |
| --- | --- |
| 第 41～55 行 | 标定点 P1 / P2 与"方向约定 10 cm -> 16 cm"（第 44～46 行）；`U`（第 55 行） |
| 第 290～303 行 | `add_valid_flags()`（第 301～303 行初始化位移字段） |
| 第 306～314 行 | `add_projection()`（第 313～314 行仅 valid 帧算 `s_px`） |
| 第 357～369 行 | `add_displacement()`（第 367～369 行仅 valid 帧算 `ds_px` / `ds_mm`；第 368 行 `ds_px = s_px - s0`） |
| 第 377～395 行 | `build_ds_row()`（第 389～392 行无效值写空） |

| 位置（`src\dynamic_displacement.py`，共 1259 行） | 内容 |
| --- | --- |
| 第 30 行 | 模块 docstring：最小运动行程 `MIN_TURN_TRAVEL_PX = 20.0 px` |
| 第 59～66 行 | M5 标定与 `U_004`（第 66 行） |
| 第 82～87 行 | 运动方向统计规则（第 83～84 行正向 / 负向；第 87 行阈值） |
| 第 111～113 行 | `DIRECTION_POSITIVE` / `DIRECTION_NEGATIVE` |
| 第 121～175 行 | 冻结常量自检（第 133 行 `U_004` 方向说明） |
| 第 487～623 行 | 转向点 / 运动段检测（第 462 行定义；本课只登记，不展开） |

（行号按 2026-10-04 当前源码逐行核对；如果实际源码行号发生变化，以当前真实源码为准。全部数据为只读核对，未重新生成。）

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L11 位移数据、正负号与运动方向"（Δds、运动方向、正向 / 负向、正方向约定（P1 → P2）、参考位置与符号侧、平台 + 台阶 + 空洞、连续往返、MIN_TURN_TRAVEL_PX、符号统计、五类材料 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L11 位移数据、正负号与运动方向"（把 ds 的正负当好坏 / 快慢、用 ds 的符号判断运动方向、跨空洞算 Δds、把 Δds 当速度、把符号统计当方向统计、混用 M4 / M5 正方向约定、在 L11 急着学峰谷 / 周期 / 频率 等）。

### 本节课暂未学习的内容

~~`detect_turning_points()` 完整算法（`src\dynamic_displacement.py` 第 487～623 行）、峰谷完整判定、运动段完整切分~~（已在 L12 学习，见下一节）/ 周期、频率、FFT——仍属于后续课程；本课只登记名称与位置，不展开。

（本节学到"ds 的符号语义 → 正方向约定 → Δds 判方向 → 三份真实数据的符号 / 形态 / 方向例子 → MIN_TURN_TRAVEL_PX 最小认识"这条链；转向点完整算法与运动段切分已在 L12 学习；周期 / 频率 / FFT 只登记名称，留到后续课程。）

---

## L12 转向点检测与运动段切分

- **课程编号**：L12
- **课程标题**：转向点检测与运动段切分
- **学习状态**：已完成
- **记录日期**：2026-10-04
- **笔记文件**：[`L12_转向点检测与运动段切分.md`](L12_转向点检测与运动段切分.md)

### 本节课目标

- 说清为什么需要转向点检测：L11 的 Δds 变号只是"方向改变"的判据；程序还需要一条能对抗噪声、处理极值平台、可复现的规则，才能确定"哪一帧是转向点"；
- 说清转向检测的输入：只使用原始 `x_px` 序列（`detected=True` 且有 `x_px` 的行，按 frame 升序；第 496、524–526 行），不平滑、不滤波、不插值、不补帧、不预测（第 497 行）；
- 说清 `valid=False` 的行只统计、不删除（第 527 行；第 514 行"只统计，不删除"），它们仍留在分析序列里参与检测；
- 背出状态机的三个变量：`turn_indexes`（第 542 行）、`direction`（第 543 行：0 / +1 / −1）、`extreme_index`（第 544 行）；
- 逐行讲清状态机三个分支（第 521–538 行）：`direction == 0` 如何确定方向；`direction == +1` 如何更新峰值与确认 peak；`direction == −1` 如何更新谷值与确认 valley；
- 说出 `MIN_TURN_TRAVEL_PX = 20.0`（第 87 行）是反向行程阈值；说清第 503–506 行的依据（静止段相邻帧 \|dx\| 中位数约 0.13 px、最大约 1.25 px；20 px 防止噪声制造假转向）；
- 严格区分极值（转向点本身）与确认帧：`turn_indexes` 存的是 `extreme_index`（第 558、565 行），不是确认帧 `i`；并用真实案例说明确认滞后（peak f491 → f505、valley f602 → f732、peak f838 → f971）；
- 说清 peak / valley：第 558 行生成 peak、第 565 行生成 valley；peak = 正向 → 负向，valley = 负向 → 正向；
- 说清 `turns` 七个字段（`describe()` 第 569–576 行 + turns 第 581–592 行）：`frame` / `time_s` / `x_px` / `ds_mm` / `kind` / `direction_before` / `direction_after`；`direction_before` / `direction_after` 由 `kind` 推导（第 585–590 行），不是再次测量；
- 说清 `segments` 输出（第 594–620 行）：第 595 行 `boundary_indexes` = 起点 + 所有转向点 + 终点；每段 start/end frame、time、x、direction、travel_px、below_min_travel；段数 = 转向点数 + 1（第 479 行）；首末帧只是边界（第 507–508 行）；
- 说清 `below_min_travel`（第 617 行）比较的是"整个运动段两端之间的行程"，与转向确认使用的"从当前极值反向的行程"不是同一个概念（两者都用 20 px，但比较对象不同）；
- 背出 EXP-004 真实结果：6 个转向点（491 peak、602 valley、838 peak、1063 valley、1254 peak、1513 valley）与 7 个运动段（205.05 / 84.80 / 126.17 / 92.22 / 190.09 / 128.80 / 188.61 px）；
- 说出这 6 个转向点与 `demo\run_m53_plot.py` 第 67–74 行冻结的 6 个 frame 完全一致（该脚本第 15–19 行明确不重新运行转向检测）；
- 复述工程思想：保留原始数据、不平滑、不插值、不补帧、不预测，用明确、冻结、可复现的规则处理噪声（第 16、27、28、30 行）；
- 说出课程关系：L10（ds）→ L11（Δds 与运动方向）→ L12（自动检测转向点、切分运动段）→ 后续课程（周期、频率、频谱等，本课不展开）。

### 核心概念

1. **转向点检测 = 用冻结规则确定"哪一帧是转向点"**：不能靠"这一帧比上一帧小"这种一帧判据；
2. **一帧判据不成立的三条原因**：噪声（静止段相邻帧 \|dx\| 中位数约 0.13 px、最大约 1.25 px，第 476 行）、极值平台、可复现性要求；
3. **输入是原始 `x_px` 序列**（`detected=True` 且 `x_px` 非空、按 frame 升序；第 467、524–526 行）；不使用 `s_px` / `ds`，不读平滑曲线；
4. **不平滑、不滤波、不插值、不补帧、不预测**（第 497 行；模块第 28 行）；
5. **`valid=False` 的行只统计、不删除**（第 527 行；第 514 行"只统计，不删除"）；它们仍留在分析序列里参与检测；
6. **状态机三个变量**：`turn_indexes`（第 542 行）、`direction`（第 514 行：0 / +1 / −1）、`extreme_index`（第 544 行）；
7. **`direction == 0`**：`|x_i − x_extreme| ≥ 20` 时确定方向（谁大往谁的方向），并把 `extreme_index` 移到 `i`（第 550–553 行）；
8. **`direction == +1`**：`x_i > x_extreme` 时更新峰值；`x_extreme − x_i ≥ 20` 时确认 peak 并翻转到 −1（第 554–560 行）；
9. **`direction == −1`**：镜像处理，`x_i < x_extreme` 时更新谷值；`x_i − x_extreme ≥ 20` 时确认 valley 并翻转到 +1（第 561–567 行）；
10. **`MIN_TURN_TRAVEL_PX = 20.0` 是反向行程阈值**（第 87、503–506 行）：只有从当前极值反向走满至少 20 px，该极值才算转向点；
11. **`turn_indexes` 存的是 `extreme_index`（转向点 / 极值帧），不是确认帧 `i`**（第 558、536 行）；确认帧只触发确认，随后 `extreme_index` 被重置为 `i`（第 531、567 行）；
12. **确认滞后是正常的**：peak f491 → f505 确认、valley f602 → f732 确认、peak f838 → f971 确认；这是抗噪与可复现的代价；
13. **peak = 正向 → 负向**（第 558 行），**valley = 负向 → 正向**（第 536 行）；因为 `ux > 0`，peak 也是 `ds` 的局部极大、valley 也是 `ds` 的局部极小（第 509–510 行）；
14. **`turns` 七个字段**：`frame` / `time_s` / `x_px` / `ds_mm`（`describe()` 第 569–576 行）+ `kind` / `direction_before` / `direction_after`（第 555–561 行）；后两个由 `kind` 推导；
15. **`segments` 用 `boundary_indexes = [0] + 所有转向点 + [len(series) − 1]` 切分**（第 595 行）；每段记录 start/end frame、time、x、direction、`travel_px`（第 600 行）、`below_min_travel`（第 617 行）；
16. **段数 = 转向点数 + 1**（第 479 行）；首帧和末帧只作为边界，不是转向点（第 507–508 行）；
17. **两种 20 px 比较对象不同**：转向确认比较"从极值反向的行程"（第 557、564 行）；`below_min_travel` 比较"整段两端之间的行程"（第 600、617 行）；
18. **EXP-004 真实结果**：6 个转向点与 7 个运动段（见下）；与 `demo\run_m53_plot.py` 第 67–74 行冻结的 6 个 frame 完全一致；本课不展开周期、频率、频谱（FFT）。

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 转向点 / 运动段检测（本课主角） | `src\dynamic_displacement.py` | 第 87 行 `MIN_TURN_TRAVEL_PX = 20.0`；第 491–622 行 `detect_turning_points()`；第 524–527 行分析序列；第 541–567 行状态机；第 569–576 行 `describe()`；第 581–592 行 turns；第 594–620 行 segments；第 617 行 `below_min_travel`；第 769–843 行报告打印 |
| 模块边界 | `src\dynamic_displacement.py` | 第 16、27、28、30 行（原始 x_px、不删行、不平滑 / 滤波 / 插值 / 补帧 / 预测、20 px 口径） |
| 冻结值引用 | `demo\run_m53_plot.py` | 第 15–19 行不重新运行转向检测；第 67–74 行 `FROZEN_TURNING_POINTS`（6 个 frame + 逐字 time_s / ds_mm） |
| 真实数据（只读核对，未重新生成） | `results\EXP-004-DYNAMIC-001_track.csv`、`results\EXP-004-DYNAMIC-001_ds.csv` | 各 1766 行、frame 0–1765；全部 detected / valid；起点 f0、终点 f1765；6 个转向点、7 个运动段 |
| 本节课笔记 | [`L12_转向点检测与运动段切分.md`](L12_转向点检测与运动段切分.md) | 19 节完整笔记（含自测题 21 道，均不附答案；文末另附"代码与事实来源说明"） |

### 本节课确认的源码事实

- 第 87 行：`MIN_TURN_TRAVEL_PX = 20.0`；第 85–86 行注释："只有当原始 x 从当前极值反向走了至少 20 px，该极值才被确认为转向点（静止段噪声不可能触发）"；
- 第 503–506 行 docstring："MIN_TURN_TRAVEL_PX = 20.0 是'反向行程阈值'：只有当原始 x 从当前极值反向走了至少 20 px，该极值才算转向点。本视频静止段的噪声（相邻帧 |dx| 中位数约 0.13 px、静止段最大约 1.25 px）远达不到 20 px，因此不会制造假转向 —— 这条规则在这里真正起作用"；
- 第 467–468 行：只使用原始 `x_px` 序列（`detected=True` 且有 x 的行，按 frame 升序），不平滑、不滤波、不插值、不补帧、不预测；第 507–508 行：首末帧只作为边界；段数 = 转向点数 + 1；第 509–510 行：正向 = ds 增大、负向 = ds 减小，`ux > 0` 使正向对应原始 x 增大；
- 第 524–526 行：`series = [row for row in rows if row["detected"] and row["x_px"] is not None]`；第 527 行：`analysis_invalid_rows = sum(1 for row in series if not row["valid"])`（只统计、不删除；第 514 行）；
- 第 529–539 行 report 骨架（analysis_rows / analysis_invalid_rows / start / end / turns / segments / min_turn_travel_px）；第 509–510 行 series 少于 2 行时提前返回；
- 第 541–544 行：`turn_indexes = []`、`direction = 0`、`extreme_index = 0`；
- 第 550–553 行（direction == 0）：`abs(x_i - x_extreme) >= MIN_TURN_TRAVEL_PX` → `direction = 1 if x_i > x_extreme else -1`，`extreme_index = i`；
- 第 554–560 行（direction == 1）：`x_i > x_extreme` → `extreme_index = i`；否则 `x_extreme - x_i >= MIN_TURN_TRAVEL_PX` → `turn_indexes.append((extreme_index, "peak"))`（第 558 行）、`direction = -1`（第 530 行）、`extreme_index = i`（第 531 行）；
- 第 561–567 行（direction == −1）：`x_i < x_extreme` → `extreme_index = i`；否则 `x_i - x_extreme >= MIN_TURN_TRAVEL_PX` → `turn_indexes.append((extreme_index, "valley"))`（第 536 行）、`direction = 1`（第 537 行）、`extreme_index = i`（第 567 行）；
- 第 569–576 行 `describe()`：返回 frame / time_s / x_px / ds_mm；第 546 行注释：ds_mm 在 valid=False 时为 None（打印"无"，不伪造数值）；第 578–579 行用它生成 start / end；
- 第 581–592 行 turns：`item = describe(series[index])`；`item["kind"] = kind`；peak → `direction_before = DIRECTION_POSITIVE`、`direction_after = DIRECTION_NEGATIVE`；否则 valley → 负向 → 正向（第 585–590 行）；报告写入 `report["turns"]`；
- 第 594–620 行 segments：第 595 行 `boundary_indexes = [0] + [index for index, _ in turn_indexes] + [len(series) - 1]`；第 600 行 `travel_px = abs(tail["x_px"] - head["x_px"])`；第 601–606 行按 tail/head 比较给出方向（正向 / 负向 / "无位移"）；第 609–618 行每段字段；第 617 行 `below_min_travel = travel_px < MIN_TURN_TRAVEL_PX`；
- 第 769–843 行打印：分析行数 / invalid 数（770–773）、起点（774–782）、终点（783–790）、转向点数量（763）、运动段数与 below_min 计数（793–800）、每个转向点（803–821）、每个运动段（824–843）；
- `demo\run_m53_plot.py` 第 15–19 行："不重新运行转向检测（只用 M5.2 冻结的 6 个 frame）"；第 67–74 行冻结 6 个 `(frame, time_s, ds_mm)`。

### L12 源码地图

| 位置（`src\dynamic_displacement.py`，共 1259 行） | 内容 |
| --- | --- |
| 第 16 行 | 数据链："原始 x_px 转向点统计（最小反向行程 20 px，不平滑、不滤波）" |
| 第 27–30 行 | 工程边界：不删行 / 留空、不写 0 / −1 / nan；不做平滑 / 滤波 / 插值 / 补帧 / 补零 / 预测 / FFT / 频率 / 周期 / 振幅；转向点只用原始 x_px，20 px |
| 第 85–87 行 | 阈值注释与 `MIN_TURN_TRAVEL_PX = 20.0` |
| 第 257–291 行 | `read_track_csv()`（按 CSV 行序读入，不排序、不删行） |
| 第 491–522 行 | `detect_turning_points()` 定义与 docstring（467–468、503–506、507–508、509–510 行） |
| 第 524–527 行 | 分析序列与 `analysis_invalid_rows` |
| 第 529–539 行 | report 骨架；series 少于 2 行提前返回 |
| 第 541–567 行 | zigzag 状态机（514 direction / 544 extreme_index / 550–553 初始方向 / 554–560 peak / 561–567 valley） |
| 第 569–576 行 | `describe()` |
| 第 578–579 行 | start / end 边界点 |
| 第 581–592 行 | turns 组装（585–590 行由 kind 推导 direction_before / after） |
| 第 594–620 行 | segments 组装（566 boundary_indexes / 571 travel_px / 588 below_min_travel） |
| 第 769–843 行 | 报告打印（17–21 项 + 每个转向点 + 每个运动段） |

| 位置（`demo\run_m53_plot.py`） | 内容 |
| --- | --- |
| 第 15–19 行 | 冻结要求：不重新运行转向检测，只用 M5.2 冻结的 6 个 frame |
| 第 67–74 行 | `FROZEN_TURNING_POINTS` 的 6 个 `(frame, time_s, ds_mm)` |
| 第 417–418、559 行 | 打印冻结转向点与"未重新检测" |

### EXP-004 真实数据（只读核对）

**输入事实**：track / ds CSV 各 1766 行（frame 0–1765），detected / valid 全部 True；`analysis_rows = 1766`、`analysis_invalid_rows = 0`；起点 f0（t 0.000000，x 852.81，ds_mm −0.5283）、终点 f1765（t 29.355535，x 1256.91，ds_mm 65.8647）。只读内存复算：`direction` 首次在 f246 确定为 +1（x0 852.81 → x246 873.27，差 20.46 px）。

**6 个转向点（turns）**：

| # | frame | time_s | x_px | ds_mm | kind | direction_before → direction_after | 确认帧（真实案例） |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 491 | 8.166327 | 1057.86 | 33.1549 | peak | 正向 → 负向 | f505（反向 21.71 px） |
| 2 | 602 | 10.012483 | 973.06 | 19.2217 | valley | 负向 → 正向 | f732（反向 22.28 px） |
| 3 | 838 | 13.937642 | 1099.23 | 39.9535 | peak | 正向 → 负向 | f971（反向 20.71 px） |
| 4 | 1063 | 17.679849 | 1007.01 | 24.7998 | valley | 负向 → 正向 | f1156（只读复算，20.03 px） |
| 5 | 1254 | 20.856567 | 1197.10 | 56.0319 | peak | 正向 → 负向 | f1346（只读复算，20.66 px） |
| 6 | 1513 | 25.164263 | 1068.30 | 34.8700 | valley | 负向 → 正向 | f1535（只读复算，20.08 px） |

**7 个运动段（segments）**：

| # | start frame | start x_px | end frame | end x_px | direction | travel_px | below_min_travel |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 0 | 852.81 | 491 | 1057.86 | 正向 | 205.05 | False |
| 2 | 491 | 1057.86 | 602 | 973.06 | 负向 | 84.80 | False |
| 3 | 602 | 973.06 | 838 | 1099.23 | 正向 | 126.17 | False |
| 4 | 838 | 1099.23 | 1063 | 1007.01 | 负向 | 92.22 | False |
| 5 | 1063 | 1007.01 | 1254 | 1197.10 | 正向 | 190.09 | False |
| 6 | 1254 | 1197.10 | 1513 | 1068.30 | 负向 | 128.80 | False |
| 7 | 1513 | 1068.30 | 1765 | 1256.91 | 正向 | 188.61 | False |

**与冻结值一致**：`demo\run_m53_plot.py` 第 67–74 行冻结的 6 个 frame（491 / 602 / 838 / 1063 / 1254 / 1513）及逐字 time_s / ds_mm 与上表完全一致；该脚本只用冻结 frame 绘图，不重新运行转向检测。

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L12 转向点检测与运动段切分"（转向点、peak / valley、`detect_turning_points()`、分析序列、状态机、direction、extreme_index、turn_indexes、反向行程阈值、确认帧、turns、describe、direction_before / direction_after、运动段、boundary_indexes、travel_px、below_min_travel、原始数据原则、冻结与可复现 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L12 转向点检测与运动段切分"（一帧变大/变小就认定转向、把 20 px 当相邻帧差值、混淆两种 20 px、把确认帧当转向点、删除 valid=False 行、用 ds / 平滑曲线做检测、把起点终点当转向点、把 direction_before / after 当测量、把专属口径当通用规则、以为要重新运行 demo、提前展开周期 / 频率 / FFT 等）。

### 本节课暂未学习的内容

周期、频率、频谱（FFT）、简谐振动理论——全部属于后续课程，本课只登记名称，不展开任何实质内容。

（本节学到"原始 x_px 分析序列 → zigzag 状态机 → 20 px 反向行程确认 → 极值帧 vs 确认帧 → peak / valley → turns / segments → EXP-004 真实结果与冻结一致性 → 工程思想"这条链；周期 / 频率 / 频谱只登记名称，留到后续课程。）

---

## L13 从运动段到往复运动——为什么可以开始讨论周期、频率与重复运动

- **课程编号**：L13
- **课程标题**：从运动段到往复运动——为什么可以开始讨论周期、频率与重复运动
- **学习状态**：已完成
- **记录日期**：2026-10-04
- **笔记文件**：[`L13_从运动段到往复运动.md`](L13_从运动段到往复运动.md)

### 本节课目标

- 说清 L13 的问题起点：L12 已经交出"带时间戳的转向点（turns）"与"单方向运动段（segments）"，项目第一次有资格讨论"重复运动"；
- 严格区分"项目已经实现的"与"刚刚开始讨论的"：源码只实现到 turns / segments；相邻转向点时间间隔、peak→peak / valley→valley 间隔统计、半周期统计、周期 T、频率 f、周期稳定性判据均未实现；
- 背出 `src\dynamic_displacement.py` 第 28 行的边界声明；
- 说清 `detect_turning_points()`（第 491–622 行）只负责转向点与运动段；
- 逐字段说出 turns（第 569–592 行）与 segments（第 594–620 行）；
- 说清当前代码只打印转向点数量、转向点信息、运动段信息，不打印间隔 / 周期 / 频率（第 792、794–799、806–821、827–842 行）；
- 说清 turns → 事件序列、segments → 单方向区间的作用；
- 说清"一个运动段 ≠ 一个周期"的三条理由；
- 说清半周期候选（peak→valley / valley→peak）与完整周期候选（peak→peak / valley→valley）；
- 说清周期成立的基本思想：间隔一致性 + 半周期与完整周期自洽 + 样本数量 + 数据一致性；
- 复述 EXP-004 的只读分析数字与本课结论；
- 复述 M6 对照信息与其性质（外部公开视频记录，不是 M5 已实现的算法）；
- 背出本课思想："先证明重复，再谈周期；先证明周期稳定，再谈频率。"

### 核心概念

1. 项目真实源码已实现：M2 单图检测 → M3 视频追踪 → M4 / M5 位移 → M5.2 转向点 turns → M5.2 运动段 segments；
2. 当前 M5 源码没有实现：相邻转向点时间间隔、peak→peak / valley→valley 间隔统计、半周期统计、周期 T、频率 f、周期稳定性判据；
3. `src\dynamic_displacement.py` 第 28 行原文："不做平滑 / 滤波 / 插值 / 补帧 / 补零 / 预测 / FFT / 频率 / 周期 / 振幅分析。"；
4. `detect_turning_points()`（第 491–622 行）只产出 turns（第 581–592 行）与 segments（第 594–620 行）；
5. turns 七个字段：`frame` / `time_s` / `x_px` / `ds_mm` / `kind` / `direction_before` / `direction_after`；其中 `time_s` 是 L13 的关键字段；
6. segments 字段：start / end 的 frame、time、x，`direction`、`travel_px`、`below_min_travel`；段时长可由两端时间相减得到，但源码没有做这个减法；
7. 打印边界：只有转向点数量（第 792 行）、运动段数量（第 794–799 行）、每个转向点（第 806–821 行）、每个运动段（第 827–842 行）；
8. 全项目检索 M5.4 / M5.5 无结果（0 条）；
9. turns 把连续运动转化为带时间戳、带事件类型的事件序列 → 可以做时间分析；
10. segments 提供每个单方向运动区间的起止时间、方向与行程；
11. 一个运动段 ≠ 一个周期：首尾段可能被视频边界截断（第 507–508 行）；一段只代表一个方向；周期应由同类事件之间定义；
12. 半周期候选 = peak→valley / valley→peak；完整周期候选 = peak→peak / valley→valley；
13. 周期成立的基本思想：同类事件的间隔 + 半周期与完整周期是否一致 + 样本数量 + 数据一致性；
14. EXP-004 只读分析：6 个转向点时间、5 个半周期候选、peak→peak / valley→valley 候选、2 × 半周期均值与偏差；结论是"有明显往复结构，但不能给出稳定可信的正式周期值"；
15. M6 对照：`docs\M6.3_FINAL_REPORT.md` 第 154–169 行的 T = 0.542593 s 等是 M6 外部公开视频记录，不是 M5 动态实验已实现的周期算法；
16. 本课思想："先证明重复，再谈周期；先证明周期稳定，再谈频率。"

### 对应的项目文件

| 类型 | 文件 | 说明 |
| --- | --- | --- |
| 本课主角（项目真实源码） | `src\dynamic_displacement.py` | `detect_turning_points()` 第 491–622 行；turns 第 569–592 行；segments 第 594–620 行；第 28 行边界声明；打印第 792、794–799、806–821、827–842 行 |
| M6 对照（项目真实源码） | `src\m63_final_visualization.py` | 第 7 行不重新计算周期 / 频率 / 极值 / FFT；第 110 行 `REPRESENTATIVE_INTERVAL` 写死字面量；第 112–127 行 `FROZEN`（`T_exp` / `f_exp` 等）；第 202–219 行只做封板值一致性核对 |
| M5.3 可视化脚本（项目真实源码） | `demo\run_m53_plot.py` | 第 19 行不计算周期 / 频率 / 振幅 / 频谱；第 67–74 行冻结 6 个转向点；第 382 行打印本轮不计算振动参数 |
| M6 对照报告 | `docs\M6.3_FINAL_REPORT.md` | 第 154–169 行：峰—峰 9 段均值 T = 0.542593 s；谷—谷 9 段 0.542593 s；半周期法 0.542105 s；互差 ≤ 0.09%（外部公开视频记录） |
| 真实数据（只读核对） | `results\EXP-004-DYNAMIC-001_track.csv`、`results\EXP-004-DYNAMIC-001_ds.csv` | 1766 行、frame 0–1765；6 个转向点的时间戳与位置 |
| 本节课笔记 | `docs\learning\L13_从运动段到往复运动.md` | 20 节完整笔记（含五类材料标签、概念伪代码与自测题） |

### 本节课确认的源码事实（项目真实源码）

- `src\dynamic_displacement.py` 第 28 行：不做平滑 / 滤波 / 插值 / 补帧 / 补零 / 预测 / FFT / 频率 / 周期 / 振幅分析；
- `detect_turning_points()`（第 491–622 行）：输入原始 `x_px` 序列，输出 turns / segments；第 507–508 行声明首末帧只是边界、段数 = 转向点数 + 1；
- turns 第 569–592 行：七个字段，`time_s` 第 544 行、`kind` 第 584 行、`direction_before` / `direction_after` 第 585–590 行；
- segments 第 594–620 行：`boundary_indexes` 第 595 行、`travel_px` 第 600 / 616 行、`below_min_travel` 第 617 行；
- 打印部分：第 792 行转向点数量、第 794–799 行运动段数量、第 806–821 行每个转向点、第 827–842 行每个运动段；没有时间间隔 / 周期 / 频率打印；
- 只读检索：全项目 `M5.4` / `M5.5` 命中 0 条；`src\` / `demo\` 中"周期 / 频率 / FFT"命中均为边界声明或 M6 冻结值引用；
- 旁证：`src\video_tracker.py` 第 17、615 行与 `src\external_oscillation_tracker.py` 第 31–33、407、611 行同样声明不做频率 / 周期分析；
- M6 侧：`src\m63_final_visualization.py` 第 7 行不重新计算周期 / 频率 / 极值 / FFT；第 110 行 `REPRESENTATIVE_INTERVAL = (150.0, 5.0000, 166.5, 5.5500, 0.550)` 是写死的字面量；第 112–127 行 `FROZEN` 含 `T_exp = 0.542593`、`f_exp = 1.843003` 等；第 202–219 行 `check_frozen_extrema_against_csv()` 只核对封板值与 CSV，不做极值搜索、不做周期重新计算；
- `demo\run_m53_plot.py` 第 19 行不计算周期 / 频率 / 振幅 / 频谱；第 67–74 行冻结 6 个转向点；第 382 行打印"本轮不计算任何振动参数"。

### EXP-004 的真实数据与只读分析

**转向点时间（真实数据，来自 track CSV）**：f491 peak 8.166327 s、f602 valley 10.012483 s、f838 peak 13.937642 s、f1063 valley 17.679849 s、f1254 peak 20.856567 s、f1513 valley 25.164263 s（与 `demo\run_m53_plot.py` 第 67–74 行冻结文本逐字一致）。

**相邻半周期候选（5 个，只读分析）**：1.846156 / 3.925159 / 3.742207 / 3.176718 / 4.307696 s；最小 1.846156 s、最大 4.307696 s、均值 3.399587 s、最大 / 最小约 2.33 倍。

**完整周期候选（只读分析）**：peak→peak = 5.771315 / 6.918925 s（均值 6.345120 s，2 个样本）；valley→valley = 7.667366 / 7.484414 s（均值 7.575890 s，2 个样本）。

**与 2 × 半周期均值的对照**：2 × 半周期均值 = 6.799174 s；peak→peak 均值约 −6.68%；valley→valley 均值约 +11.42%。

**本课结论**：EXP-004 可以确认存在明显的往复结构，但不能据此给出一个稳定、可信的正式周期值。

**性质声明**：以上间隔数字是本次课程对已有 CSV 的只读分析结果（内存中读取与计算，未写任何文件），不是当前项目代码已经实现的功能。

### M6 对照信息

`docs\M6.3_FINAL_REPORT.md` 第 154–169 行记录：峰—峰 9 段均值 T = 0.542593 s；谷—谷 9 段 0.542593 s；半周期法 0.542105 s；三种方法互差 ≤ 0.09%（第 158、159、165–169 行）。这是 M6 外部公开视频的数据记录，不是 M5 动态实验已经实现的周期算法。

### 相关术语与易错点

- 术语：[`COURSE_GLOSSARY.md`](COURSE_GLOSSARY.md) → "L13 从运动段到往复运动"（往复运动 / 重复运动、事件序列、事件间隔、半周期候选、完整周期候选、周期 T、频率 f、周期稳定性判据、冻结值（T_exp / f_exp）、运动段 ≠ 周期、M5 / M6 数据链区分 等）；
- 易错点：[`COURSE_MISTAKES.md`](COURSE_MISTAKES.md) → "L13 从运动段到往复运动"（把有转向点当成有稳定周期、把运动段当周期、只挑顺眼间隔、只看均值不看样本、把只读分析当项目功能、把 M6 的 T / f 当成 EXP-004 结论、以为源码打印了周期 / 频率、把首尾段当半周期样本、为整齐而平滑改阈值、提前展开 FFT / 简谐振动 等）。

### 本节课暂未学习的内容

- FFT / 频谱分析、简谐振动理论——本课只登记名称，不讲授、不计算；
- 如何把 turns 的时间戳真正做成间隔统计代码、如何建立"周期是否可信"的正式数据判据——留到下一课。

（本节学到"turns 的时间戳 → 事件序列 → 相邻间隔 / 同类事件间隔 → 往复结构 → 周期候选 → 一致性检查思想"这条链；所有间隔数字均为只读分析，项目源码只实现到 turns / segments。）

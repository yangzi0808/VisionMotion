# VisionMotion 专业术语表

本文件是 VisionMotion 学习过程中的**术语总表**，按课程编号组织，只登记"已经系统学习过"的术语。
每个术语记录四部分：**中文名称**、**英文名称**、**简单定义**、**VisionMotion 中的具体含义**。

使用方式：复习时先看下面的速查索引定位术语，再读对应词条；学完新课程后，把新术语补进对应课程的小节。
后续课程才会学习的术语不在正文中解释，只在文末"后续课程术语（尚未学习）"中登记名称。

## 速查索引

| 术语 | 中文名称 | 所属课程 |
| --- | --- | --- |
| Frame | 帧 | L01 / L05 / L06 |
| FPS | 每秒帧数 / 帧率 | L01 / L05 |
| CSV | 逗号分隔值（文件格式） | L01 / L06 |
| Time Series | 时间序列 | L01 |
| Pixel | 像素 | L01 / L03 |
| frame | 帧编号 / 帧序号 | L01 / L06 |
| time_s | 时间（秒） | L01 / L06 |
| x_px | 水平像素位置（M3：质心 x；M6：暗带 bbox 中心） | L01 / L06 |
| y0_px | 暗带上缘竖直像素位置 | L01 |
| Trajectory | 轨迹 | L01 |
| trajectory.csv | 正式轨迹数据文件 | L01 |
| detected | 检测成功标志 | L01 / L06 |
| bbox_w_px / bbox_h_px | 检测区域外接框宽度 / 高度 | L01 |
| area_px | 检测区域面积（M3：轮廓面积；M6：暗像素面积） | L01 / L06 |
| 图像坐标系 | image coordinate system | L01 |
| 时间分辨率 | temporal resolution | L01 |
| 局部极大 / 局部极小 | local maximum / local minimum | L01 |
| BGR | BGR 颜色通道顺序 | L02 / L03 |
| HSV | HSV 色彩空间 | L02 / L03 |
| Hue | 色相（H） | L02 / L03 |
| Saturation | 饱和度（S） | L02 / L03 |
| Value | 明度（V） | L02 / L03 |
| Mask | 掩膜 / 掩码 | L02 / L03 |
| Threshold | 阈值 | L02 / L03 |
| Morphological Opening | 形态学开运算 | L02 |
| Erosion | 腐蚀 | L02 |
| Dilation | 膨胀 | L02 |
| Contour | 轮廓 | L02 / L03 / L04 |
| Moments | 图像矩 / 轮廓矩 | L02 / L04 |
| Centroid | 质心 | L02 / L04 |
| Bounding Rectangle | 外接矩形 | L02 / L04 |
| Binary Image | 二值图 | L02 / L03 |
| Kernel | 核 / 结构元素 | L02 |
| Channel | 通道 | L02 |
| NumPy Array | NumPy 数组 | L03 |
| Image | 图像 / 图片 | L03 |
| RGB | RGB 颜色通道顺序 | L03 |
| Color Space | 颜色空间 | L03 |
| cv2.cvtColor | 颜色空间转换函数（OpenCV） | L03 |
| cv2.inRange | 范围阈值函数（OpenCV） | L03 |
| bitwise_or | 逐像素 OR 运算（OpenCV） | L03 |
| findContours | 轮廓查找函数（OpenCV） | L04 |
| RETR_EXTERNAL | 只取外部轮廓的检索模式 | L04 |
| CHAIN_APPROX_SIMPLE | 轮廓点简化存储方式 | L04 |
| Contour Area | 轮廓面积 | L04 |
| m00 | 零阶矩（面积总量） | L04 |
| m10 | 一阶矩（x 方向） | L04 |
| m01 | 一阶矩（y 方向） | L04 |
| MIN_AREA | 候选轮廓最小面积门槛 | L04 |
| Video | 视频 | L05 |
| VideoCapture | 视频读取对象（OpenCV） | L05 |
| cap.read | 读取下一帧（OpenCV） | L05 |
| ret | 读取是否成功的返回值 | L05 |
| current_frame | 当前正在处理的那一帧 | L05 |
| VideoWriter | 视频写入对象（OpenCV） | L05 |
| Overlay Video | 叠加标注视频 | L05 |
| release | 释放资源 | L05 |
| Frame Loop | 逐帧循环 | L05 |
| Function Reuse | 函数复用 | L05 |
| Module | 模块 | L05 |
| Row | 行（CSV） | L06 |
| Column | 列（CSV） | L06 |
| Header | 表头 | L06 |
| Cell | 单元格 | L06 |
| CSV_FIELDNAMES | CSV 字段名列表（表头与列顺序的唯一来源） | L06 |
| build_csv_row | 构造一行 CSV 数据的函数 | L06 |
| writerow | 写入一行（csv writer 方法） | L06 |
| lineterminator | CSV 行尾字符设置 | L06 |
| records | 逐帧记录列表（内存台账） | L06 |
| Missing Value | 缺失值（空 cell） | L06 |
| Discrete Time Series | 离散时间序列 | L01 / L06 |
| Field Design | 字段设计 | L06 |
| np.genfromtxt | NumPy 文本读取函数 | L06 |
| csv.DictWriter | 按字典写行的 CSV 写入器 | L06 |
| y_px | 质心竖直像素坐标 | L06 |
| _track.csv / _trajectory.csv | M3 / M6 逐帧数据文件（字段设计对照） | L06 |
| Detection Failure | 检测失败 | L07 |
| success | 成功标志（内存字段，对应 CSV 的 detected） | L07 |
| DETECTION FAILED | 失败提示文字（叠加视频） | L07 |
| (0,0) 伪数据 | 默认值伪数据（自检专门排查） | L07 |
| detection_rate | 检出成功率 | L07 |
| longest_miss_run | 最长连续丢失帧数 | L07 |
| Quality Check | 质量检查 | L07 |
| Robustness | 鲁棒性 | L07 |
| Evidence Boundary | 证据边界 | L07 |
| Calibration | 标定（像素尺度标定） | L08 |
| 图像坐标系 / 物理世界坐标系 | image / physical world coordinate systems | L01 / L08 |
| px/mm | 每毫米像素数（像素尺度 k） | L08 |
| mm/px | 每像素毫米数 | L08 |
| pixel_distance | 像素距离 L_pixel | L08 |
| compute_scale | 像素尺度计算函数 | L08 / L09 |
| real distance | 已知真实长度（real_distance_mm） | L08 |
| PX_PER_MM / MM_PER_PX | M4 冻结标定常量 | L08 |
| PX_PER_MM_004 / MM_PER_PX_004 | M5（EXP-004 专属）冻结标定常量 | L08 |
| unit_direction | 单位方向向量函数 | L08 / L09 |
| project_point | 一维投影函数 | L08 / L09 |
| s_px | 沿尺方向的一维投影坐标 | L08 / L09 |
| ds_px | 相对位移（像素） | L08 |
| ds_mm | 相对位移（毫米） | L08 |
| 无标定原则 | Calibration Boundary（没有有效标定就只能停留在像素层面） | L08 |
| y0_px（字段名读法） | 暗带上缘竖直像素位置（补充视角：0 属于字段名） | L01 / L06 / L08 |
| 原始方向向量 | raw direction vector（v = P2 − P1） | L09 |
| 单位方向向量 | unit direction vector（u = v / 向量长度） | L09 |
| 归一化 | normalization（让向量长度为 1） | L09 |
| 点积 | dot product（两乘一加） | L09 |
| 有号投影长度 | signed projection length（沿方向的像素距离） | L09 |
| ux / uy | 单位方向向量的两个分量（cos θ / sin θ） | L09 |
| 正交分解 | orthogonal decomposition | L09 |
| U | M4 冻结方向常量 | L09 |
| U_004 | M5（EXP-004 专属）冻结方向常量 | L09 |
| 六类材料 | 真实源码 / 真实项目常数 / 真实数据 / 数学公式 / 教学示例 / 概念伪代码 | L09 |
| 只读核对 | read-only verification（不修改、不重新生成数据） | L09 |
| valid gate | 第二道数据筛选（valid 判定） | L10 |
| is_valid_frame | valid 判定函数 | L10 |
| detected 与 valid 的区别 | 第一道 / 第二道筛选的区别 | L10 |
| 无效帧留空 | 位移字段的缺失表示（不写 0 / -1 / nan） | L10 |
| s0 | 位移基线（窗口内有效帧 s_px 平均值） | L10 |
| compute_s0 | 基线计算函数 | L10 |
| S0_WINDOW_S / MIN_S0_VALID_FRAMES | s0 窗口与最少有效帧参数 | L10 |
| 位置与位移 | position vs displacement | L10 |
| ds_px（补充视角） | 相对位移（像素，完整定义与真实数据） | L08 / L10 |
| ds_mm（补充视角） | 相对位移（毫米，完整定义与真实数据） | L08 / L10 |
| 双重舍入（补充视角） | double rounding（真实数据复核） | L08 / L10 |
| valid_rate / invalid_count | 有效性统计字段 | L10 |
| detected_invalid_count / longest_invalid_run | 被拒帧统计与最长连续 invalid | L10 |
| 数据依赖链 | detected → valid → s_px → ds_px → ds_mm | L10 |
| Δds | 位移变化量（ds 的逐帧差分，判运动方向） | L11 |
| 运动方向 | motion direction（正向 / 负向，由 Δds 判定） | L11 |
| 正向 / 负向 | DIRECTION_POSITIVE / DIRECTION_NEGATIVE（只允许这两种说法） | L11 |
| 正方向约定 | P1 → P2 人为约定（M4 10→16 cm；M5 10→20 cm） | L11 |
| 参考位置与符号侧 | s0 与 ds 正负的读法（正侧 / 负侧） | L11 |
| 符号统计 | 正 / 负 / 零计数（按 ds_mm 非空行） | L11 |
| 平台 + 台阶 + 空洞 | M4 静态位移形态 | L11 |
| 连续往返 | M5 动态位移形态 | L11 |
| MIN_TURN_TRAVEL_PX | 最小反向行程阈值（20 px，最小认识） | L11 |
| 五类材料 | 项目真实源码 / 真实数据 / 教学示例 / 概念解释 / 概念伪代码 | L11 |
| 转向点 | turning point（方向改变的极值位置） | L12 |
| 峰值 / 谷值 | peak / valley | L12 |
| detect_turning_points | 转向点检测函数 | L12 |
| 分析序列（analysis_rows / analysis_invalid_rows） | analysis series（参与检测的行与其中 invalid 行数） | L12 |
| 状态机（zigzag） | zigzag state machine | L12 |
| direction（0 / +1 / −1） | 当前已确认方向 | L12 |
| extreme_index | 当前方向上的极值下标 | L12 |
| turn_indexes | 已确认转向点列表 | L12 |
| MIN_TURN_TRAVEL_PX / 反向行程阈值 | reverse travel threshold（20 px） | L12 |
| 确认帧 | confirmation frame | L12 |
| turns（转向点报告） | turns report | L12 |
| describe() | 转向点 / 边界点字段整理函数 | L12 |
| direction_before / direction_after | 转向前后方向（由 kind 推导） | L12 |
| 运动段 | motion segment | L12 |
| boundary_indexes | 运动段边界索引 | L12 |
| travel_px | 段行程（两端之间的行程） | L12 |
| below_min_travel | 段行程是否小于 20 px | L12 |
| 边界点（起点 / 终点） | boundary points | L12 |
| 原始数据原则（不平滑 / 不滤波 / 不插值 / 不补帧 / 不预测） | raw-data principle | L12 |
| 冻结规则与可复现性 | frozen rules & reproducibility | L12 |
| 往复运动 / 重复运动 | reciprocating / repetitive motion | L13 |
| 事件序列（turns 事件序列） | event sequence | L13 |
| 事件间隔 | event interval | L13 |
| 半周期候选 | half-period candidate | L13 |
| 完整周期候选 | full-period candidate | L13 |
| 周期 T | period | L13（概念层；项目未实现） |
| 频率 f | frequency | L13（概念层；项目未实现） |
| 周期稳定性判据 | period stability criterion | L13（概念层；项目未实现） |
| 冻结值（T_exp / f_exp） | frozen values | L13 / M6 |
| 运动段 ≠ 周期 | segment ≠ period | L13 |

---

## L01 VisionMotion项目、CSV与时间序列

### 1. Frame

- **中文名称**：帧
- **英文名称**：Frame
- **简单定义**：视频中的一张静止画面。视频由许多按时间顺序排列的帧组成，每一帧代表一个具体的时间瞬间。
- **VisionMotion 中的具体含义**：当前外部视频（30 fps，1920 × 1080，共 236 帧）中的每一帧就是一幅画面；本项目对正式分析区间 frame 76–235 内的每一帧做一次检测，得到 trajectory.csv 中的一行数据。理解"视频 = 一帧一帧的图片"是理解本项目一切数据的前提。

### 2. FPS

- **中文名称**：每秒帧数 / 帧率
- **英文名称**：FPS（Frames Per Second）
- **简单定义**：视频每秒钟记录（或播放）的帧数。
- **VisionMotion 中的具体含义**：当前外部视频为 **30 fps**，即每秒 30 帧，相邻两帧的时间间隔 Δt = 1/30 s ≈ 0.033333 s。FPS 直接决定**时间分辨率**：帧与帧之间发生的事情，计算机没有数据，看不到。本项目正式数据区间 160 帧对应约 5.3333 s。

### 3. CSV

- **中文名称**：逗号分隔值（一种纯文本表格文件格式）
- **英文名称**：CSV（Comma-Separated Values）
- **简单定义**：用逗号把各个字段分隔开、一行就是一条记录的纯文本表格文件；第一行通常是表头，用来说明每一列是什么。
- **VisionMotion 中的具体含义**：项目用 CSV 保存"每一帧的检测结果"。当前正式文件为 `results\EXP-EXT-LAB67-V1_trajectory.csv`，共 160 行数据、8 列，表头为 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`。它是把视觉检测结果变成"可保存、可继续计算的数据"的关键文件。

### 4. Time Series

- **中文名称**：时间序列
- **英文名称**：Time Series
- **简单定义**：按照时间顺序排列的一系列测量值。
- **VisionMotion 中的具体含义**：以 time_s 为时间轴、以 y0_px 为测量值，就构成本项目的位置时间序列 **y0(t)**——"每隔约 1/30 秒记录一次目标（暗带上缘）位置，再按时间顺序排好"的 160 个测量值。它是离散的测量信号，不是一条连续曲线。

### 5. Pixel

- **中文名称**：像素
- **英文名称**：Pixel（缩写 px）
- **简单定义**：数字图像的最小单位；一幅图像由许多像素按行、列排成网格组成，每个像素记录该点的亮度/颜色信息。
- **VisionMotion 中的具体含义**：轨迹 CSV 中所有位置与尺寸字段的单位都是像素：x_px、y0_px、bbox_w_px、bbox_h_px 单位为 px；area_px 是"像素个数"。注意像素是**画面上的位置单位**，本项目第一阶段还没有把它换算成毫米（那属于标定 Calibration，后续课程学习）。

### 6. frame

- **中文名称**：帧编号 / 帧序号
- **英文名称**：frame
- **简单定义**：某一帧在视频中的序号，是一个计数（整数），回答"这是第几帧"。
- **VisionMotion 中的具体含义**：trajectory.csv 的第一列。当前正式数据从 frame 76 到 frame 235，共 160 个数据时刻。frame = 77 表示"视频的第 77 帧"。**frame 不等于时间**：它必须借助帧率才能换算成时间（见 time_s）。

### 7. time_s

- **中文名称**：时间（单位：秒）
- **英文名称**：time_s
- **简单定义**：某一帧距离视频开始经过了多少秒，回答"过了多长时间"。
- **VisionMotion 中的具体含义**：trajectory.csv 的第二列，为时间序列提供时间轴。当前视频 30 fps，所以 **time_s ≈ frame / 30**：frame 76 → 2.533333 s，frame 77 → 2.566667 s，frame 78 → 2.600000 s。注意它和 frame 数值完全不同，不能混用（如 frame 76 对应约 2.533 s，不是 76 s）。

### 8. x_px

- **中文名称**：水平像素位置（暗带外接框中心）
- **英文名称**：x_px
- **简单定义**：画面中水平方向的像素坐标；数值越大，位置越靠右。
- **VisionMotion 中的具体含义**：记录检测到的暗带**外接框中心**的水平位置，在本项目中**仅作为质量检查（QC）记录**，不是正式位置特征。不要把 x_px 与 y0_px 混为一谈：本阶段的正式位置特征是 y0_px。

### 9. y0_px

- **中文名称**：暗带上缘竖直像素位置（正式位置特征）
- **英文名称**：y0_px
- **简单定义**：目标竖直方向的像素位置；在本项目中特指检测到的**暗带上边缘**所在的 y 像素坐标。
- **VisionMotion 中的具体含义**：**本阶段核心的运动信号**，y0(t) 就是用它的数值构成的。由于图像坐标 y 向下增加，y0_px 越大 → 暗带上缘在画面中越靠下；y0_px 越小 → 越靠上。真实数据：frame 77 处 y0_px = 508（第一个局部极小 → 画面中较高位置）；frame 85 处 y0_px = 622（第一个局部极大 → 画面中较低位置）。注意不要把它简单称为"目标中心坐标"。

### 10. Trajectory

- **中文名称**：轨迹
- **英文名称**：Trajectory
- **简单定义**：目标位置随时间变化的记录，即"位置—时间"序列。
- **VisionMotion 中的具体含义**：本项目的轨迹 = 每一帧测得的 y0_px 按时间顺序排列形成的 **y0(t)**，保存为 trajectory.csv。它回答"目标在这段时间里是怎么运动的"，是后续周期、频率等分析的数据基础。

### 11. trajectory.csv

- **中文名称**：正式轨迹数据文件
- **英文名称**：trajectory.csv
- **简单定义**：保存轨迹（位置时间序列）的 CSV 文件。
- **VisionMotion 中的具体含义**：当前正式文件为 `results\EXP-EXT-LAB67-V1_trajectory.csv`（160 行、8 列）。它在项目数据链中处于**承上启下**的位置：左边是视觉检测（视频 → 数字），右边是后续分析（数字 → 结论）：

  ```text
  视频 → 逐帧检测 → 每帧的目标位置 → trajectory.csv → 时间序列
  ```

### 12. detected

- **中文名称**：检测成功标志
- **英文名称**：detected
- **简单定义**：真 / 假值（True / False），表示这一帧有没有成功检测到合格目标。
- **VisionMotion 中的具体含义**：trajectory.csv 的第三列。当前正式数据 **160 / 160 帧 detected = True**，即没有缺失的测量时刻。它回答"这次的测量是否有效"，属于**检测质量字段**，不是运动信号。

### 13. bbox_w_px / bbox_h_px

- **中文名称**：检测区域外接框宽度 / 高度
- **英文名称**：bbox_w_px / bbox_h_px（bounding box width / height）
- **简单定义**：把检测到的区域恰好框住的矩形（外接框）的宽度和高度，单位像素。
- **VisionMotion 中的具体含义**：用于判断**检测区域的大小与形状是否合理**。属于检测质量指标，不是运动信号。

### 14. area_px

- **中文名称**：检测区域面积（暗像素个数）
- **英文名称**：area_px
- **简单定义**：检测区域包含的像素个数，可理解为该区域的像素面积。
- **VisionMotion 中的具体含义**：它用于判断检测区域是否足够大、是否像一条暗带（面积太小的区域不会被当作合格目标）。**它是检测质量指标，不是振动幅度**——数值有起伏不代表目标在做机械振动。

### 15. 图像坐标系

- **中文名称**：图像（像素）坐标系
- **英文名称**：image coordinate system
- **简单定义**：以图像**左上角**为原点、x 向右增加、y **向下增加**的二维坐标约定。
- **VisionMotion 中的具体含义**：y0_px 直接使用该坐标系，因此本项目里：**y0_px 局部极大 → 画面中的较低位置；y0_px 局部极小 → 画面中的较高位置**。这与数学课本里"y 向上为正"的笛卡尔坐标系直觉相反，是最容易记反的一点。

### 16. 时间分辨率

- **中文名称**：时间分辨率
- **英文名称**：temporal resolution
- **简单定义**：测量系统能够分辨的最小时间间隔。
- **VisionMotion 中的具体含义**：由 FPS 决定：30 fps → 相邻两个位置样本的间隔为 1/30 s ≈ 0.033333 s，这就是本项目的**时间分辨率**。发生在两帧之间的变化无法被分辨；谈论"极值出现的时刻"时，其定位精度也受这一间隔限制。

### 17. 局部极大 / 局部极小

- **中文名称**：局部极大值 / 局部极小值
- **英文名称**：local maximum / local minimum
- **简单定义**：在一个序列中，比左右相邻点都大（或都小）的点。
- **VisionMotion 中的具体含义**：用于描述 y0(t) 的往复变化。当前正式数据中：第一个**局部极小**出现在 frame 77（y0_px = 508），第一个**局部极大**出现在 frame 85（y0_px = 622）。切记在图像坐标系下，局部极大对应画面中**较低**的位置。（如何用极值计算周期、频率属于后续课程内容。）

---

## L02 marker_detector.py：从图片到目标中心

### 1. BGR

- **中文名称**：BGR 颜色通道顺序
- **英文名称**：BGR（Blue-Green-Red）
- **简单定义**：一种彩色像素的通道排列顺序：每个像素依次记录蓝（B）、绿（G）、红（R）三个数值，每个数值范围 0 ~ 255。
- **VisionMotion 中的具体含义**：OpenCV 读取彩色图片时默认得到 **BGR** 图片，一个像素写作 `[B, G, R]`；这与常见的 RGB 顺序**正好相反**，是最容易踩的坑之一。`src\marker_detector.py` 收到的输入 `image_bgr` 就是这种 BGR 图片，检测的第一步就是把 BGR 转成 HSV（`cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)`），因为 BGR 里颜色与亮度混在一起，不利于用固定区间框住红色。

### 2. HSV

- **中文名称**：HSV 色彩空间
- **英文名称**：HSV（Hue-Saturation-Value）
- **简单定义**：用色相（H）、饱和度（S）、明度（V）三个分量描述颜色的一种颜色空间；把"是什么颜色"和"颜色多浓、多亮"分开表示。
- **VisionMotion 中的具体含义**：`create_red_mask` 中通过 `cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)` 把 BGR 图片转换成 HSV 图片，然后才可以用 H 区间 + S、V 下限描述"红色"。好处是：光照变化主要影响 S 和 V，色相 H 相对稳定，红色更容易用稳定的区间框住。

### 3. Hue

- **中文名称**：色相（符号 H）
- **英文名称**：Hue
- **简单定义**：表示"这是什么颜色"；在色环上是一个角度位置。
- **VisionMotion 中的具体含义**：本项目用两段 H 区间描述红色：第一段 H ∈ [0, 10]，第二段 H ∈ [170, 179]。注意 **OpenCV 8 位 HSV 图中 H 的范围是 0 ~ 179，不是 0 ~ 360**（存储时角度被除以 2），所以红色第二段上界写 179。红色跨过色环 0°/360° 接缝，因此必须写成两段。

### 4. Saturation

- **中文名称**：饱和度（符号 S）
- **英文名称**：Saturation
- **简单定义**：颜色有多浓、多纯；S 越低颜色越灰越白，S 越高颜色越鲜艳。
- **VisionMotion 中的具体含义**：本项目要求 **S ≥ 100**（`RED_LOWER_1` 与 `RED_LOWER_2` 的第二个数字都是 100，上界 255）。这条下限把"太淡、发白发灰"的像素排除掉，避免把浅粉色或灰红色误判成目标。

### 5. Value

- **中文名称**：明度 / 亮度（符号 V）
- **英文名称**：Value
- **简单定义**：颜色有多亮；V 很低接近黑色，V 越高越明亮。
- **VisionMotion 中的具体含义**：本项目要求 **V ≥ 70**（两个红色区间的第三个数字都是 70，上界 255）。这条下限把"太暗、接近黑"的像素排除掉，减少阴影和暗背景被误判为红色的可能。

### 6. Mask

- **中文名称**：掩膜 / 掩码
- **英文名称**：Mask
- **简单定义**：一张与原图逐像素对应的黑白图，用来表示每个像素是否满足某个条件；255 = 满足，0 = 不满足。
- **VisionMotion 中的具体含义**：由 `cv2.inRange` 生成，是**单通道 8 位图**（尺寸 `(height, width)`，没有颜色通道）。两张红色区间的 mask 用 `cv2.bitwise_or` 合并，再过一次 3×3 开运算去噪，得到最终的红色 Mask：255 = "这个像素是红色"，0 = "不是"。它是一张**"逐像素的是/否判断表"**——mask 只说明"哪里符合规则"，还没有"目标"的概念，必须再经过 `findContours` 才会变成候选形状。

### 7. Threshold

- **中文名称**：阈值
- **英文名称**：Threshold
- **简单定义**：用来做判断的临界数值；高于/低于它就会走向不同的分支。
- **VisionMotion 中的具体含义**：本项目的阈值分两类：① HSV 区间上下界——`RED_LOWER_1`、`RED_UPPER_1`、`RED_LOWER_2`、`RED_UPPER_2`（S ≥ 100、V ≥ 70 也是阈值）；② 最小面积门槛 `MIN_AREA = 200`。它们都集中写在 `src\marker_detector.py` 文件顶部，是全项目检测参数的**唯一来源**，不允许在调用方重新定义。

### 8. Morphological Opening

- **中文名称**：形态学开运算
- **英文名称**：Morphological Opening
- **简单定义**：一种针对二值图的形态学操作，等于"先腐蚀、再膨胀"，常用于去掉细小的孤立白色区域。
- **VisionMotion 中的具体含义**：`create_red_mask` 中用 3×3 矩形核执行：`kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))`，然后 `cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)`。目的是去掉零散小噪点（反光点、杂散红点），同时尽量保留主体目标。**开运算不是模糊**、不是平滑滤波，它处理的是白色区域的形状。

### 9. Erosion

- **中文名称**：腐蚀
- **英文名称**：Erosion
- **简单定义**：形态学操作：让白色区域整体缩小；核覆盖范围内只要有一个黑像素，中心就被涂黑，因此细小孤立的白点会消失。
- **VisionMotion 中的具体含义**：开运算两步中的**第一步**（`cv2.MORPH_OPEN` 内部隐含）。它负责"吃掉"Mask 里细小的噪点，为下一步膨胀做准备；主体区域虽然在腐蚀后也变小了一圈，但不会被吃掉。

### 10. Dilation

- **中文名称**：膨胀
- **英文名称**：Dilation
- **简单定义**：形态学操作：让白色区域整体扩大；核覆盖范围内只要有一个白像素，就把该位置涂白。
- **VisionMotion 中的具体含义**：开运算两步中的**第二步**。腐蚀后幸存的主体区域经膨胀恢复回近似原来的大小；此时已被腐蚀掉的噪点无法恢复——这就是"去噪点、保主体"的完整机制。

### 11. Contour

- **中文名称**：轮廓
- **英文名称**：Contour
- **简单定义**：二值图上白色区域的边界，用一串点表示的一条闭合曲线；每个轮廓对应一个候选形状。
- **VisionMotion 中的具体含义**：`find_target_contour` 中用 `cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)` 提取：`RETR_EXTERNAL` 只取最外层轮廓（不关心内部洞），`CHAIN_APPROX_SIMPLE` 压缩冗余点。Mask 上的白色像素区域经过这一步才被"组织"成一个个候选形状；随后按 `cv2.contourArea` 排序取面积最大者，并以 `MIN_AREA = 200` 检查，得到目标轮廓。

### 12. Moments

- **中文名称**：图像矩 / 轮廓矩
- **英文名称**：Image Moments
- **简单定义**：对形状里像素的分布按位置加权求和得到的一族数值；不同阶的矩描述形状不同方面的信息。
- **VisionMotion 中的具体含义**：`calculate_centroid` 中用 `cv2.moments(contour)` 计算，主要使用三个：`m00`（零阶矩，与轮廓面积有关，也作分母）、`m10`（x 方向一阶矩）、`m01`（y 方向一阶矩）。如果 `m00 == 0`（形状退化），代码返回 `None`；否则用它们计算质心。

### 13. Centroid

- **中文名称**：质心
- **英文名称**：Centroid
- **简单定义**：形状的"中心点"；本质是把形状里所有像素的位置做加权平均（权重为像素本身），因此它由面积的分布决定。
- **VisionMotion 中的具体含义**：本项目**最终输出的目标位置**。公式为 `cx = m10 / m00`、`cy = m01 / m00`，单位像素，是浮点数。检测成功时 `detect_marker` 返回 `cx`、`cy`。必须区分：**质心 ≠ 外接矩形的几何中心**——质心来自矩（面积分布），外接矩形中心来自框的几何尺寸；目标形状不规则时两者明显不同。本项目位置输出用质心，因为标记边缘不一定对称，用轮廓矩算质心比外接矩形中心更稳。

### 14. Bounding Rectangle

- **中文名称**：外接矩形
- **英文名称**：Bounding Rectangle / Bounding Box
- **简单定义**：把形状恰好框住的最小正放矩形，用左上角坐标和宽高 (x, y, w, h) 表示。
- **VisionMotion 中的具体含义**：`detect_marker` 中用 `cv2.boundingRect(contour)` 得到 `(x, y, w, h)`，随结果字典返回。它**主要用于框选显示与辅助检查**（例如 demo 在 overlay 图上画绿色矩形、人工核对检测范围），不是本项目的位置输出。它的几何中心 `(x + w/2, y + h/2)` 与质心不是一回事。

### 15. Binary Image

- **中文名称**：二值图
- **英文名称**：Binary Image
- **简单定义**：每个像素只有两种取值的图像，通常用 0 和 255 表示"否 / 是"。
- **VisionMotion 中的具体含义**：红色 Mask 就是一张二值图（单通道 8 位，255/0）。形态学开运算、`findContours` 都以二值图为操作对象；它是对应的"像素级规则判断"这一层表示，区别于彩色原图（3 通道）与轮廓（对象级表示）。

### 16. Kernel

- **中文名称**：核 / 结构元素
- **英文名称**：Kernel / Structuring Element
- **简单定义**：形态学操作使用的小模板，在图像上逐像素移动，决定每个位置如何被腐蚀/膨胀处理。
- **VisionMotion 中的具体含义**：由 `cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))` 生成的 **3×3 矩形核**，大小由常量 `MORPH_KERNEL_SIZE = 3` 控制，是开运算的核心参数。核越大，形态学效果越强；本项目用 3×3 是"去噪点但不过度损伤主体"的折中。

### 17. Channel

- **中文名称**：通道
- **英文名称**：Channel
- **简单定义**：彩色图像中每个像素的分量数量；例如 RGB/BGR 图片有 3 个通道，灰度图只有 1 个通道。
- **VisionMotion 中的具体含义**：`image_bgr` 是 3 通道（B、G、R），shape 为 `(height, width, 3)`；转换后的 HSV 图也是 3 通道（H、S、V）；红色 Mask 是**单通道**，shape 为 `(height, width)`。区分"三通道彩色图"和"单通道二值图"是看懂本模块数据流的关键一步。

---

## L03 像素、颜色空间与 Mask 的实际运算

本节词条来自第 3 课《像素、颜色空间与 Mask 的实际运算》。与 L01/L02 重复的术语不重复基础解释，只补充 L03 的像素级视角。

### 1. Pixel

- **基础词条**：见 L01 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：像素
- **英文名称**：Pixel（px）
- **初学者解释**：数字图像的最小方格：画面被切成网格，每个小方格就是一个像素；每个像素里存的是一组数字（彩色像素是 3 个数字），不是"颜色的名字"。
- **VisionMotion 中的具体作用**：像素是整条检测链的起点——图片是像素网格，数组里逐像素访问（`img[y, x]`），再逐像素套颜色规则得到 Mask；轨迹数据中的位置与尺寸也以像素（px）为单位。
- **源码位置**：`src\marker_detector.py` 第 110 行附近的输入说明（`image_bgr` 是 `cv2.imread` 读进来的 BGR 图像）；逐像素运算集中在 `create_red_mask()`（第 41 行起）。

### 2. NumPy Array

- **中文名称**：NumPy 数组
- **英文名称**：NumPy Array（`numpy.ndarray`）
- **初学者解释**：Python 里表示多维数字表格的数据结构；一张彩色图片就是"高 × 宽 × 通道"的三维数组，例如形状 `(100, 80, 3)`。
- **VisionMotion 中的具体作用**：OpenCV 读进来的图片在 Python 中就是 NumPy 数组：形状 `(height, width, 3)`，用 `img[y, x]` 访问（先写行 y、再写列 x）；8 位图像用 `uint8`、单通道 0～255。本节所有"图片是数组"的讨论都建立在这个结构上。
- **源码位置**：`src\marker_detector.py` 的 `create_red_mask(image_bgr)` 接收的 `image_bgr` 就是 NumPy 数组（函数定义见第 41 行）。

### 3. Image

- **中文名称**：图像 / 图片
- **英文名称**：Image
- **初学者解释**：由像素组成的数字网格；对计算机来说，"图片"就是一张可以按位置读取数值的数字表格（彩色图多一个通道维度）。
- **VisionMotion 中的具体作用**：项目所有检测的输入对象。约定是：`marker_detector.py` 只接收"已经读好的图像数组"，自己不读文件；M2 单图检测由 `demo\run_single_image_detection.py` 读取图片后调用 `detect_marker(image)`。
- **源码位置**：`src\marker_detector.py` 第 110 行附近（输入说明）；调用方示例：`demo\run_single_image_detection.py` 第 115 行 `result = detect_marker(image)`。

### 4. BGR

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：BGR 颜色通道顺序
- **英文名称**：BGR（Blue-Green-Red）
- **初学者解释**：彩色像素按"蓝、绿、红"排列的三个 0～255 数字；`(0, 0, 255)` 是纯红，`(255, 0, 0)` 是纯蓝——与常见的 RGB 顺序正好相反。
- **VisionMotion 中的具体作用**：OpenCV 读图默认得到 BGR 图片；`create_red_mask` 的第一步就是把 BGR 转成 HSV。原因：同一个红色物体在不同光照下 BGR 三个数都会变化，直接用 BGR 写"什么算红"不够直观。
- **源码位置**：`src\marker_detector.py` 第 110 行附近的输入说明（`image_bgr` 为 BGR 图像）、第 48 行（BGR → HSV）。

### 5. RGB

- **中文名称**：RGB 颜色通道顺序
- **英文名称**：RGB（Red-Green-Blue）
- **初学者解释**：最常见的颜色顺序："红、绿、蓝"；很多教材、网页与图片软件默认使用它。
- **VisionMotion 中的具体作用**：项目里**不使用 RGB 作为 OpenCV 的默认读入顺序**；必须牢记 OpenCV 是 BGR。把 BGR 当 RGB 会把红色与蓝色整体搞反：例如 `(0, 0, 255)` 是纯红，不是纯蓝。
- **源码位置**：无（通用概念）；项目对照事实见 `src\marker_detector.py` 第 110 行附近的 BGR 输入说明。

### 6. HSV

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：HSV 色彩空间
- **英文名称**：HSV（Hue-Saturation-Value）
- **初学者解释**：用"是什么颜色（H）、颜色有多浓（S）、有多亮（V）"三个数字描述颜色；把颜色种类与浓淡、明暗拆开表示。
- **VisionMotion 中的具体作用**：先 `cv2.cvtColor(..., cv2.COLOR_BGR2HSV)` 转成 HSV，再用两个 `[H, S, V]` 区间筛选红色：H 决定颜色种类；S ≥ 100 排除太淡的像素；V ≥ 70 排除太暗的像素。注意 HSV 只是"更好用的记账方式"，不能理解为完全消除光照影响。
- **源码位置**：`src\marker_detector.py` 第 48 行（BGR → HSV）、第 51～52 行（按两个区间筛选）。

### 7. Hue

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：色相（符号 H）
- **英文名称**：Hue
- **初学者解释**：颜色在"色环"上的位置，回答"是什么颜色"；物理上是 0°～360° 的角度，OpenCV 8 位图把它缩放到 0～179（近似 H = 角度 ÷ 2）。
- **VisionMotion 中的具体作用**：红色定义的核心：区间 1 为 H 0～10、区间 2 为 H 170～179；因为红色跨过色环 0°/360° 接缝，必须写成两段。
- **源码位置**：`src\marker_detector.py` 第 22～27 行（四个阈值数组的第一个数字）。

### 8. Saturation

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：饱和度（符号 S）
- **英文名称**：Saturation
- **初学者解释**：颜色有多浓、多纯；S 越低越接近灰白，S 越高越鲜艳。
- **VisionMotion 中的具体作用**：两个红色区间都要求 **S ≥ 100**（上界 255）——把太淡、发白、发灰的像素排除，避免浅粉或灰红被误判成目标。
- **源码位置**：`src\marker_detector.py` 第 22～27 行（`RED_LOWER_1` / `RED_LOWER_2` 的第二个数字 100，上界 255）。

### 9. Value

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：明度 / 亮度（符号 V）
- **英文名称**：Value
- **初学者解释**：颜色有多亮；V 越低越接近黑，V 越高越明亮。
- **VisionMotion 中的具体作用**：两个红色区间都要求 **V ≥ 70**（上界 255）——把太暗、接近黑的像素排除，减少阴影和暗背景被误判为红色。
- **源码位置**：`src\marker_detector.py` 第 22～27 行（`RED_LOWER_1` / `RED_LOWER_2` 的第三个数字 70，上界 255）。

### 10. Color Space

- **中文名称**：颜色空间
- **英文名称**：Color Space
- **初学者解释**："描述颜色的一套坐标 / 记账方式"；同一个颜色可以换不同方式表示——描述方式变了，颜色本身没有变。
- **VisionMotion 中的具体作用**：项目涉及两种颜色空间：BGR（OpenCV 默认读入）与 HSV（用来筛红色）；两者之间的转换由 `cv2.cvtColor` 完成。注意"通道顺序（BGR vs RGB）"与"颜色空间（BGR vs HSV）"是两件不同的事。
- **源码位置**：`src\marker_detector.py` 第 48 行（BGR → HSV 的那次转换就是一次"换颜色空间"）。

### 11. Threshold

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：阈值
- **英文名称**：Threshold
- **初学者解释**：做判断用的数值分界 / 范围；"什么算红"就是一组明确的数值条件。
- **VisionMotion 中的具体作用**：红色阈值分两层：① 同一个区间内 H、S、V 三个条件 **AND**（同时成立）；② 两个区间之间 **OR**（用 `cv2.bitwise_or` 合并）。四个阈值常量集中在文件顶部。
- **源码位置**：`src\marker_detector.py` 第 22～27 行（红色 HSV 阈值常量）；判断执行见第 51～52 行 `cv2.inRange`。

### 12. Mask

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：掩膜 / 掩码
- **英文名称**：Mask
- **初学者解释**：一张与原图逐像素对应的黑白图，用来表示每个位置"要不要保留"；255 = 保留，0 = 不保留。
- **VisionMotion 中的具体作用**：由两次 `cv2.inRange`（区间 1 得 `mask_low`、区间 2 得 `mask_high`）再用 `cv2.bitwise_or` 合并成一张红色 Mask：单通道 8 位、尺寸 H×W、只有 0/255。它**不是原图**、**不是目标本身**，而是颜色筛选的中间结果，之后作为 Contour 的输入。
- **源码位置**：`src\marker_detector.py` 第 51～52 行（两张 Mask）、第 55 行（合并）、第 73 行（作为 `cv2.findContours` 的输入）。

### 13. Binary Image

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：二值图
- **英文名称**：Binary Image
- **初学者解释**：每个像素只有两种取值的图；本项目的 Mask 用 0 与 255 表示"不满足 / 满足"。
- **VisionMotion 中的具体作用**：红色 Mask 就是二值图；`cv2.inRange` 的输出、`cv2.bitwise_or` 的操作对象都是二值图——这是"逐像素颜色规则"这一层的标准表示。
- **源码位置**：`src\marker_detector.py` 第 45 行（`create_red_mask` 文档字符串："返回的掩膜是单通道 8 位图：红色区域为 255，其他区域为 0"）、第 51～52、55 行。

### 14. cv2.cvtColor

- **中文名称**：颜色空间转换函数（OpenCV）
- **英文名称**：cv2.cvtColor
- **初学者解释**：OpenCV 里用来"换颜色记账方式"的函数；第二个参数说明从什么转到什么，例如 `cv2.COLOR_BGR2HSV` 表示从 BGR 转到 HSV。
- **VisionMotion 中的具体作用**：`create_red_mask` 的第一步：把 BGR 原图转成 HSV 图，方便按颜色区间筛选。转换只改表示方式，不改图像尺寸与像素位置。
- **源码位置**：`src\marker_detector.py` 第 48 行（`create_red_mask` 内：`hsv_image = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)`）。

### 15. cv2.inRange

- **中文名称**：范围阈值函数（OpenCV）
- **英文名称**：cv2.inRange
- **初学者解释**：逐像素检查三个通道是否都落在给定的下界与上界之间；全满足输出 255，任意一个不满足输出 0，得到一张黑白图。
- **VisionMotion 中的具体作用**：用红色两个区间各调用一次，得到 `mask_low`（区间 1）与 `mask_high`（区间 2），每张只覆盖红色的一部分；输出是 H×W 单通道图。
- **源码位置**：`src\marker_detector.py` 第 51～52 行。

### 16. bitwise_or

- **中文名称**：逐像素"或"运算（OpenCV）
- **英文名称**：cv2.bitwise_or
- **初学者解释**：对两张图逐像素做 OR：0 OR 0 = 0；其余三种组合（0/255、255/0、255/255）都等于 255。
- **VisionMotion 中的具体作用**：把 `mask_low` 与 `mask_high` 合并成最终红色 Mask——只要两个红色区间中有一个判定该像素属于红色，就保留该像素。它对应逻辑上的"或者"，与区间内部的"并且"（AND）正好配对。
- **源码位置**：`src\marker_detector.py` 第 55 行（`mask = cv2.bitwise_or(mask_low, mask_high)`）。

### 17. Contour

- **基础词条**：见 L02 同名条目；本条目补充 L03 的像素级视角。
- **中文名称**：轮廓
- **英文名称**：Contour
- **初学者解释**：黑白图上白色区域的边界，用一串点表示的一个形状。
- **VisionMotion 中的具体作用**：本节只学"接口关系"：Mask（黑白区域）作为 `cv2.findContours` 的输入；Mask 把"颜色问题"转换成"黑白区域问题"，几何边界处理交给 Contour。本节不深入轮廓筛选、最大轮廓、面积门槛等细节（那些属于 L02 已学内容与后续课程）。
- **源码位置**：`src\marker_detector.py` 第 73 行（`find_target_contour(mask)` 内：`contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`）。

---

## L04 Contour、Moments 与 Centroid

本节词条来自第 4 课《Contour、Moments 与 Centroid：从目标区域到目标中心》。与 L01/L02 重复的术语不重复基础解释，只补充 L04 的区域 / 几何层与统计层视角。

### 1. Contour

- **基础词条**：见 L02 同名条目；本条目补充 L04 的区域 / 几何层视角。
- **中文名称**：轮廓
- **英文名称**：Contour
- **初学者解释**：把二值图里白色区域的外边界抽出来、用一串边界点表示的区域形状；它是"区域 / 几何层"的对象，不是逐像素的 0 / 255 表。
- **VisionMotion 中的具体作用**：L04 知识链"Mask → Contour → 最大轮廓 → 面积门槛 → Moments → Centroid → (cx, cy)"的关键一步。Mask 是像素层（每个位置要不要保留），Contour 是区域 / 几何层（白色区域的边界形状）；后续的面积排序、面积门槛、矩与质心计算全部建立在轮廓上。注意：Contour 只是"候选区域"，哪个轮廓才是目标由下一步规则（最大轮廓）决定。
- **源码位置**：`src\marker_detector.py` 第 73 行（`find_target_contour()` 内：`cv2.findContours` 的输入是 Mask、输出是轮廓列表）。

### 2. findContours

- **中文名称**：轮廓查找函数（OpenCV）
- **英文名称**：findContours（`cv2.findContours`）
- **初学者解释**：OpenCV 函数：输入一张二值图，输出图中白色区域的轮廓列表（每个轮廓是一串边界点），另外还返回一个本项目不用的第二个返回值。
- **VisionMotion 中的具体作用**：把 L03 的红色 Mask 转换成候选区域列表，是"像素层 → 区域 / 几何层"的入口。源码写成 `contours, _ = cv2.findContours(...)`：`contours` 是轮廓**列表**（第 75～76 行判空、第 78～80 行排序取最大），第二个返回值按惯例用 `_` 丢弃。
- **源码位置**：`src\marker_detector.py` 第 73 行：`contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)`。

### 3. RETR_EXTERNAL

- **中文名称**：外部轮廓检索模式
- **英文名称**：RETR_EXTERNAL
- **初学者解释**：`findContours` 的检索模式参数之一：只取每个白色区域最外层的轮廓，不单独返回嵌套在内部的孔洞边界。
- **VisionMotion 中的具体作用**：红色标记是一整块实心区域，项目只关心"整块红色区域的外边界"，因此用 `RETR_EXTERNAL` 只取外部轮廓。它回答"要哪些轮廓"，可以减少候选数量、避免把内部边缘当成独立轮廓。
- **源码位置**：`src\marker_detector.py` 第 73 行（`cv2.findContours` 的第 2 个参数）。

### 4. CHAIN_APPROX_SIMPLE

- **中文名称**：轮廓点简化存储方式
- **英文名称**：CHAIN_APPROX_SIMPLE
- **初学者解释**：`findContours` 的轮廓点存储 / 近似参数：对直线段只保留端点，丢掉中间可以推算出来的冗余边界点，用更少的点表示同一条轮廓。它改变的是"轮廓怎么记录"，不是轮廓形状，也不是图像压缩。
- **VisionMotion 中的具体作用**：项目用它减少轮廓点数、节省内存；简化后的轮廓仍然可以正常用于 `contourArea`（面积）、`moments`（矩）与 `boundingRect`（外接矩形）等几何计算。
- **源码位置**：`src\marker_detector.py` 第 73 行（`cv2.findContours` 的第 3 个参数）。

### 5. Contour Area

- **中文名称**：轮廓面积
- **英文名称**：Contour Area（`cv2.contourArea`）
- **初学者解释**：轮廓包围出的几何面积，由轮廓点按几何方式计算，返回浮点数，单位是"像素面积"（可理解为 px²）。
- **VisionMotion 中的具体作用**：在第 79 行作为排序依据（按面积从大到小找出最大轮廓）；在第 83 行与 `MIN_AREA` 比较、做面积门槛判断；在第 140 行写入结果字典的 `"area"` 字段。**它不等于"统计 Mask 中 255 像素的简单计数"**：后者是像素层统计，`contourArea` 计算的是几何边界围出的面积，两者概念、算法、适用对象都不同。
- **源码位置**：`src\marker_detector.py` 第 79、83、140 行。

### 6. Moments

- **中文名称**：图像矩 / 轮廓矩
- **英文名称**：Moments（`cv2.moments`）
- **初学者解释**：对目标形状进行统计描述的一组量：把形状的面积、位置分布等信息压缩成若干数字；可以类比统计学里用均值、方差描述一组数据的分布。
- **VisionMotion 中的具体作用**：计算质心的第一步：`cv2.moments(contour)` 返回一个字典（键形如 `"m00"`、`"m10"`、`"m01"`……），本项目重点使用 `m00`、`m10`、`m01` 三个键，再用公式解出目标中心。**Moments 本身不返回中心点**，中心点是下一步用公式算出来的。
- **源码位置**：`src\marker_detector.py` 第 95 行（`calculate_centroid()` 内：`moments = cv2.moments(contour)`）。

### 7. m00

- **中文名称**：零阶矩
- **英文名称**：m00（zeroth-order moment）
- **初学者解释**：矩里的"总量"项；本项目里相当于轮廓的面积总量，描述形状整体有多大。
- **VisionMotion 中的具体作用**：质心公式的分母（总权重）：`cx = m10 / m00`、`cy = m01 / m00`；并且第 97～98 行先检查 `moments["m00"] == 0`，避免除零（无效时返回 `None`）。
- **源码位置**：`src\marker_detector.py` 第 97、100、101 行（`moments["m00"]`）。

### 8. m10

- **中文名称**：一阶矩（x 方向）
- **英文名称**：m10（first-order moment, x）
- **初学者解释**：把面积按 x 坐标加权后求和得到的量，描述"质量在 x 方向上的总体分布"。
- **VisionMotion 中的具体作用**：`cx` 公式的分子：`cx = moments["m10"] / moments["m00"]`。矩的下标中第一位是 x 的次数、第二位是 y 的次数，所以 `m10` 配 x——若与 `m01` 写反，`cx` 与 `cy` 会互换且程序不会报错。
- **源码位置**：`src\marker_detector.py` 第 100 行。

### 9. m01

- **中文名称**：一阶矩（y 方向）
- **英文名称**：m01（first-order moment, y）
- **初学者解释**：把面积按 y 坐标加权后求和得到的量，描述"质量在 y 方向上的总体分布"。
- **VisionMotion 中的具体作用**：`cy` 公式的分子：`cy = moments["m01"] / moments["m00"]`。注意图像坐标系 y 轴向下为正，`cy` 增大表示目标中心在画面中更靠下。
- **源码位置**：`src\marker_detector.py` 第 101 行。

### 10. Centroid

- **基础词条**：见 L02 同名条目；本条目补充 L04 的公式视角。
- **中文名称**：质心 / 目标中心
- **英文名称**：Centroid
- **初学者解释**：目标形状的"面积加权平均位置"，也就是目标中心 `(cx, cy)`；由矩的公式算出，是浮点数，单位是像素。
- **VisionMotion 中的具体作用**：本项目的最终检测结果：由 `cx = moments["m10"] / moments["m00"]`、`cy = moments["m01"] / moments["m00"]` 得到，并返回给上层（第 102 行 `return cx, cy`），最终写入结果字典的 `"cx"` / `"cy"` 字段。质心描述"目标实际形状的中心位置"，与 bounding rectangle 的中心不一定相同；本项目的运动测量使用质心。
- **源码位置**：`src\marker_detector.py` 第 100～102 行。

### 11. Bounding Rectangle

- **基础词条**：见 L02 同名条目；本条目补充 L04 的"与质心对比"视角。
- **中文名称**：外接矩形
- **英文名称**：Bounding Rectangle（`cv2.boundingRect`）
- **初学者解释**：能完整包住轮廓的最小正矩形，写成 `(x, y, w, h)`：`x, y` 是左上角坐标，`w, h` 是宽和高；它的中心是 `(x + w/2, y + h/2)`。
- **VisionMotion 中的具体作用**：用 `cv2.boundingRect(contour)` 得到 `bbox`，用于框住目标（画框、辅助检查、粗略尺寸）。它与质心是两回事：矩形中心只由轮廓最外圈的范围决定，质心由面积分布决定；规则对称形状上两者接近，不规则形状上可能相差明显。不要把矩形中心当作目标位置的替代品。
- **源码位置**：`src\marker_detector.py` 第 141 行（`x, y, w, h = cv2.boundingRect(contour)`）。

### 12. MIN_AREA

- **中文名称**：候选轮廓最小面积门槛
- **英文名称**：MIN_AREA
- **初学者解释**：一个"面积下限"参数：面积比它小的候选轮廓就不算目标。
- **VisionMotion 中的具体作用**：真实值 `MIN_AREA = 200`，单位是面积（像素²），不是长度。定义在第 33 行；使用在第 82～84 行：最大轮廓面积小于 200 时返回 `None`。它是"噪声保护 / 失败判断"——既挡掉零散的小白块，也让"没有可靠目标"这种情况明确地失败（上层 `detect_marker` 转成 `success=False`），而不是硬给一个猜测的坐标。
- **源码位置**：`src\marker_detector.py` 第 33 行（定义）、第 82～84 行（使用）。

---

## L05 从单张图片到视频：逐帧处理

本节词条来自第 5 课《从单张图片到视频：逐帧处理与 video_tracker.py》。与 L01／L02／L04 重复出现的术语不重复基础解释，只补充 L05 的视频处理视角。

### 1. Video

- **中文名称**：视频
- **英文名称**：Video
- **初学者解释**：可以理解成按时间顺序排列的一系列静态图片；它不是一个"新的数据种类"，而是"帧的序列"加上帧率等元数据。
- **VisionMotion 中的具体作用**：本项目的输入数据源之一。`data\raw\EXP-002-VIDEO-001.mp4` 就是被逐帧追踪的真实视频；视频不是"一张巨大图片"，程序用 VideoCapture 打开它、一次读一帧。视频 → 帧序列 → 逐帧检测，就是 L05 的知识主线。
- **源码位置**：`src\video_tracker.py` 第 119 行（`cv2.VideoCapture` 打开的输入文件）；`demo\run_video_tracking.py` 第 35 行（真实视频路径 `data\raw\EXP-002-VIDEO-001.mp4`）。

### 2. Frame

- **基础词条**：见 L01 同名条目；本条目补充 L05 的视频处理视角。
- **中文名称**：帧
- **英文名称**：Frame
- **初学者解释**：视频里的单张静态图片，是**实际的图像数组**（BGR NumPy 数组，有高度、宽度与 3 个颜色通道），可以像任何一张图片一样被检测函数处理。
- **VisionMotion 中的具体作用**：视频追踪的最小处理单位：每一帧先被 `detect_marker()` 检测，再把结果写进 CSV 的一行。第 438 行读出的 `first_frame` 与第 521 行读出的 `next_frame` 都是"一帧"；第 474、526 行的 `current_frame` 也是"一帧"。注意：一帧是图像数据，不是帧号（帧号是 `frame` / `frame_index`）。
- **源码位置**：`src\video_tracker.py` 第 438、474、485、521、526 行。

### 3. FPS

- **基础词条**：见 L01 同名条目；本条目补充 L05 的源码视角。
- **中文名称**：每秒帧数 / 帧率
- **英文名称**：FPS（frames per second）
- **初学者解释**：每秒有多少帧，也就是"视频的播放/记录速度"；它决定相邻两帧之间的时间间隔：间隔 = 1/fps。
- **VisionMotion 中的具体作用**：fps 在 `open_video()` 中从视频文件读取（第 124 行，未硬编码；第 147 行打印时特别注明）；主循环用它把帧号翻译成时间：`time_s = frame_index / fps`（第 488 行）。本项目视频 30 fps 时，相邻帧间隔 1/30 s ≈ 0.033333 s。fps 非法（<= 0）时第 432～435 行停止处理。
- **源码位置**：`src\video_tracker.py` 第 124、147、431～435、488 行。

### 4. VideoCapture

- **中文名称**：视频读取对象（OpenCV）
- **英文名称**：VideoCapture（`cv2.VideoCapture`）
- **初学者解释**：OpenCV 里用来打开视频文件、一次读取一帧的对象；还能用 `cap.get()` 读取 fps、总帧数等视频属性。
- **VisionMotion 中的具体作用**：视频处理的入口，在 `open_video()` 中创建（第 119 行 `cap = cv2.VideoCapture(str(video_path))`）；打开失败时第 120～121 行明确返回 `(None, None)`；随后用 `cap.get(cv2.CAP_PROP_FPS)` 读 fps（第 124 行）、`cap.get(cv2.CAP_PROP_FRAME_COUNT)` 读总帧数（第 125 行）。它记住"读到哪儿了"，所以连续 `cap.read()` 能顺序拿到每一帧。
- **源码位置**：`src\video_tracker.py` 第 113、119～125 行。

### 5. cap.read

- **中文名称**：读取下一帧（OpenCV）
- **英文名称**：cap.read（`cv2.VideoCapture.read`）
- **初学者解释**：从视频读取对象中读取一帧，返回两个值：`ret`（是否成功）与 `frame`（图像数据）；每调用一次，读取位置前进一帧。
- **VisionMotion 中的具体作用**：逐帧循环的"供帧"动作：第 438 行第一次读取第一帧（用于确定画面尺寸，第 444～457 行）；循环内第 521 行 `ret, next_frame = cap.read()` 读取下一帧；第 522～524 行读到 `ret=False` 就结束循环。视频处理的基本节奏"一次拿一帧 → 处理 → 换下一帧"就是由它实现的。
- **源码位置**：`src\video_tracker.py` 第 438、521 行（另见第 304 行 PNG 回退路径中的 `cap.read()`）。

### 6. ret

- **中文名称**：读取是否成功的返回值
- **英文名称**：ret（return 的缩写，OpenCV 惯例名）
- **初学者解释**：`cap.read()` 返回的第一个值，布尔标志：`True` 表示成功读到一帧，`False` 表示读不到（通常意味着视频结束）。
- **VisionMotion 中的具体作用**：循环的控制信号：第 439 行用 `if not ret or first_frame is None` 判断第一帧读取失败；第 522～524 行用 `if not ret or next_frame is None: break` 结束逐帧循环。**ret 和 frame 不是一回事**：`ret` 回答"读到了吗"，`frame` 才是"读到的那张图"（检测用 frame，判断结束用 ret）。
- **源码位置**：`src\video_tracker.py` 第 438～439、521～522 行。

### 7. current_frame

- **中文名称**：当前正在处理的那一帧
- **英文名称**：current_frame
- **初学者解释**：一个变量，存放"这一轮要处理的那一张图片"；它不是整个视频，每次循环结束后会被新的下一帧替换。
- **VisionMotion 中的具体作用**：主循环的处理对象：第 474 行 `current_frame = first_frame`（初始化，第一帧直接进入循环）；循环里第 485 行 `detect_marker(current_frame)` 检测它、第 507～515 行缩放它、画它；循环末尾第 526 行 `current_frame = next_frame` 换成新读到的下一帧（第 525 行同步递增 `frame_index`）。历史不留在 current_frame 里，而是靠 CSV（第 491 行）与 `records`（第 493～504 行）另外记账。
- **源码位置**：`src\video_tracker.py` 第 474、485、507～515、525～526 行。

### 8. VideoWriter

- **中文名称**：视频写入对象（OpenCV）
- **英文名称**：VideoWriter（`cv2.VideoWriter`）
- **初学者解释**：OpenCV 里用来把一帧一帧画面写成视频文件的对象；创建时要用 fourcc 指定编码器，并给出 fps 与画面尺寸。
- **VisionMotion 中的具体作用**：生成叠加标注视频：在 `open_overlay_writer()` 中创建（第 246 行 `cv2.VideoWriter_fourcc(*codec_name)`、第 247 行 `cv2.VideoWriter(str(overlay_path), fourcc, fps, (width, height))`）；编码器候选 mp4v / avc1（第 47 行），逐个尝试，打开成功返回 `(writer, codec_name)`（第 248～249 行），失败候选立即 `release()`（第 250 行）；主流程第 507～515 行 `writer.write(overlay)` 写入每一帧。**VideoWriter 是"写输出视频"，不是读取视频**——读取用 VideoCapture。
- **源码位置**：`src\video_tracker.py` 第 44、47、236～252、459～461、507～515 行。

### 9. Overlay Video

- **中文名称**：叠加标注视频
- **英文名称**：Overlay Video
- **初学者解释**：在原始画面的副本上叠加"检测结果标记"（外接框、中心点、坐标文字、帧号与时间）后写出的检查视频；原始视频本身不被修改。
- **VisionMotion 中的具体作用**：给人看的检查工具，由 `draw_tracking_frame()`（第 169 行）与第 507～515 行的写入流程生成，输出到 `results\EXP-002-VIDEO-001_overlay.mp4`。用途是人工检查三件事：检测框有没有跑偏、中心点有没有跟着目标、哪些帧检测失败（失败帧只显示 "DETECTION FAILED"，第 190～201 行）。它是检查工具，不是新的测量数据；正式数据以 CSV 为准。
- **源码位置**：`src\video_tracker.py` 第 169～233、507～515 行；输出路径见 `demo\run_video_tracking.py` 第 38 行。

### 10. release

- **中文名称**：释放资源
- **英文名称**：release
- **初学者解释**：用完把资源交还给系统：关闭视频读取器 / 写入器，释放文件句柄与解码器；不释放可能导致资源被占用、输出文件不完整。
- **VisionMotion 中的具体作用**：资源清理写在 `finally` 块（第 534～538 行）：`csv_file.close()`（第 535 行）、`cap.release()`（第 536 行）、`writer.release()`（第 538 行，writer 存在时）；配合 `try`（第 482 行）与 `except KeyboardInterrupt`（第 530～533 行），即使中途异常或按 Ctrl+C，也尽量完成清理，已处理的帧数据仍保留在 CSV 与叠加视频中。失败路径上也有 `release()`：第 250、378、434、441 行等。
- **源码位置**：`src\video_tracker.py` 第 482、530～538 行（及第 250、378 行）。

### 11. Frame Loop

- **中文名称**：逐帧循环
- **英文名称**：Frame Loop
- **初学者解释**：对视频的每一帧重复执行同一套处理的循环结构；本项目采用的循环节奏是"处理当前帧 → 读取下一帧 → 判断是否结束"。
- **VisionMotion 中的具体作用**：`track_video()` 的 `while True:`（第 483 行）：每轮依次做检测（第 485 行）、时间换算（第 488 行）、写 CSV（第 491 行）、写叠加帧（第 507～515 行）、读取下一帧（第 521 行）、判断结束（第 522～524 行）、更新 `frame_index` 与 `current_frame`（第 525～526 行）。因为"先处理、后读下一帧、再判断"，**最后一帧也能被正常处理**。
- **源码位置**：`src\video_tracker.py` 第 483～526 行。

### 12. Function Reuse

- **中文名称**：函数复用
- **英文名称**：Function Reuse
- **初学者解释**：同一段函数被不同场景直接调用，而不是在每个新场景里复制粘贴一套新逻辑；写一次、测一次、多处使用。
- **VisionMotion 中的具体作用**：本节最重要的工程事实：`src\marker_detector.py` 的 `detect_marker()` 同时被单图检测（`demo\run_single_image_detection.py` 第 115 行）、视频逐帧追踪（`src\video_tracker.py` 第 485 行）与 PNG 回退方案（第 365 行）三处直接调用，检测函数本身没有为视频重写。这就是"单张图片检测升级为视频处理，本质上是把同一个检测函数放进逐帧循环中"。
- **源码位置**：`src\video_tracker.py` 第 34、365、485 行；`demo\run_single_image_detection.py` 第 115 行。

### 13. Module

- **中文名称**：模块
- **英文名称**：Module
- **初学者解释**：一个 `.py` 文件把相关功能组织在一起，通过 `import` 提供给别的文件使用；模块之间靠明确的接口协作。
- **VisionMotion 中的具体作用**：`src\marker_detector.py` 是"检测模块"，负责回答"这一张图片里目标在哪里"；`src\video_tracker.py` 是"视频追踪模块"，负责"视频什么时候读哪一帧、如何循环、如何记录结果、如何输出"；第 34 行 `from src.marker_detector import detect_marker` 就是两个模块之间的接口。`video_tracker.py` 的模块说明（第 15～23 行）还明确：检测参数的唯一来源是 `marker_detector.py`，本模块不重新定义检测参数。
- **源码位置**：`src\video_tracker.py` 第 15～23、34、485 行。

---

## L06 从逐帧结果到 CSV：数据记录、字段设计与时间序列

本节词条来自第 6 课《从逐帧结果到 CSV：数据记录、字段设计与时间序列》。与 L01／L05 重复出现的术语不重复基础解释，只补充 L06 的数据记录与字段设计视角；CSV_FIELDNAMES、build_csv_row 等词条默认指 `src\video_tracker.py`（M3），引用 M6 时会写明文件。

### 1. Row

- **中文名称**：行（CSV 的一行）
- **英文名称**：Row
- **初学者解释**：CSV 里横向的一条完整记录，由多个 cell 组成、用逗号分隔；一行代表一次记录。
- **VisionMotion 中的具体作用**：本项目约定"一行 = 一个时刻的一次视觉测量结果"：`track_video()` 第 491 行每处理一帧就写一行（成功、失败都写）；读取时第 648 行 `rows = list(reader)` 把整个文件读成"行的列表"，第 650～651 行把表头行与数据行分开；第 657～659 行要求数据行数 = 实际解码帧数。
- **源码位置**：`src\video_tracker.py` 第 491、646～651、657～659 行。

### 2. Column

- **中文名称**：列（CSV 的一列）
- **英文名称**：Column
- **初学者解释**：同一列在所有行里代表同一种属性；列的名字与顺序由第一行表头定义。
- **VisionMotion 中的具体作用**：第 41 行 `CSV_FIELDNAMES` 定义 6 列的名字与顺序；读取与检查时按列取值（第 686～687 行取 `x_px` / `y_px` / `area_px`，第 689、705 行读 `detected`），第 711～715 行逐列校验成功行与失败行的规则。改列顺序或列名会直接破坏这些既有代码与自检（第 653～655、665、723～724 行）。
- **源码位置**：`src\video_tracker.py` 第 41、686～715 行。

### 3. Header

- **中文名称**：表头
- **英文名称**：Header
- **初学者解释**：CSV 的第一行，说明每一列是什么；表头不是数据行。
- **VisionMotion 中的具体作用**：第 40 行注释明确"第一行就是真正的表头，前面不加任何 metadata"；第 479 行把 `CSV_FIELDNAMES` 写成第一行；读回时第 650 行 `header = rows[0]`、第 651 行 `data_rows = rows[1:]`；第 653～655 行校验表头是否等于 `CSV_FIELDNAMES`；第 723～724 行校验 `np.genfromtxt` 读回的列名是否一致。M6 的表头注释与检查同款（`src\external_oscillation_tracker.py` 第 86、434～435 行）。
- **源码位置**：`src\video_tracker.py` 第 40～41、479、650～651、653～655、723～724 行；`src\external_oscillation_tracker.py` 第 86、434～435 行。

### 4. Cell

- **中文名称**：单元格
- **英文名称**：Cell
- **初学者解释**：行与列交叉处的一个值；CSV 里所有 cell 都是文本，类型由写入格式与读取约定决定。
- **VisionMotion 中的具体作用**：成功行的每个 cell 由第 396～403 行给出（`frame` 整数、`time_s` / 坐标 / 面积格式化字符串、`detected` 写 `"True"`）；失败行第 404 行的三个测量 cell 是空字符串 `""`；第 665 行检查每行 cell 数是否等于 6；第 686～707 行逐格检查数值与留空规则。空 cell 表示"没测到"，不是 0。
- **源码位置**：`src\video_tracker.py` 第 395～404、665、686～707 行。

### 5. CSV_FIELDNAMES

- **中文名称**：CSV 字段名列表（表头与列顺序的唯一来源）
- **英文名称**：CSV_FIELDNAMES
- **初学者解释**：一个字符串列表，按顺序列出 CSV 每一列的名字；写表头、写数据行、读回校验都以它为准。
- **VisionMotion 中的具体作用**：第 41 行定义为 `["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`；被四处依赖：写表头（第 479 行）、cell 数校验（第 665 行）、表头校验（第 653～655 行）、列名校验（第 723～724 行）。同时，第 396～404 行返回的 6 个值必须与它的顺序一一对应。M6 也有同类常量，但字段不同（`src\external_oscillation_tracker.py` 第 87～96 行，8 列）。
- **源码位置**：`src\video_tracker.py` 第 40～41、479、653～655、665、723～724 行；`src\external_oscillation_tracker.py` 第 86～96 行。

### 6. build_csv_row

- **中文名称**：构造一行 CSV 数据（函数）
- **英文名称**：build_csv_row
- **初学者解释**：把"一帧的检测结果"翻译成"CSV 的一行"的函数；输出是 6 个 cell 组成的列表。
- **VisionMotion 中的具体作用**：第 387 行定义 `build_csv_row(frame_index, time_s, result)`；成功行在第 396～403 行（`"%.6f"` 时间、`"%.2f"` 坐标、`"%.1f"` 面积、`"True"`），失败行在第 404 行 `[frame_index, "%.6f" % time_s, "", "", "", "False"]`；第 491 行在逐帧循环里调用它写入每一帧。
- **源码位置**：`src\video_tracker.py` 第 387～404、491 行。

### 7. writerow

- **中文名称**：写入一行（csv writer 的方法）
- **英文名称**：writerow
- **初学者解释**：csv 写入器的方法，把"一串值"写成文件里的一行（自动补逗号与行尾），一次调用写一行。
- **VisionMotion 中的具体作用**：第 478 行创建 `csv.writer(csv_file, lineterminator="\n")`；第 479 行 `writerow(CSV_FIELDNAMES)` 写表头；第 491 行 `writerow(build_csv_row(...))` 写数据行。M6 用 `csv.DictWriter` 的 `writerow` 写字典行（`src\external_oscillation_tracker.py` 第 348、352、365 行），写法不同、每帧一行相同。
- **源码位置**：`src\video_tracker.py` 第 478～479、491 行；`src\external_oscillation_tracker.py` 第 348、352、365 行。

### 8. lineterminator

- **中文名称**：行尾字符（csv 写入参数）
- **英文名称**：lineterminator
- **初学者解释**：指定 CSV 每一行结尾用什么字符；本项目统一用 `"\n"`（LF），保证不同平台写出的文件行尾一致。
- **VisionMotion 中的具体作用**：第 478 行 `csv.writer(..., lineterminator="\n")`；M6 第 348 行同样设置，并在第 347 行注释"行尾使用 `\n`，与 results/ 下已有 CSV 保持一致（不写入 CRLF）"。配合第 477 行的 `newline=""`（避免文本模式换行转换叠加出空行），两份 CSV 的行结构保持统一。
- **源码位置**：`src\video_tracker.py` 第 477～478 行；`src\external_oscillation_tracker.py` 第 346～348 行。

### 9. records

- **中文名称**：逐帧记录列表（运行内台账）
- **英文名称**：records
- **初学者解释**：内存里的一个列表，每帧追加一条字典记录；只在程序运行期间存在，程序退出就消失。
- **VisionMotion 中的具体作用**：第 470 行创建（注释"每帧一条记录，用于统计与自检"）；第 493～497 行每帧建 `{frame, time_s, success}`；成功帧再补 `cx` / `cy` / `area`（第 498～501 行）并累计 `detected_count` / `area_list`（第 502～503 行）；第 504 行 `records.append(record)`。它被 `summary` 统计（第 556～580 行）、`compute_longest_miss_run()`（第 585～598 行）与 PNG 回退选帧（第 260～286、310～334、544～549 行）使用。与 CSV 的区别：不落盘、键名是 `success`（第 496 行）、失败帧没有坐标键。
- **源码位置**：`src\video_tracker.py` 第 470、493～504、556～580、585～598 行。

### 10. Missing Value

- **中文名称**：缺失值
- **英文名称**：Missing Value
- **初学者解释**：应该有一次测量、但实际没有测到的位置；缺失要显式表达"没有"，而不是填入一个假数字。
- **VisionMotion 中的具体作用**：失败帧的 `x_px` / `y_px` / `area_px` 写成空 cell、同时 `detected=False`（第 393、404 行）；读取端 `np.genfromtxt` 把空 cell 读成 NaN（第 721～731 行），自检要求 NaN 行数 = `detected=False` 行数（第 729～731 行）。第 393 行明确"失败时绝不写 0 / -1 / nan / 字符串"——0 与 -1 是合法数值，会污染后续统计；上一帧坐标则是伪造测量。
- **源码位置**：`src\video_tracker.py` 第 393、404、705～707、713、721～731 行。

### 11. Discrete Time Series

- **中文名称**：离散时间序列
- **英文名称**：Discrete Time Series
- **初学者解释**：按时间顺序排列的一系列测量值，只在离散时刻采样；采样间隔 = 1/fps。L01 已学"时间序列"概念，本条目补充 L06 的记录视角。
- **VisionMotion 中的具体作用**：CSV 每帧一行（第 491 行）、`frame` 从 0 到 N-1 连续（第 675～677 行）、`time_s = frame_index / fps` 提供时间轴（第 488、398、404 行）、失败行占位保证时间轴不缺格。`x_px(t)` / `y_px(t)` 等信号就是按行顺序读同一列得到的离散序列；后续位移 / 周期 / 频率分析都以它为输入（本课只记录，不分析）。
- **源码位置**：`src\video_tracker.py` 第 488、491、653～677 行。

### 12. Field Design

- **中文名称**：字段设计
- **英文名称**：Field Design
- **初学者解释**：为一份数据表决定"有哪些列、叫什么名字、什么顺序、什么格式、缺失怎么写、读回来怎么解释"；不只是"起名字"。
- **VisionMotion 中的具体作用**：第 40～41 行（表头定义与"不加 metadata"）、第 395～404 行（每个 cell 的格式）、第 653～655、665、723～724 行（自检）共同构成 M3 的字段设计。M3 的 6 列与 M6 的 8 列（`src\video_tracker.py` 第 41 行 vs `src\external_oscillation_tracker.py` 第 87～96 行）说明"字段跟着这份数据要回答的问题走"，但共同底线是表头、时间轴、失败留空 + False。
- **源码位置**：`src\video_tracker.py` 第 40～41、395～404、653～665、723～724 行；`src\external_oscillation_tracker.py` 第 87～96 行。

### 13. np.genfromtxt

- **中文名称**：NumPy 文本读取函数
- **英文名称**：np.genfromtxt
- **初学者解释**：NumPy 提供的"从文本文件读表格"的函数；`names=True` 表示第一行当作列名，空字段会被读成 NaN。
- **VisionMotion 中的具体作用**：`check_csv_data()` 第 721 行用它做"独立读取验证"：列名必须与 `CSV_FIELDNAMES` 一致（第 723～724 行）；`x_px` 的 NaN 数量必须等于 `detected=False` 的行数（第 725～731 行）——证明"失败留空"在下游读取时仍然是"缺失"，不是被丢弃、也不是被当成 0。
- **源码位置**：`src\video_tracker.py` 第 717～743 行（第 721 行调用）。

### 14. csv.DictWriter

- **中文名称**：按字典写行的 CSV 写入器
- **英文名称**：csv.DictWriter
- **初学者解释**：csv 模块里按"字典 + fieldnames"写行的写入器，能一次性写出表头；字段留空时写空字符串。
- **VisionMotion 中的具体作用**：M6 的 `write_trajectory_csv()` 用它在第 348 行创建（`fieldnames=CSV_FIELDNAMES`、`lineterminator="\n"`）、第 349 行 `writeheader()` 写表头、第 352、365 行写成功 / 失败字典行；与 M3 的 `csv.writer` + 列表（第 478、491 行）形成对照——两种写法保证同样的"表头 + 每帧一行 + 失败留空"。
- **源码位置**：`src\external_oscillation_tracker.py` 第 337～377 行（第 348、349、352、365 行）；对照 `src\video_tracker.py` 第 478、491 行。

### 15. y_px

- **中文名称**：质心竖直像素坐标
- **英文名称**：y_px
- **初学者解释**：目标质心的竖直坐标（图像坐标 y 越往下数值越大）；它是 M3 `_track.csv` 的列名，不要与 M6 的 `y0_px` 混用。
- **VisionMotion 中的具体作用**：M3 `_track.csv` 的第 4 列（`src\video_tracker.py` 第 41 行）；第 400 行写入 `result["cy"]`（`"%.2f"` 格式），失败时留空（第 404 行）。`cy` 来自 L04 的质心公式 `cy = m01 / m00`（`src\marker_detector.py` 第 101 行）。M6 不使用 `y_px`：它的正式位置特征是 `y0_px = 暗带上缘`（`src\external_oscillation_tracker.py` 第 84、92、306 行）——两者不是同一种测量。
- **源码位置**：`src\video_tracker.py` 第 41、400、404 行；`src\marker_detector.py` 第 101 行；`src\external_oscillation_tracker.py` 第 84、92 行。

### 16. _track.csv / _trajectory.csv

- **中文名称**：M3 / M6 两种逐帧数据文件（字段设计对照）
- **英文名称**：track.csv / trajectory.csv
- **初学者解释**：两份"每帧一行"的测量文件；共同点是第一行表头、`frame` + `time_s` 时间轴、`detected` 标志、失败留空，字段则各自按任务设计。
- **VisionMotion 中的具体作用**：M3 由 `demo\run_video_tracking.py` 第 37 行命名为 `results\EXP-002-VIDEO-001_track.csv`，表头 6 列 `frame,time_s,x_px,y_px,area_px,detected`（`src\video_tracker.py` 第 41 行）；M6 由 `demo\run_m62_external_tracking.py` 第 54 行命名为 `results\EXP-EXT-LAB67-V1_trajectory.csv`，表头 8 列 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`（`src\external_oscillation_tracker.py` 第 87～96 行）。共有 `frame / time_s / detected / x_px / area_px`；M3 独有 `y_px`；M6 独有 `y0_px / bbox_w_px / bbox_h_px`；`detected` 的位置由第 6 列变为第 3 列——读数据要按表头取列，不要背固定列号。
- **源码位置**：`src\video_tracker.py` 第 41 行；`src\external_oscillation_tracker.py` 第 87～96 行；`demo\run_video_tracking.py` 第 37 行；`demo\run_m62_external_tracking.py` 第 54 行。

### 17. Frame（补充视角）

- **基础词条**：见 L01 同名条目与 L05 "Frame" 补充条目；本条目补充 L06 的"数据记录"视角。
- **中文名称**：帧（补充：一帧 = CSV 里的一行记录）
- **英文名称**：Frame
- **初学者解释**：帧是视频里的一张图像；在 L06 里，每一帧还对应 CSV 里的一行测量记录——帧既是"一张图"，也是一个"采样时刻"。
- **VisionMotion 中的具体作用**：逐帧循环里，第 474 / 526 行的 `current_frame` 是图像数据，第 475 / 525 行的 `frame_index` 是帧编号；第 491 行把这一帧写成 CSV 的一行，第 493～504 行把它追加进 `records`。检测失败的帧同样占一行（第 404 行），所以"帧 ↔ CSV 行"在 M3 里是一一对应的（自检第 657～659 行核对行数、第 675～677 行核对 frame 连续）。
- **源码位置**：`src\video_tracker.py` 第 475、483、491、493～504、521～526、657～659、675～677 行。

### 18. time_s（补充视角）

- **基础词条**：见 L01 同名条目与 L05 "FPS" 补充条目；本条目补充 L06 的写入格式与时间轴视角。
- **中文名称**：时间（秒）（补充：CSV 的时间轴列）
- **英文名称**：time_s
- **初学者解释**：`time_s` 是每一帧在视频时间轴上的时刻，由帧号除以 fps 得到；在 CSV 里它是第二列，提供整张表的"横轴"。
- **VisionMotion 中的具体作用**：第 488 行 `time_s = frame_index / fps`；第 398 / 404 行用 `"%.6f"` 写 6 位小数；`fps` 由第 124 行从视频文件读取（M3 视频由已有 CSV 反推 ≈ 60.12 fps，M6 为 30 fps——两个数字不同，说明不能硬编码）。失败行也照写 `time_s`（第 404 行），时间轴因此不断裂；M6 自检还要求每行 `time_s` 满足 `frame / fps`（`src\external_oscillation_tracker.py` 第 494～500 行）。
- **源码位置**：`src\video_tracker.py` 第 124、398、404、488、495 行；`src\external_oscillation_tracker.py` 第 302～303、494～500 行。

### 19. x_px（补充视角）

- **基础词条**：见 L01 同名条目；本条目补充 M3 的字段设计，并提醒"同名不同义"。
- **中文名称**：水平像素坐标（补充）
- **英文名称**：x_px
- **初学者解释**：`x_px` 表示目标中心的水平像素坐标；但"目标中心"具体指什么，各模块可能不同——必须看写它的代码。
- **VisionMotion 中的具体作用**：M3 的 `x_px` 是红色标记**质心**的横坐标：第 399 行写 `"%.2f" % result["cx"]`，`cx` 来自 `src\marker_detector.py` 第 145 行（公式 `cx = m10 / m00` 在第 100 行）；失败时留空（第 404 行）。M6 的 `x_px` 则是暗带外接框中心、仅作 QC 记录（`src\external_oscillation_tracker.py` 第 220～221 行）——同名不同义，读数据前先确认来源。
- **源码位置**：`src\video_tracker.py` 第 399、404 行；`src\marker_detector.py` 第 100、145 行；`src\external_oscillation_tracker.py` 第 220～221 行。

### 20. area_px（补充视角）

- **基础词条**：见 L01 同名条目；本条目补充 M3 的轮廓面积视角。
- **中文名称**：目标面积（像素²）（补充）
- **英文名称**：area_px
- **初学者解释**：`area_px` 记录目标区域的面积，单位是"像素²"；它是检测质量指标，不是"目标移动了多少"的测量量。
- **VisionMotion 中的具体作用**：第 401 行写 `"%.1f" % result["area"]`，`area` 来自 `src\marker_detector.py` 第 140 行 `cv2.contourArea(contour)`（第 147 行返回）；失败时留空（第 404 行）。M6 的同名列写整数（`src\external_oscillation_tracker.py` 第 361 行），但同样是"检测区域大小"的质量线索。
- **源码位置**：`src\video_tracker.py` 第 401、404 行；`src\marker_detector.py` 第 140、147 行；`src\external_oscillation_tracker.py` 第 361 行。

### 21. detected（补充视角）

- **基础词条**：见 L01 同名条目；本条目补充源码中的写法与读取方式。
- **中文名称**：检测成功标志（补充）
- **英文名称**：detected
- **初学者解释**：`detected` 表示"这一帧的测量是否有效"；CSV 里写的是文本 `True` / `False`，不是数字 1 / 0。
- **VisionMotion 中的具体作用**：来自 `result["success"]`（第 395 行在 `build_csv_row()` 里判断；第 402 / 404 行写成 `"True"` / `"False"`；`src\marker_detector.py` 第 144 行成功、第 133 / 137 行失败）。内存 `records` 里的键叫 `success`（第 496 行）而不是 `detected`。读取端：自检按字符串比较（第 689、705 行），`np.genfromtxt` 读成布尔后统计成功行数（第 726～728 行）。M6 的写法相同（`src\external_oscillation_tracker.py` 第 304、356、369 行）。
- **源码位置**：`src\video_tracker.py` 第 41、395、402、404、496、689、705、726～728 行；`src\marker_detector.py` 第 133、137、144 行；`src\external_oscillation_tracker.py` 第 304、356、369 行。

### 22. CSV（补充视角）

- **基础词条**：见 L01 同名条目；本条目补充 L06 在项目内的具体设计。
- **中文名称**：逗号分隔值（补充：项目内约定）
- **英文名称**：CSV
- **初学者解释**：L01 已解释 CSV 是纯文本表格；L06 补上"这份项目的 CSV 具体长什么样"：第一行真表头、每帧一行、失败留空 + False。
- **VisionMotion 中的具体作用**：第 40 行注释"第一行就是真正的表头，前面不加任何 metadata"；第 477～479 行用 UTF-8、`newline=""`、`lineterminator="\n"` 打开文件并写表头（第 26 行 `import csv`）；第 491 行每帧写一行（失败也写）；第 404 行失败行三个测量字段留空、`detected=False`。读取端用标准库 `csv.reader`（第 646～648 行）与 `np.genfromtxt`（第 721～743 行）都能直接读取，并由 `check_csv_data()`（第 637～748 行）逐项验收。
- **源码位置**：`src\video_tracker.py` 第 26、40、404、477～479、491、646～648、721～743 行。

---

## L07 检测失败、质量检查与鲁棒性

### 1. Detection Failure（检测失败）

- **中文名称**：检测失败
- **英文名称**：Detection Failure
- **初学者解释**：检测失败表示"这一帧没有测到可用的目标"，它是程序正常返回的一种结果，不是程序崩溃或报错。
- **VisionMotion 中的具体作用**：`src\marker_detector.py` 的三道判定任一触发即为检测失败：没有轮廓（第 75～76 行）、最大轮廓面积 < `MIN_AREA = 200`（第 33、83～84 行）、`m00 == 0` 无法算质心（第 97～98 行）；`detect_marker()` 统一返回 `{"success": False, "mask": mask}`（第 132～133、136～137 行）；下游把它翻译成 CSV 失败行 `detected=False` + 空字段（`src\video_tracker.py` 第 393、404 行）。整个逐帧循环不会因此停止（第 483～526 行）。
- **源码位置**：`src\marker_detector.py` 第 33、75～76、83～84、97～98、132～133、136～137 行；`src\video_tracker.py` 第 393、404、483～526 行。

### 2. success（成功标志，内存字段）

- **中文名称**：成功标志（补充视角）
- **英文名称**：success
- **初学者解释**：`success` 是 `detect_marker()` 返回字典里的布尔字段（成功 `True` / 失败 `False`），是调用方判断"这一帧有没有测量值"的唯一判据；CSV 文件里对应的列名是 `detected`。
- **VisionMotion 中的具体作用**：成功时 `success=True`（第 144 行）；失败时 `success=False`（第 133、137 行）；`build_csv_row()` 第 395 行 `if result["success"]:` 决定写成功行还是失败行；`records` 里存的是 `"success": bool(result["success"])`（`src\video_tracker.py` 第 496 行），而 CSV 里写文本 `"True"` / `"False"`（第 402、404 行）；`compute_longest_miss_run()` 读 `record["success"]`（第 592 行）。
- **源码位置**：`src\marker_detector.py` 第 133、137、144 行；`src\video_tracker.py` 第 395、402、404、496、592 行。

### 3. DETECTION FAILED（失败提示文字）

- **中文名称**：检测失败提示文字
- **英文名称**：DETECTION FAILED
- **初学者解释**：叠加视频里失败帧左上角显示的红色英文文字，意思是"这一帧没有检测到目标"；出现它时画面上不会再有绿框和中心点。
- **VisionMotion 中的具体作用**：`draw_tracking_frame()` 第 190～201 行：`if not result["success"]:` 后用红色 `(0, 0, 255)` 在 (10, 70) 写 "DETECTION FAILED"，随后 `return overlay`（第 201 行），成功分支的绿框 / 圆圈 / 十字 / 坐标文字（第 204～231 行）不会执行。它与 CSV 第 404 行"不伪造缺失"是同一条原则的两种呈现。
- **源码位置**：`src\video_tracker.py` 第 169～233 行（失败显示第 190～201 行）。

### 4. 失败返回结构（Failure Return Structure）

- **中文名称**：失败返回结构
- **英文名称**：Failure Return Structure
- **初学者解释**：检测失败时 `detect_marker()` 返回的字典只含两个键：`success`（False）与 `mask`；`cx` / `cy` / `area` / `bbox` / `contour` 这些测量键**不存在**——因为没有测到，就没有这些值。
- **VisionMotion 中的具体作用**：`return {"success": False, "mask": mask}`（第 132～133、136～137 行）；这些键只在成功分支（第 143～151 行）写入。使用侧的配套约定：`build_csv_row()` 只在成功分支取键（`src\video_tracker.py` 第 395～403 行）；`draw_tracking_frame()` 失败时提前返回（第 190～201 行）——所以"缺键"不会引发 `KeyError`。`mask` 保留是因为它与第 129 行同一次计算，可作为诊断用的中间结果。
- **源码位置**：`src\marker_detector.py` 第 129、132～133、136～137、143～151 行；`src\video_tracker.py` 第 190～201、395～404 行。

### 5. 空字段（Empty Field）

- **中文名称**：空字段（补充视角）
- **英文名称**：Empty Field
- **初学者解释**：CSV 失败行里 x / y / area 三列不是 0、不是 -1、不是 nan 文本，而是"什么都没有"——两个逗号之间是空的。
- **VisionMotion 中的具体作用**：`build_csv_row()` 第 404 行返回 `[frame_index, "%.6f" % time_s, "", "", "", "False"]`；第 393 行原则"失败时绝不写 0 / -1 / nan / 字符串"。读取端：`csv.reader` 读回空字符串，`np.genfromtxt` 把空字段读成 NaN（第 725～735 行据此对账）。自检第 712 行要求 `detected=False` 的行 x / y / area 全部为空。
- **源码位置**：`src\video_tracker.py` 第 393、404、705～707、712、725～735 行。

### 6. (0,0) 伪数据

- **中文名称**：(0,0) 伪数据
- **英文名称**：Zero-Zero Fake Data
- **初学者解释**：`x=0 且 y=0` 的"成功行"高度可疑：图像原点在左上角，真实目标恰好落在精确 (0,0) 的概率极低；它常见于"没算出来却写了默认值 0"的情况。
- **VisionMotion 中的具体作用**：`check_csv_data()` 第 701～702 行收集 `x == 0.0 且 y == 0.0` 的行，第 713 行把它作为独立检查项"不存在 x=0, y=0 伪数据"。它是第 393 行"失败绝不写 0"的机器验收。
- **源码位置**：`src\video_tracker.py` 第 393、701～702、713 行。

### 7. detection_rate（检出成功率）

- **中文名称**：检出成功率
- **英文名称**：detection rate
- **初学者解释**：成功帧数占实际处理帧数的比例，0～1 之间；`1.0` 表示每一帧都检测成功。
- **VisionMotion 中的具体作用**：`summary` 第 567 行 `detected_count / float(len(records))`；`print_statistics()` 第 619 行以 `%.4f%%` 打印。它只回答"有多少帧测到了"，不反映失败的分布（另见 `longest_miss_run`），也不校验数值是否合理（另见 `check_csv_data()`）。本课只读核对：两份真实 CSV 均为 1.0000。
- **源码位置**：`src\video_tracker.py` 第 564～567、619 行。

### 8. longest_miss_run（最长连续丢失帧数）

- **中文名称**：最长连续丢失帧数
- **英文名称**：longest miss run
- **初学者解释**：一整段数据里"连续多少帧一直没测到目标"的最大值；它衡量的是空白的**长度**，不是空白的**数量**。
- **VisionMotion 中的具体作用**：`compute_longest_miss_run()`（第 585～598 行）遍历 `records`：成功把当前连续计数清零，失败累加并刷新历史最大值（第 592～597 行）；返回 0 当且仅当整段没有失败帧。`summary` 第 568 行调用，`print_statistics()` 第 621 行打印"最长连续丢失帧"。
- **源码位置**：`src\video_tracker.py` 第 568、585～598、621 行。

### 9. Quality Check（质量检查）

- **中文名称**：质量检查
- **英文名称**：Quality Check / QC
- **初学者解释**：对"写出来的数据文件"做体检：格式对不对、行数对不对、失败有没有被诚实标记、数值有没有明显不合理；只读，不修改数据。
- **VisionMotion 中的具体作用**：M3 的 `check_csv_data()`（`src\video_tracker.py` 第 637～748 行）重新打开 CSV 做九项检查（表头、行数、frame 合法与连续、成功行数值、失败行留空、无 (0,0)、坐标范围、`np.genfromtxt` 读取与 NaN ↔ False 对账），第 747 行九项全过才算通过；M6 的 `check_trajectory_csv()`（`src\external_oscillation_tracker.py` 第 422～505 行）以更严的"分析型"门槛检查（100% 检出、无空值、无突跳、无歧义、时间严格）。
- **源码位置**：`src\video_tracker.py` 第 637～748 行；`src\external_oscillation_tracker.py` 第 422～505 行。

### 10. Robustness（鲁棒性）

- **中文名称**：鲁棒性
- **英文名称**：Robustness
- **初学者解释**：系统在"测不到 / 情况变差"时的表现是否仍然可靠：不崩溃、不编造数据、不弄乱时间轴、不被一帧坏数据拖垮，并且能把问题显示出来让人知道。
- **VisionMotion 中的具体作用**：五条落点——失败是返回值不是异常（`src\marker_detector.py` 第 132～133、136～137 行）；失败不写伪数据（`src\video_tracker.py` 第 393、404 行）；失败帧照写 frame / time_s（第 490～491 行）；循环不因单帧失败退出（第 483～526 行，唯一 `break` 第 522～524 行）；失败被显示与统计（第 190～201、564～568、637～748 行）。因此"鲁棒 ≠ 检出率 100%"。
- **源码位置**：`src\marker_detector.py` 第 132～133、136～137 行；`src\video_tracker.py` 第 190～201、393、404、483～526、564～568、637～748 行。

### 11. Evidence Boundary（证据边界）

- **中文名称**：证据边界
- **英文名称**：Evidence Boundary
- **初学者解释**：一条结论"最多能被什么证据支持到哪一步"；写学习记录 / 实验报告时先说清证据，再下结论，不用"设计上支持"冒充"实测已发生"。
- **VisionMotion 中的具体作用**：本课的三类证据——源码（失败处理的设计，可给行号）、真实 CSV（两份文件 100% 检出、0 失败帧，只读统计）、实验（没有触发过失败，故不能声称"实测验证过失败恢复"）。结论表述纪律：只读核对、标注来源类型、数字可复核、不越界表述。
- **源码位置**：无（概念词条）；对应事实见 `docs\learning\L07_检测失败与鲁棒性.md` 第 15、16 节与 `results\EXP-002-VIDEO-001_track.csv`、`results\EXP-EXT-LAB67-V1_trajectory.csv` 的只读统计。

---

## L08 为什么像素不能直接当毫米（像素与毫米标定）

### 1. Calibration（标定）

- **中文名称**：标定（像素尺度标定）
- **英文名称**：Calibration
- **初学者解释**：用"画面上的两个像素点 + 一个已知现实长度"求出"像素"与"毫米"之间的比例；标定回答的是"在这段视频里，1 mm 占多少像素"，不是相机的通用参数。
- **VisionMotion 中的具体作用**：由 `src\calibration.py` 的 `compute_scale()`（第 100～144 行）实现：输入 `point1` / `point2` / `real_distance_mm`，输出 `pixel_distance` / `px_per_mm` / `mm_per_px`；`real_distance_mm <= 0` 报错（第 125～126 行）、两点重合报错（第 134～135 行）。本项目做的是像素尺度标定，明确**不做相机内参 / 外参标定与畸变校正**（`src\displacement.py` 第 23 行"不做相机标定"）。标定结果冻结为常量：M4（`src\displacement.py` 第 41～55 行）、M5（`src\dynamic_displacement.py` 第 59～66 行）。
- **源码位置**：`src\calibration.py` 第 100～144 行；`src\displacement.py` 第 23、41～55 行；`src\dynamic_displacement.py` 第 59～66 行。

### 2. 图像坐标系 / 物理世界坐标系（补充视角）

- **基础词条**：图像坐标系见 L01 同名条目；本条目补充"两套坐标系为什么必须区分"。
- **中文名称**：图像坐标系 / 物理世界坐标系
- **英文名称**：image coordinate system / physical world coordinate system
- **初学者解释**：图像坐标系描述"在画面里的位置"，单位是像素，原点在画面左上角，x 向右增大、y 向下增大；物理世界坐标系描述"在现实中多远"，单位是毫米，方向由测量约定（本项目沿尺子刻线方向）。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 9～10 行给出图像坐标系约定（"点写作 (x, y)，单位是像素；原点在画面左上角，x 向右增大，y 向下增大"）；第 12～19 行把两套坐标系的桥写成公式：`L_pixel`（像素距离）、`L_real_mm`（真实距离）、`k = L_pixel / L_real_mm`、`1 / k`、单位方向 `u`。项目里以 `_px` 结尾的字段属于图像坐标系（`x_px`、`y_px`、`s_px`、`ds_px`），以 `_mm` 结尾的字段属于物理世界坐标系（`ds_mm`）。
- **源码位置**：`src\calibration.py` 第 9～19 行；`src\displacement.py` 第 44～46、72～81 行。

### 3. px/mm（像素尺度 k）

- **中文名称**：每毫米像素数（像素尺度 k）
- **英文名称**：pixels per millimeter
- **初学者解释**：1 毫米现实长度在画面里占多少个像素；数值越大，说明这段现实长度在画面里占的像素越多。它由"这一次拍摄"的几何条件决定，不是像素的固有属性。
- **VisionMotion 中的具体作用**：`compute_scale()` 第 137 行计算 `px_per_mm = pixel_distance / real_distance_mm`，第 142 行随字典返回；冻结常量：M4 `PX_PER_MM = 5.756961`（`src\displacement.py` 第 52 行）、M5 `PX_PER_MM_004 = 6.086399`（`src\dynamic_displacement.py` 第 64 行）。它是位移换算的主表达方式：`ds_mm = ds_px / PX_PER_MM`（`src\displacement.py` 第 340 行）。
- **源码位置**：`src\calibration.py` 第 137、142 行；`src\displacement.py` 第 52、340 行；`src\dynamic_displacement.py` 第 64、350 行。

### 4. mm/px（每像素毫米数）

- **中文名称**：每像素毫米数
- **英文名称**：millimeters per pixel
- **初学者解释**：1 个像素代表多少毫米现实长度；它与 `px/mm` 互为倒数：`mm/px = 1 / (px/mm)`。数值越大，说明单个像素代表的现实长度越大。
- **VisionMotion 中的具体作用**：`compute_scale()` 第 138 行计算 `mm_per_px = real_distance_mm / pixel_distance`，第 143 行随字典返回；冻结常量：M4 `MM_PER_PX = 0.173703`（`src\displacement.py` 第 53 行，注释写明"只用于自检与报告"）、M5 `MM_PER_PX_004 = 0.164301`（`src\dynamic_displacement.py` 第 65 行）。自检要求两者互为倒数：`src\displacement.py` 第 142～147 行（容差 1e-4）、`src\dynamic_displacement.py` 第 159～165 行（容差 1e-6）。
- **源码位置**：`src\calibration.py` 第 138、143 行；`src\displacement.py` 第 53、142～147 行；`src\dynamic_displacement.py` 第 65、159～165 行。

### 5. pixel_distance（像素距离 L_pixel）

- **中文名称**：像素距离
- **英文名称**：pixel_distance / L_pixel
- **初学者解释**：两个像素点之间的直线距离，单位是像素；它是"画面上的长度"，还不是现实长度。
- **VisionMotion 中的具体作用**：`compute_scale()` 第 128～131 行计算：`dx = x2 - x1`、`dy = y2 - y1`、`pixel_distance = math.hypot(dx, dy)`；第 141 行随字典返回。用 M4 冻结标定点只读复算：`hypot(345.41, -2.38) ≈ 345.418199 px`。它必须与已知真实长度相除才能得到尺度。
- **源码位置**：`src\calibration.py` 第 128～131、141 行。

### 6. compute_scale（像素尺度计算函数）

- **中文名称**：像素尺度计算函数
- **英文名称**：compute_scale
- **初学者解释**：标定模块的主函数：给它两个像素点和一个已知真实距离，它返回像素距离、每毫米像素数、每像素毫米数三个结果。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 100～144 行。参数（第 104～107 行）：`point1`（P1 像素坐标）、`point2`（P2 像素坐标）、`real_distance_mm`（真实距离，毫米）；返回（第 140～144 行）`pixel_distance` / `px_per_mm` / `mm_per_px`；报错约定（第 114～116 行）：类型错误 `TypeError`，点长度 / 重合 / 真实距离 ≤ 0 为 `ValueError`。`src\displacement.py` 第 111～112 行在冻结常量自检里调用它（只读复算，不重新标定）。
- **源码位置**：`src\calibration.py` 第 100～144 行；调用见 `src\displacement.py` 第 111 行。

### 7. 已知真实长度（real_distance_mm）

- **中文名称**：已知真实长度
- **英文名称**：known real distance / real_distance_mm
- **初学者解释**：现实里用尺子（或已知刻度）量出来的一段长度，单位毫米；它是标定的第二块拼图——没有它，"每像素多少毫米"无法确定。
- **VisionMotion 中的具体作用**：M4 用 10 cm → 16 cm 刻线的真实距离 `CALIB_REAL_DISTANCE_MM = 60.0`（`src\displacement.py` 第 46、50 行）；M5 用 10 cm → 20 cm 刻线的真实距离 `CALIB_REAL_DISTANCE_MM = 100.0`（`src\dynamic_displacement.py` 第 62 行）。`compute_scale()` 第 125～126 行把"真实距离必须大于 0"写成硬性检查；第 122～123 行拒绝 nan / inf。
- **源码位置**：`src\calibration.py` 第 122～126 行；`src\displacement.py` 第 46、50 行；`src\dynamic_displacement.py` 第 62 行。

### 8. M4 冻结标定常量（PX_PER_MM / MM_PER_PX）

- **中文名称**：M4 冻结标定常量
- **英文名称**：PX_PER_MM / MM_PER_PX
- **初学者解释**：EXP-003 静态实验（M4）正式冻结的像素尺度：`PX_PER_MM = 5.756961`、`MM_PER_PX = 0.173703`；常量一旦冻结就不再重算。
- **VisionMotion 中的具体作用**：标定来源为 EXP-003-STATIC-002.mp4 第 900 帧、`CAP_PROP_ORIENTATION_AUTO=1` 之后的 1920×1080 坐标系；P1 = 10 cm 刻线 (1036.23, 490.58)，P2 = 16 cm 刻线 (1381.64, 488.20)，真实距离 60.0 mm，方向约定 10 cm → 16 cm（`src\displacement.py` 第 42～46 行）；`U = (0.999976, -0.006894)`（第 55 行）。三个静态实验共用这一套常量（`demo\run_m43_displacement.py` 第 63～67、146～158 行）；自检（第 98～150 行）只用来发现手抄错误，不做重新标定（第 47 行）。
- **源码位置**：`src\displacement.py` 第 41～55、98～150 行；调用见 `demo\run_m43_displacement.py` 第 63～67、215～222 行。

### 9. M5 冻结标定常量（PX_PER_MM_004 / MM_PER_PX_004）

- **中文名称**：M5（EXP-004 专属）冻结标定常量
- **英文名称**：PX_PER_MM_004 / MM_PER_PX_004
- **初学者解释**：EXP-004 动态实验（M5）专属的像素尺度：`PX_PER_MM_004 = 6.086399`、`MM_PER_PX_004 = 0.164301`；命名里的 `_004` 表示"只对 EXP-004 有效"。
- **VisionMotion 中的具体作用**：标定来源为 M5.2-1 人工点击 + 独立核验（`src\dynamic_displacement.py` 第 59 行，写明"已冻结，不得重新标定"）；P1 = 10 cm 刻线 (813.50, 296.49)，P2 = 20 cm 刻线 (1422.13, 294.11)，真实距离 100.0 mm（第 60～62 行）；`U_004 = (0.999992, -0.003913)`（第 66 行）。第 20～23 行禁止把 M4 常量搬进来、禁止 `import src.displacement`；第 68～76 行专属 valid gate 写明"与 M4 gate 完全不同，不得混用"；自检第 121～174 行。
- **源码位置**：`src\dynamic_displacement.py` 第 20～23、59～66、68～76、121～174 行。

### 10. unit_direction（单位方向向量函数）

- **中文名称**：单位方向向量函数
- **英文名称**：unit_direction
- **初学者解释**：算出"从 P1 指向 P2"的方向，只保留方向、不带长度：`u = (P2 - P1) / |P2 - P1|`；两点重合时报错。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 147～173 行；方向约定 10 cm → 16 cm（第 149 行）；返回字典 `{"ux", "uy"}`（第 173 行）；重合报 `ValueError`（第 170～171 行）。`src\displacement.py` 第 34 行导入它、第 112 行在冻结常量自检里用它与常量 `U` 比对（第 128～135 行）。L08 只登记"它是什么、输入输出是什么"；完整推导留 L09。
- **源码位置**：`src\calibration.py` 第 147～173 行；`src\displacement.py` 第 34、112、128～135 行。

### 11. project_point（一维投影函数）

- **中文名称**：一维投影函数
- **英文名称**：project_point
- **初学者解释**：把一个像素点投影到给定方向上，得到一个"沿这个方向走了多远"的一维坐标 `s`，单位仍是像素。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 176～204 行；公式 `s = x * ux + y * uy`（第 180 行说明、第 204 行实现）；方向可以传 `unit_direction()` 的字典或 `(ux, uy)` 序列（第 184～185 行）；零长度方向报错（第 196～198 行）。`src\displacement.py` 第 277～285 行用它把 `(x_px, y_px)` 变成 `s_px`（第 285 行），并声明"投影公式直接复用，本模块不重写公式"（第 281 行）。L08 只登记最小认识；归一化数学细节（第 196～202 行）与投影几何推导留 L09。
- **源码位置**：`src\calibration.py` 第 176～204 行；`src\displacement.py` 第 277～285 行；`src\dynamic_displacement.py` 第 40、147～150 行。

### 12. s_px（沿尺方向的一维投影坐标）

- **中文名称**：沿尺方向的一维投影坐标
- **英文名称**：s_px
- **初学者解释**：把二维的 `(x_px, y_px)` 投影到尺子方向上之后得到的一维位置（像素）；同一目标在尺方向上的位置变化就是"位移"的来源。
- **VisionMotion 中的具体作用**：ds CSV 的第 3 列（`src\displacement.py` 第 75 行、`src\dynamic_displacement.py` 第 94 行）；由 `add_projection()` 计算（`src\displacement.py` 第 277～285 行）；`s0` 取前 0.5 s（M4）/ 前 2.0 s（M5）有效帧 `s_px` 的平均值（`src\displacement.py` 第 288～325 行、`src\dynamic_displacement.py` 第 78～80 行）；`ds_px = s_px - s0`。
- **源码位置**：`src\displacement.py` 第 75、277～325、339 行；`src\dynamic_displacement.py` 第 94、349 行。

### 13. ds_px（相对位移，像素）

- **中文名称**：相对位移（像素）
- **英文名称**：ds_px
- **初学者解释**：相对起点基准 `s0` 的位移，单位像素：`ds_px = s_px - s0`；它回答"相对开始时动了多少像素"。
- **VisionMotion 中的具体作用**：ds CSV 的第 4 列（`src\displacement.py` 第 76 行、`src\dynamic_displacement.py` 第 95 行）；计算在第 339 / 349 行；写入格式 3 位小数（第 87 / 106 行）；`valid=False` 的行留空（`src\displacement.py` 第 355、361 行）。它是 `ds_mm` 的分子：`ds_mm = ds_px / PX_PER_MM`。
- **源码位置**：`src\displacement.py` 第 76、87、339、355、361 行；`src\dynamic_displacement.py` 第 95、106、349 行。

### 14. ds_mm（相对位移，毫米）

- **中文名称**：相对位移（毫米）
- **英文名称**：ds_mm
- **初学者解释**：`ds_px` 经过本实验标定换算后的毫米位移：`ds_mm = ds_px / PX_PER_MM`（等价于 `ds_px × MM_PER_PX`）。它是换算结果，不是"又测了一遍毫米"。
- **VisionMotion 中的具体作用**：ds CSV 的第 5 列（`src\displacement.py` 第 77 行、`src\dynamic_displacement.py` 第 96 行）；M4 用 `PX_PER_MM`（第 340 行），M5 用 `PX_PER_MM_004`（第 350 行）；写入格式 4 位小数（第 88 / 107 行）；公式自检容差 0.0005 mm（`src\displacement.py` 第 736～740 行、`src\dynamic_displacement.py` 第 1105～1113 行）。真实数据注意"双重舍入"：用文件里已舍入的 `ds_px` 反算可能出现 ±0.0001 的差。M6 外部视频没有 ds_mm 列（没有有效标定）。
- **源码位置**：`src\displacement.py` 第 77、88、340、736～740 行；`src\dynamic_displacement.py` 第 96、107、350、1105～1113 行。

### 15. 无标定原则（Calibration Boundary）

- **中文名称**：无标定原则（标定边界）
- **英文名称**：no-calibration ⇒ pixels only
- **初学者解释**：**没有有效标定，就只能停留在像素层面**——不写 `_mm` 字段、不给毫米结论、不把像素数字心算成现实长度。
- **VisionMotion 中的具体作用**：正例——M4 / M5 有冻结标定，所以 ds CSV 有 `ds_mm` 列；反例——M6 外部视频模块明文禁止标定与位移换算（`src\external_oscillation_tracker.py` 第 31～34 行），其正式轨迹只有 8 列像素字段（第 87～96 行），没有已知真实长度。配套纪律：不同实验的标定常量不跨实验搬运（`src\dynamic_displacement.py` 第 20～23、68～76 行）。
- **源码位置**：`src\external_oscillation_tracker.py` 第 31～34、87～96 行；`src\dynamic_displacement.py` 第 20～23、68～76 行。

### 16. y0_px 的字段名读法（补充视角）

- **基础词条**：见 L01 "y0_px" 与 L06 "y_px"；本条目补充"名字怎么读"与"什么名字不存在"。
- **中文名称**：暗带上缘竖直像素位置（字段名读法）
- **英文名称**：y0_px
- **初学者解释**：`y0_px` 是一个完整的字段名，其中的 `0` 是**字段名的一部分**，不是数值零，也不参与计算；项目里**不存在** `x0_px`。
- **VisionMotion 中的具体作用**：`y0_px` 在源码里以字符串形式出现在 M6 表头（`src\external_oscillation_tracker.py` 第 92 行）与位置特征名称中（第 84 行 `POSITION_FEATURE_NAME = "y0_px = 暗带上缘（M6.2-2B 冻结）"`）；不能把 `y0_px = 508` 读成"y=0、px=508"，也不能写成 `y_0px` / `y_0_px`。全项目（排除 `.venv`、`__pycache__`）搜索：`x0_px` 无命中；`x_px`、`y_px`、`s_px`、`ds_px`、`ds_mm`、`y0_px` 均有命中。M3 的 `y_px`（质心竖直坐标）与 M6 的 `y0_px`（暗带上缘）不是同一种测量。
- **源码位置**：`src\external_oscillation_tracker.py` 第 84、92 行；`src\video_tracker.py` 第 41 行（`y_px`）；`src\displacement.py` 第 75～77 行（`s_px` / `ds_px` / `ds_mm`）。

---

## L09 标定、方向向量与一维投影

### 1. 原始方向向量（v = P2 − P1）

- **中文名称**：原始方向向量
- **英文名称**：raw direction vector
- **初学者解释**：把两个点相减得到的向量 `v = P2 - P1 = (dx, dy)`；它同时携带"方向"和"长度"两个信息，长度就是两点之间的像素距离。
- **VisionMotion 中的具体作用**：`src\calibration.py` 的 `unit_direction()` 第 166～168 行先算 `dx = x2 - x1`、`dy = y2 - y1`、`length = math.hypot(dx, dy)`；这里的 `(dx, dy)` 就是原始方向向量，`length` 就是它的模，数值等于 `compute_scale()` 里的 `pixel_distance`。用冻结标定点只读复算：M4 的原始方向向量是 `(345.41, -2.38)`，M5 是 `(608.63, -2.38)`。它**不能直接拿去算 `s`**——必须先归一化。
- **源码位置**：`src\calibration.py` 第 166～168 行（`unit_direction()` 内部）。

### 2. 单位方向向量（u = v / 向量长度）

- **中文名称**：单位方向向量
- **英文名称**：unit direction vector
- **初学者解释**：把原始方向向量除以它自己的长度，得到一个长度为 1、只保留方向的向量：`u = v / 向量长度 = (dx / L, dy / L)`。长度被"归一"掉了，方向原样保留。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 173 行 `return {"ux": dx / length, "uy": dy / length}`；方向约定写在 docstring 第 149 行（10 cm → 16 cm）。项目里正式使用的两个方向常量是 M4 的 `U = (0.999976, -0.006894)`（`src\displacement.py` 第 55 行，方向 10 cm → 16 cm）与 M5 的 `U_004 = (0.999992, -0.003913)`（`src\dynamic_displacement.py` 第 66 行，方向 10 cm → 20 cm）。两者都必须与本实验的尺度常量绑定，不得混用（`src\dynamic_displacement.py` 第 20～23、68 行）。
- **源码位置**：`src\calibration.py` 第 147～173 行（第 166～168、170～171、173 行）；`src\displacement.py` 第 55 行；`src\dynamic_displacement.py` 第 66 行。

### 3. 归一化（normalization）

- **中文名称**：归一化
- **英文名称**：normalization
- **初学者解释**：把向量变成"长度为 1 的同方向向量"这一步操作。
- **VisionMotion 中的具体作用**：**为什么必须归一化**——三条理由：① 单位一致：只有长度为 1 时，`s = x·ux + y·uy` 的单位才和 `point` 一样是像素；② 表示唯一：同一个方向只有一种写法；③ 几何可读：`ux` / `uy` 才能读作 cos θ / sin θ。教学反例（非项目数据，见 `docs\learning\L09_标定方向向量与一维投影.md` 第 5.6 节）：若用 `u_raw = (2, 0)` 直接算，点 `(10, 0)` 会得到 `s = 20` 而不是 `10`——被方向向量的长度缩放了。项目里归一化出现两次：`unit_direction()` 第 173 行、`project_point()` 第 196～202 行（"再次归一化"）。
- **源码位置**：`src\calibration.py` 第 166～168、173 行；第 196～202 行。

### 4. compute_scale() 的六个步骤（补充视角）

- **基础词条**：见 L08 "compute_scale（像素尺度计算函数）"；本条目补充"六步逐行"。
- **中文名称**：像素尺度计算函数的六个步骤
- **英文名称**：compute_scale — six steps
- **初学者解释**：这一个函数把"两点 + 已知真实长度"变成尺度，内部按固定顺序做六件事，每一步都有对应的检查或公式。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 100～144 行：① 参数检查（第 118～120 行，`_check_point(point1)` / `_check_point(point2)` / `_to_float(real_distance_mm)`）；② `real_distance_mm` 合法性检查（第 122～126 行，拒绝 nan / inf，且必须大于 0）；③ `dx` / `dy` / `pixel_distance = math.hypot(dx, dy)`（第 128～131 行）；④ 两点重合检查（第 134～135 行，`pixel_distance == 0` 报 `ValueError`）；⑤ `px_per_mm` / `mm_per_px`（第 137～138 行）；⑥ 返回三个键的字典（第 140～144 行）。只读复算（不是重新标定）：M4 用冻结标定点算出 `L_pixel ≈ 345.418199 px`、`px_per_mm ≈ 5.7569700`（与冻结值 5.756961 差 ≈ 9.0e-6），M5 算出 `L_pixel ≈ 608.634653 px`、`px_per_mm ≈ 6.0863465`（与冻结值 6.086399 差 ≈ 5.2e-5），都在自检容差 `1e-4` 内。
- **源码位置**：`src\calibration.py` 第 100～144 行；调用见 `src\displacement.py` 第 111 行；自检容差见 `src\displacement.py` 第 118、125 行。

### 5. unit_direction()（补充视角：完整展开）

- **基础词条**：见 L08 "unit_direction（单位方向向量函数）"；本条目补充"完整三步"。
- **中文名称**：单位方向向量函数
- **英文名称**：unit_direction
- **初学者解释**：输入两个点，输出"从 P1 指向 P2"的单位方向向量；内部只做三步：算原始向量的两个分量与长度、检查长度不为 0、除以长度。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 147～173 行：① `dx` / `dy` / `length = math.hypot(dx, dy)`（第 166～168 行）；② 零长度检查，两点重合时报 `ValueError`（第 170～171 行）；③ 返回 `{"ux": dx / length, "uy": dy / length}`（第 173 行）。方向约定在 docstring 第 149 行（"从 10 cm 刻线指向 16 cm 刻线"）。`src\displacement.py` 第 112、128～135 行用它复算 `u` 并与冻结常量 `U` 比对（容差 `1e-4`）。
- **源码位置**：`src\calibration.py` 第 147～173 行；`src\displacement.py` 第 34、112、128～135 行。

### 6. project_point()（补充视角：完整展开与"再次归一化"）

- **基础词条**：见 L08 "project_point（一维投影函数）"；本条目补充"函数内部的三个动作"与"为什么它自己再归一化一次"。
- **中文名称**：一维投影函数
- **英文名称**：project_point
- **初学者解释**：把一个像素点压到一条方向上，得到"沿这个方向走了多远"的一个数 `s`（单位 px）。函数内部：读出点和方向、把方向归一化、做点积。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 176～204 行：① 读取 `point` 与 `direction`（第 193～194 行，`_check_point` / `_check_direction`）；② 方向零长度检查 + **再次归一化**（第 196～202 行）；③ 返回 `return x * ux + y * uy`（第 204 行，与第 180 行 docstring 公式一致）。**为什么要"再次"归一化**：函数不假设调用方守规矩；而且项目里的冻结方向常量只保留 6 位小数，本身不是精确单位向量——`|U| = 0.999999763906`、`|U_004| = 0.999999655816`，与 1 分别差约 2e-7 / 3e-7。真实数据验证（只读）：把这次归一化算进去后，M4 的 1050 行、M5 的 1766 行 `s_px` 与公式的最大偏差才落回 `4.974e-4 / 4.998e-4 px`（即"写 3 位小数"的舍入上界 `5e-4 px`）；不把它算进去会差到 `8.299e-4 / 9.235e-4 px`。
- **源码位置**：`src\calibration.py` 第 176～204 行；`src\displacement.py` 第 277～285 行；`src\dynamic_displacement.py` 第 40、147～157 行。

### 7. 点积（dot product）

- **中文名称**：点积
- **英文名称**：dot product
- **初学者解释**：两个二维向量"对应分量相乘再相加"，结果是一个数（标量），不是向量：`a·b = ax·bx + ay·by = |a||b|cos θ`。
- **VisionMotion 中的具体作用**：`src\calibration.py` 第 180 行把投影公式写成 `s = x * ux + y * uy`，第 204 行就是它的实现——"两乘一加"；这里 `a = (x, y)`、`b = (ux, uy)`。注意别与"逐元素相乘"混淆：点积的结果是**一个标量**，`u` 用点积把二维点压成一条数轴上的坐标。
- **源码位置**：`src\calibration.py` 第 180、204 行。

### 8. 有号投影长度（signed projection length）

- **中文名称**：有号投影长度
- **英文名称**：signed projection length
- **初学者解释**：`s = x·ux + y·uy` 在 `|u| = 1` 时等于"点沿方向 u 走了多远"，带正负号：在方向的正侧为正、反侧为负，单位仍是像素。
- **VisionMotion 中的具体作用**：`s` 就是 ds CSV 里的 `s_px` 列（`src\displacement.py` 第 75 行、`src\dynamic_displacement.py` 第 94 行）。沿尺移动 1 px，`s` 变 1 px；垂直移动 10 px，`s` 里只漏进不到 0.07 px（因为 `uy` 只有千分之几）。`s` 可以是负数——符号说明点在方向的哪一侧。
- **源码位置**：`src\calibration.py` 第 180、204 行；`src\displacement.py` 第 75、277～285 行。

### 9. ux / uy（单位方向向量的两个分量）

- **中文名称**：单位方向向量的两个分量
- **英文名称**：ux / uy（cos θ / sin θ）
- **初学者解释**：`u = (cos θ, sin θ)`：`ux` 是方向与 x 轴夹角的余弦，`uy` 是正弦。它们只描述方向，加起来满足 `ux² + uy² = 1`。
- **VisionMotion 中的具体作用**：图像坐标系 y 轴向下（`src\calibration.py` 第 9～10 行），所以 `uy < 0` 表示方向"略向上"。M4 的 `U`：`ux ≈ 0.99998`（几乎水平向右）、`uy ≈ -0.0069`（略向上），与 +x 轴夹角约 **−0.395°**；M5 的 `U_004`：`uy ≈ -0.0039`，夹角约 **−0.224°**——比 M4 更接近水平。把 cos/sin 记反是本课的高频易错点（见易错知识库 L09 第 6 条）。
- **源码位置**：`src\calibration.py` 第 9～10、173 行；`src\displacement.py` 第 55 行；`src\dynamic_displacement.py` 第 66 行。

### 10. 正交分解（orthogonal decomposition）

- **中文名称**：正交分解
- **英文名称**：orthogonal decomposition
- **初学者解释**：把一个向量拆成"沿某方向的一部分"加"垂直于该方向的一部分"：`v = (v·u)u + (v - (v·u)u)`。
- **VisionMotion 中的具体作用**：这是"投影为什么保留沿运动方向的分量、削弱垂直方向分量"的数学依据——垂直分量与 `u` 的点积恰好为 0，所以它对 `s` 的贡献是 0。**注意这不是"算丢了"**：y 仍然通过 `uy` 进入 `s`；准确说法是"垂直于 `u` 的分量对 `s` 的贡献为 0"。垂直方向若真有运动，`s` 也看不到它——这是有意的降维取舍，要在报告里写清楚，而不是当成 bug（`docs\learning\L09_标定方向向量与一维投影.md` 第 6.6 节）。
- **源码位置**：`src\calibration.py` 第 176～204 行（公式与实现的对应）。

### 11. U（M4 冻结方向常量）

- **中文名称**：M4 冻结方向常量
- **英文名称**：U
- **初学者解释**：M4（EXP-003 静态实验）正式冻结的方向：`U = (0.999976, -0.006894)`——几乎完全水平向右、略向上（约 −0.395°）。
- **VisionMotion 中的具体作用**：写在 `src\displacement.py` 第 55 行，方向约定为"10 cm → 16 cm"，来源与尺度常量相同（第 41～47 行的标定说明：EXP-003-STATIC-002.mp4、frame 900、`CAP_PROP_ORIENTATION_AUTO=1` 之后的 1920×1080 坐标系）。自检第 128～141 行核对两件事：`u` 与冻结标定点一致（第 128～135 行）、`u` 是单位向量（第 136～141 行，`|U| = 0.999999763906`，容差 `1e-4`）。`add_projection()` 第 285 行调用 `project_point((x_px, y_px), U)`。
- **源码位置**：`src\displacement.py` 第 41～55、128～141、277～285 行。

### 12. U_004（M5 冻结方向常量）

- **中文名称**：M5（EXP-004 专属）冻结方向常量
- **英文名称**：U_004
- **初学者解释**：M5（EXP-004 动态实验）专属的方向：`U_004 = (0.999992, -0.003913)`——比 M4 更接近水平（约 −0.224°）。名字里的 `_004` 表示"只对 EXP-004 有效"。
- **VisionMotion 中的具体作用**：写在 `src\dynamic_displacement.py` 第 66 行，方向约定为"10 cm → 20 cm（正向）"，来源为 M5.2-1 人工点击 + 独立核验、已冻结不得重新标定（第 59～62 行）。自检第 138～144 行要求 `U_004` 的模在 `1e-6` 内等于 1（`|U_004| = 0.999999655816`）；第 147～157 行用 `project_point()` 复算投影长度并与 `PX_PER_MM_004` 比对；第 167～172 行用 `U_004[0] > 0` 锁定"ds 增大"的正方向。第 20～23 行禁止把 M4 的常量搬进来、禁止 `import src.displacement`。
- **源码位置**：`src\dynamic_displacement.py` 第 20～23、59～66、138～172 行。

### 13. 六类材料

- **中文名称**：六类材料
- **英文名称**：six kinds of material
- **初学者解释**：课程笔记里的内容分成六类，必须永远分清：**A 真实源码 / B 真实项目常数 / C 真实数据 / D 数学公式 / E 教学示例 / F 概念伪代码**。前四类可以当"项目事实"引用（引用前重新核对），后两类不行。
- **VisionMotion 中的具体作用**：L09 笔记第 10 节给出判定表与标注规则。例：A 类——`src\calibration.py` 第 100～144、147～173、176～204 行；B 类——`U` / `U_004`；C 类——4 份 CSV 的逐行复核；D 类——`u = v / |v|`、`s = x·ux + y·uy`；E 类——docstring 里的示例坐标 `(1043.8, 559.3)`、第 5.6 节的算术例子；F 类——第 6.6 节的对比伪代码、第 9 节的知识连接文字框图。引用项目事实时必须能指出文件、函数与行号。
- **源码位置**：`docs\learning\L09_标定方向向量与一维投影.md` 第 10 节（综合引用，不新增源码位置）。

### 14. 只读核对（read-only verification）

- **中文名称**：只读核对
- **英文名称**：read-only verification
- **初学者解释**：只"读"已有的数据文件做验算，不运行原程序、不重新生成、不修改、不覆盖任何文件。
- **VisionMotion 中的具体作用**：L09 用 `results\EXP-003-STATIC-002_track.csv` / `_ds.csv` 与 `results\EXP-004-DYNAMIC-001_track.csv` / `_ds.csv` 四份真实产物逐行核对 `s_px = x·ux + y·uy`：track 与 ds 行数相同、逐行配对，只取 `s_px` 非空的行（M4 1050 行 = `valid=True` 的行；M5 1766 行全部有值）。结论：把 `project_point()` 的再次归一化算进去后，最大偏差为 `4.974e-4 px`（M4）/ `4.998e-4 px`（M5），正好落在 `s_px` 写 3 位小数的舍入上界 `5e-4 px` 之内；二元最小二乘反推的系数与 `U / |U|`、`U_004 / |U_004|` 一致到 `1e-7` 量级。这套口径同时证明了公式正确、方向常量正确、再次归一化确实生效、数据链可追溯。
- **源码位置**：`results\EXP-003-STATIC-002_track.csv`、`results\EXP-003-STATIC-002_ds.csv`、`results\EXP-004-DYNAMIC-001_track.csv`、`results\EXP-004-DYNAMIC-001_ds.csv`（只读）。

### 15. s_px 是坐标不是位移（补充视角）

- **基础词条**：见 L08 "s_px（沿尺方向的一维投影坐标）"；本条目补充"与位移的边界"。
- **中文名称**：投影坐标与位移的区别
- **英文名称**：s_px is a coordinate, not a displacement
- **初学者解释**：`s_px` 回答"沿尺方向现在在哪"；位移回答"相对开始时走了多少"——后者需要先选一个基线。
- **VisionMotion 中的具体作用**：`s_px` 由 `project_point()` 产生；"相对基线的位移"是 `ds_px = s_px - s0`、`ds_mm = ds_px / PX_PER_MM`（`src\displacement.py` 第 339～340 行、`src\dynamic_displacement.py` 第 349～350 行）。基线 `s0` 怎么选（`compute_s0()`，`src\displacement.py` 第 288 行起）、valid gate 的完整规则（`src\displacement.py` 第 57～64 行、`src\dynamic_displacement.py` 第 68～76 行）、`ds_px` / `ds_mm` 的完整流程**都属于 L10**；L09 只登记它们的名称与位置。
- **源码位置**：`src\displacement.py` 第 57～64、288、328～340 行；`src\dynamic_displacement.py` 第 68～76、338～350 行。

---

## L10 从一维位置到位移：s0、ds_px 与 ds_mm

### 1. valid gate（第二道数据筛选）

- **中文名称**：valid gate（第二道数据筛选）
- **英文名称**：valid gate
- **初学者解释**：在"检测到目标"之后的第二道数据筛选：判断这一帧的检测结果**能不能用于物理计算**。检测到 ≠ 能用。
- **VisionMotion 中的具体作用**：ds CSV 的 `valid` 列（`DS_FIELDNAMES`：`src\displacement.py` 第 72～81 行 / `src\dynamic_displacement.py` 第 91～100 行）；判据由 `is_valid_frame()` 唯一给出；只有 `valid=True` 的帧才计算 `s_px` → `ds_px` → `ds_mm`。M4 注释原文"本次 EXP-003 拍摄几何专属参数，不是通用视觉规则"（`src\displacement.py` 第 57 行）；M5 标题原文"与 M4 gate 完全不同，不得混用"（`src\dynamic_displacement.py` 第 68 行）。真实数据：STATIC-002 的 911 帧、STATIC-003 的 792 帧都是 detected=True 但 valid=False（例：STATIC-002 frame 52，area 12439.0、y 35.44 被 y 门限拒绝）；EXP-004 为 0 帧。
- **源码位置**：`src\displacement.py` 第 57～64、175～201 行；`src\dynamic_displacement.py` 第 68～76、183～210 行。

### 2. is_valid_frame（valid 判定函数）

- **中文名称**：valid 判定函数
- **英文名称**：is_valid_frame
- **初学者解释**：输入 detected、area_px、y_px，输出这一帧能不能用（True / False）：先要求 detected=True，再要求 area 与 y 都落在本实验的门限内；缺数据也返回 False。
- **VisionMotion 中的具体作用**：M4 版（`src\displacement.py` 第 175～201 行）：第 188～189 行 `if not detected: return False`；第 191～193 行 area / y 为 None 返回 False（"数据缺失，不填 0"）；第 195～199 行两个范围判断。M5 版（`src\dynamic_displacement.py` 第 183～210 行）逻辑相同、常量换成 `_004`。第 185 行注释原文"绝不修改原始 detected，只在这里判断'这一帧能不能用'"。
- **源码位置**：`src\displacement.py` 第 175～201 行；`src\dynamic_displacement.py` 第 183～210 行。

### 3. detected 与 valid 的区别（补充视角）

- **基础词条**：见 L01 / L06 "detected" 与 L07 "Detection Failure"；本条目补充"两道筛选"的层次关系。
- **中文名称**：detected 与 valid 的区别
- **英文名称**：detected vs valid
- **初学者解释**：detected 回答"看到了吗"（M3 检测结果，track CSV 第 6 列）；valid 回答"这一帧的数据能用吗"（本模块第二道筛选，ds CSV 第 8 列）。
- **VisionMotion 中的具体作用**：detected 由 `marker_detector.py` / M3 产生；valid 由本模块 `is_valid_frame()` 产生，依据是 detected + area 范围 + y 范围。真实数据：三份 track CSV 的 detected 都是 100%；valid 分别为 1050/1961（53.54%）、1192/1984（60.08%）、1766/1766（100%）——只看 detected 成功率会严重高估可用数据量（`summarize()`：`src\displacement.py` 第 418～420 行；`summarize_dynamic()`：`src\dynamic_displacement.py` 第 435～437 行）。
- **源码位置**：`src\displacement.py` 第 57～64、175～201、390～431 行；`src\dynamic_displacement.py` 第 68～76、183～210、400～454 行。

### 4. 无效帧留空（位移字段的缺失表示）

- **中文名称**：无效帧留空
- **英文名称**：empty displacement fields for invalid rows
- **初学者解释**：valid=False 的帧**不删除**，但 `s_px` / `ds_px` / `ds_mm` 三列**留空**——空表示"没有测到 / 不能用"，绝不写 0、-1、nan。
- **VisionMotion 中的具体作用**：`add_valid_flags()` 先把三个字段初始化为 None（`src\displacement.py` 第 272～274 行 / `src\dynamic_displacement.py` 第 281～283 行）；`add_displacement()` 只在 valid 时写值；`build_ds_row()` 把 None 写成空字符串（`src\displacement.py` 第 360～363 行 / `src\dynamic_displacement.py` 第 370～372 行）；第 355 行注释"缺失数据一律写成空字符串（""），绝不写 0 / -1 / nan"。自检逐行核对（第 686～689 行 / 第 1048～1053 行）。真实数据：三份 ds CSV 中无效行位移字段非空 0 例、有效行缺字段 0 例；ds CSV 行数与 track CSV 完全一致（1961 / 1984 / 1766）。
- **源码位置**：`src\displacement.py` 第 21～22、261～274、355～363、686～689、781 行；`src\dynamic_displacement.py` 第 27、270～284、365～372、1048～1053、1159 行。

### 5. s0（基线）

- **中文名称**：位移基线
- **英文名称**：s0 / baseline
- **初学者解释**：位移的参考起点，单位像素。`ds_px = s_px - s0`；`s0` 是"时间窗口内所有有效帧的 `s_px` 平均值"，不是首帧、也不是标尺刻度位置。
- **VisionMotion 中的具体作用**：`compute_s0()` 计算（`src\displacement.py` 第 288～325 行 / `src\dynamic_displacement.py` 第 297～335 行）；窗口内先按 `time_s <= window_s` 与 `valid=True` 筛选（第 304～305 行 / 第 314～315 行），再取平均（第 322～323 行 / 第 332～333 行）；最少有效帧不足时 `ok=False`、`s0=None`（第 318 行 / 第 328 行）。源码第 294 行明文"正式禁止：用 10 cm 代替 s0、用首帧代替均值"。真实复算值：STATIC-002 `s0` = 1076.063871 px、STATIC-003 = 1077.364097 px、EXP-004 = 855.202603 px。
- **源码位置**：`src\displacement.py` 第 288～325、339 行；`src\dynamic_displacement.py` 第 297～335、349 行；真实数据 `results\EXP-003-STATIC-002_ds.csv`、`results\EXP-003-STATIC-003_ds.csv`、`results\EXP-004-DYNAMIC-001_ds.csv`（只读）。

### 6. compute_s0（基线计算函数）

- **中文名称**：基线计算函数
- **英文名称**：compute_s0
- **初学者解释**：收集时间窗口内 valid=True 的 `s_px`，检查帧数是否够，然后求平均；返回一个报告字典而不是单个数字（报告里带窗口统计与 ok 标志）。
- **VisionMotion 中的具体作用**：`src\displacement.py` 第 288～325 行；签名 `compute_s0(rows, window_s=S0_WINDOW_S, min_valid_frames=MIN_S0_VALID_FRAMES)`（第 288 行）；报告字段：`window_s` / `window_total_frames` / `window_valid_frames` / `window_missed_frames` / `window_detected_invalid_frames` / `min_valid_frames` / `ok` / `s0`（第 307～320 行）。M5 同名函数在第 297～335 行，第 311～312 行补充"不扩大窗口、不修改 gate"。调用方：第 790 行 / 第 1168 行；不达标时第 793 行 / 第 1171 行决定不写 ds CSV。
- **源码位置**：`src\displacement.py` 第 288～325、790～796 行；`src\dynamic_displacement.py` 第 297～335、1168～1174 行。

### 7. s0 窗口与最少有效帧（S0_WINDOW_S / MIN_S0_VALID_FRAMES）

- **中文名称**：s0 窗口与最少有效帧参数
- **英文名称**：S0_WINDOW_S / MIN_S0_VALID_FRAMES
- **初学者解释**：两个"拍板"参数：窗口多长（只看开头多少秒）、至少多少帧有效才允许生成 ds CSV。
- **VisionMotion 中的具体作用**：M4：`S0_WINDOW_S = 0.5`、`MIN_S0_VALID_FRAMES = 10`（`src\displacement.py` 第 66～68 行）；M5：`S0_WINDOW_S = 2.0`、`MIN_S0_VALID_FRAMES = 60`（`src\dynamic_displacement.py` 第 78～80 行）。真实数据：窗口内总帧 / 有效帧 = 31/31（STATIC-002）、31/31（STATIC-003）、121/121（EXP-004），都远高于门槛。窗口不足时的处理原文："不扩大窗口、不修改阈值、不做插值"（`src\displacement.py` 第 517 行）。
- **源码位置**：`src\displacement.py` 第 66～68、506～517 行；`src\dynamic_displacement.py` 第 78～80 行。

### 8. 位置与位移（position vs displacement）

- **中文名称**：位置与位移的区别
- **英文名称**：position vs displacement
- **初学者解释**：位置回答"在哪"（`s_px`），位移回答"相对起点走了多少"（`ds_px`、`ds_mm`）。位置有零点从哪来的问题，位移没有。
- **VisionMotion 中的具体作用**：`s_px` 是沿方向 `u` 的一维投影坐标（L09）；位移必须减去基线：`ds_px = s_px - s0`（`src\displacement.py` 第 339 行 / `src\dynamic_displacement.py` 第 349 行）。`s_px` 的绝对值跨实验不可比，差值才对应物理位移。真实证据：三份数据的 frame 0 的 `ds_px` = +4.335 / +0.164 / −3.215（都不为 0，因为 `s0` 是窗口均值而不是首帧值）。
- **源码位置**：`src\displacement.py` 第 288～325、339～340 行；`src\dynamic_displacement.py` 第 297～335、349～350 行；真实数据 `results\EXP-003-STATIC-002_ds.csv` 等三份（只读）。

### 9. ds_px（相对位移，像素）（补充视角）

- **基础词条**：见 L08 "ds_px（相对位移，像素）"；本条目补充 L10 的完整定义与真实数据。
- **中文名称**：相对位移（像素）
- **英文名称**：ds_px
- **初学者解释**：`ds_px = s_px - s0`，单位像素；"相对基线 `s0` 移动了多少像素"。
- **VisionMotion 中的具体作用**：计算在第 339 行 / 第 349 行；只在 valid=True 的行计算（`add_displacement()`，第 328～340 行 / 第 338～350 行）；写 3 位小数（第 87 / 106 行）；无效行留空（第 361 / 371 行）。真实复核（只读）：`|ds_px - (s_px - s0)|` 最大偏差 0.000870968 px（STATIC-002）/ 0.000903226 px（STATIC-003）/ 0.000603306 px（EXP-004），全部在自检容差 0.002 px 内；范围：−1.249～350.268 / −0.311～346.530 / −3.215～402.715 px。
- **源码位置**：`src\displacement.py` 第 76、87、328～340、361 行；`src\dynamic_displacement.py` 第 95、106、338～350、371 行。

### 10. ds_mm（相对位移，毫米）（补充视角）

- **基础词条**：见 L08 "ds_mm（相对位移，毫米）"；本条目补充 L10 的真实数据复核。
- **中文名称**：相对位移（毫米）
- **英文名称**：ds_mm
- **初学者解释**：`ds_mm = ds_px / PX_PER_MM`（等价 `ds_px × MM_PER_PX`）；它是换算结果，不是另一次测量。
- **VisionMotion 中的具体作用**：M4 用 `PX_PER_MM = 5.756961`（`src\displacement.py` 第 340 行）；M5 用 `PX_PER_MM_004 = 6.086399`（`src\dynamic_displacement.py` 第 350 行）；写 4 位小数（第 88 / 107 行）；无效行留空（第 362 / 372 行）。真实复核（只读）：用写入的 `ds_px` 反算最大偏差 0.000132217 / 0.000134074 / 0.000127431 mm；用 `s_px − s0` 反推未舍入 `ds_px` 最大偏差 0.000143821 / 0.000150884 / 0.000139318 mm——全部在自检容差 0.0005 mm 内；范围：−0.2170～60.8426 / −0.0540～60.1932 / −0.5283～66.1663 mm。
- **源码位置**：`src\displacement.py` 第 77、88、340、362 行；`src\dynamic_displacement.py` 第 96、107、350、372 行。

### 11. 双重舍入（补充视角）

- **基础词条**：见 L08 "ds_mm（相对位移，毫米）"中的双重舍入说明；本条目补充 L10 的真实数字。
- **中文名称**：双重舍入
- **英文名称**：double rounding
- **初学者解释**：`ds_mm` 是用**未舍入**的 `ds_px` 算出来再写 4 位小数的；而文件里的 `ds_px` 只有 3 位小数。所以"拿文件里的 `ds_px` 反算 `ds_mm`"可能出现 ±0.0001 mm 量级的差——这是正常的舍入顺序，不是数据错误。
- **VisionMotion 中的具体作用**：`FIELD_PATTERNS` 规定 `ds_px` 3 位小数、`ds_mm` 4 位小数（`src\displacement.py` 第 84～90 行 / `src\dynamic_displacement.py` 第 103～109 行）；自检容差 0.0005 mm（`src\displacement.py` 第 736～740 行 / `src\dynamic_displacement.py` 第 1105～1113 行）。真实复核（只读）：两种口径的最大偏差分别 ≤ 0.000134074 mm 与 ≤ 0.000150884 mm，正好是 ~1e-4 mm 量级——与双重舍入预期一致。
- **源码位置**：`src\displacement.py` 第 84～90、348～366、736～740 行；`src\dynamic_displacement.py` 第 103～109、358～376、1105～1113 行。

### 12. 有效性统计字段（valid_rate / invalid_count 等）

- **中文名称**：有效性统计字段
- **英文名称**：valid_rate / invalid_count / detected_invalid_count / longest_invalid_run
- **初学者解释**：四个回答"数据可用性"的统计量：有效比例、无效总数、被第二道筛选拒绝的数量、最长连续无效段。
- **VisionMotion 中的具体作用**：`summarize()`（`src\displacement.py` 第 390～431 行）：第 420 行 `valid_rate`、第 421 行 `invalid_count`、第 423 行 `detected_invalid_count`、第 427 行 `longest_invalid_run`（循环第 405～413 行）；`summarize_dynamic()`（`src\dynamic_displacement.py` 第 400～454 行）：第 437 / 438 / 440 / 450 行。真实数值：valid_rate = 1050/1961 ≈ 53.54% / 1192/1984 ≈ 60.08% / 1766/1766 = 100%；detected_invalid_count = 911 / 792 / 0；longest_invalid_run = 180 / 147 / 0。
- **源码位置**：`src\displacement.py` 第 390～431 行；`src\dynamic_displacement.py` 第 400～454 行；真实数据 `results\EXP-003-STATIC-002_ds.csv` 等三份（只读）。

### 13. 数据依赖链（detected → valid → s_px → ds_px → ds_mm）

- **中文名称**：数据依赖链
- **英文名称**：data dependency chain
- **初学者解释**：五个环节一环扣一环：先有检测（detected），再有可用性筛选（valid），才有位置（s_px）、位移（ds_px）与毫米位移（ds_mm）；每一环只依赖上一环。
- **VisionMotion 中的具体作用**：detected 写在 track CSV 第 6 列；valid 由 `is_valid_frame()` 判定并写在 ds CSV 第 8 列；`s_px` 由 `add_projection()` 只对 valid 行计算（`src\displacement.py` 第 277～285 行）；`ds_px` / `ds_mm` 由 `add_displacement()` 只对 valid 行计算（第 339～340 行）。任何一环断掉，后面全部留空：detected=False → 不判 valid；area / y 超界或缺失 → valid=False；valid=False → 没有 `s_px`、没有 ds、不参与 `s0` 平均（第 305 行）。
- **源码位置**：`src\displacement.py` 第 175～201、261～274、277～285、304～305、328～340 行；`src\dynamic_displacement.py` 第 183～210、270～284、286～294、314～315、338～350 行。

### 14. s0 不达标不写 ds CSV

- **中文名称**：s0 不达标不写 ds CSV
- **英文名称**：no ds CSV when s0 is not available
- **初学者解释**：如果视频开头窗口里有效帧太少，就不生成 ds CSV——宁可"没有结果"，也不改规则硬凑。
- **VisionMotion 中的具体作用**：`build_ds_from_track_csv()` 第 781 行原文"过程中不删除任何行；s0 窗口有效帧不足时不写 ds CSV"；第 793 行 `if s0_report["ok"]` 才调用 `add_displacement()` / `write_ds_csv()`（第 794～796 行）；M5 同逻辑（第 1159、1171～1174 行），且第 1215～1217 行还要求冻结常量自检先通过。不足时的处理原文："本视频不生成 ds CSV；不扩大窗口、不修改阈值、不做插值"（第 517 行）。
- **源码位置**：`src\displacement.py` 第 506～517、769～811 行；`src\dynamic_displacement.py` 第 1147～1191、1215～1217 行。

---

## L12 转向点检测与运动段切分

### 1. 转向点（turning point）

- **中文名称**：转向点
- **英文名称**：turning point
- **初学者解释**：运动方向发生改变的位置所对应的那一帧。它不是"程序发现方向变了"的那一帧，而是**方向改变前到达的极值帧**。
- **VisionMotion 中的具体作用**：`detect_turning_points()` 用原始 `x_px` 序列与 20 px 反向行程阈值找转向点，并把每个转向点写成 `turns` 里的一条记录（`frame` / `time_s` / `x_px` / `ds_mm` / `kind` / `direction_before` / `direction_after`）。真实结果（只读核对）：EXP-004 共 6 个转向点——491 peak、602 valley、838 peak、1063 valley、1254 peak、1513 valley；与 `demo\run_m53_plot.py` 第 67～74 行冻结的 6 个 frame 完全一致。
- **源码位置**：`src\dynamic_displacement.py` 第 462–593 行（第 529、536 行写入 `turn_indexes`；第 552–563 行组装 turns）；冻结值见 `demo\run_m53_plot.py` 第 67–74 行。

### 2. detect_turning_points()

- **中文名称**：转向点检测函数
- **英文名称**：detect_turning_points
- **初学者解释**：输入逐帧数据、输出"转向点列表 + 运动段列表"的函数；它只处理原始 `x_px`，不做平滑 / 滤波 / 插值 / 补帧 / 预测。
- **VisionMotion 中的具体作用**：定义在 `src\dynamic_displacement.py` 第 462 行，函数体到第 593 行（第 458–594 行是"八、原始 x_px 转向点 / 运动段检测"小节）。第 495–497 行构造分析序列：`row["detected"] and row["x_px"] is not None`；第 498 行统计其中 `valid=False` 的行数（只统计，不删除）；第 512–538 行是 zigzag 状态机；返回 `turns` 与 `segments`。它由 `build_ds_from_track_csv()` 调用（第 1183 行）。
- **源码位置**：`src\dynamic_displacement.py` 第 462–593 行（docstring 第 463–493 行；关键行 495–498、512–538、540–547、552–563、565–591）；调用点第 1183 行。

### 3. 分析序列（analysis_rows / analysis_invalid_rows）

- **中文名称**：分析序列与其中无效行数
- **英文名称**：analysis series / analysis_rows / analysis_invalid_rows
- **初学者解释**：真正参与转向检测的行集合叫分析序列；报告里同时记录"一共用了多少行"和"其中有多少行 `valid=False`"，后者只统计、不删除。
- **VisionMotion 中的具体作用**：第 495–497 行用 `detected=True` 且有 `x_px` 的行构造 `series`；第 498 行 `analysis_invalid_rows = sum(1 for row in series if not row["valid"])`；第 501–502 行写进 report；第 485 行 docstring 原文"其中 valid=False 的行数（只统计，不删除）"；第 741–744 行把它打印为"17. 转向点分析使用行数：%d（其中 valid=False 行：%d，只统计不删除）"。注意：`series` 的筛选条件不含 `valid`，所以 `valid=False` 的行仍留在序列里参与状态机。真实数据：EXP-004 的 `analysis_rows = 1766`、`analysis_invalid_rows = 0`。
- **源码位置**：`src\dynamic_displacement.py` 第 485、495–498、501–502、741–744 行。

### 4. 原始 x_px 序列（raw x_px series）

- **中文名称**：原始 x_px 序列
- **英文名称**：raw x_px series
- **初学者解释**：直接用检测结果里的水平像素坐标 `x_px` 按 frame 升序排成的序列——不换字段、不做任何前处理。
- **VisionMotion 中的具体作用**：第 467 行 docstring 明确"只使用原始 x_px 序列（detected=True 且有 x 的行，按 frame 升序）"；第 468 行"不平滑、不滤波、不插值、不补帧、不预测"；模块第 30 行"转向点只使用原始 x_px 数据，最小运动行程 MIN_TURN_TRAVEL_PX = 20.0 px"。因为 `U_004` 的 `ux > 0`，正向对应原始 x 增大、也对应 ds 增大（第 480–481 行）。`read_track_csv()`（第 228–262 行）按 CSV 行序读入，不排序、不删行；帧升序是 track CSV 的输入契约。
- **源码位置**：`src\dynamic_displacement.py` 第 16、30、228–262、467–468、480–481、495–497 行。

### 5. 状态机（zigzag）

- **中文名称**：zigzag 状态机
- **英文名称**：zigzag state machine
- **初学者解释**：用"当前极值 + 当前方向"两个状态逐帧推进的检测流程：顺着方向走就更新极值，反向走满 20 px 就确认一次转向。
- **VisionMotion 中的具体作用**：第 512–515 行初始化 `turn_indexes = []`、`direction = 0`、`extreme_index = 0`；第 517–538 行逐帧循环：`direction == 0` 时先确定方向（第 521–524 行，`abs(x_i - x_extreme) >= 20`）；`direction == +1` 时更新峰值并在反向 20 px 时确认 peak（第 525–531 行）；`direction == -1` 时镜像确认 valley（第 532–538 行）。确认后方向翻转、`extreme_index` 重置为确认帧 `i`。全程只用当前与历史帧，不使用未来信息。
- **源码位置**：`src\dynamic_displacement.py` 第 512–538 行。

### 6. direction（0 / +1 / −1）

- **中文名称**：当前已确认方向
- **英文名称**：direction
- **初学者解释**：状态机里的方向变量：`0` = 还没确定方向；`+1` = 正在沿 +x（正向）走；`-1` = 正在沿 −x（负向）走。
- **VisionMotion 中的具体作用**：第 514 行初始化为 0；第 523 行在 `|x_i - x_extreme| >= 20` 后设为 `1 if x_i > x_extreme else -1`，同时把 `extreme_index` 移到 `i`（第 524 行）；第 530 行 peak 确认后置为 `-1`；第 537 行 valley 确认后置为 `+1`。因为 `U_004` 的 `ux > 0`，`+1` 就是"正向 = ds 增大"、`-1` 就是"负向 = ds 减小"（第 83–84、480–481 行）。只读内存复算：EXP-004 的 `direction` 首次在 frame 246 确定为 `+1`（x0 852.81 → x246 873.27，差 20.46 px）。
- **源码位置**：`src\dynamic_displacement.py` 第 83–84、480–481、514、521–524、530、537 行。

### 7. extreme_index

- **中文名称**：当前方向上的极值下标
- **英文名称**：extreme_index
- **初学者解释**：当前这一轮运动里"最远走到哪里"的位置记账；顺着方向走就不断把它更新为最新帧，反向走满 20 px 时它就作为转向点被写入列表。
- **VisionMotion 中的具体作用**：第 515 行初始化为 0；第 526–527 行（正向）当 `x_i > x_extreme` 时 `extreme_index = i`；第 533–534 行（负向）当 `x_i < x_extreme` 时 `extreme_index = i`；第 529、536 行把 `extreme_index`（而不是确认帧 `i`）写入 `turn_indexes`；第 531、538 行在确认后把 `extreme_index` 重置为 `i`，开始跟踪新方向的极值。注意它是 `series` 的下标，不是 frame；输出时通过 `series[index]["frame"]` 取真实 frame（`describe()` 第 543 行）。EXP-004 恰好 1766 行全部进入 series，所以下标数值与 frame 相同。
- **源码位置**：`src\dynamic_displacement.py` 第 515、526–527、529、531、533–534、536、538、543、554 行。

### 8. turn_indexes

- **中文名称**：已确认转向点列表
- **英文名称**：turn_indexes
- **初学者解释**：状态机确认过的转向点清单，每一项是"极值下标 + 类型（peak / valley）"。
- **VisionMotion 中的具体作用**：第 513 行初始化为 `[]`；第 529 行追加 `(extreme_index, "peak")`；第 536 行追加 `(extreme_index, "valley")`；第 553–563 行遍历它生成 `turns`；第 566 行用它的下标组成运动段边界。它只包含确认过的转向点，不含起点 / 终点。真实数据：EXP-004 的 `turn_indexes` 长度为 6，依次为 f491 peak、f602 valley、f838 peak、f1063 valley、f1254 peak、f1513 valley（frame 由 `series[index]["frame"]` 得到）。
- **源码位置**：`src\dynamic_displacement.py` 第 513、529、536、552–563、566 行。

### 9. MIN_TURN_TRAVEL_PX = 20.0（反向行程阈值）

- **中文名称**：最小反向行程阈值
- **英文名称**：minimum turn travel threshold（MIN_TURN_TRAVEL_PX）
- **初学者解释**：只有原始 `x` 从当前极值**反向**走满至少 20 px，这个极值才被确认为转向点；它是"确认一次转向"的门槛，不是"相邻两帧变化量"的门槛。
- **VisionMotion 中的具体作用**：第 87 行 `MIN_TURN_TRAVEL_PX = 20.0`；第 85–86 行注释"只有当原始 x 从当前极值反向走了至少 20 px，该极值才被确认为转向点（静止段噪声不可能触发）"；第 474–477 行 docstring 说明依据：本视频静止段相邻帧 |dx| 中位数约 0.13 px、静止段最大约 1.25 px，远达不到 20 px，因此不会制造假转向。第 507 行把它写进 report（`min_turn_travel_px`）。20 px 在第 522、528、535、588 行各出现一次：前三条是状态机里的"从极值反向的行程"，第 588 行是"整段两端之间的行程"。
- **源码位置**：`src\dynamic_displacement.py` 第 85–87、474–477、507、522、528、535、588 行。

### 10. 确认帧（confirmation frame）与确认滞后

- **中文名称**：确认帧 / 确认滞后
- **英文名称**：confirmation frame / confirmation lag
- **初学者解释**：转向点本身是极值帧；程序要等反向行程达到 20 px 的那一帧才承认这次转向，这一帧叫确认帧。确认帧一般比转向点晚，这段延迟叫确认滞后。
- **VisionMotion 中的具体作用**：状态机在 `x_extreme - x_i >= 20`（第 528 行）或 `x_i - x_extreme >= 20`（第 535 行）时确认转向，但写入 `turn_indexes` 的是 `extreme_index`（第 529、536 行），确认帧 `i` 只用于触发确认并把 `extreme_index` 重置为 `i`（第 531、538 行）。真实案例：peak f491 在 f505 确认（反向 21.71 px）、valley f602 在 f732 确认（反向 22.28 px）、peak f838 在 f971 确认（反向 20.71 px）；按同一规则只读内存复算其余三次为 f1063→f1156（20.03 px）、f1254→f1346（20.66 px）、f1513→f1535（20.08 px）。确认滞后是抗噪与可复现的代价，不是错误。
- **源码位置**：`src\dynamic_displacement.py` 第 528–531、535–538 行；真实数据见 `results\EXP-004-DYNAMIC-001_track.csv` 对应行（只读核对）。

### 11. peak / valley（峰值 / 谷值）

- **中文名称**：峰值 / 谷值
- **英文名称**：peak / valley
- **初学者解释**：peak 是正向运动结束时留下的极值（原始 x 的局部极大）；valley 是负向运动结束时留下的极值（原始 x 的局部极小）。
- **VisionMotion 中的具体作用**：第 529 行在 `direction == +1` 分支确认 peak，方向变化为"正向 → 负向"；第 536 行在 `direction == -1` 分支确认 valley，方向变化为"负向 → 正向"；第 556–561 行把这两种类型翻译成 `direction_before` / `direction_after`。因为 `U_004` 的 `ux > 0`（第 480–481 行），peak 也对应 `ds` 的局部极大、valley 也对应 `ds` 的局部极小。真实数据：EXP-004 三次 peak（f491 / f838 / f1254）与三次 valley（f602 / f1063 / f1513）交替出现。
- **源码位置**：`src\dynamic_displacement.py` 第 480–481、529、536、556–561 行。

### 12. turns（转向点报告）与 describe()

- **中文名称**：转向点报告与字段整理函数
- **英文名称**：turns report / describe()
- **初学者解释**：`turns` 是每个转向点一条记录的列表；`describe()` 负责把一行数据整理成报告需要的四个基本字段。
- **VisionMotion 中的具体作用**：`describe(row)`（第 540–547 行）返回 `frame` / `time_s` / `x_px` / `ds_mm`（第 546 行注释：`ds_mm` 在 `valid=False` 时为 `None`，打印"无"，不伪造数值）；第 549–550 行用它生成起点 / 终点；第 552–563 行用它生成每个转向点并加上 `kind` / `direction_before` / `direction_after`。最终 `turns` 的七个字段是 `frame` / `time_s` / `x_px` / `ds_mm` / `kind` / `direction_before` / `direction_after`；第 774–792 行把每个转向点打印出来。
- **源码位置**：`src\dynamic_displacement.py` 第 540–547、549–550、552–563、774–792 行。

### 13. direction_before / direction_after

- **中文名称**：转向前后的运动方向
- **英文名称**：direction_before / direction_after
- **初学者解释**：转向点之前的运动方向与之后的运动方向；它们由转向类型直接决定，不需要再测一次。
- **VisionMotion 中的具体作用**：第 556–558 行：`kind == "peak"` → `direction_before = DIRECTION_POSITIVE`（正向）、`direction_after = DIRECTION_NEGATIVE`（负向）；第 559–561 行：`else`（valley）→ 负向 → 正向。`DIRECTION_POSITIVE = "正向"`、`DIRECTION_NEGATIVE = "负向"` 在第 111–113 行定义（注释"只允许这两种说法"）。因此这两个字段是由 `kind` **推导**得到的，不是从 Δds 重新测量出来的；真实数据里 f491 的这两个字段就是"正向 → 负向"。
- **源码位置**：`src\dynamic_displacement.py` 第 111–113、556–561 行。

### 14. 运动段（motion segment）与 boundary_indexes

- **中文名称**：运动段与边界索引
- **英文名称**：motion segment / boundary_indexes
- **初学者解释**：把"起点 → 每个转向点 → 终点"依次连起来，相邻两个边界之间就是一段运动；段数 = 转向点数 + 1。
- **VisionMotion 中的具体作用**：第 566 行 `boundary_indexes = [0] + [index for index, _ in turn_indexes] + [len(series) - 1]`；第 568–591 行对每对相邻边界生成一个 `segment` 字典（`start_frame` / `start_time_s` / `start_x_px` / `end_frame` / `end_time_s` / `end_x_px` / `direction` / `travel_px` / `below_min_travel`）；第 479 行 docstring"运动段数 = 转向点数量 + 1"；第 764–771 行把段数与 below_min 计数打印出来；第 795–814 行打印每一段。真实数据：EXP-004 的 6 个转向点把整段运动切成 7 段，边界 frame 为 0 → 491 → 602 → 838 → 1063 → 1254 → 1513 → 1765；其中 0 与 1765 是边界而不是转向点。
- **源码位置**：`src\dynamic_displacement.py` 第 478–479、565–591、764–771、795–814 行。

### 15. travel_px

- **中文名称**：段行程（像素）
- **英文名称**：travel_px
- **初学者解释**：这一运动段两端之间的行程：`|终点 x_px − 起点 x_px|`，单位像素。
- **VisionMotion 中的具体作用**：第 571 行 `travel_px = abs(tail["x_px"] - head["x_px"])`；第 586 行旁边由 `tail` / `head` 比较给出段方向（第 572–577 行：tail 大 = 正向、tail 小 = 负向、相等 = "无位移"）；第 801 行打印为"行程：%.2f px"。注意它是**两端之间**的行程（段级），不是状态机里"从极值反向的行程"（第 528、535 行）。真实数据：EXP-004 七段的 `travel_px` 为 205.05 / 84.80 / 126.17 / 92.22 / 190.09 / 128.80 / 188.61 px。
- **源码位置**：`src\dynamic_displacement.py` 第 565–577、586、795–814 行。

### 16. below_min_travel

- **中文名称**：段行程是否小于最小行程
- **英文名称**：below_min_travel
- **初学者解释**：给每一段打的标记：这段两端之间的行程是不是小于 20 px。
- **VisionMotion 中的具体作用**：第 588 行 `"below_min_travel": travel_px < MIN_TURN_TRAVEL_PX`；它比较的是**整个运动段两端之间的行程**（第 571 行），发生在状态机结束、切分运动段之后；而转向确认比较的是"从当前极值反向的行程"（第 528、535 行），发生在状态机运行中。两者都使用 20 px，但比较对象不同。第 764–771 行统计"其中行程 < 20.0 px 的段：%d"。真实数据：EXP-004 七段行程都 ≥ 20 px，因此七个 `below_min_travel` 全部为 `False`。
- **源码位置**：`src\dynamic_displacement.py` 第 571、588、764–771 行。

### 17. 边界点（起点 / 终点）

- **中文名称**：边界点（起点 / 终点）
- **英文名称**：boundary points
- **初学者解释**：视频的第一帧和最后一帧只作为运动记录的两端边界，不算转向点。
- **VisionMotion 中的具体作用**：第 478–479 行 docstring"视频首帧与末帧不是极值点，只作为记录边界（起点 / 终点），不计入转向点数量"；第 549–550 行 `report["start"] = describe(series[0])`、`report["end"] = describe(series[-1])`；第 566 行把它们与所有转向点拼成 `boundary_indexes`；第 745–761 行打印起点 / 终点。真实数据：EXP-004 的起点 f0（t 0.000000，x 852.81，ds_mm −0.5283）、终点 f1765（t 29.355535，x 1256.91，ds_mm 65.8647）。
- **源码位置**：`src\dynamic_displacement.py` 第 478–479、549–550、566、745–761 行。

### 18. 原始数据原则（不平滑 / 不滤波 / 不插值 / 不补帧 / 不预测）

- **中文名称**：原始数据原则
- **英文名称**：raw-data principle（no smoothing / filtering / interpolation / padding / prediction）
- **初学者解释**：测量数据就是证据，不能为了让曲线"好看"去改数据；噪声要用明确规则处理，而不是抹掉。
- **VisionMotion 中的具体作用**：第 467–468 行"只使用原始 x_px 序列……不平滑、不滤波、不插值、不补帧、不预测"；模块第 27 行"不删除任何 track CSV 行；valid=False 的位移字段一律留空（不写 0 / -1 / nan）"；第 28 行"不做平滑 / 滤波 / 插值 / 补帧 / 补零 / 预测 / FFT / 频率 / 周期 / 振幅分析"；第 30 行"转向点只使用原始 x_px 数据"；第 16 行数据链也写明"最小反向行程 20 px，不平滑、不滤波"。这样每个转向点、每段行程都能追溯回原始 CSV 行。
- **源码位置**：`src\dynamic_displacement.py` 第 16、27–28、30、467–468 行。

### 19. 冻结规则与可复现性

- **中文名称**：冻结规则与可复现性
- **英文名称**：frozen rules & reproducibility
- **初学者解释**：把阈值与流程写成明确常量（如 20.0 px），同一个输入必然得到同一个输出；任何人可以按行号复算。
- **VisionMotion 中的具体作用**：第 466 行 docstring"口径（已冻结，不得修改；与 M5.1-C 只读审计完全相同）"；第 87 行阈值是常量；第 512 行注释"与 M5.1-C 审计完全相同的实现"；第 20–23 行声明 EXP-004 专属、不得混用 M4 常量；第 30 行固定 MIN_TURN_TRAVEL_PX = 20.0 px。真实验证：M5.2 冻结的 6 个转向点（`demo\run_m53_plot.py` 第 67–74 行）与 `results\EXP-004-DYNAMIC-001_*.csv` 只读复算结果完全一致；该脚本第 15–19 行还明确"不重新运行转向检测（只用 M5.2 冻结的 6 个 frame）"。
- **源码位置**：`src\dynamic_displacement.py` 第 20–23、30、87、462–466、512 行；`demo\run_m53_plot.py` 第 15–19、67–74 行。

---

## L11 位移数据、正负号与运动方向

> 注：本节词条按补录顺序排在本页 L12 小节之后；课程顺序为 L10 → L11 → L12，速查索引中的排列不受影响。

### 1. Δds（位移变化量）

- **中文名称**：位移变化量
- **英文名称**：Δds / delta ds
- **初学者解释**：相邻两帧位移读数之差：`Δds = ds[i+1] - ds[i]`。它回答的是"这一段正在往哪边运动"：Δds > 0 向正方向运动，Δds < 0 向负方向运动，Δds = 0 表示该相邻间隔读数不变。Δds 不是速度（速度还要除以 Δt）。
- **VisionMotion 中的具体作用**：源码里**没有** `Δds` / `delta_ds` 变量或 CSV 字段；与它对应的文字规则写在 `src\dynamic_displacement.py` 第 83～84 行（"正向 = ds 增大（沿 U_004，即尺子 10 cm -> 20 cm 方向）"；"负向 = ds 减小"）与第 480～481 行。用 `ds_px` 或 `ds_mm` 算都同号（第 340 / 350 行除数为正）。两个前提：两帧都 valid（`ds` 非空）才能相减；空洞处 Δds 断开（M4 静态数据的平台之间就是空洞）。真实例子：M5 frame 237 → 313，`ds_mm` 从 −0.0046 增大到 +27.1660（Δds = +27.1706 mm）；M5 frame 963 → 1015，从 +39.7894 减小到 +26.1587（Δds = −13.6307 mm）。
- **源码位置**：`src\displacement.py` 第 272～274、284～285、339～340、360～363 行；`src\dynamic_displacement.py` 第 83～84、349～350、480～481 行；真实数据 `results\EXP-004-DYNAMIC-001_ds.csv`（只读核对）。

### 2. 运动方向（正向 / 负向）

- **中文名称**：运动方向
- **英文名称**：motion direction（positive / negative）
- **初学者解释**：判断"正在往哪个方向运动"只看变化量 Δds 的符号（不是看 ds 的符号）：Δds > 0 = 向正方向；Δds < 0 = 向负方向；Δds = 0 = 该相邻间隔读数不变。
- **VisionMotion 中的具体作用**：第 83～84 行给出定义；第 111～113 行规定显示文字只允许 `DIRECTION_POSITIVE = "正向"` 与 `DIRECTION_NEGATIVE = "负向"` 两种说法（注释："只允许这两种说法"）；第 480～481 行在 docstring 重复规则，并指出 `U_004` 的 `ux > 0`，所以正向对应原始 `x_px` 增大（`detect_turning_points()` 用的就是原始 `x_px`，第 467、495～497 行；完整算法属于 L12）。真实例子：M5 f237 → f313（负侧、向正方向运动）与 f963 → f1015（正侧、向负方向运动）。
- **源码位置**：`src\dynamic_displacement.py` 第 82～87、111～113、458～594 行；真实数据 `results\EXP-004-DYNAMIC-001_ds.csv`（只读）。

### 3. 正方向约定（P1 → P2）

- **中文名称**：正方向约定
- **英文名称**：positive direction convention（P1 → P2）
- **初学者解释**：正方向不是物理定律，而是实验前人为规定的"记账方向"：从标定点 P1 指向 P2。M4 是 10 cm → 16 cm；M5 是 10 cm → 20 cm。
- **VisionMotion 中的具体作用**：M4 第 46 行原文"两点真实距离：60.0 mm，方向约定 10 cm -> 16 cm"，第 55 行 `U = (0.999976, -0.006894)`（方向为 10 cm → 16 cm）；M5 第 60～62 行 P1（10 cm）/ P2（20 cm）/ 100.0 mm，第 66 行 `U_004 = (0.999992, -0.003913)`（方向 10 cm → 20 cm（正向）），第 133 行自检："U_004 指向 10 cm -> 20 cm（ux > 0，即"ds 增大"为正向）"。把约定反过来会让所有 `s_px` / `ds` 整体反号，且不会报错；M4 与 M5 是两套独立常量，不能混用（L10 已学：M5 第 20～23 行禁止 `import src.displacement`）。
- **源码位置**：`src\displacement.py` 第 44～46、55 行；`src\dynamic_displacement.py` 第 59～66、133、169 行。

### 4. 参考位置与符号侧（s0 / 正侧 / 负侧）

- **中文名称**：参考位置与符号侧
- **英文名称**：reference position and side of sign
- **初学者解释**：`s0` 是参考位置（L10 的窗口内有效帧 `s_px` 平均值），它本身**不带方向**；`ds = s_px - s0` 为正 → 这一帧在参考位置的**正侧**（沿 `U` / `U_004` 指向的一侧）；为负 → **负侧**；为零 → 恰好落在参考位置上。符号只表示"在哪一侧"，不代表好坏、不代表快慢。
- **VisionMotion 中的具体作用**：源码只写 `ds_px = s_px - s0`（第 339 / 349 行），"正侧 / 负侧"是概念解释用语（源码里没有这两个词）。真实数据（只读核对）：STATIC-002 的 34 个负号帧全部在 frame 1～51；STATIC-003 的 18 个全部在 frame 2～34；EXP-004 的 161 个全部在 frame 0～237。`|ds|` 表示离参考位置多远（沿尺方向的投影距离），不是速度。
- **源码位置**：`src\displacement.py` 第 288～325、339～340 行；`src\dynamic_displacement.py` 第 349～350 行；真实数据 `results\EXP-003-STATIC-002_ds.csv`、`results\EXP-003-STATIC-003_ds.csv`、`results\EXP-004-DYNAMIC-001_ds.csv`（只读）。

### 5. 符号统计（正 / 负 / 零计数）

- **中文名称**：符号统计
- **英文名称**：sign counts（positive / negative / zero）
- **初学者解释**：按 `ds_mm` **非空**（即 valid=True）的行统计"正侧 / 负侧 / 恰好为零"的帧数。它统计的是**符号侧**，不是"有多少帧在向正 / 负方向运动"。
- **VisionMotion 中的具体作用**：三份真实数据为 1016/34/0（STATIC-002）、1174/18/0（STATIC-003）、1605/161/0（EXP-004）；"零 0 例"只表示这三份文件的 4 位小数里没有恰好写成 `0.0000` 的行，不代表"不可能经过参考位置"。对应 `ds_mm` 范围：−0.2170～60.8426 / −0.0540～60.1932 / −0.5283～66.1663。
- **源码位置**：`src\displacement.py` 第 339～340 行；`src\dynamic_displacement.py` 第 349～350 行；统计来自 `results\` 下三份 ds CSV（只读）。

### 6. 平台 + 台阶 + 空洞（M4 静态形态）

- **中文名称**：平台 + 台阶 + 空洞
- **英文名称**：plateau + step + gap（M4 static displacement shape）
- **初学者解释**：M4 静态位移数据的形态：连续一段 valid 帧的 `ds_mm` 基本停在一个水平附近（**平台**）；相邻平台大约相差 10 mm（**台阶**）；平台之间是长段 `valid=False`（**空洞**——帧还在文件里，只是位移字段留空）。
- **VisionMotion 中的具体作用**：STATIC-002 / STATIC-003 各有 7 个平台（约 0、10、20、30、40、50、60 mm；平台 frame 区间与 `ds_mm` 范围见笔记第 7.2 节）；最长连续 invalid 段为 180 帧（止于 frame 231）与 147 帧（止于 frame 181）。只读核对：空洞中的帧 `detected` 仍为 True，被 M4 gate 的 area / y 拒绝（STATIC-002：904 帧同时违反、7 帧只违反 y、0 帧只违反 area；STATIC-003：785 / 7 / 0）；"为什么越界"不在本课做因果结论。跨空洞不能硬算 Δds。
- **源码位置**：`src\displacement.py` 第 175～201、272～274、360～363 行；真实数据 `results\EXP-003-STATIC-002_ds.csv` / `_track.csv`、`results\EXP-003-STATIC-003_ds.csv` / `_track.csv`（只读）。

### 7. 连续往返（M5 动态形态）

- **中文名称**：连续往返
- **英文名称**：continuous back-and-forth（M5 dynamic displacement shape）
- **初学者解释**：M5 动态位移数据的形态：`ds` 数值在整段数据里多次上升、下降，而且没有空洞（每一帧都有位移值，Δds 可以逐帧算）。
- **VisionMotion 中的具体作用**：EXP-004 为 1766/1766 全部 valid、0 invalid；`ds_mm` 从 −0.5283（frame 0）到 66.1663（frame 1701），末帧 frame 1765 = 65.8647；抽样轨迹见笔记第 8.2 节（约 33 → 19 → 40 → 25 → 55 → 35 → 66 mm 的多次升降）。本课不数转向点、不切运动段、不谈周期 / 频率 / FFT（留给 L12 及以后）。
- **源码位置**：`src\dynamic_displacement.py` 第 338～350 行；真实数据 `results\EXP-004-DYNAMIC-001_ds.csv` / `_track.csv`（只读）。

### 8. MIN_TURN_TRAVEL_PX（最小反向行程阈值，最小认识）

- **中文名称**：最小反向行程阈值
- **英文名称**：MIN_TURN_TRAVEL_PX
- **初学者解释**：只有原始 `x_px` 从当前极值**反向走满 20 px**，这个极值才被确认为转向点（峰 / 谷）；小于 20 px 的反向行程不改变方向认定。它是一条"行程阈值"，不是速度阈值、不是位移阈值。
- **VisionMotion 中的具体作用**：`src\dynamic_displacement.py` 第 30 行 docstring、第 85～87 行定义（第 87 行 `MIN_TURN_TRAVEL_PX = 20.0`）、第 474～477 行解释：静止段噪声的相邻帧 `|dx|` 中位数约 0.13 px、静止段最大约 1.25 px，远达不到 20 px，所以噪声不会制造假转向。本课只建立最小认识；`detect_turning_points()`（第 462 行起）的完整算法（zigzag、峰谷判定、运动段切分，第 512～594 行）属于 L12。
- **源码位置**：`src\dynamic_displacement.py` 第 30、82～87、462、474～477、480～481 行。

### 9. 五类材料（L11 版）

- **中文名称**：五类材料
- **英文名称**：five material classes（project source / real data / teaching example / conceptual explanation / conceptual pseudocode）
- **初学者解释**：本课的材料分成五类：**项目真实源码**（可给出文件 + 行号）、**真实数据**（`results\` 里已有的数值）、**教学示例**（为讲解临时编的数字，标明"非项目数据"）、**概念解释**（文字 / 表格说明，不宣称是源码或数据）、**概念伪代码**（类 Python 流程示意，不是项目源码）。引用前先分类，避免把解释工具当成项目事实。
- **VisionMotion 中的具体作用**：本课例子——真实源码：第 46、55、272～274、284～285、338～340、360～363 行与 `src\dynamic_displacement.py` 第 66、83～84、87、111～113、133 行；真实数据：三份 ds CSV 的统计与 M5 f237 / f963 例子；教学示例：笔记第 6.6 节的 `+30.0 → +27.0 mm` 算例；概念解释："三条不等于"、平台 / 台阶 / 空洞、人为约定；概念伪代码：笔记第 6.1、10.2 节的 Δds 流程。与 L09 "六类材料"的关系：L09 把"真实项目常数"单列，L11 按本课要求归为五类。
- **源码位置**：无（方法论条目）；各材料的定位见 `docs\learning\L11_位移正负与运动方向.md` 第 2 节与文末"代码与事实来源说明"。

---

## L13 从运动段到往复运动

> 本节词条的核心纪律：**L13 只把"往复结构 → 周期候选 → 周期是否可信"作为概念与判据思想来学习**；
> 当前项目真实源码只实现到 turns / segments。凡是"项目已经实现周期 / 频率"的说法都与源码矛盾。

### 1. 往复运动 / 重复运动

- **中文名称**：往复运动 / 重复运动
- **英文名称**：reciprocating motion / repetitive motion
- **初学者解释**：运动反复来回，同一种状态（例如到达峰、到达谷）在时间上再次出现。
- **VisionMotion 中的具体作用**：L12 产出的 turns 中，peak 与 valley 交替出现（EXP-004：f491 peak → f602 valley → f838 peak → f1063 valley → f1254 peak → f1513 valley），这就是"往复运动"在本项目里的最低证据形式。注意：**"看到往复"只说明存在重复结构，不等于"周期已成立"**（见第 6 条）。
- **源码位置**：`src\dynamic_displacement.py` 第 462–593 行（turns / segments 的产生）；第 540–563 行（turns 的 `kind` 与 `time_s`）。

### 2. 事件序列（turns 事件序列）

- **中文名称**：事件序列
- **英文名称**：event sequence
- **初学者解释**：把连续运动整理成一串"在什么时间、发生了什么类型的事件"的记录，例如"8.166327 s 发生 peak、10.012483 s 发生 valley"。
- **VisionMotion 中的具体作用**：turns 的每条记录都带 `time_s`（第 544 行）与 `kind`（第 555 行），因此 turns 天然构成事件序列；L13 的时间分析就只有一步——把两个 `time_s` 相减。**注意：`detect_turning_points()` 只产出这个序列，不负责对序列做间隔统计。**
- **源码位置**：`src\dynamic_displacement.py` 第 540–547、552–563 行。

### 3. 事件间隔

- **中文名称**：事件间隔
- **英文名称**：event interval
- **初学者解释**：两个转向事件之间相差多少秒，等于后一个事件的 `time_s` 减去前一个事件的 `time_s`。
- **VisionMotion 中的具体作用**：**当前 M5 源码没有实现事件间隔统计**：第 28 行声明不做周期分析；第 462–593 行只产出 turns / segments；打印部分（第 763、765–770、777–792、798–813 行）没有间隔输出。L13 的间隔数字（如 EXP-004 的 1.846156 s 等）来自对已有 CSV 的只读分析，不是项目功能。
- **源码位置**：边界证据 `src\dynamic_displacement.py` 第 28、462–593、763、765–770、777–792、798–813 行；间隔数字见 `docs\learning\L13_从运动段到往复运动.md` 第 11 节（只读分析）。

### 4. 半周期候选

- **中文名称**：半周期候选
- **英文名称**：half-period candidate
- **初学者解释**：相邻的异类事件之间的间隔——peak → valley 或 valley → peak，各代表"走了半个来回"的候选。
- **VisionMotion 中的具体作用**：EXP-004 的 5 个相邻间隔（1.846156 / 3.925159 / 3.742207 / 3.176718 / 4.307696 s）都是半周期候选；最小 1.846156 s、最大 4.307696 s、均值 3.399587 s、最大 / 最小约 2.33 倍——彼此并不一致（只读分析，非项目功能）。
- **源码位置**：素材来自 `src\dynamic_displacement.py` 第 540–563 行 turns 的 `time_s` / `kind`；统计本身见 `docs\learning\L13_从运动段到往复运动.md` 第 11.2 节（只读分析；当前源码未实现）。

### 5. 完整周期候选

- **中文名称**：完整周期候选
- **英文名称**：full-period candidate
- **初学者解释**：同类事件之间的间隔——peak → peak 或 valley → valley，各代表"走完一个完整来回"的候选。
- **VisionMotion 中的具体作用**：EXP-004 的 peak→peak = 5.771315 / 6.918925 s（均值 6.345120 s，仅 2 个样本）；valley→valley = 7.667366 / 7.484414 s（均值 7.575890 s，仅 2 个样本）；两者相对 2 × 半周期均值（6.799174 s）分别偏离约 −6.68% 与 +11.42%（只读分析，非项目功能）。
- **源码位置**：素材来自 `src\dynamic_displacement.py` 第 540–563 行；统计见 `docs\learning\L13_从运动段到往复运动.md` 第 11.3–11.4 节（只读分析；当前源码未实现）。

### 6. 周期 T

- **中文名称**：周期
- **英文名称**：period（T）
- **初学者解释**：往复运动完成一次完整来回所需要的时间；必须先证明"重复得足够一致"，周期值才可信。
- **VisionMotion 中的具体作用**：**当前 M5 源码没有实现周期计算**（第 28 行；第 4.8 节清单）。EXP-004 的只读分析结论是：可以确认存在明显的往复结构，但不能给出稳定、可信的正式周期值。M6 侧的 T = 0.542593 s 是外部公开视频（EXP-EXT-LAB67-V1）的冻结记录，被 `src\m63_final_visualization.py` 第 112–127 行 `FROZEN` 引用，**不是 M5 动态实验已实现的算法**。本课思想：先证明重复，再谈周期；先证明周期稳定，再谈频率。
- **源码位置**：`src\dynamic_displacement.py` 第 28、462–593 行；`src\m63_final_visualization.py` 第 7、112–127 行；`docs\M6.3_FINAL_REPORT.md` 第 154–169 行。

### 7. 频率 f

- **中文名称**：频率
- **英文名称**：frequency（f）
- **初学者解释**：单位时间内完成多少次完整来回；在周期稳定之后，才有"频率 = 1 / 周期"的说法。
- **VisionMotion 中的具体作用**：**当前 M5 源码没有实现频率计算**（第 28 行；`demo\run_m53_plot.py` 第 19、382 行也明确不计算）。M6 外部公开视频的冻结值 `f_exp = 1.843003`（= 1 / T_exp，M6 报告第 159 行）只属于 M6 数据链；本课只登记频率的定义与前置条件，不计算、不展开 FFT 等内容。
- **源码位置**：`src\dynamic_displacement.py` 第 28 行；`demo\run_m53_plot.py` 第 19、382 行；`src\m63_final_visualization.py` 第 112–127 行；`docs\M6.3_FINAL_REPORT.md` 第 159 行。

### 8. 周期稳定性判据

- **中文名称**：周期稳定性判据
- **英文名称**：period stability criterion
- **初学者解释**：判断"能不能宣布一个可信周期值"的检查清单，而不是某一个神奇公式。
- **VisionMotion 中的具体作用**：本课给出的判据思想（**概念解释，未实现**）：① 同类事件间隔是否一致；② 半周期与完整周期是否互相自洽；③ 样本数量是否足够；④ 数据是否来自同一段连续、可信的数据。EXP-004 在①②③上都不能通过（跨度约 2.33 倍；偏差 −6.68% / +11.42%；各只有 2 个整周期样本），所以本课不给正式周期值。当前源码中没有任何这样的检查代码（第 28 行边界 + 第 4.8 节清单）。
- **源码位置**：边界证据 `src\dynamic_displacement.py` 第 28、462–593 行；判据思想见 `docs\learning\L13_从运动段到往复运动.md` 第 10、15 节（概念解释；当前源码未实现）。

### 9. 冻结值（T_exp / f_exp）

- **中文名称**：冻结值（实验周期 / 实验频率）
- **英文名称**：frozen values（T_exp / f_exp）
- **初学者解释**：之前阶段已经封板、之后只允许读取与核对、不允许重新计算的数值。
- **VisionMotion 中的具体作用**：`src\m63_final_visualization.py` 第 112–127 行 `FROZEN` 中 `T_exp = 0.542593`、`f_exp = 1.843003`；第 7 行声明"不重新计算周期 / 频率 / 极值 / FFT"；第 110 行 `REPRESENTATIVE_INTERVAL = (150.0, 5.0000, 166.5, 5.5500, 0.550)` 是写死的字面量；第 202–219 行 `check_frozen_extrema_against_csv()` 只做封板值与 CSV 的一致性核对（容差 0.5），不做极值搜索、不做周期重新计算。这些冻结值属于 M6 外部公开视频数据链，不能套用到 EXP-004。
- **源码位置**：`src\m63_final_visualization.py` 第 7、109–110、112–127、202–219 行；`docs\M6.3_FINAL_REPORT.md` 第 154–169 行。

### 10. 运动段 ≠ 周期

- **中文名称**：运动段不等于周期
- **英文名称**：a segment is not a period
- **初学者解释**：一个运动段只描述"一个方向走了多远"；周期描述"完整来回一次要多久"，两者不是一回事。
- **VisionMotion 中的具体作用**：三条理由——① 首尾段可能被视频边界截断（`detect_turning_points()` docstring 第 478–479 行：首末帧只作为边界；EXP-004 段1 f0 → f491、段7 f1513 → f1765 各有一端是视频边界）；② 每个 segment 的 `direction` 只有一种取值（第 572–577 行），最多是半个来回；③ 周期应由同类事件之间定义（peak→peak / valley→valley），而段的边界是"起点 + 转向点 + 终点"（第 566 行），段与段交替方向，不能拿单段当周期。
- **源码位置**：`src\dynamic_displacement.py` 第 478–479、565–591 行（第 566、572–577、580–588 行）。

---

## 后续课程术语（尚未学习）

以下术语在 L01 中只作为"后续要学的内容"登记名称；其中 BGR / HSV / Mask / Morphology（形态学）/ Contour / Moments / Centroid 以及 `marker_detector.py` 源码已在 **L02** 学完并补入正文，视频逐帧追踪（`video_tracker.py`）已在 **L05** 学完并补入正文，逐帧结果写入 CSV 的字段设计与自检（`CSV_FIELDNAMES`、`build_csv_row`、`records`、`check_csv_data`）已在 **L06** 学完并补入正文，检测失败判定、失败表达、质量检查与鲁棒性（`marker_detector.py` 三道失败判定、`detect_marker()` 失败返回、`DETECTION FAILED`、九项自检、M6 独立质量检查、证据边界）已在 **L07** 学完并补入正文，Calibration（像素尺度标定、px/mm、mm/px、`compute_scale()`、`unit_direction()`、`project_point()`、`ds_px → ds_mm`、M4 / M5 冻结标定常量、无标定原则）已在 **L08** 学完并补入正文，标定的六步逐行讲解、原始方向向量与单位方向向量（归一化的三条理由）、点积与一维投影（`project_point()` 的"再次归一化"）、M4 / M5 方向常量（`U` / `U_004`）、六类材料与真实 CSV 的只读核对已在 **L09** 学完并补入正文，valid gate（第二道数据筛选）、位移基线 `s0`（`compute_s0()`、窗口与最少有效帧）、`ds_px` / `ds_mm` 的完整位移流程与三份真实 ds CSV 的只读复核已在 **L10** 学完并补入正文，位移符号语义（ds 的正负 / 大小）、运动方向判据（Δds）、正方向约定（P1 → P2）与 `MIN_TURN_TRAVEL_PX` 的最小认识已在 **L11** 学完并补入正文，转向点检测与运动段切分（`detect_turning_points()`、peak / valley、分析序列、状态机、direction、extreme_index、turn_indexes、20 px 反向行程阈值、确认帧、turns、describe、direction_before / direction_after、运动段、boundary_indexes、travel_px、below_min_travel、原始数据原则、冻结与可复现）已在 **L12** 学完并补入正文，往复运动 / 重复运动、事件序列、事件间隔、半周期候选、完整周期候选、周期稳定性判据思想（以及 M6 冻结值 T_exp / f_exp 的对照记录）已在 **L13** 学完并补入正文（**注意：周期 / 频率在项目中仍未实现计算**），本清单只保留仍未学习的部分：

周期 / 频率（L13 已建立概念与判据思想，并记录 M6 外部公开视频的冻结值；但项目代码仍未实现周期 / 频率计算）

FFT / 频谱、简谐振动（仍未学习，L13 只登记名称，不展开）

---

### 维护说明

- L09 词条（原始方向向量、单位方向向量、归一化、compute_scale 六步、unit_direction 完整展开、project_point 完整展开与再次归一化、点积、有号投影长度、ux / uy 的几何意义、正交分解、U、U_004、六类材料、只读核对、s_px 是坐标不是位移）的事实来自 `src\calibration.py` 第 9～10、24、100～144（第 118～120、122～126、128～131、134～135、137～138、140～144 行）、147～173（第 149、166～168、170～171、173 行）、176～204（第 180、193～194、196～202、204 行）行，`src\displacement.py` 第 41～55（第 48～50、52～53、55 行）、111～112、128～141、277～285 行，`src\dynamic_displacement.py` 第 20～23、40、59～66（第 60～62、64～65、66 行）、138～172（第 138～144、147～157、167～172 行）行；真实数据（只读核对，未重新生成、未修改，统计口径：`s_px` 非空才参与复算）来自 `results\EXP-003-STATIC-002_track.csv`（1961 行、frame 0～1960）与 `results\EXP-003-STATIC-002_ds.csv`（有 `s_px` 的行 1050；加归一化后最大偏差 4.974e-4 px；最小二乘拟合系数与 U / |U| 一致到 1e-7 量级），`results\EXP-004-DYNAMIC-001_track.csv`（1766 行、frame 0～1765）与 `results\EXP-004-DYNAMIC-001_ds.csv`（`s_px` 全部有值 1766 行；加归一化后最大偏差 4.998e-4 px）（按 2026-10-02 当前源码与产物逐行核对）；未重新运行任何程序。
- L10 词条（valid gate、is_valid_frame、detected 与 valid 的区别、无效帧留空、s0、compute_s0、S0_WINDOW_S / MIN_S0_VALID_FRAMES、位置与位移、ds_px 补充视角、ds_mm 补充视角、双重舍入补充视角、有效性统计字段、数据依赖链、s0 不达标不写 ds CSV）的事实来自 `src\displacement.py` 第 21～22、57～68、72～90、175～201、261～274、277～285、288～325（第 304～305、307～320、318、322～323 行）、328～340（第 339～340 行）、348～366（第 355、360～363 行）、390～431（第 405～413、420～427 行）、506～517、568～761（第 686～689、703～722、724～742 行）、769～811（第 781、793～796 行）行，`src\dynamic_displacement.py` 第 20～23、27、68～76、78～80、91～109、183～210、270～284、286～294、297～335（第 314～315、328、332～333 行）、338～350（第 349～350 行）、358～376（第 370～372 行）、400～454（第 437～450 行）、902～1139（第 1048～1053、1073～1094、1096～1116 行）、1147～1191（第 1159、1171～1174 行）、1194～1224（第 1215～1217 行）行；真实数据（只读核对，未重新生成、未修改）来自 `results\EXP-003-STATIC-002_ds.csv`（1961 行、valid 1050 / invalid 911、s0 = 1076.063871 px、ds_px −1.249～350.268、ds_mm −0.2170～60.8426、frame 0 行 `0,0.000000,1080.399,4.335,0.7530,4783.0,True,True`）、`results\EXP-003-STATIC-003_ds.csv`（1984 行、valid 1192 / invalid 792、s0 = 1077.364097 px、ds_px −0.311～346.530、ds_mm −0.0540～60.1932、frame 0 行 `0,0.000000,1077.528,0.164,0.0284,4394.5,True,True`）、`results\EXP-004-DYNAMIC-001_ds.csv`（1766 行、valid 1766 / invalid 0、s0 = 855.202603 px、ds_px −3.215～402.715、ds_mm −0.5283～66.1663、frame 0 行 `0,0.000000,851.987,-3.215,-0.5283,5713.0,True,True`）及对应三份 `_track.csv`（行数 1961 / 1984 / 1766、detected 全部 True；被拒帧例证 frame 52 / frame 35；公式复算最大偏差 ds_px ≤ 0.000904 px、ds_mm ≤ 0.000151 mm）（按 2026-10-02 当前源码与产物逐行核对）；未重新运行任何程序。
- L12 词条（转向点、detect_turning_points、分析序列（analysis_rows / analysis_invalid_rows）、原始 x_px 序列、状态机（zigzag）、direction、extreme_index、turn_indexes、MIN_TURN_TRAVEL_PX 反向行程阈值、确认帧与确认滞后、peak / valley、turns / describe、direction_before / direction_after、运动段 / boundary_indexes、travel_px、below_min_travel、边界点、原始数据原则、冻结与可复现）的事实来自 `src\dynamic_displacement.py` 第 16、20～23、27～30、85～87、228～262、462～593 行（重点：467～468、474～477、478～479、480～481、495～498、500～510、512～538、540～547、549～550、552～563、565～591、588、740～814 行）与 `demo\run_m53_plot.py` 第 15～19、67～74 行；真实数据（只读核对，未重新生成、未修改）来自 `results\EXP-004-DYNAMIC-001_track.csv` 与 `results\EXP-004-DYNAMIC-001_ds.csv`（各 1766 行、frame 0～1765、detected / valid 全部 True；`analysis_rows = 1766`、`analysis_invalid_rows = 0`；6 个转向点 f491 peak (t 8.166327, x 1057.86, ds_mm 33.1549)、f602 valley (10.012483, 973.06, 19.2217)、f838 peak (13.937642, 1099.23, 39.9535)、f1063 valley (17.679849, 1007.01, 24.7998)、f1254 peak (20.856567, 1197.10, 56.0319)、f1513 valley (25.164263, 1068.30, 34.8700)；7 个运动段 travel_px = 205.05 / 84.80 / 126.17 / 92.22 / 190.09 / 128.80 / 188.61 px，below_min_travel 全为 False；按第 512～538 行只读内存复算的确认帧：f491→f505、f602→f732、f838→f971、f1063→f1156、f1254→f1346、f1513→f1535）（按 2026-10-04 当前源码与产物逐行核对）；未重新运行任何程序。
- 词条中的项目事实来自仓库内实际文件（`results\EXP-EXT-LAB67-V1_trajectory.csv`、`README.md`、`src\external_oscillation_tracker.py` 等），未修改任何代码、数据或实验结果。
- L02 词条（BGR、HSV、Hue、Saturation、Value、Mask、Threshold、Morphological Opening、Erosion、Dilation、Contour、Moments、Centroid、Bounding Rectangle、Binary Image、Kernel、Channel）的参数与代码事实来自 `src\marker_detector.py`，未重新运行任何程序。
- L03 词条（Pixel 补充视角、NumPy Array、Image、BGR 补充视角、RGB、HSV 补充视角、Hue / Saturation / Value 补充视角、Color Space、Threshold 补充视角、Mask 补充视角、Binary Image 补充视角、cv2.cvtColor、cv2.inRange、bitwise_or、Contour 补充视角）的事实来自 `src\marker_detector.py` 第 22～27、48、51～52、55、73、110 行附近；未重新运行任何程序。
- L04 词条（Contour 补充视角、findContours、RETR_EXTERNAL、CHAIN_APPROX_SIMPLE、Contour Area、Moments 补充视角、m00、m10、m01、Centroid 补充视角、Bounding Rectangle 补充视角、MIN_AREA）的事实来自 `src\marker_detector.py` 第 33、73、75～76、78～80、82～84、95、97～98、100～102、140、141 行附近（按 2026-09-29 当前源码逐行核对）；未重新运行任何程序。
- L05 词条（Video、Frame 补充视角、FPS 补充视角、VideoCapture、cap.read、ret、current_frame、VideoWriter、Overlay Video、release、Frame Loop、Function Reuse、Module）的事实来自 `src\video_tracker.py` 第 15～23、34、44、47、119～125、147、169～201、236～252、365、431～435、438、474～475、482～491、507～515、521～526、530～538 行附近与 `demo\run_video_tracking.py` 第 35、38、43、52～58 行（按 2026-09-29 当前源码逐行核对，`src\video_tracker.py` 共 760 行）；未重新运行任何程序。
- L06 词条（Row、Column、Header、Cell、CSV_FIELDNAMES、build_csv_row、writerow、lineterminator、records、Missing Value、Discrete Time Series、Field Design、np.genfromtxt、csv.DictWriter、y_px、_track.csv / _trajectory.csv，以及 Frame / time_s / x_px / area_px / detected / CSV 六个补充视角）的事实来自 `src\video_tracker.py` 第 26、40～41、124、387～404、470、477～479、488、491、493～504、637～748 行与 `src\external_oscillation_tracker.py` 第 86～96、220～221、302～304、337～377、494～500 行；产物数据（只读核对，未重新生成）来自 `results\EXP-002-VIDEO-001_track.csv`（表头 6 列、952 行数据）与 `results\EXP-EXT-LAB67-V1_trajectory.csv`（表头 8 列、160 行数据）（按 2026-10-02 当前源码与产物逐行核对）；未重新运行任何程序。
- L07 词条（Detection Failure、success、DETECTION FAILED、失败返回结构、空字段、`(0,0)` 伪数据、detection_rate、longest_miss_run、Quality Check、Robustness、Evidence Boundary）的事实来自 `src\marker_detector.py` 第 33、75～76、83～84、97～98、129、132～133、136～137、143～151 行与 `src\video_tracker.py` 第 190～201、387～404、470、483～526、556～580、585～598、606～629、637～748 行，M6 对照来自 `src\external_oscillation_tracker.py` 第 422～505 行；产物数据（只读核对，未重新生成、未修改）来自 `results\EXP-002-VIDEO-001_track.csv`（952 行、952/952 全 True、0 失败行、0 空字段、area 4673.0 / 5265.0 / 6061.5）与 `results\EXP-EXT-LAB67-V1_trajectory.csv`（160 行、160/160 全 True、0 失败行、0 空字段、area 226 / 508.5 / 658）（按 2026-10-02 当前源码与产物逐行核对）；未重新运行任何程序。
- L08 词条（Calibration、图像坐标系 / 物理世界坐标系、px/mm、mm/px、pixel_distance、compute_scale、已知真实长度、M4 冻结标定常量、M5 冻结标定常量、unit_direction、project_point、s_px、ds_px、ds_mm、无标定原则、y0_px 字段名读法）的事实来自 `src\calibration.py` 第 1～22、24、32～43、46～70、73～92、100～144（第 125～126、128～131、134～135、137～138、140～144 行）、147～173、176～204 行，`src\displacement.py` 第 23、41～55（第 48～50、52～53、55 行）、57～64、72～90、98～150、277～340（第 339～340 行）、348～382、725～740 行，`src\dynamic_displacement.py` 第 20～23、40、59～66（第 60～62、64～65、66 行）、68～76、78～80、91～109、121～174、338～350（第 349～350 行）、1097～1116 行，以及 `src\external_oscillation_tracker.py` 第 31～34、84、87～96 行；产物数据（只读核对，未重新生成、未修改）来自 `results\EXP-003-STATIC-002_ds.csv`（1961 行、valid 1050/911、ds_px -1.249～350.268、ds_mm -0.2170～60.8426）、`results\EXP-003-STATIC-003_ds.csv`（1984 行、valid 1192/792、ds_px -0.311～346.530、ds_mm -0.0540～60.1932）、`results\EXP-004-DYNAMIC-001_ds.csv`（1766 行、valid 1766/0、ds_px -3.215～402.715、ds_mm -0.5283～66.1663）与 `results\EXP-EXT-LAB67-V1_trajectory.csv`（表头 8 列、160 行、x_px 718.5～728.0、y0_px 508～622）（按 2026-10-02 当前源码与产物逐行核对）；未重新运行任何程序。
- 新增术语时请保持五字段格式（中文名称 / 英文名称 / 初学者解释 / VisionMotion 中的具体作用 / 源码位置），并在"速查索引"中同步登记。

- 记录日期：2026-09-28；L04 记录日期：2026-09-29；L05 记录日期：2026-09-29；L06 记录日期：2026-10-02；L07 记录日期：2026-10-02；L08 记录日期：2026-10-02；L09 记录日期：2026-10-02；L10 记录日期：2026-10-02；L11 记录日期：2026-10-04；L12 记录日期：2026-10-04；L13 记录日期：2026-10-04；当前已登记课程：L01、L02、L03、L04、L05、L06、L07、L08、L09、L10、L11、L12、L13。
- L11 词条（Δds、运动方向（正向 / 负向）、正方向约定（P1 → P2）、参考位置与符号侧、符号统计、平台 + 台阶 + 空洞、连续往返、MIN_TURN_TRAVEL_PX 最小认识、五类材料）的事实来自 `src\displacement.py` 第 44～46、55、272～274、284～285、338～340、360～363 行与 `src\dynamic_displacement.py` 第 30、59～66、82～87、111～113、133、462、474～477、480～481 行；真实数据（只读核对，未重新生成、未修改）来自 `results\EXP-003-STATIC-002_ds.csv`、`results\EXP-003-STATIC-003_ds.csv`、`results\EXP-004-DYNAMIC-001_ds.csv` 及对应三份 `_track.csv`（valid 1050/911、1192/792、1766/0；`ds_mm` −0.2170～60.8426 / −0.0540～60.1932 / −0.5283～66.1663；正/负/零 = 1016/34/0、1174/18/0、1605/161/0；M5 f237→f313 与 f963→f1015 两条方向例子；平台 / 空洞统计 180 / 147 帧）（按 2026-10-04 当前源码与产物逐行核对）；未重新运行任何程序。
- L13 词条（往复运动 / 重复运动、事件序列、事件间隔、半周期候选、完整周期候选、周期 T、频率 f、周期稳定性判据、冻结值（T_exp / f_exp）、运动段 ≠ 周期）的事实来自 `src\dynamic_displacement.py` 第 16、28、30、462–593 行（重点：540–547、552–563、565–591、763、765–770、777–792、798–813 行）、`src\m63_final_visualization.py` 第 7、109–110、112–127、202–219 行、`demo\run_m53_plot.py` 第 19、67–74、382 行，旁证 `src\video_tracker.py` 第 17、608–609 行与 `src\external_oscillation_tracker.py` 第 31–33、407、611 行，M6 对照 `docs\M6.3_FINAL_REPORT.md` 第 154–169 行；真实数据（只读核对，未重新生成、未修改）来自 `results\EXP-004-DYNAMIC-001_track.csv` 与 `results\EXP-004-DYNAMIC-001_ds.csv`（各 1766 行、frame 0–1765；6 个转向点时间 f491 8.166327 / f602 10.012483 / f838 13.937642 / f1063 17.679849 / f1254 20.856567 / f1513 25.164263 s；5 个半周期候选 1.846156 / 3.925159 / 3.742207 / 3.176718 / 4.307696 s，最小 1.846156、最大 4.307696、均值 3.399587、最大 / 最小 ≈ 2.33；peak→peak 5.771315 / 6.918925 s，均值 6.345120；valley→valley 7.667366 / 7.484414 s，均值 7.575890；2 × 半周期均值 6.799174 s；偏差 ≈ −6.68% / +11.42%）；上述间隔数字均为只读分析结果（内存中读取与计算，未写任何文件），不是当前项目代码已经实现的功能；只读检索显示全项目 M5.4 / M5.5 命中 0 条（按 2026-10-04 当前源码与产物逐行核对）；未重新运行任何程序。

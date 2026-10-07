# L06 从逐帧结果到 CSV：数据记录、字段设计与时间序列

> - 课程编号：L06
> - 课程标题：从逐帧结果到 CSV：数据记录、字段设计与时间序列
> - 学习状态：已完成
> - 记录日期：2026-10-02
> - 适用对象：正在从零开始学习计算机视觉的本科生
> - 前置课程：L01（VisionMotion 项目、CSV 与时间序列）、L02（marker_detector.py：从图片到目标中心）、L03（像素、颜色空间与 Mask）、L04（Contour、Moments 与 Centroid）、L05（从单张图片到视频：逐帧处理）
>
> 本笔记整理第 6 课：L05 已经让程序"每一帧都能检测"，
> 但检测结果只是循环里的一个临时变量 `result`——循环进入下一轮，上一帧的结果就被覆盖。
> 本节把"逐帧结果"升级为"可长期保存、可被别的程序读取、可回看核对的数据"：
> 用 `CSV_FIELDNAMES`（第 41 行）定义字段，用 `build_csv_row()`（第 393～410 行）把一帧结果变成一行，
> 用 `csv.writer` 在 `track_video()`（第 413 行起）里边检测边写入 `<视频名>_track.csv`，
> 同时用内存里的 `records`（第 476、499～510 行）做运行期统计与自检（第 562～586、591～604、643～824 行）。
> 本节还对比 M3 的 `_track.csv` 与 M6 的 `_trajectory.csv` 的共同设计思想与字段差异。
> Calibration、位移、FFT、频率 / 周期等仍属于后续课程，本笔记不展开；`external_oscillation_tracker.py` 的检测算法细节也不展开。
>
> 本笔记中所有 M3 源码事实均来自 `src\video_tracker.py`（共 836 行），行号按 2026-10-07 当前源码逐行核对；
> M6 对照事实来自 `src\external_oscillation_tracker.py`（共 661 行）与仓库内真实产物 CSV（只读核对，未重新生成）；
> 如果实际源码行号发生变化，以当前真实源码为准（见第 15 节与文末说明）。

## 1. 本节课学习目标

学完本节课，应该能够：

- 说清为什么逐帧结果不能只留在单个 `result` 变量里：`result` 每轮被覆盖，程序结束后内容消失，历史必须"另找地方记账"；
- 说清 CSV 的基本结构：纯文本表格、逗号分隔、第一行是表头，并准确使用 row（行）、column（列）、header（表头）、cell（单元格）四个词；
- 背出 M3 的真实字段定义 `CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`（第 41 行）并逐字段解释含义与数值来源；
- 读懂 `build_csv_row()`（第 393～410 行）如何把 `(frame_index, time_s, result)` 变成一行 6 个字段的 CSV 数据，并说出成功行与失败行各自的格式；
- 说出检测失败时 CSV 的正确表达方式：`detected=False`、其余测量字段留空；能解释为什么**不写 0、-1、上一帧坐标，也不写 nan 字符串**（第 399、410 行）；
- 按顺序复述 `track_video()`（第 413 行起）里 CSV 的完整生命周期：打开文件（第 483 行）→ 写表头（第 485 行）→ 循环里每帧写一行（第 497 行）→ `finally` 里关闭文件（第 541 行）；
- 区分运行期内存里的 `records`（第 476、499～510 行）与磁盘上的 CSV：一个用于统计与自检，一个用于长期保存与交换；
- 说出 `records` 如何被统计使用：`summary` 统计字典（第 562～586 行）与 `compute_longest_miss_run()`（第 591～604 行）；
- 说出 `check_csv_data()`（第 643～824 行）检查了哪些内容（表头、行数、frame 连续性、成功行的合法性、失败行留空、无 (0,0) 伪数据、`time_s` 时间轴一致性、CSV 空测量字段与 `detected=False` 的语义对账），理解"写出来"不等于"可信"；
- 解释 CSV 如何构成离散时间序列：每行一个采样时刻 `time_s = frame_index / fps`（第 494 行），失败行保持时间轴完整、把缺失明确标记出来；
- 说出 M3 的 `_track.csv` 与 M6 的 `_trajectory.csv` 的共同设计思想（第一行真表头、frame/time_s/detected、失败留空 + False、写回自检）与字段差异（6 列 vs 8 列、质心 vs 暗带上缘、全片 vs 正式分析区间）；
- 明确区分三类材料：VisionMotion 真实源码、教学伪代码、教学示例；引用项目事实时必须给出"文件路径 + 函数名 + 行号"。

## 2. 为什么逐帧结果不能只留在 result 变量里

L05 的主循环里，每一帧做完检测后得到的那个变量就是 `result`：

```python
# src\video_tracker.py::track_video() 主循环内（当前约第 491 行）
result = detect_marker(current_frame)
```

这个变量回答的是"**当前这一帧**里目标在哪里"（它的 `success` / `cx` / `cy` / `area` / `bbox` 等字段来自 L02～L04 学过的 `detect_marker()`）。但它有三个无法回避的局限：

1. **每一个循环轮次都会覆盖它。** `result = detect_marker(current_frame)`（当前约第 491 行）每执行一次，`result` 就整体换成新一帧的检测结果；上一帧的结果不会自动保留在任何地方。
2. **循环结束后它只剩最后一帧。** 就算程序正常跑完，内存里的 `result` 也只代表最后处理的那一帧，前面 169 帧（M3 视频共处理 170 帧）的结果全部不可找回。
3. **程序退出后它彻底消失。** 变量属于运行中的进程；程序结束（或崩溃、或按 Ctrl+C）之后，没有任何文件留下，别的程序也无从读取。

所以"逐帧结果"必须有两个去处，二者**分工不同、同时存在**：

| 去处 | 载体 | 生命周期 | 作用 |
| --- | --- | --- | --- |
| 运行期账本 | `records` 列表（第 476 行创建，第 499～510 行追加） | 只在本次运行的内存里 | 给程序自己统计、自检、挑选代表性画面用 |
| 长期数据文件 | CSV 文件（第 483 行打开，第 497 行逐行写入） | 写在磁盘上，可长期保存 | 给人核对、给后续程序读取、给未来分析当输入 |

一句话总结本节的问题意识：

> **`result` 是"当前这一帧"的答案，不是"整段视频"的记录；想让测量结果活过这一次循环、活过这一次运行，就必须把它逐帧写进一个持久化的数据文件——这个文件就是 CSV。**

## 3. CSV 的基本结构：row / column / header / cell

### 3.1 CSV 是什么

CSV = Comma-Separated Values（逗号分隔值）：一种**纯文本**表格文件。它没有颜色、没有公式、没有数据类型，只有一行一行的文字；每一行用逗号切成若干字段。

### 3.2 用真实产物认识四个名词

打开 M3 的真实产物 `results\EXP-002-VIDEO-001_track.csv`（本笔记只读核对，未重新生成），前 3 行是：

```text
frame,time_s,x_px,y_px,area_px,detected
0,0.000000,618.28,160.56,75863.0,True
1,0.041667,625.75,159.42,74839.5,True
```

用这 3 行就能把四个名词全部对上：

| 名词 | 中文 | 在上面的文件里指什么 |
| --- | --- | --- |
| header | 表头 | 第 1 行 `frame,time_s,x_px,y_px,area_px,detected`：说明每一列是什么 |
| row | 行 | 第 2 行 `0,0.000000,...`：一条完整记录 = 一帧的一次测量 |
| column | 列 | 例如所有行的 `time_s` 组成一列；M3 共 6 列 |
| cell | 单元格 | 某一行与某一列交叉的那一个值，例如第 2 行的 `time_s` 单元格是 `0.000000` |

要强调的三件事：

1. **表头就在文件的第一行，它不是数据行。** 项目两份 CSV 的写法完全一致：`src\video_tracker.py` 第 40 行注释与 `src\external_oscillation_tracker.py` 第 87 行注释都写明"CSV 表头：第一行就是真正的表头，前面不加任何 metadata"。所以读文件时第一行要当表头解析，不能当数据。
2. **CSV 里一切都是文本。** `0.000000`、`75863.0`、`True` 都是字符串；`True` / `False` 不是 Python 布尔值本身的存储形式，而是项目约定写入的文本（见第 6 节）。类型是读文件的一方后来解释出来的。
3. **列名是唯一稳定的定位方式。** 列的顺序由写出方决定（M3 见第 41 行），读的一方应当按表头名字找列，而不是按"第几列"背下来（见第 11 节两份文件的列顺序差异）。

### 3.3 字段名的命名规律

M3 的 6 个字段名都是小写下划线风格，并且用后缀提示单位或含义：

- `_px`：单位是像素（`x_px`、`y_px`、`area_px`；稍后在 M6 里还有 `bbox_w_px`、`bbox_h_px`）；
- `_s`：单位是秒（`time_s`）；
- `frame`、`detected`：计数与标志，无单位。

## 4. CSV_FIELDNAMES：M3 的六个字段

### 4.1 源码定位

- **文件**：`src\video_tracker.py`
- **位置**：模块级常量，第 41 行（常量区，第 40 行是它的注释）
- **原代码**：

```python
# src\video_tracker.py 第 41 行
CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]
```

- **作用**：定义这张 CSV 的**列名与列顺序**。它同时被三处使用：
  1. 第 485 行 `csv_writer.writerow(CSV_FIELDNAMES)`——写出真正的第一行表头；
  2. `build_csv_row()`（第 393～410 行）返回的列表必须按同样的顺序排好 6 个字段（否则行列错位）；
  3. `check_csv_data()`（表头第 670～671 行、每行列数第 681、704、749、800 行）用它与实际文件对比，验证"表头没被改过、每行列数正确"。

### 4.2 六个字段逐个解释

| 列号 | 字段名 | 含义 | 数值来源（真实源码位置） | 写出格式 |
| --- | --- | --- | --- | --- |
| 1 | `frame` | 帧编号（从 0 开始、逐帧 +1 的整数） | `frame_index`：第 481 行初始化为 0，第 531 行每读入下一帧后 `+= 1` | 整数，直接写入（第 403 行） |
| 2 | `time_s` | 该帧在视频时间轴上的时刻，单位秒 | 第 494 行 `time_s = frame_index / fps`；fps 由第 130 行从视频文件读取、未硬编码 | 字符串 `"%.6f"`（6 位小数，第 404、410 行） |
| 3 | `x_px` | 红色标记**质心**的水平像素坐标 | `result["cx"]`（第 405 行取值；`cx` 来自 L04 学过的 `marker_detector.py` 质心公式 `cx = m10 / m00`） | 字符串 `"%.2f"`（2 位小数） |
| 4 | `y_px` | 红色标记**质心**的竖直像素坐标 | `result["cy"]`（第 406 行取值；对应 `cy = m01 / m00`，L04） | 字符串 `"%.2f"`（2 位小数） |
| 5 | `area_px` | 红色标记轮廓的面积（像素面积） | `result["area"]`（第 407 行取值；来自 `marker_detector.py` 第 140 行 `cv2.contourArea(contour)`，L04） | 字符串 `"%.1f"`（1 位小数） |
| 6 | `detected` | 这一帧是否检测成功 | `result["success"]`（第 401 行在 `build_csv_row()` 里判断并在第 408 / 410 行成文；第 502 行同时在 `records` 里记账） | 文本 `True` / `False` |

几个必须记住的细节：

1. **`x_px` / `y_px` 记录的是 L04 的质心 `(cx, cy)`**，不是外接矩形中心、不是左上角、也不是面积中心之外的其他定义。
2. **`area_px` 来自 `cv2.contourArea`**，是轮廓几何面积（L04 已强调：它不等于"数 Mask 中 255 像素的个数"）。
3. **`frame` 是"第几帧"，`time_s` 是"第几秒"**；两者靠 fps 换算（L01 / L05 已学，本节把它写成 CSV 的前两列）。
4. **`detected` 是"测量是否有效"的标志**，不是运动信号本身；它和 `x_px` / `y_px` / `area_px` 一起构成"一条完整的测量记录"。
5. **`CSV_FIELDNAMES` 是唯一的"列清单"**：要加列、删列、改列名，都必须先改第 41 行，再同步 `build_csv_row()` 与自检逻辑——这是"字段设计"的中心思想。

## 5. build_csv_row()：把一帧结果变成一行

### 5.1 源码定位

- **文件**：`src\video_tracker.py`
- **函数**：`build_csv_row(frame_index, time_s, result)`，第 393～410 行
- **原代码（成功 / 失败两条分支）**：

```python
# src\video_tracker.py::build_csv_row()（当前约第 393～410 行）
def build_csv_row(frame_index, time_s, result):
    """
    构造一行 CSV 数据。

    检测成功：frame, time_s(6 位小数), x(2 位), y(2 位), area(1 位), True
    检测失败：frame, time_s(6 位小数), 空, 空, 空, False
    失败时绝不写 0 / -1 / nan / 字符串。
    """
    if result["success"]:
        return [
            frame_index,
            "%.6f" % time_s,
            "%.2f" % result["cx"],
            "%.2f" % result["cy"],
            "%.1f" % result["area"],
            "True",
        ]
    return [frame_index, "%.6f" % time_s, "", "", "", "False"]
```

### 5.2 这个函数做了什么

它只做一件事：**把"一帧的三样东西"（帧号、时间、检测结果字典）翻译成"CSV 需要的一行 6 个值"**，并且严格遵守 `CSV_FIELDNAMES` 的顺序。它**不打开文件、不写文件、不参与循环**——这是 L02～L05 一直强调的"一个函数只做一件明确的小事"的延续。

| 输入 | 来源 | 说明 |
| --- | --- | --- |
| `frame_index` | 第 481、531 行 | 0 开始的帧编号 |
| `time_s` | 第 494 行 `frame_index / fps` | 秒为单位的时刻 |
| `result` | 第 491 行 `detect_marker(current_frame)` | L02～L04 的检测结果字典 |

| 输出 | 去向 | 说明 |
| --- | --- | --- |
| 6 个值的列表 | 第 497 行 `csv_writer.writerow(build_csv_row(...))` | 被 `csv.writer` 原样写成一行文本 |

### 5.3 格式设计：为什么写成字符串

- `"%.6f" % time_s`：时间保留 6 位小数。这样 30 fps 的 `1/30 s ≈ 0.033333`、M3 视频的 `0.041667` 在文件里都有稳定的写法；
- `"%.2f" % result["cx"] / ["cy"]`：坐标保留 2 位小数（亚像素精度够用，也不至于让文件充满无意义的长小数）；
- `"%.1f" % result["area"]`：面积保留 1 位小数；
- `"True"` / `"False"`：明确写成文本，与文件里其他内容保持"纯文本"的一致性。

### 5.4 一个容易忽略的事实

`build_csv_row()` 的 docstring（第 394～400 行）本身就是项目设计文档：第 397～398 行写成功 / 失败两种行的格式，第 399 行写下失败行的硬性原则：

> **失败时绝不写 0 / -1 / nan / 字符串。（第 399 行）**

## 6. 成功与失败：CSV 里的两种行

### 6.1 成功行

检测成功时，6 个字段全部填写：`frame`、`time_s` 照常，`x_px` / `y_px` / `area_px` 填真实测量值，`detected` 写 `True`（第 401～409 行）。

真实产物示例（来自 `results\EXP-002-VIDEO-001_track.csv`，只读摘录）：

```text
frame,time_s,x_px,y_px,area_px,detected
0,0.000000,618.28,160.56,75863.0,True
```

读法：frame 0（t = 0.000000 s）这一帧检测成功，质心在 (618.28, 160.56) px，轮廓面积 75863.0（像素面积）。

### 6.2 失败行

检测失败时（`result["success"]` 为 `False`），`build_csv_row()` 走第 410 行：

```python
return [frame_index, "%.6f" % time_s, "", "", "", "False"]
```

即：

| frame | time_s | x_px | y_px | area_px | detected |
| --- | --- | --- | --- | --- | --- |
| 照常填写 | 照常填写 | **留空（空字符串）** | **留空** | **留空** | `False` |

关键点：**失败行也要写，且 frame 与 time_s 必须照常填写**。第 496～497 行的注释写得很直白：

```python
# ---- 写 CSV：每帧一行，检测失败也要写 ----
csv_writer.writerow(build_csv_row(frame_index, time_s, result))
```

教学示例（人为构造、不是项目数据）——假设 60 fps 视频的 frame 4 检测失败：

```text
4,0.066667,,,,False
```

"测量不到"本身也是关于这段视频的重要信息；把这一行如实写下来，时间轴才完整，后面统计和自检才有依据。

### 6.3 为什么失败时是"留空 + False"，而不是 0、-1、上一帧坐标

这是一个**数据诚信**问题，也是本节最重要的设计决策之一。

| 错误写法 | 后果 |
| --- | --- |
| 写 `0`（例如 x=0, y=0） | 0 是一个"看起来合法"的坐标（像素 (0,0) 是画面左上角）；画曲线、算平均、找极值时会被当成真实的测量值参与计算，凭空制造出"目标跳到左上角"的假事件。自检程序因此专门检查"不存在 x=0, y=0 伪数据"（第 726～727、738 行）。 |
| 写 `-1` | 同样是一个数字，会被后续程序当成坐标读进去；负数坐标在图像坐标系里没有意义，但程序不会自动报错。 |
| 写 `nan` / `NaN` 字符串 | "nan" 是文本，谁读谁要自己解释；而且它和"空白"在文件里的含义就重复了，读数工具对两种写法的处理还可能不一致。 |
| 沿用**上一帧**的坐标 | 最隐蔽的一种：数据表面上"完整又平滑"，但那是**伪造的测量**——它掩盖了真实发生的丢失，还会把运动曲线抹平、扰动后面的位移与频率分析。 |
| 干脆这一行不写 | 时间轴会断裂：行号与帧号对不上，别人无法知道"是这帧没测到，还是这帧根本不存在"。 |

项目的选择是：

- **测量字段留空**：明确表示"没有值"，而不是"值为 0"；
- **`detected=False`**：明确表示"这一时刻的测量无效"；
- **绝不写 0 / -1 / nan / 字符串**（第 399 行原则）；
- **每一帧仍然占一行**（第 496 行注释），保持时间轴连续。

留空还有一个"机器可读"的证明：第 794～818 行的自检（`check_csv_data()` 第 6 组）用 `csv.reader` 读回的**文本视角**对账：空测量字段（`x_px` 为空）的行数必须等于 `detected=False` 的行数（第 817 行汇总判定），即"文本视角的空"与"失败标志"必须一一对应——也就是说，"空白"在数据世界里会被解释为"缺失值"，这正是我们想要的语义。

一句话总结：

> **测不到，就明确标记缺失，而不是制造一个假测量。**

## 7. track_video()：整张 CSV 是怎么生成的

### 7.1 源码定位

- **文件**：`src\video_tracker.py`
- **函数**：`track_video(video_path, csv_path, overlay_path)`，第 413～588 行（第 413 行为函数定义）
- **作用**：逐帧追踪主流程——读取完整视频、每帧 `detect_marker`、写 CSV、生成可视化；返回统计字典 `summary`；视频无法打开时返回 `None`（第 417、433～435 行）。

### 7.2 准备阶段（第 419～467 行）

| 位置 | 代码做的事 |
| --- | --- |
| 第 419～425 行 | 把三个路径转成 `Path`，`mkdir(parents=True, exist_ok=True)` 保证结果目录存在 |
| 第 428 行 | `sha256_before = compute_sha256(video_path)`：运行前给原始视频算指纹（只读，不改视频） |
| 第 430 行 | 开始计时 `time.perf_counter()` |
| 第 432 行 | `cap, video_info = open_video(video_path)` 打开视频（L05 的 `open_video`，第 119 行起） |
| 第 437～441 行 | fps 非法（≤ 0）就释放并报错退出——因为 `time_s` 依赖 fps，必须先保证它合法 |
| 第 444 行 | 先读第一帧 `ret, first_frame = cap.read()`，用于确定实际画面尺寸（第 452～463 行） |
| 第 465～467 行 | 打开叠加视频写入器（失败则走 PNG 回退，与 CSV 无关） |

### 7.3 账本初始化（第 476～481 行）

```python
# src\video_tracker.py::track_video() 第 476～481 行
records = []          # 每帧一条记录，用于统计与自检
sharpness_list = []   # 每帧清晰度指标（只在回退方案中使用）
detected_count = 0
area_list = []
current_frame = first_frame
frame_index = 0
```

这里同时开了"两套账"：

- `records`：**每帧一条**的明细账（本节重点，见第 8 节）；
- `detected_count`、`area_list`：**运行中的累计量**（检出计数、成功帧的面积列表），供最后统计使用（第 562～586 行）。

`frame_index` 从 0 开始，并且第一帧已经在第 444 行读好、第 480 行交给 `current_frame`——所以第一帧不会被浪费，CSV 的第一行就是 frame 0。

### 7.4 打开 CSV、创建 writer、写表头（第 483～485 行）

```python
# src\video_tracker.py::track_video() 第 483～485 行
csv_file = open(csv_path, "w", encoding="utf-8", newline="")
csv_writer = csv.writer(csv_file, lineterminator="\n")
csv_writer.writerow(CSV_FIELDNAMES)
```

三个细节：

1. `"w"` 模式：每次运行**重新写**一个新的 CSV（覆盖同名旧文件）；
2. `encoding="utf-8"` 与 `newline=""`：保证文本内容按 UTF-8 写入，并避免 `csv` 模块写出的行尾被文本模式重复转换（`newline=""` 是 `csv` 模块的推荐写法）；
3. `lineterminator="\n"`：行尾统一用 `\n`，不写 CRLF——M6 的 `external_oscillation_tracker.py` 第 367 行注释说明这是为了"与 results 下已有 CSV 保持一致"。

### 7.5 逐帧循环（第 488～535 行）：每一轮的顺序

```python
# src\video_tracker.py::track_video() 第 488～510 行（节选）
try:
    while True:
        # ---- 调用现有检测器（检测参数唯一来源：src/marker_detector.py）----
        result = detect_marker(current_frame)

        # ---- 时间轴：time_s = frame_index / fps（frame_index 从 0 开始）----
        time_s = frame_index / fps

        # ---- 写 CSV：每帧一行，检测失败也要写 ----
        csv_writer.writerow(build_csv_row(frame_index, time_s, result))

        record = {
            "frame": frame_index,
            "time_s": time_s,
            "success": bool(result["success"]),
        }
        if result["success"]:
            record["cx"] = result["cx"]
            record["cy"] = result["cy"]
            record["area"] = result["area"]
            detected_count += 1
            area_list.append(result["area"])
        records.append(record)
```

每一轮要做的事（带行号）：

| 步骤 | 行号 | 做的事 |
| --- | --- | --- |
| 1 | 第 489 行 | `while True:` 逐帧循环开始 |
| 2 | 第 491 行 | `result = detect_marker(current_frame)`：复用 L02～L04 的检测器 |
| 3 | 第 494 行 | `time_s = frame_index / fps`：把帧号翻译成时间 |
| 4 | 第 496～497 行 | `csv_writer.writerow(build_csv_row(...))`：**本帧立刻成文一行** |
| 5 | 第 499～510 行 | 组装 `record` 并追加进 `records`；成功时累计 `detected_count` 与 `area_list` |
| 6 | 第 513～521 行 | 生成叠加可视化（有 writer 就写叠加帧；没有就记清晰度指标备用） |
| 7 | 第 526～532 行 | 读取下一帧：`ret, next_frame = cap.read()`（第 527 行）；读不到就 `break`（第 528～530 行）；读到就 `frame_index += 1`（第 531 行）、`current_frame = next_frame`（第 532 行） |
| 8 | 第 534～535 行 | 每 200 帧打印一次进度 |

两个容易忽略、但很重要的顺序事实：

1. **先处理、后读下一帧、再判断结束**（L05 已学）：这个顺序保证最后一帧也被完整写入 CSV；
2. **CSV 是"边处理边写"的**：不等到循环结束才一次性写文件。所以即使中途按 Ctrl+C，已经写下的行仍然留在文件里（第 536～539 行的中断提示就是在说这件事）。

### 7.6 收尾：关闭文件与异常保护（第 536～544 行）

```python
# src\video_tracker.py::track_video() 第 536～544 行
except KeyboardInterrupt:
    interrupted = True
    print("")
    print("警告：收到中断信号，已处理的帧数据仍然保留在 CSV 与叠加视频中")
finally:
    csv_file.close()
    cap.release()
    if writer is not None:
        writer.release()
```

- 第 541 行 `csv_file.close()`：**关闭 CSV 文件**（把缓冲区内容交给操作系统落盘、释放文件句柄）；
- 第 542 行 `cap.release()`、第 543～544 行 `writer.release()`：释放视频资源（L05 已学）；
- 三者都放在 `finally` 里（第 540 行），无论正常结束、异常还是 Ctrl+C，都尽量完成清理。

### 7.7 结束后的统计与返回（第 546～588 行）

- 第 546 行：计算总耗时；
- 第 548～555 行：叠加视频写入器不可用时，用 `records` 挑代表性帧保存 PNG（回退方案，与 CSV 无关）；
- 第 557～560 行：打印 CSV / 叠加视频写入位置；
- 第 562～586 行：组装 `summary` 统计字典（下一节展开）；
- 第 588 行：`return summary` 交给调用方（`demo\run_video_tracking.py` 第 43 行接收）。

### 7.8 数据流一览

```text
视频文件
  └─ cap.read()（第 444、527 行）
       └─ current_frame（第 480、532 行）
            └─ detect_marker(current_frame)（第 491 行）→ result
                 ├─ time_s = frame_index / fps（第 494 行）
                 ├─ build_csv_row(frame_index, time_s, result)（第 393～410 行）
                 │       └─ csv_writer.writerow(...)（第 497 行）→ results\..._track.csv
                 └─ record dict（第 499～510 行）→ records（内存账本）
                        └─ summary / compute_longest_miss_run（第 562～586、591～604 行）
```

## 8. records 与 CSV 的区别

两者都由第 491 行的同一个 `result` 产生，也都"每帧一条"，但它们是**两种不同的东西**：

| 对比项 | `records`（内存账本） | CSV 文件 |
| --- | --- | --- |
| 存在形式 | Python 列表，元素是字典（第 499～510 行） | 磁盘上的纯文本表格（第 483～485、497 行） |
| 生命周期 | 只在本次运行期间存在；程序结束就消失 | 写入磁盘，可长期保存、可被别的程序读取 |
| 内容形态 | 原始值：`frame` 整数、`time_s` 浮点数、`success` 布尔值；成功时才有 `cx` / `cy` / `area`（第 499～509 行） | 全部是文本：格式化后的数字字符串、`"True"` / `"False"`、失败处的空字符串 |
| 失败行的样子 | `{"frame": ..., "time_s": ..., "success": False}`——**没有** cx / cy / area 这些键 | `frame,time_s(6位小数),空,空,空,False`——6 列都在，只是测量列留空 |
| 包含哪些字段 | 程序内部需要的字段（`success`、原始浮点坐标等） | 设计给人和下游程序的字段（列名、列序由 `CSV_FIELDNAMES` 规定） |
| 主要用途 | 运行期统计（`summary`，第 562～586 行）、最长连续丢失（第 591～604 行）、PNG 回退挑帧（第 266～292、548～555 行） | 交付产物：长期保存、人工核对、后续读取分析（`check_csv_data` 读的就是它，第 662～664 行） |
| 是否可被外部工具读 | 否（只在 Python 进程内） | 是（任何能读文本表的工具都能读） |

三个要点：

1. **`records` 不是"内存里的 CSV"，CSV 也不是"被保存的 records"。** 两者的字段选择、数据类型、失败表达方式都是各自设计的；第 497 行（写 CSV）与第 499～510 行（追加 records）是两条并行的支线，使用同一份 `result`。
2. **`records` 面向"程序自己"，CSV 面向"文件外面的人与程序"。** 统计只能读 `records`（因为 CSV 里没有 `success` 布尔值这种原始类型），而长期价值全在 CSV 里。
3. **"内存里有账"不等于"数据已保存"。** 如果只写了 `records` 而没有 CSV，程序一退出数据就没了——这正是本节要解决的核心问题。

M6 里有一个同样的证据：`external_oscillation_tracker.py` 运行期把每帧组装成字典（第 319～332 行），其中包含 `candidate_count`、`accepted_count` 两个"候选人 / 接受人数"统计（第 330～331 行）；但 `write_trajectory_csv()` 写文件时只挑选正式字段组成 8 列（第 372～382 行），这两个内存统计**不会进入 CSV**。这就是"内存记录 ≠ 落盘字段"在 M6 中的又一次体现（该模块检测算法细节不属于本节内容，这里只引用与 CSV 相关的行）。

## 9. 运行期统计与落盘自检

### 9.1 summary 统计字典（第 562～586 行）

循环结束后，`track_video()` 用第 562～586 行组装 `summary`，里面的每一项都能找到"数据从哪来"：

| summary 字段 | 来源 | 含义 |
| --- | --- | --- |
| `processed_frames` | `len(records)`（第 570 行） | 实际处理（= 实际解码）的帧数 |
| `detected_frames` | `detected_count`（第 571 行） | 检出成功的帧数 |
| `missed_frames` | `len(records) - detected_count`（第 572 行） | 丢失帧数 |
| `detection_rate` | `detected_count / len(records)`（第 573 行） | 检出成功率（0~1） |
| `longest_miss_run` | `compute_longest_miss_run(records)`（第 574 行） | 最长连续丢失帧数 |
| `area_min` / `area_median` / `area_max` | `area_list` + `np.median`（第 575～577 行） | 成功帧的面积统计 |
| `first_time_s` / `last_time_s` | `records[0]["time_s"]` / `records[-1]["time_s"]`（第 578～579 行） | 序列的起止时刻 |
| `elapsed_seconds` | 第 546 行计时 | 本次运行耗时 |
| `sha256_before` / `sha256_after` | 第 428、585 行 | 原始视频运行前后的指纹（证明没被改动） |

`compute_longest_miss_run()`（第 591～604 行）是一个独立的小函数：遍历 `records`，用 `record["success"]` 判断；成功把当前计数清零，失败则累加并刷新历史最大值，最后返回"最长连续丢失帧数"。它回答的问题是："这段数据里有没有连续一大段看不到目标？"——这是判断时序数据是否可信的基本指标之一。

### 9.2 check_csv_data()：对"写出来的文件"再做一次体检（第 643～824 行）

- **文件 / 函数**：`src\video_tracker.py` → `check_csv_data(csv_path, expected_rows, frame_width, frame_height, fps=None)`（第 643 行起，返回 `(checks, passed)`，第 823～824 行）
- **特点**：它**重新打开磁盘上的 CSV 文件**（第 662～664 行用 `csv.reader` 读回），而不是复用内存里的 `records`——检查的对象是"真正交付出去的那份文件"。
- **调用方**：`demo\run_video_tracking.py` 第 52～58 行（传入 `summary["csv_path"]`、`summary["processed_frames"]`、`summary["width"]`、`summary["height"]`），结果由 `print_check_results()`（第 827～836 行）打印。

现行实现是 **10 项检查**（每次把 `(说明, 是否通过)` 追加进 `checks` 列表），可按职责归纳为六组：

| 组 | 行号 | 检查什么 |
| --- | --- | --- |
| 1. 表头 | 第 670～671 行 | CSV 第一行是否严格等于 `CSV_FIELDNAMES`（列名与顺序都对） |
| 2. 行数 | 第 674～675 行 | 数据行数是否等于实际处理的帧数 `expected_rows` |
| 3. frame 列 | 第 678～693 行 | 每行是否 6 列；`frame` 是否全部为合法整数（第 689 行）；是否从 0 到 N-1 连续、无重复（第 692～693 行） |
| 4. 成功 / 失败行的内容 | 第 700～740 行 | `detected=True` 的行：x/y/area 必须是合法数值（第 736 行）、不允许 x=0 且 y=0 的伪数据（第 738 行）、坐标必须落在画面范围内（第 739～740 行）；`detected=False` 的行：x/y/area 必须全部为空（第 737 行） |
| 5. `time_s` 时间轴 | 第 742～783 行 | 逐行核对 `|time_s - frame / fps|` 是否在容差内（`TIME_AXIS_TOLERANCE_S`）；fps 必须来自真实视频读取，缺失或不合法时本项判为"无法验证" |
| 6. 失败字段语义 | 第 794～818 行 | 复用 `csv.reader` 读回的文本视角：`detected=False` 的行测量字段必须全空、`detected=True` 的行不得为空，且"空 `x_px` 行数"必须等于"`detected=False` 行数"（第 817 行） |

最后第 823 行 `passed = all(ok for _, ok in checks)`：所有检查项都通过才算"数据可信"。

这组自检回答了本节的一个关键态度问题：

> **"把 CSV 写出来"只是第一步，"确认写出来的 CSV 与设计一致"才是完成——数据文件也需要体检。**

## 10. CSV 如何形成离散时间序列

### 10.1 一行 = 一个采样点

把 M3 的 CSV 从列的角度重新读一遍：

- **时间轴**：`time_s` 列，第 k 行的值 = `frame_index / fps`（第 494 行）；
- **测量值**：`x_px`、`y_px`（质心位置），`area_px` 作为质量指标；
- **有效性**：`detected` 列。

于是整张表就是一组采样点：

```text
(t_0, x_0, y_0, area_0, detected_0)
(t_1, x_1, y_1, area_1, detected_1)
...
(t_{N-1}, ...)
```

其中 `t_k = k / fps`，相邻两个采样点的时间间隔恒为 `Δt = 1/fps`。这就是"离散时间序列"在文件里的样子：**行是采样时刻，列是同时刻测到的量**。

### 10.2 离散的含义

- 只能在帧时刻取值：两帧之间的任何时刻，计算机没有数据（L01 / L05 已学）；
- 时间分辨率 = 1/fps：M3 视频的 fps 从文件读取，CSV 里 frame 1 的 `time_s = 0.041667`（24 fps）；M6 外部视频是 30 fps，`frame 76 → 2.533333 s`。**公式相同，fps 数值由各自的视频文件决定，不能把某一课的 30 当成全项目常数**；
- 采样是等间隔的：只要 frame 连续（自检第 3 组保证），时间轴就均匀。

### 10.3 失败行如何影响时间序列

- 失败行**保留**（第 496～497 行），所以时间轴始终完整：`t_k` 与 `frame_index` 一一对应，不会"少一个点、整体错位"；
- 失败行的测量值留空、`detected=False`（第 410 行），读进程序后表现为缺失值（自检第 6 组把"空字段"与"`detected=False`"对账，第 794～818 行）；
- 因此得到的是一条"**时刻齐全、个别时刻缺失测量值**"的离散序列——这是对真实情况最诚实的表达。

### 10.4 与 L01 的呼应

L01 从"数据使用者的角度"学过两句话：**"一行 CSV = 一个时刻的一次视觉测量结果"**、**"y0_px 按时间排列形成时间序列 y0(t)"**。本节从"数据生产者的角度"补上了它们的代码实现：

- "一行 = 一次测量"→ 第 496～497 行"每帧一行、失败也写"；
- "位置随时间排列"→ 第 494 行 `time_s = frame_index / fps` 与第 497 行的写入顺序；
- 区别只在于：L01 的正式特征是外部视频的 `y0_px`（M6），M3 的 `_track.csv` 记录的是红色标记的质心 `(x_px, y_px)`——**同样是"位置时间序列"，被测对象与特征不同**。

## 11. M3 的 _track.csv 与 M6 的 _trajectory.csv

### 11.1 两份文件分别是谁写的

| | M3 `_track.csv` | M6 `_trajectory.csv` |
| --- | --- | --- |
| 代表文件 | `results\EXP-002-VIDEO-001_track.csv` | `results\EXP-EXT-LAB67-V1_trajectory.csv` |
| 生成代码 | `src\video_tracker.py` → `track_video()`（第 413 行起） | `src\external_oscillation_tracker.py` → `write_trajectory_csv()`（第 357 行起），由 `run_external_tracking()`（第 627 行起）调用（第 639 行） |
| 调用入口 | `demo\run_video_tracking.py` 第 43 行 | `demo\run_m62_external_tracking.py` |
| 真实规模（只读核对） | 表头 + 170 行数据（frame 0～169，全片） | 表头 + 160 行数据（frame 76～235，正式分析区间） |
| 正式表头 | `frame,time_s,x_px,y_px,area_px,detected` | `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px` |

### 11.2 共同设计思想（"同一套数据记录规范"）

1. **第一行就是真表头，前面不加任何 metadata。** M3 注释见 `video_tracker.py` 第 40 行；M6 注释见 `external_oscillation_tracker.py` 第 87 行；写表头分别是第 485 行 `writerow(CSV_FIELDNAMES)` 与第 369 行 `writeheader()`。
2. **都有字段名清单常量。** M3 第 41 行 `CSV_FIELDNAMES`；M6 第 88～97 行 `CSV_FIELDNAMES`（8 项）。
3. **都有 frame 与 time_s 两列，且 time_s 使用同一条绝对时间轴 `frame / fps`。** M3 第 494 行；M6 第 322～323 行（注释写明"使用原视频绝对时间轴：frame / fps（不重新定义时间零点）"）。时间都写 `"%.6f"`（M3 第 404、410 行；M6 第 375、388 行）。
4. **都有 detected 标志列，采用同一原则："测不到"不能伪造。** M3 第 399 行"失败时绝不写 0 / -1 / nan / 字符串"；M6 第 361 行"detected=True -> 写全字段；detected=False -> 写 detected=False，其余字段留空"，失败分支在第 384～396 行逐字段写 `""`。
5. **每帧仍然占一行（在各自记录的区间内），不跳过失败帧。** M3 第 496～497 行；M6 按 rows 顺序遍历逐行写（第 370～396 行）。
6. **文本编码与行尾约定一致。** 都以 `encoding="utf-8", newline=""` 打开、`lineterminator="\n"`（M3 第 483～484 行；M6 第 366～368 行，第 367 行注释说明与 results 下已有 CSV 保持一致）。
7. **写完后都要"读回来"做独立核对，而不是写完就信。** M3 用 `csv.reader` + 表头 / 行数 / 连续性 / 留空规则 + `time_s` 时间轴 / 失败字段语义检查（第 643～824 行）；M6 用 `csv.DictReader` 读回（第 400～423 行），再检查表头（第 459～460 行）、行数（第 463～464 行）与 `time_s ≈ frame / fps`（第 519～523 行）等。

一句话概括共同思想：

> **两份 CSV 是同一套"数据记录规范"的两次应用：真表头、字段名清单、frame/time_s 时间轴、detected 有效性标志、失败留空不伪造、写完读回自检。**

### 11.3 字段差异（同一规范下按需裁剪）

| 对比项 | M3 `_track.csv`（6 列） | M6 `_trajectory.csv`（8 列） | 说明 |
| --- | --- | --- | --- |
| 列顺序 | `frame, time_s, x_px, y_px, area_px, detected` | `frame, time_s, detected, x_px, y0_px, bbox_w_px, bbox_h_px, area_px` | `detected` 在 M3 排最后、在 M6 排第三；**同一份规范下，列顺序由各自 `CSV_FIELDNAMES` 决定** |
| 位置特征 | `x_px`, `y_px`：红色标记**质心**（L04 的 `(cx, cy)`） | `y0_px`：**暗带上缘竖直位置**（M6 冻结的正式特征）；`x_px`：暗带 bbox 中心，"仅作为 QC 记录"（第 240～241 行注释） | 每份文件测的是各自场景里"有意义的位置" |
| 质量字段 | `area_px` | `area_px` + `bbox_w_px` / `bbox_h_px` | M6 需要更多"检测区域是否像一条暗带"的形状信息 |
| frame 覆盖范围 | 整个视频：frame 0～169，170 行（逐帧全记录） | 正式分析区间：frame 76～235，160 行（第 4 行模块说明与 README / CHANGELOG 登记一致） | M3 是"全程记录"，M6 是"只记录正式区间" |
| 数字格式 | 坐标 `"%.2f"`、面积 `"%.1f"` | 坐标 `"%.2f"`；`bbox_w_px` / `bbox_h_px` / `area_px` 写整数（第 379～381 行） | 都是"够用即可"的可读格式 |
| writer 用法 | `csv.writer` + `writerow(CSV_FIELDNAMES)`（第 478～479 行） | `csv.DictWriter` + `writeheader()`（第 368～369 行），每行显式按字段名组装（第 372～395 行） | 两种写法都合法，`DictWriter` 让"字段名 → 值"的对应更显式 |
| 视频 fps | 该视频文件自己的 fps（CSV 中 frame 1 → 0.041667 s，24 fps） | 外部视频 30 fps（frame 76 → 2.533333 s） | 再次说明 fps 必须从文件读，不能由别的课的数字照搬 |

### 11.4 两张表带来的两个额外结论

1. **同名字段在不同文件里可能含义不同。** M3 的 `x_px` 是红色标记质心 `cx`（`video_tracker.py` 第 405 行）；M6 的 `x_px` 是暗带 bbox 中心（`external_oscillation_tracker.py` 第 240～241 行）。字段名只是文件内部的通行语言，**要引用字段，必须先找到写它的代码**（这也解释了为什么 L01 词条里的 `x_px` 解释是"暗带外接框中心"——那是 M6 的语境）。
2. **"记录区间"本身是设计决策。** M3 把整段视频逐帧全部记录（170 行）；M6 只把冻结后的正式区间写进正式文件（160 行）。两者都不是"随便行数"，而是写代码时明确的选择——CSV 的行数 = 想留下的时刻数。

## 12. L06 与 L01～L05 的知识连接

### 12.1 一句话链条

> **L04 的 centroid → L05 的逐帧检测 → L06 的 CSV → 后续的时间序列分析（位移 / 周期 / 频率）。**

### 12.2 逐课连接表

| 课程 | 已经学到的 | L06 用到了它的什么 |
| --- | --- | --- |
| L01 | CSV 与时间序列的概念：一行 = 一个时刻的一次测量；frame 与 time_s 的关系；轨迹文件在数据链中的位置 | 本节把"概念上的 CSV"变成"由代码生成的真实文件"，并研究它的字段设计与失败表达 |
| L02 | `detect_marker()` 的输入输出：成功返回 `success/cx/cy/area/bbox/contour/mask`，失败返回 `success=False` | `result["success"]` / `["cx"]` / `["cy"]` / `["area"]` 就是 CSV 六个字段里 4 个字段的源头（第 501～509 行） |
| L03 | 像素、颜色空间、Mask：像素是位置的单位 | 所有 `_px` 字段的单位；`area_px` 是像素面积 |
| L04 | Contour / Moments / Centroid：`cx = m10/m00`、`cy = m01/m00`；`cv2.contourArea` | `x_px` / `y_px` 记录的就是这个质心；`area_px` 就是轮廓面积 |
| L05 | 逐帧循环：`detect_marker(current_frame)`（第 491 行）、`time_s = frame_index / fps`（第 494 行）、"处理当前帧 → 读下一帧 → 判断结束"、失败不伪造坐标（第 399、410 行） | L06 的 CSV 生成流程就嵌在这个循环里：第 497 行写文件、第 499～510 行记 records、第 527～532 行推进帧号 |
| L06（本节） | 字段设计（`CSV_FIELDNAMES`）、行生成（`build_csv_row`）、持久化（`csv.writer`）、内存账本（`records`）、统计与自检（`summary`、`compute_longest_miss_run`、`check_csv_data`）、离散时间序列、M3/M6 字段对比 | 从此"逐帧检测结果"第一次成为可离线使用的数据文件 |
| 后续课程 | Calibration（px → mm）、位移计算（displacement）、周期 / 频率、FFT | 它们都会以 CSV（如 `_track.csv`、`_trajectory.csv`、`_ds.csv`）为输入；本节只学"怎么把数据完好地写下来"，不学"怎么分析它" |

### 12.3 从数据流角度看"承上启下"

```text
原始视频 → 逐帧检测（L05）→ 每帧结果 result（L04 的质心等）
                              ↓  build_csv_row()（第 393～410 行）
                         _track.csv / _trajectory.csv（L06）
                              ↓  后续课程（本节不展开）
                     位移 → 周期 / 频率 → FFT
```

## 13. 真实源码、教学伪代码与教学示例

本课程笔记涉及三类材料，必须**永远分清**，否则长期复习时会把"解释用的"当成"项目里真实存在的"。

### 13.1 三类材料对照表

| 类别 | 是什么 | 本笔记中的例子 | 如何标注 | 能不能当"项目事实"引用 |
| --- | --- | --- | --- | --- |
| A. VisionMotion 真实源码 | 仓库里实际存在的代码 | `src\video_tracker.py` 第 41、393～410、483～485 行；`src\external_oscillation_tracker.py` 第 87～97、357～397 行 | 给出"文件路径 + 函数名 + 行号" | 可以（引用前重新核对行号） |
| B. 教学伪代码 | 为帮助理解而重写的简化流程，**不是项目源码** | 下面第 13.2 节的伪代码块 | 代码块前明确写"教学伪代码（不是项目源码）" | 不可以 |
| C. 教学示例 | 为说明机制人为构造的例子 | 第 6.2 节的失败行 `4,0.066667,,,,False`；第 6.3 节的反面写法 | 前后明确写"教学示例（非真实数据）" | 不可以；项目数字实例应改用真实产物文件里的行 |

### 13.2 教学伪代码（不是 VisionMotion 源码）

```text
# 教学伪代码（不是 VisionMotion 真实源码）
打开 CSV 文件
写表头（CSV_FIELDNAMES）
for 每一帧:
    result = 检测这一帧
    time_s = 帧号 / fps
    一行 = 把 (帧号, time_s, result) 变成 6 个字段
    把这一行写入 CSV
关闭 CSV 文件
```

对照真实源码，可以看到项目实际多做了哪些事（也正是工程上不能省略的部分）：

- 用标准库 `csv.writer`（第 484 行）而不是手工拼字符串——避免逗号 / 引号 / 换行等转义问题；
- 失败行有明确的格式约定（第 410 行），而不是"随便写"；
- 用 `try / finally` 保证文件一定被关闭（第 488、540～544 行）；
- 同时维护 `records` 与统计（第 499～510、562～586 行），并对写出的文件做自检（第 643～824 行）；
- 写入的是**每一帧**（包括失败帧），保持时间轴连续。

### 13.3 为什么必须这样区分

- 复习时最容易记混的往往是"最显眼"的内容（表格、口诀、小例子），所以教学示例必须自带"非真实数据"标签；
- 项目事实需要可复查：只有"文件 + 函数 + 行号"能让人一分钟内回到源码验证；
- 伪代码只承担"讲清楚思路"的任务，不能反过来当作对项目行为的描述。

## 14. 本节课不深入的内容

以下内容本节**只登记名称、不展开**（有的属于后续课程，有的不属于本项目第一阶段范围）：

- **Calibration（相机标定 / px → mm 换算）**：CSV 里的 `_px` 仍是像素单位，本节不做毫米换算；
- **Displacement（位移计算）**：如何从 `_track.csv` 进一步计算位移序列（项目里有 `_ds.csv` 这类产物）不在本节展开；
- **FFT、频率、周期（含峰谷与周期测量）**：属于后续分析课程；
- **`external_oscillation_tracker.py` 的检测算法细节**：本节只引用它与 CSV 相关的部分（字段清单第 87～97 行、写文件第 357～397 行、读回自检第 400～423、442～460 行），暗带检测内部逻辑不展开；
- **pandas / 数据库 / 高级数据分析**：本项目 CSV 读写使用 Python 标准库 `csv`（`video_tracker.py` 第 26 行 `import csv`；自检也统一用 `csv.reader`，不再依赖 `np.genfromtxt`）；`video_tracker.py` 第 23 行的代码风格声明明确"不使用 pandas / scipy"，项目依赖清单（`requirements.txt`）里也没有 pandas；数据库、数据仓库等更不在本项目范围内。

## 15. L06 源码地图

### 15.1 `src\video_tracker.py`（共 836 行，2026-10-07 逐行核对）

| 位置 | 函数 / 位置 | 内容与作用 |
| --- | --- | --- |
| 第 26 行 | 模块导入区 | `import csv`（标准库表格读写工具） |
| 第 34 行 | 模块导入区 | `from src.marker_detector import detect_marker`（检测器复用，L05 已学） |
| 第 40～41 行 | 常量区 | 注释"第一行就是真正的表头"；`CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]` |
| 第 393～410 行 | `build_csv_row(frame_index, time_s, result)` | 把一帧结果变成一行 6 个字段：成功分支第 401～409 行；失败分支第 410 行 |
| 第 399 行 | `build_csv_row()` docstring | 失败行原则："失败时绝不写 0 / -1 / nan / 字符串" |
| 第 413 行 | `track_video(video_path, csv_path, overlay_path)` | 逐帧追踪主流程（第 413～588 行） |
| 第 428 行 | `track_video()` | 运行前原始视频 SHA-256 指纹 |
| 第 432 行 | `track_video()` | 调用 `open_video()` 打开视频 |
| 第 437～441 行 | `track_video()` | fps 合法性检查（≤ 0 则停止） |
| 第 444 行 | `track_video()` | 读取第一帧（用于确定画面尺寸） |
| 第 476 行 | `track_video()` | `records = []`：每帧一条记录的内存账本 |
| 第 477～481 行 | `track_video()` | `sharpness_list` / `detected_count` / `area_list` / `current_frame = first_frame` / `frame_index = 0` |
| 第 483～485 行 | `track_video()` | 打开 CSV（`encoding="utf-8"`、`newline=""`）、创建 `csv.writer`（`lineterminator="\n"`）、写表头 `CSV_FIELDNAMES` |
| 第 488～541 行 | `track_video()` | `try:` 包住主循环，`finally:` 保证收尾 |
| 第 489 行 | `track_video()` | `while True:` 逐帧循环开始 |
| 第 491 行 | `track_video()` | `result = detect_marker(current_frame)` 逐帧检测 |
| 第 494 行 | `track_video()` | `time_s = frame_index / fps` 帧号 → 时间 |
| 第 496～497 行 | `track_video()` | 注释"每帧一行，检测失败也要写"；`csv_writer.writerow(build_csv_row(...))` |
| 第 499～510 行 | `track_video()` | 组装 `record`（frame / time_s / success；成功时补 cx / cy / area 并累计统计）并 `records.append(record)` |
| 第 527～532 行 | `track_video()` | 读下一帧；读不到 `break`（第 528～530 行）；`frame_index += 1`（第 531 行）、`current_frame = next_frame`（第 532 行） |
| 第 536～539 行 | `track_video()` | `except KeyboardInterrupt`：中断时已写数据仍保留 |
| 第 540～544 行 | `track_video()` | `finally`：`csv_file.close()`（第 541 行）、`cap.release()`（第 542 行）、`writer.release()`（第 543～544 行） |
| 第 562～586 行 | `track_video()` | `summary` 统计字典（含 `processed_frames`、`detected_frames`、`detection_rate`、`longest_miss_run`、面积统计、起止时间等） |
| 第 591～604 行 | `compute_longest_miss_run(records)` | 依据 `records` 计算最长连续丢失帧数 |
| 第 643～824 行 | `check_csv_data(csv_path, expected_rows, frame_width, frame_height, fps=None)` | 读回磁盘 CSV 做 **10 项**自检：第 670～671 行表头、第 674～675 行行数、第 678～693 行 frame 合法与连续、第 700～740 行成功 / 失败行内容、第 742～783 行 `time_s` 时间轴一致性（第 9 项）、第 794～818 行 CSV 空测量字段与 `detected=False` 语义对账（第 10 项）；第 823～824 行返回 `(checks, passed)` |
| 第 827～836 行 | `print_check_results(checks, passed)` | 打印自检结果 |

### 15.2 M6 对照：`src\external_oscillation_tracker.py`（共 661 行，仅列 CSV 相关位置）

| 位置 | 函数 / 位置 | 内容与作用 |
| --- | --- | --- |
| 第 4、28 行 | 模块 docstring | 说明本模块流程包含"写正式轨迹 CSV"（`frame / time_s / detected / x_px / y0_px / bbox_w_px / bbox_h_px / area_px`） |
| 第 88～97 行 | 常量区 | 注释"第一行就是真正的表头"；`CSV_FIELDNAMES`（8 项） |
| 第 319～332 行 | `track_external_oscillation()` | 每帧组装内存行字典：第 321 行 frame、第 322～323 行 `time_s = decoded_index / video_info["fps"]`、第 324 行 `detected`、第 325～329 行各测量字段、第 330～331 行额外的内存统计 `candidate_count` / `accepted_count` |
| 第 357～397 行 | `write_trajectory_csv(rows, csv_path)` | 写正式轨迹 CSV：第 361 行 docstring 写明"成功写全字段、失败写 False 其余留空"；第 366～369 行打开文件、`csv.DictWriter`、`writeheader()`；第 371～383 行成功行；第 384～396 行失败行（其余字段写 `""`） |
| 第 400～423 行 | `load_trajectory_csv(csv_path)` | 用 `csv.DictReader` 读回（第 407～409 行）；空字段解析为 `None`（第 417～419 行） |
| 第 442～460 行 | `check_trajectory_csv(...)` | 读回自检：第 459～460 行校验表头等于 `CSV_FIELDNAMES` |
| 第 519～523 行 | `check_trajectory_csv(...)` | 校验 `time_s` 严格满足 `frame / fps`（含容差） |
| 第 639 行 | `run_external_tracking(...)` | 调用 `write_trajectory_csv(...)` 落盘，第 640 行再读回做独立质量检查 |

### 15.3 真实产物（只读登记，本笔记未重新生成）

| 文件 | 真实内容（2026-10-02 只读核对） |
| --- | --- |
| `results\EXP-002-VIDEO-001_track.csv` | 表头 `frame,time_s,x_px,y_px,area_px,detected`；170 行数据（frame 0～169）；首行 `0,0.000000,618.28,160.56,75863.0,True` |
| `results\EXP-EXT-LAB67-V1_trajectory.csv` | 表头 `frame,time_s,detected,x_px,y0_px,bbox_w_px,bbox_h_px,area_px`；160 行数据（frame 76～235）；首行 `76,2.533333,True,724.00,514.00,57,4,226` |

> 以上行号按 **2026-10-07** 的当前源码逐行核对（`src\video_tracker.py` 共 836 行、`src\external_oscillation_tracker.py` 共 661 行）。
> **如果实际源码行号发生变化，以当前真实源码为准**——知识链与结论不因行号漂移而改变，但引用时应重新核对"文件 + 函数 + 行号"。

## 16. 本节课最重要的概念

1. **`result` 只是"当前这一帧"的临时答案**（第 491 行）：每轮被覆盖、程序结束即消失；逐帧结果必须另有"内存账本 + 落盘文件"两个去处。
2. **CSV 是纯文本表格**：第一行是表头（第 40～41、485 行），后面每行是一条记录；row / column / header / cell 是最基本的四个名词。
3. **`CSV_FIELDNAMES`（第 41 行）是唯一的字段定义**：列名、列顺序由它决定，写出（第 485、497 行）与自检（第 670～671 行）都依赖它。
4. **六个字段各有分工**：`frame` / `time_s` 是坐标轴，`x_px` / `y_px` / `area_px` 是测量值与质量指标，`detected` 是有效性标志。
5. **`build_csv_row()`（第 393～410 行）是"帧结果 → 一行字段"的翻译器**：成功写全 6 项（`"%.6f"` / `"%.2f"` / `"%.2f"` / `"%.1f"` / `"True"`），失败写 `frame, time_s, "", "", "", "False"`（第 410 行）。
6. **失败行的原则：留空 + False，绝不写 0 / -1 / nan / 上一帧坐标（第 399 行）**——"测不到，就明确标记缺失，而不是制造一个假测量"。
7. **失败行也要写、每帧占一行（第 496～497 行）**：时间轴因此保持连续，缺失是"有标记的空"，不是"消失的行"。
8. **CSV 的完整生命周期在 `track_video()` 里**：打开（第 483 行）→ 写表头（第 485 行）→ 每帧一行（第 497 行）→ `finally` 关闭（第 541 行）。
9. **`records` 与 CSV 是两种不同表示**（第 476、499～510、497 行）：前者是运行期内存字典列表（原始类型、含 `success` 布尔值），后者是磁盘文本（格式化、空字符串、`True` / `False` 文本）。
10. **统计只认 `records`，自检只认 CSV 文件**：`summary`（第 562～586 行）与 `compute_longest_miss_run()`（第 591～604 行）用内存账本；`check_csv_data()`（第 643～824 行）重新打开磁盘文件做 10 项检查（表头、行数、frame 连续、成功 / 失败行内容、`time_s` 时间轴、失败字段语义对账）。
11. **CSV 就是离散时间序列的表格形式**：`t_k = k / fps` 均匀采样（第 494 行）；失败行保留 → "时刻齐全、个别值缺失"。
12. **fps 永远从各自的视频文件读取**：M3 视频 24 fps（frame 1 → 0.041667 s），M6 外部视频 30 fps（frame 76 → 2.533333 s）；公式 `frame / fps` 相同，数字不能照搬。
13. **M3 与 M6 共用同一套记录规范**：真表头、字段名清单、frame/time_s 时间轴、detected 标志、失败留空、写完读回自检；差异在于字段选择（6 列 vs 8 列：质心 vs 暗带上缘 + bbox）、记录范围（全片 170 行 vs 正式区间 160 行）与列顺序。
14. **引用字段前必须回到生成它的代码**：同名的 `x_px` 在 M3 是质心横坐标、在 M6 是暗带 bbox 中心——字段名只是文件内部的约定。

## 17. 易错点

1. **以为 `result` 会一直保存历史。** 它每轮被第 491 行整体替换，循环结束只剩最后一帧；历史在 `records` 与 CSV 里。
2. **把 CSV 当成"程序内存里的表格"。** CSV 是磁盘上的纯文本；它不能保存 Python 布尔值 / 字典，只保存写出的那些文本字段。
3. **把表头当装饰、按"第几列"硬读。** 列名与列顺序由 `CSV_FIELDNAMES` 决定（M3 第 41 行、M6 第 88～97 行）；且两份文件列顺序不同（`detected` 一在最后、一在第三），必须按名字找列。
4. **失败时写 0 / -1 / nan 字符串。** 这些值会被当成"真实数值"，污染统计与曲线；项目用自检专门挡 `(0,0)` 伪数据（第 726～727、738 行）。
5. **失败时沿用上一帧坐标。** 这是最隐蔽的伪造：数据看起来完整，实际掩盖了丢失、抹平了运动；原则见第 399 行。
6. **失败帧干脆不写。** 行数与帧号会错位，时间轴断裂；正确做法是"每帧一行、失败也写"（第 496～497 行）。
7. **把 `records` 与 CSV 混为一谈。** `records` 含有 CSV 里没有的信息（`success` 布尔值、原始浮点值），也缺少 CSV 的格式化与空字符串约定；两者是并行的两套表示。
8. **把某一课的 fps 当成全项目常数。** 30 fps 是 L01 外部视频 / M6 的数字；M3 的 `EXP-002-VIDEO-001` 24 fps。`time_s` 必须用第 130 行从文件读到的 fps 算。
9. **认为"文件写出来了"就等于"数据可信"。** 还要跑 `check_csv_data()`（第 643～824 行）：表头、行数、frame 连续性、成功行合法性、失败行留空、无伪数据、`time_s` 时间轴一致、失败字段语义对账。
10. **以为 CSV 行数一定等于视频总帧数。** M3 全片 170 行是"全程记录"的选择；M6 只写正式区间 160 行（frame 76～235）——行数 = 写代码时决定留下的时刻数。

## 18. 本节课自测题

先不看任何资料，用自己的话回答。本页不附答案。

1. 为什么逐帧检测结果不能只留在 `result` 变量里？请从"覆盖、生命周期、可传递性"三个角度回答。
2. 用一句话说清 CSV 是什么；再用 row / column / header / cell 四个词描述 `results\EXP-002-VIDEO-001_track.csv` 的前两行。
3. `CSV_FIELDNAMES` 定义在哪个文件、第几行？它被哪三处使用？如果它和 `build_csv_row()` 的顺序不一致，会发生什么？
4. M3 的 6 个字段分别是什么？逐个说出含义、单位 / 类型与数值来源（提示：质心、时间换算、成功标志）。
5. `build_csv_row()` 在第几行到第几行？它的输入、处理、输出分别是什么？它自己负责写文件吗？
6. 成功行和失败行在 6 个字段上分别怎么写？请把第 410 行的失败行背写出来。
7. 第 399 行的原则是什么？为什么失败时不能写 0？为什么不能写 -1？为什么不能沿用上一帧坐标？为什么不能干脆不写这一行？
8. 空白字段在读回时会变成什么？自检程序如何验证"空白"与"检测失败"一一对应？（提示：`csv.reader` 文本视角、空测量字段行数与 `detected=False` 行数相等）
9. 按顺序说出 `track_video()` 里 CSV 的生命周期（打开、表头、逐帧写、record、关闭），并给出每步行号。
10. CSV 的写入发生在循环的哪一步？为什么说它是"边处理边写"？如果中途按 Ctrl+C，已经写下的数据会怎样？
11. `records` 与 CSV 在"存在形式、生命周期、内容形态、失败行样子、用途"五个方面有什么不同？
12. `summary`（第 562～586 行）里的 `processed_frames`、`detection_rate`、`longest_miss_run` 分别从哪里来？`compute_longest_miss_run()` 的算法思路是什么？
13. `check_csv_data()` 的 10 项检查（六组）分别是什么？它检查的是内存里的 `records` 还是磁盘上的 CSV 文件？调用方在哪个文件、哪些行？
14. CSV 如何构成离散时间序列？为什么相邻采样点间隔是 `1/fps`？失败行如何影响时间轴？
15. M3 视频与外部分析视频的 fps 分别是多少？请用两份真实 CSV 里的一行数据说明你如何得到这个结论。
16. M3 `_track.csv` 与 M6 `_trajectory.csv` 的共同设计思想有哪些（至少 4 条）？字段与记录范围的主要差异是什么（至少 4 条）？
17. 同名 `x_px` 在两份 CSV 里含义相同吗？这件事给"读懂字段"提出了什么要求？
18. 辨析下列材料属于"真实源码 / 教学伪代码 / 教学示例"中的哪一类：① 第 41 行 `CSV_FIELDNAMES`；② "打开 CSV → 写表头 → for 每一帧 → 写一行"这段流程；③ `4,0.066667,,,,False` 这行数据。为什么必须区分？

## 19. 一句话总结

> 逐帧检测得到的 `result` 只是"当前这一帧"的临时答案，循环一过就消失；L06 用 `CSV_FIELDNAMES`（第 41 行）定义字段、用 `build_csv_row()`（第 393～410 行）把每帧结果翻译成"frame, time_s, x_px, y_px, area_px, detected"一行、在 `track_video()`（第 413 行起）里边检测边写 `<视频名>_track.csv`（打开第 483 行、表头第 485 行、逐帧第 497 行、关闭第 541 行），失败时坚持"留空 + False、绝不写 0 / -1 / nan / 上一帧坐标"（第 399、410 行），同时用内存里的 `records` 做统计与自检（第 562～586、591～604、643～824 行）——于是每一个测量时刻都被如实保存下来，CSV 就成了"时刻齐全、缺失有标记"的离散时间序列；M3 的 `_track.csv`（6 列、质心、全片 170 行）与 M6 的 `_trajectory.csv`（8 列、暗带上缘 `y0_px` + bbox、正式区间 160 行）正是同一套记录规范在不同测量任务上的两次应用，也为后续的位移、周期与频率分析准备好了唯一可信的数据入口。

---

### 代码与事实来源说明

- 本笔记中的 M3 源码事实来自仓库内实际文件 `src\video_tracker.py`（共 836 行），按 2026-10-07 当前源码逐行核对：
  - 第 26 行：`import csv`；第 23 行：代码风格声明"不使用 class / 多线程 / 异步 / logging / pandas / scipy"；第 34 行：`from src.marker_detector import detect_marker`；
  - 第 40～41 行：表头注释与 `CSV_FIELDNAMES = ["frame", "time_s", "x_px", "y_px", "area_px", "detected"]`；
  - 第 393～410 行：`build_csv_row()`（第 399 行失败原则；第 401～409 行成功行；第 410 行失败行）；
  - 第 413 行：`def track_video(...)`；第 428 行 SHA-256；第 432 行 `open_video()`；第 437～441 行 fps 检查；第 444 行第一帧；第 465～467 行写入器；
  - 第 476 行：`records = []`；第 477～481 行其余账本与 `frame_index = 0`；
  - 第 483～485 行：打开 CSV / `csv.writer` / 写表头；第 488 行 `try:`；第 489 行 `while True:`；第 491 行 `detect_marker`；第 494 行 `time_s = frame_index / fps`；第 496～497 行写行；第 499～510 行 `records` 追加；第 513～521 行可视化；第 527～532 行读下一帧与推进；第 534～535 行进度；第 536～539 行 Ctrl+C；第 540～544 行 `finally`（第 541 行 `csv_file.close()`）；
  - 第 546 行计时；第 548～555 行 PNG 回退；第 557～560 行打印；第 562～586 行 `summary`；第 588 行 `return summary`；
  - 第 591～604 行 `compute_longest_miss_run()`；第 643～824 行 `check_csv_data()`（第 670～671、674～675、678～693、700～740、742～783、794～818、823～824 行；第 9 项为 `time_s` 时间轴一致性，第 10 项为失败字段语义对账）；第 827～836 行 `print_check_results()`。
- M6 对照事实来自 `src\external_oscillation_tracker.py`（共 661 行）：第 4、28 行模块说明；第 87～97 行 `CSV_FIELDNAMES`（8 项）；第 240～241 行 `x_px` 定义注释（暗带 bbox 中心，仅 QC）；第 319～332 行内存行字典（第 322～323 行 `time_s`、第 324 行 `detected`、第 330～331 行额外内存统计）；第 357～397 行 `write_trajectory_csv()`（第 361 行失败留空原则、第 366～369 行打开 / `DictWriter` / `writeheader()`、第 371～383 行成功行、第 384～396 行失败行）；第 400～423 行 `load_trajectory_csv()`（第 407～409 行 `DictReader`、第 417～419 行空字段 → `None`）；第 442～460 行表头自检；第 519～523 行 `time_s` 自检；第 639～641 行落盘与读回调用。该模块的检测算法细节不在本笔记范围内。
- 调用方信息：`demo\run_video_tracking.py` 第 24～29 行导入、第 35～38 行输入输出路径、第 43 行调用 `track_video()`、第 49 行 `print_statistics()`、第 52～58 行 `check_csv_data()` 与 `print_check_results()`。
- 真实产物（只读核对，未重新生成、未修改）：`results\EXP-002-VIDEO-001_track.csv`（表头 + 170 行数据，frame 0～169）与 `results\EXP-EXT-LAB67-V1_trajectory.csv`（表头 + 160 行数据，frame 76～235）；本笔记引用的两行真实数据均来自这两个文件的前几行。
- 本笔记中的教学伪代码（第 13.2 节流程块）与教学示例（第 6.2 节失败行示例、第 6.3 节反面写法）均为课堂教学材料，**不是项目实际数据、不是项目源码**；项目事实一律以"文件 + 函数 + 行号"定位。
- 关于项目其他 M3 类产物：`results\EXP-003-*-track.csv`、`results\EXP-004-DYNAMIC-001_track.csv` 等同样由 `video_tracker.py` 流程生成（本笔记只登记，未逐一核对内容）。
- 依赖范围：`requirements.txt` 只列 `opencv-python`、`numpy`、`matplotlib`，未包含 pandas；本笔记据此说明"CSV 读写与自检均使用标准库 `csv`"。
- 行号说明：以上行号按 2026-10-07 当前源码 `src\video_tracker.py`（共 836 行）核对；如果实际源码行号发生变化，以当前真实源码为准。
- 本笔记未运行任何 demo、未执行任何 Python 程序、未生成任何实验数据；只进行了源码与已有结果文件的只读检查，未修改 `src\`、`results\` 或任何代码 / 数据文件。

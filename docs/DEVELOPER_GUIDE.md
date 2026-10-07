# VisionMotion 开发者 / 科研使用指南

> **适用对象**：科研用户、实验人员、希望替换数据 / 复现实验 / 做二次开发的人。
> 如果你只是第一次使用、想把项目跑起来看结果，请先看 [用户使用指南](USER_GUIDE.md)。
>
> 本指南不逐行讲源码，重点是回答一个问题：
> **"如果我要把 VisionMotion 真正用于自己的实验 / 数据，应该怎么做？"**

## 1. 适合谁

- **普通用户**（第一次接触、只想跑起来）：请看 [用户使用指南](USER_GUIDE.md)，并优先运行 M6.3。
- **本指南面向**：
  - 想把自己的图片 / 视频换成项目输入的人；
  - 想理解参数、标定、QC、结果解释的人；
  - 想复现实验（结果复现 / 从原始数据重跑）的人；
  - 想理解 M2–M7 各模块职责并做二次开发的开发者。

一句话区分：**USER_GUIDE 讲"怎么用"，本指南讲"怎么把它用到你自己的实验上，以及哪些不能乱动"。**

## 2. 项目模块地图

| 模块 | 作用 | 输入 | 输出 | 用户是否直接操作 |
| --- | --- | --- | --- | --- |
| M2 · `src/marker_detector.py` | 红色标记检测（HSV 掩膜 → 轮廓 → 质心） | BGR 图像 | 检测结果字典（中心 `cx/cy`、面积、外接矩形、掩膜） | 通过 `demo/run_single_image_detection.py`（支持 `--input` / `--out-dir`） |
| M3 · `src/video_tracker.py` | 视频逐帧检测、记录时序坐标、生成叠加可视化 | 视频 + 输出路径 | `_track.csv`（像素坐标时序）+ overlay 视频 | 通过 `demo/run_video_tracking.py`（支持 `--input` / `--out-dir`） |
| M4 · `src/calibration.py` | 纯数学标定（两点 + 真实距离 → 尺度与方向） | 两个像素点 + 真实距离 | `k`（px/mm）、`u`（单位方向）、`project_point()` 一维投影 | 否（被标定脚本与 M4/M5 调用） |
| M4 · `src/displacement.py` | 静态位移链：track CSV → 位移 CSV（含 QC） | `_track.csv` | `_ds.csv`（`s_px / ds_px / ds_mm`） | 通过 `demo/run_m43_displacement.py` |
| M5 · `src/dynamic_displacement.py` | 动态位移链：track CSV → 位移 CSV + 转向点 / 运动段 | `_track.csv` | `_ds.csv` + 转向点与运动段统计 | 通过 `demo/run_m52_dynamic_displacement.py` |
| M6.2 · `src/external_oscillation_tracker.py` | 外部公开视频正式轨迹提取（冻结视觉规则） | 外部视频 | `_trajectory.csv`（`y0(t)` 像素轨迹，含 QC） | 通过 `demo/run_m62_external_tracking.py` |
| M6.3 · `src/m63_final_visualization.py` | 封板轨迹的可视化与一致性核对 | 封板 `_trajectory.csv` | 三张最终成果图 + 自检 | 通过 `demo/run_m63_final_visualization.py` |
| M7.3 · `src/m73_presentation.py` | 生成最终展示 PPT | 三张成果图 + 冻结数值 | `docs/VisionMotion_Final_Presentation.pptx` | **直接运行**（位于 `src/`，不是 demo） |

> 说明：M2 的 `marker_detector.py` 是**唯一检测实现来源**，M3 只调用它，不重复实现检测；M4/M5 也不重新实现投影公式（统一调用 `src/calibration.py` 的 `project_point()`）。
>
> 关于编号：M0–M7 是项目内部的实验 / 里程碑编号，**不是软件版本号**；编号允许跳号（例如没有单独的 M6.1），本表只列出用户可直接操作的模块。

## 3. 推荐科研工作流

```text
新实验数据
   ↓
M2（图片）/ M3（视频）
   ↓
质量检查（QC）
   ↓
M4 标定（人工点选 → 得到 k / u → 人工更新冻结常量）
   ↓
M4 位移（静态）
   ↓
M5 动态位移（转向点 / 运动段）
   ↓
M6.2 外部数据（如适用，独立链路）
   ↓
M6.3 展示 / 冻结结果
```

**必须注意：这条链路不是"必须全走一遍"。**

- **图片链**（M2）和**视频链**（M3 → M4 → M5）是**不同入口**：M2 只处理单张图，单张图不走位移/频谱链路。
- **外部公开视频链**（M6.2 → M6.3）是**独立链路**，与自采实验的标定、位移链互不共用常量。
- 只做"检测 / 跟踪"就够的实验，不需要 M4 / M5；只有需要毫米位移时才进入标定与位移链。

## 4. 如何替换自己的实验图片（M2）

M2 与 M3 使用**同一套命令行接口**；真正的检测仍然全部在 `src/marker_detector.py` 里。

### 1. 用户可输入（命令行参数）

```powershell
.\.venv\Scripts\python.exe demo\run_single_image_detection.py --input data\raw\my_image.jpg --out-dir results\my_image
```

| 参数 | 含义 | 说明 |
| --- | --- | --- |
| `--input` | 输入图片路径 | 不给则用默认 `data/raw/EXP-001-IMAGE-001.jpg` |
| `--out-dir` | 输出目录 | 不给则用默认 `results/`；目录不存在时自动创建 |
| `--overwrite` | 允许覆盖已存在的输出文件 | 属**文件管理行为**，不是实验参数；默认不覆盖 |

- **输出名由输入图片的 `stem` 派生**：`my_image.jpg` → `my_image_overlay.png` + `my_image_mask.png`。
  这样换图片时输出名会自动跟着变，不会再出现"换了图片却仍写成 `EXP-001-IMAGE-001_*`"的错位。
- **相对路径按项目根目录解析**（不是当前工作目录）；绝对路径原样使用。
- 不给 `--input` / `--out-dir` 时，行为与旧版完全一致：`EXP-001-IMAGE-001.jpg` → `results/EXP-001-IMAGE-001_overlay.png` / `_mask.png`。
  这是为兼容旧教程保留的默认行为；它**不启用**覆盖保护。
- `--overwrite` **只决定输出文件是否被覆盖**，与检测参数 / 检测逻辑无关。项目**没有**、也不应新增 `--no-verify` 之类的开关。

### 2. 冻结内容（不是命令行参数）

M2 的检测参数全部留在 `src/marker_detector.py`，**不通过 CLI 暴露**：

| 内容 | 位置 |
| --- | --- |
| HSV 双区间（`RED_LOWER_1/2`、`RED_UPPER_1/2`） | `src/marker_detector.py` |
| `MORPH_KERNEL_SIZE`、`MIN_AREA` | `src/marker_detector.py` |
| 最大轮廓策略（`RETR_EXTERNAL` + 按面积取最大） | `src/marker_detector.py` |
| 轮廓矩质心计算 | `src/marker_detector.py` |

CLI 只负责**输入与输出管理**。

### 3. 怎么判断结果

终端打印中心坐标 / 面积 / 外接矩形；输出目录下生成 `..._overlay.png`（叠加图）与 `..._mask.png`（掩膜图）。看到掩膜里目标区域是连通的白色块、叠加图方框套住目标，即视为检测合理。

> 只有在你要改**检测逻辑**（例如目标不是红色、阈值需要调整）时，才需要改 `src/marker_detector.py`。
> 那属于"换一套实验方案"，不是"换一张图片"。

### 4. 退出码（M2）

| 退出码 | 触发条件 |
| --- | --- |
| `0` | 图片处理完成，且 `detect_marker()["success"] is True` |
| `1` | 输入图片不存在 / `read_image()` 返回 None / `save_image()` 写入失败 |
| `2` | 目标输出已存在且未加 `--overwrite`；**argparse 参数用法错误默认也是 `2`**（码值重载，非本项目自定义） |
| `3` | 流程完成、mask 已写出，但 `detect_marker()["success"] is False`（该图未检出红色标记） |

> `save_image()` 的返回值**已被检查**：overlay 或 mask 任一写入失败都会返回 `1`，不再出现"打印成功但实际没写成功"。

> M2 与 M3 的参数语义完全对称，M3 的说明见 §5。

## 5. 如何替换自己的实验视频：M3

M3 现在**优先通过命令行参数提供用户输入**；真正的视频处理仍然全部在 `src/video_tracker.py` 的 `track_video()` 里，本轮没有改动任何检测 / 时间轴 / QC 逻辑。

### 1. 用户可输入（命令行参数）

```powershell
.\.venv\Scripts\python.exe demo\run_video_tracking.py --input data\raw\my_video.mp4 --out-dir results\my_video
```

| 参数 | 含义 | 说明 |
| --- | --- | --- |
| `--input` | 输入视频路径 | 不给则用默认 `data/raw/EXP-002-VIDEO-001.mp4` |
| `--out-dir` | 输出目录 | 不给则用默认 `results/`；目录不存在时自动创建 |
| `--overwrite` | 允许覆盖已存在的输出文件 | 属**文件管理行为**，不是实验参数；默认不覆盖 |

- **输出名由输入视频的 `stem` 派生**：`my_video.mp4` → `my_video_track.csv` + `my_video_overlay.mp4`。
  这样换视频时输出名会自动跟着变，不会再出现"换了视频却仍写成 `EXP-002-VIDEO-001_*`"的错位。
- **相对路径按项目根目录解析**（不是当前工作目录）；绝对路径原样使用。
- 不给 `--input` / `--out-dir` 时，行为与旧版完全一致：`EXP-002-VIDEO-001.mp4` → `results/EXP-002-VIDEO-001_*`。
  这是为兼容旧教程保留的默认行为；它**不启用**覆盖保护。
- `--overwrite` **只决定输出文件是否被覆盖**，与 SHA / QC / 冻结参数无关。项目**没有**、也不应新增 `--no-verify` 之类的校验开关。

### 2. 冻结内容（不是命令行参数）

| 内容 | 位置 | 为什么不是参数 |
| --- | --- | --- |
| 检测器参数（HSV 双区间、`MIN_AREA` 等） | `src/marker_detector.py` | 属检测方案本身；换目标颜色等于换方案，不是配置 |
| FPS | `src/video_tracker.py`（`cv2.CAP_PROP_FPS`） | 必须从视频文件实读，`time_s = frame_index / fps` |
| QC | `src/video_tracker.py` 的 `check_csv_data()` 等 | QC 是独立裁判，不能变成可配置项 |
| SHA | `src/video_tracker.py` 运行前后各自计算 | 证明程序没有改动原始视频；不设绕过开关 |

### 3. 输出

- `_track.csv`：逐帧的**像素坐标时间序列**（列：`frame, time_s, x_px, y_px, area_px, detected`）。
- overlay 视频：在每帧上画出检测到的目标，用于人工核对（文件名为 `<输入文件名>_overlay.mp4`）。

### 4. CSV QC

脚本调用 `src/video_tracker.py` 的 `check_csv_data()` 做完整性自检（表头、行数 = 实际解码帧数、frame 连续、`time_s` 与 `frame/fps` 一致、坐标/面积数值合理等）。QC 只是**核对**，不会替你修数据。

### 5. SHA 的适用范围（重要）

- M3 会在运行前后各算一次原始视频的 SHA-256，用来证明**程序没有改动你的原始视频**（前后一致即通过）。
- M5.2 / M6.2 等阶段还会把**某个特定冻结视频**的 SHA 写死在源码里作为"身份基准"。
- **新视频不能直接套用旧实验的 SHA**：SHA 是**文件身份**，不是"算法精度"。换视频后，你若要沿用冻结校验，就必须用你自己的新视频重新记录其应有的哈希基准（并清楚这属于你自己的新实验），**不要**指望旧脚本的旧哈希对新视频成立。

> **M3 的结果仍然是像素坐标**（`x_px` / `y_px`），**不是毫米位移**。毫米位移要经过 M4 标定与位移计算。

### 6. 退出码（M3）

| 退出码 | 触发条件 |
| --- | --- |
| `0` | `track_video()` 正常返回、`summary["track_integrity"] == "complete"`、`check_csv_data()` 通过、且 `summary["detected_frames"] > 0` |
| `1` | 输入视频不存在 / `track_video()` 返回 None / **`check_csv_data()` 未通过** |
| `2` | 目标输出已存在且未加 `--overwrite`；**argparse 参数用法错误默认也是 `2`** |
| `3` | 轨迹 `complete`、CSV 自检通过，但 `summary["detected_frames"] == 0`（全程零检出） |
| `4` | `summary["interrupted"] is True`：`track_video()` 的逐帧循环被 `KeyboardInterrupt` 中断（用户按 Ctrl+C） |
| `5` | `summary["track_integrity"]` 为 `"suspect"` 或 `"unverified"`：完整性存疑或未验证 |

判定优先级：**QC 未通过（`1`）> 用户主动中断（`4`）> 完整性未确认（`5`）> 全程零检出（`3`）> 正常成功（`0`）**。五处 `return` 都发生在全部终端输出之后，退出码只是追加的机器可读信号。

`track_integrity` 由 `src/video_tracker.py` 的 `track_video()` 产出，状态机如下（只使用三种证据：程序计数 `processed_frames`、容器声明 `declared_frame_count`、以及"seek 到声明末帧后再次 `read()`"这一次独立解码）：

| `track_integrity` | 条件 | 语义 |
| --- | --- | --- |
| `complete` | 非中断 + `processed_frames >= declared_frame_count` + 末帧 seek 成功 | 可按完整轨迹处理 |
| `suspect` | 非中断 + `processed_frames < declared_frame_count` + 末帧 seek 失败 | 完整性存疑（**不写作"确认不完整"**） |
| `unverified` | 判据不可用（`declared_frame_count <= 0`）或两个证据互相矛盾 | 完整性未验证 |
| `not_evaluated` | 用户 Ctrl+C（**不进行 seek**） | 未评估（由 `4` 表达） |

> `5` 只覆盖 `suspect` 与 `unverified` 两种状态；`not_evaluated` 永远走 `4`，不会变成 `5`。
> **完整性状态与 `detected_frames` 是两个正交维度**：`complete + 零检出` 是"完整视频但没有找到目标"（`3`），不是"视频不完整"；反过来 `suspect/unverified + 有检出` 也不能算成功（`5`）。

> `4` 的精确语义是"**逐帧循环被 Ctrl+C 中断退出**"，**不等同于程序崩溃**，也**不等于"必然少处理了帧"**（存在"最后一帧已处理完、Ctrl+C 恰好在离开 `try` 之前到达"的极窄窗口）。是否完整处理现在由 `track_integrity` 给出结论（见上表），仍可用统计里的"总帧数（文件声明）"与"实际处理帧数"人工复核。
> `interrupted` 由 `src/video_tracker.py` 的 `track_video()`（`except KeyboardInterrupt`）产生，`demo/run_video_tracking.py` 只读取 `summary["interrupted"]`；`track_video()` 的**中断捕获机制未被修改**，中断路径**不做完整性 seek**（状态固定为 `not_evaluated`，因此不会与 `5` 冲突）。

> 本轮**没有**引入"检出率 ≥ X%"阈值：部分漏检（例如 170 帧中检出 80 帧）仍然是 `0`，只有全程 `0 / N` 才是 `3`。
> `check_csv_data()` 仍只校验文件结构与字段语义（表头、行数、frame 连续、`time_s` 与 `frame/fps` 一致、空值语义、数值合法），它**不判断检出率**；"全程零检出"是 demo 层依据 `summary["detected_frames"]` 单独判定的。

## 6. 新视频的标定：M4（本指南最重要的一节）

标定回答一个问题：**"画面里 1 毫米对应多少像素？"** 只有先知道它，才能把像素位置换算成毫米位移。

### 第一步：用交互式脚本点选已知实际距离的两点

入口：`demo/pick_calibration_points.py`。

- 它打开 `data/raw/EXP-003-STATIC-002.mp4` 的第 900 帧（`VIDEO_PATH` / `FRAME_INDEX` 都是脚本里写死的）；
- 你依次点选 **P1 = 10 cm 刻线**、**P2 = 16 cm 刻线**（两点真实距离 `REAL_DISTANCE_MM = 60.0 mm`）；
- 它调用 `src/calibration.py` 的 `compute_scale()` 与 `unit_direction()`。

### 第二步：得到 `k` 与 `u`

终端会打印：

- `k`（`PX_PER_MM`，像素/毫米）与其倒数 `1/k`（`MM_PER_PX`，毫米/像素）；
- `u = (ux, uy)`（从 10 cm 指向 16 cm 的**单位方向向量**）。

### 第三步：认清一个关键事实

> **交互式脚本不会自动保存这些值。**

`pick_calibration_points.py` 只在终端打印 `k` 与 `u`，**不写文件、不写 CSV、不写配置、不写结果图**。也就是说：**点选脚本与后续 M4 / M5 位移管线之间没有自动衔接**——点完两个点，后面的位移计算不会自动"用上"这次结果。

### 第四步：按你的新实验，人工更新 M4 的冻结常量

后续位移计算使用的是**写死在源码里的实验专属冻结常量**。做新实验时，需要由你（高级用户）根据新的标定结果，人工更新：

`src/displacement.py`（M4 静态位移）中的冻结常量：

- `CALIB_P1_PX`、`CALIB_P2_PX`、`CALIB_REAL_DISTANCE_MM`（你实际点选的基准点与真实距离）
- `PX_PER_MM`、`MM_PER_PX`（由上面三点复算得到）
- `U`（单位方向）
- 以及配套的 valid gate（`AREA_MIN_PX / AREA_MAX_PX / Y_MIN_PX / Y_MAX_PX`）与 s0 规则（`S0_WINDOW_S / MIN_S0_VALID_FRAMES`）

> **不要简单复制旧实验的 `PX_PER_MM` / `U` / gate / s0 到新视频。**
> 这些值是**实验专属**的：它们和拍摄距离、焦距、分辨率、目标大小、释放/起始条件都有关。照搬旧值会得到**看起来正常、实际错误**的结果。

### 第五步：重新运行 M4 并检查 QC

```powershell
.\.venv\Scripts\python.exe demo\run_m43_displacement.py
```

运行时脚本会自动做两类核对：

- `check_calibration_constants()`：用你新的 `CALIB_P1_PX / CALIB_P2_PX / CALIB_REAL_DISTANCE_MM` **复算** `PX_PER_MM` / `MM_PER_PX` 并与常量比对，同时检查 `u` 是单位向量——所以如果你只改了标定点却没同步改 `PX_PER_MM` / `U`，自检会**报错并停止**；
- `check_ds_csv()`：对生成的 `_ds.csv` 做独立复算核对（详见第 11 节 QC 体系）。

> M4 / M5 都会先调用 M3 的 `track_video()`。若上游的 `track_integrity` 不是 `complete`，它们的处理方式（继续并警告 / 跳过）见 §7 末的「上游轨迹完整性如何影响 M4 / M5」。

### 为什么新数据必须重新标定

因为 `k`（px/mm）取决于**相机到目标的拍摄几何**：换视频、换机位、换焦距、换分辨率、改变拍摄距离，都会让"1 毫米 = 多少像素"发生变化。旧的 px/mm 只在旧拍摄条件下成立。

> 本项目当前**没有**把标定做成命令行参数或配置文件（这是设计选择，不是遗漏）。本指南**不**要求你改造为通用配置系统；做新实验时，按上面第四步人工替换常量并重跑 QC 即可。

## 7. M5 动态实验

### M5 与 M4 的关系

- M4 与 M5 都从 M3 的 `_track.csv` 出发，链路前半段相同（检测 → 像素坐标）。
- 差别在"后半段"：M4 面向**静态位移**（前 0.5 s 参考窗口 `s0`，gate 较宽）；M5 面向**动态往复运动**（前 2.0 s 参考窗口 `s0`、更严格的 gate，并额外做**转向点 / 运动段**统计）。

### 为什么动态实验有独立冻结常量

`src/dynamic_displacement.py` 中的常量（`PX_PER_MM_004`、`U_004`、`AREA_MIN_PX_004 / AREA_MAX_PX_004`、`Y_MIN_PX_004 / Y_MAX_PX_004`、`S0_WINDOW_S = 2.0`、`MIN_S0_VALID_FRAMES = 60`、`MIN_TURN_TRAVEL_PX = 20.0`）是 **EXP-004 专属**的，与 M4 的 EXP-003 常量**完全不同**。

模块设计上有一条**结构性要求**：`src/dynamic_displacement.py` **不得 `import src.displacement`**——目的就是从根上防止动态代码误用 M4 的 gate 与 s0 规则。因此，**不要为了"共享实验常量"去让 M5 简单 import M4 的模块**；当前设计要求实验常量**各自独立冻结**。（可在源码文件顶部的模块说明中看到这条约束。）

### s0、valid gate、turning point、segment（使用视角）

- **s0**：位移的零点参考。只使用起始窗口内**有效帧**的平均位置作为起点，窗口内有效帧不足时**不生成 `_ds.csv`**（属正常冻结行为）。
- **valid gate**：逐帧判断"这一帧的位置是否可信"（依赖检测成功、面积范围、y 位置范围）。`valid=False` 的位移字段**留空**，不会写 0 或补值。
- **turning point（转向点）**：在**原始 `x_px`** 序列上检测运动方向反转点，最小反向行程 `MIN_TURN_TRAVEL_PX = 20.0 px`；不平滑、不滤波、不插值。
- **segment（运动段）**：由起点、各转向点、终点切分出的区间；**运动段数 = 转向点数量 + 1**。

运行入口：

```powershell
.\.venv\Scripts\python.exe demo\run_m52_dynamic_displacement.py
```

> 本指南只讲"怎么用"。转向点 / 运动段的原理与教学推导属于学习材料，见 [源码学习课程索引](learning/COURSE_INDEX.md)，此处不重复。

### 上游轨迹完整性如何影响 M4 / M5

M4 / M5 的 demo 都会**自己调用 `track_video()`**，因此上游的完整性结论在**同一进程内已经存在**，直接读取 `track_summary["track_integrity"]` 即可，**不需要**（也不应该）从 `_track.csv` 反推——CSV 自洽不等于视频完整。

| `track_integrity` | M4 / M5 行为 |
| --- | --- |
| `complete` | 继续计算，无额外提示 |
| `suspect` | **继续计算 + warning**（终端提示"上游轨迹完整性存疑，使用结果前请人工核对"），并在 report 中标记 `track_integrity` |
| `unverified` | **继续计算 + warning**（同上，措辞为"未验证"） |
| `not_evaluated` | **跳过该视频的位移计算**：不调用 `run_experiment()`、不生成 `_ds.csv`、不伪造任何 displacement 指标，并打印明确原因；M4 的汇总里会单列"跳过" |

两条边界：

1. **不修改 CSV 格式**（`_track.csv` 与 `_ds.csv` 表头保持不变）；
2. **不重新判断上游完整性**，也不把 `EXPECTED_TRACK_ROWS`（EXP-004 专属冻结身份自检）改造成通用完整性机制。

M4 的完整性与检测质量是两个正交维度：`complete + 检出率低` 不等于轨迹可靠，`suspect + 检出率高` 也不能算可靠。

### M4 / M5 的退出码（Phase 5-2 Step 3）

M4（`demo/run_m43_displacement.py`）与 M5（`demo/run_m52_dynamic_displacement.py`）现在与 M2 / M3 一样，用 `raise SystemExit(main())` 提供**机器可读退出码**。只有 `0` 与 `1` 两档，**不新增 2 / 3 / 4**：

| 退出码 | 含义 |
| --- | --- |
| `0` | 本次入口要求执行的全部实验均成功完成，且每个**预期生成**的 `_ds.csv` 都已落盘 |
| `1` | 存在阻断性失败：输入视频不存在 / 视频无法处理 / 冻结常量自检未通过 / 上游 `track_integrity` 为 `not_evaluated` 导致实验被跳过 / 预期生成的 `_ds.csv` 未落盘 |

- M4 一次运行包含三个实验：**只要其中一个失败，整体就是 `1`**，不会因为其余实验成功而降级为 `0`；
- 两个与冻结语义一致的判断（不新增业务规则）：
  - 按冻结 s0 规则"窗口内有效帧不足因此不写 `_ds.csv`"是**预期结果**（终端打印为 `[注意] ... 按冻结规则不写`），在 M4 中**不计入**阻断性失败（例如 `EXP-003-STATIC-001` 本来就没有 `_ds.csv`）；而 EXP-004 的 `_ds.csv` 是 M5 的正式产物，**未生成即判 `1`**；
  - `suspect` / `unverified` 保持 Phase 5-1 语义：**继续计算位移 + 打印警告**，本轮**没有**把这两种状态升级为退出码 `1`。

终端输出与以前完全一致，退出码只是**追加**在最后的机器可读信号。在 PowerShell 中查看：

```powershell
.\.venv\Scripts\python.exe demo\run_m43_displacement.py
$LASTEXITCODE   # 0 = 全部预期实验成功；1 = 存在阻断性失败
```

### M4 / M5 会重新写入 results/ 中的输出（运行前请确认）

M4 / M5 是仓库内冻结实验的**重放入口**，输出目录固定为 `results/`，并且**默认允许重算**：

- 目标文件**不存在**时：正常执行，不打印任何覆盖提示；
- 目标文件**已存在**时：在真正写盘之前打印 `[警告] 输出文件已存在，将重新写入冻结结果：<路径>`，然后**继续执行**——不拒绝覆盖、不做交互、也没有新增命令行参数。

可能被重新写入的是各实验的 `<实验名>_track.csv`、`<实验名>_ds.csv`（其中 M4 的 `EXP-003-STATIC-001` 因冻结 s0 规则本来就不产生 `_ds.csv`）以及 `<实验名>_overlay.mp4`（该 mp4 被 `.gitignore` 忽略）。前两类是**已被 Git 跟踪的冻结结果**。

因此运行 M4 / M5 之前，请先确认工作区状态：

```powershell
git status --short
```

当前冻结结果的重算是**确定性**的（实测 `results/` 下已跟踪文件运行前后 SHA-256 逐字节一致），关键结果也有 SHA-256 校验；但如果你本地有**不希望被覆盖**的产物，请先自行备份，或在确认 `git status` 干净之后再运行。项目**不会**为了这个原因把 M4 / M5 改成默认拒绝覆盖。

## 8. M6.2 外部公开视频

### 外部数据与自采数据的区别

- **自采实验数据**：你自己拍摄的图片 / 视频，放在 `data/raw/`，其标定与结果属于你自己的实验。
- **外部公开数据**：第三方公开教育视频，放在项目根目录的 `_external/`（**注意：`_external/` 不在 `data/` 里面**），其来源、作者、许可、哈希记录在 [ATTRIBUTION.md](ATTRIBUTION.md)。

### 当前正式外部视频

- 正式使用的外部视频：`_external/_candidates/candidate_comPADRE_Lab67_01_Video1_51p5g.mp4`。
- 来源：ComPADRE / OSP（条目 ID 16081），许可 **CC BY-NC-SA 3.0**。
- 该视频在源码中被冻结校验：`src/external_oscillation_tracker.py` 的 `EXTERNAL_VIDEO_SHA256`（运行前校验，不一致立即停止）。
- 处理区间为 `frame 76–235`（`START_FRAME` / `END_FRAME` 冻结）。

### 得到的是什么

运行：

```powershell
.\.venv\Scripts\python.exe demo/run_m62_external_tracking.py
```

输出 `results/EXP-EXT-LAB67-V1_trajectory.csv`，列包含 `frame, time_s, detected, x_px, y0_px, bbox_w_px, bbox_h_px, area_px`。即：

> **M6.2 得到的是 `y0(t)` —— 像素位置轨迹。**

### 关键边界

**本项目没有为这段外部视频建立并应用有效的 px/mm 标定。** 因此：

> **不能把 M6.2 的输出直接写成毫米位移或振幅。**

它是以**像素**为单位的位置时间序列；把它当作毫米数据是错误用法。

## 9. M6.3 的科研意义

M6.3 的定位是：

```text
封板 trajectory CSV
   → 可视化
   → 一致性核对
   → 最终展示图
```

运行：

```powershell
.\.venv\Scripts\python.exe demo/run_m63_final_visualization.py
```

**它不是"运行时重新做 FFT"。** `src/m63_final_visualization.py` 使用**已封板的数值与极值清单**作图并做一致性核对，**不重新计算**周期 / 频率 / 极值 / FFT。

因此要正确理解：

- 报告中的周期 `T_exp = 0.542593 s`、频率 `f_exp = 1.843003 Hz`、FFT 主峰 `1.875 Hz` 等属于**冻结分析结果 / 展示层**；
- 它们**不等于** `m63_final_visualization.py` 每次运行时重新计算出来的值；
- 若要**重建**这些数值，需要按 [M6.3_FINAL_REPORT.md](M6.3_FINAL_REPORT.md) 中规定的规则（基于 160 点、30 Hz 的封板轨迹，"仅减均值后 rFFT"）自行实现 —— 这属于"从原始数据重新分析"，而不是本 demo 的默认行为。
- 当前项目**没有把 FFT 作为 M6.3 的运行时代码**：M6.3 的运行脚本只负责可视化与一致性核对，"可自行重建"不表示项目已提供现成的 FFT 实现。

## 10. 如何复现实验

有两种不同层次的"复现"：

### A. 结果复现（使用仓库内冻结数据）

- 直接使用仓库里已有的 `results/*.csv` 与 `results/*.png`；
- 运行 `demo/run_m63_final_visualization.py` 即可从封板轨迹**重新生成三张成果图**；
- 前提：仓库内数据未被修改，且本机具备所需中文字体。
- 这是"展示层复现"，**不涉及**从原始视频重跑算法。

### B. 从原始数据重新运行

- 需要：对应的**原始图片 / 视频**、正确的**参数**、正确的**标定**、以及每步的 **QC**；
- 图片链从 M2 起，视频链从 M3 起；需要毫米位移时才进入 M4 / M5；外部数据走 M6.2 独立链。
- **注意字节级一致性**：项目对部分上游产物（如 M5.3 的封板 `_ds.csv`）有 **SHA-256 冻结检查**。如果你重新生成上游 CSV，下游的冻结检查**可能**因字节不同而失败。
- 因此：**本指南不保证"重跑一定得到完全相同的 SHA"**。是否字节级一致，取决于生成过程的确定性（浮点舍入、换行、编码等）。遇到不一致时，应判断"这是否是新实验 / 新版本"，而不是强行删掉校验。

## 11. QC 体系

项目在每个阶段都内置**自动质量核对**（QC）。它们的作用是**发现问题**，不是自动修复问题。

| 阶段 | QC 函数 | 主要核对内容 |
| --- | --- | --- |
| M3 | `src/video_tracker.py` · `check_csv_data()` | 表头 / 行数 = 实际解码帧数 / frame 连续 / `time_s` 与 `frame/fps` 一致 / 坐标与面积数值合理性 |
| M4 | `src/displacement.py` · `check_ds_csv()` | 编码与换行、表头、行数与 frame 逐行一致、`valid` 与 gate 复算一致、空字段规范、小数位、`s0` 复算、`ds_px / ds_mm` 公式复算、成功率一致 |
| M5 | `src/dynamic_displacement.py` · `check_ds_csv()` | 在 M4 基础上增加 EXP-004 专属项（track 行数 = 1766、frame 0–1765 连续、`s0` 窗口与 `MIN_S0_VALID_FRAMES`、`ds` 公式容差、转向点相关统计） |
| M6.2 | `src/external_oscillation_tracker.py` · `check_trajectory_csv()` | 表头、行数、frame 严格 76–235、连续性、字段规范、检出率，以及**原始视频 SHA-256 完整性**（第 16 项） |

两条通用原则：

1. **QC 用来发现数据 / 参数 / 文件完整性问题，不是自动修复工具。** QC 未通过时应**定位原因**，而不是绕过或跳过。
2. **SHA-256 验证的是"冻结文件身份"，不是"算法精度"。** 它回答的是"你手上的文件是不是那个被冻结的版本"，与测量准不准无关。

## 12. requirements-dev 与测试

- **运行项目本身不需要 pytest**：`requirements.txt` 就是运行期依赖（opencv-python / numpy / matplotlib / Pillow / python-pptx）。
- 如果要运行 `tests/`，需要**额外**安装开发依赖（`requirements-dev.txt` 中固定 `pytest==9.1.1`，并通过 `-r requirements.txt` 引入运行期依赖）：

  ```powershell
  pip install -r requirements-dev.txt
  ```

  然后：

  ```powershell
  python -m pytest
  ```

- **当前 `.venv` 可能没有安装 pytest，这是正常的**，因为它不是运行期依赖。想看代码是否通过测试，请先按上面安装开发依赖。
- 说明：本指南**不**声称测试结果一定是最新的——是否通过取决于你当前的工作树状态；本阶段也没有在本机运行测试。

## 13. M7.3 PPT 入口

`src/m73_presentation.py` 是**科研 / 展示用户**的入口（用于生成最终展示材料），注意：

- 它**不是** `demo/` 下的普通入口，而是位于 `src/`，需要**直接运行**：

  ```powershell
  .\.venv\Scripts\python.exe src\m73_presentation.py
  ```

- 它使用 **python-pptx**（该依赖已经列入 `requirements.txt` 的 `python-pptx==1.0.2`，并在源码注释中同步标注）；
- 输入是**当前成果图 / 冻结结果**（三张成果图与封板数值）；
- 输出是 `docs/VisionMotion_Final_Presentation.pptx`。

> 本阶段不运行它、不重新生成 PPT。

## 14. 不要修改的东西

### 可以修改

- 你自己的实验数据（放进 `data/raw/`）；
- **M2 / M3 的输入路径请用命令行 `--input` / `--out-dir`，不要改源码**；其余 demo 仍改脚本内的路径常量；
- 针对**新实验重新标定**得到的常量（在 `src/displacement.py` / `src/dynamic_displacement.py` 中按新实验更新）；
- 实验专属冻结参数（高级用户，需自行承担"这是新实验"的责任并重跑 QC）。

### 不应随意修改

- **历史正式结果**（`results/` 里已封板的 CSV / PNG）；
- **外部数据 SHA**（`EXTERNAL_VIDEO_SHA256` 等冻结哈希）；
- **QC 逻辑**（`check_*` 系列函数）；
- **已封板实验数据与常量**（M4 / M5 中标注为"冻结"的常量）；
- **M6.2 的能力边界**（不要把 `y0(t)` 像素轨迹当作毫米位移）。

> 一句话原则：**如果确实要改变核心方法或换一套实验条件，应"新建版本 / 新实验"，而不是直接覆盖已冻结的结果。**

## 15. 目录与命名（认知说明）

### 目录

| 目录 | 用途 |
| --- | --- |
| `data/raw/` | 实验**原始输入**（你自己的图片 / 视频） |
| `results/` | 程序输出与已封板结果 |
| `_external/` | 第三方公开数据（**不在 `data/` 下**） |
| `data/processed/` | 当前版本**暂未**作为主要运行入口使用（保留目录） |

### CSV 后缀

| 文件后缀 | 当前用途 |
| --- | --- |
| `_track.csv` | M3 / M4 / M5 的视频检测轨迹（像素坐标时序） |
| `_ds.csv` | M4 / M5 的位移数据（`s_px / ds_px / ds_mm`） |
| `_trajectory.csv` | M6.2 的外部轨迹（`y0(t)`） |

`_track.csv` 与 `_trajectory.csv` 的差异是**模块历史设计差异，不代表错误**。本阶段**只说明、不重命名**：强行统一后缀可能影响冻结结果、文档引用与历史实验，因此保持不变。

> 补充：`data/raw/` 中还存在以下**历史 / 示例 / 非主入口文件**：`red_move.mp4`、`red_test.jpg`、`EXP-003-DYNAMIC-001.mp4`、`EXP-003-CAL-001.jpg`。它们**不是**当前 demo 的标准输入，**普通用户不要依赖这些文件作为教程输入**。本指南不处理它们（不删除、不移动、不改名）；请以"当前 demo 实际读取的文件名"为准。

---

**相关文档**：[用户使用指南](USER_GUIDE.md) · [README](../README.md) · [M6.3 阶段成果报告](M6.3_FINAL_REPORT.md) · [第三方数据来源与署名](ATTRIBUTION.md) · [项目说明书](../PROJECT_SPEC.md) · [源码学习课程索引](learning/COURSE_INDEX.md)

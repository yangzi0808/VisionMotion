# VisionMotion 用户使用指南

> 面向**第一次拿到 VisionMotion、不懂源码、计算机基础一般**的普通 Windows 用户。
> 目标：只照本文操作，就能从「下载项目」一路走到「看到自己的检测结果」，并且知道**为什么成功 / 为什么没检测到**。
>
> 想理解算法、标定、QC、数据替换等进阶内容，请看根目录 README 与 `docs/` 下的报告；本文最后一部分只做指路，不展开。

**本文的使用顺序（重要）：**

```text
第一部分：第一次使用（从下载到跑通环境）   ← 必须完整做完
第二部分：检测自己的图片（M2）
第三部分：检测自己的视频（M3）
第四部分：结果怎么看
第五部分：常见问题排查表
第六部分：高级实验流程（M4 / M5 / M6 / M7）  ← 第一次使用可以先跳过
```

第一次使用，请**按顺序只看前五部分**。

---

## 第一部分：第一次使用（从下载到跑通环境）

### 1. 这个项目是做什么的（30 秒）

VisionMotion 是一个用**普通摄像头视频**做**低成本、非接触式位移与振动测量**的教学型科研项目：

- 输入：一张图片，或一段视频；
- 处理：用 OpenCV 的颜色阈值 + 几何规则找到画面里的**红色标记**，得到它的**像素位置**；
- 输出：图片的叠加图 / 掩膜图；视频的**像素坐标时间序列 CSV** 与叠加视频。

**一句话**：这是一个「跑得通、讲得清、可复现」的教学型项目，**不是**通用目标跟踪工具，也**不是**计量级测量系统。

**它当前只认红色目标。** 如果你给的图片 / 视频里没有明显的红色目标，它**不会**"自动识别你想检测的东西"——这不是程序坏了，而是当前算法就是这么设计的（见第二部分 §10）。

### 2. 下载 VisionMotion

#### 方法 A：GitHub 网页下载 ZIP（推荐新手，不需要安装任何工具）

1. 打开项目页面：<https://github.com/yangzi0808/VisionMotion>
2. 点页面右上方的绿色 **`Code`** 按钮；
3. 在下拉菜单里点 **`Download ZIP`**；
4. 下载完成后，找到这个 `.zip` 文件（一般在「下载」文件夹），**右键 → 全部解压缩**（或「提取全部」）；
5. 解压后得到一个**文件夹**，例如 `VisionMotion-master`。

**注意：**

- 真正要用的，是**解压出来的文件夹**，不是那个 `.zip` 文件本身；
- 打开这个文件夹，里面的内容才叫「项目根目录」。

**检查：项目根目录里应该能看到这些**（至少要有前两个）：

```text
README.md
requirements.txt
demo\
src\
results\
data\
```

如果看不到 `README.md` 和 `requirements.txt`，说明**你打开的不是项目根目录**（可能多点进了一层，例如点进了 `src`）。请退回到同时能看到这两个文件的那一层。

#### 方法 B：Git clone（可选，仅限已安装 Git 的人）

如果你**已经会用 Git**，也可以：

```powershell
git clone https://github.com/yangzi0808/VisionMotion.git
cd VisionMotion
```

> **不会 Git 的人不需要安装 Git**，直接用上面的 ZIP 方法即可，效果完全一样。

### 3. 打开终端，并进入项目根目录

本文所有命令都在 **Windows PowerShell** 里执行（Windows 10 / 11 自带的「Windows Terminal / PowerShell」即可，不需要安装别的软件）。

先进入项目根目录，二选一：

#### 方法 A（最不容易走错目录）

1. 用文件资源管理器打开 VisionMotion 的**项目根目录**（就是能看到 `README.md`、`requirements.txt` 的那一层）；
2. 点击窗口上方的**地址栏**；
3. 输入 `powershell`，按 Enter。

这一步会自动打开一个 PowerShell，并且**当前目录就是项目根目录**。

#### 方法 B（手动切换目录）

打开 PowerShell，然后：

```powershell
cd "<你的 VisionMotion 文件夹路径>"
```

把 `<你的 VisionMotion 文件夹路径>` 换成你电脑上实际的路径（路径含空格时，两侧的引号要保留）。

#### 确认你在项目根目录

```powershell
Get-ChildItem
```

**看到 `README.md` 和 `requirements.txt` 才算正确。**

如果没看到：说明当前终端不在 VisionMotion 项目根目录，**不要继续**，先回到项目目录（用方法 A 最省事）。

### 4. 检查 Python（先检查，再决定怎么做）

先看看电脑上有没有可用的 Python：

```powershell
python --version
```

按结果分三种情况处理：

#### 情况 A：显示版本号

例如：

```text
Python 3.14.1
```

- 如果是 **Python 3.14.x** → 可以进入第 5 步；
- 如果**不是** 3.14.x（例如 3.11.x、3.12.x、3.13.x）→ 建议先不要继续，按下面「情况 C」处理。

#### 情况 B：提示找不到 python

例如（中文系统）：

```text
python : 无法将“python”项识别为 cmdlet、函数、脚本文件或可运行程序的名称...
```

（英文系统可能是 `'python' is not recognized as an internal or external command`）

→ **说明当前电脑没有可用的 Python 命令，需要先安装 Python 3.14.x。**

1. 打开 <https://www.python.org/downloads/>；
2. 下载 **Python 3.14.x** 的 Windows 安装包；
3. 安装时，**务必勾选 `Add python.exe to PATH`**（在安装向导第一页的最下面）；
4. 安装完成后，**关闭当前 PowerShell 窗口，重新打开一个新的 PowerShell**（不重开终端，版本信息不会刷新）；
5. 回到项目根目录，重新执行：

```powershell
python --version
```

直到出现正确的 `Python 3.14.x` 再继续。

> 小提示 1：如果执行 `python --version` 时**弹出了 Microsoft Store 界面**，说明这台电脑的 `python` 只是一个"占位符"，Python 并没有真正装好。请按上面步骤从 python.org 正式安装。
>
> 小提示 2：如果提示 `python` 找不到，但 `py --version` 能显示 3.14.x，说明 Python 装了、只是 `python` 命令没进 PATH。最省事的做法仍是按上面重新安装并勾选 `Add python.exe to PATH`；如果你已经熟悉命令行，也可以把后面的 `python` 换成 `py`。

#### 情况 C：版本不是 3.14.x

例如：

```text
Python 3.13.5
```

> 为避免依赖安装和运行出现兼容性问题，**建议安装并使用 Python 3.14.x**（本项目在 Python 3.14.1 上验证通过）。

你可以保留电脑上原有的 Python，只需**另外安装一个 3.14.x**；安装后用 `python --version` 确认显示的是 3.14.x 再继续。如果一时分不清哪个 Python 生效，最稳的办法是把系统里多余的旧 Python 卸载，只保留 3.14.x。

### 5. 创建虚拟环境 `.venv`

虚拟环境的作用：把 VisionMotion 需要的依赖装进一个**独立文件夹**，不污染电脑上其它 Python 项目。

```powershell
python -m venv .venv
```

**必须知道的一点：这条命令成功时，通常不会打印任何"成功"字样。**

- 只要命令跑完后**重新出现 PowerShell 提示符**、而且**没有红色报错**，一般就已经创建完成；
- 不要因为"没输出"而以为失败。

**立刻用下面这条命令确认：**

```powershell
Test-Path ".\.venv\Scripts\python.exe"
```

- 输出 `True` → 创建成功，进入第 6 步；
- 输出 `False` → 创建**没有**完成，回到第 4 步确认 Python 状态后重试。

**如果创建 venv 时报错，按下面处理：**

| 报错 | 含义 | 下一步 |
| --- | --- | --- |
| `No module named venv` | 当前 Python 安装不完整 / 不可用 | 重新安装 Python 3.14.x（安装保持默认组件），不要继续 |
| 权限错误（`Permission denied` / `拒绝访问`） | 当前文件夹不允许写入 | 把整个 VisionMotion 文件夹移动到你有写权限的普通位置，例如「下载」或「桌面」下属于你自己的文件夹，再重新执行本条命令 |
| 其它报错 | 无法判断 | 先不要继续，按第五部分排查表处理 |

> **不要**用"管理员身份"去改系统设置来解决权限问题。把项目放到自己有权写入的普通文件夹即可。

### 6. 安装依赖

**先确认 `.venv` 里的 Python 能用**（这一步同时也告诉你：后面真正运行项目用的是哪个 Python）：

```powershell
.\.venv\Scripts\python.exe --version
```

应显示 `Python 3.14.x`。

再确认 `.venv` 里的 pip 可用：

```powershell
.\.venv\Scripts\python.exe -m pip --version
```

应显示类似 `pip 25.x from ...\.venv\Lib\site-packages\pip`。

都正常后，安装项目依赖：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

（`requirements.txt` 共 5 项：opencv-python / numpy / matplotlib / Pillow / python-pptx。你不必逐个理解，装完就行。）

**正常情况**会看到类似下面这些（或其中一部分）：

```text
Collecting opencv-python==...
Downloading ...
Installing collected packages: ...
Successfully installed ...
```

```text
Requirement already satisfied: ...
```

上面这些都属于**正常**（第一次安装通常要下载 + 安装，联网情况下等一两分钟）。

**如果最后出现 `ERROR`：** 说明安装**没有完成**，请**先不要运行项目**。按第五部分排查表处理，常见原因有四类：

- Python 版本不兼容（不是 3.14.x）；
- 网络无法访问 PyPI（公司网络 / 代理 / 断网）；
- 文件夹权限问题；
- 某个依赖包下载或编译失败。

> **可选：激活虚拟环境。**
> 上面所有命令都用 `.\.venv\Scripts\python.exe` 直接调用虚拟环境里的 Python，**不激活也完全可以运行本项目**。
> 如果你**希望**像很多人习惯的那样"先激活再操作"，可以执行 `.\.venv\Scripts\Activate.ps1`（激活成功后提示符前会出现 `(.venv)`）。但这一步**不是必须的**：如果它报「禁止运行脚本 / 无法加载 Activate.ps1」，那是 PowerShell 的执行策略限制，**你不需要去修改系统策略**——直接忽略激活、继续按本文的 `.\.venv\Scripts\python.exe` 命令操作即可。

### 7. 环境安装成功检查

这一步用来一次性确认"依赖真的装好了"：

```powershell
.\.venv\Scripts\python.exe -c "import cv2, numpy, matplotlib, PIL; print('环境检查通过')"
```

**必须看到：**

```text
环境检查通过
```

看到 `环境检查通过`，说明运行 M2 / M3 / M6.3 需要的东西已经就位，可以进入第二部分。

> 如果你还打算生成成果 PPT（高级流程 M7.3），可以额外检查一下 `python-pptx`：
>
> ```powershell
> .\.venv\Scripts\python.exe -c "import pptx; print('pptx 检查通过')"
> ```
>
> 这一步对第一次使用**不是必须**的。

如果上面这条命令报 `ModuleNotFoundError`，说明第 6 步的依赖没装好，回到第 6 步重新安装。

### 8. 从下载到第一次成功运行：一页式清单

（把每一行都做完再往下走）

```text
1.  下载 ZIP 并解压                        → 得到 VisionMotion 项目文件夹
2.  进入项目根目录（能看到 README.md）      → cd "<你的路径>" 或 地址栏输入 powershell
3.  Get-ChildItem                          → 能看到 README.md 和 requirements.txt
4.  python --version                       → 必须是 Python 3.14.x
5.  python -m venv .venv                   → 没有输出正常，别慌
6.  Test-Path ".\.venv\Scripts\python.exe"  → 必须是 True
7.  .\.venv\Scripts\python.exe --version    → 显示 3.14.x
8.  .\.venv\Scripts\python.exe -m pip install -r requirements.txt   → 无 ERROR
9.  .\.venv\Scripts\python.exe -c "import cv2, numpy, matplotlib, PIL; print('环境检查通过')"
                                           → 显示 环境检查通过
10. 准备一张含红色目标的图片放进 data\raw\   → 见第二部分
11. 运行 M2（第二部分）                     → 看 results 里的 overlay / mask
12. 用 $LASTEXITCODE 判断结果                → 0 成功 / 3 没检测到 / 2 输出冲突 / 1 错误
13. 准备一段含红色目标的视频放进 data\raw\   → 见第三部分
14. 运行 M3（第三部分）                     → 看 results 里的 track.csv / overlay
```

---

## 第二部分：检测自己的图片（M2）

### 9. 放图片：把自己的素材放进 `data\raw\`

推荐做法：把你的图片复制到项目根目录下的 `data\raw\`：

```text
data\raw\my_red_object.jpg
```

要点：

- 文件名可以由你随便取（建议用英文 / 数字，避免奇怪符号）；
- **不需要**改任何源码；
- **不要**把素材放进 `src\`、`demo\` 或 `.venv\`；**不要**使用 `.data`；
- 项目里所有路径都以**项目根目录**为基准，`data\raw\` 才是推荐的用户输入位置；
- 如果你不想复制到这里也可以，运行命令时直接把路径写给 `--input`（绝对路径、或相对项目根目录的路径都行）。

### 10. 什么样的图片更容易成功（重要）

当前 M2 / M3 检测的是**红色目标**（在 HSV 颜色空间里提取红色区域，再取面积最大的连通块）。所以第一次测试，建议选这样的画面：

- 画面里有**明显的红色目标**；
- 红色目标**不要太小**（太小可能面积不足，被当成噪点忽略）；
- **背景里尽量不要有大片红色**（否则可能把背景当目标）；
- **光照不要极端**（过暗 / 过曝会让红色偏色）；
- 红色目标**没有被严重遮挡**。

**必须理解**：本项目当前**不是通用目标检测器**。

> 如果你给它一张没有红色目标的照片，它**不会**"自动识别你想检测的东西"。
> 这不是程序坏了，而是当前算法设计如此。

### 11. 第一次成功运行：图片

假设你已经把图片放成：

```text
data\raw\my_red_object.jpg
```

在**项目根目录**执行这一条命令（可整行复制）：

```powershell
.\.venv\Scripts\python.exe demo\run_single_image_detection.py --input ".\data\raw\my_red_object.jpg" --out-dir ".\results\my_image_test"
```

参数说明：

- `--input`：你的输入图片；
- `--out-dir`：输出目录（**不存在会自动创建**）；
- 输出文件名**自动跟随输入图片名**（`my_red_object.jpg` → `my_red_object_overlay.png`、`my_red_object_mask.png`），不会乱用别的名字；
- 如果这一步报"输出文件已存在"，先看下面 §13 的 `$LASTEXITCODE = 2`。

**运行过程中会看到什么：**

- 开头打印输入图片、输出目录、两个输出文件路径；
- 打印"已读取图像"与"图像尺寸：宽 ... px，高 ... px"；
- 如果检测到红色目标：打印 `检测成功`、中心坐标 `x = ... / y = ...`、面积、外接矩形，最后打印两个结果图片的保存路径；
- 如果**没有**检测到红色目标：打印 `检测失败：未检测到红色目标`（**注意：这不是崩溃**）。

**运行结束后，看退出码：**

```powershell
$LASTEXITCODE
```

### 12. 根据退出码判断发生了什么（M2）

| 退出码 | 含义 |
| --- | --- |
| `0` | 图片处理完成，**并且检测到目标** |
| `1` | 输入图片不存在 / 图片无法读取 / 结果写入失败等错误 |
| `2` | 目标输出已存在、但你没加 `--overwrite`（程序防止误覆盖）；另外命令参数写错时也是 `2` |
| `3` | 图片处理完成，但**没有检测到目标**（流程正常，只是没找到红色标记） |

### 13. 每种退出码下一步做什么

#### `$LASTEXITCODE` = `0`（成功，检测到目标）

打开输出目录（以本文命令为例是 `results\my_image_test\`），看两张图：

- `<名字>_overlay.png`：**叠加图** —— 在原图上画出红色目标的方框、中心点和坐标；
- `<名字>_mask.png`：**掩膜图** —— 只保留"被判为红色"的白色区域，用来检查分割是否合理。

用任意图片查看器打开即可。

#### `$LASTEXITCODE` = `3`（正常跑完，但没检测到）

**这不是程序失败**，而是当前这张图里没有找到符合条件的红色目标。按下面顺序排查：

1. 打开 `<名字>_mask.png`，看它是不是**几乎全黑**（全黑 = 没找到红色区域）；
2. 检查目标是不是**红色**（偏橙、偏粉、很暗的红可能落在阈值之外）；
3. 检查**背景是不是也有大片红色**（可能把背景当成目标，或反过来干扰）；
4. 检查目标是不是**太小 / 太暗 / 被遮挡**；
5. 换一张"红色更明显、背景更干净"的图片，重新运行。

#### `$LASTEXITCODE` = `2`（输出文件已存在）

程序为了**防止意外覆盖**上一次的结果，主动停下了。两种处理方式：

- **方案 A（第一次推荐）**：换一个输出目录，例如

  ```powershell
  .\.venv\Scripts\python.exe demo\run_single_image_detection.py --input ".\data\raw\my_red_object.jpg" --out-dir ".\results\my_image_test_2"
  ```

- **方案 B**：确认就是要覆盖旧结果时，加上 `--overwrite`：

  ```powershell
  .\.venv\Scripts\python.exe demo\run_single_image_detection.py --input ".\data\raw\my_red_object.jpg" --out-dir ".\results\my_image_test" --overwrite
  ```

> `--overwrite` **只决定是否覆盖输出文件**，与检测参数、检测逻辑无关。

#### `$LASTEXITCODE` = `1`（出错）

多为**输入文件不存在**、图片无法读取或写入失败。先确认路径对不对：

```powershell
Test-Path ".\data\raw\my_red_object.jpg"
```

- 输出 `False` → 输入路径错了（文件名 / 文件夹对不上），核对后重新运行；
- 输出 `True` → 再看终端最后打印的错误信息（例如"错误：无法读取图像：..."）。

---

## 第三部分：检测自己的视频（M3）

### 14. 放视频

和图片同理，推荐放到 `data\raw\`：

```text
data\raw\my_motion.mp4
```

- 文件名可以自己取；
- **不需要**改源码，也不需要放到 `src\` / `demo\` / `.venv\`，**不要**使用 `.data`；
- **推荐**视频里的目标也是**红色**，且整段视频目标都比较清晰（判断标准同 §10）。

### 15. 第一次成功运行：视频

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe demo\run_video_tracking.py --input ".\data\raw\my_motion.mp4" --out-dir ".\results\my_video_test"
```

参数含义与 M2 一致：

- `--input`：输入视频；`--out-dir`：输出目录（不存在会自动创建）；
- 输出名自动跟随视频名：`my_motion.mp4` → `my_motion_track.csv`、`my_motion_overlay.mp4`；
- 已存在同名输出且未加 `--overwrite` 时，会像 M2 一样停下（退出码 `2`）。

**运行过程中会看到什么：**

- 开头打印输入视频、输出目录、两个输出文件路径；
- 每处理 200 帧会打印一行"已处理 N 帧 ..."；
- 结束后打印一段统计（视频尺寸、FPS、总帧数、实际处理帧数、检出帧数、检出成功率、丢失帧数、area 最小/中位/最大、首末帧时间、耗时）；
- 打印 **CSV 数据完整性自检**结果；
- 打印 **原始视频完整性**（运行前后 SHA-256，确认原始视频没被改动）；
- 打印 **最终结果**：CSV 路径与行数、叠加视频路径（或"已回退保存 N 张代表性 PNG"）；
- 最后打印一行 **轨迹完整性**（`complete` / `suspect` / `unverified` / `not_evaluated`）。

**关于叠加视频**：M3 会生成一个**半尺寸**的 `_overlay.mp4`（在原视频上画出检测结果），方便快速核对"跟没跟上"。如果当前环境缺少可用的视频编码器，程序**不会中断**，而是**回退**保存最多 5 张代表性 PNG（文件名形如 `<名字>_overlay_frame0000_start.png`，标签可能是 `start` / `middle` / `end` / `fastest_motion` / `blurriest`）。只要 `_track.csv` 正常生成、终端提示已回退保存 PNG，这次追踪就算**正常完成**——回退只影响可视化视频，不影响 CSV。

**运行结束后，看退出码：**

```powershell
$LASTEXITCODE
```

### 16. 根据退出码判断发生了什么（M3）

| 退出码 | 含义 |
| --- | --- |
| `0` | 轨迹完整（`complete`）、至少检出过一次目标、且 CSV 自检通过 |
| `1` | 输入 / 视频处理错误，或 CSV 自检未通过 |
| `2` | 目标输出已存在且未加 `--overwrite`；命令参数写错也是 `2` |
| `3` | 轨迹完整、CSV 自检通过，但**全程没有检出到任何目标** |
| `4` | 你**主动按了 `Ctrl+C`** 中断逐帧处理 |
| `5` | 轨迹完整性**存疑或未验证**（`suspect` / `unverified`） |

**逐条解读：**

#### `0`（最理想）

视频正常处理完，轨迹完整，检出过目标，CSV 自检通过。去 `results\my_video_test\` 看 `my_motion_track.csv` 与 `my_motion_overlay.mp4`。

#### `3`（正常跑完，但全程没检测到目标）

和 M2 的 `3` 一样：**不是崩溃**，只是整段视频里没有一帧检出到红色目标。排查思路同 §13 的 `3`（目标是不是红色、是不是太小 / 太暗、背景是不是干扰）。注意：**部分漏检不会变成 3**；只有全程 0 检出才是 `3`。

#### `4`（你按了 Ctrl+C）

**不是程序崩溃**，而是**你自己主动停下来的**。程序会尽量保留已经处理的数据并正常收尾，但这次生成的 CSV / overlay **通常只覆盖到中断时的位置**，不能直接当成完整视频轨迹。**想得到完整结果，请重新运行一次。**

#### `5`（轨迹完整性存疑或未验证）

**不是崩溃，不是输入错误，不是 CSV 自检失败，也不是你按 Ctrl+C。** 它的意思是：

> 程序完成了本次处理，但**没有足够证据**把这份输出当作"已确认完整的视频轨迹"（终端会显示 `suspect` 或 `unverified`）。

请先按终端提示确认视频本身（例如文件是否完整、能否用播放器正常播放到结尾），然后**重新运行**。

#### `1`（错误）

多为输入视频不存在、视频无法打开 / 处理，或 CSV 自检没通过。先核对：

```powershell
Test-Path ".\data\raw\my_motion.mp4"
```

`False` 说明路径不对；`True` 则看终端最后打印的错误信息。

#### `2`（输出冲突）

处理方式与 M2 §13 的 `2` 完全相同：**换输出目录**，或确认后加 `--overwrite`。

> **再次提醒**：M3 得到的是**像素坐标**（`x_px` / `y_px`），**不是毫米位移**。把像素换算成毫米需要标定，属于 M4 / M5 的高级流程（第六部分）。

---

## 第四部分：结果怎么看

### 17. 输出文件在哪里

都在你指定的 `--out-dir` 下（本文示例是 `results\my_image_test\` 与 `results\my_video_test\`）。

- M2（图片）：`<名字>_overlay.png`、`<名字>_mask.png`；
- M3（视频）：`<名字>_track.csv`、`<名字>_overlay.mp4`（或回退的若干 `<名字>_overlay_frameXXXX_*.png`）。

### 18. 图片怎么看

- **overlay（叠加图）**：在原图上标出检测结果（方框、中心、坐标），用来判断"检测到的东西对不对"；
- **mask（掩膜图）**：把满足红色条件的像素涂成白色、其余为黑，用来判断"分割是否合理"。几乎全黑 = 没找到红色。

### 19. 视频结果怎么看

#### `_track.csv`（最重要）

每行对应视频中的一帧，各列含义：

| 列 | 含义 |
| --- | --- |
| `frame` | 第几帧（从 0 开始） |
| `time_s` | 该帧时间，单位秒（= 帧号 ÷ 帧率） |
| `x_px` | 目标中心的横向像素坐标 |
| `y_px` | 目标中心的纵向像素坐标（向下为正） |
| `area_px` | 目标区域的像素面积（大致反映目标大小） |
| `detected` | 这一帧是否检测成功（`True` / `False`） |

一句话：**这是一张"目标什么时候在哪里"的表格**。用 Excel 就能打开；横轴取 `time_s`、纵轴取 `x_px`（或 `y_px`）画曲线，就能看出目标怎么运动。**这是后续位移 / 轨迹分析最重要的结构化结果。**

> 检测失败的那一帧，`x_px` / `y_px` / `area_px` 会**留空**、`detected` 为 `False`（程序不会用 0 或上一帧的值来"假装"测到了）。

#### `_overlay.mp4`

在原视频上叠加检测结果，适合**直观看程序到底跟没跟上**（半尺寸）。

---

## 第五部分：常见问题排查表

### 20. 安装 / 环境类

| 现象 | 原因 | 下一步 |
| --- | --- | --- |
| `python is not recognized` / 无法识别 `python` | Python 未安装或未加入 PATH | 安装 Python 3.14.x（勾选 `Add python.exe to PATH`），**关闭并重开终端** |
| 执行 `python --version` 弹出 Microsoft Store | `python` 只是占位符，未真正安装 | 从 <https://www.python.org/downloads/> 正式安装 3.14.x |
| `Python 3.13.x` 等旧版本 | 不是本项目推荐环境 | 安装并使用 Python 3.14.x，再用 `python --version` 确认 |
| `python -m venv .venv` 后**没有任何输出** | 正常现象 | 用 `Test-Path ".\.venv\Scripts\python.exe"` 确认，`True` 即成功 |
| `Test-Path` 输出 `False` | venv 创建失败 | 回到第 5 步；先确认 `python --version` 是 3.14.x，再重试 |
| `No module named venv` | Python 安装不完整 | 重新安装 Python 3.14.x，不要继续 |
| `Activate.ps1` 被阻止 / 禁止运行脚本 | PowerShell 执行策略 | **不要改系统策略**，直接用 `.\.venv\Scripts\python.exe` 命令（本文主流程）即可 |
| `.\.venv\Scripts\python.exe` 不存在 | venv 没建好 | 回到第 5 步重新创建 |
| `pip install` 出现 `ERROR` | 网络 / Python 版本 / 权限 / 依赖问题 | 先**不要运行项目**：确认 Python 是 3.14.x、网络能访问 PyPI、文件夹可写，再重试 |
| 运行环境检查报 `ModuleNotFoundError` | 依赖没装全 | 回到第 6 步重新执行 `pip install -r requirements.txt` |

### 21. 运行 / 结果类

| 现象 | 原因 | 下一步 |
| --- | --- | --- |
| `错误：输入图片不存在：...` | 图片路径不对 | `Test-Path ".\data\raw\你的文件名"`，`False` 就核对路径 |
| `错误：输入视频不存在：...` | 视频路径不对 | 同上 |
| 退出码 `3` | 没有检测到目标（流程正常） | 检查目标是否为红色、是否太小 / 太暗、背景是否有大片红色 |
| 退出码 `2` / "目标输出文件已存在" | 上次输出还在，程序防误覆盖 | 换 `--out-dir`，或确认后加 `--overwrite` |
| 退出码 `4` | 你按了 `Ctrl+C` | 重新运行，让视频完整处理 |
| 退出码 `5`（`suspect` / `unverified`） | 轨迹完整性无法充分确认 | 先按终端提示确认视频本身完整、能正常播放到结尾，再重新运行 |
| 叠加视频没生成，出现若干 `_overlay_frameXXXX_*.png` | 当前环境没有可用视频编码器 | 属正常回退；只要 `_track.csv` 正常就代表追踪成功 |
| 中文字体缺失导致出图失败 | 缺少中文字体 | 安装微软雅黑（Microsoft YaHei）即可；普通用户只用 M2 / M3 时通常用不到 |

> 更完整的排错清单，见根目录 [README 的「常见问题 / FAQ」](../README.md#18-常见问题--faq排错入口)。

---

## 第六部分：高级实验流程（M4 / M5 / M6 / M7）

> **第一次使用可以先跳过这一部分。** 下面这些流程涉及标定、冻结常量、第三方视频与频域分析，属于科研 / 开发用户的进阶内容，本文只做指路，不展开操作步骤。

### 22. 项目里的三类内容（先说清楚，避免误会）

| 类别 | 含义 | 例子 |
| --- | --- | --- |
| 当前真实运行能力 | 现在用源码 / demo 真能跑出来的东西 | M2 / M3 的可运行脚本 |
| 冻结实验结果 | 已经封板、写进报告与结果的数值 | `results/EXP-EXT-LAB67-V1_*` 的周期 0.542593 s、频率 1.843003 Hz |
| 教学 / 历史实验 | 学习文档中的例子，不代表当前通用能力 | `docs/learning/` 下的课程笔记 |

> 关于编号：M0–M7 是项目内部的实验 / 里程碑编号，**不是软件版本号**；编号允许跳号（例如没有单独的 M6.1），这里只列出与使用者相关的里程碑。

### 23. M4 / M5：毫米级位移

- M4 用**静态标定**把像素换算成毫米位移；M5 做**动态位移 / 运动轨迹**；
- 两者都依赖 `data/raw/` 里的**自采实验数据**（不随仓库分发），并且使用**写死在源码里的冻结标定常量**；
- **更换实验视频后，不能直接套用旧标定**：高级用户需要根据新的标定结果人工更新源码中的冻结常量（及相应门限），再重新跑脚本内置的 QC 自检；
- M4 / M5 会先看上游 M3 轨迹的完整性：`suspect` / `unverified` 时**继续计算但给出警告**；`not_evaluated`（用户主动中断）时**跳过该视频的位移计算、不生成 `_ds.csv`**；
- **注意：M4 / M5 默认会重新写入 `results/` 里的结果文件**（输出目录固定是 `results/`）。运行前请先看一下工作区状态：

  ```powershell
  git status --short
  ```

  确认没有需要保留的改动后再运行。完整说明见 [开发者 / 科研使用指南](DEVELOPER_GUIDE.md) 与 README §8「标定说明」。

### 24. M6.2 / M6.3：外部视频与最终成果图

- M6.2 用**第三方公开教育视频**按冻结规则提取正式轨迹；该视频**不随仓库分发**，需要你自己准备；
- M6.3 使用**仓库内已封板的轨迹 CSV** 生成最终成果图（三张 PNG），**不需要外部视频**；
- **M6.3 不会重新计算周期 / 频率 / FFT**，它做的是可视化与一致性核对，用的是封板数值；
- 运行方式（进阶）：

  ```powershell
  .\.venv\Scripts\python.exe demo\run_m63_final_visualization.py
  ```

  成功时终端会打印三张图路径，并以 `自检结论：全部通过` 收尾。

### 25. M7.3：生成成果 PPT

- 入口是 `src\m73_presentation.py`（**不在 `demo\` 下**）：

  ```powershell
  .\.venv\Scripts\python.exe src\m73_presentation.py
  ```

- 它使用仓库内的成果图与冻结结果生成 `docs/VisionMotion_Final_Presentation.pptx`。

### 26. 进一步阅读

- 标定流程，以及"点选结果不会自动进入后续管线"：README §8「标定说明」；
- 模块 / 参数 / QC / 结果解释：根目录 README 与 [M6.3_FINAL_REPORT.md](M6.3_FINAL_REPORT.md)；
- 更换数据、复现实验、二次开发：[开发者 / 科研使用指南](DEVELOPER_GUIDE.md)；
- 分阶段原理讲解（源码 / 课程化学习）：[课程索引 COURSE_INDEX](learning/COURSE_INDEX.md)。

---

## 附：能力边界（请务必了解）

### 你现在可以安全做的事情

- 运行 **M2 / M3**（检测图片、跟踪视频中的红色目标）；
- 运行 **M6.3**（查看最终成果图）；
- 用 Excel 或任意工具**查看 CSV**、用图片查看器**查看 PNG**。

### 请不要做的事情

1. **不要随便改"冻结"参数**：源码里的标定常量、有效门限（valid gate）等是实验封板值，改动会让结果无法追溯；
2. **不要把外部视频当成已标定的毫米数据**：M6.2 / M6.3 用的是**像素位置**；本项目当前**未**为那段外部视频建立有效的 px/mm 标定；
3. **不要把 M6.3 的周期 / 频率当成"每次运行重新算出来"**：那是**封板数值**，M6.3 只做可视化与一致性核对；
4. **不要删除 SHA-256 校验来"解决错误"**：校验失败说明输入不是对应版本，删掉只会让结果失真；
5. **不要以为换一段新视频就会自动得到同样的周期 / 频率**：换视频需要重新采集、重新标定、重新评估，不能照搬旧结果。

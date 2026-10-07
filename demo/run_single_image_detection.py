"""
VisionMotion —— M2.3 演示脚本

功能：读取一张真实图片，调用 src/marker_detector.py 检测红色标记，
      在终端打印检测结果，并把可视化结果保存为 overlay 图与 mask 图。

本脚本只负责：
    1. 决定输入图片路径（命令行参数，或向后兼容的默认值）
    2. 决定输出目录，并由输入图片的文件名派生输出文件名
    3. 调用原来的 detect_marker() 与原来的绘图逻辑
    4. 打印最终结果

运行方式（在项目根目录下）：

    1）无参数：完全保持旧行为
    .venv\\Scripts\\python.exe demo\\run_single_image_detection.py
       -> 输入 data/raw/EXP-001-IMAGE-001.jpg
       -> 输出 results/EXP-001-IMAGE-001_overlay.png
                 results/EXP-001-IMAGE-001_mask.png

    2）指定输入图片：输出文件名自动跟随输入文件名
    .venv\\Scripts\\python.exe demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg
       -> 输出 results/my_image_overlay.png
                 results/my_image_mask.png

    3）指定输出目录（目录不存在会自动创建）
    .venv\\Scripts\\python.exe demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg --out-dir results\\my_image
       -> 输出 results/my_image/my_image_overlay.png
                 results/my_image/my_image_mask.png

    4）目标文件已存在时，必须显式允许覆盖
    .venv\\Scripts\\python.exe demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg --overwrite

路径规则：
    绝对路径原样使用；相对路径一律相对项目根目录解析（不依赖当前工作目录），
    因此在任何工作目录下运行，上面这些示例命令都能照抄使用。

冻结边界（本脚本不提供、也不得新增对应命令行参数）：
    检测参数（HSV 双区间 / MORPH_KERNEL_SIZE / MIN_AREA）、最大轮廓策略、
    质心计算全部留在 src/marker_detector.py 内。本脚本只把「输入图片」与
    「输出目录」两个用户输入交给原来的 read_image() / detect_marker() / 绘图流程。

退出码（供脚本 / 自动化判断；终端输出仍保留全部细节）：
    0 = 图片处理完成，且检测到目标
    1 = 输入 / 图片处理 / 结果写入错误
    2 = 输出文件已存在（未加 --overwrite）；argparse 参数用法错误默认也是 2
    3 = 图片处理完成，但没有检测到目标（流程正常，只是没找到红色标记）
"""

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np

# 把项目根目录加入 Python 的模块搜索路径，
# 这样 demo 目录下的脚本才能 import 到 src 目录里的模块。
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.marker_detector import detect_marker  # noqa: E402

# ============================================================
# 默认输入输出（只用于「无参数运行」，保持旧行为）
# ============================================================

DEFAULT_INPUT_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-001-IMAGE-001.jpg"
DEFAULT_OUT_DIR = PROJECT_ROOT / "results"


def parse_args(argv=None):
    """
    解析命令行参数。

    只暴露两个用户输入（输入图片、输出目录）和一个输出覆盖开关；
    检测参数（HSV / MIN_AREA / 形态学 / 轮廓 / 质心）一律不作为参数出现。
    """
    parser = argparse.ArgumentParser(
        prog="run_single_image_detection.py",
        description=(
            "VisionMotion M2.3：读取一张图片，检测红色标记，"
            "打印中心坐标并保存 overlay / mask 两张结果图。"
        ),
        epilog=(
            "示例：\n"
            "  python demo\\run_single_image_detection.py\n"
            "      无参数运行（保持旧行为）：输入 data\\raw\\EXP-001-IMAGE-001.jpg，输出到 results\\\n"
            "  python demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg\n"
            "      输出 results\\my_image_overlay.png 与 results\\my_image_mask.png\n"
            "  python demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg --out-dir results\\my_image\n"
            "      输出目录不存在时自动创建\n"
            "  python demo\\run_single_image_detection.py --input data\\raw\\my_image.jpg --overwrite\n"
            "      目标文件已存在时允许覆盖（默认发现同名输出就停止）\n"
            "\n"
            "路径说明：相对路径一律相对项目根目录解析，绝对路径原样使用。\n"
            "冻结说明：HSV / MIN_AREA / 形态学 / 轮廓 / 质心等检测参数均不是命令行参数。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--input",
        metavar="IMAGE",
        default=None,
        help="输入图片路径（默认：data\\raw\\EXP-001-IMAGE-001.jpg）",
    )
    parser.add_argument(
        "--out-dir",
        metavar="DIR",
        default=None,
        help="输出目录（默认：results\\；目录不存在时自动创建）",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="允许覆盖已存在的输出文件（默认：发现同名输出文件就停止）",
    )
    return parser.parse_args(argv)


def resolve_user_path(path_text, default_path):
    """
    把用户给的路径解析成绝对路径。

    规则：
        - 未提供（None）  -> 返回默认路径
        - 绝对路径        -> 原样使用
        - 相对路径        -> 相对项目根目录解析（不依赖当前工作目录）
    """
    if path_text is None:
        return default_path

    path = Path(path_text)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def build_output_paths(input_path, out_dir):
    """
    由输入图片的文件名派生输出文件名（取 Path.stem，即不含扩展名的部分）。

    例：foo.JPG -> <out_dir>/foo_overlay.png、<out_dir>/foo_mask.png
    这样换输入图片时，输出名会自动跟着变，不会再冒充 EXP-001-IMAGE-001。
    """
    stem = input_path.stem
    return out_dir / ("%s_overlay.png" % stem), out_dir / ("%s_mask.png" % stem)


def read_image(path):
    """
    读取一张图片。

    说明：Windows 上 cv2.imread 无法读取含中文的路径（本项目路径里有中文），
    所以先用 np.fromfile 把文件读成字节，再用 cv2.imdecode 解码。
    读取失败时返回 None。
    """
    file_bytes = np.fromfile(str(path), dtype=np.uint8)
    if file_bytes.size == 0:
        return None
    return cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)


def save_image(path, image):
    """
    保存一张图片。

    说明：与 read_image 同理，cv2.imwrite 在中文路径下会失败，
    所以先用 cv2.imencode 编码，再把字节写入文件。
    """
    success, encoded = cv2.imencode(path.suffix, image)
    if not success:
        return False
    encoded.tofile(str(path))
    return True


def draw_overlay(image_bgr, result):
    """
    在原图的副本上画出检测结果。

    画三样东西：外接矩形、目标中心点（圆圈 + 十字）、中心坐标文字。
    注意：这里操作的是副本，原图不会被修改。
    """
    overlay = image_bgr.copy()

    x, y, w, h = result["bbox"]
    cx = result["cx"]
    cy = result["cy"]
    center = (int(round(cx)), int(round(cy)))

    # 外接矩形（绿色）
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), 3)

    # 中心点：圆圈 + 十字（绿色）
    cv2.circle(overlay, center, 12, (0, 255, 0), 3)
    cv2.drawMarker(overlay, center, (255, 0, 0), cv2.MARKER_CROSS, 40, 3)

    # 中心坐标文字（写在矩形上方，注意别超出图像顶部）
    text = "center = (%.1f, %.1f) px" % (cx, cy)
    text_y = y - 20
    if text_y < 30:
        text_y = y + h + 40
    cv2.putText(
        overlay,
        text,
        (x, text_y),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    return overlay


def main():
    args = parse_args()

    input_path = resolve_user_path(args.input, DEFAULT_INPUT_PATH)
    out_dir = resolve_user_path(args.out_dir, DEFAULT_OUT_DIR)
    overlay_path, mask_path = build_output_paths(input_path, out_dir)

    # 用户是否显式给出了新的输入 / 输出位置。
    # 两者都没给 = 旧的无参数运行方式：旧的 EXP-001 输出本来就在 results/ 里，
    # 必须继续允许运行，否则会破坏 README / USER_GUIDE 里已有的教程命令。
    user_gave_new_paths = (args.input is not None) or (args.out_dir is not None)

    print("========== VisionMotion M2.3 单图红色标记检测 ==========")
    print("输入图片：%s" % input_path)
    print("输出目录：%s" % out_dir)
    print("输出 overlay：%s" % overlay_path)
    print("输出 mask：%s" % mask_path)
    if not user_gave_new_paths:
        print("运行方式：无参数（保持旧行为：固定 EXP-001 图片，输出到 results/）")
    print("")

    # 1. 输入图片必须存在（避免 np.fromfile 直接抛 traceback）
    if not input_path.is_file():
        print("错误：输入图片不存在：%s" % input_path)
        print("提示：--input 可用绝对路径，或写相对项目根目录的路径（例如 data\\raw\\my_image.jpg）。")
        return 1

    # 2. 覆盖保护：只在用户显式换了输入 / 输出位置时启用。
    #    目的：换图片时不会静默覆盖上一次的结果；旧的无参数运行不受影响。
    if user_gave_new_paths and not args.overwrite:
        existing_files = [item for item in (overlay_path, mask_path) if item.exists()]
        if existing_files:
            print("错误：目标输出文件已存在，已停止（不覆盖已有结果）：")
            for item in existing_files:
                print("  %s" % item)
            print("处理方式（二选一）：")
            print("  1) 换一个输出目录：--out-dir <DIR>")
            print("  2) 确认要覆盖已有结果：加 --overwrite")
            print("说明：--overwrite 只决定是否覆盖输出文件，与检测参数 / 检测逻辑无关。")
            return 2

    # 3. 输出目录：不存在则创建
    out_dir.mkdir(parents=True, exist_ok=True)

    # 4. 读取图片
    image = read_image(input_path)
    if image is None:
        print("错误：无法读取图像：%s" % input_path)
        return 1

    height, width = image.shape[0], image.shape[1]
    print("已读取图像：%s" % input_path)
    print("图像尺寸：宽 %d px，高 %d px" % (width, height))
    print()

    # 5. 检测红色标记（检测逻辑唯一来源：src/marker_detector.py）
    result = detect_marker(image)

    if not result["success"]:
        print("检测失败：未检测到红色目标")
        # 保存掩膜，方便查看是哪个环节出了问题
        if not save_image(mask_path, result["mask"]):
            print("错误：掩膜图写入失败：%s" % mask_path)
            return 1
        # 流程正常跑完，但整张图没有检出目标 -> 退出码 3
        return 3

    # 6. 打印检测结果
    x, y, w, h = result["bbox"]
    print("检测成功")
    print("中心坐标：")
    print("x = %.1f px" % result["cx"])
    print("y = %.1f px" % result["cy"])
    print()
    print("面积：")
    print("%.1f px" % result["area"])
    print()
    print("外接矩形：")
    print("x = %d px" % x)
    print("y = %d px" % y)
    print("w = %d px" % w)
    print("h = %d px" % h)
    print()

    # 7. 生成并保存可视化结果
    overlay = draw_overlay(image, result)
    if not save_image(overlay_path, overlay):
        print("错误：overlay 图写入失败：%s" % overlay_path)
        return 1
    if not save_image(mask_path, result["mask"]):
        print("错误：掩膜图写入失败：%s" % mask_path)
        return 1

    print("已保存结果图片：")
    print(overlay_path)
    print(mask_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

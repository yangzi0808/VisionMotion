"""
VisionMotion —— M4.3-1 标定工具：人工点选 10 cm / 16 cm 刻线

功能（只做这些）：
    1. 用 cv2.VideoCapture 打开 data/raw/EXP-003-STATIC-002.mp4（只读）
    2. 打开自动旋转：cv2.CAP_PROP_ORIENTATION_AUTO = 1
    3. 跳到 frame = 900，读取并显示这一帧
    4. 用户在窗口里用鼠标左键点两个点：
           第 1 次点击 -> P1 = 10 cm 刻线
           第 2 次点击 -> P2 = 16 cm 刻线
    5. 图上显示 P1 / P2 / 连线 / 坐标 / 文字（P1 = 10 cm，P2 = 16 cm）
    6. 按 r 重置重选；按 Enter 或 q 确认
    7. 调用 src/calibration.py 的 compute_scale() 和 unit_direction()，打印 k 与 u

明确不做的事情：
    不自动识别刻线、不做 OCR、不用颜色检测找尺子、不修改原始视频、
    不保存结果图片、不写 CSV、不写配置文件。

运行方式（在项目根目录下）：
    .venv\\Scripts\\python.exe demo\\pick_calibration_points.py

代码风格：普通函数 + 一个全局点列表 + OpenCV 鼠标回调，不使用 class / 多线程 / argparse。
"""

import math
import sys
from pathlib import Path

import cv2

# 把项目根目录加入模块搜索路径，这样 demo 里的脚本才能 import 到 src 里的模块
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.calibration import compute_scale, unit_direction  # noqa: E402

# ============================================================
# 固定参数
# ============================================================

# 正式标定输入：真实视频（不是 EXP-003-CAL-001.jpg，那张图片坐标系不同）
VIDEO_PATH = PROJECT_ROOT / "data" / "raw" / "EXP-003-STATIC-002.mp4"

# 标定使用的帧号
FRAME_INDEX = 900

# 10 cm 刻线到 16 cm 刻线的真实距离
REAL_DISTANCE_MM = 60.0

WINDOW_NAME = "VisionMotion M4.3-1 calibration"

# 用户点出的点，单位是视频原始像素坐标（不是窗口显示坐标）
points = []

# 视频原始尺寸与窗口显示尺寸（读到帧之后再填）
frame_width = 0
frame_height = 0
display_width = 0
display_height = 0


# ============================================================
# 坐标换算：显示坐标 <-> 视频原始像素坐标
# ============================================================


def to_original(x, y):
    """
    把窗口显示坐标换算回视频原始像素坐标。

    这样即使用户屏幕上放不下 1920x1080、窗口做了等比缩小，
    记录下来的坐标也始终和视频追踪用的是同一套坐标系。
    """
    return (x * frame_width / display_width, y * frame_height / display_height)


def to_display(point):
    """
    把视频原始像素坐标换算成窗口显示坐标（整数），只用于画图。
    """
    x = int(round(point[0] * display_width / frame_width))
    y = int(round(point[1] * display_height / frame_height))
    return (x, y)


def get_screen_size():
    """
    读取屏幕分辨率（Windows 上调用系统接口）。
    读不到时返回 1920 x 1080，程序仍然可以正常运行。
    """
    try:
        import ctypes

        user32 = ctypes.windll.user32
        screen_width = user32.GetSystemMetrics(0)
        screen_height = user32.GetSystemMetrics(1)
        if screen_width > 0 and screen_height > 0:
            return screen_width, screen_height
    except Exception:
        pass

    return 1920, 1080


# ============================================================
# 鼠标回调
# ============================================================


def on_mouse(event, x, y, flags, param):
    """
    OpenCV 鼠标回调：只处理鼠标左键按下。

    x, y 是窗口里的坐标，必须先换算回视频原始像素坐标再记录。
    第 1 次点击记 P1（10 cm），第 2 次点击记 P2（16 cm）。
    已经有两个点时，再点不会覆盖，按 r 可以重选。
    """
    if event != cv2.EVENT_LBUTTONDOWN:
        return

    if len(points) >= 2:
        return

    points.append(to_original(x, y))


# ============================================================
# 画面绘制（只画在内存里的显示画布上，不保存任何图片）
# ============================================================


def put_text_outlined(canvas, text, org, color, font_scale=0.8, thickness=2):
    """
    写一行字：先用黑字描边，再写彩色字，保证在任何背景上都看得清。
    """
    cv2.putText(canvas, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                (0, 0, 0), thickness + 3, cv2.LINE_AA)
    cv2.putText(canvas, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                color, thickness, cv2.LINE_AA)


def draw_points(canvas):
    """
    把已经点出的点、连线和文字画到显示画布上。

    P1 用红色，P2 用绿色；文字里同时写出原始像素坐标，方便人工核对。
    """
    # 两个点都在时画出连线
    if len(points) == 2:
        cv2.line(canvas, to_display(points[0]), to_display(points[1]), (255, 255, 0), 2)

    for index, point in enumerate(points):
        center = to_display(point)
        text = "(%d, %d)" % (round(point[0]), round(point[1]))

        if index == 0:
            color = (0, 0, 255)          # 红色：P1
            label = "P1 = 10 cm  " + text
        else:
            color = (0, 255, 0)          # 绿色：P2
            label = "P2 = 16 cm  " + text

        # 十字标记 + 空心圆，方便看清点在哪条刻线上
        cv2.drawMarker(canvas, center, color, cv2.MARKER_CROSS, 28, 2)
        cv2.circle(canvas, center, 8, color, 2)
        # OpenCV 不支持显示中文，所以文字用英文
        put_text_outlined(canvas, label, (center[0] + 14, center[1] - 14), color)


def draw_header(canvas):
    """
    在画布顶部写帧号、尺寸和操作提示。
    """
    put_text_outlined(
        canvas,
        "frame = %d   video %d x %d   display %d x %d"
        % (FRAME_INDEX, frame_width, frame_height, display_width, display_height),
        (14, 34), (255, 255, 255), font_scale=0.8,
    )
    put_text_outlined(
        canvas,
        "click 1: P1 = 10 cm    click 2: P2 = 16 cm    r = reset    Enter / q = confirm",
        (14, 72), (0, 255, 255), font_scale=0.8,
    )


def draw_result(canvas, scale_result, direction):
    """
    在结果图上写出 L_pixel、k、1/k 和 u，方便人工核对后关闭窗口。
    """
    lines = [
        "L_real = %.1f mm" % REAL_DISTANCE_MM,
        "L_pixel = %.4f px" % scale_result["pixel_distance"],
        "k = %.6f px/mm" % scale_result["px_per_mm"],
        "1/k = %.6f mm/px" % scale_result["mm_per_px"],
        "u = (%.6f, %.6f)" % (direction["ux"], direction["uy"]),
        "press any key to close",
    ]

    # 从画布底部往上写，避免遮挡画面中间的内容
    y = canvas.shape[0] - 24 - 34 * (len(lines) - 1)
    for line in lines:
        color = (0, 255, 255) if line.startswith("press") else (255, 255, 255)
        put_text_outlined(canvas, line, (14, y), color, font_scale=0.9)
        y = y + 34


# ============================================================
# 主流程
# ============================================================


def main():
    global frame_width, frame_height, display_width, display_height

    # ---------- 1. 打开视频（只读，不会修改原始文件） ----------
    capture = cv2.VideoCapture(str(VIDEO_PATH))
    if not capture.isOpened():
        print("视频打开失败：%s" % VIDEO_PATH)
        return

    # ---------- 2. 打开自动旋转 ----------
    capture.set(cv2.CAP_PROP_ORIENTATION_AUTO, 1)

    # ---------- 3. 跳到 frame = 900 ----------
    capture.set(cv2.CAP_PROP_POS_FRAMES, FRAME_INDEX)

    # ---------- 4. 读取这一帧 ----------
    ok, frame = capture.read()
    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    capture.release()

    if not ok or frame is None:
        print("读取 frame %d 失败" % FRAME_INDEX)
        return

    frame_height = frame.shape[0]
    frame_width = frame.shape[1]

    # ---------- 5. 计算显示尺寸：屏幕放不下就等比缩小显示 ----------
    screen_width, screen_height = get_screen_size()
    scale = min(1.0,
                (screen_width - 60) / frame_width,
                (screen_height - 160) / frame_height)
    display_width = int(round(frame_width * scale))
    display_height = int(round(frame_height * scale))

    print("视频路径：%s" % VIDEO_PATH)
    print("视频是否成功打开：是")
    print("视频尺寸（宽 x 高）：%d x %d" % (frame_width, frame_height))
    print("FPS：%.3f" % fps)
    print("总帧数：%d" % total_frames)
    print("标定帧号：%d" % FRAME_INDEX)
    print("实际显示尺寸（宽 x 高）：%d x %d（缩放系数 %.3f）"
          % (display_width, display_height, scale))
    print("")
    print("请在窗口里依次点击：先点 P1 = 10 cm 刻线，再点 P2 = 16 cm 刻线。")
    print("按 r 重选，按 Enter 或 q 确认。")
    print("")

    # ---------- 6. 开窗，等用户点击 ----------
    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    confirmed = False
    while True:
        canvas = cv2.resize(frame, (display_width, display_height),
                            interpolation=cv2.INTER_AREA)
        draw_points(canvas)
        draw_header(canvas)
        cv2.imshow(WINDOW_NAME, canvas)

        key = cv2.waitKey(20) & 0xFF

        if key == ord("r") or key == ord("R"):
            points.clear()
            print("已重置，请重新点击 P1 = 10 cm 刻线。")
        elif key in (13, 10, ord("q"), ord("Q")):
            if len(points) == 2:
                confirmed = True
                break
            print("还需要两个点（当前 %d 个），请先点 P1 = 10 cm 和 P2 = 16 cm。"
                  % len(points))
        elif key == 27:
            break

        # 用户直接关掉窗口时结束循环
        if cv2.getWindowProperty(WINDOW_NAME, cv2.WND_PROP_VISIBLE) < 1:
            break

    if not confirmed:
        cv2.destroyAllWindows()
        print("已取消：没有确认两个点，未计算标定结果。")
        return

    # ---------- 7. 计算 k 与 u ----------
    point1 = points[0]
    point2 = points[1]
    scale_result = compute_scale(point1, point2, REAL_DISTANCE_MM)
    direction = unit_direction(point1, point2)

    # ---------- 8. 打印最终结果 ----------
    print("")
    print("========== M4.3-1 标定结果 ==========")
    print("P1 = (%.2f, %.2f)" % (point1[0], point1[1]))
    print("P2 = (%.2f, %.2f)" % (point2[0], point2[1]))
    print("")
    print("L_real = %.1f mm" % REAL_DISTANCE_MM)
    print("L_pixel = %.4f px" % scale_result["pixel_distance"])
    print("k = %.6f px/mm" % scale_result["px_per_mm"])
    print("1/k = %.6f mm/px" % scale_result["mm_per_px"])
    print("u = (%.6f, %.6f)" % (direction["ux"], direction["uy"]))
    print("")
    print("自检：k * (1/k) = %.6f（应约等于 1.0）"
          % (scale_result["px_per_mm"] * scale_result["mm_per_px"]))
    print("自检：|u| = %.6f（应约等于 1.0）"
          % math.hypot(direction["ux"], direction["uy"]))
    print("自检：P1 与 P2 是否重合：%s"
          % ("是（异常）" if point1 == point2 else "否"))
    print("")

    # ---------- 9. 再次显示标定结果（只看，不保存图片） ----------
    result_canvas = cv2.resize(frame, (display_width, display_height),
                               interpolation=cv2.INTER_AREA)
    draw_points(result_canvas)
    draw_result(result_canvas, scale_result, direction)
    cv2.imshow(WINDOW_NAME, result_canvas)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

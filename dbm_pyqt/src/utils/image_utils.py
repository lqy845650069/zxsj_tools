# src/utils/image_utils.py
import cv2
import pygetwindow as gw
import pyautogui
import numpy as np


def detect_image_on_screen(image_path):
    windows = gw.getWindowsWithTitle('ZhuxianClient')
    if not windows:
        print("窗口未找到")
        return False
    else:
        window = windows[0]

        # 确保窗口是激活的
        #window.activate()

        # 获取窗口的位置和大小
        left, top, width, height = window.left, window.top, window.width, window.height

        # 读取模板图像
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)

        if template is None:
            return False

        # 设置匹配阈值
        threshold = 0.9

        # 获取窗口截图
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot = np.array(screenshot)

        # 转换颜色通道顺序（从 BGR 到 RGB）
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB)

        # 进行模板匹配

        res = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if max_val >= threshold:
            print(f"屏幕上检测到图片: {image_path} 可信度: {max_val:.4f}")
            return True
        else:
            print(f"屏幕上未检测到图片: {image_path} 可信度: {max_val:.4f}")
            return False


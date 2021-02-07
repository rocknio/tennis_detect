# -*- coding: utf-8 -*-
import cv2
import numpy as np

import settings
from settings import low_color, high_color


def nothing(x):
    pass


def show_color_setting(window_name):
    lower_color_img = np.zeros((100, 100, 3), np.uint8)
    cv2.namedWindow(window_name)

    # 创建RGB三个滑动条
    # =============================================================================
    # cv2.createTrackbar('R','image',0,255,call_back)
    # 参数1：滑动条的名称
    # 参数2：所在窗口的名称
    # 参数3：当前的值
    # 参数4：最大值
    # 参数5：回调函数名称，回调函数默认有一个表示当前值的参数
    # =============================================================================
    cv2.createTrackbar('R', window_name, 0, 255, nothing)
    cv2.createTrackbar('G', window_name, 0, 255, nothing)
    cv2.createTrackbar('B', window_name, 0, 255, nothing)

    # 根据setting当前值，设置颜色
    color = [0, 0, 0]
    if window_name == 'lower_color_img':
        color = low_color

    if window_name == 'higher_color_img':
        color = high_color

    cv2.setTrackbarPos('B', window_name, color[0])
    cv2.setTrackbarPos('R', window_name, color[1])
    cv2.setTrackbarPos('G', window_name, color[2])

    while True:
        # 获取滑块的值
        r = cv2.getTrackbarPos('R', window_name)
        g = cv2.getTrackbarPos('G', window_name)
        b = cv2.getTrackbarPos('B', window_name)

        if window_name == 'lower_color_img':
            settings.low_color = [b, g, r]

        if window_name == 'higher_color_img':
            settings.high_color = [b, g, r]

        # 设定img的颜色
        lower_color_img[:] = [b, g, r]

        cv2.imshow(window_name, lower_color_img)
        if cv2.waitKey(1) == ord('q'):
            break

# -*- coding: utf-8 -*-
import cv2
import numpy as np

from config_util.settings import SettingService


def nothing(x):
    pass


def show_color_setting(window_name, cfg):
    settings = SettingService()
    cfg['low_color'] = settings.settings['color_range']['low']
    cfg['high_color'] = settings.settings['color_range']['high']
    cfg['hsv_low'] = settings.settings['color_range']['hsv_low']
    cfg['hsv_high'] = settings.settings['color_range']['hsv_high']
    cfg['detect_zone'] = settings.settings['detect_zone']
    cfg['limit_pixel'] = settings.settings['limit_pixel']
    cfg['min_contour_area'] = settings.settings['min_contour_area']
    cfg['robot_master_sn'] = settings.settings['robot_master_sn']

    img = np.zeros((100, 100, 3), np.uint8)
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
    if window_name == 'low':
        cv2.setTrackbarPos('B', window_name, cfg['low_color']['blue'])
        cv2.setTrackbarPos('R', window_name, cfg['low_color']['red'])
        cv2.setTrackbarPos('G', window_name, cfg['low_color']['green'])

    if window_name == 'high':
        cv2.setTrackbarPos('B', window_name, cfg['high_color']['blue'])
        cv2.setTrackbarPos('R', window_name, cfg['high_color']['red'])
        cv2.setTrackbarPos('G', window_name, cfg['high_color']['green'])

    while True:
        # 获取滑块的值
        r = cv2.getTrackbarPos('R', window_name)
        g = cv2.getTrackbarPos('G', window_name)
        b = cv2.getTrackbarPos('B', window_name)

        if window_name == 'low':
            cfg['low_color'] = {
                'blue': b,
                'green': g,
                'red': r
            }

        if window_name == 'high':
            cfg['high_color'] = {
                'blue': b,
                'green': g,
                'red': r
            }

        # 设定img的颜色
        img[:] = [b, g, r]

        cv2.imshow(window_name, img)
        if cv2.waitKey(1) == ord('q'):
            settings.save_config(cfg)
            break

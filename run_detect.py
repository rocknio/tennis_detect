# -*- coding: utf-8 -*-
import queue
import time

from RoboMasterService.robo_master_control import RoboMasterControlService
from camera_service.camera_utils import CameraService
from config_util.config_service import show_color_setting
from config_util.settings import SettingService
from global_var.global_queue import q
from tennis_detect_service.tennis_detect import TennisDetectService
from RoboMasterService.robo_master_service import RoboMasterService
import logging
import logging.handlers
from multiprocessing import Process, Manager


def init_logging():
    """
    init logging module
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    file_log = logging.handlers.TimedRotatingFileHandler('run.log', 'MIDNIGHT', 1, 0)
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-7s] [%(module)s:%(filename)s-%(funcName)s-%(lineno)d] %(message)s')
    sh.setFormatter(formatter)
    file_log.setFormatter(formatter)

    logger.addHandler(sh)
    logger.addHandler(file_log)

    logging.info("Current log level is : %s", logging.getLevelName(logger.getEffectiveLevel()))


if __name__ == '__main__':
    init_logging()

    # d = Manager().dict()

    settings = SettingService()
    cfg = {
        'low_color': settings.settings['color_range']['low'],
        'high_color': settings.settings['color_range']['high'],
        'hsv_low': [x * 255 for x in settings.settings['color_range']['hsv_low']],
        'hsv_high': [x * 255 for x in settings.settings['color_range']['hsv_high']],
        'detect_zone': settings.settings['detect_zone'],
        'limit_pixel': settings.settings['limit_pixel'],
        'min_contour_area': settings.settings['min_contour_area'],
        'robot_master_sn': settings.settings['robot_master_sn'],
        'shot_hsv_low': [x * 255 for x in settings.settings['marker_range']['hsv_low']],
        'shot_hsv_high': [x * 255 for x in settings.settings['marker_range']['hsv_high']]
    }

    # # 启动设置界面
    # p = Process(target=show_color_setting, args=('low', d))
    # p.start()
    #
    # p1 = Process(target=show_color_setting, args=('high', d))
    # p1.start()
    #
    # # 等3秒，颜色调节窗口打开后，d才会有初始值
    # time.sleep(2)

    # 1、图片文件测试
    # svc = TennisDetectService([([0, 60, 100], [95, 255, 255])], './images/t1.jpg')
    # svc.detect_color()

    # 2、电脑摄像头采集图像测试
    # svc = CameraService(0, cfg)
    # svc.start_capture()

    # 3、RoboMaster摄像头采集图像
    # robot运动控制线程
    rb_ctrl = RoboMasterControlService(q, cfg)
    rb_ctrl.start()

    # robot摄像头，图像识别线程
    svc = RoboMasterService(cfg, q)
    svc.start_capture()

    # p.join()
    # p1.join()

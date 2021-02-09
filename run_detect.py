# -*- coding: utf-8 -*-
from camera_service.camera_utils import CameraService
from config_util.config_service import show_color_setting
from config_util.settings import SettingService
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

    d = Manager().dict()

    # 启动设置界面
    p = Process(target=show_color_setting, args=('low', d))
    p.start()

    p1 = Process(target=show_color_setting, args=('high', d))
    p1.start()

    # 1、图片文件测试
    # svc = TennisDetectService([([0, 60, 100], [95, 255, 255])], './images/t1.jpg')
    # svc.detect_color()

    # 2、电脑摄像头采集图像测试
    # svc = CameraService(0, d)
    # svc.start_capture()

    # 3、RoboMaster摄像头采集图像
    svc = RoboMasterService(d)
    svc.start_capture()

    p.join()
    p1.join()

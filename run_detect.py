# -*- coding: utf-8 -*-
from config_util.settings import SettingService
from global_var.global_queue import q
from RoboMasterService.robo_master_service_v2 import RoboMasterServiceV2
import logging
import logging.handlers


def init_logging():
    """
    init logging module
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    sh = logging.StreamHandler()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)-7s] [%(module)s:%(filename)s-%(funcName)s-%(lineno)d] %(message)s')
    sh.setFormatter(formatter)

    logger.addHandler(sh)

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
        'shot_hsv_high': [x * 255 for x in settings.settings['marker_range']['hsv_high']], 
        'msg_interval': settings.settings['msg_interval'], 
        'release_mode': settings.settings['release_mode'],
        'run_mode': settings.settings['run_mode']
    }

    # robot摄像头，图像识别线程
    svc = RoboMasterServiceV2(cfg, q)
    svc.start_capture()

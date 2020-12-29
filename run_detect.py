# -*- coding: utf-8 -*-
from camera_service.camera_utils import CameraService
from tennis_detect_service.tennis_detect import TennisDetectService
from RoboMasterService.robo_master_service import RoboMasterService

if __name__ == '__main__':
    # 1、图片文件测试
    # svc = TennisDetectService([([0, 60, 100], [95, 255, 255])], './images/t1.jpg')
    # svc.detect_color()

    # 2、电脑摄像头采集图像测试
    # svc = CameraService(0)
    # svc.start_capture()

    # 3、RoboMaster摄像头采集图像
    svc = RoboMasterService()
    svc.start_capture()

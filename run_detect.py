# -*- coding: utf-8 -*-
from camera_service.camera_utils import CameraService
from tennis_detect_service.tennis_detect import TennisDetectService

if __name__ == '__main__':
    svc = TennisDetectService([([0, 60, 100], [95, 255, 255])], './images/t1.jpg')
    svc.detect_color()
    # svc = CameraService(0)
    # svc.start_capture()

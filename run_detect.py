# -*- coding: utf-8 -*-
from camera_service.camera_utils import CameraService


if __name__ == '__main__':
    # # svc = TennisDetect('./images/t1.jpg', [(  [50, 128, 205], [87, 255, 255])])  ,,,,   [([0, 60, 100], [95, 255, 255])]
    svc = CameraService(0)
    svc.start_capture()

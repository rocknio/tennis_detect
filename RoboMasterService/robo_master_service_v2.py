# -*- coding: utf-8 -*-
from RoboMasterService.robo_master_control_v2 import RoboMasterControlService_V2
from enum import Enum

import cv2
import logging
from robomaster import robot

from tennis_detect_service.tennis_detect import TennisDetectService


class Colors(Enum):
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)


class RoboMasterServiceV2:
    def __init__(self, cfg, q):
        self._cfg = cfg
        self._q = q
        self._camera = None

        self._robo_ctrl_service_v2 = RoboMasterControlService_V2(q, cfg)

        try:
            # 初始化
            self._robot = robot.Robot()

            # 初始化相机
            self._robot.initialize(conn_type='sta', sn=self._cfg['robot_master_sn'])
            self._camera = self._robot.camera
        except Exception as err:
            self._robot.close()
            logging.error(f"exception: {err}")

    @staticmethod
    def release_robot():
        cv2.destroyAllWindows()
        exit()

    def start_capture(self):
        if self._camera is None:
            logging.error("RoboMasterService is not initialized!!!")
            return

        self._camera.start_video_stream(display=False)
        while True:
            img = self._camera.read_cv2_image(strategy='newest')
            if img is not None:
                tennis_detect_service = TennisDetectService(self._cfg, cap_frame=img)
                x_match, y_match, delta = tennis_detect_service.detect_color(self._robo_ctrl_service_v2.step())
                cv2.imshow("vision", img)

                self._robo_ctrl_service_v2.robo_action(x_match, y_match, delta)

                if cv2.waitKey(1) == ord('q'):
                    break

        exit()

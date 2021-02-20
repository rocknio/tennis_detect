# -*- coding: utf-8 -*-
import time

import cv2
import logging
# from robomaster import robot

import global_var.robotic_ip
from tennis_detect_service.tennis_detect import TennisDetectService


class RoboMasterService:
    def __init__(self, cfg, q):
        self._cfg = cfg
        self._q = q
        self._is_need_stop = False
        self._is_running = False
        self._camera = None
        self._robotic_conn = None
        self._robotic_ctrl = None
        self._msg_interval = 0.5
        self._last_msg_time = None

        try:
            # 初始化日志文件
            # robomaster.enable_logging_to_file()

            # 初始化
            # self._robot = robot.Robot()

            # 初始化相机
            # self._robot.initialize(conn_type='sta', sn=self._cfg['robot_master_sn'])
            # self._camera = self._robot.camera

            # 等待连接上robot
            while True:
                if not global_var.robotic_ip.robotic_host:
                    continue

                self._camera = cv2.VideoCapture(f'tcp://{global_var.robotic_ip.robotic_host}:40921')
                assert self._camera.isOpened(), 'failed to connect to video stream'
                self._camera.set(cv2.CAP_PROP_BUFFERSIZE, 4)
        except Exception as err:
            if self._camera:
                self._camera.release()
            logging.error(f"exception: {err}")

    def release_robot(self):
        if self._camera:
            self._camera.release()

        cv2.destroyAllWindows()

    def check_msg_send(self):
        current_time = round(time.time(), 1)

        if not self._last_msg_time:
            self._last_msg_time = current_time
            return True

        if current_time - self._last_msg_time > self._msg_interval:
            self._last_msg_time = current_time
            return True
        else:
            return False

    def start_capture(self):
        if self._camera is None:
            logging.error("RoboMasterService is not initialized!!!")
            return

        self._is_running = True
        while True:
            if self._is_need_stop:
                logging.info("capture is stopped!")
                self._is_running = False
                self._is_need_stop = False
                self.release_robot()
                break

            ok, img = self._camera.read()
            if not ok:
                break

            if img is not None:
                tennis_detect_service = TennisDetectService(self._cfg, cap_frame=img)
                x_match, y_match, delta = tennis_detect_service.detect_color()
                if cv2.waitKey(1) == ord('q'):
                    break

                if self.check_msg_send():
                    self._q.put({'x_match': x_match, 'y_match': y_match, 'delta': delta})

        self.release_robot()

    def stop_capture(self):
        if not self._is_running:
            logging.error("capture is not running")
            return

        self._is_need_stop = True

    def destroy(self):
        if self._is_running:
            self._is_need_stop = True
            logging.info("capture is waiting for stop")
            cv2.destroyAllWindows()

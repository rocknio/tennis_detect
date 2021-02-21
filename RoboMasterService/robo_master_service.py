# -*- coding: utf-8 -*-
import time
from enum import Enum

import cv2
import logging
from robomaster import robot

from global_var.global_queue import detect_q
from global_var.step_const import StepService
from tennis_detect_service.tennis_detect import TennisDetectService


class Colors(Enum):
    red = (0, 0, 255)
    green = (0, 255, 0)
    blue = (255, 0, 0)


class RoboMasterService:
    def __init__(self, cfg, q):
        self._cfg = cfg
        self._q = q
        self._detect_q = detect_q
        self._is_need_stop = False
        self._is_running = False
        self._camera = None
        self._robotic_conn = None
        self._robotic_ctrl = None
        self._msg_interval = 0.5
        self._last_msg_time = None
        self._detect_info = None

        try:
            # 初始化
            self._robot = robot.Robot()

            # 初始化相机
            self._robot.initialize(conn_type='sta', sn=self._cfg['robot_master_sn'])
            self._camera = self._robot.camera
        except Exception as err:
            if self._camera:
                self._camera.release()

            self._robot.close()
            logging.error(f"exception: {err}")

    @staticmethod
    def release_robot():
        cv2.destroyAllWindows()
        exit()

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

    def draw_detect_zone(self, img):
        # 画出探测区域中心点
        detect_zone_center = (self._cfg['detect_zone']['down_right']['y']
                              - (self._cfg['detect_zone']['down_right']['y']
                                 - self._cfg['detect_zone']['top_left']['y']) // 2 // 2,

                              self._cfg['detect_zone']['top_left']['x']
                              + (self._cfg['detect_zone']['down_right']['x']
                                 - self._cfg['detect_zone']['top_left']['x']) // 2,)

        cv2.rectangle(img,
                      (detect_zone_center[1], detect_zone_center[0]),
                      (detect_zone_center[1] + self._cfg['limit_pixel']['x'] // 2,
                       detect_zone_center[0] + self._cfg['limit_pixel']['y'] // 2),
                      (0, 255, 0),
                      2)

        # 划线重点探测区域
        cv2.rectangle(img,
                      (self._cfg['detect_zone']['top_left']['x'], self._cfg['detect_zone']['top_left']['y']),
                      (self._cfg['detect_zone']['down_right']['x'], self._cfg['detect_zone']['down_right']['y']),
                      (0, 255, 0), 2)

        return detect_zone_center

    def start_capture(self):
        if self._camera is None:
            logging.error("RoboMasterService is not initialized!!!")
            return

        self._is_running = True
        self._camera.start_video_stream(display=False)
        while True:
            if self._is_need_stop:
                logging.info("capture is stopped!")
                self._is_running = False
                self._is_need_stop = False
                self.release_robot()
                break

            img = self._camera.read_cv2_image(strategy='newest')
            if img is not None:
                # tennis_detect_service = TennisDetectService(self._cfg, cap_frame=img)
                # tennis_detect_service.detect_color(2)

                self.draw_detect_zone(img)
                if self.check_msg_send():
                    self._q.put(img)
                    while True:
                        try:
                            self._detect_info = self._detect_q.get(timeout=0.1)
                            break
                        except Exception:
                            pass

                if self._detect_info is not None:
                    c = self._detect_info['c']
                    x_match = self._detect_info['x_match']
                    y_match = self._detect_info['y_match']
                    delta = self._detect_info['delta']
                    step = self._detect_info['step']

                    if c is not None:
                        # 画出被探测物体区域及中心点
                        x, y, w, h = cv2.boundingRect(c)
                        center = (x + w // 2, y + h // 2)

                        if x_match and y_match:
                            center_color = Colors.green.value
                        else:
                            center_color = Colors.red.value

                        if step == 2:
                            cv2.rectangle(img, (x, y), (x + w, y + h), center_color, 2)
                            cv2.rectangle(img, (center[0], center[1]), (center[0] + 2, center[1] + 2),
                                          center_color, 2)
                        else:
                            (x, y), pixel_radius = cv2.minEnclosingCircle(c)
                            cv2.circle(img, (int(x), int(y)), int(pixel_radius), center_color, 2)
                            cv2.circle(img, (int(x), int(y)), 1, center_color, 2)

                        # 返回值打印在图像上
                        text = f'x_match = {x_match} and y_match = {y_match}, delta = {delta}'
                        cv2.putText(img, text, (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0, center_color, 2)

                cv2.imshow("vision", img)

                if cv2.waitKey(1) == ord('q'):
                    break

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

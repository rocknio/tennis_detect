# -*- coding: utf-8 -*-
import logging
import threading
import time

from enum import Enum

from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn
from robo_master_protocol.robotic_ctrl.robotic_control import RoboticController
from tennis_detect_service.tennis_detect import TennisDetectService


class Step(Enum):
    tennis = 1
    shot = 2


class RoboMasterControlService(threading.Thread):
    def __init__(self, q, cfg):
        # 初始化
        super().__init__()
        self._q = q
        self._cfg = cfg
        self._is_gripper_close = False
        self._step = Step.tennis.value

        # 初始化控制连接
        self._robotic_conn = RoboticConn()
        if self._robotic_conn.connect_robo() is False:
            logging.fatal(f'connect to robot failed!')
            exit()

        # 初始化各模块
        self._robotic_ctrl = RoboticController(self._robotic_conn)

        # 初始化状态
        self._robotic_ctrl.reset_arm()
        time.sleep(0.5)
        self._robotic_ctrl.expand_arm(1000, 0)
        self._robotic_ctrl.open_gripper()

    def step_change(self):
        if self._step == Step.shot.value:
            self._step = Step.tennis.value
        else:
            self._step = Step.shot.value

    def run(self):
        while True:
            try:
                img = self._q.get()
                # if isinstance(msg, dict):
                #     # 图像识别消息
                #     self.robo_action(msg['x_match'], msg['y_match'], msg['delta'])
                tennis_detect_service = TennisDetectService(self._cfg, cap_frame=img)
                x_match, y_match, delta = tennis_detect_service.detect_color(self._step)
                self.robo_action(x_match, y_match, delta)
            except Exception as e:
                logging.error(f"msg get exception = {e}")

    def robo_action(self, x_match, y_match, delta):
        if not delta:
            # 没有delta，表示画面没有网球，转动10°
            print("转30度")
            self._robotic_ctrl.move_rotate(30, duration=1)
            return False

        if x_match and y_match:
            if not self._is_gripper_close and self._step == Step.tennis.value:
                logging.info("可以抓取")
                self._robotic_ctrl.close_gripper()
                time.sleep(1)
                self._robotic_ctrl.reset_arm()
                self._is_gripper_close = True

                self.step_change()
            else:
                logging.info("可以释放")
            return True

        if not x_match:
            # 转向
            delta_x = delta[0]
            if delta_x > 0:
                direction = -1
            else:
                direction = 1
            self._robotic_ctrl.move_rotate(10, direction=direction, duration=0.5)
            return False

        if not y_match:
            # 纵向移动
            delta_y = delta[1]
            if delta_y < 0:
                return

            self._robotic_ctrl.move_y(0.1, duration=0.5)
            return False

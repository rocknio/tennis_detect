# -*- coding: utf-8 -*-
import logging
import time

from enum import Enum

from global_var.global_queue import detect_q
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn
from robo_master_protocol.robotic_ctrl.robotic_control import RoboticController
from tennis_detect_service.tennis_detect import TennisDetectService


class Step(Enum):
    tennis = 1
    shot = 2


class RoboMasterControlService_V2():
    def __init__(self, q, cfg):
        # 初始化
        super().__init__()
        self._q = q
        self._detect_q = detect_q
        self._cfg = cfg
        self._is_x_match = False
        self._is_y_match = False
        self._x_return_count = 0
        self._y_return_count = 0
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

    def step(self):
        return self._step

    def step_change(self):
        if self._step == Step.shot.value:
            self._step = Step.tennis.value
        else:
            self._step = Step.shot.value

    def reset_match(self):
        self._is_x_match = False
        self._is_y_match = False

        self._x_return_count, self._y_return_count = 0, 0

    def do_cap(self):
        self._robotic_ctrl.close_gripper()
        time.sleep(1)
        self._robotic_ctrl.reset_arm()
        self._is_gripper_close = True

        self.step_change()
        self.reset_match()

    def do_release(self, mode):
        if mode == 'bucket':
            self._robotic_ctrl.expand_arm(0, 1000)
            time.sleep(0.5)
            self._robotic_ctrl.move_y(0.2, duration=0.5)
            time.sleep(0.5)
            self._robotic_ctrl.expand_arm(300, 0)
            time.sleep(0.5)
            self._robotic_ctrl.open_gripper()
        else:
            self._robotic_ctrl.expand_arm(1000, 0)
            time.sleep(0.5)
            self._robotic_ctrl.open_gripper()
            time.sleep(0.5)

        self._is_gripper_close = False
        self.step_change()
        self.reset_match()

        # 倒退，掉头
        self._robotic_ctrl.move_y(-0.3, 0.5)
        time.sleep(0.5)
        self._robotic_ctrl.move_rotate(180, duration=1)

    def robo_action(self, x_match, y_match, delta):
        if not delta:
            # 没有delta，表示画面没有网球，转动10°
            print("转30度")
            self._robotic_ctrl.move_rotate(30, duration=1)
            return False

        if x_match and y_match:
            if not self._is_gripper_close and self._step == Step.tennis.value:
                logging.info("可以抓取")
                self.stop()
                self.do_cap()
            else:
                logging.info("可以释放")
                self.do_release(self._cfg['release_mode'])
            
            return True

        if not x_match:
            if self._is_x_match and self._x_return_count <= 5:
                self._x_return_count += 1
            else:
                # 转向
                delta_x = delta[0]
                if delta_x > 0:
                    direction = -1
                else:
                    direction = 1
                self._robotic_ctrl.move_rotate(10, direction=direction)
        else:
            self._is_x_match = True

        if not y_match:
            if self._is_y_match and self._y_return_count <= 5:
                self._y_return_count += 1
            else:
                # 纵向移动
                delta_y = delta[1]
                if delta_y < 0:
                    return

                self._robotic_ctrl.move_y(0.1)
        else:
            self._is_y_match = True

# -*- coding: utf-8 -*-
import logging
import threading
import time

from robomaster import robot

from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn
from robo_master_protocol.robotic_ctrl.robotic_control import RoboticController


class RoboMasterControlService(threading.Thread):
    def __init__(self, q, cfg):
        # 初始化
        super().__init__()
        self._q = q
        self._cfg = cfg
        self._robot = robot.Robot()
        self._is_gripper_close = False

        # 初始化控制连接
        self._robotic_conn = RoboticConn(self._robot, self._cfg['robot_master_sn'])
        if self._robotic_conn.connect_robo() is False:
            logging.fatal(f'connect to robot failed!')
            self.release_robot()

        # 初始化各模块
        self._robotic_ctrl = RoboticController(self._robotic_conn)

        # 初始化状态
        self._robotic_ctrl.reset_arm()
        time.sleep(0.5)
        self._robotic_ctrl.expand_arm(1000, 0)
        self._robotic_ctrl.open_gripper()

    def release_robot(self):
        if self._robot:
            self._robot.close()
            self._robot = None

    def run(self):
        while True:
            try:
                msg = self._q.get()
                self.robo_action(msg['x_match'], msg['y_match'], msg['delta'])
            except Exception as e:
                logging.error(f"msg get exception = {e}")

    def robo_action(self, x_match, y_match, delta):
        if self._is_gripper_close:
            return

        if not delta:
            # 没有delta，表示画面没有网球，转动10°
            print("转30度")
            self._robotic_ctrl.move_rotate(30, duration=1)
            return False

        if x_match and y_match:
            logging.info("可以抓取")
            self._robotic_ctrl.close_gripper()
            time.sleep(1)
            self._robotic_ctrl.reset_arm()
            self._is_gripper_close = True
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

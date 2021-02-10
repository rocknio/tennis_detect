# -*- coding: utf-8 -*-
import cv2
import logging
from robomaster import robot

from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn
from robo_master_protocol.robotic_ctrl.robotic_control import RoboticController
from tennis_detect_service.tennis_detect import TennisDetectService


class RoboMasterService:
    def __init__(self, cfg):
        self._cfg = cfg
        self._is_need_stop = False
        self._is_running = False
        self._robot = None
        self._camera = None

        try:
            # 初始化日志文件
            # robomaster.enable_logging_to_file()

            # 初始化
            self._robot = robot.Robot()

            # 初始化相机
            self._robot.initialize(conn_type='sta', sn=self._cfg['robot_master_sn'])
            self._camera = self._robot.camera

            # 初始化控制连接
            self._robotic_conn = RoboticConn(self._robot)
            if self._robotic_conn.connect_robo() is False:
                logging.fatal(f'connect to robot failed!')
                self.release_robot()

            # 初始化各模块
            self._robotic_ctrl = RoboticController(self._robotic_conn)

            # 初始化状态
            self._robotic_ctrl.reset_arm()
            self._robotic_ctrl.open_gripper()
        except Exception as err:
            self._camera = None
            self._robot.close()
            logging.error(f"exception: {err}")

    def release_robot(self):
        if self._robot:
            self._robot.close()
            self._robot = None

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
                self._camera.stop_video_stream()
                self.release_robot()
                break

            img = self._camera.read_cv2_image(strategy='newest')
            if img is not None:
                tennis_detect_service = TennisDetectService(self._cfg, cap_frame=img)
                x_match, y_match, delta = tennis_detect_service.detect_color()
                if cv2.waitKey(1) == ord('q'):
                    break

                self.robo_action(x_match, y_match, delta)

        cv2.destroyAllWindows()

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

    def robo_action(self, x_match, y_match, delta):
        if not delta:
            # 没有delta，表示画面没有网球，转动10°
            self._robotic_ctrl.move_rotate(10)

        if x_match and y_match:
            logging.info("可以抓取")
            self._robotic_ctrl.close_gripper()

        if not x_match:
            # 横向移动
            delta_x = delta[0]
            pass

        if not y_match:
            # 纵向移动
            delta_y = delta[1]

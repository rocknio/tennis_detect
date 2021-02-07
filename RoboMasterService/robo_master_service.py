# -*- coding: utf-8 -*-
import cv2
import logging
from robomaster import robot

from robo_master_protocol.arm.robotic_arm import RoboticArm
from robo_master_protocol.chassis.robotic_chassis import RoboticChassis
from robo_master_protocol.gripper.robotic_gripper import RoboticGripper
from robo_master_protocol.ir.robotic_ir import RoboticIr
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn
from tennis_detect_service.tennis_detect import TennisDetectService
from config_util.settings import SettingService


class RoboMasterService:
    def __init__(self):
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
            self._robot.initialize(conn_type='sta', sn=robot_master_sn)
            self._camera = self._robot.camera

            # 初始化控制连接
            self._robotic_conn = RoboticConn(self._robot)
            if self._robotic_conn.connect_robo() is False:
                logging.fatal(f'connect to robot failed!, host = {robot_host}, port = {robot_port}')
                self.release_robot()

            # 初始化各模块
            self._arm = RoboticArm(self._robotic_conn)
            self._gripper = RoboticGripper(self._robotic_conn)
            self._ir = RoboticIr(self._robotic_conn)
            self._chassis = RoboticChassis(self._robotic_conn)
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
                tennis_detect_service = TennisDetectService((low_color, high_color), cap_frame=img)
                direction = tennis_detect_service.detect_color()
                logging.info(f"direction: {direction}")
                if cv2.waitKey(1) == ord('q'):
                    break

                # cv2.imshow("result", img)

                # TODO: 根据direction，控制robomaster移动
                pass

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

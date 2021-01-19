# -*- coding: utf-8 -*-
import cv2
import logging
import robomaster
from robomaster import robot
from tennis_detect_service.tennis_detect import TennisDetectService
from settings import low_color, high_color, robot_master_sn
from RoboMasterService.robo_master_stats import RoboMasterStats

RobotMasterStat = RoboMasterStats()


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

            # 各模块初始化
            self._ep_arm = self._robot.robotic_arm
            self._chassis = self._robot.chassis
            self._gripper = self._robot.gripper
            self._sensor = self._robot.sensor

            # 机械臂回中
            self._ep_arm.recenter()

            # 设置状态订阅
            # self._ep_arm.sub_position(freq=5, callback=self.sub_arm_pos)
            # self._chassis.sub_position(freq=5, callback=self.sub_chassis_pos)
            self._gripper.sub_status(freq=5, callback=self.sub_gripper_status)
            # self._sensor.sub_distance(freq=5, callback=self.sub_sensor_distance)

            # for test
            import time
            # self._gripper.open(power=50)
            # time.sleep(3)
            # self._gripper.pause()

            self._gripper.close(power=50)
            time.sleep(3)
            self._gripper.pause()

        except Exception as err:
            self._camera = None
            self._robot.close()
            logging.error(f"exception: {err}")

    @staticmethod
    def sub_sensor_distance(sub_info):
        logging.info(f"sub_gripper_status: {sub_info}")
        RobotMasterStat.distance = sub_info

    @staticmethod
    def sub_gripper_status(sub_info):
        logging.info(f"sub_gripper_status: {sub_info}")
        RobotMasterStat.gripper_status = sub_info

    @staticmethod
    def sub_arm_pos(sub_info):
        logging.info(f"sub_arm_pos: {sub_info}")
        x, y = sub_info
        RobotMasterStat.robotic_arm_pos = {
            'x': x,
            'y': y
        }

    @staticmethod
    def sub_chassis_pos(position_info):
        logging.info(f"sub_chassis_pos: {position_info}")
        x, y, z = position_info
        RobotMasterStat.chassis_pos = {
            'x': x,
            'y': y,
            'z': z
        }

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
                self._robot.close()
                break

            img = self._camera.read_cv2_image()
            if img is not None:
                tennis_detect_service = TennisDetectService((low_color, high_color), cap_frame=img)
                tennis_detect_service.detect_color()
                if cv2.waitKey(1) == ord('q'):
                    break

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

        if self._cap:
            self._cap.release()
            cv2.destroyAllWindows()

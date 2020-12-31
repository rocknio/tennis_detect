# -*- coding: utf-8 -*-
import cv2
import logging
from robomaster import robot


class RoboMasterService:
    def __init__(self):
        self._is_need_stop = False
        self._is_running = False
        self._robot = None
        self._camera = None
        try:
            self._robot = robot.Robot()
            self._robot.initialize(conn_type='sta')
            self._camera = self._robot.camera
        except Exception:
            pass

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
                break

            img = ep_camera.read_cv2_image()
            if img:
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

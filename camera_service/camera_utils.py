# -*- coding: utf-8 -*-
import cv2
import logging
from tennis_detect_service.tennis_detect import TennisDetectService


class CameraService:
    def __init__(self, channel):
        self._channel = channel
        self._is_need_stop = False
        self._is_running = False
        self._open_capture_channel()

    def _open_capture_channel(self):
        try:
            self._cap = cv2.VideoCapture(self._channel)
        except Exception as e:
            self._cap = None
            logging.error("Open channel = {} is failed with error: {}".format(self._channel, e))
    
    def start_capture(self):
        if self._cap is None:
            logging.error("capture channel is not open yet")
            return

        self._is_running = True
        while True:
            if self._is_need_stop:
                logging.info("capture is stopped!")
                self._is_running = False
                self._is_need_stop = False
                break

            ret, frame = self._cap.read()
            if ret is False:
                logging.error("capture read failed")
                break
            else:
                tennis_detect_service = TennisDetectService([([0, 60, 100], [95, 255, 255])], cap_frame=frame)
                tennis_detect_service.detect_color()

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

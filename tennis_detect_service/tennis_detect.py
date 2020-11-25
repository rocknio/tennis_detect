# -*- coding: utf-8 -*-
import cv2
import logging
import numpy as np


class TennisDetectService(object):
    def __init__(self, color_boundaries, img_path=None, cap_frame=None):
        self._image_path = img_path
        if self._image_path is not None:
            self._output_path = '.' + self._image_path.split('.')[1] + '_out.' + self._image_path.split('.')[2]
            try:
                self._image = cv2.imread(self._image_path)
                if self._image is None:
                    logging.error(f"TennisDetect, __init__ failed: {self._image_path} is not available")
            except Exception as e:
                logging.error("TennisDetect, __init__ failed: %s", e)
                self._image = None
        elif cap_frame is not None:
            self._image = cap_frame

        self._color_boundaries = color_boundaries

    def detect_color(self):
        if self._image is None:
            return None

        # hsv = cv2.cvtColor(self._image, cv2.COLOR_RGB2HSV)
        cv2.imshow("original", self._image)
        for (lower, upper) in self._color_boundaries:
            lower = np.array(lower)
            upper = np.array(upper)

            mask = cv2.inRange(self._image, lower, upper)
            cv2.imshow("mask", mask)
            res = cv2.bitwise_and(self._image, self._image, mask=mask)
            cv2.imshow("result", res)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

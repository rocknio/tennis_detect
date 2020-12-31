# -*- coding: utf-8 -*-
import cv2
import logging
import numpy as np
from enum import Enum


class DetectShape(Enum):
    circle = "CIRCLE"
    rect = "RECT"
    triangle = "TRIANGLE"


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

    @staticmethod
    def find_max_contours(contours):
        max_contour = None
        for c in contours:
            if cv2.contourArea(c) <= 50:
                continue

            if max_contour is None:
                max_contour = c
            else:
                if cv2.contourArea(c) > cv2.contourArea(max_contour):
                    max_contour = c

        return max_contour

    def get_direction(self, dst_center):
        image_center = (self._image.shape[0] // 2, self._image.shape[1] // 2)

        ret = []
        if image_center[0] < dst_center[0]:
            ret.append('left|{}'.format(image_center[0] - dst_center[0]))
        elif image_center[0] > dst_center[0]:
            ret.append('right|{}'.format(image_center[0] - dst_center[0]))
        else:
            ret.append(None)

        if image_center[1] < dst_center[1]:
            ret.append('up|{}'.format(image_center[1] - dst_center[1]))
        elif image_center[1] > dst_center[1]:
            ret.append('down|{}'.format(image_center[1] - dst_center[1]))
        else:
            ret.append(None)

        print(ret)
        return ret

    @staticmethod
    def detect_shape(contour):
        if contour is None:
            return

        # 轮廓逼近
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # 分析形状
        corners = len(approx)
        shape = ""
        if corners == 3:
            shape = DetectShape.triangle.value
        elif corners == 4:
            shape = DetectShape.rect.value
        elif corners > 10:
            shape = DetectShape.circle.value

        return shape

    def detect_color(self):
        if self._image is None:
            return None

        # cv2.imshow("original", self._image)
        lower = np.array(self._color_boundaries[0])
        upper = np.array(self._color_boundaries[1])

        mask = cv2.inRange(self._image, lower, upper)
        res = cv2.bitwise_and(self._image, self._image, mask=mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        c = self.find_max_contours(contours)
        shape = self.detect_shape(c)
        x, y, w, h = cv2.boundingRect(c)
        cv2.rectangle(res, (x, y), (x + w, y + h), (0, 0, 255), 2)
        center = (x + w // 2, y + h // 2)
        cv2.rectangle(res, (center[0], center[1]), (center[0] + 2, center[1] + 2), (0, 0, 255), 2)
        self.get_direction(center)

        image_center = (self._image.shape[0] // 2, self._image.shape[1] // 2)
        cv2.rectangle(res,
                      (image_center[1], image_center[0]),
                      (image_center[1] + 5, image_center[0] + 5),
                      (0, 0, 255),
                      2)

        cv2.putText(res,
                    shape,
                    center,
                    cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 0), 1)

        cv2.imshow("result", res)

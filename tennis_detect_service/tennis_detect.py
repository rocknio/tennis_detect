# -*- coding: utf-8 -*-
import cv2
import logging
import numpy as np
from enum import Enum

from settings import detect_zoo, x_match_limit_pixel, y_match_limit_pixel


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

    @staticmethod
    def detect_edge(img):
        # 高斯模糊
        blurred = cv2.GaussianBlur(img, (3, 3), 0)

        # 灰度
        gray = cv2.cvtColor(blurred, cv2.COLOR_RGBA2GRAY)

        # 图像梯度
        x_grad = cv2.Sobel(gray, cv2.CV_16SC1, 1, 0)
        y_grad = cv2.Sobel(gray, cv2.CV_16SC1, 0, 1)

        # 计算边缘
        edge_output = cv2.Canny(x_grad, y_grad, 80, 240)

        dst = cv2.bitwise_and(img, img, mask=edge_output)
        return dst

    @staticmethod
    def is_detect_contour_in_zoo(contour):
        x, y, w, h = cv2.boundingRect(contour)
        contour_area = w * h

        detect_zoo_w = detect_zoo[1][0] - detect_zoo[0][0]
        detect_zoo_h = detect_zoo[1][1] - detect_zoo[1][0]

        # TODO: 待完成面积占比计算

    @staticmethod
    def is_x_match(detect_center, dst_center):
        detect_x = detect_center[0]
        dst_x = dst_center[0]
        diff = abs(dst_x - detect_x)
        return diff <= x_match_limit_pixel

    @staticmethod
    def is_y_match(detect_center, dst_center):
        detect_y = detect_center[1]
        dst_y = dst_center[1]
        diff = abs(dst_y - detect_y)
        return diff <= y_match_limit_pixel

    def is_match(self, detect_center, dst_center):
        x_match = self.is_x_match(detect_center, dst_center)
        y_match = self.is_y_match(detect_center, dst_center)
        return x_match and y_match

    def detect_color(self):
        if self._image is None:
            return None

        direction = None
        is_match = False

        lower = np.array(self._color_boundaries[0])
        upper = np.array(self._color_boundaries[1])

        mask = cv2.inRange(self._image, lower, upper)
        # res = cv2.bitwise_and(self._image, self._image, mask=mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        c = self.find_max_contours(contours)
        if c.all():
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(self._image, (x, y), (x + w, y + h), (0, 0, 255), 2)

            # 画出被探测物体区域中心点
            center = (x + w // 2, y + h // 2)
            cv2.rectangle(self._image, (center[0], center[1]), (center[0] + 2, center[1] + 2), (0, 0, 255), 2)

            # 画出探测区域中心点
            detect_zoo_center = (detect_zoo[0][1] + (detect_zoo[1][1] - detect_zoo[0][1]) // 2,
                                 detect_zoo[0][0] + (detect_zoo[1][0] - detect_zoo[0][0]) // 2)
            cv2.rectangle(self._image,
                          (detect_zoo_center[1], detect_zoo_center[0]),
                          (detect_zoo_center[1] + 5, detect_zoo_center[0] + 5),
                          (0, 255, 0),
                          2)

            # 判断偏移方向和像素距离
            direction = self.get_direction(center)

            # 划线重点探测区域
            cv2.rectangle(self._image, detect_zoo[0], detect_zoo[1], (0, 255, 0), 2)

            cv2.imshow("result", self._image)

        cv2.imshow("result", self._image)
        return direction, is_match

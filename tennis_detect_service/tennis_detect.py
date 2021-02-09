# -*- coding: utf-8 -*-
import cv2
import logging
import numpy as np
from enum import Enum


class DetectShape(Enum):
    circle = "CIRCLE"
    rect = "RECT"
    triangle = "TRIANGLE"


class Colors(Enum):
    red = (0, 0, 255)
    green = (0, 255, 255)
    blue = (255, 0, 0)


class TennisDetectService(object):
    def __init__(self, config, img_path=None, cap_frame=None):
        self._cfg = config
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

        # self._color_boundaries = color_boundaries

    def find_max_contours(self, contours):
        max_contour = None
        for c in contours:
            if cv2.contourArea(c) <= self._cfg['min_contour_area']:
                continue

            if max_contour is None:
                max_contour = c
            else:
                if cv2.contourArea(c) > cv2.contourArea(max_contour):
                    max_contour = c

        if max_contour is not None:
            return max_contour, True
        else:
            return max_contour, False

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

    def is_x_match(self, detect_center, dst_center):
        detect_x = detect_center[0]
        dst_x = dst_center[1]
        diff = abs(dst_x - detect_x)
        return diff <= self._cfg['limit_pixel']['x'], dst_x - detect_x

    def is_y_match(self, detect_center, dst_center):
        detect_y = detect_center[1]
        dst_y = dst_center[0]
        diff = abs(dst_y - detect_y)
        return diff <= self._cfg['limit_pixel']['y'], dst_y - detect_y

    def is_match(self, detect_center, dst_center):
        x_match, delta_x = self.is_x_match(detect_center, dst_center)
        y_match, delta_y = self.is_y_match(detect_center, dst_center)
        return x_match and y_match, (delta_x, delta_y)

    def detect_color(self):
        if self._image is None:
            return None

        delta = None
        is_match = False

        lower = np.array([self._cfg['low_color']['blue'],
                          self._cfg['low_color']['red'],
                          self._cfg['low_color']['green']])
        upper = np.array([self._cfg['high_color']['blue'],
                          self._cfg['high_color']['red'],
                          self._cfg['high_color']['green']])

        mask = cv2.inRange(self._image, lower, upper)
        # res = cv2.bitwise_and(self._image, self._image, mask=mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        c, is_found = self.find_max_contours(contours)
        if is_found:
            # 画出探测区域中心点
            detect_zone_center = (self._cfg['detect_zone']['top_left']['y']
                                  + (self._cfg['detect_zone']['down_right']['y']
                                     - self._cfg['detect_zone']['top_left']['y']) // 2,

                                  self._cfg['detect_zone']['top_left']['x']
                                  + (self._cfg['detect_zone']['down_right']['x']
                                     - self._cfg['detect_zone']['top_left']['x']) // 2,)

            cv2.rectangle(self._image,
                          (detect_zone_center[1], detect_zone_center[0]),
                          (detect_zone_center[1] + self._cfg['limit_pixel']['x'] // 2,
                           detect_zone_center[0] + self._cfg['limit_pixel']['y'] // 2),
                          (0, 255, 0),
                          2)

            # 划线重点探测区域
            cv2.rectangle(self._image,
                          (self._cfg['detect_zone']['top_left']['x'], self._cfg['detect_zone']['top_left']['y']),
                          (self._cfg['detect_zone']['down_right']['x'], self._cfg['detect_zone']['down_right']['y']),
                          (0, 255, 0), 2)

            # 画出被探测物体区域及中心点
            x, y, w, h = cv2.boundingRect(c)
            center = (x + w // 2, y + h // 2)

            is_match, delta = self.is_match(center, detect_zone_center)
            if is_match:
                center_color = Colors.green.value
            else:
                center_color = Colors.red.value

            cv2.rectangle(self._image, (x, y), (x + w, y + h), center_color, 2)

            cv2.rectangle(self._image, (center[0], center[1]), (center[0] + 2, center[1] + 2), center_color, 2)

            # 返回值打印在图像上
            text = f'is_match = {is_match}, delta = {delta}'
            cv2.putText(self._image, text, (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0, center_color, 2)

        cv2.imshow("result", self._image)
        return is_match, delta

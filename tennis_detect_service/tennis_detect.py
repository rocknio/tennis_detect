# -*- coding: utf-8 -*-
from typing import List, Tuple

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
    green = (0, 255, 0)
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
        return x_match, y_match, (delta_x, delta_y)

    @staticmethod
    def contour_analysis(cnt) -> Tuple[int, int]:
        approx = cv2.approxPolyDP(cnt, 0.01 * cv2.arcLength(cnt, True), True)
        area = cv2.contourArea(cnt)
        return len(approx), area

    def biggest_circle_cnt(self, cnts: List):
        found_cnt = None
        found_area = 0

        for cnt in cnts:
            edges, area = self.contour_analysis(cnt)
            if edges > 10 \
                    and self._cfg['min_contour_area'] < area \
                    and area > found_area:
                found_area = area
                found_cnt = cnt

        return found_cnt

    def detect_color(self, hsv=True):
        if self._image is None:
            return None, None, None

        delta = None
        x_match, y_match = False, False
        # 画出探测区域中心点
        detect_zone_center = (self._cfg['detect_zone']['down_right']['y']
                              - (self._cfg['detect_zone']['down_right']['y']
                                 - self._cfg['detect_zone']['top_left']['y']) // 2 // 2,

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

        if hsv:
            processed = cv2.GaussianBlur(self._image, (11, 11), 0)
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2HSV)

            lower = tuple(self._cfg['hsv_low'])
            upper = tuple(self._cfg['hsv_high'])
            mask = cv2.inRange(processed, lower, upper)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, None)
            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            c = self.biggest_circle_cnt(cnts)
        else:
            lower = np.array([self._cfg['low_color']['blue'],
                              self._cfg['low_color']['red'],
                              self._cfg['low_color']['green']])
            upper = np.array([self._cfg['high_color']['blue'],
                              self._cfg['high_color']['red'],
                              self._cfg['high_color']['green']])

            mask = cv2.inRange(self._image, lower, upper)

            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            c = self.biggest_circle_cnt(contours)

        if c is not None:
            # 画出被探测物体区域及中心点
            x, y, w, h = cv2.boundingRect(c)
            center = (x + w // 2, y + h // 2)

            x_match, y_match, delta = self.is_match(center, detect_zone_center)
            if x_match and y_match:
                center_color = Colors.green.value
            else:
                center_color = Colors.red.value

            # cv2.rectangle(self._image, (x, y), (x + w, y + h), center_color, 2)
            # cv2.rectangle(self._image, (center[0], center[1]), (center[0] + 2, center[1] + 2), center_color, 2)
            (x, y), pixel_radius = cv2.minEnclosingCircle(c)
            cv2.circle(self._image, (int(x), int(y)), int(pixel_radius), center_color, 2)
            cv2.circle(self._image, (int(x), int(y)), 1, center_color, 2)

            # 返回值打印在图像上
            text = f'x_match = {x_match} and y_match = {y_match}, delta = {delta}'
            cv2.putText(self._image, text, (40, 50), cv2.FONT_HERSHEY_PLAIN, 2.0, center_color, 2)

        cv2.imshow("result", self._image)
        return x_match, y_match, delta

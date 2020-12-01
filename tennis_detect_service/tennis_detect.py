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
            ret.append('left')
        elif image_center[0] > dst_center[0]:
            ret.append('right')
        else:
            ret.append(None)

        if image_center[1] < dst_center[1]:
            ret.append('down')
        elif image_center[1] > dst_center[1]:
            ret.append('up')
        else:
            ret.append(None)

        print(ret)
        return ret

    def detect_color(self):
        if self._image is None:
            return None

        # hsv = cv2.cvtColor(self._image, cv2.COLOR_RGB2HSV)
        cv2.imshow("original", self._image)
        for (lower, upper) in self._color_boundaries:
            lower = np.array(lower)
            upper = np.array(upper)

            mask = cv2.inRange(self._image, lower, upper)
            res = cv2.bitwise_and(self._image, self._image, mask=mask)

            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            c = self.find_max_contours(contours)
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(res, (x, y), (x + w, y + h), (0, 0, 255), 2)
            center = (x + w // 2, y + h // 2)
            cv2.rectangle(res, (center[0], center[1]), (center[0] + 2, center[1] + 2), (0, 0, 255), 2)
            self.get_direction(center)
            cv2.imshow("result", res)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

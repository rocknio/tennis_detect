# -*- coding: utf-8 -*-


CONST_MAX_DISTANCE = 999999999.0
CONST_FLOAT_INIT = 0.0


class RoboMasterStats:
    def __init__(self, sn=''):
        self.sn = sn

        # 车身周围测距，
        self.ir = {
            'switch': 'off',
            'distance': CONST_MAX_DISTANCE
        }

        # 车辆运动速度，单位：米/秒
        self.speed = {
            'x': CONST_FLOAT_INIT,  # 前进方向，负数 = 后退，正数 = 前进
            'y': CONST_FLOAT_INIT,  # 横移方向，负数 = 左移，正数 = 右移
            'z': CONST_FLOAT_INIT   # 转动方向，负数 = 左转，正数 = 右转
        }

        # 机械爪状态
        self.gripper_status = 'closed'

        # 机械臂位置
        self.robotic_arm_pos = {
            'x': CONST_FLOAT_INIT,
            'y': CONST_FLOAT_INIT
        }

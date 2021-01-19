# -*- coding: utf-8 -*-


CONST_MAX_DISTANCE = 999999999.0


class RoboMasterStats:
    def __init__(self, sn=''):
        self.sn = sn

        # 车身周围测距，
        self.distance = [CONST_MAX_DISTANCE, CONST_MAX_DISTANCE, CONST_MAX_DISTANCE, CONST_MAX_DISTANCE]

        # 车辆运动速度，单位：米/秒
        self.driver_speed = {
            'x': 0,  # 前进方向，负数 = 后退，正数 = 前进
            'y': 0,  # 横移方向，负数 = 左移，正数 = 右移
            'z': 0   # 转动方向，负数 = 左转，正数 = 右转
        }

        # 车辆底盘位置
        self.chassis_pos = {
            'x': CONST_MAX_DISTANCE,   # x 轴方向距离，单位：米
            'y': CONST_MAX_DISTANCE,   # y 轴方向距离，单位：米
            'z': CONST_MAX_DISTANCE    # z 轴方向旋转角度，单位：度
        }

        # 机械爪状态
        self.gripper_status = 'closed'

        # 机械臂位置
        self.robotic_arm_pos = {
            'x': 0.0,
            'y': 0.0
        }

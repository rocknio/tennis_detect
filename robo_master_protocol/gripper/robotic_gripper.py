import logging
from enum import Enum

from robo_master_protocol.common.utils import check_robot_resp_ok, MyEnumMeta
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class GripperStatus(Enum, metaclass=MyEnumMeta):
    open = 'open'
    close = 'close'


class GripperStrengthLevel(Enum, metaclass=MyEnumMeta):
    lowest = 1
    normal = 2
    high = 3
    max = 4


class RoboticGripper:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def gripper_status(self):
        ret = self._robot_ctrl.robot_do_command('robotic_gripper status ?')
        if ret == 'fail':
            logging.error(f'get gripper_status fail')
        else:
            self._robot_ctrl.stat.gripper_status = ret

    def gripper_ctrl(self, mode: str, level: int = 1):
        if mode not in GripperStatus.value or level not in GripperStrengthLevel:
            logging.error(f"param is invalid: {mode} -- {level}")
            return

        ret = self._robot_ctrl.robot_do_command(f'robotic_gripper {mode} {level}')
        if check_robot_resp_ok(ret):
            self._robot_ctrl.stat.gripper_status = mode
        else:
            logging.error(f'get gripper_status fail')

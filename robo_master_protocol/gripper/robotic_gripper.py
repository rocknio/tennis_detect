import logging
from enum import Enum

from robo_master_protocol.common.utils import check_robot_resp_ok, MyEnumMeta
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticGripper:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def gripper_status(self):
        """
        robot返回status始终未0，不要使用该方法
        :return:
        """
        ret = self._robot_ctrl.robot_do_command('robotic_gripper status ?')
        if int(ret) not in [0, 1, 2]:
            logging.error(f'get gripper_status fail')
        else:
            self._robot_ctrl.stat.gripper_status = int(ret)

        return int(ret)

    def gripper_ctrl(self, mode: str, level: int = 1):
        ret = self._robot_ctrl.robot_do_command(f'robotic_gripper {mode} {level}')
        if check_robot_resp_ok(ret):
            self._robot_ctrl.stat.gripper_status = mode
            return True
        else:
            logging.error(f'get gripper_status fail')
            return False

import logging
from enum import Enum

from robo_master_protocol.common.utils import check_robot_resp_ok, MyEnumMeta
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticIr:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def ir_switch(self, switch: str):
        ret = self._robot_ctrl.robot_do_command(f'ir_distance_sensor measure {switch}')
        if check_robot_resp_ok(ret):
            return True
        else:
            logging.error(f'set ir_switch = {switch} fail')
            return False

    def ir_distance(self):
        ret = self._robot_ctrl.robot_do_command('ir_distance_sensor distance 1 ?')
        if ret != 'fail':
            return True
        else:
            logging.error(f'get ir distance fail')
            return False

import logging
from enum import Enum

from robo_master_protocol.common.utils import check_robot_resp_ok, MyEnumMeta
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class IrSwitch(Enum, metaclass=MyEnumMeta):
    on = 'on'
    off = 'off'


class RoboticIr:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def ir_switch(self, switch: str):
        if switch not in IrSwitch:
            logging.error(f"param is invalid: {switch}")
            return

        ret = self._robot_ctrl.robot_do_command(f'ir_distance_sensor measure {switch}')
        if check_robot_resp_ok(ret):
            self._robot_ctrl.stat.ir['switch'] = switch
        else:
            logging.error(f'set ir_switch = {switch} fail')

    def ir_distance(self):
        if self._robot_ctrl.stat.ir['switch'] == IrSwitch.off.value:
            logging.warning(f'ir switch is off!!!')
            return

        ret = self._robot_ctrl.robot_do_command('ir_distance_sensor distance 1 ?')
        if ret != 'fail':
            self._robot_ctrl.stat.ir['distance'] = float(ret)
        else:
            logging.error(f'get ir distance fail')

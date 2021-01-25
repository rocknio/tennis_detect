import logging

from robo_master_protocol.common.utils import check_robot_resp_ok
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticArm:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def move(self, x, y, z):
        cmd = 'chassis speed'
        if x:
            cmd += f'x {x}'

        if y:
            cmd += f' y {y}'

        if x:
            cmd += f' z {z}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            if x:
                self._robot_ctrl.stat.speed['x'] = x

            if y:
                self._robot_ctrl.stat.speed['y'] = y

            if z:
                self._robot_ctrl.stat.speed['z'] = z
        else:
            logging.error(f'robotic speed move {x}:{y}:{z} failed, resp = {ret}')

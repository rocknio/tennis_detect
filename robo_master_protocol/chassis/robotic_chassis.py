import logging

from robo_master_protocol.common.utils import check_robot_resp_ok
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticChassis:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def move(self, x=0, y=0, z=0):
        cmd = f'chassis speed x {x} y {y} z {z}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            if x:
                self._robot_ctrl.stat.speed['x'] = x

            if y:
                self._robot_ctrl.stat.speed['y'] = y

            if z:
                self._robot_ctrl.stat.speed['z'] = z

            return True
        else:
            logging.error(f'robotic speed move {x}:{y}:{z} failed, resp = {ret}')
            return False

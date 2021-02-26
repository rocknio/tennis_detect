import logging

from robo_master_protocol.common.utils import check_robot_resp_ok
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


init_pos = (9, 3)
lowest_pos = (2, 0)


class RoboticArm:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def recenter(self):
        ret = self._robot_ctrl.robot_do_command('robotic_arm recenter')
        if check_robot_resp_ok(ret):
            return True
        else:
            return False

    def current_pos(self):
        pos = self._robot_ctrl.robot_do_command('robotic_arm position ?')
        return True

    def arm_move(self, x: float, y: float):
        cmd = f'robotic_arm moveto x {x} y {y}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            return True
        else:
            logging.error(f'robotic_arm moveto {x}:{y} failed, resp = {ret}')
            return False

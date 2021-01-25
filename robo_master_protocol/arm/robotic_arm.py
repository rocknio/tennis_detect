import logging

from robo_master_protocol.common.utils import check_robot_resp_ok
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticArm:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def recenter(self):
        self._robot_ctrl.robot_do_command('robotic_arm recenter')

    def current_pos(self):
        pos = self._robot_ctrl.robot_do_command('robotic_arm position ?')
        self._robot_ctrl.stat.robotic_arm_pos = {
            'x': pos[0],
            'y': pos[1]
        }

    def move_to(self, x, y):
        cmd = 'robotic_arm moveto '
        if x:
            cmd += f'x {x}'

        if y:
            cmd += f' y {y}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            if x:
                self._robot_ctrl.stat.robotic_arm_pos['x'] = x

            if y:
                self._robot_ctrl.stat.robotic_arm_pos['y'] = y
        else:
            logging.error(f'robotic_arm move to {x}:{y} failed, resp = {ret}')

import logging

from robo_master_protocol.common.utils import check_robot_resp_ok
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class RoboticAI:
    def __init__(self, robotic: RoboticConn):
        self._robot_ctrl = robotic

    def marker_set(self, color, dist):
        cmd = f'AI attribute marker_color {color} marker_dist {dist}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            return True
        else:
            logging.error(f'{cmd} failed, resp = {ret}')
            return False

    def marker_push_switch(self, switch):
        cmd = f'AI push marker {switch}'

        ret = self._robot_ctrl.robot_do_command(cmd)
        if check_robot_resp_ok(ret):
            return True
        else:
            logging.error(f'{cmd} failed, resp = {ret}')
            return False

    def marker_push_on(self):
        return self.marker_push_switch('on')

    def marker_push_off(self):
        return self.marker_push_switch('off')

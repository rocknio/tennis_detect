import logging
import socket

from robomaster import robot

from RoboMasterService.robo_master_stats import RoboMasterStats


class RoboticConn:
    def __init__(self, robot_host, robot_port, robotic: robot):
        self.conn = None
        self._address = (robot_host, int(robot_port))
        self.robot = robotic
        self.stat = RoboMasterStats(f"{self._address}")

    def connect_robo(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"connect to robot: {self._address}")

        try:
            self.conn.connect(address=self._address)
            logging.info(f"connected to {self._address}")
        except Exception as err:
            self.conn = None
            logging.error(f"connect to robotic failed! robot={self._address}, err = {err}")

    def disconnect_robo(self):
        if self.conn:
            self.conn.shutdown(socket.SHUT_WR)
            self.conn.close()
            self.conn = None

    def start_command_mode(self):
        self.robot_do_command("command")

    def reconnect_robo(self):
        self.disconnect_robo()
        self.connect_robo()

    def robot_do_command(self, msg):
        if self.conn:
            if msg[-1:] != ';':
                msg += ';'

            self.conn.send(msg.encode())

            try:
                resp = self.conn.recv(1024)
                if resp[-1:] == ';':
                    resp = resp[:-1]
                return resp
            except Exception as err:
                logging.error(f"Recv robot response error: {err}")
                self.reconnect_robo()
                return 'fail'

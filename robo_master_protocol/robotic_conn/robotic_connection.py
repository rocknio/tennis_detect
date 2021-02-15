import logging
import socket

from robomaster import robot

from RoboMasterService.robo_master_stats import RoboMasterStats
from robo_master_protocol.common.utils import check_robot_resp_ok
from config_util.settings import SettingService


class RoboticConn:
    def __init__(self, robotic: robot, sn):
        self.conn = None
        self.robot = robotic
        self.stat = RoboMasterStats(sn)
        self._address = None

    def connect_robo(self):
        if self.conn:
            return True

        ip_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # 绑定 IP 广播端口
        ip_sock.bind(('0.0.0.0', 40926))

        # 等待接收机器人广播数据
        data, ip_str = ip_sock.recvfrom(1024)
        host = ip_str[0]

        # 设置机器人连接地址端口
        self._address = (host, int(40923))

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        logging.info(f"connect to robot: {self._address}")

        try:
            self.conn.connect(self._address)
            logging.info(f"connected to {self._address}")

            # 开启命令模式
            ret = self.robot_do_command('command')
            if not check_robot_resp_ok(ret):
                logging.error(f"command mode set failed!")
                self.disconnect_robo()

            return True
        except Exception as err:
            self.disconnect_robo()
            logging.error(f"connect to robotic failed! robot={self._address}, err = {err}")
            return False

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

            self.conn.send(msg.encode('utf-8'))

            try:
                buf = self.conn.recv(1024)
                resp = buf.decode('utf-8')
                if resp[-1:] == ';':
                    resp = resp[:-1]
                return resp
            except Exception as err:
                logging.error(f"Recv robot response error: {err}")
                self.reconnect_robo()
                return 'fail'
        else:
            return 'fail'

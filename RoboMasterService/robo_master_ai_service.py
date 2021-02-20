import logging
import socket
import threading

from global_queue.global_queue import q


class RoboMasterPushReceiverService(threading.Thread):
    def __init__(self):
        super().__init__()
        self._q = q

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as conn:
            # 绑定 marker udp 推送端口
            conn.bind(('0.0.0.0', 40924))

            while True:
                buf = conn.recvfrom(1024)
                resp = buf[0].decode('utf-8')
                if resp[-1:] == ';':
                    resp = resp[:-1]

                logging.info(f"RECV RB AI Push: {resp}")
                self._q.put(resp)

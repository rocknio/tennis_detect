import socket
import threading


class RoboMasterPushReceiverService(threading.Thread):
    def __init__(self, q):
        super().__init__()
        self._q = q

    def run(self):
        while True:
            ip_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # 绑定 robot 事件推送端口
            ip_sock.bind(('0.0.0.0', 40925))
            buf = ip_sock.recv(1024)
            resp = buf.decode('utf-8')
            if resp[-1:] == ';':
                resp = resp[:-1]

            self._q.send(resp)

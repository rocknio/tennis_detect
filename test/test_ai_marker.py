import queue
import unittest

from robomaster import robot

from RoboMasterService.robo_master_ai_service import RoboMasterPushReceiverService
from robo_master_protocol.AI_recognition.robotic_ai import RoboticAI
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestAI(unittest.TestCase):

    def setUp(self) -> None:
        self._robot = robot.Robot()
        self._robot_conn = RoboticConn(self._robot)

        self._robot_conn.connect_robo()
        self._ai = RoboticAI(self._robot_conn)

    def tearDown(self) -> None:
        self._robot_conn.disconnect_robo()
        print(f"robot stat = {self._robot_conn.stat.ir}")

    def test_marker_set(self, color, dist):
        self._ai.marker_set(color, dist)

    def test_marker_on(self):
        ret = self._ai.marker_push_on()
        self.assertEqual(ret, True)

        q = queue.Queue()
        push_service = RoboMasterPushReceiverService(q)
        push_service.start()

        while True:
            msg = q.get()
            print(f"Recv robot AI push: {msg}")
            break

        self.assertIn("marker", msg)

    def test_marker_off(self):
        ret = self._ai.marker_push_off()
        self.assertEqual(ret, True)


if __name__ == '__main__':
    unittest.main()

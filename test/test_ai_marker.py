import unittest

from robomaster import robot

from RoboMasterService.robo_master_ai_service import RoboMasterPushReceiverService
from global_queue.global_queue import q
from robo_master_protocol.AI_recognition.robotic_ai import RoboticAI
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestAI(unittest.TestCase):

    def setUp(self) -> None:
        self._robot = robot.Robot()
        self._robot_conn = RoboticConn(self._robot, '')

        self._robot_conn.connect_robo()
        self._ai = RoboticAI(self._robot_conn)

    def tearDown(self) -> None:
        self._ai.marker_push_off()
        self._robot_conn.disconnect_robo()

    def test_marker_set(self):
        self._ai.marker_set('red', 0.5)

    def test_marker_on(self):
        self._ai.marker_set('red', 0.5)
        ret = self._ai.marker_push_on()
        self.assertEqual(ret, True)

        push_service = RoboMasterPushReceiverService()
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

import unittest

from robomaster import robot

from robo_master_protocol.gripper.robotic_gripper import RoboticGripper
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestGripper(unittest.TestCase):

    def setUp(self) -> None:
        self._robot = robot.Robot()
        self._robot_conn = RoboticConn(self._robot)

        self._robot_conn.connect_robo()
        self._gripper = RoboticGripper(self._robot_conn)

    def tearDown(self) -> None:
        self._robot_conn.disconnect_robo()

    def test_gripper_status(self):
        ret = self._gripper.gripper_status()
        self.assertIn(ret, [0, 1, 2])

    def test_gripper_open(self):
        ret = self._gripper.gripper_ctrl('open')
        self.assertEqual(ret, True)

    def test_gripper_close(self):
        ret = self._gripper.gripper_ctrl('close')
        self.assertEqual(ret, True)


if __name__ == '__main__':
    unittest.main()

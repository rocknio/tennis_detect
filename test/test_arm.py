import unittest

from robomaster import robot

from robo_master_protocol.arm.robotic_arm import RoboticArm
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestArm(unittest.TestCase):

    def setUp(self) -> None:
        self._robot = robot.Robot()
        self._robot_conn = RoboticConn(self._robot)

        self._robot_conn.connect_robo()
        self._arm = RoboticArm(self._robot_conn)

    def tearDown(self) -> None:
        self._robot_conn.disconnect_robo()

    def test_arm_recenter(self):
        self.assertEqual(self._arm.recenter(), True)

    def test_arm_pos(self):
        self.assertEqual(self._arm.current_pos(), True)

    def test_arm_move(self):
        self.assertEqual(self._arm.arm_move(self, 100, 100), True)


if __name__ == '__main__':
    unittest.main()

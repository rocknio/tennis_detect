import time
import unittest

from robomaster import robot

from robo_master_protocol.chassis.robotic_chassis import RoboticChassis
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestArm(unittest.TestCase):

    def setUp(self) -> None:
        self._robot = robot.Robot()
        self._robot_conn = RoboticConn(self._robot)

        self._robot_conn.connect_robo()
        self._chassis = RoboticChassis(self._robot_conn)

    def tearDown(self) -> None:
        self._robot_conn.disconnect_robo()

    def test_ir_move(self):
        self.assertEqual(self._chassis.move(x=0.2), True)
        time.sleep(2)

        self.assertEqual(self._chassis.move(x=-0.2), True)
        time.sleep(2)

        self.assertEqual(self._chassis.move(y=0.2), True)
        time.sleep(2)

        self.assertEqual(self._chassis.move(y=-0.2), True)
        time.sleep(2)

        self.assertEqual(self._chassis.move(z=60), True)
        time.sleep(6)

        self.assertEqual(self._chassis.move(z=-60), True)
        time.sleep(6)

        self.assertEqual(self._chassis.move(), True)


if __name__ == '__main__':
    unittest.main()

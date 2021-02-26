import unittest

# from robomaster import robot

from robo_master_protocol.ir.robotic_ir import RoboticIr
from robo_master_protocol.robotic_conn.robotic_connection import RoboticConn


class TestArm(unittest.TestCase):

    def setUp(self) -> None:
        # self._robot = robot.Robot()
        self._robot_conn = RoboticConn()

        self._robot_conn.connect_robo()
        self._ir = RoboticIr(self._robot_conn)

    def tearDown(self) -> None:
        self._robot_conn.disconnect_robo()
        # print(f"robot stat = {self._robot_conn.stat.ir}")

    def test_ir_switch_on(self):
        self.assertEqual(self._ir.ir_switch('on'), True)

    def test_ir_distance(self):
        self._ir.ir_switch('on')
        self.assertEqual(self._ir.ir_distance(), True)


if __name__ == '__main__':
    unittest.main()

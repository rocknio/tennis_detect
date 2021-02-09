from robo_master_protocol.arm.robotic_arm import RoboticArm
from robo_master_protocol.chassis.robotic_chassis import RoboticChassis
from robo_master_protocol.gripper.robotic_gripper import RoboticGripper
from robo_master_protocol.ir.robotic_ir import RoboticIr


class RoboticController:
    def __init__(self, robotic_conn):
        self._robotic_conn = None
        self._arm = None
        self._gripper = None
        self._ir = None
        self._chassis = None

        if robotic_conn:
            self._robotic_conn = robotic_conn

            # 初始化各模块
            self._arm = RoboticArm(self._robotic_conn)
            self._gripper = RoboticGripper(self._robotic_conn)
            self._ir = RoboticIr(self._robotic_conn)
            self._chassis = RoboticChassis(self._robotic_conn)

    def move_left(self, speed):
        if self._chassis:
            self._chassis.move(y=(-1 * speed))

    def move_right(self, speed):
        if self._chassis:
            self._chassis.move(y=speed)

    def move_forward(self, speed):
        if self._chassis:
            self._chassis.move(x=speed)

    def move_backward(self, speed):
        if self._chassis:
            self._chassis.move(x=(-1 * speed))

    def move_rotate(self, speed, direction):
        if self._chassis:
            self._chassis.move(x=(direction * speed))

    def expand_arm(self, x, y):
        if self._arm:
            self._arm.arm_move(x, y)

    def reset_arm(self):
        if self._arm:
            self._arm.recenter()

    def close_gripper(self):
        if self._gripper:
            self._gripper.gripper_ctrl('close')

    def open_gripper(self):
        if self._gripper:
            self._gripper.gripper_ctrl('open')

from pybricks.ev3devices import Motor

from parts.ArmPart import ArmPart


class GripperPart(ArmPart):
    def __init__(self, motor: Motor):
        super().__init__("Gripper")
        self.motor = motor

    def grab(self):
        self.motor.run_angle(100, 90)
        self.motor.hold()
        print("Gripper grabbed")
        return True

    def release(self):
        self.motor.run_angle(100, -90)
        self.motor.hold()
        print("Gripper released")
        return True

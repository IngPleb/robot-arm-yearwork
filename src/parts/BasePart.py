from pybricks.ev3devices import Motor, TouchSensor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class BasePart(ArmPart):
    def __init__(self, motor: Motor, touch_sensor: TouchSensor, ration: float):
        super().__init__("Base")
        self.motor = motor
        self.touchSensor = touch_sensor
        self.ration = ration

        motor.hold()

    def calibrate(self):
        calibration_speed = 100

        while not self.touchSensor.pressed():
            self.motor.run(calibration_speed)
            wait(10)

        self.motor.reset_angle(0)
        self.motor.hold()
        print("Calibration of " + self.name + " complete")
        return True

    def move_to_angle(self, angle):
        self.motor.run_target(100, angle)
        self.motor.hold()
        print("Base moved to angle: " + str(angle))
        return True

from pybricks.ev3devices import Motor, TouchSensor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class BasePart(ArmPart):
    def __init__(self, motor: Motor, touch_sensor: TouchSensor, ratio: float):
        super().__init__("Base", motor, ratio)
        self.touchSensor = touch_sensor

    def calibrate(self):
        calibration_speed = 100

        while not self.touchSensor.pressed():
            self.motor.run(calibration_speed)
            wait(10)

        self.motor.hold()

        # Wait for the motor to debounce
        wait(250)

        self.motor.reset_angle(0)
        print("[Base] Calibration complete")
        return True

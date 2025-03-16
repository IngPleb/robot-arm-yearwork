from pybricks.ev3devices import Motor, TouchSensor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class ShoulderPart(ArmPart):
    def __init__(self, motor: Motor, touch_sensor: TouchSensor, ratio, length: float):
        super().__init__('Shoulder', motor, ratio)
        self.touch_sensor = touch_sensor
        self.length = length

    def calibrate(self):
        calibration_speed = 100

        while not self.touch_sensor.pressed():
            self.motor.run(calibration_speed)
            wait(10)

        self.motor.hold()

        # Wait for the motor to debounce
        wait(250)

        self.motor.reset_angle(0)
        print("[Shoulder] Calibration complete")
        return True

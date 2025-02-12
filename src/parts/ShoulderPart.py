from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class ShoulderPart(ArmPart):
    def __init__(self, motor: Motor, sonic_sensor: UltrasonicSensor, ratio, length: float):
        super().__init__('Shoulder', motor, ratio)
        self.sonic_sensor = sonic_sensor
        self.length = length

    def calibrate(self):
        calibration_speed = 100
        target_ticks = 3
        tick_count = 0

        while tick_count < target_ticks:
            distance = self.sonic_sensor.distance()
            if distance <= 60:
                tick_count += 1

            self.motor.run(calibration_speed)

            wait(10)

        self.motor.hold()

        # Wait for the motor to debounce
        wait(250)

        self.motor.reset_angle(0)
        print("Calibration of " + self.name + " complete")
        return True

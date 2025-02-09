from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class ShoulderPart(ArmPart):
    def __init__(self, motor: Motor, sonic_sensor: UltrasonicSensor, ratio, length: float):
        super().__init__('Shoulder')
        self.motor = motor
        self.sonic_sensor = sonic_sensor
        self.ratio = ratio
        self.length = length

        self.motor.hold()

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
        self.motor.reset_angle(0)
        print("Calibration of " + self.name + " complete")
        return True

    def move_to_angle(self, angle):
        self.motor.run_target(100, angle * self.ratio)
        self.motor.hold()
        print("Shoulder moved to angle: " + str(angle))
        return True

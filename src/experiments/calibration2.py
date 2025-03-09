#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, UltrasonicSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()
motor = Motor(Port.A)
ultrasound = UltrasonicSensor(Port.S3)
motor.hold()

# Calibration parameters
SPEED = 100
TARGET_TICKS = 3  # can be set to any value between 3-5 or made configurable

tick_count = 0

while tick_count < TARGET_TICKS:
    # Check ultrasonic sensor distance
    distance = ultrasound.distance()
    if distance <= 60:
        tick_count += 1

    motor.run(SPEED)
    print("Tick count: " + str(tick_count))
    print("Ultrasonic distance: " + str(distance))

    wait(10)

motor.hold()

motor.reset_angle(0)
ev3.speaker.beep()
print("Calibration complete")

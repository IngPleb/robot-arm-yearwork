#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()
motor = Motor(Port.D)
touch_sensor = TouchSensor(Port.S4)
motor.hold()

# Calibration parameters
SPEED = 100


while True:
    if touch_sensor.pressed():
        break
    motor.run(SPEED)

    wait(10)

motor.hold()

motor.reset_angle(0)
ev3.speaker.beep()
print("Calibration complete")
#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()
color_sensor = ColorSensor(Port.S3)

while True:
    print(color_sensor.rgb())
    wait(1000)
#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()
motor = Motor(Port.D)

# Run the motor at speed 100
motor.run(-100)

# Let it run for 2 seconds
wait(20000)

# Stop the motor
motor.hold()

print("Test complete")
#!/usr/bin/env pybricks-micropython

"""
MAIN MODULE

This module is the entry point of the Mindstorm EV3 robot program.

"""

from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Button
from pybricks.tools import wait

# Constants
speed = 200

# Initialize the EV3 Brick
ev3 = EV3Brick()

# Initialize the motor
motor = Motor(Port.A)
motor2 = Motor(Port.B)
motor3 = Motor(Port.C)
motor3_direction = 1


def main():
    global speed, motor3_direction
    while True:
        pressed_buttons = ev3.buttons.pressed()

        if Button.LEFT in pressed_buttons:
            while Button.LEFT in ev3.buttons.pressed():
                motor.run(speed)
                wait(10)
            motor.hold()
        elif Button.RIGHT in pressed_buttons:
            while Button.RIGHT in ev3.buttons.pressed():
                motor.run(-speed)
                wait(10)
            motor.hold()
        elif Button.UP in pressed_buttons:
            while Button.UP in ev3.buttons.pressed():
                motor2.run(speed)
                wait(10)
            motor2.hold()
        elif Button.DOWN in pressed_buttons:
            while Button.DOWN in ev3.buttons.pressed():
                motor2.run(-speed)
                wait(10)
            motor2.hold()
        elif Button.CENTER in pressed_buttons:
            motor3.run(-speed)
            wait(500)  # Debounce delay
            motor3.hold()
        else:
            motor.hold()
            motor2.hold()
            motor3.hold()

        print(motor.angle())
        print(motor2.angle())

        wait(10)  # Small delay to prevent excessive CPU usage


if __name__ == "__main__":
    main()

#!/usr/bin/env pybricks-micropython

"""
MAIN MODULE

Main entry point for the robotic arm. Initializes the EV3 brick, sensors, and motors. Injects them into the controllers
and starts the main navigation loop.

"""
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port, Button

from constants import RATIOS
from modes.AutomaticMode import AutomaticMode
from modes.ColorCalibrationMode import ColorCalibrationMethod
from modes.ManualMode import ManualMode
from utils.input import get_input

# Execution

ev3 = EV3Brick()

# Main entry point

# Initialize the motors
base_motor = Motor(Port.D)
shoulder_motor = Motor(Port.A)
elbow_motor = Motor(Port.C)
gripper_motor = Motor(Port.B)

# Initialize the sensors
base_touch_sensor = TouchSensor(Port.S4)
color_sensor = ColorSensor(Port.S3)
shoulder_touch_sensor = TouchSensor(Port.S1)

# Now we decide what mode we want the robot to run in
# 1. Manual mode – control each joint individually for testing
# 2. Color calibration mode – the robot will help us calibrate the color sensor
# 3. Automatic mode – the robot will perform the given routine for sorting cubes and building the ordered stack
ev3.screen.print("Select mode:\n\nLEFT: Manual\nRIGHT: Color Calibration\nCENTER: Automatic")
print("[Main] Select mode:\n\nLEFT: Manual\nRIGHT: Color Calibration\nCENTER: Automatic\n")
given_input = get_input(ev3)

# Manual mode
if given_input == Button.LEFT:
    print("[Main] Manual mode engaged")
    manual_mode = ManualMode(ev3, base_motor, shoulder_motor, elbow_motor, gripper_motor, shoulder_touch_sensor,
                             base_touch_sensor,
                             RATIOS)
    manual_mode.run()

# Color calibration mode
elif given_input == Button.RIGHT:
    print("[Main] Color calibration mode engaged")
    color_calibration_mode = ColorCalibrationMethod(ev3, color_sensor)
    color_calibration_mode.run()

# Automatic mode
elif given_input == Button.CENTER:
    print("[Main] Automatic mode engaged")
    automatic_mode = AutomaticMode(ev3, base_motor, shoulder_motor, elbow_motor, gripper_motor, base_touch_sensor,
                                   shoulder_touch_sensor, color_sensor, RATIOS)
    automatic_mode.run()

# Invalid input
else:
    ev3.screen.clear()
    ev3.screen.print("Invalid input. Exiting...")
    print("[Main] Invalid input. Exiting...")
    ev3.speaker.beep(100, 500)

ev3.screen.clear()
ev3.screen.print("Program complete!")
print("[Main] Program complete!")

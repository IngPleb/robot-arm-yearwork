#!/usr/bin/env pybricks-micropython

"""
MAIN MODULE

Main entry point for the robotic arm. Initializes the EV3 brick, sensors, and motors. Injects them into the controllers
and starts the main navigation loop.

"""
from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port

from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.GripperPart import GripperPart
from parts.ShoulderPart import ShoulderPart
from systems.ColorDetectionSystem import ColorDetectionSystem

ev3 = EV3Brick()

# Initialize the motors
base_motor = Motor(Port.D)
shoulder_motor = Motor(Port.A)
elbow_motor = Motor(Port.C)
gripper_motor = Motor(Port.B)

# Initialize the sensors
base_touch_sensor = TouchSensor(Port.S4)
shoulder_sonic_sensor = UltrasonicSensor(Port.S1)
color_sensor = ColorSensor(Port.S3)

# Initialize the parts

# As for the ration… The big gear has 36 teeth but the small gear probably has 12 (or 20 we can check). So the ration is 36/12 = 3
basePart = BasePart(base_motor, base_touch_sensor, 36/12)
shoulderPart = ShoulderPart(shoulder_motor, shoulder_sonic_sensor, 36/12)
elbowPart = ElbowPart(elbow_motor, 36/12)
gripperPart = GripperPart(gripper_motor)

# Calibrate the parts
# The order of calibration is important.
# It may be subject to change in the future.
elbowPart.calibrate()
shoulderPart.calibrate()
basePart.calibrate()

# Systems initialization
color_detection_system = ColorDetectionSystem(color_sensor)
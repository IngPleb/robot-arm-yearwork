from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick

from modes.Mode import Mode
from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.GripperPart import GripperPart
from parts.ShoulderPart import ShoulderPart
from systems.ColorDetectionSystem import ColorDetectionSystem
from systems.MoveSystem import MoveSystem


class AutomaticMode(Mode):
    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor,
                 gripper_motor: Motor, base_touch_sensor: TouchSensor, shoulder_sonic_sensor: UltrasonicSensor,
                 color_sensor: ColorSensor, ratios):
        super().__init__("Automatic")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.gripper_motor = gripper_motor
        self.base_touch_sensor = base_touch_sensor
        self.shoulder_sonic_sensor = shoulder_sonic_sensor
        self.color_sensor = color_sensor
        self.ratios = ratios

    def run(self):
        print("Running Automatic Mode")
        # Initialize the parts
        basePart = BasePart(self.base_motor, self.base_touch_sensor, self.ratios["base"])
        shoulderPart = ShoulderPart(self.shoulder_motor, self.shoulder_sonic_sensor, self.ratios["shoulder"],
                                    length=8)
        elbowPart = ElbowPart(self.elbow_motor, self.ratios["elbow"], length=13.5)
        gripperPart = GripperPart(self.gripper_motor)

        # Calibrate the parts
        # The order of calibration is important.
        # It may be subject to change in the future.
        elbowPart.calibrate()
        shoulderPart.calibrate()
        basePart.calibrate()

        # Systems initialization
        color_detection_system = ColorDetectionSystem(self.color_sensor)
        move_system = MoveSystem(basePart, shoulderPart, elbowPart)

        move_system.move(-13.5, 8, 0)


from pybricks.ev3devices import Motor, UltrasonicSensor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait

from constants import OFFSETS
from modes.Mode import Mode
from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.ShoulderPart import ShoulderPart
from utils.input import get_input
from utils.kinematics import get_coordinates


class ManualMode(Mode):
    min_page = 0
    max_page = 1

    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor,
                 sonic_sensor: UltrasonicSensor, touch_sensor: TouchSensor, ratios):
        super().__init__("Manual")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.speed = 200
        self.base_direction = 1

        # Creating parts for the manual mode
        self.base_part = BasePart(self.base_motor, ratio=ratios["base"], touch_sensor=touch_sensor)
        self.shoulder_part = ShoulderPart(self.shoulder_motor, sonic_sensor=sonic_sensor, ratio=ratios["shoulder"],
                                          length=8)
        self.elbow_part = ElbowPart(self.elbow_motor, ratio=ratios["elbow"], length=13.5)

        self.pages = {
            0: {
                "instructions": "Manual Mode\n\nUP/DOWN: Elbow\nLEFT/RIGHT: Shoulder\nCENTER: Switch page",
                "actions": self.page_0_actions
            },
            1: {
                "instructions": "Manual Mode\n\nLEFT: Base\nRIGHT: Base\nUP: Calibrate\nDOWN: ANGLES\nCENTER: Switch page",
                "actions": self.page_1_actions
            },
            2: {
                "instructions": "Manual Mode\n\nLEFT: Gripper O\nRIGHT: Gripper C\nUP: FWK\nCENTER: Switch page",
                "actions": self.page_2_actions
            }
        }

    def page_0_actions(self, pressed_button):
        if pressed_button == Button.LEFT:
            while Button.LEFT in self.ev3.buttons.pressed():
                self.shoulder_motor.run(-self.speed)
                wait(10)
            self.shoulder_motor.hold()
        elif pressed_button == Button.RIGHT:
            while Button.RIGHT in self.ev3.buttons.pressed():
                self.shoulder_motor.run(self.speed)
                wait(10)
            self.shoulder_motor.hold()
        elif pressed_button == Button.UP:
            while Button.UP in self.ev3.buttons.pressed():
                self.elbow_motor.run(-self.speed)
                wait(10)
            self.elbow_motor.hold()
        elif pressed_button == Button.DOWN:
            while Button.DOWN in self.ev3.buttons.pressed():
                self.elbow_motor.run(self.speed)
                wait(10)
            self.elbow_motor.hold()

    def page_1_actions(self, pressed_button):
        if pressed_button == Button.LEFT:
            while Button.LEFT in self.ev3.buttons.pressed():
                self.base_motor.run(-self.speed)
                wait(10)
            self.base_motor.hold()
        elif pressed_button == Button.RIGHT:
            while Button.RIGHT in self.ev3.buttons.pressed():
                self.base_motor.run(self.speed)
                wait(10)
            self.base_motor.hold()

        # Calibrate the robot
        elif pressed_button == Button.UP:
            self.base_part.calibrate()
            self.elbow_part.calibrate()

            # Safety wait so the motors have time to debounce
            wait(250)
            self.shoulder_part.calibrate()
            # Safety wait so the brick has time to update the list accordingly & motors to debounce
            wait(500)

        # Get part angles
        elif pressed_button == Button.DOWN:
            # Console
            print("Angles:")
            print("Base: " + str(self.base_part.get_angle()))
            print("Shoulder: " + str(self.shoulder_part.get_angle()))
            print("Elbow: " + str(self.elbow_part.get_angle()))
            print("|--------------|")

            # Screen
            self.ev3.screen.clear()
            self.ev3.screen.print("-----\nAngles:\n")
            self.ev3.screen.print("Base:\n" + str(self.base_part.get_angle()))
            self.ev3.screen.print("Shoulder:\n" + str(self.shoulder_part.get_angle()))
            self.ev3.screen.print("Elbow:\n" + str(self.elbow_part.get_angle()))

    def page_2_actions(self, pressed_button):
        if pressed_button == Button.LEFT:
            pass
        elif pressed_button == Button.RIGHT:
            pass
        elif pressed_button == Button.UP:
            x,y = get_coordinates(self.shoulder_part.get_angle() + OFFSETS["shoulder"], self.shoulder_part.length, self.elbow_part.get_angle() + OFFSETS["elbow"], self.elbow_part.length)
            print("X: ", x, "Y: ", y)
            print("|--------------|")
            self.ev3.screen.clear()
            self.ev3.screen.print("X: " + str(x) + "\nY: " + str(y))
            # Safety wait
            wait(500)
        elif pressed_button == Button.DOWN:
            self.shoulder_part.move_to_angle(-55)
            self.elbow_part.move_to_angle(-90)
            wait(350)

    def run(self):
        print("Running Manual Mode")
        self.ev3.screen.clear()
        self.ev3.screen.print(self.pages[0]["instructions"])
        self.ev3.speaker.beep()
        print(self.pages[0]["instructions"])

        current_page = 0

        # Main input loop
        while True:
            pressed_button = get_input(self.ev3)

            # Execute actions for the current page
            self.pages[current_page]["actions"](pressed_button)

            if pressed_button == Button.CENTER:
                current_page = (current_page + 1) % len(self.pages)
                self.ev3.screen.clear()
                self.ev3.screen.print(self.pages[current_page]["instructions"])
                self.ev3.speaker.beep()

                # Safety wait so the brick has time to update the list accordingly
                wait(250)

            # Hold all motors when no buttons pressed
            self.shoulder_motor.hold()
            self.elbow_motor.hold()
            self.base_motor.hold()

            wait(10)  # Small delay to prevent excessive CPU usage

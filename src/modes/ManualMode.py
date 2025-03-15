from pybricks.ev3devices import Motor, UltrasonicSensor, TouchSensor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait

from constants import OFFSETS
from modes.Mode import Mode
from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.GripperPart import GripperPart
from parts.ShoulderPart import ShoulderPart
from systems.MoveSystem import MoveSystem
from utils.input import get_input
from utils.kinematics import get_coordinates


class ManualMode(Mode):
    min_page = 0
    max_page = 1

    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor,
                 gripper_motor: Motor,
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
        self.gripper_part = GripperPart(gripper_motor)

        self.move_system = MoveSystem(self.base_part, self.shoulder_part, self.elbow_part,)

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
                "instructions": "Manual Mode\n\nLEFT: Gripper O\nRIGHT: Gripper C\nUP: FWK\nCENTER: Switch page\nDOWN: Get Raw Angles",
                "actions": self.page_2_actions
            },
            3: {
                "instructions": "Manual Mode\n\nLeft: EXE XY\nRight: EXE Angles\nCenter: Switch page",
                "actions": self.page_3_actions
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
            self.gripper_part.release()
            # Safety wait
            wait(350)
        elif pressed_button == Button.RIGHT:
            self.gripper_part.grab()
            # Safety wait
            wait(350)
        elif pressed_button == Button.UP:
            shoulder_angle = self.shoulder_part.get_angle() + OFFSETS["shoulder"]
            elbow_angle = self.elbow_part.get_angle() + OFFSETS["elbow"]
            shoulder_angle = -shoulder_angle
            x, y = get_coordinates(shoulder_angle, self.shoulder_part.length, elbow_angle, self.elbow_part.length)
            print("X: ", x, "Y: ", y)
            print("Base angle: ", self.base_part.get_angle())
            print("|--------------|")
            self.ev3.screen.clear()
            self.ev3.screen.print("X: " + str(x) + "\nY: " + str(y))
            # Safety wait
            wait(500)
        elif pressed_button == Button.DOWN:
            print("Angles:")
            print("Shoulder: " + str(self.shoulder_part.get_angle()))
            print("Elbow: " + str(self.elbow_part.get_angle()))
            print("Base: " + str(self.base_part.get_angle()))
            print("\nRaw angles:")
            print("Shoulder: " + str(self.shoulder_part.get_raw_angle()))
            print("Elbow: " + str(self.elbow_part.get_raw_angle()))
            print("Base: " + str(self.base_part.get_raw_angle()))
            wait(350)

    def page_3_actions(self, pressed_button):
        if pressed_button == Button.LEFT:
            try:
                with open("XY_instructions.txt", "r") as file:
                    content = file.read().strip()
                    coords = content.split()

                    if len(coords) >= 2:
                        x = float(coords[0])
                        y = float(coords[1])
                        base_angle = 0  # Default base angle

                        # Use additional base angle if provided
                        if len(coords) >= 3:
                            base_angle = float(coords[2])


                        # Execute movement
                        result = self.move_system.move(x, y, base_angle)

                        if result:
                            self.ev3.speaker.beep()
                        else:
                            self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone
                    else:
                        print("Invalid format in XY_instructions.txt")
                        self.ev3.screen.clear()
                        self.ev3.screen.print("Invalid format\nin file")
                        self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone

            except ValueError:
                print("Invalid number format in XY_instructions.txt")
                self.ev3.screen.clear()
                self.ev3.screen.print("Invalid numbers\nin file")
                self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone

            # Safety wait
            wait(500)

        elif pressed_button == Button.RIGHT:
            try:
                with open("angle_instructions.txt", "r") as file:
                    content = file.read().strip()
                    angles = content.split()

                    if len(angles) >= 2:
                        shoulder_angle = float(angles[0])
                        elbow_angle = float(angles[1])
                        base_angle = 0  # Default base angle

                        # Use additional base angle if provided
                        if len(angles) >= 3:
                            base_angle = float(angles[2])

                        # Replace f-string with regular string concatenation and screen print with console print
                        print("Moving to angles:")
                        print("S: " + str(shoulder_angle))
                        print("E: " + str(elbow_angle))
                        print("B: " + str(base_angle))

                        # Execute movement
                        result = self.move_system.move_to_angle(shoulder_angle, elbow_angle, base_angle)

                        if result:
                            self.ev3.speaker.beep()
                        else:
                            self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone
                    else:
                        print("Invalid format in angle_instructions.txt")
                        print("Invalid format in file")
                        self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone

            except ValueError:
                print("Invalid number format in angle_instructions.txt")
                self.ev3.screen.clear()
                self.ev3.screen.print("Invalid numbers\nin file")
                self.ev3.speaker.beep(frequency=200, duration=500)  # Error tone

            # Safety wait
            wait(500)



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

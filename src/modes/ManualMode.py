from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait

from modes.Mode import Mode
from utils.input import get_input


class ManualMode(Mode):
    min_page = 0
    max_page = 1

    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor):
        super().__init__("Manual")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.speed = 200
        self.base_direction = 1

        self.pages = {
            0: {
                "instructions": "Manual Mode\n\nUP/DOWN: Elbow\nLEFT/RIGHT: Shoulder\nCENTER: Switch page",
                "actions": self.page_0_actions
            },
            1: {
                "instructions": "Manual Mode\n\nLEFT: Base\nRIGHT: Base\nCENTER: Switch page",
                "actions": self.page_1_actions
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
                self.elbow_motor.run(self.speed)
                wait(10)
            self.elbow_motor.hold()
        elif pressed_button == Button.DOWN:
            while Button.DOWN in self.ev3.buttons.pressed():
                self.elbow_motor.run(-self.speed)
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
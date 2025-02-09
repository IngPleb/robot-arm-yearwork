from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait

from modes.Mode import Mode


class ManualMode(Mode):
    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor):
        super().__init__("Manual")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.speed = 200
        self.base_direction = 1

    def run(self):
        print("Running Manual Mode")
        self.ev3.screen.clear()
        self.ev3.screen.print("Manual Mode\n\nUP/DOWN: Elbow\nLEFT/RIGHT: Shoulder\nCENTER: Base")
        self.ev3.speaker.beep()
        print("Manual Mode\n\nUP/DOWN: Elbow\nLEFT/RIGHT: Shoulder\nCENTER: Base")

        while True:
            pressed_buttons = self.ev3.buttons.pressed()

            # Handle shoulder movement with LEFT/RIGHT
            if Button.LEFT in pressed_buttons:
                while Button.LEFT in self.ev3.buttons.pressed():
                    self.shoulder_motor.run(-self.speed)
                    wait(10)
                self.shoulder_motor.hold()
            elif Button.RIGHT in pressed_buttons:
                while Button.RIGHT in self.ev3.buttons.pressed():
                    self.shoulder_motor.run(self.speed)
                    wait(10)
                self.shoulder_motor.hold()

            # Handle elbow movement with UP/DOWN
            elif Button.UP in pressed_buttons:
                while Button.UP in self.ev3.buttons.pressed():
                    self.elbow_motor.run(self.speed)
                    wait(10)
                self.elbow_motor.hold()
            elif Button.DOWN in pressed_buttons:
                while Button.DOWN in self.ev3.buttons.pressed():
                    self.elbow_motor.run(-self.speed)
                    wait(10)
                self.elbow_motor.hold()

            # Handle base rotation with CENTER
            elif Button.CENTER in pressed_buttons:
                while Button.CENTER in self.ev3.buttons.pressed():
                    self.base_motor.run(self.speed * self.base_direction)
                    wait(10)
                self.base_direction *= -1  # Switch direction
                self.base_motor.hold()
            else:
                # Hold all motors when no buttons pressed
                self.shoulder_motor.hold()
                self.elbow_motor.hold()
                self.base_motor.hold()

            wait(10)  # Small delay to prevent excessive CPU usage

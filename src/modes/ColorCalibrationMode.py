from pybricks.ev3devices import ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

from modes.Mode import Mode
from systems.ColorDetectionSystem import ColorDetectionSystem


class ColorCalibrationMethod(Mode):
    def __init__(self, ev3: EV3Brick, color_sensor: ColorSensor):
        super().__init__("Color Calibration")
        self.ev3 = ev3
        self.color_sensor = color_sensor

    def run(self):
        print("Running Color Calibration Mode")
        self.ev3.screen.clear()
        self.ev3.screen.print("Press any\n button to\n exit")

        # We will use this to compare our results against the default settings
        color_detection_system = ColorDetectionSystem(self.color_sensor)

        # Safety wait so the brick has time to update the list accordingly
        wait(1000)
        while True:
            if self.ev3.buttons.pressed():
                break

            print("Currently measured color: ", self.color_sensor.rgb())
            print("Currently detected color: ", color_detection_system.detect_color())
            print("|----------|")
            wait(250)

        return True
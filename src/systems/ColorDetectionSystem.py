from pybricks.ev3devices import ColorSensor


class ColorDetectionSystem:
    
    # The colors are really messed up coming from the sensor. It is basically guessing between yellow and red
    COLORS = {
        "yellow": (14, 9, 0),
        "red": (22, 0, 0),
        "blue": (0, 0, 30),
        "green": (2, 8, 3),
    }

    def __init__(self, color_sensor: ColorSensor):
        print("Initializing ColorDetectionSystem")
        self.color_sensor = color_sensor

    def detect_color(self) -> str:
        color = self.color_sensor.rgb()
        return self.get_closest_color(color)


    def get_closest_color(self, color: tuple) -> str:
        closest_color = None
        closest_distance = float("inf")
        for known_color, known_rgb in self.COLORS.items():
            distance = sum((color[i] - known_rgb[i]) ** 2 for i in range(3))
            if distance < closest_distance:
                closest_color = known_color
                closest_distance = distance
        return closest_color
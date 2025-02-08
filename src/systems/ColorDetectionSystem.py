from pybricks.ev3devices import ColorSensor


class ColorDetectionSystem:
    COLORS = {
        "yellow": (0, 100, 100),
        "red": (255, 0, 0),
        "blue": (255, 255, 0),
        "green": (0, 170, 0),
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
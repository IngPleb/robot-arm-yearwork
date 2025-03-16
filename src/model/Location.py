class Location:
    def __init__(self, x: float = None, y: float = None, base_angle: float = None, elbow_angle: float = None, shoulder_angle: float = None):
        self.x = x
        self.y = y
        self.base_angle = base_angle
        self.elbow_angle = elbow_angle
        self.shoulder_angle = shoulder_angle

    def is_cartesian(self):
        return self.x is not None and self.y is not None

    def get_angles(self):
        return self.shoulder_angle, self.elbow_angle, self.base_angle

    def get_cartesian(self):
        return self.x, self.y, self.base_angle

    def set_base_angle(self, base_angle: float):
        if self.is_cartesian():
            return Location(self.x, self.y, base_angle)
        else:
            return Location(elbow_angle=self.elbow_angle, shoulder_angle=self.shoulder_angle, base_angle=base_angle)

    def __str__(self):
        if self.is_cartesian():
            return "Location(x=" + str(self.x) + ", y=" + str(self.y) + ", base_angle=" + str(self.base_angle) + ")"
        else:
            return "Location(shoulder_angle=" + str(self.shoulder_angle) + ", elbow_angle=" + str(self.elbow_angle) + ", base_angle=" + str(self.base_angle) + ")"
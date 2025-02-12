class ArmPart:
    def __init__(self, name, motor, ratio=1):
        self.name = name
        self.motor = motor
        self.ratio = ratio
        self.motor.hold()
        print("ArmPart created: " + name)

    def __str__(self):
        return 'ArmPart: ' + self.name

    def move_motor_to_angle(self, angle):
        self.motor.run_target(100, angle * self.ratio)
        self.motor.hold()
        print("{} moved to angle: {}".format(self.name, angle))
        return True

    def get_angle(self):
        return self.motor.angle() / self.ratio

    def calibrate(self):
        raise NotImplementedError()

    def move_to_angle(self, angle):
        return self.move_motor_to_angle(angle)

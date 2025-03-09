from pybricks.ev3devices import Motor


class ArmPart:
    def __init__(self, name, motor: Motor, ratio=1):
        self.name = name
        self.motor = motor
        self.ratio = ratio
        self.motor.hold()
        print("[ArmPart] created: " + name)

    def __str__(self):
        return 'ArmPart: ' + self.name

    def move_motor_to_angle(self, angle, speed=100, wait=True):
        self.motor.run_target(speed, angle * self.ratio, wait=wait)
        print("[{}] moved to angle: {}".format(self.name, angle))
        return True

    def get_angle(self):
        return self.motor.angle() / self.ratio

    def calibrate(self):
        raise NotImplementedError()

    def move_to_angle(self, angle, speed=100, wait=True):
        return self.move_motor_to_angle(angle, speed, wait)

    def is_done(self):
        return self.motor.control.done()
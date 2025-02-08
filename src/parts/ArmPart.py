class ArmPart:
    def __init__(self, name):
        self.name = name
        print("ArmPart created: " + name)

    def __str__(self):
        return 'ArmPart: ' + self.name

    def calibrate(self):
        raise NotImplementedError()
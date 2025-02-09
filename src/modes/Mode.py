class Mode:
    def __init__(self, name):
        print("Initializing Mode " + name)
        self.name = name

    def run(self):
        raise NotImplementedError("run method not implemented")
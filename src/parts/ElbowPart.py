from pybricks.ev3devices import Motor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class ElbowPart(ArmPart):
    def __init__(self, motor: Motor, ratio: float, length: float):
        super().__init__('Elbow')
        self.motor = motor
        self.ratio = ratio
        self.length = length
        self.motor.hold()

    def calibrate(self):
        # Calibration parameters
        SPEED = 400
        ANGLE_THRESHOLD = 6
        TARGET_TICKS = 25
        TENSION_ANGLE = -400

        tick_count = 0
        last_angle = self.motor.angle()

        while tick_count < TARGET_TICKS:
            self.motor.run(SPEED)
            wait(10)
            
            current_angle = self.motor.angle()
            angle_difference = abs(current_angle - last_angle)
            
            if angle_difference < ANGLE_THRESHOLD:
                tick_count += 1
            else:
                tick_count = 0
                
            last_angle = current_angle

        self.motor.hold()

        # Remove tension from the motor
        self.motor.run_angle(SPEED, TENSION_ANGLE)
        
        # Reset angle to 0
        self.motor.reset_angle(0)
        
        print("Calibration of " + self.name + " complete")
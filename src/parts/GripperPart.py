import time

from pybricks.ev3devices import Motor
from pybricks.tools import wait

from parts.ArmPart import ArmPart


class GripperPart(ArmPart):
    def __init__(self, motor: Motor):
        super().__init__("Gripper", motor)
        self.motor = motor

    def grab(self):
        self.motor.run_time(400, 750)
        self.motor.hold()
        print("[Gripper] grabbed")
        return True

    def release(self):

        target_angle = -97
        timeout_seconds = 3  # Set a reasonable timeout
        start_time = time.time()
        speed = 400

        # Start the motor moving toward the target
        direction = -speed if self.motor.angle() > target_angle else speed
        self.motor.run(direction)

        # Wait until the motor reaches the target or timeout occurs
        while True:
            current_angle = self.motor.angle()
            angle_diff = abs(current_angle - target_angle)

            if angle_diff <= 5:  # 5 degrees tolerance
                print("[Gripper] Target reached: {}".format(current_angle))
                break

            if time.time() - start_time > timeout_seconds:
                print("[Gripper] Warning: Release timed out after {} seconds, diff: {}".format(timeout_seconds,
                                                                                               angle_diff))
                break

            wait(10)  # Check every 10ms

        # Make sure to hold the motor regardless of how the loop exited
        self.motor.hold()
        print("[Gripper] finished running target")
        print("[Gripper] released")
        return True

    def open(self):
        return self.release()

    def calibrate(self):
        # Calibration parameters
        SPEED = 400
        ANGLE_THRESHOLD = 6  # Minimum angle change to detect stalling
        TARGET_TICKS = 10  # Number of consecutive readings with minimal movement
        TENSION_ANGLE = -2  # Small reverse to release tension

        tick_count = 0
        last_angle = self.motor.angle()

        while tick_count < TARGET_TICKS:
            self.motor.run(SPEED)  # Run in the grab direction
            wait(10)

            current_angle = self.motor.angle()
            angle_difference = abs(current_angle - last_angle)

            print("[Gripper] Current angle: {}, Difference: {}".format(current_angle, angle_difference))

            if angle_difference < ANGLE_THRESHOLD:
                tick_count += 1
                print("[Gripper] Stall detected: {} of {}".format(tick_count, TARGET_TICKS))
            else:
                tick_count = 0

            last_angle = current_angle

        self.motor.hold()

        # Wait for the motor to debounce
        wait(250)

        # Reset angle to 0
        self.motor.reset_angle(0)
        self.motor.hold()

        print("[Gripper] calibrated")
        return True

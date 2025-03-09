# Wait for both movements to complete
from pybricks.tools import wait

from constants import OFFSETS
from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.ShoulderPart import ShoulderPart
from utils.kinematics import calculate_angles


class MoveSystem:
    def __init__(self, base_part: BasePart, shoulder_part: ShoulderPart, elbow_part: ElbowPart,
                 shoulder_offset: float = OFFSETS["shoulder"], elbow_offset: float = OFFSETS["elbow"]):
        self.base_part = base_part
        self.shoulder_part = shoulder_part
        self.elbow_part = elbow_part
        self.shoulder_offset = shoulder_offset  # Offset for shoulder calibration
        self.elbow_offset = elbow_offset  # Offset for elbow calibration

    def move(self, x: float, y: float, base_angle: float, speed=100) -> bool:
        # Calculate the angles
        try:
            shoulder_angle, elbow_angle = calculate_angles(x, y, self.shoulder_part.length, self.elbow_part.length)
        except ValueError as e:
            print("[Move System] Error -", str(e))
            return False  # Target is unreachable

        print("[Move System] Calculated angles: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°")

        # Apply offsets
        shoulder_angle -= self.shoulder_offset
        elbow_angle -= self.elbow_offset
        shoulder_angle = -shoulder_angle

        print("[Move System] Applying offsets: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°")
        print("[Move System] Moving to x =", x, ", y =", y, ", base_angle =", base_angle)

        # Start shoulder and elbow movements (non-blocking)
        self.shoulder_part.move_to_angle(shoulder_angle, speed=speed, wait=False)
        self.elbow_part.move_to_angle(elbow_angle, speed=speed, wait=False)

        # Wait for both movements to complete
        while not (self.shoulder_part.is_done() and self.elbow_part.is_done()):
            wait(10)  # Small delay to prevent excessive CPU usage

        # Hold motors in position
        self.shoulder_part.motor.hold()
        self.elbow_part.motor.hold()

        print("[Move System] Shoulder and elbow movements completed")

        # Now move the base
        self.base_part.move_to_angle(base_angle)

        print("[Move System] Movement completed")
        return True

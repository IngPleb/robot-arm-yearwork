# Wait for both movements to complete
from pybricks.tools import wait

from constants import OFFSETS
from model.Location import Location
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

    def move(self, x: float, y: float, base_angle: float, speed: int =100, move_sequentially: bool = False) -> bool:
        # Calculate the angles
        try:
            shoulder_angle, elbow_angle = calculate_angles(x, y, self.shoulder_part.length, self.elbow_part.length)
        except ValueError as e:
            print("[Move System] Error -", str(e))
            return False  # Target is unreachable

        print("[Move System] Calculated angles: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°")

        shoulder_angle -= self.shoulder_offset
            
        elbow_angle -= self.elbow_offset
        shoulder_angle = -shoulder_angle

        print("[Move System] Applying offsets: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°")
        print("[Move System] Moving to x =", x, ", y =", y, ", base_angle =", base_angle)

        return self.move_to_angle(shoulder_angle, elbow_angle, base_angle, speed, move_sequentially)

    def move_to_angle(self, shoulder_angle: float, elbow_angle: float, base_angle: float, speed: int = 100, move_sequentially: bool = False) -> bool:
        # Offsets are not considered here

        print("[Move System] Moving to angles: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°, base=", base_angle)

        # Move the shoulder and elbow (non-blocking)
        self.shoulder_part.move_to_angle(shoulder_angle, speed=speed, wait=move_sequentially)
        self.elbow_part.move_to_angle(elbow_angle, speed=speed, wait=move_sequentially)

        # Wait for both movements to complete
        while not (self.shoulder_part.is_done() and self.elbow_part.is_done()):
            wait(10)

        # Hold motors in position
        self.shoulder_part.motor.hold()
        self.elbow_part.motor.hold()

        # Move the base first
        self.base_part.move_to_angle(base_angle)

        print("[Move System] Movement to angles completed")
        return True

    def move_to_location(self, location: Location, speed: int = 100, move_sequentially: bool = False):
        if location.is_cartesian():
            return self.move(location.x, location.y, location.base_angle, speed=speed, move_sequentially=move_sequentially)
        else:
            return self.move_to_angle(*location.get_angles(), move_sequentially=move_sequentially)

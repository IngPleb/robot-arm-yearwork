from math import acos, atan2, degrees, sqrt

from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.ShoulderPart import ShoulderPart


class MoveSystem:
    def __init__(self, base_part: BasePart, shoulder_part: ShoulderPart, elbow_part: ElbowPart,
                 shoulder_offset: float = 61, elbow_offset: float = 91):
        self.base_part = base_part
        self.shoulder_part = shoulder_part
        self.elbow_part = elbow_part
        self.shoulder_offset = shoulder_offset  # Offset for shoulder calibration
        self.elbow_offset = elbow_offset  # Offset for elbow calibration

    def move(self, x: float, y: float, base_angle: float) -> bool:
        # Calculate the angles
        try:
            shoulder_angle, elbow_angle = self.calculate_angles(x, y, self.shoulder_part.length, self.elbow_part.length)
        except ValueError as e:
            print("Move System: Error -", str(e))
            return False  # Target is unreachable

        print(shoulder_angle, elbow_angle)

        # Apply offsets
        shoulder_angle += self.shoulder_offset
        elbow_angle += self.elbow_offset

        print("Move System: Calculated angles: shoulder=", shoulder_angle, "°, elbow=", elbow_angle, "°")
        print("Move System: Moving to x =", x, ", y =", y, ", base_angle =", base_angle)

        # Move the parts
        self.shoulder_part.move_to_angle(-shoulder_angle)
        self.elbow_part.move_to_angle(-elbow_angle)
        self.base_part.move_to_angle(base_angle)

        print("Move System: Movement completed")
        return True

    def calculate_angles(self, x, y, shoulder_length, elbow_length):
        d = (x ** 2 + y ** 2) ** 0.5

        if d > (shoulder_length + elbow_length) or d < abs(shoulder_length - elbow_length):
            raise ValueError("Target out of reach")

        cos_elbow = (shoulder_length ** 2 + elbow_length ** 2 - d ** 2) / (2 * shoulder_length * elbow_length)
        cos_elbow = max(min(cos_elbow, 1), -1)
        elbow_angle = acos(cos_elbow)

        # Shoulder angle
        sin_elbow = sqrt(1 - cos_elbow ** 2)
        phi = atan2(y, x)
        psi = atan2(elbow_length * sin_elbow, shoulder_length + elbow_length * cos_elbow)
        shoulder_angle = phi - psi

        # Convert from radians to degrees if needed
        shoulder_deg = degrees(shoulder_angle)
        elbow_deg = degrees(elbow_angle)

        return (shoulder_deg, elbow_deg)

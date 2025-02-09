from math import acos, atan2, degrees, sqrt

from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.ShoulderPart import ShoulderPart


class MoveSystem():
    def __init__(self, base_part: BasePart, shoulder_part: ShoulderPart, elbow_part: ElbowPart):
        self.base_part = base_part
        self.shoulder_part = shoulder_part
        self.elbow_part = elbow_part

    def move(self, x, y, base_angle):
        # Calculate the angles
        shoulder_angle, elbow_angle = self.calculate_angles(x, y, self.shoulder_part.length, self.elbow_part.length)

        # Move the parts
        self.shoulder_part.move_to_angle(shoulder_angle)
        self.elbow_part.move_to_angle(elbow_angle)
        self.base_part.move_to_angle(base_angle)

        return True

    def calculate_angles(self, x, y, shoulder_length: float, elbow_length: float):
        # Link lengths
        L1 = shoulder_length
        L2 = elbow_length

        # Compute intermediate values
        d = (x ** 2 + y ** 2) ** 0.5
        cos_elbow = (L1 ** 2 + L2 ** 2 - d ** 2) / (2 * L1 * L2)
        elbow_angle = acos(cos_elbow)

        # Shoulder angle
        sin_elbow = sqrt(1 - cos_elbow ** 2)
        phi = atan2(y, x)
        psi = atan2(L2 * sin_elbow, L1 + L2 * cos_elbow)
        shoulder_angle = phi - psi

        # Convert from radians to degrees (hopefully the motors will accept this xD)
        shoulder_deg = degrees(shoulder_angle)
        elbow_deg = degrees(elbow_angle)

        return shoulder_deg, elbow_deg

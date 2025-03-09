from math import acos, sqrt, atan2, degrees

import math


def get_coordinates(shoulder_angle: float, shoulder_length: float, elbow_angle: float, elbow_length: float):
    # Convert angles to radians
    shoulder_rad = math.radians(shoulder_angle)
    elbow_rad = math.radians(elbow_angle)
    # For relative angles: the elbow's global angle is the sum of the shoulder and elbow angles.
    x = shoulder_length * math.cos(shoulder_rad) + elbow_length * math.cos(shoulder_rad + elbow_rad)
    y = shoulder_length * math.sin(shoulder_rad) + elbow_length * math.sin(shoulder_rad + elbow_rad)
    return x, y

def calculate_angles(x, y, l1, l2):
    """
    Computes the joint angles for a 2-link planar robotic arm.

    Parameters:
        x (float): x-coordinate of the target point.
        y (float): y-coordinate of the target point.
        l1 (float): Length of the first link (shoulder segment).
        l2 (float): Length of the second link (elbow segment).

    Returns:
        tuple: A tuple containing two solutions in degrees:
            ((shoulder_angle_solution1, elbow_angle_solution1),
             (shoulder_angle_solution2, elbow_angle_solution2))
        Angles are in degrees.

    Raises:
        ValueError: If the target point is unreachable with the given link lengths.
    """
    # Calculate the distance from the origin to the target point.
    distance = math.sqrt(x ** 2 + y ** 2)

    # Check if the target is reachable.
    if distance > (l1 + l2) or distance < abs(l1 - l2):
        raise ValueError("The target point is unreachable with the given link lengths.")

    # Compute the cosine of the elbow angle using the cosine law.
    cos_angle2 = (x ** 2 + y ** 2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)
    # Clamp the value to avoid numerical issues.
    cos_angle2 = max(min(cos_angle2, 1), -1)

    # Calculate the two possible elbow angles.
    theta2_elbow_up = math.acos(cos_angle2)  # Elbow up configuration.
    theta2_elbow_down = -theta2_elbow_up  # Elbow down configuration.

    # Helper function to compute the shoulder angle given an elbow angle.
    def compute_theta1(theta2):
        k1 = l1 + l2 * math.cos(theta2)
        k2 = l2 * math.sin(theta2)
        return math.atan2(y, x) - math.atan2(k2, k1)

    # Compute the shoulder angles for both configurations.
    theta1_elbow_up = compute_theta1(theta2_elbow_up)
    theta1_elbow_down = compute_theta1(theta2_elbow_down)

    # Convert angles from radians to degrees.
    shoulder_deg_up = math.degrees(theta1_elbow_up)
    elbow_deg_up = math.degrees(theta2_elbow_up)
    
    # This is the second configuration in which we are not interested.
    shoulder_deg_down = math.degrees(theta1_elbow_down)
    elbow_deg_down = math.degrees(theta2_elbow_down)

    # Return both configurations in degrees.
    return shoulder_deg_up, elbow_deg_up

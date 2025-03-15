import math
import tkinter as tk
from tkinter import messagebox


# Kinematics functions
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
        tuple: (shoulder_angle, elbow_angle) in degrees for the "elbow up" configuration.

    Raises:
        ValueError: If the target point is unreachable.
    """
    distance = math.sqrt(x ** 2 + y ** 2)
    if distance > (l1 + l2) or distance < abs(l1 - l2):
        raise ValueError("The target point is unreachable with the given link lengths.")

    cos_angle2 = (x ** 2 + y ** 2 - l1 ** 2 - l2 ** 2) / (2 * l1 * l2)
    cos_angle2 = max(min(cos_angle2, 1), -1)
    theta2 = math.acos(cos_angle2)  # Elbow up configuration

    # Helper function to compute the shoulder angle
    def compute_theta1(theta2):
        k1 = l1 + l2 * math.cos(theta2)
        k2 = l2 * math.sin(theta2)
        return math.atan2(y, x) - math.atan2(k2, k1)

    theta1 = compute_theta1(theta2)
    shoulder_deg = math.degrees(theta1)
    elbow_deg = math.degrees(theta2)
    return shoulder_deg, elbow_deg


# GUI Application
class RoboticArmSimulator:
    def __init__(self, master):
        self.master = master
        master.title("Robotic Arm Simulator")

        # Arm lengths
        self.shoulder_length = 8.0
        self.elbow_length = 13.6

        # Create input frame
        self.input_frame = tk.Frame(master)
        self.input_frame.pack(pady=10)

        tk.Label(self.input_frame, text="Target X:").grid(row=0, column=0, padx=5)
        self.x_entry = tk.Entry(self.input_frame, width=10)
        self.x_entry.grid(row=0, column=1, padx=5)
        self.x_entry.insert(0, "10")  # default value

        tk.Label(self.input_frame, text="Target Y:").grid(row=0, column=2, padx=5)
        self.y_entry = tk.Entry(self.input_frame, width=10)
        self.y_entry.grid(row=0, column=3, padx=5)
        self.y_entry.insert(0, "10")  # default value

        self.draw_button = tk.Button(self.input_frame, text="Redraw", command=self.redraw)
        self.draw_button.grid(row=0, column=4, padx=10)

        # Canvas for drawing the arm
        self.canvas_width = 600
        self.canvas_height = 600
        self.canvas = tk.Canvas(master, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)

        # Set origin in the middle of the canvas
        self.origin_x = self.canvas_width // 2
        self.origin_y = self.canvas_height // 2

        # Scale factor (pixels per unit)
        self.scale = 20

        # Draw initial arm position
        self.redraw()

    def transform(self, x, y):
        """Convert Cartesian coordinates to canvas coordinates."""
        canvas_x = self.origin_x + x * self.scale
        canvas_y = self.origin_y - y * self.scale  # invert y for canvas coordinates
        return canvas_x, canvas_y

    def redraw(self):
        # Clear canvas
        self.canvas.delete("all")

        # Get target coordinates from user
        try:
            x_target = float(self.x_entry.get())
            y_target = float(self.y_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric coordinates.")
            return

        try:
            shoulder_angle, elbow_angle = calculate_angles(x_target, y_target, self.shoulder_length, self.elbow_length)
        except ValueError as e:
            messagebox.showerror("Unreachable Target", str(e))
            return

        # Calculate elbow joint coordinates (first link end)
        shoulder_rad = math.radians(shoulder_angle)
        elbow_x = self.shoulder_length * math.cos(shoulder_rad)
        elbow_y = self.shoulder_length * math.sin(shoulder_rad)

        # Calculate end effector coordinates using provided function
        end_x, end_y = get_coordinates(shoulder_angle, self.shoulder_length, elbow_angle, self.elbow_length)

        # Transform to canvas coordinates
        origin_canvas = self.transform(0, 0)
        elbow_canvas = self.transform(elbow_x, elbow_y)
        end_canvas = self.transform(end_x, end_y)
        target_canvas = self.transform(x_target, y_target)

        # Draw base as a circle
        r = 5
        self.canvas.create_oval(origin_canvas[0] - r, origin_canvas[1] - r, origin_canvas[0] + r, origin_canvas[1] + r,
                                fill="black")

        # Draw first link (shoulder to elbow)
        self.canvas.create_line(origin_canvas[0], origin_canvas[1], elbow_canvas[0], elbow_canvas[1], width=4,
                                fill="blue")

        # Draw second link (elbow to end effector)
        self.canvas.create_line(elbow_canvas[0], elbow_canvas[1], end_canvas[0], end_canvas[1], width=4, fill="red")

        # Draw joints
        self.canvas.create_oval(elbow_canvas[0] - r, elbow_canvas[1] - r, elbow_canvas[0] + r, elbow_canvas[1] + r,
                                fill="black")
        self.canvas.create_oval(end_canvas[0] - r, end_canvas[1] - r, end_canvas[0] + r, end_canvas[1] + r,
                                fill="green")

        # Draw target point for visual reference
        self.canvas.create_oval(target_canvas[0] - r, target_canvas[1] - r, target_canvas[0] + r, target_canvas[1] + r,
                                outline="purple", width=2)

        # Display current angles as text on the canvas
        info_text = f"Shoulder angle: {shoulder_angle:.2f}°\nElbow angle: {elbow_angle:.2f}°"
        self.canvas.create_text(100, 20, text=info_text, fill="black", anchor="nw")


if __name__ == '__main__':
    root = tk.Tk()
    app = RoboticArmSimulator(root)
    root.mainloop()
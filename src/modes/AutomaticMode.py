from pybricks.ev3devices import Motor, TouchSensor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

from modes.Mode import Mode
from parts.BasePart import BasePart
from parts.ElbowPart import ElbowPart
from parts.GripperPart import GripperPart
from parts.ShoulderPart import ShoulderPart
from systems.ColorDetectionSystem import ColorDetectionSystem
from systems.MoveSystem import MoveSystem

# Cube handling parameters
CUBE_SEQUENCE = ["red", "blue", "green", "yellow"]  # Target stacking order

# Pickup parameters (main cube bin)
PICKUP_POSITION = (-15, 5, 0)       # Base position above the cube stack (x, y, base_angle)
PICKUP_DROP_INITIAL = 2             # Initial downward drop to pick up the first cube
PICKUP_DROP_INCREMENT = 2           # Additional drop for each subsequent cube

# Two-phase color detection parameters
SAFE_HEIGHT_OFFSET = 5              # How much to raise after pickup for clearance
COLOR_CHECK_ROTATION = 45           # Phase 1: Base rotation angle for initial color check
COLOR_CHECK_POSITION = (-15, 7, 45)  # Phase 2: Final color check position (x, y, base_angle)

# Stacking parameters
STACK_BASE_POSITION = (-15, 10, 0)   # Base stacking position
STACK_VERTICAL_INCREMENT = 2         # Additional vertical offset for each cube in the tower

# Storage bins (three bins) now keep a list of cubes (colors) that are stored.
STORAGE_BINS = {
    "A": {"pos": (-20, 5, 0), "cubes": []},
    "B": {"pos": (-20, 7, 0), "cubes": []},
    "C": {"pos": (-20, 9, 0), "cubes": []}
}


class AutomaticMode(Mode):
    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor,
                 gripper_motor: Motor, base_touch_sensor: TouchSensor, shoulder_sonic_sensor: UltrasonicSensor,
                 color_sensor: ColorSensor, ratios):
        super().__init__("Automatic")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.gripper_motor = gripper_motor
        self.base_touch_sensor = base_touch_sensor
        self.shoulder_sonic_sensor = shoulder_sonic_sensor
        self.color_sensor = color_sensor
        self.ratios = ratios

        # Tower and sequence
        self.cube_sequence = CUBE_SEQUENCE
        self.current_tower = []  # Cubes correctly stacked (by color)

        # Storage bins
        self.storage_bins = STORAGE_BINS

        # Main bin pickup tracking: count of cubes picked so far (to lower the pickup position)
        self.pickup_position = PICKUP_POSITION
        self.cube_pickup_count = 0

        # Base stacking position
        self.stack_base_position = STACK_BASE_POSITION

    def has_cube_in_storage(self, target_color: str) -> bool:
        """Check if any storage bin contains a cube of the target color."""
        for bin_data in self.storage_bins.values():
            if target_color in bin_data["cubes"]:
                return True
        return False

    def retrieve_cube_from_storage(self, target_color: str, move_system, gripper_part) -> bool:
        """
        Retrieve a cube of the target_color from one of the storage bins.
        The cube is then delivered to the stacking area.
        """
        bin_key = None
        for key, bin_data in self.storage_bins.items():
            if target_color in bin_data["cubes"]:
                bin_key = key
                # Remove one occurrence of the target cube from the bin.
                bin_data["cubes"].remove(target_color)
                break

        if bin_key is None:
            print("AutomaticMode: No cube of", target_color, "found in storage.")
            return False

        storage_pos = self.storage_bins[bin_key]["pos"]
        print("AutomaticMode: Retrieving cube of color " + target_color + " from storage bin " + bin_key + " at " + str(storage_pos))

        # Move to the storage bin pickup position.
        if not move_system.move(*storage_pos):
            print("AutomaticMode: Error - Cannot reach storage bin pickup position.")
            return False

        # Grab the cube from storage.
        gripper_part.grab()
        print("AutomaticMode: Cube retrieved from storage.")

        # Move to safe height.
        safe_position = (storage_pos[0], storage_pos[1] + SAFE_HEIGHT_OFFSET, storage_pos[2])
        if not move_system.move(*safe_position):
            print("AutomaticMode: Error - Cannot reach safe height from storage bin.")
            return False

        # Deliver to stack.
        destination = self.compute_dynamic_stack_position()
        delivery_safe = (destination[0], destination[1] + SAFE_HEIGHT_OFFSET, destination[2])
        if not move_system.move(*delivery_safe):
            print("AutomaticMode: Error - Cannot reach safe delivery position for stacking.")
            return False

        if not move_system.move(*destination):
            print("AutomaticMode: Error - Cannot reach final stacking destination.")
            return False

        gripper_part.release()
        print("AutomaticMode: Retrieved cube delivered to stack.")
        return True

    def compute_effective_pickup_position(self):
        """
        Compute the current pickup position from the main bin by lowering the y-coordinate
        based on how many cubes have been picked.
        """
        pickup_x, pickup_y, base_angle = self.pickup_position
        offset = PICKUP_DROP_INITIAL + self.cube_pickup_count * PICKUP_DROP_INCREMENT
        return (pickup_x, pickup_y - offset, base_angle)

    def compute_dynamic_stack_position(self):
        """
        Compute the stacking position based on the current tower height.
        """
        base_x, base_y, base_angle = self.stack_base_position
        dynamic_y = base_y + len(self.current_tower) * STACK_VERTICAL_INCREMENT
        return (base_x, dynamic_y, base_angle)

    def handle_cube_from_main_bin(self, move_system, gripper_part, color_detection_system) -> bool:
        """
        Process a new cube from the main bin: pick it up, do two-phase color detection,
        then either deliver it to the stack (if it matches the expected color)
        or deposit it in a storage bin.
        """
        # === Pickup Phase ===
        effective_pickup = self.compute_effective_pickup_position()
        print("AutomaticMode: Moving to effective pickup position:", effective_pickup)
        if not move_system.move(*effective_pickup):
            print("AutomaticMode: Error - Cannot reach pickup position.")
            return False

        gripper_part.grab()
        print("AutomaticMode: Cube grabbed from main bin.")

        # Move upward to safe height.
        pickup_x, pickup_y, pickup_base_angle = effective_pickup
        safe_position = (pickup_x, pickup_y + SAFE_HEIGHT_OFFSET, pickup_base_angle)
        print("AutomaticMode: Moving to safe height:", safe_position)
        if not move_system.move(*safe_position):
            print("AutomaticMode: Error - Cannot reach safe height position.")
            return False

        # === Two-Phase Color Detection ===
        # Phase 1: Adjust base rotation while keeping (x, y) fixed.
        phase1_position = (safe_position[0], safe_position[1], COLOR_CHECK_ROTATION)
        print("AutomaticMode: Phase 1 - Adjusting base rotation for color check:", phase1_position)
        if not move_system.move(*phase1_position):
            print("AutomaticMode: Error - Cannot adjust base for color detection.")
            return False

        wait(250)  # Stabilization delay

        # Phase 2: Move to final color check position.
        print("AutomaticMode: Phase 2 - Moving to final color check position:", COLOR_CHECK_POSITION)
        if not move_system.move(*COLOR_CHECK_POSITION):
            print("AutomaticMode: Error - Cannot reach final color check position.")
            return False

        detected_color = color_detection_system.detect_color()
        print("AutomaticMode: Detected cube color:", detected_color)

        # === Decision & Delivery Phase ===
        expected_color = (self.cube_sequence[len(self.current_tower)]
                          if len(self.current_tower) < len(self.cube_sequence) else None)
        if detected_color == expected_color:
            # Correct cube: deliver to stacking area.
            destination = self.compute_dynamic_stack_position()
            self.current_tower.append(detected_color)
            print("AutomaticMode: Cube matches expected color. Stacking at:", destination)
        else:
            # Incorrect cube: deposit it into a storage bin.
            # Select the storage bin with the fewest cubes.
            bin_key = min(self.storage_bins, key=lambda k: len(self.storage_bins[k]["cubes"]))
            destination = self.storage_bins[bin_key]["pos"]
            self.storage_bins[bin_key]["cubes"].append(detected_color)
            print("AutomaticMode: Cube does not match expected color. Storing in bin", bin_key, "at:", destination)

        # Two-phase delivery: move upward first, then to destination.
        delivery_safe = (destination[0], destination[1] + SAFE_HEIGHT_OFFSET, destination[2])
        print("AutomaticMode: Moving upward to safe delivery position:", delivery_safe)
        if not move_system.move(*delivery_safe):
            print("AutomaticMode: Error - Cannot reach safe delivery position.")
            return False

        print("AutomaticMode: Moving to final delivery destination:", destination)
        if not move_system.move(*destination):
            print("AutomaticMode: Error - Cannot reach delivery destination.")
            return False

        gripper_part.release()
        print("AutomaticMode: Cube released at destination.")

        # Increment pickup counter for next main-bin cube.
        self.cube_pickup_count += 1
        return True

    def run(self):
        print("Running Automatic Mode with full tower completion logic...")
        # Initialize parts with typical Python naming.
        base_part = BasePart(self.base_motor, self.base_touch_sensor, self.ratios["base"])
        shoulder_part = ShoulderPart(self.shoulder_motor, self.shoulder_sonic_sensor, self.ratios["shoulder"], length=9.6)
        elbow_part = ElbowPart(self.elbow_motor, self.ratios["elbow"], length=13.5)
        gripper_part = GripperPart(self.gripper_motor)

        # Calibrate parts.
        elbow_part.calibrate()
        shoulder_part.calibrate()
        base_part.calibrate()
        gripper_part.calibrate()

        # Initialize supporting systems.
        color_detection_system = ColorDetectionSystem(self.color_sensor)
        move_system = MoveSystem(base_part, shoulder_part, elbow_part)

        # Main loop: always aim to complete the full tower.
        while len(self.current_tower) < len(self.cube_sequence):
            next_expected = self.cube_sequence[len(self.current_tower)]
            print("\nAutomaticMode: Next expected cube color:", next_expected)
            # First, check if the needed cube is already stored.
            if self.has_cube_in_storage(next_expected):
                print("AutomaticMode: Found stored cube matching", next_expected, ". Initiating retrieval.")
                if not self.retrieve_cube_from_storage(next_expected, move_system, gripper_part):
                    print("AutomaticMode: Error retrieving cube from storage. Retrying...")
                    wait(500)
                    continue
            else:
                # If not, process a new cube from the main bin.
                if not self.handle_cube_from_main_bin(move_system, gripper_part, color_detection_system):
                    print("AutomaticMode: Error handling new cube. Retrying...")
                    wait(500)
                    continue
            wait(500)  # Optional delay between cycles

        print("AutomaticMode: Tower complete! Final tower:", self.current_tower)
        return True
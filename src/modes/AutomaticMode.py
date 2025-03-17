from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

from model.Location import Location
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
PRE_PICKUP_POSITION = Location(x=-3.9, y=17.2,
                               base_angle=-185.25)  # Base position above the cube stack (x, y, base_angle)

# Each cube will get a pickup position because the arm is inaccurate as fuck
PICKUP_POSITIONS = [
    Location(shoulder_angle=-53.12, elbow_angle=-70.6, base_angle=-185.25),
    Location(shoulder_angle=-54.56, elbow_angle=-59.2, base_angle=-185.25),
    Location(shoulder_angle=-76.96, elbow_angle=-48.4, base_angle=-185.25),
    Location(shoulder_angle=-124.32, elbow_angle=-43.2, base_angle=-185.25)
]

# Two-phase color detection parameters
PRE_SCAN_POSITION = Location(x= -3.9, y= 17.2, base_angle= -110.75) 
SCAN_POSITION = Location(shoulder_angle= -50.08, elbow_angle= -47.8, base_angle= -110.75)

# Stacking parameters
STACK_BASE_ANGLE = -31.5  # Base angle for stacking

# Storage bins (three bins) now keep a list of cubes (colors) that are stored.
STORAGE_BIN_PRE_POSITION = Location(shoulder_angle=-116.6, elbow_angle=-32.6, base_angle=0)
STORAGE_BIN_BASE_POS = Location(shoulder_angle=-128.96, elbow_angle=-43, base_angle=0) # Base position of the storage bins – this isn't meant to be used directly

STORAGE_BINS = {
    "A": {"base_angle": -50, "cube": ""},
    "B": {"base_angle": -70, "cube": ""},
    "C": {"base_angle": -90, "cube": ""}
}


class AutomaticMode(Mode):
    def __init__(self, ev3: EV3Brick, base_motor: Motor, shoulder_motor: Motor, elbow_motor: Motor,
                 gripper_motor: Motor, base_touch_sensor: TouchSensor, shoulder_touch_sensor: TouchSensor,
                 color_sensor: ColorSensor, ratios):
        super().__init__("Automatic")
        self.ev3 = ev3
        self.base_motor = base_motor
        self.shoulder_motor = shoulder_motor
        self.elbow_motor = elbow_motor
        self.gripper_motor = gripper_motor
        self.base_touch_sensor = base_touch_sensor
        self.shoulder_touch_sensor = shoulder_touch_sensor
        self.color_sensor = color_sensor
        self.ratios = ratios

        # Tower and sequence
        self.cube_sequence = CUBE_SEQUENCE
        self.current_tower = []  # Cubes correctly stacked (by color)

        # Storage bins
        self.storage_bins = STORAGE_BINS

        # Main bin pickup tracking: count of cubes picked so far (to lower the pickup position)
        self.pre_pickup_position = PRE_PICKUP_POSITION
        self.cube_pickup_count = 0

    def has_cube_in_storage(self, target_color: str) -> bool:
        """Check if any storage bin contains a cube of the target color."""
        for bin_data in self.storage_bins.values():
            if target_color == bin_data["cube"]:
                return True
        return False

    def retrieve_cube_from_storage(self, target_color: str, move_system, gripper_part) -> bool:
        """
        Retrieve a cube of the target_color from one of the storage bins.
        The cube is then delivered to the stacking area.
        """
        bin_key = None
        for key, bin_data in self.storage_bins.items():
            if target_color == bin_data["cube"]:
                bin_key = key
                # Remove one occurrence of the target cube from the bin.
                bin_data["cube"] = ""
                break

        if bin_key is None:
            print("AutomaticMode: No cube of", target_color, "found in storage.")
            return False

        storage_angle = self.storage_bins[bin_key]["base_angle"]
        move_system.move_to_location(PRE_PICKUP_POSITION.set_base_angle(storage_angle))
        print("AutomaticMode: Moving to storage bin pickup position:", storage_angle)

        gripper_part.open()

        # Move to the storage bin pickup position.
        move_system.move_to_location(STORAGE_BIN_BASE_POS.set_base_angle(storage_angle))

        # Grab the cube from storage.
        gripper_part.grab()
        print("AutomaticMode: Cube retrieved from storage.")

        destination = self.get_dynamic_stack_position()
        move_system.move_to_location(PRE_PICKUP_POSITION.set_base_angle(destination.base_angle))

        # Deliver to stack.
        if not move_system.move_to_location(destination):
            print("AutomaticMode: Error - Cannot reach safe delivery position for stacking.")
            return False

        gripper_part.release()
        self.current_tower.append(target_color)
        print("AutomaticMode: Retrieved cube delivered to stack.")
        return True

    def get_pickup_position(self) -> Location:
        return PICKUP_POSITIONS[self.cube_pickup_count % len(PICKUP_POSITIONS)]

    def get_dynamic_stack_position(self) -> Location:
        """
        Compute the stacking position based on the current tower height.
        """

        pos = PICKUP_POSITIONS[-(len(self.current_tower))]

        return pos.set_base_angle(STACK_BASE_ANGLE)

    def handle_cube_from_main_bin(self, move_system, gripper_part, color_detection_system) -> bool:
        """
        Process a new cube from the main bin: pick it up, do two-phase color detection,
        then either deliver it to the stack (if it matches the expected color)
        or deposit it in a storage bin.
        """
        # === Pickup Phase ===

        # Moves the arm above to the main bin pickup position.
        print("AutomaticMode: Moving to main bin pickup position:")
        move_system.move_to_location(PRE_PICKUP_POSITION)

        # Prepares to grab the cube.
        gripper_part.open()

        pickup_location = self.get_pickup_position()
        print("AutomaticMode: Moving to effective pickup position:", pickup_location)
        if not move_system.move_to_location(pickup_location):
            print("AutomaticMode: Error - Cannot reach pickup position.")
            return False

        gripper_part.grab()
        print("AutomaticMode: Cube grabbed from main bin.")

        # Move upward to safe height.
        if not move_system.move_to_location(PRE_PICKUP_POSITION):
            print("AutomaticMode: Error - Cannot reach safe height position.")
            return False

        # === Two-Phase Color Detection ===
        # Phase 1: Adjust base rotation while keeping (x, y) fixed.
        print("AutomaticMode: Phase 1 - Adjusting base rotation for color check")
        if not move_system.move_to_location(PRE_SCAN_POSITION):
            print("AutomaticMode: Error - Cannot adjust base for color detection.")
            return False

        wait(250)  # Stabilization delay

        # Phase 2: Move to final color check position.
        print("AutomaticMode: Phase 2 - Moving to final color check position")
        if not move_system.move_to_location(SCAN_POSITION):
            print("AutomaticMode: Error - Cannot reach final color check position.")
            return False

        detected_color = color_detection_system.detect_color()
        print("AutomaticMode: Detected cube color:", detected_color)

        # === Decision & Delivery Phase ===
        expected_color = (self.cube_sequence[len(self.current_tower)]
                          if len(self.current_tower) < len(self.cube_sequence) else None)
        if detected_color == expected_color:
            # Correct cube: deliver to stacking area.
            self.current_tower.append(detected_color)
            destination = self.get_dynamic_stack_position()
            print("AutomaticMode: Cube matches expected color. Stacking at:", destination)
        else:
            # Incorrect cube: deposit it into a storage bin.
            # Select the storage bin with the fewest cubes.
            bin_key = None
            for key, bin_data in self.storage_bins.items():
                if bin_data["cube"] == "":
                    bin_key = key
                    break

            if bin_key is None:
                print("AutomaticMode: No storage bin available for incorrect cube.")
                return False

            bin_angle = self.storage_bins[bin_key]["base_angle"]
            destination = STORAGE_BIN_BASE_POS.set_base_angle(bin_angle)

            self.storage_bins[bin_key]["cube"] = detected_color
            print("AutomaticMode: Cube does not match expected color. Storing in bin", bin_key)

        # Two-phase delivery: move upward first, then to destination.
        move_system.move_to_location(PRE_PICKUP_POSITION.set_base_angle(destination.base_angle))
        print("AutomaticMode: Moving upward to safe delivery position")
        if not move_system.move_to_location(destination):
            print("AutomaticMode: Error - Cannot reach safe delivery position.")
            return False

        print("AutomaticMode: Releasing cube at destination:", destination)
        gripper_part.release()
        print("AutomaticMode: Cube released at destination.")

        # Increment pickup counter for next main-bin cube.
        self.cube_pickup_count += 1
        return True

    def run(self):
        print("Running Automatic Mode with full tower completion logic...")
        # Initialize parts with typical Python naming.
        base_part = BasePart(self.base_motor, self.base_touch_sensor, self.ratios["base"])
        shoulder_part = ShoulderPart(self.shoulder_motor, self.shoulder_touch_sensor, self.ratios["shoulder"],
                                     length=9.6)
        elbow_part = ElbowPart(self.elbow_motor, self.ratios["elbow"], length=13.5)
        gripper_part = GripperPart(self.gripper_motor)

        # Calibrate parts.
        base_part.calibrate()
        elbow_part.calibrate()
        shoulder_part.calibrate()
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

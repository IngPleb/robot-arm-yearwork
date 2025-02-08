#!/usr/bin/env pybricks-micropython

from pybricks.ev3devices import Motor
from pybricks.hubs import EV3Brick
from pybricks.parameters import Port
from pybricks.tools import wait

ev3 = EV3Brick()
motor = Motor(Port.B)
motor.hold()

# Calibration parameters
SPEED = -400
ANGLE_THRESHOLD = 6  # adjust this constant as needed
TARGET_TICKS = 17     # can be set to any value between 3-5 or made configurable
TENSION_ANGLE = -300

tick_count = 0
last_angle = motor.angle()  # initialize last_angle before starting
while tick_count < TARGET_TICKS:
    motor.run(SPEED)
    
    wait(10)
    
    current_angle = motor.angle()
    angle_difference = abs(current_angle - last_angle)
    
    print("Current angle is: " + str(current_angle))
    print("Angle difference is: " + str(angle_difference))
    
    if angle_difference < ANGLE_THRESHOLD:
        tick_count += 1
        print("Tick count: " + str(tick_count))
    else:
        # Optionally reset tick_count if the movement difference exceeds the threshold
        tick_count = 0
        
    last_angle = current_angle
    
    
motor.hold()
    
# Remove the tension from the motor
motor.run_angle(SPEED, TENSION_ANGLE)

motor.reset_angle(0)
ev3.speaker.beep()
print("Calibration complete")
wait(1000)


#motor.run_angle(100, 300)
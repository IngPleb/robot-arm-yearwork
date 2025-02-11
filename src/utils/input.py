from pybricks.hubs import EV3Brick
from pybricks.parameters import Button
from pybricks.tools import wait


def get_input(ev3: EV3Brick) -> Button:
    pressed_inputs = []
    while len(pressed_inputs) == 0:
        pressed_inputs = ev3.buttons.pressed()
        wait(10)

    return pressed_inputs[0]

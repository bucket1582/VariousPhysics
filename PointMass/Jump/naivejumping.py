import turtle as t

from Basics.kinematics import *
from Basics.input_handler import *
from Basics.renderer import setup_renderer, begin_render

from PointMass.moving_point import MovingPoint
from PointMass.Fall.generalfalling import *

HORIZONTAL_SPEED = 50
VERTICAL_SPEED_MAX = 50
MAX_HOLD = 0.5

# Bad practice but...
started_jump = False

def horinzontal_loop_dynamics(moving_position: MovingPoint):
    if moving_position.x > 100:
        delta = moving_position.x - 100
        moving_position.x = -100 + delta

def naive_jump_press(event: KeyboardInputEvent, moving_position: MovingPoint):
    global started_jump
    if abs(moving_position.y + 100) < 1e-2:
        moving_position.vy = VERTICAL_SPEED_MAX
        started_jump = True

def naive_jump(event: KeyboardHoldEvent, moving_position: MovingPoint):
    if event.duration < MAX_HOLD and started_jump:
        moving_position.vy = VERTICAL_SPEED_MAX

def naive_jump_release(event: KeyboardInputEvent):
    global started_jump
    started_jump = False

if __name__ == "__main__":
    set_parameters(elasticity=0)
    setup_kinematics(PHYSICS_FPS)

    character, pen, env_pen, screen = preset()
    character.vx = HORIZONTAL_SPEED
    falling_setup(character)
    character.add_post_behavior(horinzontal_loop_dynamics)
    key_handler = KeyboardInputHandler(screen)
    key_handler.bind("space", "PRESS", lambda ev: naive_jump_press(ev, character))
    key_handler.bind("space", "HOLD", lambda ev: naive_jump(ev, character))
    key_handler.bind("space", "RELEASE", lambda ev: naive_jump_release(ev))
    key_handler.start_listen()

    setup_renderer(FPS, pen, env_pen, screen)
    begin_simulation()
    begin_render()
import turtle as t

from Basics.kinematics import *
from Basics.input_handler import *
from Basics.renderer import setup_renderer, begin_render

from PointMass.moving_point import MovingPoint
from PointMass.Fall.generalfalling import *

HORIZONTAL_SPEED = 100
JUMP_IMPULSE = 100
JUMP_FORCE = 1000
MAX_HOLD = 0.5

# Bad practice but...
started_jump = False
move = 0

def horinzontal_loop_dynamics(moving_position: MovingPoint):
    if moving_position.x > 100:
        delta = moving_position.x - 100
        moving_position.x = -100 + delta

    if moving_position.x < -100:
            delta = moving_position.x + 100
            moving_position.x = 100 + delta

def constant_force_jump_press(event: KeyPressEvent, moving_position: MovingPoint):
    global started_jump
    if abs(moving_position.y + 100) < 1e-2:
        moving_position.exert_impulse_out_of_sync(0, JUMP_IMPULSE)
        moving_position.exert_force_out_of_sync(0, JUMP_FORCE)
        started_jump = True

def constant_force_jump(event: KeyHoldEvent, moving_position: MovingPoint):
    global started_jump
    if event.duration < MAX_HOLD and started_jump:
        moving_position.exert_force_out_of_sync(0, JUMP_FORCE)

def constant_force_jump_release(event: KeyReleaseEvent, moving_position: MovingPoint):
    global started_jump
    started_jump = False

def naive_right_press(event: KeyPressEvent):
    global move
    move = 1

def naive_left_press(event: KeyPressEvent):
    global move
    move = -1

def naive_right_hold(event: KeyHoldEvent, moving_position: MovingPoint):
    if move == 1:
        moving_position.vx = HORIZONTAL_SPEED

def naive_left_hold(event: KeyHoldEvent, moving_position: MovingPoint):
    if move == -1:
        moving_position.vx = -HORIZONTAL_SPEED

def naive_right_release(event: KeyReleaseEvent, moving_position: MovingPoint):
    global move
    if move == 1:
        move = 0
        moving_position.vx = 0


def naive_left_release(event: KeyReleaseEvent, moving_position: MovingPoint):
    global move
    if move == -1:
        move = 0
        moving_position.vx = 0

if __name__ == "__main__":
    set_parameters(elasticity=0)
    setup_kinematics(PHYSICS_FPS)

    character, pen, env_pen, screen = preset()
    falling_setup(character)
    character.add_post_behavior(horinzontal_loop_dynamics)
    key_handler = KeyboardInputHandler(screen)
    key_handler.bind("d", "PRESS", lambda ev: naive_right_press(ev))
    key_handler.bind("d", "HOLD", lambda ev: naive_right_hold(ev, character))
    key_handler.bind("d", "RELEASE", lambda ev: naive_right_release(ev, character))
    key_handler.bind("a", "PRESS", lambda ev: naive_left_press(ev))
    key_handler.bind("a", "HOLD", lambda ev: naive_left_hold(ev, character))
    key_handler.bind("a", "RELEASE", lambda ev: naive_left_release(ev, character))
    key_handler.bind("space", "PRESS", lambda ev: constant_force_jump_press(ev, character))
    key_handler.bind("space", "HOLD", lambda ev: constant_force_jump(ev, character))
    key_handler.bind("space", "RELEASE", lambda ev: constant_force_jump_release(ev, character))
    key_handler.start_listen()

    setup_renderer(FPS, pen, env_pen, screen)
    begin_simulation()
    begin_render()
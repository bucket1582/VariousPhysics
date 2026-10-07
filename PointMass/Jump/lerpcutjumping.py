import turtle as t

from Basics.kinematics import *
from Basics.input_handler import *
from Basics.renderer import setup_renderer, begin_render

from PointMass.moving_point import MovingPoint
from PointMass.Fall.generalfalling import *

HORIZONTAL_SPEED = 100
VERTICAL_SPEED_MAX = 100
VERTICAL_SPEED_MIN = 0
CUT_SPEED_RATIO = 0.4
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

def cut_jump_press(event: KeyPressEvent, moving_position: MovingPoint):
    global started_jump
    if abs(moving_position.y + 100) < 1e-2:
        moving_position.vy = VERTICAL_SPEED_MAX
        started_jump = True

def cut_jump(event: KeyHoldEvent, moving_position: MovingPoint):
    global started_jump
    if event.duration < MAX_HOLD and started_jump:
        ratio = event.duration / MAX_HOLD
        moving_position.vy = VERTICAL_SPEED_MAX * (1 - ratio)+ VERTICAL_SPEED_MIN * ratio
    elif started_jump:
        started_jump = False
        moving_position.vy *= CUT_SPEED_RATIO

def cut_jump_release(event: KeyReleaseEvent, moving_position: MovingPoint):
    global started_jump
    if started_jump:
        moving_position.vy *= CUT_SPEED_RATIO
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
    key_handler.bind("space", "PRESS", lambda ev: cut_jump_press(ev, character))
    key_handler.bind("space", "HOLD", lambda ev: cut_jump(ev, character))
    key_handler.bind("space", "RELEASE", lambda ev: cut_jump_release(ev, character))
    key_handler.start_listen()

    setup_renderer(FPS, pen, env_pen, screen)
    begin_simulation()
    begin_render()
import turtle as t
import time

from Basics.dynamics import *
from Basics.statistics import *

# Constants
GRAVITY = 500
DAMP = 2
FPS = 1000
PHYSICS_FPS = 1000
ELASTICITY = 0.8

statistics = FrameStatistics()
character = MovingPosition(0, 100, 0, 0, 0, 0)
screen = t.Screen()
screen.setworldcoordinates(-200, -200, 200, 200)
screen.setup(500, 500)
screen.tracer(0, 0)

pen = t.Turtle()
pen.ht()
pen.color("black")

env_pen = t.Turtle()
env_pen.ht()
env_pen.color("black")

env_pen.pu()
env_pen.goto(-100, -102.5)
env_pen.pd()
env_pen.goto(100, -102.5)
env_pen.pu()

def falling_dynamics(moving_position: MovingPosition):
    moving_position.ay = -GRAVITY - DAMP * moving_position.vy

def ground_dynamics(moving_position: MovingPosition):
    if moving_position.y < -100:
        moving_position.y = -100
        moving_position.vy = ELASTICITY * (-moving_position.vy)

character.add_pre_behavior(falling_dynamics)
character.add_post_behavior(ground_dynamics)

def render():
    pen.clear()
    pen.pu()
    
    # property를 활용하여 값 가져오기
    render_x, render_y = character.position
    
    pen.goto(render_x, render_y)
    pen.pd()
    pen.dot(10)
    screen.update()

if __name__ == "__main__":
    # 1. 물리 엔진 초기 세팅 및 가동
    physics = PhysicsThread.thread()
    physics.set_fps(PHYSICS_FPS)
    physics.simulate()
    
    old_render_time = time()
    last_print_time = time()
    
    # 2. 메인 스레드는 렌더링만 전담
    while True:
        try:
            curr_time = time()
            if curr_time > old_render_time + 1 / FPS:
                render()
                old_render_time = curr_time
                
        except t.Terminator:
            break

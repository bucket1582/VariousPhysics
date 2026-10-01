import turtle as t
import time

from Basics.dynamics import *
from Basics.statistics import *

# Constants
GRAVITY = 500
CLAMP = 150
FPS = 1000
PHYSICS_FPS = 1000

statistics = FrameStatistics()
character = MovingPosition(0, 100, 0, 0, 0, -GRAVITY, -1, CLAMP)
screen = t.Screen()
screen.setworldcoordinates(-200, -200, 200, 200)
screen.setup(500, 500)
screen.tracer(0, 0)

pen = t.Turtle()
pen.ht()
pen.color("black")

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

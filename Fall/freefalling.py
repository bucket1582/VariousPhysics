import turtle as t
import time

from Basics.dynamics import *
from Basics.statistics import *

# Constants
GRAVITY = 500
FPS = 1000
PHYSICS_FPS = 1000

statistics = FrameStatistics()
character = MovingPosition(0, 100, 0, 0, 0, -GRAVITY)
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
    pen.goto(character.x, character.y)
    pen.pd()
    pen.dot(10)
    screen.update()

def phsyics_update(delta: float):
    character.update(delta)


if __name__ == "__main__":
    old_physics_time = time.time()
    old_render_time = old_physics_time
    
    # print 출력을 1초에 한 번만 하도록 타이머를 추가합니다.
    last_print_time = time.time()
    
    while True:
        try:
            curr_time = time.time()
            
            # 1. 물리 업데이트 (초당 1000번 목표)
            if curr_time > old_physics_time + 1 / PHYSICS_FPS:
                delta = curr_time - old_physics_time
                statistics.add_physics_frame_stat(1 / delta)
                phsyics_update(delta)
                old_physics_time = curr_time
                
            # 2. 렌더링 업데이트 (초당 60번 목표)
            if curr_time > old_render_time + 1 / FPS:
                delta = curr_time - old_render_time
                statistics.add_render_frame_stat(1 / delta)
                render()
                old_render_time = curr_time
                
            # 3. 콘솔 출력은 별도로 1초(또는 0.5초)에 한 번만 실행하여 I/O 병목을 없앱니다.
            if curr_time > last_print_time + 1.0:
                print(statistics)
                last_print_time = curr_time
                
        except t.Terminator: # 창이 닫혔을 때 우아하게 종료
            break
        except Exception as e:
            print(f"Error: {e}")
            break

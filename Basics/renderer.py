from typing import Self, Optional, Callable
from abc import ABC, abstractmethod
from turtle import Turtle, _Screen

from Basics.design_pattern import Singleton

class RenderObject(ABC):
    def render(self, pen: Turtle, env_pen: Turtle, screen: _Screen) -> None:
        self._pre_render(pen, env_pen, screen)
        self._render(pen, env_pen, screen)
        self._post_render(pen, env_pen, screen)

    def _pre_render(self, pen: Turtle, env_pen: Turtle, screen: _Screen) -> None:
        pen.pd()

    def _post_render(self, pen:Turtle, env_pen: Turtle, screen: _Screen) -> None:
        pen.pu()

    @abstractmethod
    def _render(self, pen: Turtle, env_pen: Turtle, screen: _Screen) -> None:
        pass

class RenderThread(Singleton):
    def __init__(self):
        self.render_objects: list[RenderObject] = []
        self._frame_interval: float = 1 / 120

        self.pen: Optional[Turtle] = None
        self.env_pen: Optional[Turtle] = None
        self.screen: Optional[_Screen] = None

    def setup(self, pen: Turtle, env_pen: Turtle, screen: _Screen):
        self.pen = pen
        self.env_pen = env_pen
        self.screen = screen

    @property
    def frame_interval(self):
        return self._frame_interval

    def begin_loop_thread(self):
        if self.pen is None or self.env_pen is None or self.screen is None:
            raise ValueError("아직 렌더러에 필요한 정보가 모두 주어지지 않았습니다. setup을 진행하세요.")
        self._loop()

    def subscribe(self, object: RenderObject) -> None:
        self.render_objects.append(object)

    def set_fps(self, fps: int):
        self._frame_interval = 1 / fps

    def _render_step(self):
        self.pen.clear()
        for object in self.render_objects:
            object.render(self.pen, self.env_pen, self.screen)
        self.screen.update()
        
        # frame_interval(예: 1/120초 -> 약 8ms) 뒤에 이 함수를 다시 실행하도록 Tkinter 스케줄러에 예약
        delay_ms = int(self._frame_interval * 1000)
        self.screen.ontimer(self._render_step, delay_ms)
        
    def begin_loop_thread(self):
        if self.pen is None or self.env_pen is None or self.screen is None:
            raise ValueError("아직 렌더러에 필요한 정보가 모두 주어지지 않았습니다.")
        self._render_step()
        self.screen.mainloop() # Tkinter 메인 루프 가동 (창 닫기 등 GUI 이벤트 정상 처리)

def setup_renderer(fps: int, pen: Turtle, env_pen: Turtle, screen: _Screen) -> tuple['RenderThread']:
    renderer = RenderThread.instance()
    renderer.setup(pen, env_pen, screen)
    renderer.set_fps(fps)

def begin_render() -> None:
    RenderThread.instance().begin_loop_thread()

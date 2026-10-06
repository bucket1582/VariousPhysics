from typing import Callable
from abc import ABC, abstractmethod

from Basics.design_pattern import *

class PhysicsThread(HasTimedLoop, Singleton):
    def __init__(self):
        # 인스턴스 생성 시 구독자 리스트 초기화
        self.subscribers: list[Callable[[float], None]] = []
        self._frame_interval: float = 1 / 240 # 기본값

    @property
    def frame_interval(self):
        return self._frame_interval

    def set_fps(self, fps: int):
        self._frame_interval = 1 / fps

    def on_physics_frame(self, func: Callable[[float], None]):
        self.subscribers.append(func)

    def _loop_action(self, old_time, curr_time, delta):
        for func in self.subscribers:
            func(delta)


def setup_kinematics(fps: int) -> tuple['PhysicsThread']:
    physics = PhysicsThread.instance()
    physics.set_fps(fps)

def begin_simulation() -> None:
    PhysicsThread.instance().begin_loop_thread()

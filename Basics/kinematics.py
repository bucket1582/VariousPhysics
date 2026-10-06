from dataclasses import dataclass, field
from typing import Self, Optional, Callable

from Basics.design_pattern import *

class PhysicsThread(HasTimedLoop):
    singleton: Optional[Self] = None
    
    def __init__(self):
        # 인스턴스 생성 시 구독자 리스트 초기화
        self.subscribers: list[Callable[[float], None]] = []
        self._frame_interval: float = 1 / 240 # 기본값

    @classmethod
    def thread(cls) -> Self:
        if cls.singleton is None:
            cls.singleton = PhysicsThread()
        return cls.singleton

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

@dataclass
class MovingPoint:
    x: float
    y: float
    # 기본값이 없는 변수들을 위로 배치
    vx: float
    vy: float
    ax: float
    ay: float
    # 기본값이 있는 변수들을 아래로 배치
    clamp_vx: float = -1
    clamp_vy: float = -1

    pre_behaviors: list[Callable[['MovingPoint'], None]] = field(default_factory=list)
    post_behaviors: list[Callable[['MovingPoint'], None]] = field(default_factory=list)

    def __post_init__(self):
        # 객체가 생성되자마자 알아서 물리 스레드에 자신을 등록 (아주 훌륭한 패턴입니다)
        PhysicsThread.thread().on_physics_frame(self.update)

    def add_pre_behavior(self, behavior: Callable[['MovingPoint'], None]):
        self.pre_behaviors.append(behavior)

    def add_post_behavior(self, behavior: Callable[['MovingPoint'], None]):
            self.post_behaviors.append(behavior)

    def update(self, delta: float):
        for behavior in self.pre_behaviors:
            behavior(self)

        old_vx = self.vx
        old_vy = self.vy

        new_vx = old_vx + self.ax * delta
        new_vy = old_vy + self.ay * delta

        if self.clamp_vx > 0:
            if new_vx > self.clamp_vx: 
                new_vx = self.clamp_vx
            elif new_vx < -self.clamp_vx: 
                new_vx = -self.clamp_vx
                
        if self.clamp_vy > 0:
            if new_vy > self.clamp_vy: 
                new_vy = self.clamp_vy
            elif new_vy < -self.clamp_vy: 
                new_vy = -self.clamp_vy

        # Zeroing
        if abs(new_vx) < 1e-6:
            new_vx = 0
        if abs(new_vy) < 1e-6:
            new_vy = 0

        self.x += ((old_vx + new_vx) / 2) * delta
        self.y += ((old_vy + new_vy) / 2) * delta

        self.vx = new_vx
        self.vy = new_vy

        for behavior in self.post_behaviors:
            behavior(self)

    @property
    def position(self):
        return (self.x, self.y)


@dataclass
class RoundRigidBody(MovingPoint):
    radius: float = 5

    def __post_init__(self):
        super().__post_init__()


def setup_kinematics(fps: int) -> tuple['PhysicsThread']:
    physics = PhysicsThread.thread()
    physics.set_fps(fps)
    return physics

def begin_simulation() -> None:
    PhysicsThread.thread().begin_loop_thread()

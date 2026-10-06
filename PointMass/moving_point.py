from dataclasses import dataclass, field
from typing import Callable

from Basics.kinematics import PhysicsThread
from Basics.renderer import RenderObject, RenderThread

@dataclass
class MovingPoint(RenderObject):
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
    diameter: int = 10

    pre_behaviors: list[Callable[['MovingPoint'], None]] = field(default_factory=list)
    post_behaviors: list[Callable[['MovingPoint'], None]] = field(default_factory=list)

    def __post_init__(self):
        # 객체가 생성되자마자 알아서 물리 스레드에 자신을 등록 (아주 훌륭한 패턴입니다)
        PhysicsThread.instance().on_physics_frame(self.update)
        RenderThread.instance().subscribe(self)

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

    def _render(self, pen, env_pen, screen):
        pen.goto(self.x, self.y)
        pen.dot(self.diameter)

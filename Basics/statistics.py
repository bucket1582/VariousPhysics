from collections import deque
from dataclasses import dataclass, field

@dataclass
class FrameStatistics:
    running_mean_capacity: int = 30
    render_frames: deque[float] = field(default_factory=deque)
    physics_frames: deque[float] = field(default_factory=deque)

    def add_render_frame_stat(self, datum: float):
        self.render_frames.append(datum)
        while len(self.render_frames) > self.running_mean_capacity:
            self.render_frames.popleft()

    def add_physics_frame_stat(self, datum: float):
            self.physics_frames.append(datum)
            while len(self.physics_frames) > self.running_mean_capacity:
                self.physics_frames.popleft()

    @property
    def render_frame_mean(self):
        if len(self.render_frames) == 0: return 0
        return sum(self.render_frames) / len(self.render_frames)

    @property
    def physics_frame_mean(self):
        if len(self.physics_frames) == 0: return 0
        return sum(self.physics_frames) / len(self.physics_frames)

    def __str__(self):
        return f"Render: {self.render_frame_mean}, Physics: {self.physics_frame_mean}"

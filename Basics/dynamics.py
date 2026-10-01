from dataclasses import dataclass

@dataclass
class MovingPosition:
    x: float
    y: float
    vx: float
    vy: float
    ax: float
    ay: float

    def update(self, delta: float):
        old_vx = self.vx
        old_vy = self.vy

        new_vx = old_vx + self.ax * delta
        new_vy = old_vy + self.ay * delta

        # Middle point difference
        self.x += ((old_vx + new_vx) / 2) * delta
        self.y += ((old_vy + new_vy) / 2) * delta

        self.vx = new_vx
        self.vy = new_vy

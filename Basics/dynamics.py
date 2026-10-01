from dataclasses import dataclass

@dataclass
class MovingPosition:
    x: float
    y: float
    vx: float
    vy: float
    ax: float
    ay: float

    def update(
            self, delta: float, clamp_vx: float = -1, clamp_vy: float = -1
        ):
        old_vx = self.vx
        old_vy = self.vy

        new_vx = old_vx + self.ax * delta
        new_vy = old_vy + self.ay * delta

        if clamp_vx > 0:
            if new_vx > clamp_vx: 
                new_vx = clamp_vx
            elif new_vx < -clamp_vx: 
                new_vx = -clamp_vx
                
        if clamp_vy > 0:
            if new_vy > clamp_vy: 
                new_vy = clamp_vy
            elif new_vy < -clamp_vy: 
                new_vy = -clamp_vy

        # Middle point difference
        self.x += ((old_vx + new_vx) / 2) * delta
        self.y += ((old_vy + new_vy) / 2) * delta

        self.vx = new_vx
        self.vy = new_vy

"""Court geometry and image <-> world coordinate conversion.

World coordinates (cm):
    origin = rim center, X = horizontal (image right is +), Y = up.
The rim's known diameter (45.72 cm) gives the pixel-to-cm scale, so the
camera must look at the shot from the side (roughly perpendicular to the
shooter-rim line) for the numbers to be meaningful.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

RIM_DIAMETER_CM = 45.72
RIM_RADIUS_CM = RIM_DIAMETER_CM / 2
BALL_DIAMETER_CM = 24.3          # size 7 ball
BALL_RADIUS_CM = BALL_DIAMETER_CM / 2
RIM_HEIGHT_CM = 305.0
GRAVITY_CM_S2 = 981.0

# Ball center can pass the rim plane within this distance of the rim center
# without touching the rim (front/back direction).
CLEAN_WINDOW_CM = RIM_RADIUS_CM - BALL_RADIUS_CM


@dataclass
class Rim:
    """Rim given by its left and right edge in image pixels."""

    x1: float
    y1: float
    x2: float
    y2: float

    def __post_init__(self) -> None:
        if self.x2 < self.x1:
            self.x1, self.y1, self.x2, self.y2 = self.x2, self.y2, self.x1, self.y1
        if self.width_px <= 0:
            raise ValueError("rim edges must be two different points")

    @property
    def cx(self) -> float:
        return (self.x1 + self.x2) / 2

    @property
    def cy(self) -> float:
        return (self.y1 + self.y2) / 2

    @property
    def width_px(self) -> float:
        return ((self.x2 - self.x1) ** 2 + (self.y2 - self.y1) ** 2) ** 0.5

    @property
    def px_per_cm(self) -> float:
        return self.width_px / RIM_DIAMETER_CM

    def to_world(self, x: float, y: float) -> tuple[float, float]:
        s = self.px_per_cm
        return (x - self.cx) / s, (self.cy - y) / s

    def to_image(self, X: float, Y: float) -> tuple[float, float]:
        s = self.px_per_cm
        return self.cx + X * s, self.cy - Y * s

    # --- persistence -------------------------------------------------
    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(asdict(self), indent=2))

    @classmethod
    def load(cls, path: str | Path) -> "Rim":
        return cls(**json.loads(Path(path).read_text()))

    @classmethod
    def parse(cls, text: str) -> "Rim":
        """Parse 'x1,y1,x2,y2'."""
        parts = [float(v) for v in text.split(",")]
        if len(parts) != 4:
            raise ValueError("expected x1,y1,x2,y2")
        return cls(*parts)

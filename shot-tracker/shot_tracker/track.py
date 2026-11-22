"""Single-ball tracker: links per-frame detections into continuous tracks."""
from __future__ import annotations

import math
from dataclasses import dataclass

from .detect import Detection
from .geometry import GRAVITY_CM_S2, Rim


@dataclass
class TrackPoint:
    frame: int
    t: float      # seconds
    x: float      # image px
    y: float
    X: float      # world cm (rim center origin, Y up)
    Y: float
    r: float


class BallTracker:
    def __init__(self, rim: Rim, fps: float, max_gap_s: float = 0.12, gate_cm: float = 45.0) -> None:
        self.rim = rim
        self.fps = fps
        self.max_gap = max(2, int(round(max_gap_s * fps)))
        self.gate_cm = gate_cm
        self.tracks: list[list[TrackPoint]] = []
        self._active: list[TrackPoint] | None = None

    def _predict(self, t: float) -> tuple[float, float] | None:
        tr = self._active
        if not tr:
            return None
        last = tr[-1]
        if len(tr) < 2:
            return last.X, last.Y
        prev = tr[-2]
        dt0 = last.t - prev.t
        if dt0 <= 0:
            return last.X, last.Y
        vx = (last.X - prev.X) / dt0
        vy = (last.Y - prev.Y) / dt0
        dt = t - last.t
        return last.X + vx * dt, last.Y + vy * dt - 0.5 * GRAVITY_CM_S2 * dt * dt

    def update(self, frame: int, dets: list[Detection]) -> TrackPoint | None:
        t = frame / self.fps
        if self._active and frame - self._active[-1].frame > self.max_gap:
            self._close()

        best = None
        pred = self._predict(t)
        if pred is not None:
            gap = frame - self._active[-1].frame
            gate = self.gate_cm * (1 + 0.5 * (gap - 1))
            best_d = gate
            for d in dets:
                X, Y = self.rim.to_world(d.x, d.y)
                dist = math.hypot(X - pred[0], Y - pred[1])
                if dist < best_d:
                    best, best_d = d, dist
        if best is None and self._active is None and dets:
            best = dets[0]
            self._active = []
        if best is None:
            return None

        X, Y = self.rim.to_world(best.x, best.y)
        p = TrackPoint(frame, t, best.x, best.y, X, Y, best.r)
        self._active.append(p)
        return p

    def _close(self) -> None:
        if self._active:
            self.tracks.append(self._active)
        self._active = None

    def finish(self) -> list[list[TrackPoint]]:
        self._close()
        return self.tracks

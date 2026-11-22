"""Multi-target tracker: links per-frame detections into continuous tracks.

Every ball-colored blob is tracked (the ball, but also e.g. the shooter's
arms). Deciding which track is a shot is left to the analysis step, which
only accepts tracks that follow a free-flight parabola above the rim.
"""
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
    def __init__(
        self,
        rim: Rim,
        fps: float,
        max_gap_s: float = 0.12,
        gate_cm: float = 45.0,
        new_track_gate_cm: float = 70.0,
    ) -> None:
        self.rim = rim
        self.fps = fps
        self.max_gap = max(2, int(round(max_gap_s * fps)))
        self.gate_cm = gate_cm
        self.new_track_gate_cm = new_track_gate_cm
        self.tracks: list[list[TrackPoint]] = []
        self._active: list[list[TrackPoint]] = []

    @staticmethod
    def _predict(tr: list[TrackPoint], t: float) -> tuple[float, float]:
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

    def update(self, frame: int, dets: list[Detection]) -> None:
        t = frame / self.fps
        # retire stale tracks
        still = []
        for tr in self._active:
            (still if frame - tr[-1].frame <= self.max_gap else self.tracks).append(tr)
        self._active = still

        world = [self.rim.to_world(d.x, d.y) for d in dets]
        pairs = []
        for ti, tr in enumerate(self._active):
            px, py = self._predict(tr, t)
            gap = frame - tr[-1].frame
            base = self.gate_cm if len(tr) >= 2 else self.new_track_gate_cm
            gate = base * (1 + 0.5 * (gap - 1))
            for di, (X, Y) in enumerate(world):
                dist = math.hypot(X - px, Y - py)
                if dist < gate:
                    pairs.append((dist, ti, di))
        pairs.sort()
        used_t: set[int] = set()
        used_d: set[int] = set()
        for _, ti, di in pairs:   # greedy nearest-first assignment
            if ti in used_t or di in used_d:
                continue
            used_t.add(ti)
            used_d.add(di)
            self._active[ti].append(self._point(frame, t, dets[di], world[di]))
        for di, d in enumerate(dets):
            if di not in used_d:
                self._active.append([self._point(frame, t, d, world[di])])

    @staticmethod
    def _point(frame: int, t: float, d: Detection, w: tuple[float, float]) -> TrackPoint:
        return TrackPoint(frame, t, d.x, d.y, w[0], w[1], d.r)

    def finish(self) -> list[list[TrackPoint]]:
        self.tracks.extend(self._active)
        self._active = []
        self.tracks.sort(key=lambda tr: tr[0].frame)
        return self.tracks

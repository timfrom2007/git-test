"""Synthetic side-view shooting video with known ground truth.

Used to test the pipeline before real footage is available. Each shot is
defined by its release angle and the depth at which it reaches rim height;
the release speed is solved from projectile physics.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from .geometry import (
    BALL_RADIUS_CM,
    CLEAN_WINDOW_CM,
    GRAVITY_CM_S2 as G,
    RIM_HEIGHT_CM,
    RIM_RADIUS_CM,
    Rim,
)

W, H = 1280, 720
SCALE = 2.0                       # px per cm
RIM_CENTER_PX = (1000.0, 300.0)
BALL_BGR = (40, 115, 225)
RIM_BGR = (20, 70, 230)


@dataclass
class ShotSpec:
    release_angle_deg: float
    depth_cm: float
    distance_cm: float = 450.0
    release_height_cm: float = 230.0


@dataclass
class ShotTruth:
    release_frame: int
    result: str
    release_angle_deg: float
    release_speed_ms: float
    entry_angle_deg: float
    depth_cm: float
    apex_height_cm: float
    release_height_cm: float


def make_rim() -> Rim:
    half = RIM_RADIUS_CM * SCALE
    cx, cy = RIM_CENTER_PX
    return Rim(cx - half, cy, cx + half, cy)


def _flight(spec: ShotSpec):
    th = math.radians(spec.release_angle_deg)
    x0 = -spec.distance_cm
    y0 = spec.release_height_cm - RIM_HEIGHT_CM
    D = spec.depth_cm - x0
    denom = 2 * math.cos(th) ** 2 * (y0 + D * math.tan(th))
    if denom <= 0:
        raise ValueError("release angle too low to reach the rim")
    v = math.sqrt(G * D * D / denom)
    vx, vy = v * math.cos(th), v * math.sin(th)
    te = D / vx
    return x0, y0, vx, vy, te


def shot_samples(spec: ShotSpec, fps: float) -> tuple[list[tuple[float, float]], ShotTruth]:
    """Ball positions (world cm) for every frame of one shot, plus truth."""
    x0, y0, vx, vy, te = _flight(spec)
    pos: list[tuple[float, float]] = []
    # 1) hold / shooting motion: ball rises from chest to release, eased
    n_hold = int(0.45 * fps)
    for i in range(n_hold):
        u = i / n_hold
        e = 1 - (1 - u) ** 2
        pos.append((x0 - 25 * (1 - e), y0 - 70 * (1 - e)))
    release_idx = len(pos)
    # 2) free flight until rim height
    n_fl = int(te * fps)
    for i in range(n_fl + 1):
        t = i / fps
        pos.append((x0 + vx * t, y0 + vy * t - 0.5 * G * t * t))
    vy_e = vy - G * te
    xe = x0 + vx * te
    make = abs(spec.depth_cm) < CLEAN_WINDOW_CM - 1
    t_start = (n_fl + 1) / fps
    if make:
        # through the net: horizontal speed killed, falls slower
        px, py = x0 + vx * t_start, y0 + vy * t_start - 0.5 * G * t_start ** 2
        for i in range(1, int(0.5 * fps)):
            t = i / fps
            pos.append((px + 0.25 * vx * t, py + 0.6 * vy_e * t - 0.5 * G * t * t))
    else:
        # rim contact: bounce back up and away
        bx, by = xe, 0.0
        bvx, bvy = -0.45 * vx, 0.4 * abs(vy_e)
        for i in range(1, int(0.8 * fps)):
            t = i / fps
            pos.append((bx + bvx * t, by + bvy * t - 0.5 * G * t * t))
    t_apex = vy / G
    truth = ShotTruth(
        release_frame=release_idx,  # offset added by caller
        result="make" if make else "miss",
        release_angle_deg=spec.release_angle_deg,
        release_speed_ms=math.hypot(vx, vy) / 100,
        entry_angle_deg=math.degrees(math.atan2(-vy_e, vx)),
        depth_cm=spec.depth_cm,
        apex_height_cm=RIM_HEIGHT_CM + y0 + vy * t_apex - 0.5 * G * t_apex ** 2,
        release_height_cm=spec.release_height_cm,
    )
    return pos, truth


def _background(rim: Rim) -> np.ndarray:
    grad = np.linspace(70, 120, H, dtype=np.float32)[:, None]
    bg = np.repeat(np.repeat(grad, W, axis=1)[:, :, None], 3, axis=2)
    bg[:, :, 0] += 15
    img = bg.clip(0, 255).astype(np.uint8)
    # floor
    floor_y = int(rim.cy + RIM_HEIGHT_CM * SCALE * 0.75)
    cv2.rectangle(img, (0, floor_y), (W, H), (60, 90, 120), -1)
    # backboard (seen edge-on) and pole
    bx = int(rim.cx + (RIM_RADIUS_CM + 15) * SCALE)
    cv2.rectangle(img, (bx, int(rim.cy - 90 * SCALE)), (bx + 6, int(rim.cy + 15 * SCALE)), (235, 235, 235), -1)
    cv2.rectangle(img, (bx + 6, int(rim.cy - 40 * SCALE)), (bx + 30, H), (50, 50, 50), -1)
    return img


def _draw_static_front(img: np.ndarray, rim: Rim) -> None:
    # net
    for k in range(5):
        u = k / 4
        top = (int(rim.x1 + u * rim.width_px), int(rim.cy))
        bot = (int(rim.cx + (u - 0.5) * rim.width_px * 0.55), int(rim.cy + 40 * SCALE))
        cv2.line(img, top, bot, (225, 225, 225), 1, cv2.LINE_AA)
    cv2.line(img, (int(rim.x1), int(rim.cy)), (int(rim.x2) + int(15 * SCALE), int(rim.cy)), RIM_BGR, 4)


def generate(out_video: str | Path, specs: list[ShotSpec], fps: float = 60.0, seed: int = 0) -> tuple[Rim, list[ShotTruth]]:
    rng = np.random.default_rng(seed)
    rim = make_rim()
    bg = _background(rim)
    writer = cv2.VideoWriter(str(out_video), cv2.VideoWriter_fourcc(*"mp4v"), fps, (W, H))
    truths: list[ShotTruth] = []
    frame_idx = 0
    ball_r = int(round(BALL_RADIUS_CM * SCALE))

    def emit(ball_world):
        nonlocal frame_idx
        img = bg.copy()
        # simple shooter silhouette
        sx = int(rim.to_image(-spec.distance_cm - 30, 0)[0])
        cv2.rectangle(img, (sx - 25, int(rim.cy + 90 * SCALE)), (sx + 25, int(rim.cy + 230 * SCALE)), (45, 45, 55), -1)
        if ball_world is not None:
            x, y = rim.to_image(*ball_world)
            cv2.circle(img, (int(x), int(y)), ball_r, BALL_BGR, -1, cv2.LINE_AA)
            cv2.circle(img, (int(x), int(y)), ball_r, (20, 60, 140), 2, cv2.LINE_AA)
        _draw_static_front(img, rim)
        noise = rng.normal(0, 3, img.shape)
        writer.write((img.astype(np.float32) + noise).clip(0, 255).astype(np.uint8))
        frame_idx += 1

    spec = specs[0] if specs else ShotSpec(50, 5)
    for _ in range(int(1.0 * fps)):          # empty lead-in for background model
        emit(None)
    for spec in specs:
        pos, truth = shot_samples(spec, fps)
        truth.release_frame += frame_idx
        truths.append(truth)
        for p in pos:
            emit(p)
        for _ in range(int(0.7 * fps)):
            emit(None)
    writer.release()
    return rim, truths


DEFAULT_SPECS = [
    ShotSpec(52, 6),
    ShotSpec(48, -14),    # short -> front rim
    ShotSpec(55, 3),
    ShotSpec(45, 16),     # long -> back rim
    ShotSpec(50, 8),
    ShotSpec(44, -2, distance_cm=470),
    ShotSpec(58, 5, distance_cm=380),
    ShotSpec(50, -16),    # short
]


def write_truth(path: str | Path, rim: Rim, truths: list[ShotTruth]) -> None:
    Path(path).write_text(json.dumps({"rim": asdict(rim), "shots": [asdict(t) for t in truths]}, indent=2))

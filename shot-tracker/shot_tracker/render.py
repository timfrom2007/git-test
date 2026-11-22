"""Drawing helpers for the annotated video and the overlay image."""
from __future__ import annotations

import cv2
import numpy as np

from .analyze import Shot
from .geometry import Rim
from .track import TrackPoint

GREEN = (80, 200, 80)
RED = (60, 60, 230)
GRAY = (170, 170, 170)
YELLOW = (0, 220, 255)
WHITE = (255, 255, 255)


def color_for(shot: Shot):
    return {"make": GREEN, "miss": RED}.get(shot.result, GRAY)


def curve_points(shot: Shot, rim: Rim, t_from: float | None = None, t_to: float | None = None) -> np.ndarray:
    a = shot.fit_t0 if t_from is None else t_from
    b = shot.fit_t_end + 0.05 if t_to is None else t_to
    ts = np.linspace(a, b, 60)
    pts = [rim.to_image(*shot.position(t)) for t in ts]
    return np.array(pts, np.int32).reshape(-1, 1, 2)


def draw_rim(img: np.ndarray, rim: Rim) -> None:
    cv2.line(img, (int(rim.x1), int(rim.y1)), (int(rim.x2), int(rim.y2)), YELLOW, 2)
    cv2.circle(img, (int(rim.cx), int(rim.cy)), 3, YELLOW, -1)


def shot_label(shot: Shot) -> list[str]:
    res = {"make": "MAKE", "miss": "MISS", "unknown": "?"}[shot.result]
    if shot.miss_type:
        res += f" ({shot.miss_type})"
    return [
        f"#{shot.id} {res}",
        f"entry  {shot.entry_angle_deg:5.1f} deg",
        f"release{shot.release_angle_deg:5.1f} deg  {shot.release_speed_ms:4.1f} m/s",
        f"depth  {shot.depth_cm:+5.1f} cm",
        f"apex   {shot.apex_height_cm:5.0f} cm",
    ]


def draw_panel(img: np.ndarray, lines: list[str], color=WHITE, origin=(16, 16)) -> None:
    x, y = origin
    h = 24 * len(lines) + 12
    w = 300
    overlay = img.copy()
    cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, img, 0.45, 0, img)
    for i, line in enumerate(lines):
        c = color if i == 0 else WHITE
        cv2.putText(img, line, (x + 10, y + 26 + 24 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, c, 1, cv2.LINE_AA)


def annotate_frame(
    img: np.ndarray,
    frame: int,
    rim: Rim,
    shots: list[Shot],
    trail: list[TrackPoint],
    fps: float,
    hold_s: float = 2.0,
) -> np.ndarray:
    out = img.copy()
    draw_rim(out, rim)
    for p in trail:
        cv2.circle(out, (int(p.x), int(p.y)), 3, YELLOW, -1)
    current = None
    for sh in shots:
        if sh.release_frame <= frame <= sh.entry_frame + hold_s * fps:
            current = sh
    if current is not None:
        cv2.polylines(out, [curve_points(current, rim)], False, color_for(current), 2, cv2.LINE_AA)
        if frame >= current.entry_frame:
            draw_panel(out, shot_label(current), color_for(current))
    done = [s for s in shots if s.entry_frame + 0.3 * fps <= frame and s.result != "unknown"]
    makes = sum(1 for s in done if s.result == "make")
    txt = f"{makes}/{len(done)}"
    cv2.putText(out, txt, (out.shape[1] - 130, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, WHITE, 2, cv2.LINE_AA)
    return out


def overlay_image(background: np.ndarray, rim: Rim, shots: list[Shot]) -> np.ndarray:
    out = (background.astype(np.float32) * 0.6).astype(np.uint8)
    draw_rim(out, rim)
    for sh in shots:
        cv2.polylines(out, [curve_points(sh, rim)], False, color_for(sh), 2, cv2.LINE_AA)
    makes = sum(1 for s in shots if s.result == "make")
    draw_panel(out, [f"{len(shots)} shots, {makes} makes", "green = make  red = miss"], WHITE)
    return out

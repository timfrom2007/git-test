"""Turn ball tracks into shots: parabola fit, shot metrics, make/miss."""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

import numpy as np

from .geometry import (
    BALL_RADIUS_CM,
    CLEAN_WINDOW_CM,
    GRAVITY_CM_S2,
    RIM_HEIGHT_CM,
    RIM_RADIUS_CM,
)
from .track import TrackPoint

MIN_FLIGHT_POINTS = 6
MIN_SHOT_DISTANCE_CM = 100.0   # layups / rim bounces are not analyzed


@dataclass
class Shot:
    id: int
    release_frame: int
    entry_frame: int
    result: str                 # make | miss | unknown
    miss_type: str              # "" | short | long | rim_out
    release_angle_deg: float
    release_speed_ms: float
    release_height_cm: float    # above floor
    apex_height_cm: float       # above floor
    entry_angle_deg: float
    depth_cm: float             # + = past rim center (toward back rim)
    shot_distance_cm: float     # horizontal release -> rim center
    gravity_ratio: float        # fitted g / 9.81, ~1.0 means good calibration
    fit_t0: float = 0.0
    fit_x: list[float] = field(default_factory=list)   # X(t) = a*t + b
    fit_y: list[float] = field(default_factory=list)   # Y(t) = a*t^2 + b*t + c
    fit_t_end: float = 0.0
    n_points: int = 0

    def to_row(self) -> dict:
        d = asdict(self)
        for k in ("fit_x", "fit_y"):
            d.pop(k)
        return d

    def position(self, t: float) -> tuple[float, float]:
        tt = t - self.fit_t0
        return float(np.polyval(self.fit_x, tt)), float(np.polyval(self.fit_y, tt))


# --------------------------------------------------------------------------
def _fit(pts: list[TrackPoint]):
    t0 = pts[0].t
    t = np.array([p.t - t0 for p in pts])
    X = np.array([p.X for p in pts])
    Y = np.array([p.Y for p in pts])
    cx = np.polyfit(t, X, 1)
    cy = np.polyfit(t, Y, 2)
    res = np.hypot(np.polyval(cx, t) - X, np.polyval(cy, t) - Y)
    return t0, cx, cy, res


def _robust_fit(pts: list[TrackPoint], apex_idx: int):
    """Seed the fit on the descending part (apex -> rim, always free flight),
    then grow it backward point by point while points still follow the
    parabola. Points where the ball is still in the hands are left out, so
    the first kept point is the release."""
    n = len(pts)
    start = max(0, min(apex_idx - 2, n - MIN_FLIGHT_POINTS))
    _, _, _, res = _fit(pts[start:])
    thr = max(4.0, 4.0 * float(np.median(res)))
    while start > 0:
        t0, cx, cy, _ = _fit(pts[start:])
        p = pts[start - 1]
        tt = p.t - t0
        err = float(np.hypot(np.polyval(cx, tt) - p.X, np.polyval(cy, tt) - p.Y))
        if err > thr:
            break
        start -= 1
    kept = pts[start:]
    t0, cx, cy, _ = _fit(kept)
    return kept, t0, cx, cy


def _in_rim_zone(p: TrackPoint) -> bool:
    return abs(abs(p.X) - RIM_RADIUS_CM) < BALL_RADIUS_CM + 4 and abs(p.Y) < BALL_RADIUS_CM + 8


def _flight_segments(track: list[TrackPoint]) -> list[tuple[int, int, int]]:
    """(start, end, apex) indices of rising-then-falling arcs above the rim."""
    Y = [p.Y for p in track]
    n = len(track)
    segs: list[tuple[int, int, int]] = []
    i = 0
    while i < n:
        # candidate apex: local max clearly above rim
        if Y[i] > 15 and (i == 0 or Y[i] >= Y[i - 1]) and (i == n - 1 or Y[i] >= Y[i + 1]):
            s = i
            while s > 0 and Y[s - 1] <= Y[s] + 3:
                s -= 1
            e = i
            while e + 1 < n and Y[e + 1] <= Y[e] + 3 and Y[e + 1] > -BALL_RADIUS_CM and not _in_rim_zone(track[e + 1]):
                e += 1
            if e - s + 1 >= MIN_FLIGHT_POINTS:
                segs.append((s, e, i))
            i = e + 1
        else:
            i += 1
    return segs


def _classify(entry_t: float, depth: float, later: list[TrackPoint]) -> tuple[str, str]:
    window = [p for p in later if entry_t - 0.02 < p.t < entry_t + 0.8]
    through = [p for p in window if -90 < p.Y < -(BALL_RADIUS_CM + 3) and abs(p.X) < RIM_RADIUS_CM + 2]
    if through:
        return "make", ""
    if not window:
        return "unknown", ""
    if depth < -CLEAN_WINDOW_CM:
        return "miss", "short"
    if depth > CLEAN_WINDOW_CM:
        return "miss", "long"
    return "miss", "rim_out"


def estimate_time_scale(tracks: list[list[TrackPoint]]) -> float:
    """Detect videos whose timestamps don't match real time.

    A ball in free flight must fall with g = 9.81 m/s^2. If all flights in a
    video show e.g. 4x that, the video plays 2x faster than real time (sped
    up); 1/64 means a slow-motion clip exported at 1/8 speed. Returns the
    factor to multiply video time by to get real time (1.0 = no change).
    """
    ratios = []
    for tr in tracks:
        for s, e, apex in _flight_segments(tr):
            pts, _, cx, cy = _robust_fit(tr[s : e + 1], apex - s)
            if len(pts) < MIN_FLIGHT_POINTS or cy[0] >= 0:
                continue
            if abs(pts[0].X) < MIN_SHOT_DISTANCE_CM:
                continue
            ratios.append(-2 * cy[0] / GRAVITY_CM_S2)
    if len(ratios) < 2:
        return 1.0
    k = math.sqrt(float(np.median(ratios)))
    # within ~1.4x is perspective / calibration error, not a speed change
    return k if not 0.7 < k < 1.4 else 1.0


def analyze_tracks(tracks: list[list[TrackPoint]], time_scale: float = 1.0) -> list[Shot]:
    if time_scale != 1.0:
        tracks = [
            [TrackPoint(p.frame, p.t * time_scale, p.x, p.y, p.X, p.Y, p.r) for p in tr] for tr in tracks
        ]
    # Tracks that begin at the rim: the ball after rim contact / in the net,
    # when tracking broke at the rim. Used together with the shot's own track
    # to decide make/miss.
    rim_pts = [p for tr in tracks if math.hypot(tr[0].X, tr[0].Y) < 90 for p in tr]
    shots: list[Shot] = []
    for tr in tracks:
        own_and_rim = sorted({id(p): p for p in tr + rim_pts}.values(), key=lambda p: p.t)
        for s, e, apex in _flight_segments(tr):
            pts, t0, cx, cy = _robust_fit(tr[s : e + 1], apex - s)
            if len(pts) < MIN_FLIGHT_POINTS:
                continue
            a, b, c = cy
            g_ratio = -2 * a / GRAVITY_CM_S2
            if not 0.4 < g_ratio < 2.5:
                continue  # not a free-flight parabola
            vx = cx[0]
            if abs(vx) < 1:
                continue
            disc = b * b - 4 * a * c
            if disc < 0:
                continue  # never comes down to rim height
            # later root of Y(t)=0 (a < 0)
            te = (-b - math.sqrt(disc)) / (2 * a)
            tr_rel = pts[0].t - t0
            xr, yr = np.polyval(cx, tr_rel), np.polyval(cy, tr_rel)
            if abs(xr) < MIN_SHOT_DISTANCE_CM:
                continue  # arc starts at the rim: a rebound, not a shot
            xe = np.polyval(cx, te)
            direction = 1.0 if vx > 0 else -1.0
            depth = float(xe * direction)
            if abs(depth) > 150:
                continue  # not aimed at this rim
            vy_r = 2 * a * tr_rel + b
            vy_e = 2 * a * te + b
            t_apex = -b / (2 * a)
            y_apex = np.polyval(cy, t_apex)
            entry_t = t0 + te
            result, miss = _classify(entry_t, depth, [p for p in own_and_rim if p.t > pts[-1].t])
            fps_est = (pts[-1].frame - pts[0].frame) / max(1e-6, pts[-1].t - pts[0].t)
            shots.append(
                Shot(
                    id=len(shots) + 1,
                    release_frame=pts[0].frame,
                    entry_frame=int(round(entry_t * fps_est)),
                    result=result,
                    miss_type=miss,
                    release_angle_deg=math.degrees(math.atan2(vy_r, abs(vx))),
                    release_speed_ms=math.hypot(vx, vy_r) / 100,
                    release_height_cm=float(RIM_HEIGHT_CM + yr),
                    apex_height_cm=float(RIM_HEIGHT_CM + y_apex),
                    entry_angle_deg=math.degrees(math.atan2(-vy_e, abs(vx))),
                    depth_cm=depth,
                    shot_distance_cm=float(abs(xr)),
                    gravity_ratio=float(g_ratio),
                    fit_t0=t0,
                    fit_x=[float(v) for v in cx],
                    fit_y=[float(v) for v in cy],
                    fit_t_end=float(entry_t),
                    n_points=len(pts),
                )
            )
    shots.sort(key=lambda s: s.release_frame)
    for i, sh in enumerate(shots, 1):
        sh.id = i
    return shots


# --------------------------------------------------------------------------
def summarize(shots: list[Shot]) -> dict:
    if not shots:
        return {"shots": 0}
    known = [s for s in shots if s.result != "unknown"]
    makes = [s for s in known if s.result == "make"]

    def stats(vals):
        v = np.array(vals, float)
        return {"mean": round(float(v.mean()), 1), "std": round(float(v.std()), 1)}

    summary = {
        "shots": len(shots),
        "makes": len(makes),
        "fg_pct": round(100 * len(makes) / len(known), 1) if known else None,
        "entry_angle_deg": stats([s.entry_angle_deg for s in shots]),
        "release_angle_deg": stats([s.release_angle_deg for s in shots]),
        "depth_cm": stats([s.depth_cm for s in shots]),
        "apex_height_cm": stats([s.apex_height_cm for s in shots]),
        "miss_types": {k: sum(1 for s in known if s.miss_type == k) for k in ("short", "long", "rim_out")},
    }
    summary["advice"] = advice(summary)
    return summary


def advice(summary: dict) -> list[str]:
    tips: list[str] = []
    ea = summary["entry_angle_deg"]["mean"]
    dm = summary["depth_cm"]["mean"]
    ea_sd = summary["entry_angle_deg"]["std"]
    d_sd = summary["depth_cm"]["std"]
    if ea < 41:
        tips.append(f"入框角度平均 {ea}°，弧度偏平（理想約 43–47°）。試著出手角度再高一些。")
    elif ea > 50:
        tips.append(f"入框角度平均 {ea}°，弧度偏高，會需要更大的力量、距離較難控制。")
    else:
        tips.append(f"入框角度平均 {ea}°，在理想範圍內。")
    if dm < 0:
        tips.append(f"落點平均在籃框中心前 {abs(dm)} cm，偏短；理想是越過中心約 5–8 cm。")
    elif dm > 12:
        tips.append(f"落點平均在籃框中心後 {dm} cm，偏長。")
    if ea_sd > 3:
        tips.append(f"入框角度標準差 {ea_sd}°，每球弧度不太一致，先練固定的出手動作。")
    if d_sd > 8:
        tips.append(f"落點前後標準差 {d_sd} cm，距離控制的一致性有進步空間。")
    mt = summary["miss_types"]
    if mt["short"] > mt["long"] and mt["short"] >= 2:
        tips.append(f"失手中有 {mt['short']} 球是打前框（偏短）。")
    elif mt["long"] > mt["short"] and mt["long"] >= 2:
        tips.append(f"失手中有 {mt['long']} 球是打後框（偏長）。")
    return tips

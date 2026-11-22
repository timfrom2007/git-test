"""End-to-end: video file -> shots + report files."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import cv2

from .analyze import Shot, analyze_tracks, estimate_time_scale, summarize
from .detect import ColorBallDetector, YoloBallDetector
from .geometry import Rim
from .render import annotate_frame, overlay_image
from .track import BallTracker


def track_video(video: str | Path, rim: Rim, detector: str = "color", progress: bool = True):
    cap = cv2.VideoCapture(str(video))
    if not cap.isOpened():
        raise SystemExit(f"cannot open video: {video}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    det = YoloBallDetector(rim) if detector == "yolo" else ColorBallDetector(rim)
    tracker = BallTracker(rim, fps)
    first = None
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if first is None:
            first = frame.copy()
        tracker.update(i, det(frame))
        i += 1
        if progress and i % 200 == 0:
            print(f"  tracking {i}/{total} frames", flush=True)
    cap.release()
    return tracker.finish(), fps, first


def write_annotated(video, out_path, rim: Rim, shots: list[Shot], tracks, fps: float) -> None:
    cap = cv2.VideoCapture(str(video))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
    # only draw tracks that were above the rim at some point (the ball in
    # flight), not every orange blob that was tracked
    by_frame = {p.frame: p for tr in tracks if max(q.Y for q in tr) > 0 for p in tr}
    trail_len = int(fps * 0.6)
    i = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        trail = [by_frame[f] for f in range(max(0, i - trail_len), i + 1) if f in by_frame]
        writer.write(annotate_frame(frame, i, rim, shots, trail, fps))
        i += 1
    cap.release()
    writer.release()


def run(
    video,
    rim: Rim,
    out_dir,
    detector: str = "color",
    annotate: bool = True,
    speed: float | None = None,
) -> tuple[list[Shot], dict]:
    """speed: playback speed of the video relative to real time (2 = sped up
    2x, 0.125 = slow motion at 1/8). None = detect it from gravity."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    print(f"analyzing {video}")
    tracks, fps, first = track_video(video, rim, detector)
    time_scale = speed if speed else estimate_time_scale(tracks)
    if time_scale != 1.0:
        how = "given" if speed else "detected from gravity"
        print(f"  video speed x{time_scale:.2f} vs real time ({how}); correcting")
    shots = analyze_tracks(tracks, time_scale)
    summary = summarize(shots)
    summary["fps"] = fps
    summary["video_speed"] = round(time_scale, 3)

    with open(out / "shots.csv", "w", newline="", encoding="utf-8") as f:
        rows = [s.to_row() for s in shots]
        if rows:
            wr = csv.DictWriter(f, fieldnames=list(rows[0]))
            wr.writeheader()
            wr.writerows(rows)
    (out / "report.json").write_text(
        json.dumps({"summary": summary, "shots": [s.to_row() for s in shots]}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    if first is not None:
        cv2.imwrite(str(out / "overlay.png"), overlay_image(first, rim, shots))
    if annotate:
        write_annotated(video, out / "annotated.mp4", rim, shots, tracks, fps)
    return shots, summary

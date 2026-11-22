"""Command line entry point.

    python -m shot_tracker synth   --out demo/                 # make a test video
    python -m shot_tracker pick-rim VIDEO --out rim.json       # click rim edges
    python -m shot_tracker analyze VIDEO --rim rim.json --out results/
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .geometry import Rim


def _print_report(shots, summary) -> None:
    print()
    print(f"{'#':>3} {'result':<14} {'release°':>8} {'speed':>6} {'entry°':>7} {'depth':>7} {'apex':>6}")
    for s in shots:
        res = s.result + (f"/{s.miss_type}" if s.miss_type else "")
        print(
            f"{s.id:>3} {res:<14} {s.release_angle_deg:8.1f} {s.release_speed_ms:6.2f} "
            f"{s.entry_angle_deg:7.1f} {s.depth_cm:+7.1f} {s.apex_height_cm:6.0f}"
        )
    if summary.get("shots"):
        print(f"\n命中 {summary['makes']}/{summary['shots']}  ({summary['fg_pct']}%)")
        for tip in summary["advice"]:
            print(" -", tip)


def cmd_synth(a) -> None:
    from .synth import DEFAULT_SPECS, generate, write_truth

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rim, truths = generate(out / "synthetic.mp4", DEFAULT_SPECS, fps=a.fps)
    rim.save(out / "rim.json")
    write_truth(out / "truth.json", rim, truths)
    print(f"wrote {out/'synthetic.mp4'}, {out/'rim.json'}, {out/'truth.json'}")


def cmd_pick_rim(a) -> None:
    import cv2

    cap = cv2.VideoCapture(a.video)
    cap.set(cv2.CAP_PROP_POS_FRAMES, a.frame)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit("cannot read frame")
    pts: list[tuple[int, int]] = []
    win = "click LEFT edge then RIGHT edge of the rim (Enter = save, r = reset, Esc = quit)"

    def on_click(event, x, y, *_):
        if event == cv2.EVENT_LBUTTONDOWN and len(pts) < 2:
            pts.append((x, y))

    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win, on_click)
    while True:
        view = frame.copy()
        for p in pts:
            cv2.circle(view, p, 4, (0, 255, 255), -1)
        if len(pts) == 2:
            cv2.line(view, pts[0], pts[1], (0, 255, 255), 2)
        cv2.imshow(win, view)
        k = cv2.waitKey(20) & 0xFF
        if k == 27:
            raise SystemExit("cancelled")
        if k == ord("r"):
            pts.clear()
        if k in (13, 10) and len(pts) == 2:
            break
    cv2.destroyAllWindows()
    rim = Rim(*pts[0], *pts[1])
    rim.save(a.out)
    print(f"saved {a.out}: {rim}")


def cmd_analyze(a) -> None:
    from .pipeline import run

    if a.rim_points:
        rim = Rim.parse(a.rim_points)
    elif a.rim:
        rim = Rim.load(a.rim)
    else:
        raise SystemExit("need --rim rim.json or --rim-points x1,y1,x2,y2")
    shots, summary = run(a.video, rim, a.out, detector=a.detector, annotate=not a.no_video)
    _print_report(shots, summary)
    print(f"\noutputs in {a.out}/")


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="shot_tracker", description="Basketball shot trajectory analysis")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("synth", help="generate a synthetic test video")
    s.add_argument("--out", default="demo")
    s.add_argument("--fps", type=float, default=60.0)
    s.set_defaults(func=cmd_synth)

    s = sub.add_parser("pick-rim", help="click the rim edges on a frame (needs a display)")
    s.add_argument("video")
    s.add_argument("--out", default="rim.json")
    s.add_argument("--frame", type=int, default=0)
    s.set_defaults(func=cmd_pick_rim)

    s = sub.add_parser("analyze", help="analyze a side-view shooting video")
    s.add_argument("video")
    s.add_argument("--rim", help="rim.json from pick-rim")
    s.add_argument("--rim-points", help="x1,y1,x2,y2 of rim left/right edge")
    s.add_argument("--out", default="results")
    s.add_argument("--detector", choices=["color", "yolo"], default="color")
    s.add_argument("--no-video", action="store_true", help="skip annotated.mp4")
    s.set_defaults(func=cmd_analyze)

    a = p.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()

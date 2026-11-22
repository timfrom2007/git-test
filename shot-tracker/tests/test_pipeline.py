import json
import math

import pytest

from shot_tracker.analyze import analyze_tracks, summarize
from shot_tracker.geometry import Rim
from shot_tracker.pipeline import run
from shot_tracker.synth import ShotSpec, generate, make_rim, shot_samples
from shot_tracker.track import TrackPoint

FPS = 60.0


def _tracks_from_spec(spec: ShotSpec, rim: Rim, noise_cm: float = 0.0, seed: int = 0):
    import numpy as np

    rng = np.random.default_rng(seed)
    pos, truth = shot_samples(spec, FPS)
    pts = []
    for i, (X, Y) in enumerate(pos):
        X += rng.normal(0, noise_cm)
        Y += rng.normal(0, noise_cm)
        x, y = rim.to_image(X, Y)
        pts.append(TrackPoint(i, i / FPS, x, y, X, Y, 24))
    return [pts], truth


def test_rim_world_roundtrip():
    rim = Rim(100, 200, 191.44, 200)
    assert rim.px_per_cm == pytest.approx(2.0)
    X, Y = rim.to_world(*rim.to_image(-123.0, 45.0))
    assert (X, Y) == pytest.approx((-123.0, 45.0))


@pytest.mark.parametrize(
    "spec",
    [ShotSpec(52, 6), ShotSpec(45, -15), ShotSpec(58, 14, distance_cm=380), ShotSpec(47, 0, distance_cm=600)],
)
def test_metrics_from_clean_track(spec):
    rim = make_rim()
    tracks, truth = _tracks_from_spec(spec, rim)
    shots = analyze_tracks(tracks)
    assert len(shots) == 1
    s = shots[0]
    assert s.result == truth.result
    assert s.release_angle_deg == pytest.approx(truth.release_angle_deg, abs=0.5)
    assert s.entry_angle_deg == pytest.approx(truth.entry_angle_deg, abs=0.5)
    assert s.depth_cm == pytest.approx(truth.depth_cm, abs=1.0)
    assert s.release_speed_ms == pytest.approx(truth.release_speed_ms, abs=0.05)
    assert s.gravity_ratio == pytest.approx(1.0, abs=0.05)


def test_metrics_with_detection_noise():
    rim = make_rim()
    tracks, truth = _tracks_from_spec(ShotSpec(50, 5), rim, noise_cm=1.5, seed=3)
    s = analyze_tracks(tracks)[0]
    assert s.entry_angle_deg == pytest.approx(truth.entry_angle_deg, abs=1.5)
    assert s.depth_cm == pytest.approx(truth.depth_cm, abs=3.0)


def test_shot_from_right_side_is_mirrored():
    rim = make_rim()
    tracks, truth = _tracks_from_spec(ShotSpec(50, -14), rim)
    mirrored = [[TrackPoint(p.frame, p.t, 0, 0, -p.X, p.Y, p.r) for p in tracks[0]]]
    s = analyze_tracks(mirrored)[0]
    assert s.depth_cm == pytest.approx(-14, abs=1.0)
    assert s.miss_type == "short"


def test_advice_flags_flat_shots():
    rim = make_rim()
    shots = []
    for d in (-14, -15, -13):
        tracks, _ = _tracks_from_spec(ShotSpec(42, d, distance_cm=430), rim)
        shots += analyze_tracks(tracks)
    summ = summarize(shots)
    assert summ["fg_pct"] == 0
    assert summ["miss_types"]["short"] == 3
    assert any("弧度偏平" in t for t in summ["advice"])


def test_end_to_end_video(tmp_path):
    specs = [ShotSpec(52, 6), ShotSpec(48, -14), ShotSpec(45, 16)]
    rim, truths = generate(tmp_path / "v.mp4", specs, fps=FPS)
    shots, summary = run(tmp_path / "v.mp4", rim, tmp_path / "out", annotate=False)
    assert [s.result for s in shots] == [t.result for t in truths]
    for s, t in zip(shots, truths):
        assert s.entry_angle_deg == pytest.approx(t.entry_angle_deg, abs=1.5)
        assert s.depth_cm == pytest.approx(t.depth_cm, abs=3.0)
        assert abs(s.release_frame - t.release_frame) <= 2
    report = json.loads((tmp_path / "out" / "report.json").read_text(encoding="utf-8"))
    assert report["summary"]["shots"] == 3
    assert (tmp_path / "out" / "overlay.png").exists()
    assert not math.isnan(summary["depth_cm"]["mean"])


@pytest.mark.parametrize("speed", [2.0, 0.125])
def test_detects_sped_up_or_slow_motion_video(speed):
    """A video played at `speed` x real time shows gravity scaled by speed^2;
    the analysis should detect that and still produce correct metrics."""
    from shot_tracker.analyze import estimate_time_scale

    rim = make_rim()
    tracks, truths = [], []
    for i, spec in enumerate([ShotSpec(52, 6), ShotSpec(48, -14), ShotSpec(55, 3)]):
        (tr,), truth = _tracks_from_spec(spec, rim)
        off = i * 400
        tracks.append([TrackPoint(p.frame + off, (p.t + off / FPS) / speed, p.x, p.y, p.X, p.Y, p.r) for p in tr])
        truths.append(truth)
    k = estimate_time_scale(tracks)
    assert k == pytest.approx(speed, rel=0.02)
    shots = analyze_tracks(tracks, time_scale=k)
    assert [s.result for s in shots] == [t.result for t in truths]
    for s, t in zip(shots, truths):
        assert s.release_speed_ms == pytest.approx(t.release_speed_ms, abs=0.1)
        assert s.entry_angle_deg == pytest.approx(t.entry_angle_deg, abs=0.5)


def test_normal_speed_video_is_not_rescaled():
    from shot_tracker.analyze import estimate_time_scale

    rim = make_rim()
    tracks = []
    for i, spec in enumerate([ShotSpec(52, 6), ShotSpec(48, -14)]):
        (tr,), _ = _tracks_from_spec(spec, rim)
        tracks.append([TrackPoint(p.frame + i * 400, p.t + i * 400 / FPS, p.x, p.y, p.X, p.Y, p.r) for p in tr])
    assert estimate_time_scale(tracks) == 1.0

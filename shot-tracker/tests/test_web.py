import time

import pytest
from fastapi.testclient import TestClient

from shot_tracker.synth import ShotSpec, generate
from shot_tracker.web.app import create_app


def _wait(client, sid, until, timeout=120):
    t0 = time.time()
    while time.time() - t0 < timeout:
        meta = client.get(f"/api/sessions/{sid}").json()
        if meta["status"] in until:
            return meta
        time.sleep(0.2)
    raise AssertionError(f"timeout, last status {meta['status']}")


@pytest.fixture()
def client(tmp_path):
    with TestClient(create_app(tmp_path / "data")) as c:
        yield c


def test_full_flow(client, tmp_path):
    rim, truths = generate(tmp_path / "practice.mp4", [ShotSpec(52, 6), ShotSpec(48, -14)], fps=60)

    with open(tmp_path / "practice.mp4", "rb") as f:
        r = client.post("/api/sessions", files={"file": ("practice.mp4", f, "video/mp4")})
    assert r.status_code == 200, r.text
    sid = r.json()["id"]

    meta = _wait(client, sid, {"ready", "error"})
    assert meta["status"] == "ready", meta
    assert meta["video"]["width"] == 1280 and meta["video"]["fps"] == 60

    frame = client.get(f"/api/sessions/{sid}/frame.jpg", params={"t": 0.5})
    assert frame.status_code == 200 and frame.headers["content-type"] == "image/jpeg"

    r = client.post(f"/api/sessions/{sid}/analyze", json={"rim": [rim.x1, rim.y1, rim.x2, rim.y2]})
    assert r.status_code == 200, r.text
    meta = _wait(client, sid, {"done", "error"})
    assert meta["status"] == "done", meta.get("error")
    assert meta["summary"]["shots"] == 2 and meta["summary"]["makes"] == 1

    report = client.get(f"/api/sessions/{sid}/files/report.json").json()
    assert [s["result"] for s in report["shots"]] == [t.result for t in truths]
    video = client.get(f"/api/sessions/{sid}/files/annotated.mp4")
    assert video.status_code == 200 and len(video.content) > 10_000
    # H.264 so it plays in Safari
    assert b"avc1" in video.content[:200_000]

    assert [s["id"] for s in client.get("/api/sessions").json()] == [sid]
    assert client.delete(f"/api/sessions/{sid}").status_code == 200
    assert client.get(f"/api/sessions/{sid}").status_code == 404


def test_rejects_bad_input(client):
    r = client.post("/api/sessions", files={"file": ("notes.txt", b"hello", "text/plain")})
    assert r.status_code == 400
    assert client.get("/api/sessions/../../etc").status_code == 404
    assert client.get("/api/sessions/zzzzzzzzzzzz").status_code == 404


def test_broken_video_reports_error(client):
    r = client.post("/api/sessions", files={"file": ("broken.mp4", b"not a video", "video/mp4")})
    sid = r.json()["id"]
    meta = _wait(client, sid, {"ready", "error"})
    assert meta["status"] == "error" and "轉檔失敗" in meta["error"]


def test_result_files_are_whitelisted(client, tmp_path):
    generate(tmp_path / "v.mp4", [ShotSpec(52, 6)], fps=30)
    with open(tmp_path / "v.mp4", "rb") as f:
        sid = client.post("/api/sessions", files={"file": ("v.mp4", f, "video/mp4")}).json()["id"]
    _wait(client, sid, {"ready"})
    assert client.get(f"/api/sessions/{sid}/files/meta.json").status_code == 404
    assert client.get(f"/api/sessions/{sid}/files/..%2Fmeta.json").status_code == 404

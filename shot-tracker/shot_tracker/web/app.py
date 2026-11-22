"""Phase 1 web app: upload a video from the phone, mark the rim, get results.

Run:  python -m shot_tracker serve
Then open the printed http://<pc-ip>:8000 address on the iPhone (same Wi-Fi).

Each upload is a "session" stored in DATA_DIR/<id>/:
    original.<ext>   uploaded file
    video.mp4        normalized H.264 (what gets analyzed)
    meta.json        status, progress, rim, timestamps
    results/         report.json, shots.csv, overlay.png, annotated.mp4
"""
from __future__ import annotations

import json
import os
import re
import shutil
import threading
import time
import traceback
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import cv2
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ..geometry import Rim
from ..media import normalize
from ..pipeline import run

STATIC_DIR = Path(__file__).parent / "static"
RESULT_FILES = {"report.json", "shots.csv", "overlay.png", "annotated.mp4"}
VIDEO_EXTS = {".mp4", ".mov", ".m4v", ".avi", ".mkv", ".webm"}
ID_RE = re.compile(r"^[0-9a-f]{12}$")


class AnalyzeRequest(BaseModel):
    rim: list[float] = Field(min_length=4, max_length=4, description="x1,y1,x2,y2 in video.mp4 pixels")
    speed: float | None = Field(default=None, gt=0, description="playback speed vs real time; None = auto")


class Store:
    """File-based session storage; meta.json writes are serialized by a lock."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def dir(self, sid: str) -> Path:
        if not ID_RE.match(sid):
            raise HTTPException(404, "no such session")
        d = self.root / sid
        if not (d / "meta.json").exists():
            raise HTTPException(404, "no such session")
        return d

    def create(self, name: str) -> tuple[str, Path]:
        sid = uuid.uuid4().hex[:12]
        d = self.root / sid
        d.mkdir()
        self.write(sid, {"id": sid, "name": name, "created": time.time(), "status": "uploaded"}, d)
        return sid, d

    def read(self, sid: str) -> dict:
        return json.loads((self.dir(sid) / "meta.json").read_text(encoding="utf-8"))

    def write(self, sid: str, meta: dict, d: Path | None = None) -> None:
        d = d or self.root / sid
        tmp = d / "meta.json.tmp"
        tmp.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(d / "meta.json")

    def update(self, sid: str, **fields) -> dict:
        with self._lock:
            meta = self.read(sid)
            meta.update(fields)
            self.write(sid, meta)
            return meta

    def list(self) -> list[dict]:
        out = []
        for d in self.root.iterdir():
            f = d / "meta.json"
            if f.exists():
                try:
                    out.append(json.loads(f.read_text(encoding="utf-8")))
                except (OSError, json.JSONDecodeError):
                    continue
        return sorted(out, key=lambda m: m.get("created", 0), reverse=True)


def create_app(data_dir: str | Path | None = None) -> FastAPI:
    store = Store(Path(data_dir or os.environ.get("SHOT_TRACKER_DATA", "data")).resolve())
    jobs = ThreadPoolExecutor(max_workers=1)  # one video at a time; analysis is CPU-bound
    app = FastAPI(title="Shot Tracker")
    app.state.store = store
    # jobs don't survive a restart: don't leave sessions spinning forever
    for meta in store.list():
        if meta.get("status") in ("uploaded", "preparing", "queued", "analyzing"):
            store.update(meta["id"], status="error", error="伺服器重新啟動，處理被中斷，請重試")
    app.state.jobs = jobs

    # ---- background jobs ----------------------------------------------
    def prepare(sid: str, src: Path) -> None:
        d = store.root / sid
        try:
            store.update(sid, status="preparing")
            normalize(src, d / "video.mp4")
            cap = cv2.VideoCapture(str(d / "video.mp4"))
            info = {
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "fps": round(cap.get(cv2.CAP_PROP_FPS), 2),
                "frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            }
            cap.release()
            if not info["frames"]:
                raise RuntimeError("影片裡沒有可讀取的畫面")
            info["duration"] = round(info["frames"] / (info["fps"] or 30), 2)
            store.update(sid, status="ready", video=info)
        except Exception as e:  # noqa: BLE001 - report any failure to the UI
            traceback.print_exc()
            store.update(sid, status="error", error=f"影片轉檔失敗：{e}")

    def analyze(sid: str, req: AnalyzeRequest) -> None:
        d = store.root / sid
        weights = {"tracking": (0.0, 0.7), "rendering": (0.7, 0.3)}

        def on_progress(stage: str, frac: float) -> None:
            base, span = weights[stage]
            store.update(sid, progress=round(base + span * frac, 3), stage=stage)

        try:
            store.update(sid, status="analyzing", progress=0.0, stage="tracking", error=None)
            rim = Rim(*req.rim)
            res = d / "results"
            if res.exists():
                shutil.rmtree(res)
            _, summary = run(d / "video.mp4", rim, res, speed=req.speed, on_progress=on_progress, log=lambda *_: None)
            store.update(sid, status="done", progress=1.0, summary=summary, analyzed=time.time())
        except Exception as e:  # noqa: BLE001
            traceback.print_exc()
            store.update(sid, status="error", error=f"分析失敗：{e}")

    # ---- API ------------------------------------------------------------
    @app.get("/api/sessions")
    def list_sessions() -> list[dict]:
        return store.list()

    @app.post("/api/sessions")
    def upload(file: UploadFile = File(...)) -> dict:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in VIDEO_EXTS:
            raise HTTPException(400, f"不支援的檔案格式：{ext or '未知'}")
        sid, d = store.create(Path(file.filename).stem[:80])
        src = d / f"original{ext}"
        with open(src, "wb") as f:
            shutil.copyfileobj(file.file, f, length=1 << 20)
        jobs.submit(prepare, sid, src)
        return store.read(sid)

    @app.get("/api/sessions/{sid}")
    def get_session(sid: str) -> dict:
        return store.read(sid)

    @app.delete("/api/sessions/{sid}")
    def delete_session(sid: str) -> dict:
        meta = store.read(sid)
        if meta["status"] in ("preparing", "analyzing"):
            raise HTTPException(409, "處理中，請稍後再刪除")
        shutil.rmtree(store.dir(sid))
        return {"deleted": sid}

    @app.get("/api/sessions/{sid}/frame.jpg")
    def frame(sid: str, t: float = 0.0) -> Response:
        d = store.dir(sid)
        if not (d / "video.mp4").exists():
            raise HTTPException(409, "影片還在處理中")
        cap = cv2.VideoCapture(str(d / "video.mp4"))
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, t) * 1000)
        ok, img = cap.read()
        cap.release()
        if not ok:
            raise HTTPException(404, "讀不到這個時間點的畫面")
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return Response(buf.tobytes(), media_type="image/jpeg", headers={"Cache-Control": "no-store"})

    @app.post("/api/sessions/{sid}/analyze")
    def start_analysis(sid: str, req: AnalyzeRequest) -> dict:
        meta = store.read(sid)
        if meta["status"] not in ("ready", "done", "error") or "video" not in meta:
            raise HTTPException(409, "影片還沒準備好")
        x1, y1, x2, y2 = req.rim
        if abs(x2 - x1) < 5:
            raise HTTPException(400, "籃框的左右兩點太近了")
        meta = store.update(sid, status="queued", rim=req.rim, speed=req.speed, progress=0.0)
        jobs.submit(analyze, sid, req)
        return meta

    @app.get("/api/sessions/{sid}/files/{name}")
    def result_file(sid: str, name: str) -> FileResponse:
        if name not in RESULT_FILES:
            raise HTTPException(404, "no such file")
        f = store.dir(sid) / "results" / name
        if not f.exists():
            raise HTTPException(404, "還沒有結果")
        return FileResponse(f, headers={"Cache-Control": "no-cache"})

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    return app

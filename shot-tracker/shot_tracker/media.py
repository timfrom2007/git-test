"""Video conversion with the ffmpeg binary bundled by imageio-ffmpeg.

iPhone videos are usually HEVC .mov files with rotation metadata, and the
mp4v files OpenCV writes don't play in Safari. Everything going in is
normalized to H.264 mp4 (rotation applied, width capped) and everything
coming out is re-encoded to browser-friendly H.264.
"""
from __future__ import annotations

import subprocess
from pathlib import Path


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg
    except ImportError as e:  # pragma: no cover
        raise SystemExit("needs: pip install imageio-ffmpeg") from e
    return imageio_ffmpeg.get_ffmpeg_exe()


def _run(args: list[str]) -> None:
    proc = subprocess.run([ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {proc.stderr.strip()[-500:]}")


def normalize(src: str | Path, dst: str | Path, max_width: int = 1280) -> None:
    """Any input video -> H.264 mp4, rotation applied, width <= max_width,
    original frame rate kept, audio dropped."""
    _run([
        "-i", str(src),
        "-vf", f"scale='min({max_width},iw)':-2",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart",
        str(dst),
    ])


def to_browser_mp4(src: str | Path, dst: str | Path) -> None:
    _run([
        "-i", str(src),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        "-an", "-movflags", "+faststart",
        str(dst),
    ])

"""Ball detectors.

ColorBallDetector  - no ML, orange color + motion. Works for a fixed camera and
                     is the default for Phase 0.
YoloBallDetector   - optional, needs `pip install ultralytics` (AGPL license,
                     fine for personal use; see docs/plan.md before shipping).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import cv2
import numpy as np

from .geometry import BALL_RADIUS_CM, Rim


@dataclass
class Detection:
    x: float      # image px
    y: float
    r: float      # radius px
    score: float  # 0..1


class ColorBallDetector:
    def __init__(
        self,
        rim: Rim,
        hsv_lo: tuple[int, int, int] = (3, 80, 50),
        hsv_hi: tuple[int, int, int] = (25, 255, 255),
        use_motion: bool = True,
    ) -> None:
        self.rim = rim
        self.hsv_lo = np.array(hsv_lo, np.uint8)
        self.hsv_hi = np.array(hsv_hi, np.uint8)
        self.expected_r = BALL_RADIUS_CM * rim.px_per_cm
        self.use_motion = use_motion
        self._bg = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=32, detectShadows=False)
        k = max(3, int(self.expected_r / 6) | 1)
        self._kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))

    def _rim_mask(self, shape: tuple[int, int]) -> np.ndarray:
        """Mask that hides the (also orange) rim itself."""
        mask = np.full(shape, 255, np.uint8)
        pad = int(self.rim.width_px * 0.08) + 2
        thick = max(3, int(self.rim.px_per_cm * 3))
        cv2.line(
            mask,
            (int(self.rim.x1) - pad, int(self.rim.y1)),
            (int(self.rim.x2) + pad, int(self.rim.y2)),
            0,
            thick,
        )
        return mask

    def __call__(self, frame: np.ndarray) -> list[Detection]:
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, self.hsv_lo, self.hsv_hi)
        if self.use_motion:
            motion = self._bg.apply(frame)
            motion = cv2.dilate(motion, self._kernel, iterations=2)
            mask = cv2.bitwise_and(mask, motion)
        mask = cv2.bitwise_and(mask, self._rim_mask(mask.shape))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self._kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self._kernel)

        out: list[Detection] = []
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        r0 = self.expected_r
        for c in contours:
            area = cv2.contourArea(c)
            if area < math.pi * (0.35 * r0) ** 2:
                continue
            (x, y), r = cv2.minEnclosingCircle(c)
            if not (0.45 * r0 <= r <= 1.7 * r0):
                continue
            fill = area / (math.pi * r * r + 1e-6)   # 1.0 for a perfect disc
            size = math.exp(-((r / r0 - 1) ** 2) / 0.15)
            score = float(min(1.0, fill) * size)
            if score > 0.2:
                out.append(Detection(float(x), float(y), float(r), score))
        out.sort(key=lambda d: d.score, reverse=True)
        return out


class YoloBallDetector:
    """COCO 'sports ball' (class 32) via ultralytics YOLO."""

    def __init__(self, rim: Rim, model: str = "yolo11n.pt", conf: float = 0.25) -> None:
        try:
            from ultralytics import YOLO  # type: ignore
        except ImportError as e:  # pragma: no cover
            raise SystemExit("YOLO detector needs: pip install ultralytics") from e
        self.model = YOLO(model)
        self.conf = conf
        self.rim = rim

    def __call__(self, frame: np.ndarray) -> list[Detection]:  # pragma: no cover
        res = self.model.predict(frame, classes=[32], conf=self.conf, verbose=False)[0]
        out = []
        for box, conf in zip(res.boxes.xyxy.tolist(), res.boxes.conf.tolist()):
            x1, y1, x2, y2 = box
            out.append(Detection((x1 + x2) / 2, (y1 + y2) / 2, (x2 - x1 + y2 - y1) / 4, float(conf)))
        out.sort(key=lambda d: d.score, reverse=True)
        return out

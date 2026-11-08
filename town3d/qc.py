"""Independent Quality Control stage.

Uses OpenCV (opencv-python-headless) to inspect rendered frames *after* the
renderer has produced them, deliberately as a separate, independent check
rather than trusting the renderer's own idea of "it worked". This sandbox's
OpenCV build cannot decode mp4 containers (its ffmpeg video-I/O backend
needs system libavcodec/libavformat .so files this image has none of, and
pip cannot install system libraries here) -- so QC operates on in-memory
RGB frame arrays (numpy, uint8, HxWx3) captured straight out of the
renderer, before they are handed to ffmpeg for encoding. That sidesteps the
broken decode path entirely and is actually more useful: it catches a bad
frame before it is ever encoded.

Metrics computed per frame, all real pixel statistics (no heuristics that
pretend to "see" the 3D content semantically):
  - mean_brightness   : grayscale mean (0-255)
  - contrast_std       : grayscale standard deviation
  - sharpness_laplacian: variance of the Laplacian (classic focus/blur proxy)
  - caption_yellow_px  : count of near-pure-yellow pixels in the caption
                         safe-zone band (sanity check that a caption is
                         actually burned in, not just drawn off-canvas)

Thresholds below were calibrated empirically against this project's own
flat-shaded low-poly renders (see town3d/README.md Phase 6 test log) -- they
are NOT generic "any video" thresholds and will need re-tuning for a
different visual style (e.g. noisy/textured renders will have much higher
baseline Laplacian variance).
"""
from dataclasses import dataclass, field

import numpy as np
import cv2


@dataclass
class FrameReport:
    index: int
    mean_brightness: float
    contrast_std: float
    sharpness_laplacian: float
    caption_yellow_px: int
    flags: list = field(default_factory=list)


# Calibrated against Skyline Town's flat-shaded style (see README log).
TOO_DARK = 8.0
TOO_BRIGHT = 248.0
MIN_CONTRAST = 3.0          # near-solid-color frame (e.g. camera stuck in geometry)
MIN_SHARPNESS = 0.5         # near-zero => totally uniform/blank frame


def analyze_frame(rgb: np.ndarray, index: int = 0, expect_caption: bool = False) -> FrameReport:
    assert rgb.ndim == 3 and rgb.shape[2] == 3, "expected HxWx3 RGB uint8 array"
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    brightness = float(gray.mean())
    contrast = float(gray.std())
    sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    h, w, _ = rgb.shape
    band = rgb[int(h * 0.55):int(h * 0.80), :, :]
    yellow_mask = (band[:, :, 0] > 190) & (band[:, :, 1] > 160) & (band[:, :, 2] < 120)
    yellow_px = int(yellow_mask.sum())

    flags = []
    if brightness < TOO_DARK:
        flags.append("too_dark")
    if brightness > TOO_BRIGHT:
        flags.append("too_bright")
    if contrast < MIN_CONTRAST:
        flags.append("near_blank_frame")
    if sharpness < MIN_SHARPNESS:
        flags.append("degenerate_frame")
    if expect_caption and yellow_px < 20:
        flags.append("caption_missing")

    return FrameReport(index, brightness, contrast, sharpness, yellow_px, flags)


def summarize(reports: list) -> dict:
    n = len(reports)
    failed = [r for r in reports if r.flags]
    return {
        "frames_checked": n,
        "frames_failed": len(failed),
        "pass": len(failed) == 0,
        "avg_brightness": round(sum(r.mean_brightness for r in reports) / n, 2) if n else 0,
        "avg_contrast": round(sum(r.contrast_std for r in reports) / n, 2) if n else 0,
        "avg_sharpness": round(sum(r.sharpness_laplacian for r in reports) / n, 2) if n else 0,
        "failed_frame_indices": [r.index for r in failed][:20],
        "failed_frame_flags": sorted({f for r in failed for f in r.flags}),
    }

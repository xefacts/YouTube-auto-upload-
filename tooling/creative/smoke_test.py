#!/usr/bin/env python3
"""Offline smoke test: local source extraction -> procedural motion -> MoviePy MP4.

No network fetches, generation services, uploads, or copyrighted reference media.
"""
from pathlib import Path
import cv2
import numpy as np
import trafilatura
from moviepy import VideoClip

root = Path(__file__).resolve().parents[2]
out = root / 'work' / 'creative_smoke.mp4'
out.parent.mkdir(parents=True, exist_ok=True)
text = trafilatura.extract(
    '<html><body><article><h1>Fictional preview</h1>'
    '<p>This original test sentence exists only to check local extraction.</p>'
    '</article></body></html>'
)
assert text and 'original test sentence' in text

def frame(t):
    arr = np.zeros((128, 72, 3), dtype=np.uint8)
    arr[:] = (24, 42, 54)
    cv2.circle(arr, (int(12 + 40 * t), 64), 12, (220, 160, 70), -1)
    return arr

clip = VideoClip(frame_function=frame, duration=0.5)
clip.write_videofile(str(out), fps=10, codec='libx264', audio=False, logger=None)
clip.close()
assert out.stat().st_size > 1000
print('PASS local extraction, OpenCV procedural motion, MoviePy H.264:', out)

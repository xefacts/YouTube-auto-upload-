#!/usr/bin/env python3
"""Verify a downloaded blender-render artifact: frames present, mp4 valid,
technical QC stats (no vision — pure pixel stats, town3d/qc.py conventions).
Usage: python verify_render.py <artifact_dir>
"""
import json, sys, glob, os
import numpy as np
from PIL import Image

d = sys.argv[1]
frames = sorted(glob.glob(os.path.join(d, "frame_*.png")))
mp4 = os.path.join(d, "sample.mp4")
print(f"frames: {len(frames)}  mp4: {os.path.exists(mp4)} ({os.path.getsize(mp4)//1024} KB)" if os.path.exists(mp4) else f"frames: {len(frames)}  mp4: MISSING")
rep = os.path.join(d, "render_report.json")
if os.path.exists(rep):
    print(json.dumps(json.load(open(rep)), indent=1))

TOO_DARK, TOO_BRIGHT, MIN_CONTRAST = 8.0, 248.0, 3.0
stats = []
for f in frames:
    a = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32)
    g = a.mean(axis=2)
    stats.append((g.mean(), g.std(), a.shape))

if stats:
    means = [s[0] for s in stats]; stds = [s[1] for s in stats]
    flags = []
    for i, (m, s, _) in enumerate(stats):
        if m < TOO_DARK: flags.append((i, "too_dark"))
        if m > TOO_BRIGHT: flags.append((i, "too_bright"))
        if s < MIN_CONTRAST: flags.append((i, "near_blank"))
    print(f"\nQC over {len(stats)} frames @ {stats[0][2][1]}x{stats[0][2][0]}:")
    print(f"  brightness mean {np.mean(means):.1f} (min {np.min(means):.1f} max {np.max(means):.1f})")
    print(f"  contrast std mean {np.mean(stds):.1f}")
    print(f"  flags: {flags if flags else 'NONE'}")
    print(f"  PASS = {not flags}")

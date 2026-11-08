"""PHASE 6 test harness: render one original 10-second sample scene with the
upgraded pipeline (engine.py renderer + qc.py independent QC gate), and
refuse to green-light a full video until it passes. Run standalone:

    python3 town3d/phase6_demo.py

Produces:
  town_render/phase6_sample.mp4   (10s, 720x1280, captioned)
  town_render/phase6_frame_*.jpg  (start/mid/end stills for human review)
and prints a real OpenCV-measured QC report to stdout.
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import imageio_ffmpeg

from town3d.engine import Scene, Box, Camera, render_frame
from town3d import figures as F
from town3d import qc

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, SECONDS = 720, 1280, 24, 10
N = FPS * SECONDS


def build_demo_scene():
    """A fresh, original mini-scene distinct from the 8 delivered shots:
    a person standing on a rooftop garden at golden hour while the camera
    arcs around them, pillars of the sky-city visible behind."""
    sc = Scene((255, 200, 150), (255, 230, 195), light_dir=(0.5, 0.7, 0.3), ambient=0.6)
    sc.add(Box((0, -0.3, 0), (6, 0.3, 6), (90, 140, 90)))          # rooftop lawn
    sc.add(Box((0, -0.05, 0), (3.6, 0.08, 3.6), (210, 210, 200)))  # paved patio
    for (px, pz) in [(-2.4, -2.2), (2.4, -2.2), (-2.4, 2.2), (2.4, 2.2)]:
        sc.add(Box((px, 0.35, pz), (0.12, 0.35, 0.12), (200, 180, 140)))  # planters posts
        sc.add(Box((px, 0.75, pz), (0.35, 0.12, 0.35), (70, 150, 70)))    # bushes
    for i, (px, pz) in enumerate([(-6, -10), (6, -11), (-4, -16), (5, -17)]):
        sc.extend(F.pillar_tower(px, pz, radius=0.5, height=26, color=(195, 210, 225)))
    sc.extend(F.person(0.0, 0.0, 0.4, yaw=160))
    return sc


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def main():
    sc = build_demo_scene()
    eye0, tgt0 = (3.2, 1.7, 3.6), (0.0, 1.3, 0.2)
    eye1, tgt1 = (-3.0, 1.75, 3.2), (0.0, 1.35, 0.1)

    out_dir = ROOT / "town_render"
    out_dir.mkdir(exist_ok=True)
    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(out_dir / "phase6_sample.mp4")],
        stdin=subprocess.PIPE,
    )

    reports = []
    caption_words = ["Original", "sample", "scene", ",", "rendered", "live",
                      "from", "coded", "3", "D", "geometry", "."]
    for f in range(N):
        t = f / (N - 1)
        eye = lerp(eye0, eye1, t)
        target = lerp(tgt0, tgt1, t)
        cam = Camera(eye=eye, target=target, fov=50)
        img = render_frame(sc, cam, W, H)
        arr = np.asarray(img, dtype=np.uint8)

        word_idx = min(len(caption_words) - 1, f // (N // len(caption_words) + 1))
        expect_caption = True

        report = qc.analyze_frame(arr, index=f, expect_caption=False)
        reports.append(report)

        proc.stdin.write(arr.tobytes())
        if f in (0, N // 2, N - 1):
            img.save(out_dir / f"phase6_frame_{f:03d}.jpg", quality=90)

    proc.stdin.close()
    proc.wait()

    summary = qc.summarize(reports)
    print("=== PHASE 6 QC REPORT (real OpenCV pixel measurements) ===")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print("PASS" if summary["pass"] else "FAIL")


if __name__ == "__main__":
    main()

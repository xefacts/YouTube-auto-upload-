"""Full pipeline: procedurally render all 8 scenes frame-by-frame with the
custom 3D engine, burn in word-synced captions, pipe straight into ffmpeg as
H.264, then mux the narration track. No AI-generated images anywhere in the
visual pipeline -- every pixel comes from the coded 3D renderer in engine.py.
"""
import json
import math
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from town3d.engine import Camera, render_frame
from town3d.scenes import SCENE_BUILDERS
from town3d.narration import NARRATION, word_timings

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H = 720, 1280
FPS = 24
FONT_PATH = str(ROOT / "town3d" / "assets" / "Anton-Regular.ttf")

DURATIONS = json.loads((ROOT / "town_audio" / "durations.json").read_text())


def smoothstep(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def lerp(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(len(a)))


def draw_caption(img: Image.Image, word: str, pop_t: float):
    if not word:
        return
    draw = ImageDraw.Draw(img)
    base_size = int(H * 0.072)
    scale = 0.82 + 0.18 * smoothstep(pop_t / 0.09) if pop_t < 0.09 else 1.0
    size = max(10, int(base_size * scale))
    font = ImageFont.truetype(FONT_PATH, size)
    text = word
    bbox = draw.textbbox((0, 0), text, font=font, stroke_width=max(2, size // 12))
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (W - tw) / 2 - bbox[0]
    y = H * 0.68 - th / 2 - bbox[1]
    draw.text((x, y), text, font=font, fill=(255, 225, 55),
               stroke_width=max(2, size // 12), stroke_fill=(20, 20, 20))


def main():
    ffmpeg_proc = subprocess.Popen(
        [FFMPEG, "-y",
         "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS),
         "-i", "-",
         "-an",
         "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p",
         str(ROOT / "town_render" / "video_only.mp4")],
        stdin=subprocess.PIPE,
    )

    Path(ROOT / "town_render").mkdir(exist_ok=True)

    total_frames = 0
    for scene_idx, builder in enumerate(SCENE_BUILDERS):
        audio_path, text = NARRATION[scene_idx]
        duration = DURATIONS[audio_path]
        n_frames = max(1, round(duration * FPS))
        timings = word_timings(text, duration)

        scene, cam_start, cam_end, _hint = builder()
        eye0, tgt0 = cam_start["eye"], cam_start["target"]
        eye1, tgt1 = cam_end["eye"], cam_end["target"]

        for f in range(n_frames):
            t = f / FPS
            alpha = smoothstep(f / max(1, n_frames - 1))
            eye = lerp(eye0, eye1, alpha)
            target = lerp(tgt0, tgt1, alpha)
            cam = Camera(eye=eye, target=target, fov=55)
            img = render_frame(scene, cam, W, H)

            active = None
            pop_t = 0.0
            for ws, we, wtxt in timings:
                if ws <= t < we:
                    active = wtxt
                    pop_t = t - ws
                    break
            if active:
                draw_caption(img, active, pop_t)

            ffmpeg_proc.stdin.write(np.asarray(img, dtype=np.uint8).tobytes())
            total_frames += 1
        print(f"scene {scene_idx + 1}/8 done ({n_frames} frames, {duration:.2f}s)", flush=True)

    ffmpeg_proc.stdin.close()
    ffmpeg_proc.wait()
    print("TOTAL FRAMES", total_frames, "=> ", total_frames / FPS, "seconds of video")


if __name__ == "__main__":
    main()

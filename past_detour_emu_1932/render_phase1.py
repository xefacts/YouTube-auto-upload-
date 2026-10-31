#!/usr/bin/env python3
"""Render the 1932 Emu War Phase-1 Short from AI-generated still images.

No drawn/rigged/frame-by-frame character animation: the only visual motion is a
whole-image camera crop/zoom of generated scene stills. Requires pillow, numpy,
imageio-ffmpeg. Narration MP3 is a separately synthesized original voiceover.
"""
from __future__ import annotations

import math
import subprocess
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
AUDIO = ROOT / "audio"
OUT = ROOT / "Emu_War_1932_Phase1_Short.mp4"
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, DURATION = 720, 1280, 24, 52
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Each beat is its own generated still, or a new camera crop on an earlier still.
# Captions summarize the nearby narrated passage, not verbatim timed subtitles.
BEATS = [
    ("01_wheatbelt_opening.png", 3.6, "THE EMU WAR", "Western Australia, 1932", "01  /  THE SETUP"),
    ("07_truck.png", 3.5, "SOLDIERS VS. BIRDS", "The birds had other plans.", "02  /  THE HOOK"),
    ("02_migration.png", 5.2, "20,000 EMUS", "Moved into wheat country", "03  /  THE ARRIVAL"),
    ("03_crop_damage.png", 4.0, "CROPS IN TROUBLE", "Farmers asked for help", "04  /  THE PROBLEM"),
    ("04_detachment.png", 4.7, "A TINY DETACHMENT", "Three men. Two Lewis guns.", "05  /  THE RESPONSE"),
    ("02_migration.png", 4.0, "THE FLOCK GATHERS", "An opportunity, briefly", "06  /  THE PLAN"),
    ("05_scatter.png", 4.1, "THEN IT SCATTERS", "Smaller groups, harder targets", "07  /  THE ESCAPE"),
    ("06_waterhole_jam.png", 4.2, "THE GUN JAMS", "The emus get away again", "08  /  THE WATERHOLE"),
    ("07_truck.png", 5.6, "A BOUNCING TRUCK", "Rough ground ruined the aim", "09  /  THE CHASE"),
    ("04_detachment.png", 5.0, "HUNDREDS KILLED", "But the problem remained", "10  /  THE RESULT"),
    ("03_crop_damage.png", 4.0, "STILL STRUGGLING", "The farms were not saved", "11  /  THE AFTERMATH"),
    ("02_migration.png", 4.1, "NOT A FORMAL WAR", "Who won the headline?", "12  /  THE QUESTION"),
]
assert round(sum(beat[1] for beat in BEATS) * FPS) == DURATION * FPS


def run(args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def cover(source: Path) -> Image.Image:
    image = Image.open(source).convert("RGB")
    scale = max(W / image.width, H / image.height)
    size = (math.ceil(image.width * scale), math.ceil(image.height * scale))
    image = image.resize(size, Image.Resampling.LANCZOS)
    x, y = (image.width - W) // 2, (image.height - H) // 2
    return image.crop((x, y, x + W, y + H))


def fit_text(draw, text, max_width, initial=50):
    for size in range(initial, 22, -1):
        font = ImageFont.truetype(FONT_B, size)
        if draw.textbbox((0, 0), text, font=font)[2] <= max_width:
            return font
    return ImageFont.truetype(FONT_B, 23)


def make_card(path: Path, beat, index: int):
    source, _, heading, detail, section = beat
    scene = cover(IMAGES / source).convert("RGBA")
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = ov.load()
    # Soft gradient mats keep the original imagery visible and type readable.
    for y in range(H):
        top = max(0, (365 - y) / 365) ** 1.7
        bottom = max(0, (y - 825) / (H - 825)) ** 1.5
        alpha = min(194, int(128 * top + 184 * bottom))
        if alpha:
            for x in range(W):
                p[x, y] = (8, 17, 19, alpha)
    d = ImageDraw.Draw(ov)
    gold = (244, 196, 112, 255)
    white = (248, 245, 235, 255)
    small = ImageFont.truetype(FONT_B, 18)
    mid = ImageFont.truetype(FONT_R, 25)
    d.rounded_rectangle((38, 55, 178, 92), radius=18, fill=(242, 187, 100, 246))
    d.text((54, 63), "PAST DETOUR", font=ImageFont.truetype(FONT_B, 15), fill=(23, 32, 32, 255))
    d.text((W - 198, 66), "1932  ·  AUS", font=small, fill=white)
    d.line((41, 121, 103, 121), fill=gold, width=4)
    section_width = d.textbbox((0, 0), section, font=small)[2]
    d.rounded_rectangle((37, 134, 61 + section_width, 177), radius=10, fill=(8, 17, 19, 198))
    d.text((49, 146), section, font=small, fill=gold)
    f = fit_text(d, heading, W - 82)
    d.text((38, 934), heading, font=f, fill=white, stroke_width=2, stroke_fill=(10, 18, 20))
    d.text((40, 1007), detail, font=mid, fill=(247, 223, 182, 255))
    d.line((40, 1090, W - 40, 1090), fill=(230, 212, 176, 130), width=1)
    d.text((40, 1112), "AI VISUAL RECONSTRUCTION  /  REAL HISTORY", font=ImageFont.truetype(FONT_B, 13), fill=(232, 230, 221, 220))
    d.text((W - 84, 1112), f"{index:02d}", font=small, fill=gold)
    Image.alpha_composite(scene, ov).convert("RGB").save(path, quality=94)


def make_effects(path: Path):
    """Deterministic original non-melodic wind, wheat rustle, clicks and truck rattle."""
    sr = 24000
    n = sr * DURATION
    rng = np.random.default_rng(1932)
    raw = rng.standard_normal(n).astype(np.float32)
    # Moving-average noise: subdued gusts, not a tonal musical bed.
    breeze = np.convolve(raw, np.ones(100, dtype=np.float32) / 100, mode="same")
    breeze /= max(np.max(np.abs(breeze)), 1e-8)
    t = np.arange(n, dtype=np.float32) / sr
    signal = (0.020 + 0.009 * np.sin(t * 0.38) ** 2) * breeze

    def rustle(time, length=.45, gain=.055):
        i, count = int(time * sr), int(length * sr)
        count = min(count, n - i)
        if count <= 0:
            return
        noise = rng.standard_normal(count).astype(np.float32)
        env = np.sin(np.linspace(0, np.pi, count, dtype=np.float32)) ** 2
        signal[i:i + count] += gain * env * noise

    def thump(time, gain=.09):
        i, count = int(time * sr), int(.13 * sr)
        if i + count > n:
            return
        x = np.arange(count, dtype=np.float32) / sr
        signal[i:i + count] += gain * np.exp(-x * 50) * np.sin(2 * np.pi * 88 * x)

    for pos in [7.0, 11.4, 13.8, 20.2, 24.6, 28.0, 38.2, 43.0, 47.1]:
        rustle(pos, .5, .024)
    # Short dry mechanical click for the jam, no gunshot or melodic element.
    rustle(29.5, .14, .065)
    thump(29.58, .035)
    # Light rough-road bumps only during truck shot.
    for pos in np.arange(34.3, 38.6, .41):
        thump(float(pos), .045)
        rustle(float(pos) + .10, .12, .014)
    # Gentle fades avoid edits at the head and tail.
    fade = min(n // 2, sr)
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)
    signal = np.clip(signal, -.9, .9)
    pcm = (signal * 32767).astype("<i2")
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes(pcm.tobytes())


def main():
    AUDIO.mkdir(exist_ok=True)
    effects = AUDIO / "original_foley.wav"
    make_effects(effects)
    with tempfile.TemporaryDirectory(prefix="emu_short_") as temp:
        temp = Path(temp)
        segments = []
        for index, beat in enumerate(BEATS, start=1):
            card = temp / f"card_{index:02d}.png"
            clip = temp / f"clip_{index:02d}.mp4"
            make_card(card, beat, index)
            frames = round(beat[1] * FPS)
            # Zoom/pan the complete still as a camera move: no character rigging.
            direction = 1 if index % 2 else -1
            pan = "0.38" if direction == 1 else "0.62"
            vf = (f"zoompan=z='1+0.085*on/{max(frames-1, 1)}':"
                  f"x='(iw-iw/zoom)*{pan}':y='(ih-ih/zoom)*0.48':"
                  f"d=1:s={W}x{H}:fps={FPS},format=yuv420p")
            run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                 "-i", str(card), "-vf", vf, "-frames:v", str(frames), "-an", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", str(clip)])
            segments.append(clip)
            print(f"Rendered {index:02d}/{len(BEATS)}: {beat[2]}", flush=True)
        concat = temp / "concat.txt"
        concat.write_text("".join(f"file '{part}'\n" for part in segments))
        # Voiceover is dominant. Foley is kept low and there is no music.
        run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", str(concat), "-i", str(AUDIO / "narration.mp3"), "-i", str(effects),
             "-filter_complex", "[1:a]volume=1.0[v];[2:a]volume=0.38[f];"
             "[v][f]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92[a]",
             "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
             "-ar", "48000", "-ac", "2", "-t", str(DURATION), "-movflags", "+faststart", str(OUT)])
    print(f"Wrote {OUT} ({OUT.stat().st_size / 1024 / 1024:.1f} MiB)")


if __name__ == "__main__":
    main()

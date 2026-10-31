#!/usr/bin/env python3
"""Phase 2: render a real Short from generated still images, narration, and Foley.

Only image-based pans/crops/cuts. No independently animated or rigged characters.
Run from the repository root after installing Pillow, NumPy, and imageio-ffmpeg.
"""
from __future__ import annotations

import math
import subprocess
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images"
AUDIO = ROOT / "audio"
PHASE1 = ROOT.parent / "images"
OUTPUT = ROOT / "Emu_War_1932_Phase2_Short.mp4"
FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS, DURATION = 720, 1280, 24, 48
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
# Image, seconds, section, headline, subheading, optional report number.
# Editorial beat cards summarize the narration; they are not word-timed subtitles.
BEATS = [
    ("03_return.png", 3.0, "THE COMEBACK", "THEY CAME BACK", "Emu War  ·  Part 2", None),
    ("01_withdrawal.png", 3.5, "NOVEMBER 1932", "FIRST, THEY LEFT", "The early attempt faltered", None),
    ("02_farmers_petition.png", 4.0, "THE FARMERS", "CROPS WERE STILL AT RISK", "They asked for more help", None),
    ("03_return.png", 3.5, "SECOND ATTEMPT", "THE TEAM RETURNED", "A small detachment, once more", None),
    ("04_report.png", 4.5, "DECEMBER 1932", "986 REPORTED", "Emus killed in the operation", "986"),
    ("../images/02_migration.png", 4.0, "THE SCALE", "NOT ENOUGH", "The migration continued", None),
    ("05_press.png", 4.0, "THE REACTION", "HEADLINES SPREAD", "Farmers still needed protection", None),
    ("06_supplies.png", 5.0, "1934", "A DIFFERENT APPROACH", "Ammunition and bounties", None),
    ("10_bounty_ledger.png", 5.0, "SIX MONTHS", "57,000+ CLAIMS", "Bounties claimed for emus", "57,000+"),
    ("07_fence_work.png", 3.5, "LONGER TERM", "BUILD THE FENCE", "Protection across farm country", None),
    ("08_fence_aerial.png", 3.0, "THE DEFENCE", "LONG-DISTANCE FENCING", "A physical barrier, not a battle", None),
    ("09_final.png", 5.0, "THE LEGACY", "THE STORY DIDN'T END", "The crop problem outlasted the war", None),
]
assert sum(round(b[1] * FPS) for b in BEATS) == DURATION * FPS


def run(args):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr[-3500:])


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def fit(draw, text, max_width, initial=47):
    for size in range(initial, 22, -1):
        f = font(size, True)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_width:
            return f
    return font(23, True)


def cover(path):
    image = Image.open(path).convert("RGB")
    scale = max(W / image.width, H / image.height)
    image = image.resize((math.ceil(image.width * scale), math.ceil(image.height * scale)), Image.Resampling.LANCZOS)
    x = (image.width - W) // 2
    y = (image.height - H) // 2
    return image.crop((x, y, x + W, y + H))


def create_card(dest, beat, index):
    name, _, section, heading, detail, stat = beat
    source = PHASE1 / name.split("/")[-1] if name.startswith("../") else IMAGES / name
    scene = cover(source).convert("RGBA")
    if stat:
        # Historical figures are typed by the editor, never hallucinated by the image model.
        d = ImageDraw.Draw(scene)
        if stat == "986":
            d.text((130, 492), "MEREDITH'S REPORT", font=font(18, True), fill=(37, 48, 42, 255))
            d.text((128, 521), "986", font=font(94, True), fill=(37, 48, 42, 255))
        else:
            d.text((104, 417), "BOUNTY CLAIMS", font=font(18, True), fill=(37, 48, 42, 255))
            d.text((102, 445), "57,000+", font=font(61, True), fill=(37, 48, 42, 255))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    # Top and bottom title-safe gradient; all characters remain in the generated scene.
    for y in range(H):
        top = max(0.0, 1 - y / 245) ** 1.4
        bottom = max(0.0, (y - 808) / (H - 808)) ** 1.35
        alpha = min(210, round(170 * top + 184 * bottom))
        if alpha:
            ImageDraw.Draw(overlay).line((0, y, W, y), fill=(15, 27, 30, alpha))
    d = ImageDraw.Draw(overlay)
    paper = (248, 242, 222, 255)
    mint = (174, 225, 204, 255)
    d.rounded_rectangle((37, 55, 188, 94), radius=17, fill=(174, 225, 204, 247))
    d.text((53, 64), "PAST DETOUR", font=font(16, True), fill=(22, 43, 43, 255))
    d.rounded_rectangle((548, 58, 676, 92), radius=12, fill=(16, 31, 32, 198))
    d.text((563, 65), "PART 02", font=font(16, True), fill=mint)
    d.rounded_rectangle((37, 130, min(678, 64 + d.textbbox((0, 0), section, font=font(18, True))[2]), 171), radius=8, fill=(16, 31, 32, 200))
    d.text((49, 141), section, font=font(18, True), fill=mint)
    d.rectangle((40, 914, 45, 1025), fill=mint)
    d.text((60, 929), heading, font=fit(d, heading, 613), fill=paper, stroke_width=2, stroke_fill=(14, 25, 27, 255))
    d.text((62, 1007), detail, font=font(23), fill=(245, 222, 180, 255))
    d.line((40, 1097, 678, 1097), fill=(219, 221, 203, 165), width=1)
    d.text((41, 1115), "AI VISUAL RECONSTRUCTION", font=font(15, True), fill=(232, 236, 228, 240))
    d.text((630, 1115), f"{index:02d}", font=font(16, True), fill=mint)
    Image.alpha_composite(scene, overlay).convert("RGB").save(dest, quality=94)


def original_foley(dest):
    """Low-level synthesized non-melodic wind, paper and wire sounds; no samples/music."""
    sr, length = 24000, DURATION
    count = sr * length
    rng = np.random.default_rng(1934)
    raw = rng.standard_normal(count).astype(np.float32)
    smooth = np.convolve(raw, np.ones(80, np.float32) / 80, mode="same")
    smooth /= max(np.max(np.abs(smooth)), 1e-8)
    signal = 0.024 * smooth

    def rustle(time, seconds, level):
        start = int(time * sr)
        n = min(int(seconds * sr), count - start)
        if n <= 0:
            return
        envelope = np.sin(np.linspace(0, np.pi, n, dtype=np.float32)) ** 2
        signal[start:start+n] += level * envelope * rng.standard_normal(n).astype(np.float32)

    def tap(time, level=.045):
        start = int(time * sr)
        n = min(int(.10 * sr), count - start)
        x = np.arange(n, dtype=np.float32) / sr
        signal[start:start+n] += level * np.exp(-45*x) * np.sin(2*np.pi*70*x)

    for t in (3.0, 6.5, 10.5, 22.5, 26.5, 31.5, 43.0):
        rustle(t, .35, .020)
    for t in (14.9, 16.3, 32.4, 35.2):
        rustle(t, .33, .029)  # paper movement
    for t in (36.7, 38.6, 40.1, 41.9):
        tap(t)
        rustle(t+.09, .14, .012)  # non-tonal wire/wood contact
    fade = sr
    signal[:fade] *= np.linspace(0, 1, fade)
    signal[-fade:] *= np.linspace(1, 0, fade)
    with wave.open(str(dest), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sr)
        wav.writeframes((np.clip(signal, -.9, .9) * 32767).astype("<i2").tobytes())


def main():
    effects = AUDIO / "original_foley.wav"
    original_foley(effects)
    with tempfile.TemporaryDirectory(prefix="emu_phase2_") as temp_dir:
        temp = Path(temp_dir)
        clips = []
        for i, beat in enumerate(BEATS, 1):
            card = temp / f"card_{i:02}.png"
            clip = temp / f"clip_{i:02}.mp4"
            create_card(card, beat, i)
            frames = round(beat[1] * FPS)
            pan = .34 if i % 2 else .62
            vf = (f"zoompan=z='1+0.07*on/{max(frames-1, 1)}':"
                  f"x='(iw-iw/zoom)*{pan}':y='(ih-ih/zoom)*0.5':"
                  f"d=1:s={W}x{H}:fps={FPS},format=yuv420p")
            run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                 "-i", str(card), "-vf", vf, "-frames:v", str(frames), "-an", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", str(clip)])
            clips.append(clip)
            print(f"Scene {i:02}/{len(BEATS)}: {beat[3]}", flush=True)
        playlist = temp / "segments.txt"
        playlist.write_text("".join(f"file '{c}'\n" for c in clips))
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", str(playlist), "-i", str(AUDIO / "narration.mp3"), "-i", str(effects),
             "-filter_complex", "[1:a]volume=1[v];[2:a]volume=0.38[fx];"
             "[v][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.92[a]",
             "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
             "-ar", "48000", "-ac", "2", "-t", str(DURATION), "-movflags", "+faststart", str(OUTPUT)])
    print(f"Video: {OUTPUT} ({OUTPUT.stat().st_size / 1024 / 1024:.1f} MiB)")


if __name__ == "__main__":
    main()

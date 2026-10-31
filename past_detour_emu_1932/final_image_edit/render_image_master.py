#!/usr/bin/env python3
"""Image-only Emu War final cut: 10 new scenes + 9 generated alternate poses.

No subtitle layer, no speech re-generation, no imported reference footage. Short
on-scene typography is rasterized into the source stills BEFORE camera moves.
Shot-specific smooth whole-image camera moves, matched pose cuts, one sky-lift
transition, and unchanged Phase-2 AAC audio. `--8k` is a 4320x7680 upscale:
generated source images are 768x1376, not native 8K photography.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent
IMAGES = ROOT / "images_new"
FONTS = ROOT / "fonts"
STAGED = ROOT / "staged"
EPISODE = ROOT.parent
PHASE2 = EPISODE / "phase2"
FF = imageio_ffmpeg.get_ffmpeg_exe()
BASE_W, BASE_H, FPS = 1440, 2560, 24

# End, scene file, camera move (zoom start/end; horizontal/vertical anchor 0..1).
# Times follow the PRE-EXISTING Phase-2 48-second narration; no new dialogue.
SHOTS = [
    (1.62, "01_return_landscape", "01_dolly", (1.08, 1.13, .46, .52, .46, .49)),
    (3.44, "11_return_reaction", "02_matched_pose", (1.13, 1.17, .52, .56, .49, .50)),
    (7.61, "02_departure_sky", "03_track_road", (1.09, 1.13, .43, .55, .57, .54)),
    (8.96, "03_farmers_petition_wall", "04_reveal_paper", (1.09, 1.13, .53, .50, .34, .60)),
    (10.76, "13_farmer_petition_gesture", "05_matched_gesture", (1.13, 1.16, .50, .51, .60, .59)),
    (12.34, "01_return_landscape", "06_return_close", (1.18, 1.18, .46, .46, .69, .68)),
    (13.68, "11_return_reaction", "07_return_react", (1.18, 1.20, .46, .48, .68, .66)),
    (17.56, "old_report", "08_report_push", (1.08, 1.18, .45, .46, .50, .60)),
    (19.25, "04_emus_open_sky", "09_emus_track", (1.11, 1.14, .37, .49, .54, .56)),
    (21.87, "14_emus_change_position", "10_matched_flock", (1.14, 1.16, .49, .54, .56, .56)),
    (22.90, "05_press_blank", "11_press_push", (1.08, 1.16, .50, .55, .57, .62)),
    (23.93, "15_press_expression", "12_paper_react", (1.16, 1.19, .55, .54, .62, .60)),
    (25.66, "04_emus_open_sky", "13_return_field", (1.10, 1.13, .51, .50, .57, .56)),
    (26.20, "04_emus_open_sky", "14_tilt_to_sky", (1.55, 1.55, .50, .50, 1.00, .00)),
    (26.66, "10_sky_bridge", "15_sky_bridge", (1.00, 1.01, .50, .50, .40, .43)),
    (27.51, "old_field", "16_tilt_down_1934", (1.54, 1.54, .50, .50, .00, .95)),
    (29.37, "06_1934_supply", "17_supply_track", (1.09, 1.13, .43, .55, .54, .54)),
    (31.30, "16_supply_reaction", "18_matched_supply", (1.13, 1.16, .55, .56, .54, .54)),
    (33.28, "07_bounty_ledger", "19_ledger_push", (1.07, 1.15, .43, .47, .43, .53)),
    (35.35, "17_ledger_hand_shift", "20_matched_ledger", (1.15, 1.18, .47, .48, .53, .55)),
    (37.30, "08_fence_build", "21_fence_track", (1.10, 1.15, .38, .50, .50, .56)),
    (39.26, "18_fence_wire_action", "22_matched_wire", (1.15, 1.18, .50, .54, .56, .57)),
    (42.26, "old_fence_aerial", "23_fence_length", (1.06, 1.13, .48, .56, .40, .56)),
    (44.78, "09_fence_aftermath", "24_last_look", (1.13, 1.11, .47, .50, .55, .51)),
    (48.00, "19_final_emu_look", "25_final_hold", (1.11, 1.05, .50, .50, .51, .49)),
]
assert round(SHOTS[-1][0] * FPS) == 1152


def run(cmd):
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if result.returncode:
        raise RuntimeError(f"ffmpeg exited {result.returncode}: {result.stderr[-2400:]}")


def cover(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(BASE_W / im.width, BASE_H / im.height)
    im = im.resize((math.ceil(im.width * scale), math.ceil(im.height * scale)), Image.Resampling.LANCZOS)
    x, y = (im.width - BASE_W) // 2, (im.height - BASE_H) // 2
    return im.crop((x, y, x + BASE_W, y + BASE_H))


def ink(draw, pos, text, size, fill, font="Anton", stroke=0, shadow=False):
    face = ImageFont.truetype(str(FONTS / ("Anton-Regular.ttf" if font == "Anton" else "DMSans.ttf")), size)
    if shadow:
        draw.text((pos[0]+3, pos[1]+5), text, font=face, fill=(18, 35, 36), stroke_width=stroke+2, stroke_fill=(18,35,36))
    draw.text(pos, text, font=face, fill=fill, stroke_width=stroke, stroke_fill=(38, 56, 50))


def make_stage(key: str):
    STAGED.mkdir(exist_ok=True)
    if key == "old_report":
        source = PHASE2 / "images" / "04_report.png"
    elif key == "old_field":
        source = EPISODE / "images" / "01_wheatbelt_opening.png"
    elif key == "old_fence_aerial":
        source = PHASE2 / "images" / "08_fence_aerial.png"
    else:
        source = IMAGES / (key + ".png")
    path = STAGED / (key + ".jpg")
    scene = cover(source)
    d = ImageDraw.Draw(scene)
    # Type is an environmental element of the IMAGE, not a timed caption layer.
    # It uses only facts/words already spoken in the unchanged narration.
    if key in {"01_return_landscape", "11_return_reaction"}:
        ink(d, (104, 555), "NOVEMBER", 178, (241, 230, 204), shadow=True)
        ink(d, (104, 750), "1932", 310, (218, 235, 131), shadow=True)
    elif key in {"03_farmers_petition_wall", "13_farmer_petition_gesture"}:
        ink(d, (118, 460), "NOVEMBER", 166, (61, 81, 75))
        ink(d, (122, 630), "1932", 290, (85, 105, 86))
    elif key == "old_report":
        ink(d, (250, 1000), "986", 310, (36, 49, 46))
    elif key in {"05_press_blank", "15_press_expression"}:
        # A headline ON the newsprint; not a fake excerpt from a real paper.
        ink(d, (735, 1880), "EMU WAR", 90, (40, 50, 43))
    elif key in {"07_bounty_ledger", "17_ledger_hand_shift"}:
        ink(d, (330, 1280), "57,000+", 235, (47, 55, 47))
    scene.save(path, quality=96, subsampling=0)
    return path


def stage_all():
    paths = {}
    for _, key, _, _ in SHOTS:
        if key not in paths:
            paths[key] = make_stage(key)
    return paths


def render(output_width: int):
    if output_width not in (1080, 4320):
        raise ValueError("Use 1080 preview or 4320 wide 8K portrait export")
    height = output_width * 16 // 9
    is_8k = output_width == 4320
    output = ROOT / ("Emu_War_Image_Edit_8K_Portrait.mp4" if is_8k else "Emu_War_Image_Edit_1080p_preview.mp4")
    stages = stage_all()
    with tempfile.TemporaryDirectory(prefix="emu_image_master_") as tmp:
        tmp = Path(tmp)
        clips = []
        last_frame = 0
        for n, (end, key, label, move) in enumerate(SHOTS, 1):
            total = round(end * FPS)
            frames = total - last_frame
            assert frames > 0, (end, last_frame)
            last_frame = total
            z0, z1, x0, x1, y0, y1 = move
            denom = max(frames-1, 1)
            ease = f"(0.5-0.5*cos(PI*on/{denom}))"
            zoom = f"({z0}+({z1-z0})*{ease})"
            px = f"({x0}+({x1-x0})*{ease})"
            py = f"({y0}+({y1-y0})*{ease})"
            vf = (f"zoompan=z='{zoom}':x='(iw-iw/zoom)*{px}':"
                  f"y='(ih-ih/zoom)*{py}':d=1:s={output_width}x{height}:fps={FPS},format=yuv420p")
            clip = tmp / f"s{n:02}.mp4"
            run([FF, "-hide_banner", "-loglevel", "error", "-y", "-loop", "1", "-framerate", str(FPS),
                 "-i", str(stages[key]), "-vf", vf, "-frames:v", str(frames), "-an", "-c:v", "libx264",
                 "-preset", "ultrafast" if is_8k else "veryfast", "-threads", "2", "-crf", "33" if is_8k else "20",
                 "-pix_fmt", "yuv420p", str(clip)])
            clips.append(clip)
            print(f"{n:02}/{len(SHOTS)} {label:23} {frames:3} frames | {output_width}x{height}",flush=True)
        playlist = tmp / "concat.txt"
        playlist.write_text("".join(f"file '{p}'\n" for p in clips))
        # Crucial: audio comes from Phase 2 directly, bitstream copied unchanged.
        run([FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(playlist),
             "-i", str(PHASE2 / "Emu_War_1932_Phase2_Short.mp4"),
             "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy", "-t", "48",
             "-movflags", "+faststart", str(output)])
    print(f"OUTPUT {output}: {output.stat().st_size/1024/1024:.1f} MiB",flush=True)
    return output


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--8k", action="store_true", help="4320x7680 upscaled 8K portrait master")
    args = ap.parse_args()
    render(4320 if args.__dict__["8k"] else 1080)

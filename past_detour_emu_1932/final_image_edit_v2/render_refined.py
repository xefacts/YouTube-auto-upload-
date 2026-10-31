#!/usr/bin/env python3
"""Refined image-only Emu War cut: 8K-upscaled master and 1080p preview.

The English script stays unchanged. More AI-generated adjacent stills supply
expression, gesture, page, bird and wire movement. Sparse contextual typography
is baked into scene images, not added as timed captions. The soundtrack is the
existing narration plus original, very quiet NON-MELODIC wind and five small
situational Foley cues. No samples, music, new narration or rigged characters.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
PREV = ROOT.parent / "final_image_edit"
EPISODE = ROOT.parent
PHASE2 = EPISODE / "phase2"
IMAGES = ROOT / "images_new"
STAGED = ROOT / "staged"
FONTS = PREV / "fonts"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, BASE_W, BASE_H = 24, 1440, 2560

# Time marks follow the original narration's pauses. Each move is a whole-image
# camera crop with easing. Alternate stills are generated independently.
# end, still, label, (zoom0, zoom1, x0, x1, y0, y1)
SHOTS = [
    (1.45, "01_return_landscape", "establish_and_dolly", (1.07,1.12,.46,.50,.45,.47)),
    (2.35, "11_return_reaction", "matched_uncertainty", (1.12,1.14,.50,.51,.47,.48)),
    (3.44, "21_return_deep_breath", "matched_breath", (1.14,1.12,.51,.50,.48,.47)),
    (5.40, "02_departure_sky", "track_along_road", (1.07,1.12,.42,.50,.52,.55)),
    (7.61, "22_departure_intermediate", "matched_walking_pose", (1.12,1.14,.50,.53,.55,.55)),
    (8.72, "03_farmers_petition_wall", "room_to_table_tilt", (1.09,1.12,.52,.50,.35,.54)),
    (9.73, "13_farmer_petition_gesture", "matched_resolve", (1.12,1.15,.50,.51,.54,.57)),
    (10.76, "23_petition_hand", "petition_hand", (1.15,1.16,.51,.51,.57,.58)),
    (12.25, "01_return_landscape", "return_to_team", (1.17,1.17,.46,.46,.69,.67)),
    (13.68, "21_return_deep_breath", "reaction_close", (1.17,1.19,.46,.48,.67,.66)),
    (15.65, "old_report", "report_reveal", (1.06,1.13,.46,.45,.49,.56)),
    (17.56, "24_report_hand_step", "report_point", (1.13,1.18,.45,.46,.56,.58)),
    (18.85, "04_emus_open_sky", "flock_wide", (1.09,1.12,.37,.45,.52,.55)),
    (20.30, "14_emus_change_position", "flock_cross", (1.12,1.14,.45,.51,.55,.56)),
    (21.87, "25_emus_scatter_more", "flock_separates", (1.14,1.15,.51,.54,.56,.56)),
    (22.90, "05_press_blank", "paper_push", (1.07,1.14,.52,.54,.55,.61)),
    (23.93, "26_press_page_turn", "page_reaction", (1.14,1.17,.54,.54,.61,.61)),
    (25.66, "04_emus_open_sky", "return_to_open_field", (1.10,1.13,.50,.50,.55,.55)),
    (26.20, "04_emus_open_sky", "skyward_tilt", (1.55,1.55,.50,.50,1.0,.00)),
    (26.66, "10_sky_bridge", "sky_time_bridge", (1.00,1.01,.5,.5,.40,.43)),
    (27.51, "old_field", "down_to_new_setting", (1.54,1.54,.5,.5,.00,.95)),
    (28.85, "06_1934_supply", "supply_entrance", (1.08,1.12,.43,.48,.53,.53)),
    (30.05, "16_supply_reaction", "consult_ledger", (1.12,1.14,.48,.53,.53,.53)),
    (31.30, "27_supply_clerk_turn", "clerk_shifts", (1.14,1.16,.53,.55,.53,.53)),
    (32.60, "07_bounty_ledger", "ledger_dolly", (1.06,1.11,.43,.45,.42,.49)),
    (33.80, "17_ledger_hand_shift", "hand_approaches", (1.11,1.15,.45,.46,.49,.53)),
    (35.35, "28_ledger_turn_start", "page_turn_start", (1.15,1.18,.46,.47,.53,.54)),
    (36.75, "08_fence_build", "fence_line_track", (1.09,1.13,.37,.45,.50,.54)),
    (38.00, "18_fence_wire_action", "wire_work", (1.13,1.15,.45,.50,.54,.55)),
    (39.26, "29_fence_post_tighten", "post_secured", (1.15,1.16,.50,.52,.55,.55)),
    (42.26, "old_fence_aerial", "long_barrier_reveal", (1.06,1.13,.47,.55,.40,.55)),
    (44.00, "09_fence_aftermath", "quiet_evening", (1.13,1.11,.47,.49,.55,.53)),
    (46.00, "19_final_emu_look", "emu_turn", (1.11,1.08,.49,.50,.53,.51)),
    (48.00, "30_final_quiet_look", "calm_end", (1.08,1.04,.50,.50,.51,.49)),
]
assert round(SHOTS[-1][0] * FPS) == 1152


def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if p.returncode:
        raise RuntimeError(f"ffmpeg exit {p.returncode}: {p.stderr[-2500:]}")


def cover(path):
    im = Image.open(path).convert("RGB")
    s = max(BASE_W/im.width, BASE_H/im.height)
    im = im.resize((math.ceil(im.width*s), math.ceil(im.height*s)), Image.Resampling.LANCZOS)
    return im.crop(((im.width-BASE_W)//2, (im.height-BASE_H)//2,
                    (im.width+BASE_W)//2, (im.height+BASE_H)//2))


def type_on_scene(image, key):
    """Editorial type is printed onto the location still BEFORE video editing."""
    d = ImageDraw.Draw(image)
    anton = str(FONTS / "Anton-Regular.ttf")
    cinzel = str(EPISODE.parent / "past_detour_gold_1971" / "v3_fonts" / "Cinzel.ttf")
    f = lambda path, size: ImageFont.truetype(path, size)
    if key in {"01_return_landscape", "11_return_reaction", "21_return_deep_breath"}:
        d.text((101, 571), "NOVEMBER", font=f(cinzel, 112), fill="#173B41", stroke_width=2, stroke_fill="#E8E7CD")
        d.text((99, 713), "1932", font=f(anton, 350), fill="#E0EF91", stroke_width=3, stroke_fill="#26474C")
    elif key in {"03_farmers_petition_wall", "13_farmer_petition_gesture", "23_petition_hand"}:
        d.text((132, 472), "NOVEMBER", font=f(cinzel, 100), fill="#485852")
        d.text((127, 617), "1932", font=f(anton, 315), fill="#6C7560")
    elif key in {"old_report", "24_report_hand_step"}:
        d.text((252, 968), "REPORTED", font=f(cinzel, 67), fill="#30423C")
        d.text((246, 1049), "986", font=f(anton, 300), fill="#273933")
    elif key in {"05_press_blank", "15_press_expression"}:
        d.text((752, 1880), "EMU WAR", font=f(anton, 86), fill="#283D38")
    elif key == "26_press_page_turn":
        # The bent sheet is narrower: stack the same title so every letter
        # stays physically on newsprint instead of spilling onto the worker.
        d.text((806, 1848), "EMU", font=f(anton, 72), fill="#283D38")
        d.text((815, 1932), "WAR", font=f(anton, 72), fill="#283D38")
    elif key in {"07_bounty_ledger", "17_ledger_hand_shift", "28_ledger_turn_start"}:
        d.text((335, 1236), "CLAIMS", font=f(cinzel, 67), fill="#3E4C42")
        d.text((330, 1323), "57,000+", font=f(anton, 228), fill="#293E34")
    return image


def stage():
    STAGED.mkdir(exist_ok=True)
    paths = {}
    for _, key, _, _ in SHOTS:
        if key in paths: continue
        if key == "old_report": source = PHASE2 / "images" / "04_report.png"
        elif key == "old_field": source = EPISODE / "images" / "01_wheatbelt_opening.png"
        elif key == "old_fence_aerial": source = PHASE2 / "images" / "08_fence_aerial.png"
        elif (IMAGES / f"{key}.png").is_file(): source = IMAGES / f"{key}.png"
        else: source = PREV / "images_new" / f"{key}.png"
        dest = STAGED / f"{key}.jpg"
        type_on_scene(cover(source), key).save(dest, quality=96, subsampling=0)
        paths[key] = dest
    return paths


def effects_only(path):
    """Extremely restrained, non-melodic accents: no drum beat or soundtrack music."""
    sr, seconds = 24000, 48
    n = sr*seconds
    rng = np.random.default_rng(1935)
    raw = rng.standard_normal(n).astype(np.float32)
    wind = np.convolve(raw, np.ones(115,np.float32)/115,mode="same")
    wind /= max(np.max(np.abs(wind)),1e-9)
    signal = .012 * wind  # very low ambient bed, silence/voice dominates

    def paper(t, duration, level):
        start = int(t*sr)
        count = min(int(duration*sr), n-start)
        env = np.sin(np.linspace(0,np.pi,count,dtype=np.float32))**2
        signal[start:start+count] += level * env * rng.standard_normal(count).astype(np.float32)

    # One accent for each genuine change of action, not every image cut.
    paper(14.1,.32,.017)   # report
    paper(19.2,.36,.013)   # wheat and birds
    paper(22.1,.25,.014)   # newspaper sheet
    paper(32.1,.32,.015)   # farm ledger
    paper(37.1,.16,.012)   # wire/post dry contact, not a musical note
    signal[:sr] *= np.linspace(0,1,sr)
    signal[-sr:] *= np.linspace(1,0,sr)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((np.clip(signal,-.9,.9)*32767).astype("<i2").tobytes())


def render(width):
    if width not in (1080,4320): raise ValueError("1080 preview or 4320 portrait 8K")
    height = width*16//9
    is_8k = width==4320
    output = ROOT/("Emu_War_Refined_Final_8K_Portrait.mp4" if is_8k else "Emu_War_Refined_1080p_Preview.mp4")
    paths = stage()
    foley = ROOT/"restrained_effects.wav"
    effects_only(foley)
    with tempfile.TemporaryDirectory(prefix="emu_refined_") as folder:
        tmp = Path(folder)
        clips=[]
        frame0=0
        for i,(end,key,label,move) in enumerate(SHOTS,1):
            frame1=round(end*FPS); count=frame1-frame0;frame0=frame1
            assert count>0
            z0,z1,x0,x1,y0,y1=move
            e=f"(0.5-0.5*cos(PI*on/{max(count-1,1)}))"
            z=f"({z0}+({z1-z0})*{e})"
            x=f"({x0}+({x1-x0})*{e})"
            y=f"({y0}+({y1-y0})*{e})"
            vf=(f"zoompan=z='{z}':x='(iw-iw/zoom)*{x}':"
                f"y='(ih-ih/zoom)*{y}':d=1:s={width}x{height}:fps={FPS},format=yuv420p")
            clip=tmp/f"scene_{i:02}.mp4"
            run([FF,"-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),
                 "-i",str(paths[key]),"-vf",vf,"-frames:v",str(count),"-an","-c:v","libx264",
                 "-preset","ultrafast" if is_8k else "veryfast","-threads","2",
                 "-crf","33" if is_8k else "20","-pix_fmt","yuv420p",str(clip)])
            clips.append(clip)
            print(f"{i:02}/{len(SHOTS)} {label}: {count} frames @ {width}x{height}",flush=True)
        playlist=tmp/"concat.txt"
        playlist.write_text("".join(f"file '{c}'\n" for c in clips))
        # No previous noisy mix and no new narration. Reuse original spoken voice.
        run([FF,"-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(playlist),
             "-i",str(PHASE2/"audio"/"narration.mp3"),"-i",str(foley),
             "-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.30[fx];"
             "[voice][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94[a]",
             "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
             "-ar","48000","-ac","2","-t","48","-movflags","+faststart",str(output)])
    print(f"OUTPUT {output} ({output.stat().st_size/1024/1024:.1f} MiB)")


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--8k",action="store_true",help="4320x7680 upscaled 8K portrait export")
    args=parser.parse_args()
    render(4320 if args.__dict__["8k"] else 1080)

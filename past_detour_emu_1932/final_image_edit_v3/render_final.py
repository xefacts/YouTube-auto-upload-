#!/usr/bin/env python3
"""V3 Emu War Short: portrait image-edit, authentic narration, non-melodic ambience.

Generated stills are separate pose images; no character rigging or reference
footage. Context text is typeset INTO selected graded stills before movement,
not rendered as timed video subtitles. Bird cues are original synthesis, not
field recordings or music. The 8K export is upscaled, not native 8K imagery.
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
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parent
EPISODE = ROOT.parent
OLD = EPISODE / "final_image_edit"
V2 = EPISODE / "final_image_edit_v2"
PHASE2 = EPISODE / "phase2"
NEW = ROOT / "images_new"
STAGED = ROOT / "staged"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, BASE_W, BASE_H = 24, 1440, 2560

# end seconds, still name, camera beat, (zoom start/end, x start/end, y start/end)
# Opening November still is used ONCE. Each subsequent shot uses a distinct
# still. The sky-up / sky-down change happens at 26 seconds, in three parts.
SHOTS = [
    (1.45,"01_return_landscape","date_establish",(1.08,1.15,.44,.50,.43,.47)),
    (2.35,"11_return_reaction","concern_close",(1.13,1.18,.47,.55,.54,.56)),
    (3.44,"old_withdrawal","first_withdrawal",(1.10,1.19,.40,.58,.48,.61)),
    (5.40,"02_departure_sky","road_lateral",(1.09,1.16,.36,.54,.55,.55)),
    (6.47,"12_departure_farther","road_wide",(1.11,1.15,.43,.54,.48,.52)),
    (7.61,"22_departure_intermediate","walking_pose",(1.15,1.19,.47,.57,.52,.56)),
    (8.72,"03_farmers_petition_wall","enter_petition",(1.08,1.15,.44,.53,.42,.55)),
    (9.73,"13_farmer_petition_gesture","farmer_resolves",(1.14,1.20,.47,.57,.55,.58)),
    (10.58,"32_farmer_wheat_close","crop_damage_hand",(1.16,1.22,.53,.58,.59,.67)),
    (11.46,"23_petition_hand","point_to_crops",(1.16,1.20,.50,.56,.59,.62)),
    (13.68,"31_team_reentry_side","team_back_into_field",(1.08,1.18,.35,.61,.60,.58)),
    (15.65,"33_officer_report_reaction","report_examination",(1.09,1.18,.53,.62,.48,.59)),
    (16.89,"old_report","report_figure",(1.08,1.17,.45,.49,.52,.61)),
    (17.56,"24_report_hand_step","report_finger",(1.18,1.20,.48,.52,.64,.66)),
    (18.80,"34_emus_wheat_foreground","flock_cross_foreground",(1.11,1.19,.38,.58,.57,.59)),
    (19.75,"14_emus_change_position","birds_run",(1.13,1.19,.40,.58,.55,.59)),
    (20.80,"25_emus_scatter_more","birds_spread",(1.12,1.19,.37,.60,.55,.61)),
    (21.88,"35_emu_dust_turn","bird_pivots",(1.12,1.19,.37,.56,.60,.61)),
    (23.07,"05_press_blank","press_headline",(1.07,1.15,.51,.57,.60,.63)),
    (24.08,"26_press_page_turn","newsprint_turn",(1.15,1.20,.53,.60,.58,.63)),
    (25.66,"36_press_farmer_listens","press_reader_reaction",(1.10,1.18,.48,.58,.55,.60)),
    (26.20,"04_emus_open_sky","skyward_tilt",(1.54,1.54,.50,.50,.99,.00)),
    (26.66,"10_sky_bridge","sky_time_bridge",(1.00,1.01,.50,.50,.42,.45)),
    (27.51,"37_post_sky_new_field","down_into_new_field",(1.50,1.50,.50,.50,.00,.95)),
    (28.85,"06_1934_supply","supply_shed_1934",(1.09,1.15,.40,.54,.55,.57)),
    (30.05,"16_supply_reaction","farmer_consults_clerk",(1.14,1.18,.49,.60,.54,.59)),
    (31.30,"27_supply_clerk_turn","clerk_turn",(1.13,1.20,.50,.61,.55,.58)),
    (32.60,"07_bounty_ledger","bounty_claims",(1.07,1.16,.42,.49,.49,.59)),
    (33.80,"17_ledger_hand_shift","ledger_hand",(1.15,1.19,.48,.55,.57,.61)),
    (35.35,"28_ledger_turn_start","turn_ledger",(1.14,1.20,.47,.56,.59,.64)),
    (36.75,"08_fence_build","fence_line",(1.08,1.16,.35,.56,.53,.57)),
    (37.90,"18_fence_wire_action","wire_work",(1.13,1.20,.46,.58,.56,.61)),
    (39.26,"38_fence_wire_close","tool_on_wire",(1.11,1.20,.40,.57,.65,.72)),
    (40.46,"29_fence_post_tighten","post_secured",(1.13,1.19,.46,.55,.58,.62)),
    (42.26,"old_fence_aerial","barrier_reveal",(1.06,1.17,.38,.61,.41,.58)),
    (44.00,"39_farmer_fence_walk","walk_along_fence",(1.10,1.18,.40,.59,.54,.60)),
    (45.35,"09_fence_aftermath","evening_distance",(1.13,1.11,.47,.55,.53,.56)),
    (46.60,"19_final_emu_look","emu_looks_back",(1.13,1.10,.47,.52,.57,.56)),
    (48.00,"40_final_emu_profile","quiet_end",(1.11,1.02,.53,.52,.55,.53)),
]
assert round(SHOTS[-1][0]*FPS) == 1152
assert len({row[1] for row in SHOTS}) == len(SHOTS), "Do not repeat a scene still"


def run(cmd):
    proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if proc.returncode:
        raise RuntimeError(f"ffmpeg failed ({proc.returncode}): {proc.stderr[-3000:]}")


def cover(path):
    with Image.open(path) as original:
        image = original.convert("RGB")
    scale = max(BASE_W/image.width, BASE_H/image.height)
    image = image.resize((math.ceil(image.width*scale),math.ceil(image.height*scale)), Image.Resampling.LANCZOS)
    x,y = (image.width-BASE_W)//2,(image.height-BASE_H)//2
    return image.crop((x,y,x+BASE_W,y+BASE_H))


def grade(image):
    """Unified subtle warm highlight / cool shadow film grade on each still."""
    image = ImageEnhance.Color(image).enhance(0.96)
    image = ImageEnhance.Contrast(image).enhance(1.055)
    # Soft amber highlight and blue-green shadow bias; preserve white paper.
    red = [min(255,max(0,round(v + 2 + 3*(v/255)**2))) for v in range(256)]
    green = [min(255,max(0,round(v + 1))) for v in range(256)]
    blue = [min(255,max(0,round(v + 3*(1-v/255)**2 - 3*(v/255)**2))) for v in range(256)]
    channels = image.split()
    return Image.merge("RGB", tuple(c.point(lut) for c,lut in zip(channels,(red,green,blue))))


def print_on_still(image,key):
    """Physically bake contextual print into selected scene stills, before pans."""
    draw=ImageDraw.Draw(image)
    anton = str(OLD/"fonts"/"Anton-Regular.ttf")
    cinzel = str(EPISODE.parent/"past_detour_gold_1971"/"v3_fonts"/"Cinzel.ttf")
    f=lambda p,n: ImageFont.truetype(p,n)
    if key=="01_return_landscape":
        # Date appears ONCE, on the opener only (not on later returns).
        draw.text((101,571),"NOVEMBER",font=f(cinzel,112),fill="#173B41",stroke_width=2,stroke_fill="#E8E7CD")
        draw.text((99,713),"1932",font=f(anton,350),fill="#E0EF91",stroke_width=3,stroke_fill="#26474C")
    elif key=="old_report":
        draw.text((252,968),"REPORTED",font=f(cinzel,67),fill="#30423C")
        draw.text((246,1049),"986",font=f(anton,300),fill="#273933")
    elif key=="05_press_blank":
        draw.text((752,1880),"EMU WAR",font=f(anton,86),fill="#283D38")
    elif key=="07_bounty_ledger":
        draw.text((335,1236),"CLAIMS",font=f(cinzel,67),fill="#3E4C42")
        draw.text((330,1323),"57,000+",font=f(anton,228),fill="#293E34")
    return image


def source(key):
    if key=="old_report": return PHASE2/"images"/"04_report.png"
    if key=="old_withdrawal": return PHASE2/"images"/"01_withdrawal.png"
    if key=="old_fence_aerial": return PHASE2/"images"/"08_fence_aerial.png"
    for folder in (NEW,V2/"images_new",OLD/"images_new"):
        candidate=folder/f"{key}.png"
        if candidate.is_file():return candidate
    raise FileNotFoundError(key)


def stage():
    STAGED.mkdir(exist_ok=True)
    paths={}
    for _,key,_,_ in SHOTS:
        if key in paths:continue
        dest=STAGED/f"{key}.jpg"
        print_on_still(grade(cover(source(key))),key).save(dest,quality=96,subsampling=0)
        paths[key]=dest
    return paths


def original_natural_cues(path):
    """Non-melodic, original emu-inspired low rumbles and sparse Foley.

    These are synthesized texture, NOT a genuine emu field recording. Each
    bird gesture is a slightly different band-limited air/guttural pulse,
    with no pitched melody or drums. Narration remains clearly in front.
    """
    sr=24000;n=sr*48
    rng=np.random.default_rng(1936)
    raw=rng.standard_normal(n).astype(np.float32)
    wind=np.convolve(raw,np.ones(127,dtype=np.float32)/127,mode="same")
    wind/=max(np.max(np.abs(wind)),1e-8)
    signal=.011*wind

    def rustle(t,d,level):
        start=int(t*sr);length=min(int(d*sr),n-start)
        env=np.sin(np.linspace(0,np.pi,length,dtype=np.float32))**2
        grain=rng.standard_normal(length).astype(np.float32)
        signal[start:start+length]+=level*env*grain

    def emu_inspired(t,d,level,seed):
        start=int(t*sr);length=min(int(d*sr),n-start)
        local=np.random.default_rng(seed)
        airy=local.standard_normal(length).astype(np.float32)
        # A noisy low guttural pulse, not a stable note or a song.
        airy=np.convolve(airy,np.ones(42,dtype=np.float32)/42,mode="same")
        airy/=max(np.max(np.abs(airy)),1e-8)
        times=np.arange(length,dtype=np.float32)/sr
        rough=np.sin(2*np.pi*(38*times+4.8*times*times) + .7*np.sin(2*np.pi*3.2*times))
        wav=.58*airy+.42*rough*local.uniform(.4,1.,length).astype(np.float32)
        tremolo=.55+.45*np.sin(2*np.pi*(3.5+seed*.07)*times)**2
        envelope=np.sin(np.pi*np.linspace(0,1,length,dtype=np.float32))**2
        signal[start:start+length]+=level*wav*tremolo*envelope

    # Small contextual cues, never a cue on every image change.
    rustle(9.80,.28,.012)    # damaged wheat
    rustle(16.01,.22,.014)   # report paper
    emu_inspired(18.28,.48,.060,8)
    emu_inspired(20.60,.40,.045,17)
    rustle(23.18,.27,.013)   # newsprint
    emu_inspired(25.79,.36,.038,27) # distant, prior to sky transition
    rustle(32.28,.29,.012)   # claims ledger
    rustle(38.16,.17,.012)   # wire contact
    emu_inspired(45.77,.47,.042,38) # quiet conclusion
    signal[:sr]*=np.linspace(0,1,sr)
    signal[-sr:]*=np.linspace(1,0,sr)
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(sr)
        wav.writeframes((np.clip(signal,-.9,.9)*32767).astype("<i2").tobytes())


def render(width):
    if width not in (1080,4320):raise ValueError("1080 or upscaled portrait 8K")
    height=width*16//9
    is8=width==4320
    output=ROOT/("Emu_War_Final_v3_8K_Portrait.mp4" if is8 else "Emu_War_Final_v3_1080p_Preview.mp4")
    paths=stage()
    foley=ROOT/"natural_cues.wav"
    original_natural_cues(foley)
    with tempfile.TemporaryDirectory(prefix="emu_final_v3_") as work:
        temp=Path(work); clips=[];last=0
        for i,(end,key,label,move) in enumerate(SHOTS,1):
            stop=round(end*FPS);count=stop-last;last=stop
            assert count>0
            z0,z1,x0,x1,y0,y1=move
            easing=f"(0.5-0.5*cos(PI*on/{max(count-1,1)}))"
            z=f"({z0}+({z1-z0})*{easing})"
            x=f"({x0}+({x1-x0})*{easing})"
            y=f"({y0}+({y1-y0})*{easing})"
            vf=(f"zoompan=z='{z}':x='(iw-iw/zoom)*{x}':"
                f"y='(ih-ih/zoom)*{y}':d=1:s={width}x{height}:fps={FPS},format=yuv420p")
            clip=temp/f"scene_{i:02}.mp4"
            run([FF,"-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),
                 "-i",str(paths[key]),"-vf",vf,"-frames:v",str(count),"-an","-c:v","libx264",
                 "-preset","ultrafast" if is8 else "veryfast","-threads","2",
                 "-crf","33" if is8 else "20","-pix_fmt","yuv420p",str(clip)])
            clips.append(clip)
            print(f"{i:02}/{len(SHOTS)} {label}: {count} frames @ {width}x{height}",flush=True)
        playlist=temp/"concat.txt"
        playlist.write_text("".join(f"file '{clip}'\n" for clip in clips))
        run([FF,"-hide_banner","-loglevel","error","-y","-f","concat","-safe","0","-i",str(playlist),
             "-i",str(PHASE2/"audio"/"narration.mp3"),"-i",str(foley),
             "-filter_complex","[1:a]volume=1.0[voice];[2:a]volume=0.56[fx];"
             "[voice][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94[a]",
             "-map","0:v:0","-map","[a]","-c:v","copy","-c:a","aac","-b:a","160k",
             "-ar","48000","-ac","2","-t","48","-movflags","+faststart",str(output)])
    print(f"OUTPUT {output} ({output.stat().st_size/1024/1024:.1f} MiB)")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--8k",action="store_true",help="4320x7680 upscaled export")
    args=parser.parse_args()
    render(4320 if args.__dict__["8k"] else 1080)

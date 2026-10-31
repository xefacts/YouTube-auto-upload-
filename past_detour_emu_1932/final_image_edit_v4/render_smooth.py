#!/usr/bin/env python3
"""V4 Emu War Short: voice-aligned image-edit with match cuts and short dissolves.

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
V3 = EPISODE / "final_image_edit_v3"
PHASE2 = EPISODE / "phase2"
NEW = ROOT / "images_new"
STAGED = ROOT / "staged"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, BASE_W, BASE_H = 30, 1440, 2560

# End seconds, still name, camera beat, zoom/x/y start and end.
# Script beats: 0–3 return, 3–7 withdrawal, 7–11 crops/farmers, 11–14
# second return, 14–17 report, 17–22 migration, 22–26 news and farmers,
# 26–31 sky/1934 supplies, 31–35 claims, 35–42 fencing, 42–48 legacy.
# Every scene still is UNIQUE. Camera travel stays purposeful, not frantic.
SHOTS = [
    (1.45,"01_return_landscape","return_date",(1.08,1.13,.45,.51,.44,.47)),
    (3.44,"31_team_reentry_side","small_team_returns",(1.09,1.17,.41,.55,.55,.57)),
    (5.45,"old_withdrawal","first_withdrawal",(1.09,1.16,.41,.53,.49,.55)),
    (7.61,"02_departure_sky","road_out",(1.08,1.14,.42,.53,.52,.55)),
    (8.72,"03_farmers_petition_wall","crop_concern_establish",(1.08,1.14,.46,.51,.43,.53)),
    (9.73,"13_farmer_petition_gesture","farmer_plea",(1.13,1.17,.50,.55,.54,.57)),
    (11.46,"32_farmer_wheat_close","damaged_wheat",(1.12,1.19,.46,.55,.61,.63)),
    (13.68,"old_return","detachment_returns",(1.09,1.17,.44,.54,.54,.58)),
    (15.65,"33_officer_report_reaction","officer_reports",(1.08,1.15,.49,.56,.51,.57)),
    (16.89,"old_report","reported_986",(1.07,1.15,.45,.48,.55,.60)),
    (17.56,"24_report_hand_step","report_detail",(1.16,1.18,.48,.51,.62,.64)),
    (18.80,"34_emus_wheat_foreground","birds_not_stopped",(1.08,1.16,.39,.56,.58,.60)),
    (19.80,"42_migration_damage_detail","migration_scale",(1.10,1.17,.41,.56,.55,.56)),
    (20.80,"25_emus_scatter_more","birds_continue",(1.10,1.16,.41,.56,.54,.57)),
    (21.88,"35_emu_dust_turn","flock_disappears",(1.12,1.16,.46,.53,.57,.58)),
    (23.20,"05_press_blank","newspaper_headline",(1.07,1.13,.50,.56,.59,.61)),
    (24.00,"26_press_page_turn","press_page_turn",(1.14,1.17,.55,.58,.59,.61)),
    (25.66,"41_farmer_news_crop","farmers_still_need_help",(1.10,1.17,.47,.55,.56,.59)),
    (26.20,"04_emus_open_sky","look_up_from_field",(1.50,1.50,.50,.50,.99,.00)),
    (26.66,"10_sky_bridge","sky_to_1934",(1.00,1.01,.50,.50,.44,.46)),
    (27.51,"37_post_sky_new_field","down_to_new_farm",(1.50,1.50,.50,.50,.00,.93)),
    (28.85,"06_1934_supply","1934_supply",(1.08,1.14,.43,.52,.54,.56)),
    (30.10,"43_supply_exchange","supplies_passed",(1.10,1.16,.44,.54,.56,.58)),
    (31.30,"27_supply_clerk_turn","clerk_action",(1.10,1.16,.48,.55,.53,.56)),
    (32.60,"07_bounty_ledger","claims_total",(1.06,1.13,.43,.48,.50,.58)),
    (33.80,"44_claims_clerk_cards","claims_processed",(1.11,1.15,.48,.53,.54,.58)),
    (35.35,"28_ledger_turn_start","ledger_close",(1.13,1.17,.47,.53,.59,.61)),
    (36.75,"08_fence_build","fencing_begins",(1.08,1.14,.39,.52,.53,.56)),
    (37.90,"18_fence_wire_action","wire_pulled",(1.12,1.16,.46,.54,.55,.58)),
    (39.26,"38_fence_wire_close","wire_fastened",(1.10,1.16,.47,.54,.66,.69)),
    (40.46,"29_fence_post_tighten","post_secured",(1.12,1.16,.47,.53,.58,.60)),
    (42.26,"old_fence_aerial","long_barrier",(1.07,1.15,.41,.57,.44,.56)),
    (44.00,"45_long_fence_protection","fence_protects_crops",(1.06,1.12,.43,.54,.56,.58)),
    (45.35,"39_farmer_fence_walk","farmers_walk_on",(1.10,1.15,.45,.53,.56,.59)),
    (48.00,"40_final_emu_profile","quiet_bird_outro",(1.10,1.02,.54,.52,.55,.53)),
]
assert round(SHOTS[-1][0]*FPS) == 1440
assert len({row[1] for row in SHOTS}) == len(SHOTS), "Repeated still is forbidden"

# Short 5-frame dissolves ONLY between changes of place/topic. Pose matches,
# report details and ledger/fence actions retain intentional cuts-on-action.
FADE_AFTER = {
    "02_departure_sky", "32_farmer_wheat_close", "24_report_hand_step",
    "35_emu_dust_turn", "41_farmer_news_crop", "10_sky_bridge",
    "28_ledger_turn_start", "39_farmer_fence_walk",
}
assert FADE_AFTER <= {s[1] for s in SHOTS[:-1]}
FADE_FRAMES = 5  # 167 ms at 30 fps; preserve total 48 seconds


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
    if key=="old_return": return PHASE2/"images"/"03_return.png"
    if key=="old_fence_aerial": return PHASE2/"images"/"08_fence_aerial.png"
    for folder in (NEW,V3/"images_new",V2/"images_new",OLD/"images_new"):
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


def render():
    """Render 30fps 1440p camera moves, bridge topic changes, then two exports.

    A chapter transition consumes the *last* five frames of the old shot and
    the *first* five frames of the next shot simultaneously. The next shot gets
    a five-frame visual preroll. Its body starts at frame 5, so no frame repeats,
    no subtitle moves independently of an image, and total length stays 48 s.
    """
    paths=stage()
    foley=ROOT/"natural_cues.wav"
    original_natural_cues(foley)
    with tempfile.TemporaryDirectory(prefix="emu_smooth_v4_") as work:
        tmp=Path(work); shots=[];segment_files=[];last=0
        enc=["-c:v","libx264","-preset","veryfast","-crf","22",
             "-pix_fmt","yuv420p","-r",str(FPS),"-an"]
        for i,(end,key,label,move) in enumerate(SHOTS):
            stop=round(end*FPS);count=stop-last;last=stop
            preroll=FADE_FRAMES if i and SHOTS[i-1][1] in FADE_AFTER else 0
            total=count+preroll
            assert count>FADE_FRAMES*2
            z0,z1,x0,x1,y0,y1=move
            ease=f"(0.5-0.5*cos(PI*on/{max(total-1,1)}))"
            z=f"({z0}+({z1-z0})*{ease})"
            x=f"({x0}+({x1-x0})*{ease})"
            y=f"({y0}+({y1-y0})*{ease})"
            vf=(f"zoompan=z='{z}':x='(iw-iw/zoom)*{x}':"
                f"y='(ih-ih/zoom)*{y}':d=1:s={BASE_W}x{BASE_H}:fps={FPS},format=yuv420p")
            clip=tmp/f"shot_{i:02}.mp4"
            run([FF,"-hide_banner","-loglevel","error","-y","-loop","1","-framerate",str(FPS),
                 "-i",str(paths[key]),"-vf",vf,"-frames:v",str(total),*enc,str(clip)])
            shots.append((clip,count,preroll,total,key))
            print(f"{i+1:02}/{len(SHOTS)} {label} ({count} timeline frames)",flush=True)
        for i,(clip,count,pre,total,key) in enumerate(shots):
            tail=FADE_FRAMES if key in FADE_AFTER else 0
            body_count=count-tail
            body=tmp/f"body_{i:02}.mp4"
            run([FF,"-hide_banner","-loglevel","error","-y","-i",str(clip),
                 "-vf",f"trim=start_frame={pre}:end_frame={pre+body_count},setpts=PTS-STARTPTS",
                 "-frames:v",str(body_count),*enc,str(body)])
            segment_files.append(body)
            if tail:
                nextclip=shots[i+1][0]
                fade=tmp/f"fade_{i:02}.mp4"
                a=f"trim=start_frame={total-FADE_FRAMES}:end_frame={total},setpts=PTS-STARTPTS"
                b=f"trim=start_frame=0:end_frame={FADE_FRAMES},setpts=PTS-STARTPTS"
                # Blend synchronized camera frames, not a fade to black.
                expr=f"A*(1-min(1,N/{FADE_FRAMES}))+B*min(1,N/{FADE_FRAMES})"
                filtergraph=f"[0:v]{a}[a];[1:v]{b}[b];[a][b]blend=all_expr='{expr}',format=yuv420p[v]"
                run([FF,"-hide_banner","-loglevel","error","-y","-i",str(clip),"-i",str(nextclip),
                     "-filter_complex",filtergraph,"-map","[v]","-frames:v",str(FADE_FRAMES),*enc,str(fade)])
                segment_files.append(fade)
        playlist=tmp/"timeline.txt"
        playlist.write_text("".join(f"file '{clip}'\n" for clip in segment_files))
        for width in (1080,4320):
            height=width*16//9
            output=ROOT/("Emu_War_Smooth_Final_v4_8K_Portrait.mp4" if width==4320 else
                         "Emu_War_Smooth_Final_v4_1080p_Preview.mp4")
            # 8K requires low-memory x264 preset; a slightly higher CRF keeps
            # the upscaled export below the cloud delivery size limit.
            preset="ultrafast" if width==4320 else "veryfast"
            crf="34.5" if width==4320 else "19"
            run([FF,"-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
                 "-i",str(playlist),"-i",str(PHASE2/"audio"/"narration.mp3"),"-i",str(foley),
                 "-filter_complex","[0:v]scale="+f"{width}:{height}:flags=lanczos"+"[v];"
                 "[1:a]volume=1.0[voice];[2:a]volume=0.56[fx];"
                 "[voice][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94[a]",
                 "-map","[v]","-map","[a]","-c:v","libx264","-preset",preset,
                 "-crf",crf,"-pix_fmt","yuv420p","-r",str(FPS),
                 "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",
                 "-t","48","-movflags","+faststart",str(output)])
            print(f"OUTPUT {output} ({output.stat().st_size/1024/1024:.1f} MiB)",flush=True)


if __name__=="__main__":
    render()

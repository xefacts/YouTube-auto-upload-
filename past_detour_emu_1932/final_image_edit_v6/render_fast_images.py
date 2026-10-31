#!/usr/bin/env python3
"""V6 Emu War Short: fast, smooth image-pose movement without rigging.

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
V4 = EPISODE / "final_image_edit_v4"
V5 = EPISODE / "final_image_edit_v5"
PHASE2 = EPISODE / "phase2"
NEW = ROOT / "images_new"
STAGED = ROOT / "staged"
FF = imageio_ffmpeg.get_ffmpeg_exe()
FPS, BASE_W, BASE_H = 30, 1440, 2560

# The three indoor wheat/table farmer stills are intentionally EXCLUDED.
# Voiceover beats remain: withdrawal, outdoor crop damage, small team return,
# report, continuing birds, press, 1934 assistance, claims, fences and ending.
# Emu run frames 49-51 and turn frames 52-53 are independently generated
# adjacent-pose STILL IMAGES, never separately rigged character animation.
# (end seconds, unique image, narration beat, z0/z1/x0/x1/y0/y1)
SHOTS = [
    ( 1.45,"01_return_landscape","date_once",(1.065,1.065,.49,.49,.46,.46)),
    ( 3.44,"31_team_reentry_side","team_approaches",(1.14,1.14,.43,.61,.55,.55)),
    ( 5.45,"old_withdrawal","first_withdrawal",(1.13,1.13,.59,.39,.52,.52)),
    ( 7.61,"02_departure_sky","road_departure",(1.14,1.14,.35,.62,.55,.55)),
    ( 8.85,"46_crop_damage_outdoor_wide","farmers_see_damage",(1.17,1.17,.37,.61,.56,.56)),
    (10.00,"47_crop_damage_outdoor_gesture","farmers_appeal",(1.19,1.19,.59,.43,.59,.59)),
    (11.46,"48_crop_damage_outdoor_close","broken_stalks",(1.17,1.17,.51,.51,.69,.55)),
    (12.55,"old_return","team_comes_back",(1.13,1.13,.42,.57,.55,.55)),
    (13.68,"54_team_return_gesture","team_changes_pose",(1.16,1.16,.36,.64,.54,.54)),
    (15.65,"33_officer_report_reaction","report_examined",(1.13,1.13,.60,.44,.56,.56)),
    (16.89,"old_report","986_reported",(1.09,1.09,.47,.51,.55,.55)),
    (17.56,"24_report_hand_step","finger_on_report",(1.17,1.17,.42,.59,.62,.62)),
    (18.25,"34_emus_wheat_foreground","flock_in_field",(1.17,1.17,.39,.62,.58,.58)),
    # These birds sit near the image's right edge. Retain the full head in
    # the crop; rapid pose changes create the movement, not an unsafe zoom.
    (18.85,"49_emu_run_pose_a","emu_run_step_one",(1.08,1.08,.80,1.00,.58,.58)),
    (19.45,"50_emu_run_pose_b","emu_run_step_two",(1.08,1.08,.80,1.00,.58,.58)),
    (20.00,"51_emu_run_pose_c","emu_run_step_three",(1.08,1.08,.80,1.00,.58,.58)),
    (20.80,"42_migration_damage_detail","migration_continues",(1.15,1.15,.41,.63,.56,.56)),
    (21.30,"52_emu_turn_pose_a","emu_turn_start",(1.16,1.16,.44,.61,.56,.56)),
    (21.88,"53_emu_turn_pose_b","emu_turn_complete",(1.16,1.16,.46,.65,.56,.56)),
    (23.20,"05_press_blank","newsprint_headline",(1.11,1.11,.50,.60,.58,.58)),
    (24.00,"26_press_page_turn","paper_is_read",(1.17,1.17,.53,.65,.60,.60)),
    (25.66,"41_farmer_news_crop","farmers_need_protection",(1.16,1.16,.42,.62,.56,.56)),
    (26.20,"04_emus_open_sky","look_up_to_sky",(1.50,1.50,.5,.5,.99,.0)),
    (26.66,"10_sky_bridge","time_passes",(1.04,1.04,.46,.54,.44,.44)),
    (27.51,"37_post_sky_new_field","down_to_new_year",(1.50,1.50,.5,.5,.0,.93)),
    (28.85,"06_1934_supply","supplies_in_1934",(1.09,1.09,.45,.53,.54,.54)),
    (30.10,"43_supply_exchange","assistance_handed_over",(1.15,1.15,.45,.59,.56,.56)),
    (31.30,"27_supply_clerk_turn","clerk_reacts",(1.14,1.14,.60,.46,.53,.53)),
    (32.60,"07_bounty_ledger","claims_figure",(1.08,1.08,.44,.51,.54,.57)),
    (33.80,"44_claims_clerk_cards","claims_recorded",(1.15,1.15,.38,.60,.55,.55)),
    (35.35,"28_ledger_turn_start","ledger_turns",(1.14,1.14,.43,.61,.59,.59)),
    (36.40,"08_fence_build","fence_rises",(1.18,1.18,.30,.70,.54,.54)),
    (37.25,"18_fence_wire_action","wire_pulled",(1.18,1.18,.44,.62,.56,.56)),
    (38.05,"55_fence_worker_second_pose","farmers_shift",(1.18,1.18,.35,.68,.58,.58)),
    (39.26,"38_fence_wire_close","wire_fastened",(1.16,1.16,.45,.58,.68,.67)),
    (40.46,"29_fence_post_tighten","post_secured",(1.16,1.16,.38,.64,.58,.58)),
    (42.26,"old_fence_aerial","long_barrier",(1.14,1.14,.32,.70,.47,.47)),
    (44.00,"45_long_fence_protection","protected_fields",(1.12,1.12,.34,.68,.56,.56)),
    (45.35,"39_farmer_fence_walk","farmer_walks",(1.15,1.15,.40,.62,.56,.56)),
    (46.70,"19_final_emu_look","bird_turns_to_leave",(1.12,1.12,.48,.58,.55,.55)),
    (48.00,"40_final_emu_profile","quiet_emus_end",(1.12,1.04,.55,.50,.55,.55)),
]
assert round(SHOTS[-1][0] * FPS) == 1440
assert len({s[1] for s in SHOTS}) == len(SHOTS) == 41
assert not ({"03_farmers_petition_wall","13_farmer_petition_gesture","32_farmer_wheat_close"}
            & {s[1] for s in SHOTS}), "Rejected wheat-table scene returned"
assert {f"{i:02}_" for i in range(46,56)} == {key[:3] for _,key,_,_ in SHOTS if key.startswith(tuple(f"{i:02}_" for i in range(46,56)))}

# Small blends only where a changed image pose or location needs continuity.
# All camera pan/tilt movement itself uses cosine easing at 30 fps.
FADE_AFTER = {"02_departure_sky","48_crop_damage_outdoor_close",
              "49_emu_run_pose_a","50_emu_run_pose_b","52_emu_turn_pose_a",
              "10_sky_bridge","28_ledger_turn_start"}
assert FADE_AFTER <= {s[1] for s in SHOTS[:-1]}
FADE_FRAMES = 4


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
        draw.text((170,571),"NOVEMBER",font=f(cinzel,112),fill="#173B41",stroke_width=2,stroke_fill="#E8E7CD")
        draw.text((170,713),"1932",font=f(anton,350),fill="#E0EF91",stroke_width=3,stroke_fill="#26474C")
    elif key=="old_report":
        draw.text((335,1020),"REPORTED",font=f(cinzel,67),fill="#30423C")
        draw.text((300,1100),"986",font=f(anton,300),fill="#273933")
    elif key=="05_press_blank":
        draw.text((795,1845),"EMU WAR",font=f(anton,68),fill="#283D38")
    elif key=="07_bounty_ledger":
        draw.text((335,1236),"CLAIMS",font=f(cinzel,67),fill="#3E4C42")
        draw.text((330,1323),"57,000+",font=f(anton,228),fill="#293E34")
    return image


def source(key):
    if key=="old_report": return PHASE2/"images"/"04_report.png"
    if key=="old_withdrawal": return PHASE2/"images"/"01_withdrawal.png"
    if key=="old_return": return PHASE2/"images"/"03_return.png"
    if key=="old_fence_aerial": return PHASE2/"images"/"08_fence_aerial.png"
    for folder in (NEW,V4/"images_new",V3/"images_new",V2/"images_new",OLD/"images_new"):
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
    """Original non-melodic soundscape with speech-aware level control.

    Quiet wind, just four bird-like calls and action-matched dry touches.
    Calls are *synthesized emu-inspired textures*, not actual field recordings.
    No music, sample library or imported audio. The unchanged narration controls
    ambience gain so no effect competes with a spoken phrase.
    """
    sr=24000;n=sr*48
    rng=np.random.default_rng(1940)

    def smooth(data,window):
        # O(n) moving average, instead of a long O(n*window) convolution.
        half=window//2
        padded=np.pad(data.astype(np.float32),(half,window-half-1),mode="edge")
        sums=np.cumsum(np.pad(padded,(1,0)),dtype=np.float64)
        return ((sums[window:]-sums[:-window])/window).astype(np.float32)

    times=np.arange(n,dtype=np.float32)/sr
    grain=rng.standard_normal(n).astype(np.float32)
    breeze=smooth(grain,85) + .38*smooth(grain,430)
    breeze/=max(float(np.max(np.abs(breeze))),1e-8)
    gust=.82+.13*np.sin(2*np.pi*.095*times + .4)
    signal=.022*breeze*gust

    def rustle(t,d,level):
        start=int(t*sr);length=min(int(d*sr),n-start)
        noise=smooth(rng.standard_normal(length).astype(np.float32),7)
        noise/=max(float(np.max(np.abs(noise))),1e-8)
        env=np.sin(np.pi*np.linspace(0,1,length,dtype=np.float32))**2
        signal[start:start+length]+=level*noise*env

    def bird_texture(t,d,level,seed):
        start=int(t*sr);length=min(int(d*sr),n-start)
        local=np.random.default_rng(seed)
        noise=smooth(local.standard_normal(length).astype(np.float32),37)
        noise/=max(float(np.max(np.abs(noise))),1e-8)
        x=np.arange(length,dtype=np.float32)/sr
        # A weak irregular glottal component provides character without melody.
        rough=np.sin(2*np.pi*(36*x+5.7*x*x)+.8*np.sin(2*np.pi*2.9*x))
        vocal=.76*noise+.24*rough*(.58+.42*local.random(length).astype(np.float32))
        env=np.sin(np.pi*np.linspace(0,1,length,dtype=np.float32))**2
        signal[start:start+length]+=level*vocal*env

    rustle(9.82,.25,.017)    # stalks
    rustle(16.02,.26,.018)   # report
    bird_texture(18.17,.43,.090,8)
    bird_texture(19.36,.42,.070,17)
    rustle(23.18,.26,.017)   # newsprint
    bird_texture(20.94,.38,.059,27)
    rustle(32.30,.27,.016)   # ledger
    rustle(38.16,.16,.018)   # wire
    bird_texture(46.07,.46,.064,38)

    # Estimate speech presence from ORIGINAL narration, not new speech.
    decoded=subprocess.run([FF,"-hide_banner","-loglevel","error","-i",
                            str(PHASE2/"audio"/"narration.mp3"),"-ac","1",
                            "-ar",str(sr),"-f","f32le","pipe:1"],
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
    voice=np.frombuffer(decoded,dtype="<f4")
    block=480  # 20 ms; smoothed over 180 ms for gradual ducks
    voice=np.pad(voice,(0,(-len(voice))%block)).reshape(-1,block)
    rms=np.sqrt(np.mean(voice*voice,axis=1))
    presence=np.interp(times,(np.arange(len(rms))+.5)*block/sr,
                       np.clip((rms-.013)/.040,0,1)).astype(np.float32)
    presence=smooth(presence,int(.18*sr))
    signal *= (.86-.48*presence)
    signal[:sr]*=np.linspace(0,1,sr,dtype=np.float32)
    signal[-sr:]*=np.linspace(1,0,sr,dtype=np.float32)
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
    with tempfile.TemporaryDirectory(prefix="emu_fast_images_v6_") as work:
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
            output=ROOT/("Emu_War_Fast_Images_Final_v6_8K_Portrait.mp4" if width==4320 else
                         "Emu_War_Fast_Images_Final_v6_1080p_Preview.mp4")
            # 8K requires low-memory x264 preset; a slightly higher CRF keeps
            # the upscaled export below the cloud delivery size limit.
            preset="ultrafast" if width==4320 else "veryfast"
            crf="34.5" if width==4320 else "19"
            run([FF,"-hide_banner","-loglevel","error","-y","-f","concat","-safe","0",
                 "-i",str(playlist),"-i",str(PHASE2/"audio"/"narration.mp3"),"-i",str(foley),
                 "-filter_complex","[0:v]scale="+f"{width}:{height}:flags=lanczos"+"[v];"
                 "[1:a]volume=1.0[voice];[2:a]volume=0.82[fx];"
                 "[voice][fx]amix=inputs=2:duration=longest:normalize=0,alimiter=limit=0.94[a]",
                 "-map","[v]","-map","[a]","-c:v","libx264","-preset",preset,
                 "-crf",crf,"-pix_fmt","yuv420p","-r",str(FPS),
                 "-c:a","aac","-b:a","160k","-ar","48000","-ac","2",
                 "-t","48","-movflags","+faststart",str(output)])
            print(f"OUTPUT {output} ({output.stat().st_size/1024/1024:.1f} MiB)",flush=True)


if __name__=="__main__":
    render()

#!/usr/bin/env python3
"""Render a private 9:16 image-based Ben's Casebook pilot; never uploads to YouTube.

Requires Pillow, numpy, imageio-ffmpeg. All human poses come from separately
generated stills (not a character rig). Multiple distinct evidence stills plus
case-room portrait, later Ben clue pose, and port ending. No music.
"""
from __future__ import annotations
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps
from imageio_ffmpeg import get_ffmpeg_exe

ROOT=Path(__file__).resolve().parent
BRAND=ROOT.parents[1]
ASSETS=ROOT/'assets'
AUDIO=ROOT/'audio'
OUTPUT=ROOT/'Mary_Celeste_Bens_Casebook_DRAFT_1080x1920.mp4'
W,H,FPS=1080,1920,30
WHITE=(250,247,232)
LIME=(210,239,112)
FONT_HEAD=BRAND/'assets/fonts/Anton-Regular.ttf'
FONT_BODY=BRAND/'assets/fonts/DMSans.ttf'
VOICE=[AUDIO/f'{i:02d}_{name}.wav' for i,name in enumerate(
    ['hook','ben','discovery','evidence','hypothesis','end'],1)]


def typography(im,word,small=None):
    d=ImageDraw.Draw(im)
    # The video uses selective contextual words, not persistent subtitles.
    f=ImageFont.truetype(str(FONT_HEAD),110 if len(word)>14 else 126)
    x,y=74,255
    bbox=d.textbbox((0,0),word,font=f)
    if bbox[2]-bbox[0]>855:
        f=ImageFont.truetype(str(FONT_HEAD),round(126*855/(bbox[2]-bbox[0])))
    d.text((x+5,y+6),word,font=f,fill=(4,15,18),stroke_width=3,stroke_fill=(4,15,18))
    d.text((x,y),word,font=f,fill=LIME,stroke_width=1,stroke_fill=(25,31,21))
    if small:
        sf=ImageFont.truetype(str(FONT_BODY),31)
        d.text((x,y+154),small,font=sf,fill=WHITE,stroke_width=2,stroke_fill=(10,24,28))


def cutout(path,corner=None):
    image=Image.open(path).convert('RGB')
    ar=np.array(image,dtype=np.float32)
    if corner is None:corner=np.median(np.concatenate([ar[:30,:30].reshape(-1,3),ar[:30,-30:].reshape(-1,3)]),axis=0)
    diff=np.max(np.abs(ar-np.array(corner,dtype=np.float32)),axis=2)
    alpha=np.uint8(np.clip((diff-10)*(255/39),0,255))
    rgba=image.convert('RGBA');rgba.putalpha(Image.fromarray(alpha,'L'))
    return rgba


def source_image(name):
    # The three affected source PNGs were cleaned before delivery: no
    # screenshot UI, anachronistic foreground tool, or modern port buildings.
    return Image.open(ASSETS/name).convert('RGB')


def plate(name,word=None,small=None,ben=None):
    if name=='case_room':
        image=Image.open(BRAND/'assets/realistic_case_room_background.png').convert('RGB')
    else:
        image=source_image(name)
    image=ImageOps.fit(image,(W,H),method=Image.Resampling.LANCZOS,centering=(.5,.45)).convert('RGBA')
    # Original illustrations, not purported historical photographs.
    shade=Image.new('RGBA',(W,H),(0,0,0,0));sd=ImageDraw.Draw(shade)
    for y in range(0,560,8):
        alpha=round(115*(1-y/560))
        sd.rectangle((0,y,W,y+8),fill=(4,15,20,alpha))
    image=Image.alpha_composite(image,shade)
    if ben:
        if ben=='intro':
            character=Image.open(BRAND/'assets/male_detective_cutout_v2.png').convert('RGBA')
            size=(850,850);xy=(119,577)
        else:
            character=cutout(ASSETS/'detective_ben_clue_pose.png')
            size=(770,770);xy=(152,708)
        image.alpha_composite(character.resize(size,Image.Resampling.LANCZOS),xy)
    im=image.convert('RGB');d=ImageDraw.Draw(im)
    font=ImageFont.truetype(str(FONT_BODY),27)
    d.text((75,110),'ILLUSTRATED RECONSTRUCTION',font=font,fill=(235,236,218),
           stroke_width=1,stroke_fill=(4,15,19))
    if word:typography(im,word,small)
    return im


def read_voice_and_timeline():
    parts=[];starts=[];offset=0;rate=None
    for i,path in enumerate(VOICE):
        with wave.open(str(path),'rb') as w:
            assert w.getnchannels()==1 and w.getsampwidth()==2
            rate=rate or w.getframerate();assert rate==w.getframerate()
            data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
        if i==0:
            # TTS inserted 0.26 s of leading silence; make the mystery hook audible
            # essentially on the first frame while leaving a tiny safety margin.
            data=data[round(rate*.19):]
        starts.append(offset/rate);parts.append(data);offset+=len(data)
        if i<5:
            gap=np.zeros(round(rate*.12),dtype=np.float32)
            parts.append(gap);offset+=len(gap)
    end=offset/rate
    tail=np.zeros(round(rate*.25),dtype=np.float32);parts.append(tail)
    pcm=np.concatenate(parts)
    # Sparse home-made non-melodic paper/sea swishes, safely below narration.
    rng=np.random.default_rng(1872)
    for at,dur in [(starts[1],.24),(starts[3],.17),(starts[4],.18)]:
        n=int(rate*dur);noise=rng.normal(size=n).astype(np.float32)
        smooth=np.convolve(noise,np.ones(36,dtype=np.float32)/36,mode='same')
        envelope=np.sin(np.linspace(0,np.pi,n))**2
        begin=round(at*rate)
        pcm[begin:begin+n]+=smooth*envelope*.018
    pcm=np.clip(pcm,-.98,.98)
    with wave.open(str(AUDIO/'narration_mix.wav'),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        w.writeframes(np.int16(pcm*32767).tobytes())
    return starts,end+len(tail)/rate


def call(args):
    subprocess.run(args,check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)


def main():
    starts,total=read_voice_and_timeline()
    # Boundaries follow the spoken clips exactly; 3 visual phases contain
    # distinct stills and purposeful ~2-4s cuts instead of repeating a scene.
    points=[0,starts[1],starts[2],starts[2]+(starts[3]-starts[2])/2,
            starts[3],starts[3]+(starts[4]-starts[3])/2,starts[4],
            starts[4]+(starts[5]-starts[4])/2,starts[5],total]
    frames=[round(t*FPS) for t in points]
    specs=[
      ('01_ship_at_sea.png','EVERYONE GONE',None,None),
      ('case_room',"BEN'S CASEBOOK",'I\'M BEN. LET\'S FOLLOW THE CLUES.', 'intro'),
      ('02_empty_deck.png','THE MARY CELESTE','1872 · NEAR THE AZORES',None),
      ('03_cabin_belongings.png','TEN MISSING','BELONGINGS LEFT BEHIND',None),
      ('06_empty_davits.png','BOAT GONE',None,None),
      ('04_pump_evidence.png','ONE PUMP',None,None),
      ('08_storm_hypothesis.png','WHY LEAVE?','DETECTIVE BEN EXAMINES THE CLUE','clue'),
      ('07_chart_uncertainty.png','A THEORY','NOT A VERDICT',None),
      ('05_ship_to_port.png','STILL UNSOLVED',None,None),
    ]
    assert len(specs)==len(frames)-1
    ff=get_ffmpeg_exe()
    with tempfile.TemporaryDirectory(prefix='bens_casebook_') as tmpstr:
        tmp=Path(tmpstr);clips=[]
        for i,(name,word,small,ben) in enumerate(specs):
            plate_path=tmp/f'plate_{i:02}.png'
            plate(name,word,small,ben).save(plate_path,optimize=True)
            output=tmp/f'shot_{i:02}.mp4';count=frames[i+1]-frames[i]
            assert count>10,(i,count)
            # Image-based positional movement, no hand-rigged character animation.
            delta=.00046 if i%2==0 else .00037
            effect=f"zoompan=z='min(zoom+{delta},1.06)':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s={W}x{H}:fps={FPS}"
            call([ff,'-hide_banner','-loglevel','error','-loop','1','-framerate',str(FPS),'-i',str(plate_path),
                 '-vf',effect,'-frames:v',str(count),'-c:v','libx264','-preset','veryfast',
                 '-crf','18','-pix_fmt','yuv420p','-r',str(FPS),'-an','-y',str(output)])
            clips.append(output)
            print(f'shot {i+1}/{len(specs)} {count} frames {name}',flush=True)
        concat=tmp/'list.txt'
        concat.write_text(''.join(f"file '{path}'\n" for path in clips))
        silent=tmp/'video_only.mp4'
        call([ff,'-hide_banner','-loglevel','error','-f','concat','-safe','0','-i',str(concat),
              '-c','copy','-y',str(silent)])
        call([ff,'-hide_banner','-loglevel','error','-i',str(silent),'-i',str(AUDIO/'narration_mix.wav'),
              '-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k',
              '-ar','44100','-movflags','+faststart','-shortest','-y',str(OUTPUT)])
    print(f'FINAL {OUTPUT} {OUTPUT.stat().st_size:,} bytes {frames[-1]} frames {frames[-1]/FPS:.2f}s')

if __name__=='__main__':main()

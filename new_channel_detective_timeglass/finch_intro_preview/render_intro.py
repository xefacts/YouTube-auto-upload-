#!/usr/bin/env python3
"""Render a 6.2s original image-based 2D motion-graphics review intro, voice-only.

Uses independently generated key poses, composited optical wipes and manually typeset names.
This is not frame-by-frame hand-drawn character animation.
"""
from pathlib import Path
import math, subprocess, wave
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parent
ASSETS=ROOT/'art'
FONTS=ROOT.parent/'assets'/'fonts'
W,H,FPS,DUR=1080,1920,24,6.2
N=round(FPS*DUR)
INK=(11,39,43); COPPER=(207,151,100); IVORY=(247,242,226)
HEAD=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),116)
HEAD2=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),151)
SMALL=ImageFont.truetype(str(FONTS/'DMSans.ttf'),37)
LITTLE=ImageFont.truetype(str(FONTS/'DMSans.ttf'),27)

def ease(x):
    x=max(0.,min(1.,x));return x*x*(3-2*x)

def prepped(name):
    src=Image.open(ASSETS/name).convert('RGB')
    return ImageOps.fit(src,(1140,2028),Image.Resampling.LANCZOS,centering=(.5,.5))

SCENES=[prepped('01_optical_portrait.png'),prepped('02_archive_transition.png'),prepped('03_hero_title_bg.png')]

def shot(i,t):
    # Distinct pose image, subtle independent camera settle rather than one frozen viewport.
    s=SCENES[i]
    if i==0:
        x=30+int(16*ease(t/1.5)); y=52-int(12*ease(t/1.5))
    elif i==1:
        u=ease((t-1.35)/1.8);x=8+int(46*u);y=46-int(10*u)
    else:
        u=ease((t-2.8)/3.4);x=12+int(25*u);y=46+int(18*u)
    return s.crop((x,y,x+W,y+H))

def nameplate(canvas,t):
    # Deliberately manually typeset, never generated in AI art.
    a=ease((t-.34)/.24)*(1-ease((t-1.22)/.22))
    if a<=.01:return
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    dx=int(43*(1-ease((t-.34)/.28)))
    x=72-dx;y=1427
    d.rounded_rectangle((x,y,x+556,y+130),radius=5,fill=(12,44,46,int(220*a)))
    d.rectangle((x,y,x+7,y+130),fill=(*COPPER,int(255*a)))
    d.text((x+26,y+13),'ARLEN FINCH',font=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),74),fill=(*IVORY,int(255*a)))
    canvas.alpha_composite(layer)

def iris_transition(front,back,t):
    q=ease((t-1.32)/.44)
    if q<=0:return front
    if q>=1:return back
    # Expanding optical aperture; lens rim is a matte, not a magical glow.
    r=int(10+2550*q);cx=1250;cy=925
    mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask)
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(9))
    result=Image.composite(back,front,mask)
    dd=ImageDraw.Draw(result)
    dd.ellipse((cx-r,cy-r,cx+r,cy+r),outline=COPPER,width=7)
    return result

def archive_transition(front,back,t):
    q=ease((t-2.76)/.54)
    if q<=0:return front
    if q>=1:return back
    # Film-style archive-card shape wipe; no generic cross-dissolve or sci-fi tunnel.
    mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask)
    edge=int(-110+q*(W+220))
    if edge>0:d.rectangle((0,0,edge,H),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(8))
    result=Image.composite(back,front,mask)
    dd=ImageDraw.Draw(result);dd.rectangle((edge-5,0,edge+2,H),fill=COPPER)
    return result

def archive_wordmark(canvas,t):
    a=ease((t-1.85)/.35)*(1-ease((t-2.83)/.25))
    if a<=.01:return
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    d.rounded_rectangle((568,884,1053,1154),radius=7,fill=(8,37,41,int(205*a)))
    d.rectangle((595,918,1008,924),fill=(*COPPER,int(255*a)))
    f1=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),67)
    f2=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),113)
    d.text((593,946),'THE ARLEN',font=f1,fill=(*IVORY,int(255*a)))
    d.text((588,1025),'ARCHIVE',font=f2,fill=(*IVORY,int(255*a)))
    canvas.alpha_composite(layer)

def title(canvas,t):
    a=ease((t-3.12)/.42)
    if a<=0:return
    layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
    # Masked reveal moves across stationary typography rather than fake AI lettering.
    d.text((72,614),'THE ARLEN',font=ImageFont.truetype(str(FONTS/'Anton-Regular.ttf'),89),fill=(*IVORY,255))
    d.text((69,715),'ARCHIVE',font=HEAD2,fill=(*IVORY,255))
    d.text((75,899),'ARLEN FINCH',font=SMALL,fill=(*COPPER,255))
    d.rectangle((72,966,72+int(481*ease((t-3.47)/.73)),972),fill=(*COPPER,255))
    mask=Image.new('L',(W,H),0)
    ImageDraw.Draw(mask).rectangle((0,0,int(65+a*630),H),fill=255)
    layer.putalpha(Image.fromarray(__import__('numpy').minimum(__import__('numpy').array(layer.getchannel('A')),__import__('numpy').array(mask)).astype('uint8')))
    canvas.alpha_composite(layer)

def frame(t):
    a=shot(0,t)
    if t<1.32:
        out=a
    elif t<1.76:
        out=iris_transition(a,shot(1,t),t)
    elif t<2.76:out=shot(1,t)
    elif t<3.30:out=archive_transition(shot(1,t),shot(2,t),t)
    else:out=shot(2,t)
    out=out.convert('RGBA')
    if t<1.44:nameplate(out,t)
    if 1.85<t<3.08:archive_wordmark(out,t)
    if t>3.12:title(out,t)
    return out.convert('RGB')

def render():
    audio=ROOT/'audio/arlen_brand_voice.wav'
    with wave.open(str(audio),'rb') as f:
        voice_len=f.getnframes()/f.getframerate()
    assert .15+voice_len<DUR, f'Voice clips: {voice_len:.2f}s > runtime'
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    out=ROOT/'ARLEN_ARCHIVE_INTRO_REVIEW_6s.mp4'
    cmd=[ff,'-y','-hide_banner','-loglevel','error',
        '-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
        '-i',str(audio),'-filter_complex',f'[1:a]adelay=150,apad,atrim=0:{DUR}[v]',
        '-map','0:v:0','-map','[v]','-c:v','libx264','-preset','veryfast','-crf','19',
        '-pix_fmt','yuv420p','-r',str(FPS),'-c:a','aac','-b:a','192k',
        '-t',str(DUR),'-movflags','+faststart','-shortest',str(out)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for n in range(N):
            pic=frame(n/FPS)
            proc.stdin.write(pic.tobytes())
        proc.stdin.close()
        err=proc.stderr.read().decode('utf8',errors='replace');code=proc.wait()
        if code:raise RuntimeError(err)
    except Exception:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
        proc.kill();raise
    frame(4.8).save(ROOT/'PREVIEW_POSTER.png',optimize=True)
    print('Wrote',out,out.stat().st_size,'bytes',f'{N} frames',f'{DUR}s','voice',f'{voice_len:.3f}s')

if __name__=='__main__':render()

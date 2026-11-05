#!/usr/bin/env python3
"""V13 private, original-illustration cut: vector-ink proof sequence + supplied music.

The selected 36.4955s narration is uncut. Original SVG annotations and fictional
blood are authored in assets/. Train 2/Text references guide pacing only; no
reference pixels, audio, marks, logos or wording are reused. This export is
4320x7680 *upscaled* from 1080x1920 animation and smaller illustrated sources.
"""
from pathlib import Path
from xml.etree import ElementTree
import math, re, subprocess, wave
import numpy as np
from scipy.signal import butter, sosfilt
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageFilter
import imageio_ffmpeg
import render_v12 as prev

HERE=Path(__file__).resolve().parent
EP=HERE.parent
REPO=HERE.parents[3]
A=HERE/'assets'; CACHE=HERE/'render_cache'; CACHE.mkdir(exist_ok=True)
SFX=REPO/'work/v12_user_sfx'
W,H,FPS,DUR=prev.W,prev.H,prev.FPS,prev.DUR
FF=imageio_ffmpeg.get_ffmpeg_exe()
v11=prev.v11
EASE=v11.old.ease

# Preserve the same PRISM artwork and fixed shoe locations. Ease the camera,
# never tween the drawn limbs or move the grounded sprite across a floor.
reframed=[]
for a,b,key,z0,z1,c0,c1 in v11.SHOTS:
    if key.startswith('prism') or key in ('hall_open','door_half','wife','wife_turn','partner'):
        z1=min(z1,z0+.025)
        c1=(c0[0]+.35*(c1[0]-c0[0]),c0[1]+.35*(c1[1]-c0[1]))
    reframed.append((a,b,key,z0,z1,c0,c1))
v11.SHOTS=reframed
# Thin light fringes from a white studio key are eroded BEFORE the composite.
# Never change face, height scaling, garment colour or selected identity.
for name in ('prism_corridor_stand','prism_suite_look','prism_balcony_stand','prism_reach_v12'):
    sprite=v11.SPRITES[name]
    alpha=sprite.getchannel('A').filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.55))
    sprite.putalpha(alpha)

# Render the hand-authored SVG once at source resolution; load only fictional,
# non-graphic accents into the already continuous illustrated flashback.
# Pre-rasterized from assets/v13_blood_marks.svg with resvg-js 2.6.2.
# Keep the original editable vector master; runtime needs no SVG browser/Node.
raster=A/'v13_blood_marks.png'
marks=Image.open(raster).convert('RGBA')
assert marks.size==v11.IM['falling'].size==v11.IM['collapsed'].size

def add_stain(im,box):
    layer=Image.new('RGBA',im.size)
    layer.paste(marks.crop(box),box[:2])
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')
v11.IM['falling']=add_stain(v11.IM['falling'],(580,690,695,770))
v11.IM['collapsed']=add_stain(v11.IM['collapsed'],(580,772,695,840))
flash_after=add_stain(v11.IM['flashback'],(580,690,695,770))
old_plate=v11.plate_for

def plate_with_impact(t,key):
    if key=='flashback' and t>=3.35:return flash_after
    return old_plate(t,key)
v11.plate_for=plate_with_impact

# Five original clues; each proof image is seen BIG before its dossier card.
# No invented proof of a particular killer, watch time or historic event.
labels=['FIBER ON THE COAT','THREAD ON THE RAIL','BOLT ACROSS THE GAP',
        'THE SUITE DOOR','FOOTPRINTS TO BALCONY']
images=[v11.IM['coat'].crop((100,750,490,1160)),
        v11.IM['thread_art'].crop((140,500,550,1080)),
        v11.IM['bolt_closed'],v11.IM['door_closed'],
        v11.grade(Image.open(EP/'phase2/05_footprints_to_balcony.png').convert('RGB')).crop((175,650,620,1160))]
# Individual aspect-aware crops: no stretched anatomy or distorted objects.
photos=[ImageOps.fit(im,(720,910),method=Image.Resampling.LANCZOS,centering=(.5,.5)) for im in images]
PAPER=prev.PAPER
F_TITLE=ImageFont.truetype(str(prev.ROOT/'assets/fonts/Anton-Regular.ttf'),45)
F_CARD=ImageFont.truetype(str(prev.ROOT/'assets/fonts/Anton-Regular.ttf'),32)
F_SMALL=ImageFont.truetype(str(prev.ROOT/'assets/fonts/DMSans.ttf'),24)
INK=(174,45,53,255)

def fitting_text(draw,text,font,max_width):
    while draw.textbbox((0,0),text,font=font)[2]>max_width:
        font=ImageFont.truetype(str(prev.ROOT/'assets/fonts/Anton-Regular.ttf'),font.size-1)
    return font

hero_cards=[]; board_cards=[]
for im,label in zip(photos,labels):
    card=Image.new('RGBA',(752,1006),(245,238,221,255))
    card.paste(im,(16,16))
    d=ImageDraw.Draw(card)
    d.rectangle((2,2,749,1003),outline=(102,89,77,255),width=3)
    font=fitting_text(d,label,F_TITLE,708)
    d.text((28,937),label,font=font,fill=(38,44,43,255))
    hero_cards.append(card)
    thumb=ImageOps.fit(im,(388,347),method=Image.Resampling.LANCZOS,centering=(.5,.5))
    small=Image.new('RGBA',(420,435),(246,239,223,255))
    small.paste(thumb,(16,16))
    d=ImageDraw.Draw(small)
    d.rectangle((2,2,417,432),outline=(95,89,78,255),width=2)
    font=fitting_text(d,label,F_CARD,388)
    d.text((16,370),label,font=font,fill=(36,43,45,255))
    board_cards.append(small)

# These cubic paths are parsed from the editable SVG master, not hardcoded arcs.
# Sampling an authored Bezier is a vector-driven stroke reveal at native 1080p.
root=ElementTree.parse(A/'v13_clue_ink.svg').getroot()
paths={x.attrib['id']:x.attrib['d'] for x in root.iter() if 'id' in x.attrib and 'd' in x.attrib}

def cubic_points(d):
    tokens=re.findall(r'[MC]|-?\d+(?:\.\d+)?',d)
    assert tokens[0]=='M'
    p=(float(tokens[1]),float(tokens[2])); points=[p]
    i=3
    while i<len(tokens):
        assert tokens[i]=='C';q=[float(x) for x in tokens[i+1:i+7]];i+=7
        p1=(q[0],q[1]);p2=(q[2],q[3]);p3=(q[4],q[5])
        for k in range(1,22):
            t=k/21;u=1-t
            points.append((u*u*u*p[0]+3*u*u*t*p1[0]+3*u*t*t*p2[0]+t*t*t*p3[0],
                           u*u*u*p[1]+3*u*u*t*p1[1]+3*u*t*t*p2[1]+t*t*t*p3[1]))
        p=p3
    return points
strokes={k:cubic_points(d) for k,d in paths.items()}
assert len(strokes)==11

def trace(d,path,progress,width):
    n=max(2,round(len(strokes[path])*max(0,min(1,progress))))
    if progress>0:d.line(strokes[path][:n],fill=INK,width=width,joint='curve')

# Board always has legible 2-column pictures, with a final centered fifth card.
positions=[(100,185),(560,185),(100,695),(560,695),(330,1205)]
sequence=[28.80,29.95,31.10,32.25,33.40,34.55]
names=['fiber','thread','bolt','door','prints']

def lower_caption(im,label,alpha=1):
    # Lower image zone, not a footer or an upper headline. Editorial labels only.
    if alpha<=.001:return im
    box=Image.new('RGBA',im.size)
    d=ImageDraw.Draw(box)
    font=fitting_text(d,label,F_TITLE,820)
    tw=d.textbbox((0,0),label,font=font)[2]
    x=(W-tw)//2;y=1518
    d.rounded_rectangle((x-29,y-13,x+tw+29,y+72),radius=13,fill=(18,29,33,round(215*alpha)))
    d.rectangle((x-29,y-13,x-23,y+72),fill=(171,53,58,round(230*alpha)))
    d.text((x,y),label,font=font,fill=(249,241,223,round(255*alpha)))
    return Image.alpha_composite(im.convert('RGBA'),box).convert('RGB')

# Other labels are short and not asserted to be a verbatim word-level transcript.
nonclue_cues=[(6.98,8.75,'THE CLOSED DOOR'),(16.02,17.05,'THE SLIDE BOLT'),
              (26.38,28.46,'THREAD ON THE RAIL')]

def clue_closeup(t):
    idx=next(i for i in range(5) if sequence[i]<=t<sequence[i+1])
    q=t-sequence[idx]
    # Source photo remains still while camera makes a 1.5% eased push.
    back=PAPER.copy()
    d=ImageDraw.Draw(back,'RGBA')
    d.line((70,138,1010,138),fill=(121,104,78,90),width=2)
    z=1.0+.014*EASE(q/1.15)
    x=round(164+16*EASE(q/.25))
    y=round(322+11*EASE(q/.25))
    card=hero_cards[idx]
    shadow=Image.new('RGBA',back.size)
    ImageDraw.Draw(shadow).rounded_rectangle((x+17,y+22,x+card.width+20,y+card.height+25),
                                             radius=8,fill=(18,23,25,105))
    back=Image.alpha_composite(back.convert('RGBA'),shadow.filter(ImageFilter.GaussianBlur(18)))
    back.alpha_composite(card,(x,y))
    # SVG coords are on the landed card, so the ink starts AFTER its short entrance.
    d=ImageDraw.Draw(back,'RGBA')
    trace(d,'hero-'+names[idx],EASE((q-.27)/.56),9)
    result=v11.crop(back.convert('RGB'),z,(.5,.5))
    # The photo-card itself carries the necessary lower label; do not repeat it.
    return result

def final_board(t):
    q=t-34.55
    im=PAPER.copy().convert('RGBA')
    for i,(card,(x,y)) in enumerate(zip(board_cards,positions)):
        enter=EASE((q-i*.075)/.33)
        if enter<.001:continue
        yy=round(y+32*(1-enter))
        sh=Image.new('RGBA',im.size)
        ImageDraw.Draw(sh).rectangle((x+12,yy+14,x+card.width+14,yy+card.height+15),fill=(23,20,17,65))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(13)))
        im.alpha_composite(card,(x,yy))
    d=ImageDraw.Draw(im,'RGBA')
    for i,name in enumerate(names):
        trace(d,'board-'+name,EASE((q-.36-i*.07)/.41),5)
    # Five independent purposeful rings; do not draw a spurious causal link.
    z=1.035-.035*EASE(q/1.05)
    return v11.crop(im.convert('RGB'),z,(.5,.50))

def frame(t):
    if t>=34.55:return final_board(t)
    if t>=28.80:return clue_closeup(t)
    image=prev.frame(t)
    if t<2.2:return image  # Centered typewriter intro; no upper third overlay.
    for a,b,label in nonclue_cues:
        if a<=t<b:
            fade=min(EASE((t-a)/.28),EASE((b-t)/.26))
            return lower_caption(image,label,fade)
    return image

def soundtrack():
    """Uncut selected VO + provided dramatic music and synchronized user SFX."""
    sr=48000;n=int(sr*DUR)
    voice=v11.old.read_audio(EP/'audio/voice_full_1934_edit.mp3',sr)
    assert 36.48<len(voice)/sr<=DUR, 'Selected complete voice missing'
    audio=np.zeros((n,2),np.float32)
    audio[:len(voice)]+=(.90*voice)[:,None]
    rng=np.random.default_rng(1313)
    def source(filename):
        path=SFX/filename
        if not path.exists():raise FileNotFoundError(f'Private supplied audio missing: {path}')
        return v11.old.read_audio(path,sr)
    def put(at,sig,pan=0):
        start=round(at*sr)
        if start>=n:return
        z=np.asarray(sig[:n-start],np.float32)
        audio[start:start+len(z),0]+=z*math.sqrt((1-pan)/2)
        audio[start:start+len(z),1]+=z*math.sqrt((1+pan)/2)
    music=source('hitslab-tension-suspense-mystery-629029.mp3')
    # Track's last ~5 sec naturally fade. Restart underneath it with a gentle
    # crossfade, then duck musical level according to the *real* voice envelope.
    bed=np.zeros(n,np.float32)
    for at in (0.,21.0):
        start=int(at*sr);length=min(len(music),n-start)
        seg=music[:length].copy()
        if at>0:seg*=np.minimum(1,np.arange(length,dtype=np.float32)/(1.0*sr))
        bed[start:start+length]+=seg
    block=480
    rms=np.sqrt(np.mean(np.pad(voice,(0,(-len(voice))%block)).reshape(-1,block)**2,axis=1))
    smooth=np.convolve(rms,np.ones(17,dtype=np.float32)/17,mode='same')
    duck=.040+.020*np.clip((.011-smooth)/.011,0,1)
    gain=np.repeat(duck,block)[:n]
    gain*=np.minimum(1,np.arange(n,dtype=np.float32)/(sr*.9))
    gain*=np.minimum(1,np.arange(n-1,-1,-1,dtype=np.float32)/(sr*.48))
    # Dramatic but never masking VO; reserve headroom for SFX on impact.
    gain[int(3.20*sr):int(5.0*sr)]*=.68
    audio[:,0]+=bed*gain*.95
    audio[:,1]+=bed*gain*1.05
    gun=source('freesound_community-single-gunshot-54-40780.mp3')
    scream=source('universfield-male-death-scream-123078.mp3')
    laugh=source('dragon-studio-evil-laugh-with-reverb-423668.mp3')
    put(3.34,.23*gun[:int(sr*1.10)],-.16) # one animated shot, one report
    put(3.25,.17*scream[:int(sr*1.78)],.12) # sampled onset ~shot frame
    put(4.22,.075*laugh[:int(sr*1.30)],-.20) # distant, not proof of perpetrator
    # Sparse original physical foley only on events (not a second soundtrack).
    def thud(at,amp):
        z=np.arange(int(.48*sr),dtype=np.float32)/sr
        q=sosfilt(butter(2,310,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        put(at,amp*q*np.exp(-z*13),.2)
    thud(4.17,.19);thud(6.80,.30)
    for at in (15.98,28.80,29.95,31.10,32.25,33.40,34.55):
        z=np.arange(int(.11*sr),dtype=np.float32)/sr
        tap=sosfilt(butter(2,[720,3300],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        put(at,.026*tap*np.exp(-z*33),-.2 if at<29 else .2)
    # Soft safety limiter does not truncate the final intelligible word. Source
    # waveform ends in silence after ~36.3; no isolated terminal p is verifiable.
    audio=np.tanh(audio*.97)
    peak=float(np.max(abs(audio)))
    if peak>.94:audio*=.94/peak
    wav=CACHE/'v13_complete_vo_supplied_music_sfx.wav'
    with wave.open(str(wav),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr)
        out.writeframes((audio*32767).astype('<i2').tobytes())
    print('AUDIO',len(voice)/sr,'s source voice preserved, peak',peak,flush=True)
    return wav

if __name__=='__main__':
    wav=soundtrack()
    raw=CACHE/'silent_v13_1080.mp4'
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-c:v','libx264',
         '-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*4)==0:print('frame',k,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('1080 animation encode failed')
    finally:
        if p.poll() is None:p.kill()
    out=HERE/'FLORIDA_V13_SVG_CLUES_PRIVATE_REVIEW_8K_UPSCALED.mp4'
    # 4320x7680 = vertical 8K raster; source photographs are much smaller.
    subprocess.run([FF,'-y','-loglevel','error','-threads','1','-filter_threads','1',
        '-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
        '-vf','scale=4320:7680:flags=bicubic',
        '-c:v','libx264','-threads','1','-preset','ultrafast','-crf','29',
        '-x264-params','ref=1:rc_lookahead=0:bframes=0','-pix_fmt','yuv420p',
        '-af','loudnorm=I=-18:TP=-1.5:LRA=9',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
        '-shortest',str(out)],check=True)
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

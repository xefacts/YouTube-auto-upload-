#!/usr/bin/env python3
"""V12 private Florida cut: typed red-ink intro, original moving evidence collage,
user-supplied SFX, larger grounded PRISM action. Full original selected narration
still ends at 36.5s. No third-party reference frames or unapproved music.
"""
from pathlib import Path
import importlib.util
import math
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from scipy.signal import butter, sosfilt
import imageio_ffmpeg

HERE=Path(__file__).resolve().parent
EP=HERE.parent
ROOT=HERE.parents[2]
REPO=HERE.parents[3]
A=HERE/'assets'
CACHE=HERE/'render_cache'; CACHE.mkdir(exist_ok=True)
USER_SFX=REPO/'work/v12_user_sfx'
spec=importlib.util.spec_from_file_location('florida_v11',HERE/'render_v11.py')
v11=importlib.util.module_from_spec(spec);spec.loader.exec_module(v11)
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,DUR=v11.W,v11.H,v11.FPS,v11.DUR
assert (W,H,FPS,DUR)==(1080,1920,24,36.5)

# Keep every existing timed narrative beat through the thread study. Only the
# ending becomes the requested all-clues sequence, not another generic title.
SHOTS=[]
for sh in v11.SHOTS:
    a,b,key,*rest=sh
    if key=='exterior':
        SHOTS.append((a,b,'intro',*rest))
    elif key=='prism_balcony':
        SHOTS.extend([(a,14.10,key,*rest),(14.10,b,'prism_reach',1.05,1.12,(.43,.57),(.45,.57))])
    elif key=='prism_thread':
        SHOTS.extend([(a,25.10,key,*rest),(25.10,b,'prism_reach_thread',1.06,1.12,(.45,.57),(.46,.58))])
    elif key=='rail_thread':
        SHOTS.append((a,28.80,key,*rest))
    elif a<29.10:
        SHOTS.append(sh)
SHOTS.append((28.80,DUR,'evidence_board',1,1,(.5,.5),(.5,.5)))
assert all(a[1]==b[0] for a,b in zip(SHOTS,SHOTS[1:])),SHOTS
assert SHOTS[-1][1]==DUR
v11.SHOTS=SHOTS
v11.CUES=[]  # remove all generic "CASE NOTES" story headings
# Protect feet: change scale within the same full-body art, never translate
# feet around the floor during a shot. Ground y=1282 for balcony poses.
for key,height in (('prism_corridor',760),('prism_suite',710),('prism_balcony',710),('prism_thread',710)):
    plate,x,y,_=v11.ACTORS[key]
    v11.ACTORS[key]=(plate,x,y,height)
# A bent pose is physically shorter than the upright pose; keep shoe soles at
# the identical floor y, and reduce its graphic scale to match head/hand size.
v11.ACTORS['prism_reach']=('balcony',430,1282,620)
v11.ACTORS['prism_reach_thread']=('balcony',430,1282,620)
v11.SPRITES['prism_reach_v12']=v11.grade(v11.prism_isolate('prism_balcony_reach_v12'))
original_plate=v11.plate_for

def plate_for(t,key):
    if key not in ('prism_reach','prism_reach_thread'):
        return original_plate(t,key)
    plate,x,y,h=v11.ACTORS[key]
    fg=v11.SPRITES['prism_reach_v12']
    fg=fg.resize((round(fg.width*h/fg.height),h),Image.Resampling.LANCZOS)
    bg=v11.IM[plate].convert('RGBA')
    px,py=round(x-fg.width/2),round(y-h)
    sh=Image.new('RGBA',bg.size)
    ImageDraw.Draw(sh).ellipse((px+fg.width*.17,y-11,px+fg.width*.87,y+12),fill=(0,0,0,126))
    bg=Image.alpha_composite(bg,sh.filter(ImageFilter.GaussianBlur(9)))
    bg.alpha_composite(fg,(px,py))
    return bg.convert('RGB')
v11.plate_for=plate_for

# Red ink is editorial art, not actual blood. One purposeful intro title replaces
# the four unsynced stock-style headings. Keypress ticks align to actual letters.
INTRO=v11.grade(Image.open(A/'florida_typewriter_red_intro.png').convert('RGB'))
INK=ImageFont.truetype(str(ROOT/'assets/fonts/Anton-Regular.ttf'),70)
LABEL=ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'),22)
TITLE='THE LOCKED\nSUITE'
CHAR_TIMES=[.38+i*.095 for i in range(len(TITLE.replace('\n','')))]

def typed_intro(t):
    z=1.025+.065*v11.old.ease(t/2.2)
    im=v11.crop(INTRO,z,(.5,.51))
    typed=sum(t>=x for x in CHAR_TIMES)
    letters=TITLE.replace('\n','')[:typed]
    line1=letters[:10]  # 'THE LOCKED' => 10 characters
    line2=letters[10:]
    d=ImageDraw.Draw(im,'RGBA')
    # Restrained ink on the actual paper plane, not floating lower-third text.
    if t>.10:
        d.text((405,665),'FICTIONAL DRAMATIZATION',font=LABEL,fill=(80,67,62,200))
    d.text((407,735),line1,font=INK,fill=(108,21,29,255))
    d.text((407,820),line2,font=INK,fill=(108,21,29,255))
    if .40<t<1.98 and int(t*5)%2==0:
        txt=line2 if len(letters)>10 else line1
        tw=d.textbbox((0,0),txt,font=INK)[2]
        y=820 if len(letters)>10 else 735
        d.rectangle((410+tw,y+5,415+tw,y+62),fill=(119,29,35,175))
    return im

# Original assets on aged paper, inspired by the *motion language* of the Train 2
# Tuk-Tuk and Thai Ghosts references: cut-out photos, stagger, annotating strokes.
# No reference stills, logos, text, people or sound ever appear in the output.
rng=np.random.default_rng(1212)
noise=rng.normal(0,2.2,(H,W)).astype(np.float32)
ly=np.arange(H,dtype=np.float32)[:,None]/H
lx=np.arange(W,dtype=np.float32)[None,:]/W
paper=np.empty((H,W,3),np.uint8)
for ch,base in enumerate((225,212,188)):
    paper[:,:,ch]=np.uint8(np.clip(base-10*ly+2*lx+noise,0,255))
PAPER=Image.fromarray(paper,'RGB')
FIBER=ImageOps.fit(v11.IM['coat'],(390,445),method=Image.Resampling.LANCZOS,centering=(.58,.50))
DOOR=ImageOps.fit(v11.IM['door_closed'],(365,385),method=Image.Resampling.LANCZOS,centering=(.50,.49))
THREAD=ImageOps.fit(v11.IM['thread_art'],(475,450),method=Image.Resampling.LANCZOS,centering=(.68,.53))
LATCH=ImageOps.fit(v11.IM['bolt_closed'],(340,360),method=Image.Resampling.LANCZOS,centering=(.50,.53))
FOOTPRINTS=ImageOps.fit(v11.grade(Image.open(EP/'phase2/05_footprints_to_balcony.png').convert('RGB')),(410,370),method=Image.Resampling.LANCZOS,centering=(.50,.72))
HOTEL=ImageOps.fit(v11.IM['exterior'],(380,380),method=Image.Resampling.LANCZOS,centering=(.50,.38))
CARD_SOURCES=[FIBER,DOOR,THREAD,LATCH,FOOTPRINTS,HOTEL]
CARD_SPECS=[# x,y,rotation(deg), entrance seconds, slides from left/right
    # First photo is mostly landed by the incoming cut: never start on blank paper.
    (94,180,3,28.32,-1), (562,170,-4,29.54,1),
    (96,760,-3,30.46,-1), (625,780,5,31.26,1),
    (130,1290,4,32.22,-1), (598,1270,-5,33.18,1)]
# A brief larger forensic photo precedes each small pinned card. This is key for
# 9:16 phone readability: users see the actual thread/fiber/bolt before the
# six-image final board. No reference-video image is reused.
HERO_SOURCES=[
    v11.IM['coat'].crop((140,680,510,1175)),
    v11.IM['door_closed'],
    v11.IM['thread_art'].crop((155,525,535,1080)),
    v11.IM['bolt_closed'],
    v11.grade(Image.open(EP/'phase2/05_footprints_to_balcony.png').convert('RGB')),
    v11.IM['exterior']]
HERO_CENTERS=[(.5,.5),(.62,.55),(.5,.5),(.42,.52),(.50,.70),(.50,.34)]
HEROES=[]
for image,center in zip(HERO_SOURCES,HERO_CENTERS):
    photo=ImageOps.fit(image,(676,820),method=Image.Resampling.LANCZOS,centering=center)
    card=Image.new('RGBA',(700,880),(248,244,231,255))
    card.paste(photo,(12,12))
    ImageDraw.Draw(card).rectangle((0,0,699,879),outline=(111,91,70,255),width=3)
    HEROES.append(card)
CARDS=[]
for im,(x,y,angle,at,side) in zip(CARD_SOURCES,CARD_SPECS):
    # Nearly monochrome documentary prints with traces of teal/rust remaining.
    photo=ImageEnhance.Color(im).enhance(.55)
    card=Image.new('RGBA',(photo.width+22,photo.height+58),(248,243,227,255))
    card.paste(photo,(11,11))
    ImageDraw.Draw(card).rectangle((0,0,card.width-1,card.height-1),outline=(124,110,89,255),width=2)
    rotated=card.rotate(angle,resample=Image.Resampling.BICUBIC,expand=True)
    CARDS.append((rotated,x,y,at,side))

def evidence_board(t):
    im=PAPER.copy().convert('RGBA')
    d=ImageDraw.Draw(im,'RGBA')
    # Offset lines suggest archival paper; no fabricated historical captions.
    for y in (130,650,1220,1840):
        d.line((50,y,W-60,y),fill=(130,107,82,65),width=2)
    visible=[]
    for i,(card,x,y,at,side) in enumerate(CARDS):
        progress=v11.old.ease((t-at)/.45)
        if progress<=.001:continue
        px=round(x+side*(1-progress)*680)
        py=round(y+(1-progress)*70)
        shadow=Image.new('RGBA',im.size)
        ImageDraw.Draw(shadow).rounded_rectangle((px+15,py+17,px+card.width+17,py+card.height+17),radius=8,fill=(25,23,20,70))
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
        im.alpha_composite(card,(px,py))
        visible.append((px,py,card.width,card.height,i))
    d=ImageDraw.Draw(im,'RGBA')
    # Kinetic ink markers land on relevant *own* photos, not imported graphics.
    targets=[(.37,.77),(.64,.55),(.45,.55),(.36,.45),(.49,.50),(.49,.49)]
    for x,y,w,h,i in visible:
        at=CARD_SPECS[i][3]+.48
        u=v11.old.ease((t-at)/.45)
        if u<=0:continue
        cx=x+w*targets[i][0];cy=y+h*targets[i][1]
        r=36+(i%3)*10
        d.arc((cx-r,cy-r,cx+r,cy+r),-45,-45+330*u,fill=(155,34,39,round(235*u)),width=5)
        if i in (0,2,4):
            d.line((x+18,y+h-42,x+18+u*w*.52,y+h-48),fill=(159,39,46,round(200*u)),width=6)
    # Final relationship line is hand-annotated after evidence has arrived.
    u=v11.old.ease((t-34.05)/1.2)
    if u>0:
        d.line((385,565,385+u*310,565+u*310),fill=(145,37,45,int(195*u)),width=4)
        d.line((660,1050,660-u*120,1050+u*340),fill=(145,37,45,int(195*u)),width=4)
    # Track each clue as it lands, then ease out to show the complete six-photo
    # board before the selected narrator's last syllable. No abrupt zoom jumps.
    camera=[
        (28.80,1.16,.32,.30),(29.52,1.22,.33,.29),
        (30.26,1.17,.68,.30),(31.17,1.18,.36,.54),
        (32.12,1.16,.68,.54),(33.05,1.15,.34,.75),
        (34.05,1.13,.70,.76),(35.28,1.025,.50,.50),
        (36.50,1.00,.50,.50)]
    for (t0,z0,x0,y0),(t1,z1,x1,y1) in zip(camera,camera[1:]):
        if t<=t1:
            e=v11.old.ease((t-t0)/(t1-t0))
            z=z0+(z1-z0)*e
            focus=(x0+(x1-x0)*e,y0+(y1-y0)*e)
            break
    else:z=1.0;focus=(.5,.5)
    result=v11.crop(im.convert('RGB'),z,focus).convert('RGBA')
    # Featured card appears large and legible for a beat, then returns to its
    # pinned slot. The final 2s resolve into the complete board with no overlay.
    for i,card in enumerate(HEROES):
        at=CARD_SPECS[i][3]
        next_at=CARD_SPECS[i+1][3] if i+1<len(CARD_SPECS) else 34.40
        if not at<=t<next_at:continue
        enter=v11.old.ease((t-at)/.16)
        leave=v11.old.ease((t-(next_at-.34))/.30)
        alpha=enter*(1-leave)
        if alpha<.01:break
        px,py=round(184+(1-enter)*380),round(265+(1-enter)*85)
        sh=Image.new('RGBA',result.size)
        ImageDraw.Draw(sh).rectangle((px+15,py+18,px+card.width+15,py+card.height+18),fill=(25,19,17,round(90*alpha)))
        result=Image.alpha_composite(result,sh.filter(ImageFilter.GaussianBlur(17)))
        layer=card.copy()
        layer.putalpha(layer.getchannel('A').point(lambda v:round(v*alpha)))
        result.alpha_composite(layer,(px,py))
        break
    return result.convert('RGB')

def frame(t):
    if t<2.2:return typed_intro(t)
    if t>=28.80:return evidence_board(t)
    return v11.frame(t)


def soundtrack():
    """Full selected VO + conservative non-melodic bed + user's private SFX.

    No ruling on religious permissibility is implied; provided musical background
    is deliberately NOT mixed pending the user's own decision. Missing private
    samples fall back to original procedural accents, not a false claim of use.
    """
    sr=48000;n=int(DUR*sr)
    rng=np.random.default_rng(1208)
    a=np.zeros((n,2),np.float32)
    voice=v11.old.read_audio(EP/'audio/voice_full_1934_edit.mp3',sr)
    assert len(voice)<=n and n-len(voice)<.02*sr
    a[:len(voice),:]+=(.88*voice)[:,None]
    def add(at,sig,pan=0):
        ix=int(at*sr)
        if ix>=n:return
        sig=np.asarray(sig[:n-ix],np.float32)
        a[ix:ix+len(sig),0]+=sig*math.sqrt((1-pan)/2)
        a[ix:ix+len(sig),1]+=sig*math.sqrt((1+pan)/2)
    def source(name,seconds):
        path=USER_SFX/name
        if path.exists():return v11.old.read_audio(path,sr)[:int(seconds*sr)]
        print('PRIVATE SFX ABSENT; procedural fallback:',name,flush=True)
        return None
    # Independent spatial air and rain; explicitly NON-musical/no pitched bed.
    for ch in (0,1):
        r=rng.normal(0,1,n).astype(np.float32)
        lo=sosfilt(butter(2,880,fs=sr,output='sos'),r).astype(np.float32)
        a[:,ch]+=.0030*(r-lo)
    r=rng.normal(0,1,n).astype(np.float32)
    wind=sosfilt(butter(2,110,fs=sr,output='sos'),r).astype(np.float32)
    a+=.11*wind[:,None]
    # Foley for red typewriter: actual letter-onset ticks, not click spam.
    for i,at in enumerate(CHAR_TIMES):
        z=np.arange(int(.08*sr),dtype=np.float32)/sr
        c=sosfilt(butter(2,[500,3600],fs=sr,btype='bandpass',output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        add(at,((.026+.005*(i%3))*c*np.exp(-z*52)),pan=(-.3 if i%2 else .3))
    # User-supplied effects are included only in this owner-only review. Keep
    # dialogue centered and legible, trim sample tails (not the selected VO).
    gun=source('freesound_community-single-gunshot-54-40780.mp3',1.06)
    scream=source('universfield-male-death-scream-123078.mp3',1.70)
    laugh=source('dragon-studio-evil-laugh-with-reverb-423668.mp3',1.80)
    if gun is not None:add(3.34,.23*gun,pan=-.20)
    else:
        z=np.arange(int(.65*sr),dtype=np.float32)/sr
        add(3.34,.18*rng.normal(0,1,len(z)).astype(np.float32)*np.exp(-z*18),pan=-.2)
    if scream is not None:add(3.25,.15*scream,pan=.16) # audible attack ~3.34s
    if laugh is not None:add(4.05,.13*laugh,pan=-.16)
    # Original chair, wood door and latch; quiet, sparse spatial details.
    def thud(at,scale=.1):
        z=np.arange(int(.56*sr),dtype=np.float32)/sr
        q=sosfilt(butter(2,340,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        add(at,scale*q*np.exp(-z*13),pan=.15)
    thud(4.17,.16)
    z=np.arange(int(.89*sr),dtype=np.float32)/sr
    rub=sosfilt(butter(2,[170,1000],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
    add(5.91,.06*rub*np.sin(np.pi*z/.89)**2,pan=.15)
    thud(6.80,.43)
    for at,amp in ((15.96,.045),(24.68,.025),(28.88,.030),(30.46,.024),(33.18,.024)):
        z=np.arange(int(.16*sr),dtype=np.float32)/sr
        sw=sosfilt(butter(2,[800,2900],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        add(at,amp*sw*np.exp(-z*29),pan=(-.20 if at<20 else .20))
    # A breath of filtered air anticipates each purposeful transition.
    for at,duration,amp in ((2.1,.55,.08),(24.35,.7,.08),(28.55,1.05,.10),(34.35,1.2,.07)):
        z=np.arange(int(duration*sr),dtype=np.float32)
        q=sosfilt(butter(2,240,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        add(at,amp*q*np.sin(np.pi*z/len(z))**2,pan=-.26)
    a=np.tanh(a*1.02)
    peak=np.max(np.abs(a))
    if peak>.95:a*=.95/peak
    path=CACHE/'v12_user_sfx_nonmusical_stereo.wav'
    with wave.open(str(path),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr)
        out.writeframes((a*32767).astype('<i2').tobytes())
    return path

if __name__=='__main__':
    wav=soundtrack()
    raw=CACHE/'silent_v12_1080.mp4'
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-c:v','libx264',
         '-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*5)==0:print('frame',k,flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('1080p video encoding failed')
    finally:
        if p.poll() is None:p.kill()
    out=HERE/'FLORIDA_V12_RED_INK_ALL_CLUES_PRIVATE_REVIEW_4K_UPSCALED.mp4'
    # 4K-size output from lower-res illustrated sources, not native 4K artwork.
    # Single-thread no-lookahead path avoids earlier memory-related encoder OOM.
    subprocess.run([FF,'-y','-loglevel','error','-threads','1','-filter_threads','1',
        '-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
        '-vf','scale=2160:3840:flags=bicubic',
        '-c:v','libx264','-threads','1','-preset','ultrafast','-crf','25',
        '-x264-params','ref=1:rc_lookahead=0:bframes=0','-pix_fmt','yuv420p',
        '-af','loudnorm=I=-18:TP=-1.5:LRA=8',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
        '-shortest',str(out)],check=True)
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

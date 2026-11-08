#!/usr/bin/env python3
"""V17 private review: original narration, illustrated evidence-room ending,
source-consistent darker death passage, non-melodic procedural sound design.
No theological certification: the soundscape uses no instruments, melody, or beat.
"""
from pathlib import Path
import math, subprocess, wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.signal import butter,sosfilt
import render_v16 as old

HERE=Path(__file__).resolve().parent
EP=HERE.parent
W,H,FPS,DUR,FF=old.W,old.H,old.FPS,old.DUR,old.FF
EASE=old.EASE
v11=old.v11
BACK=Image.open(HERE/'assets/v17_evidence_room_backplate.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
ANTON=old.FONT
SANS=old.SANS
# Deep side walls, practical light, and one coherent shared grade.
arr=np.asarray(BACK.convert('RGB')).astype(np.float32)
yy,xx=np.mgrid[0:H,0:W]
fall=np.clip(1-.29*((xx-W*.5)/(W*.56))**2-.20*((yy-H*.53)/(H*.65))**2,.50,1)
arr*=fall[:,:,None]
BACK=Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB').convert('RGBA')

def label_font(size):return ImageFont.truetype(ANTON,size)
def body_font(size):return ImageFont.truetype(SANS,size)

def card_layer(i,x,y,scale,e):
    """Reuses the *actual* V15 five marked clue photographs, not generated facts."""
    original=old.old.marked[i]
    w,h=original.size
    im=original.resize((round(w*scale),round(h*scale)),Image.Resampling.LANCZOS)
    if e<1:
        a=im.getchannel('A').point(lambda z:round(z*e))
        im.putalpha(a)
    X=round(x);Y=round(y+(1-e)*46)
    return im,(X,Y)

# The finished physical image is assembled before the camera moves: two larger
# competing clues, three smaller context clues, no fabricated new evidence.
PLACES=[(0,140,420,.88),(1,565,420,.88),
        (2,128,897,.59),(3,415,897,.59),(4,702,897,.59)]
STILL=BACK.copy()
for idx,x,y,scale in PLACES:
    im,pos=card_layer(idx,x,y,scale,1)
    sh=Image.new('RGBA',(im.width+40,im.height+50),(0,0,0,0))
    ImageDraw.Draw(sh).rounded_rectangle((15,15,im.width+24,im.height+30),radius=14,fill=(0,0,0,165))
    STILL.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)),(pos[0]-18,pos[1]-11))
    STILL.alpha_composite(im,pos)
    d=ImageDraw.Draw(STILL,'RGBA')
    pinx=pos[0]+im.width//2;piny=pos[1]+11
    d.ellipse((pinx-6,piny-6,pinx+6,piny+6),fill=(222,165,88,255))
    d.ellipse((pinx-2,piny-3,pinx+2,piny+1),fill=(255,225,156,230))
# Opening dossier heading is set into negative space above the clue photos.
d=ImageDraw.Draw(STILL,'RGBA')
d.text((133,267),'THE LOCKED SUITE',font=label_font(68),fill=(235,213,178,250),stroke_width=1,stroke_fill=(19,13,13,255))
d.text((137,346),'A FICTIONAL CASE  /  FIVE CLUES',font=body_font(24),fill=(198,171,138,255))
d.line((135,396,920,396),fill=(160,112,76,170),width=2)
# A physical dossier slip, placed below *all* five pieces of evidence.
SLIP=Image.new('RGBA',(908,389),(0,0,0,0))
s=ImageDraw.Draw(SLIP,'RGBA')
s.rounded_rectangle((6,7,901,379),radius=13,fill=(20,22,23,246),outline=(170,113,75,240),width=3)
s.rectangle((47,42,55,102),fill=(196,58,59,255))
s.text((75,38),'THE DETAIL THAT STAYS WITH YOU',font=body_font(26),fill=(216,178,143,255))
s.text((47,92),'THE SUITE',font=label_font(83),fill=(244,227,197,255))
s.text((47,173),'WAS LOCKED.',font=label_font(83),fill=(244,227,197,255))
s.line((47,278,844,278),fill=(149,99,75,190),width=2)
s.text((47,287),'EXPLAIN THE THREAD.',font=label_font(61),fill=(217,79,74,255))
SLIP=SLIP.rotate(-.45,Image.Resampling.BICUBIC,expand=False)

def end_frame(t):
    q=max(0,t-36.90)
    # Transition from the existing evidence wall into the new illustrated
    # physical board: no generic black screen, no direct comment instruction.
    image=STILL.copy()
    u=EASE((q-.22)/.73)
    if u>0:
        slip=SLIP.copy()
        slip.putalpha(slip.getchannel('A').point(lambda a:round(a*u)))
        image.alpha_composite(slip,(86,round(1178+(1-u)*35)))
    # Slow motivated push toward the two fiber/thread proofs; don't hide text.
    z=1.012+.018*EASE(q/2.2)
    image=v11.crop(image.convert('RGB'),z,(.5,.50)).convert('RGBA')
    if q<.22:
        prev=old.old.final_collage(36.78).convert('RGBA')
        image=Image.blend(prev,image,EASE(q/.22))
    # Brief moving tungsten investigation light; texture remains visible.
    s=math.exp(-((q-.7)/.45)**2)*.038
    if s>.001:
        image=Image.blend(image,Image.new('RGBA',image.size,(241,204,154,255)),s)
    return image.convert('RGB')

# One fixed radial lighting matte rather than a new inconsistent generated actor.
fy,fx=np.mgrid[0:H,0:W]
rad=np.sqrt(((fx-W*.61)/(W*.69))**2+((fy-H*.48)/(H*.72))**2)
DARK=np.clip(1-.49*rad**1.65,.42,1).astype(np.float32)

def death_frame(t):
    scene=old.frame(t)
    # At 4.15 the source switches to an illustrated static collapse pose. A
    # closer camera hides stiff legs and retains *the same* face, suit and set.
    if 4.15<=t<5.2:
        p=EASE((t-4.15)/1.05)
        scene=v11.crop(scene,1.37+.11*p,(.70,.58))
    a=np.asarray(scene).astype(np.float32)
    strength=.5+.5*EASE((t-3.31)/.55)
    a*=1-strength*(1-DARK[:,:,None])
    # Practical lamp goes out after the flash: the left side remains dim but
    # the wound/face is readable. Nothing is redrawn as an extra character.
    shadow=np.clip((fx-W*.26)/(W*.68),0,1).astype(np.float32)
    a*=1-(.08*strength*shadow[:,:,None])
    if 3.35<=t<3.56:
        pulse=math.exp(-21*(t-3.35))
        a=a*(1-.11*pulse)+np.array([226,151,105])[None,None,:]*(.11*pulse)
    return Image.fromarray(np.uint8(np.clip(a,0,255)))

def frame(t):
    if t>=36.90:return end_frame(t)
    if 3.30<=t<5.20:return death_frame(t)
    return old.frame(t)

# All procedural material is unpitched, aperiodic noise and transient envelopes.
# No instruments, melody, singing, bass notes or rhythmic music. Religious
# permissibility itself is NOT something software can guarantee or certify.
def soundtrack(voice_only=False):
    sr=48000;n=round(DUR*sr)
    voice=v11.old.read_audio(EP/'audio/voice_full_1934_edit.mp3',sr)
    assert 36.48<len(voice)/sr<36.50
    out=np.zeros((n,2),np.float32)
    out[:len(voice),:]=voice[:,None] # original words, timing, speed, and gain
    if not voice_only:
        fx=np.zeros_like(out)
        rng=np.random.default_rng(1703)
        def noise(seconds,cutoff=None,kind='lowpass'):
            a=rng.standard_normal(round(seconds*sr)).astype(np.float32)
            if cutoff:
                a=sosfilt(butter(2,cutoff,kind,fs=sr,output='sos'),a).astype(np.float32)
            return a
        def put(at,a,level=1.0,pan=0.0):
            start=round(sr*at)
            z=np.asarray(a,np.float32)
            if start>=n:return
            z=z[:n-start]*level
            fx[start:start+len(z),0]+=z*math.sqrt((1-pan)/2)
            fx[start:start+len(z),1]+=z*math.sqrt((1+pan)/2)
        live=round(sr*38.83)
        # Low ventilation pressure and gritty rainy glass: aperiodic, not a drone.
        for ch in (0,1):
            air=noise(live/sr,155)
            grit=noise(live/sr,620,'highpass')
            # Slowly wandering stochastic envelope, no meter or recurring beat.
            knots=rng.uniform(.63,1.0,19)
            env=np.interp(np.arange(live),np.linspace(0,live-1,len(knots)),knots)
            fx[:live,ch]+=(.105*air+.0030*grit)*env
        # The shot interrupts the room tone; air falls out rather than swells.
        fall0,fall1=round(3.34*sr),round(4.11*sr)
        fade=np.linspace(.56,.69,fall1-fall0,dtype=np.float32)
        fx[fall0:fall1,:]*=fade[:,None]
        def hit(at,seconds,level,pan=0.0,low=450):
            raw=noise(seconds)
            lp=sosfilt(butter(2,low,fs=sr,output='sos'),raw).astype(np.float32)
            t=np.arange(len(raw),dtype=np.float32)/sr
            sound=(.65*raw+.35*lp)*np.exp(-t*19)
            put(at,sound,level,pan)
        # Six short unpitched scene moments, deliberately non-periodic.
        for at,level in ((.23,.019),(.54,.018),(.90,.018),(15.96,.014),
                         (24.38,.012),(36.73,.012)):
            hit(at,.14,level,-.17,1800)
        # Shot: close crack + a muffled hotel-wall reflection + chair movement.
        hit(3.34,.62,.20,-.24,390)
        hit(3.405,.38,.065,.18,310)
        hit(3.77,.51,.050,.12,225)
        hit(4.13,.69,.042,.19,175)
        # Uneven room creaks and clue-paper handling, not a pulse.
        for at,level in ((6.81,.027),(10.78,.019),(16.02,.023),
                         (23.92,.018),(26.75,.015),(32.20,.014),(34.60,.021),
                         (37.17,.013)):
            hit(at,.35,level,(at%3-1)*.25,440)
        # Suspense is largely absence: short irregular high-frequency air draw.
        for at,length,level in ((2.85,.43,.0039),(14.87,.56,.0036),
                                (28.18,.55,.0038),(36.78,.44,.0030)):
            nse=noise(length,240,'highpass')
            env=np.sin(np.pi*np.linspace(0,1,len(nse)))**1.8
            put(at,nse*env,level,.2)
        # Taper into quiet instead of hard-cutting noisy ambience.
        fade_start,fade_end=round(38.16*sr),round(38.84*sr)
        fx[fade_start:fade_end]*=np.linspace(1,0,fade_end-fade_start,dtype=np.float32)[:,None]
        fx[fade_end:]=0
        # No broadband limiting on the narration; only FX may be attenuated.
        if np.max(np.abs(out+fx))>.97:
            fx*=.97/np.max(np.abs(out+fx))
        out+=fx
    assert np.max(abs(out))<.98
    dest=old.v13.CACHE/('v17_voice_only.wav' if voice_only else 'v17_unpitched_room_film_sound.wav')
    dest.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(dest),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((out*32767).astype('<i2').tobytes())
    print('AUDIO',dest.name,'narration length',len(voice)/sr,'peak',np.max(np.abs(out)),flush=True)
    return dest

if __name__=='__main__':
    wav=soundtrack()
    out=HERE/'FLORIDA_V17_DARK_MYSTERY_PRIVATE_REVIEW_1080x1920.mp4'
    cmd=[FF,'-y','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r',str(FPS),'-i','pipe:0','-i',str(wav),'-map','0:v',
         '-map','1:a','-c:v','libx264','-threads','2','-preset','medium','-crf','19',
         '-maxrate','8M','-bufsize','16M','-profile:v','high','-level:v','4.2',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000',
         '-movflags','+faststart','-shortest',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(5*FPS)==0:print('frame',k,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('V17 encode failed')
    finally:
        if p.poll() is None:p.kill()
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

#!/usr/bin/env python3
"""V18: source-narration-preserving illustrated COMMENT BELOW finish.
The soundbed uses recorded rain/wind/thunder/footsteps/impacts plus the existing
spoken alarm; no synthesized tonal bed, instruments, tune, song or rhythmic music.
No religious certification is asserted.
"""
from pathlib import Path
import subprocess,wave,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import render_v17 as old

HERE=Path(__file__).resolve().parent
EP=HERE.parent
A=HERE/'assets'
S=A/'v18_cc0_weather'
W,H,FPS,DUR,FF=old.W,old.H,old.FPS,old.DUR,old.FF
EASE=old.EASE
v11=old.v11
ANTON=old.ANTON
SANS=old.SANS
OUT=HERE/'FLORIDA_V18_NATURAL_VOCAL_COMMENT_PRIVATE_REVIEW_1080x1920.mp4'
CARD=HERE/'FLORIDA_V18_COMMENT_ENDCARD_1080x1920.png'

def font(size,heavy=False):
    return ImageFont.truetype(ANTON if heavy else SANS,size)

def centered(draw,text,y,f,fill,stroke_width=0,stroke_fill=None):
    l,t,r,b=draw.textbbox((0,0),text,font=f,stroke_width=stroke_width)
    draw.text(((W-(r-l))//2-l,y),text,font=f,fill=fill,
              stroke_width=stroke_width,stroke_fill=stroke_fill)

def make_endcard(words=True):
    """A bespoke finished image: original two clue photos on the same new board."""
    im=old.BACK.copy()
    d=ImageDraw.Draw(im,'RGBA')
    # Physical top evidence: no invented culprit, no generated clue content.
    for i,x,ang in ((0,132,-2.2),(1,569,2.2)):
        photo=old.old.old.marked[i].resize((376,387),Image.Resampling.LANCZOS)
        photo=photo.rotate(ang,Image.Resampling.BICUBIC,expand=True)
        y=377+(4 if i else 0)
        shadow=Image.new('RGBA',(photo.width+45,photo.height+50))
        ImageDraw.Draw(shadow).rounded_rectangle((14,14,photo.width+29,photo.height+30),
                                                 radius=12,fill=(0,0,0,155))
        im.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(19)),(x-13,y-8))
        im.alpha_composite(photo,(x,y))
        d=ImageDraw.Draw(im,'RGBA')
        px=x+photo.width//2
        d.ellipse((px-7,y+4,px+7,y+18),fill=(214,157,90,255))
        d.ellipse((px-2,y+7,px+2,y+11),fill=(255,221,153,250))
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((373,280,381,343),fill=(205,62,57,255))
    d.text((405,272),'CASE FILE 001  /  FICTIONAL MYSTERY',font=font(29),fill=(205,184,151,255))
    d.line((375,357,970,357),fill=(156,119,89,210),width=3)
    # Handmade archival paper occupies center; glyphs are rendered in code,
    # never entrusted to generative typography. 1080-wide safe text margins.
    s=Image.new('RGBA',(970,628))
    z=ImageDraw.Draw(s,'RGBA')
    z.rounded_rectangle((19,20,954,615),radius=24,fill=(11,20,24,244),
                        outline=(184,131,90,245),width=4)
    z.line((45,42,927,42),fill=(215,173,121,125),width=2)
    z.text((76,66),'WHO LEFT THE THREAD?',font=font(68,True),
           fill=(242,226,192,255),stroke_width=2,stroke_fill=(27,16,17,255))
    z.line((76,164,885,164),fill=(166,100,82,190),width=3)
    z.rectangle((70,205,82,352),fill=(194,55,54,255))
    if words:
        z.text((115,187),'COMMENT',font=font(136,True),fill=(241,226,197,255),
               stroke_width=3,stroke_fill=(31,22,24,255))
        z.text((115,345),'BELOW',font=font(147,True),fill=(221,77,68,255),
               stroke_width=3,stroke_fill=(32,21,22,255))
        z.line((115,522,844,522),fill=(208,64,59,255),width=10)
    z.text((118,548),'EVERY CASE LEAVES A TRACE',font=font(29),fill=(200,168,138,255))
    # Soft texture in the glassless black backing (does not damage letterforms).
    im.alpha_composite(s,(55,820))
    d=ImageDraw.Draw(im,'RGBA')
    # Red evidence-thread arrow physically points down, never to a fake clue.
    d.line((505,1460,512,1512,523,1544),fill=(194,68,60,230),width=6,joint='curve')
    d.line((504,1530,523,1544,543,1528),fill=(194,68,60,230),width=6)
    d.text((167,1662),'THE LOCKED SUITE',font=font(35,True),fill=(198,167,134,220))
    d.text((168,1715),'A CASE EMBER STORY',font=font(25),fill=(168,150,129,220))
    im=im.convert('RGB')
    CARD.parent.mkdir(parents=True,exist_ok=True)
    if words:im.save(CARD,optimize=True)
    return im
BASE=make_endcard(words=False)
POSTER=make_endcard(words=True)
WORD1=Image.new('RGBA',(W,H))
wd=ImageDraw.Draw(WORD1,'RGBA')
wd.text((170,1007),'COMMENT',font=font(136,True),fill=(241,226,197,255),
        stroke_width=3,stroke_fill=(31,22,24,255))
WORD2=Image.new('RGBA',(W,H))
wd=ImageDraw.Draw(WORD2,'RGBA')
wd.text((170,1165),'BELOW',font=font(147,True),fill=(221,77,68,255),
        stroke_width=3,stroke_fill=(32,21,22,255))
wd.line((170,1342,899,1342),fill=(208,64,59,255),width=10)

def frame(t):
    # Final 1.95 s is an image-led prompt with two clean text beats and a slow
    # physical push. Preserve existing earlier death scene and every voice cue.
    if t<37.30:return old.frame(t)
    q=t-37.30
    image=BASE.convert('RGBA')
    for layer,when in ((WORD1,.14),(WORD2,.55)):
        e=EASE((q-when)/.36)
        if e>0:
            overlay=layer.copy()
            overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*e)))
            image=Image.alpha_composite(image,overlay)
    z=1.014+.028*EASE(q/1.95)
    im=v11.crop(image.convert('RGB'),z,(.5,.49))
    if q<.16:
        return Image.blend(old.frame(37.28),im,EASE(q/.16))
    return im

def decode(path,sr=48000):
    raw=subprocess.check_output([FF,'-v','error','-i',str(path),'-ar',str(sr),
                                 '-ac','1','-f','f32le','pipe:1'])
    return np.frombuffer(raw,dtype='<f4').copy()

def loop_recording(src,n,fade=.25):
    """Crossfade actual field recording loops, no synthesis/periodic melody."""
    overlap=round(fade*48000)
    out=np.zeros(n,np.float32)
    pos=0
    while pos<n:
        end=min(pos+len(src),n)
        size=end-pos
        if pos and size>overlap:
            ramp=np.linspace(0,1,overlap,dtype=np.float32)
            out[pos:pos+overlap]=out[pos:pos+overlap]*(1-ramp)+src[:overlap]*ramp
            out[pos+overlap:end]=src[overlap:size]
        else:out[pos:end]=src[:size]
        pos=end-overlap if end<n else n
    return out

def soundtrack():
    sr=48000;n=round(DUR*sr)
    voice=decode(EP/'audio/voice_full_1934_edit.mp3')
    assert 36.48<len(voice)/sr<36.50
    mix=np.zeros((n,2),np.float32)
    mix[:len(voice),:]=voice[:,None]
    fx=np.zeros_like(mix)
    def put(at,sig,amp,pan=0):
        k=round(at*sr)
        sig=np.asarray(sig[:max(0,n-k)],np.float32)
        if not len(sig):return
        fx[k:k+len(sig),0]+=sig*amp*math.sqrt((1-pan)/2)
        fx[k:k+len(sig),1]+=sig*amp*math.sqrt((1+pan)/2)
    def clean(name):
        a=decode(S/name)
        a-=np.mean(a)
        rms=np.sqrt(np.mean(a*a))
        assert rms>.0001,(name,rms)
        return a
    rain=loop_recording(clean('rain-heavy.ogg'),n)
    light=loop_recording(clean('rain-light.ogg'),n)
    wind=loop_recording(clean('wind.ogg'),n)
    # Original recordings, not generated low-frequency oscillators or drum beat.
    # Preplanned room geography: rain grows at the balcony and with the clues.
    t=np.arange(n,dtype=np.float32)/sr
    exterior=np.exp(-((t-13.7)/3.1)**2)+.9*np.exp(-((t-26.8)/3.4)**2)
    env=np.minimum(1,(t+.18)/.70)*np.minimum(1,(DUR-t+.16)/.60)
    bed=(.062*rain + .044*light + (.027+.025*exterior)*wind)*env
    fx[:,0]+=.94*bed
    fx[:,1]+=bed
    # Keep narrator clear by ducking recorded environment, not touching voice.
    duck=np.ones(n,dtype=np.float32)
    duck[round(3.34*sr):round(4.20*sr)]=.45
    fx*=duck[:,None]
    # Genuine one-shot field recordings, never looped into a rhythmic track.
    shot=clean('shot_rifle.ogg')
    wood=clean('impact_wood.ogg')
    stone=clean('stone.ogg')
    thunder=clean('thunder1.ogg')
    put(3.34,shot,.22,-.28)
    alarm=decode(A/'businessman_alarm.wav')
    put(3.26,alarm[:round(.85*sr)],.13,.18) # existing human exclamation
    put(4.14,wood,.12,.20)  # chair/wood, immediately after the fall
    put(4.3,thunder,.035,-.05) # distant real thunder outside hotel
    for at in (7.08,7.89,8.68):put(at,stone[:round(.32*sr)],.038,-.27)
    put(16.04,wood[:round(.24*sr)],.035,-.1) # bolt/door contact
    put(24.50,stone[:round(.21*sr)],.018,.25)
    put(37.82,wood[:round(.21*sr)],.030,.0) # single card-settle at CTA
    # Stop with natural fade, no offscreen musical sting after the final text.
    stop0=round(38.77*sr)
    fx[stop0:]*=np.linspace(1,0,n-stop0,dtype=np.float32)[:,None]
    if np.max(abs(mix+fx))>.96:fx*=.96/np.max(abs(mix+fx))
    stem=old.old.v13.CACHE/'V18_NATURAL_VOCAL_SOUND_DESIGN_STEM.wav'
    with wave.open(str(stem),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((fx*32767).astype('<i2').tobytes())
    mix+=fx
    assert np.max(abs(mix))<.98
    wav=old.old.v13.CACHE/'v18_natural_field_recordings_vocal_alarm.wav'
    with wave.open(str(wav),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((mix*32767).astype('<i2').tobytes())
    print('AUDIO original VO',len(voice)/sr,'s','peak',np.max(abs(mix)),flush=True)
    return wav

if __name__=='__main__':
    wav=soundtrack()
    cmd=[FF,'-y','-v','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r',str(FPS),'-i','pipe:0','-i',str(wav),'-map','0:v',
         '-map','1:a','-c:v','libx264','-threads','2','-preset','medium','-crf','19',
         '-maxrate','8M','-bufsize','16M','-profile:v','high','-level:v','4.2',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000',
         '-movflags','+faststart','-shortest',str(OUT)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(5*FPS)==0:print('frame',k,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('V18 encode failed')
    finally:
        if p.poll() is None:p.kill()
    print('DELIVERABLE',OUT,OUT.stat().st_size,flush=True)

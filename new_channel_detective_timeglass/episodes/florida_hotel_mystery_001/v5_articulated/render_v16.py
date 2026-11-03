#!/usr/bin/env python3
"""V16 evidence-led cinematic revision. Narration/story remain untouched.

The original selected VO waveform is decoded once at 48 kHz and placed at the
same starting sample and speed with unity gain: no transcription, stretch,
trimming, denoising, remix through a vocal effect, or rewritten narration.
No melodic background music; non-pitched rain/air and sparse scene SFX only.
This is honest source-based 2.5D compositing, not a claim of native 3D footage.
"""
from pathlib import Path
import math,subprocess,wave
import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.signal import butter,sosfilt
import render_v15 as old

HERE=Path(__file__).resolve().parent
EP=HERE.parent
ROOT=old.old.ROOT
A=HERE/'assets'
W,H,FPS,DUR=old.W,old.H,old.FPS,old.DUR
VOICE_END=old.VOICE_END
FF=old.FF
EASE=old.EASE
v11=old.v11
v13=old.old.base
v12=v13.prev
FONT=str(ROOT/'assets/fonts/Anton-Regular.ttf')
SANS=str(ROOT/'assets/fonts/DMSans.ttf')

# Subtle shared light treatment on the SAME selected actor art, once per sprite.
# Motivated warm camera-left practical and blue-green camera-right shadow.
for name in ('prism_corridor_stand','prism_suite_look','prism_reach_v12',
             'wife_master','wife_turn_pose','partner_master','partner_case_pose'):
    if name not in v11.SPRITES:continue
    im=v11.SPRITES[name]
    a=np.asarray(im).copy()
    w=a.shape[1];xx=np.linspace(-1,1,w,dtype=np.float32)[None,:,None]
    rgb=a[:,:,:3].astype(np.float32)
    warm=np.clip(-xx,0,1)
    cool=np.clip(xx,0,1)
    rgb[:,:,0:1]+=4.2*warm-2.0*cool
    rgb[:,:,1:2]+=2.1*warm+0.3*cool
    rgb[:,:,2:3]-=1.5*warm-3.0*cool
    a[:,:,:3]=np.uint8(np.clip(rgb,0,255))
    v11.SPRITES[name]=Image.fromarray(a)
v11.SPRITES['prism_balcony_stand']=v11.SPRITES['prism_suite_look']

# The source suit is already painted directly into the same room image (not an
# overlaid white-background sprite). Recompose the stylized chest stain as
# dyed *fabric texture*, rather than a flat red decal, on the original plates.
marks=np.array(Image.open(A/'v13_blood_marks.png').convert('RGBA'))[:,:,3].astype(np.float32)/255

def fabric_stain(filename,box):
    src=v11.grade(Image.open(A/filename).convert('RGB'))
    original=np.asarray(src).astype(np.float32)
    y0,y1=box[1],box[3];x0,x1=box[0],box[2]
    factor=(marks[y0:y1,x0:x1,None]**1.1)*.72
    original[y0:y1,x0:x1,:]=original[y0:y1,x0:x1,:]*(1-factor)+np.array([95,20,27])[None,None,:]*factor
    return Image.fromarray(np.uint8(np.clip(original,0,255)))
v11.IM['falling']=fabric_stain('florida_suite_falling_consistent.png',(580,690,695,770))
v11.IM['collapsed']=fabric_stain('florida_suite_collapse_consistent.png',(580,772,695,840))
v13.flash_after=fabric_stain('florida_suite_shooter_consistent.png',(580,690,695,770))

# A typeset image is projected INTO the original angled typewriter page. This
# replaces the floating, small flat title; chosen title words and meaning remain.
page=Image.new('RGBA',(440,430))
page_draw=ImageDraw.Draw(page,'RGBA')
serif=ImageFont.truetype(SANS,21)
font_small=ImageFont.truetype(FONT,62)
font_big=ImageFont.truetype(FONT,90)
page_draw.text((250,111),'FICTIONAL',font=serif,fill=(82,68,61,240))
page_draw.text((39,88),'THE',font=font_small,fill=(116,29,36,255))
page_draw.text((36,151),'LOCKED',font=font_big,fill=(101,23,31,255))
page_draw.text((36,251),'SUITE',font=font_big,fill=(101,23,31,255))
page_draw.line((40,366,329,366),fill=(141,51,55,210),width=4)
# The original title words are animated by opacity reveal, not a flat cursor.
# 768×1376 source-plane quadrilateral, calibrated from paper edges.
src=np.float32([[0,0],[440,0],[440,430],[0,430]])
dst=np.float32([[284,385],[659,341],[604,755],[238,780]])
transform=cv2.getPerspectiveTransform(src,dst)

def projected_intro(t):
    q=np.asarray(page).copy()
    # Reveal headline row by row with a thin typewriter wipe; caption stays.
    for lo,hi,start in ((83,165,.23),(150,269,.54),(250,377,.90)):
        e=EASE((t-start)/.38)
        cutoff=round(hi*e+lo*(1-e))
        q[cutoff:hi,:,3]=0
    if t<1.32:q[378:430,:,3]=0
    title=cv2.warpPerspective(q,transform,v12.INTRO.size,
                              flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_CONSTANT,
                              borderValue=(0,0,0,0))
    image=Image.alpha_composite(v12.INTRO.convert('RGBA'),Image.fromarray(title))
    z=1.018+.055*EASE(t/2.2)
    return v11.crop(image.convert('RGB'),z,(.50,.51))
v12.typed_intro=projected_intro

# End on the SAME visible evidence board, not an unrelated black CTA. Audio is
# silent beyond the selected narrator; the question is an editorial invitation,
# not an assertion that a suspect or solution was proven.
QUESTION='WHO LEFT THE THREAD?'
PROMPT='COMMENT YOUR THEORY'
qfont=ImageFont.truetype(FONT,83)
pfont=ImageFont.truetype(SANS,37)
qbox=Image.new('RGBA',(W,H))
d=ImageDraw.Draw(qbox,'RGBA')
d.rounded_rectangle((76,734,1004,1175),radius=24,fill=(7,17,22,220),
                    outline=(173,123,78,245),width=3)
d.rectangle((112,773,120,845),fill=(205,63,60,255))
d.text((153,759),'THE UNANSWERED QUESTION',font=ImageFont.truetype(SANS,29),
       fill=(211,172,126,255))
while d.textbbox((0,0),QUESTION,font=qfont)[2]>845:
    qfont=ImageFont.truetype(FONT,qfont.size-2)
d.text((111,850),QUESTION,font=qfont,fill=(249,237,215,255))
d.text((112,1011),PROMPT,font=pfont,fill=(213,207,192,255))
d.line((112,1080,420,1080),fill=(207,60,62,255),width=7)
board_plate=old.final_collage(36.78).convert('RGBA')

def evidence_question(t):
    q=t-36.90
    slow=EASE(q/2.35)
    im=v11.crop(board_plate.convert('RGB'),1+.027*slow,(.5,.5)).convert('RGBA')
    # Charcoal shade protects text, but the real five labeled photos remain seen.
    shade=Image.new('RGBA',im.size,(4,13,18,round(68*EASE(q/.56))))
    im=Image.alpha_composite(im,shade)
    e=EASE((q-.13)/.60)
    overlay=qbox.copy()
    overlay.putalpha(overlay.getchannel('A').point(lambda a:round(a*e)))
    # Confine question text to safe central area; no unsupported top labels.
    im=Image.alpha_composite(im,overlay)
    return im.convert('RGB')

# A tiny shared post-grade (not frame-varying auto-exposure) preserves detail in
# dark skin and clothing while keeping practical lights warm and evidence red.
post=[]
for c,shift in enumerate((0,0,-1)):
    post.extend(int(np.clip(np.interp(k,[0,22,80,150,223,255],
                                    [3,25+shift,81+shift,151,223,252]),0,255))
                for k in range(256))

def frame(t):
    if t<2.2:return projected_intro(t).point(post)
    if t>=36.90:return evidence_question(t)
    image=old.frame(t)
    if 3.34<=t<3.46:
        energy=math.exp(-23*(t-3.34))
        image=Image.blend(image,Image.new('RGB',image.size,(203,169,110)),.060*energy)
    # Stable source-plane camera drift through two longer character holds;
    # no warping facial anatomy or letting feet slide against the hotel floor.
    for a,b,p0,p1 in ((17.20,20.22,(.50,.50),(.51,.50)),
                      (20.22,24.30,(.49,.50),(.52,.50))):
        if a<=t<b:
            e=EASE((t-a)/(b-a))
            image=v11.crop(image,1+.018*e,
                           (p0[0]+(p1[0]-p0[0])*e,p0[1]))
            break
    return image.point(post)

# No theological verdict is claimed. For private review we conservatively use
# NO pitched or melodic music. Only naturalistic noise and user's scene SFX.
def soundtrack():
    sr=48000;n=int(DUR*sr)
    voice=v11.old.read_audio(EP/'audio/voice_full_1934_edit.mp3',sr)
    assert 36.48<len(voice)/sr<=36.5
    mix=np.zeros((n,2),np.float32)
    mix[:len(voice),0]=voice
    mix[:len(voice),1]=voice
    fx=np.zeros((n,2),np.float32)
    rng=np.random.default_rng(1606)
    def put(at,signal,pan=0):
        start=round(at*sr)
        z=np.asarray(signal[:max(0,n-start)],np.float32)
        if len(z):
            fx[start:start+len(z),0]+=z*math.sqrt((1-pan)/2)
            fx[start:start+len(z),1]+=z*math.sqrt((1+pan)/2)
    # Non-pitched hotel rain and room air stop BEFORE the silent end question.
    n_live=int(VOICE_END*sr)
    for channel in (0,1):
        noise=rng.normal(0,1,n_live).astype(np.float32)
        low=sosfilt(butter(2,690,fs=sr,output='sos'),noise).astype(np.float32)
        fx[:n_live,channel]+=.0025*(noise-low)
    air=rng.normal(0,1,n_live).astype(np.float32)
    air=sosfilt(butter(2,130,fs=sr,output='sos'),air).astype(np.float32)
    fx[:n_live]+=(.080*air)[:,None]
    def sample(name,secs):
        path=v13.SFX/name
        if not path.exists():raise FileNotFoundError(path)
        return v11.old.read_audio(path,sr)[:int(secs*sr)]
    gun=sample('freesound_community-single-gunshot-54-40780.mp3',1.0)
    scream=sample('universfield-male-death-scream-123078.mp3',1.8)
    put(3.34,.20*gun,-.12)
    put(3.25,.13*scream,.10)
    for at,amp in ((4.17,.10),(6.80,.16),(15.98,.028),(28.80,.018)):
        z=np.arange(int(.4*sr),dtype=np.float32)/sr
        thud=sosfilt(butter(2,390,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        put(at,amp*thud*np.exp(-z*15),.11)
    for at in (.23,.54,.90):
        z=np.arange(int(.05*sr),dtype=np.float32)/sr
        tick=rng.normal(0,1,len(z)).astype(np.float32)
        put(at,.016*tick*np.exp(-z*65),-.1)
    # Do not compress, filter, denoise or gain-change the VO. Control FX only.
    mx=float(np.max(abs(mix+fx)))
    if mx>.95:fx*=.95/mx
    mix+=fx
    assert np.max(abs(mix))<.98
    assert not np.any(fx[n_live:]) and not np.any(mix[n_live:])
    path=v13.CACHE/'v16_unmodified_vo_nonmelodic_sfx_then_silence.wav'
    with wave.open(str(path),'wb') as out:
        out.setnchannels(2);out.setsampwidth(2);out.setframerate(sr)
        out.writeframes((mix*32767).astype('<i2').tobytes())
    print('VO unmodified',len(voice)/sr,'s; mix_peak',float(np.max(abs(mix))),flush=True)
    return path

if __name__=='__main__':
    wav=soundtrack()
    out=HERE/'FLORIDA_V16_CINEMATIC_SHORTS_PRIVATE_REVIEW_1080x1920.mp4'
    cmd=[FF,'-y','-hide_banner','-loglevel','error','-f','rawvideo',
         '-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','pipe:0',
         '-i',str(wav),'-map','0:v','-map','1:a','-c:v','libx264','-threads','2',
         '-preset','medium','-crf','19','-maxrate','8M','-bufsize','16M',
         '-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','160k','-ar','48000',
         '-movflags','+faststart','-shortest',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*5)==0:print('frame',k,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('V16 video encoding failed')
    finally:
        if p.poll() is None:p.kill()
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

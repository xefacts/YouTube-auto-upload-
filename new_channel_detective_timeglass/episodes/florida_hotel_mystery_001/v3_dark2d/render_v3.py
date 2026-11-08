#!/usr/bin/env python3
"""Florida fictional locked-suite: original hybrid dark-noir review cut.
The supplied Adam VO is preserved. Characters are reusable isolated 2D sprites,
not photographic people; backgrounds are realistic plates. No map animation.
"""
from __future__ import annotations
import math, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

HERE=Path(__file__).resolve().parent
EP=HERE.parent
ART=HERE/'assets'
WORK=HERE/'render_cache'; WORK.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS=720,1280,24
DUR=38.5
DM='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
FONT=ImageFont.truetype(DM,30); SMALL=ImageFont.truetype(DM,15)
TAN=(237,204,153,255); TEAL=(138,213,207,255)

def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def sprite(name, variant=0):
    src=Image.open(ART/f'{name}.png').convert('RGB')
    if name=='investigator':
        src=src.crop((0,0,535,src.height)) if variant==0 else src.crop((595,0,1376,src.height))
    arr=np.asarray(src)
    # Exterior white only, preserving enclosed light clothing and eyes.
    foreground=np.any(arr<236,axis=2)
    from scipy.ndimage import binary_fill_holes, gaussian_filter
    foreground=binary_fill_holes(foreground)
    alpha=np.uint8(np.clip(gaussian_filter(foreground.astype(np.float32),.6),0,1)*255)
    ys,xs=np.where(alpha>120)
    bbox=(max(0,int(xs.min())-4),max(0,int(ys.min())-4),min(src.width,int(xs.max())+5),min(src.height,int(ys.max())+5))
    rgba=src.convert('RGBA');rgba.putalpha(Image.fromarray(alpha,'L'))
    return rgba.crop(bbox)

SPRITES={n:sprite(n) for n in ('victim','wife','partner','investigator','wife_turn','investigator_reach')}
SPRITES['investigator_alt']=sprite('investigator',1)
BG={n:Image.open(ART/f'{n}.png').convert('RGB') for n in ('hotel_exterior','hallway','suite','balcony')}

def zoom_frame(key, zoom, center=(.5,.5), shake=(0,0)):
    im=BG[key]; iw,ih=im.size
    cw=iw/zoom; ch=ih/zoom
    cx=iw*center[0]+shake[0];cy=ih*center[1]+shake[1]
    # Zoom can exceed source boundary: black extension is preferable to a repeated seam.
    box=(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2)
    return im.transform((W,H),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).convert('RGBA')

def place(canvas,name,x,base_y,h,lean=0,head=0,flip=False,alpha=1):
    """Character motion: animated path, body rotation, independent cutout head and hand.
    The exact same canonical sprite is reused at every appearance.
    """
    original=SPRITES[name]; sw,sh=original.size
    w=round(h*sw/sh); im=original.resize((w,round(h)),Image.Resampling.LANCZOS)
    # Separate head from body with overlapping neck strip to avoid a detached-sticker seam.
    headheight=int(im.height*.255); neck=int(im.height*.16)
    body=im.copy(); body.paste((0,0,0,0),(0,0,w,neck))
    face=Image.new('RGBA',im.size,(0,0,0,0));face.paste(im.crop((0,0,w,headheight)),(0,0))
    if abs(head)>.1: face=face.rotate(head,Image.Resampling.BICUBIC,center=(w*.48,headheight*.79),expand=False)
    body.alpha_composite(face)
    if flip: body=body.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if lean: body=body.rotate(lean,Image.Resampling.BICUBIC,center=(w*.52,h*.84),expand=True)
    if alpha<1: body.putalpha(body.getchannel('A').point(lambda p:int(p*alpha)))
    x=int(x-body.width*.5);y=int(base_y-body.height)
    # Contact shadow keeps cartoon actor grounded in a realistic photographic plate.
    shadow=Image.new('RGBA',canvas.size,(0,0,0,0)); sd=ImageDraw.Draw(shadow)
    sd.ellipse((x+body.width*.1,base_y-17,x+body.width*.9,base_y+17),fill=(0,0,0,150))
    shadow=shadow.filter(ImageFilter.GaussianBlur(12));canvas.alpha_composite(shadow)
    canvas.alpha_composite(body,(x,y))

rng=np.random.default_rng(3009)
RAINDROPS=[(float(rng.uniform(0,W)),float(rng.uniform(0,H)),float(rng.uniform(5,20)),float(rng.uniform(.65,1.6))) for _ in range(78)]

def rain(draw,t,level=1):
    for x,y,length,speed in RAINDROPS:
        yy=(y+t*speed*180)%(H+100)-50
        xx=x+(t*13)%40
        draw.line((xx,yy,xx-3,yy+length),fill=(171,218,222,round(34*level)),width=1)

def title(draw,label,t,t0,t1):
    if not t0<=t<t1:return
    a=ease((t-t0)/.24)*(1-ease((t1-t)/.22))
    tw=draw.textbbox((0,0),label,font=FONT)[2]
    x=(W-tw)/2
    draw.rounded_rectangle((x-24,100,x+tw+24,170),radius=9,fill=(5,17,20,round(193*a)))
    draw.text((x,113),label,font=FONT,fill=(246,232,209,round(255*a)),stroke_width=1,stroke_fill=(0,0,0,round(255*a)))
    draw.line((x,172,x+tw,172),fill=(184,125,86,round(220*a)),width=2)

def grain_and_vignette(img,t):
    wash=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(wash)
    d.rectangle((0,0,W,80),fill=(3,10,16,85));d.rectangle((0,H-168,W,H),fill=(3,10,16,78))
    img.alpha_composite(wash)
    return img

def door_action(img,t):
    """Hand-drawn perspective door panel pivots around a fixed hinge; not crossfaded stills."""
    p=ease((t-5.55)/.85)
    shake=(1-ease((t-6.42)/.16))*max(0,1-abs(t-6.48)/.12)
    xhinge=690; left=602-(385*p)
    ytop=225-40*p; ybot=1260
    d=ImageDraw.Draw(img,'RGBA')
    d.polygon([(xhinge,ytop),(left,ytop+43*p),(left,ybot-80*p),(xhinge,ybot)],fill=(36,25,23,250),outline=(132,100,67,255),width=6)
    for frac in (.12,.18,.84,.9):
        x=left+(xhinge-left)*frac
        d.line((x,ytop+55,x,ybot-100),fill=(137,97,60,80),width=3)
    d.rounded_rectangle((left+18,ytop+100,xhinge-25,ybot-130),radius=5,outline=(126,95,61,160),width=7)
    cx=left+27+(xhinge-left)*.16; cy=690
    d.ellipse((cx-13,cy-13,cx+13,cy+13),fill=(209,157,74,255),outline=(49,39,22,255),width=3)
    if shake: d.rectangle((0,0,W,H),fill=(215,198,174,round(36*shake)))

def latch_action(img,t):
    d=ImageDraw.Draw(img,'RGBA');p=ease((t-15.38)/.85)
    d.rounded_rectangle((68,610,652,800),radius=16,fill=(13,26,27,245),outline=(174,133,83,205),width=4)
    d.rounded_rectangle((111,675,577,736),radius=5,fill=(53,48,39,255),outline=(173,139,94,255),width=4)
    d.rounded_rectangle((111+139*p,685,264+170*p,727),radius=7,fill=(209,169,104,255),outline=(71,54,37,255),width=3)
    d.ellipse((280+128*p,669,344+128*p,741),fill=(143,105,65,255),outline=(236,193,112,255),width=5)
    d.rectangle((567,654,595,752),fill=(181,141,87,255),outline=(61,41,30,255),width=3)

def watch_overlay(img,t,location=(420,770),scale=1):
    x,y=location;d=ImageDraw.Draw(img,'RGBA')
    r=int(43*scale); gl=ease((t%1.7)/1.7)
    d.ellipse((x-r-15,y-r-15,x+r+15,y+r+15),outline=(172,232,209,round(90*(1-gl))),width=3)
    d.ellipse((x-r,y-r,x+r,y+r),fill=(160,170,159,255),outline=(35,39,37,255),width=6)
    d.ellipse((x-r+8,y-r+8,x+r-8,y+r-8),fill=(233,221,193,255),outline=(66,71,66,255),width=2)
    d.line((x,y,x+10*scale,y-22*scale),fill=(35,42,39,255),width=max(2,int(3*scale)))
    d.line((x,y,x-15*scale,y-11*scale),fill=(35,42,39,255),width=max(2,int(3*scale)))
    d.ellipse((x-4,y-4,x+4,y+4),fill=(41,46,39,255))

def render(t):
    if t<2.15:
        z=1.03+.34*ease(t/2.15)
        center=(.5+.064*ease(t/2.15),.5-.13*ease(t/2.15))
        img=zoom_frame('hotel_exterior',z,center)
    elif t<5.2:
        z=1.02+.17*ease((t-2.15)/3.05)
        img=zoom_frame('suite',z,(.5,.56))
        p=ease((t-2.25)/1.3)
        place(img,'victim',420-53*p,1120+40*p,600,lean=-18*p,head=8*p)
        if t>4.25:place(img,'investigator',95,1180,470,lean=3,alpha=ease((t-4.25)/.45))
    elif t<9.5:
        jitter=0
        if 6.38<t<6.58:jitter=math.sin((t-6.38)*100)*6*(1-ease((t-6.38)/.2))
        img=zoom_frame('hallway',1.0+.17*ease((t-5.2)/4.3),(.51,.53),(jitter,0))
        door_action(img,t)
        if t>6.8:
            p=ease((t-6.8)/2.4)
            x=-120+340*p+5*math.sin((t-6.8)*13)*math.sin(math.pi*p)
            place(img,'investigator',x,1180,540,lean=2+2*math.sin(t*6),head=2*math.sin(t*4))
    elif t<12.7:
        z=1.1+1.0*ease((t-9.5)/3.2)
        img=zoom_frame('suite',z,(.22+.04*ease((t-9.5)/3.2),.70+.07*ease((t-9.5)/3.2)))
        if t>10.5:watch_overlay(img,t,(407,753),scale=.8+1.2*ease((t-10.5)/2.0))
    elif t<15.3:
        p=ease((t-12.7)/2.6)
        img=zoom_frame('balcony',1.02+.35*p,(.46+.16*p,.54+.13*p))
        if t<13.6:
            place(img,'investigator',180+105*p,1190,495,lean=-11*p,head=-5*p)
        else:
            # A distinct illustrated crouch/reach key pose, not just a zoom on one rigid sprite.
            place(img,'investigator_reach',205+55*p,1240,720,lean=-2*p)
        d=ImageDraw.Draw(img,'RGBA');d.ellipse((454,782,509,837),outline=(204,153,102,round(180*p)),width=4)
    elif t<17.25:
        img=zoom_frame('suite',1.42,(.63,.51));latch_action(img,t)
    elif t<20.25:
        p=ease((t-17.25)/.55)
        img=zoom_frame('hallway',1.13+.18*ease((t-17.25)/3),(.36,.49))
        wife_pose='wife' if t<18.5 else 'wife_turn'
        place(img,wife_pose,375+19*math.sin((t-17.25)*1.7),1205,770,lean=2*math.sin(t*1.6),head=6*ease((t-18.0)/.75)-3)
        # Her appearance carries no implication of guilt.
    elif t<24.3:
        img=zoom_frame('hallway',1.18+.15*ease((t-20.25)/4),(.55,.5))
        p=ease((t-20.25)/1.2)
        place(img,'partner',400-48*p,1220,770,lean=3*math.sin((t-20.25)*1.2),head=3*math.sin((t-20.25)*1.4))
    elif t<27.35:
        p=ease((t-24.3)/3.05)
        img=zoom_frame('balcony',1.45+.8*p,(.68,.60))
        if t<25.55:
            place(img,'investigator',180+135*p,1205,540,lean=-14*p,head=-3*p)
        else:
            place(img,'investigator_reach',162+105*p,1320,730,lean=-3*p)
        d=ImageDraw.Draw(img,'RGBA')
        x=503-60*p;y=752-80*p
        d.line((x,y,x-22,y+45),fill=(156,77,57,255),width=4)
        d.ellipse((x-19,y-19,x+19,y+19),outline=(235,185,113,255),width=3)
    elif t<30.1:
        img=zoom_frame('balcony',2.05+.16*ease((t-27.35)/2.75),(.67,.58))
        d=ImageDraw.Draw(img,'RGBA')
        for k in range(4):
            x=375+k*6
            d.line((x,664+30*math.sin(t*2),x+58,545-75*ease((t-27.35)/2.75)),fill=(154,77,57,205),width=4-k//2)
        d.ellipse((310,500,501,695),outline=(186,219,196,125),width=3)
    elif t<33.5:
        p=ease((t-30.1)/3.4)
        img=zoom_frame('suite',1.35+.65*p,(.28,.68))
        place(img,'investigator',535-35*p,1150,510,lean=-11*p,head=-7*p)
        watch_overlay(img,t,(275+40*p,827-52*p),1.05+.55*p)
    elif t<34.62:
        p=ease((t-33.5)/1.12)
        img=zoom_frame('suite',2.0+1.45*p,(.30,.70))
        watch_overlay(img,t,(340,720),1.55+1.5*p)
    else:
        # The strongest camera move: smash-match into the lit window, then crane backwards
        # from the third-floor detail into the full rainy facade, with eased deceleration.
        p=ease((t-34.62)/(DUR-34.62))
        z=3.65-(3.65-1.03)*(p*p*(3-2*p))
        cx=.63-(.63-.5)*p; cy=.31+(.50-.31)*p
        img=zoom_frame('hotel_exterior',z,(cx,cy))
        if t<34.9:
            flash=(1-ease((t-34.62)/.28))*.14
            img=Image.blend(img,Image.new('RGBA',(W,H),(200,217,201,255)),flash)
    img=grain_and_vignette(img,t)
    d=ImageDraw.Draw(img,'RGBA')
    if t<3 or t>34.62 or 12.7<t<15.3:rain(d,t,1.7 if t>34.62 else 1)
    if t<2.15: title(d,'THE LOCKED SUITE',t,.28,2.10)
    for a,b,s in [(5.4,9.25,'NO FORCED ENTRY'),(9.6,12.6,'THE WATCH'),
                  (12.75,15.2,'FOOTPRINTS'),(15.35,17.2,'LOCKED FROM INSIDE'),
                  (17.35,20.1,'THE WIFE'),(20.3,24.15,'THE PARTNER'),
                  (24.35,27.2,'ONE LOOSE THREAD'),(30.2,33.3,'NO EASY ANSWER')]:
        title(d,s,t,a,b)
    if t<3:
        d.text((27,H-55),'FICTIONAL DRAMATIZATION',font=SMALL,fill=(241,224,201,220))
    return img.convert('RGB')

def decode_audio(path,sr=48000):
    p=subprocess.run([FF,'-loglevel','error','-i',str(path),'-ac','1','-ar',str(sr),'-f','f32le','pipe:1'],capture_output=True,check=True)
    return np.frombuffer(p.stdout,dtype='<f4').copy()

def mix_audio():
    sr=48000;n=round(sr*DUR)
    vo=decode_audio(EP/'audio/voice_edit_1934.mp3',sr)
    bed=decode_audio(EP/'audio/percussion_air_draft.mp3',sr)
    a=np.zeros(n,np.float32)
    a[:min(n,len(bed))]+=.39*bed[:n]
    a[:min(n,len(vo))]+=.88*vo[:n]
    rng=np.random.default_rng(1948)
    x=np.arange(n,dtype=np.float32)/sr
    rainnoise=rng.normal(0,1,n).astype(np.float32)
    a+=.007*(rainnoise-.4*np.roll(rainnoise,1))
    a+=.007*np.sin(2*np.pi*48*x)
    def put(at,sig):
        idx=int(at*sr);m=min(len(sig),n-idx)
        if idx>=0 and m>0:a[idx:idx+m]+=sig[:m]
    def thunk(t,amp=.17):
        z=np.arange(int(.7*sr),dtype=np.float32)/sr
        put(t,(np.sin(2*np.pi*(68*z-13*z*z))*.65+rng.normal(0,.13,len(z)))*np.exp(-z*11)*amp)
    def sweep(t,dur=.48,amp=.05):
        z=np.arange(round(dur*sr),dtype=np.float32)/sr
        r=rng.normal(0,1,len(z)).astype(np.float32)
        soft=(r+np.roll(r,1)+np.roll(r,2)+np.roll(r,3))*.25
        env=np.sin(np.pi*z/dur)**2
        put(t,soft*env*amp)
    for t in (2.1,5.1,9.55,12.7,15.3,17.25,20.25,24.3,27.3,30.1,33.5,34.65):sweep(t)
    # Door: pitched hardwood creak -> moving hinge -> clean low door slam and latch click.
    z=np.arange(round(.85*sr),dtype=np.float32)/sr
    creak=(np.sin(2*np.pi*(191*z-44*z*z))+.34*np.sin(2*np.pi*(408*z-80*z*z)))*.022
    creak*=np.sin(np.pi*z/.85)**1.4
    put(5.52,creak)
    thunk(6.44,.30)
    for i,at in enumerate((7.3,7.83,8.36,13.08,13.62)):
        thunk(at,.055 if i<3 else .034)
    for t in (10.2,15.94,26.9,33.5):thunk(t,.095)
    thunk(34.67,.23)
    # Strong visual-only end: a low rain swell follows the camera back from the suite.
    end=int(34.62*sr)
    end_env=np.linspace(0,1,n-end,dtype=np.float32)**.7
    a[end:]+=.013*rng.normal(0,1,n-end).astype(np.float32)*end_env
    # Unpitched, original low storm swells; no sampled or reference audio.
    for at in (.05,34.67):
        z=np.arange(round(1.9*sr),dtype=np.float32)/sr
        soft=rng.normal(0,1,len(z)).astype(np.float32)
        soft=(soft+np.roll(soft,9)+np.roll(soft,18))/3
        put(at,soft*np.exp(-z*2)*.045+np.sin(2*np.pi*49*z)*np.exp(-z*3)*.065)
    a=np.tanh(a*1.12)
    a[-round(.20*sr):]*=np.linspace(1,0,round(.20*sr))
    peak=max(.01,float(np.max(np.abs(a))))
    if peak>.96:a*=.96/peak
    p=WORK/'master_mix.wav'
    with wave.open(str(p),'wb') as wf:
        wf.setframerate(sr);wf.setsampwidth(2);wf.setnchannels(1)
        wf.writeframes(np.int16(a*32767).tobytes())
    return p

if __name__=='__main__':
    audio=mix_audio()
    raw=WORK/'silent.mp4'
    args=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
          '-r',str(FPS),'-i','pipe:0','-c:v','libx264','-preset','veryfast','-crf','19',
          '-pix_fmt','yuv420p','-movflags','+faststart',str(raw)]
    proc=subprocess.Popen(args,stdin=subprocess.PIPE)
    try:
        for f in range(round(DUR*FPS)):
            proc.stdin.write(render(f/FPS).tobytes())
            if f%(FPS*5)==0:print('frame',f,'/',round(DUR*FPS),flush=True)
        proc.stdin.close()
        if proc.wait()!=0:raise RuntimeError('video encoder failed')
    finally:
        if proc.poll() is None:proc.kill()
    output=HERE/'FLORIDA_LOCKED_SUITE_V3_PRIVATE_REVIEW_720x1280.mp4'
    subprocess.run([FF,'-y','-loglevel','error','-i',str(raw),'-i',str(audio),'-map','0:v','-map','1:a',
      '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(output)],check=True)
    print('Wrote',output,output.stat().st_size,flush=True)

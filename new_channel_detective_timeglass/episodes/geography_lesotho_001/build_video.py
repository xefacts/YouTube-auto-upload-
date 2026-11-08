#!/usr/bin/env python3
"""Render an original 9:16 geography micro-documentary. Source assets live in work/geography_lesotho.
No reference footage/audio is incorporated. Run from the repository root with .venv/bin/python.
"""
import json, math, subprocess, wave
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[3]
ASSET = ROOT/'work/geography_lesotho'
DEST = Path(__file__).parent
W,H,FPS = 720,1280,24
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
F=lambda n,bold=False: ImageFont.truetype(BOLD if bold else FONT,n)
GEO=json.loads((ASSET/'countries.geo.json').read_text())['features']
AQUA=(102,235,207); IVORY=(246,239,219); GOLD=(255,198,94)
LINES=(ASSET/'SCRIPT.txt').read_text().strip().splitlines()

# One rendered sentence per clip. Gaps keep the hook punchy and preserve intelligibility.
clips=[]; time=0.55
for i,line in enumerate(LINES):
    with wave.open(str(ASSET/f'voice_{i}.wav')) as wr:
        d=wr.getnframes()/wr.getframerate()
    clips.append((time,time+d,line))
    time+=d+[0.38,0.32,0.40,0.42,0.40,0.48,0.0][i]
DURATION=math.ceil(time+1.0)
print('sentence timing:',[(round(a,2),round(b,2)) for a,b,_ in clips], 'duration',DURATION,flush=True)


def ease(x):
    x=max(0,min(1,x)); return x*x*(3-2*x)

def interpolate(t,keyframes):
    for i in range(len(keyframes)-1):
        a,b=keyframes[i:i+2]
        if a[0]<=t<=b[0]:
            z=ease((t-a[0])/(b[0]-a[0])); return tuple(a[j]+z*(b[j]-a[j]) for j in range(1,len(a)))
    return keyframes[-1][1:]

# Geographic coordinates, not hand-drawn borders. The polygon source is Natural Earth via
# johan/world.geo.json; accurate for this zoom level (not a survey-grade boundary map).
def coords(poly):
    typ=poly['geometry']['type']; c=poly['geometry']['coordinates']
    if typ=='Polygon': return [c[0]]
    if typ=='MultiPolygon': return [p[0] for p in c]
    return []

def project(lon,lat,box,sz):
    x0,x1,y0,y1=box; w,h=sz
    return ((lon-x0)/(x1-x0)*w, (y1-lat)/(y1-y0)*h)

BOXES=[(-35,60,-50,45),(8,47,-46,-10),(23,34,-35,-24)]
MAP_W=2200

def make_map(box,index):
    x0,x1,y0,y1=box; mw=MAP_W; mh=round(mw*(y1-y0)/(x1-x0)); mh=max(mh,2000)
    cache=ASSET/f'geo_map_{index}.jpg'
    if cache.exists(): return Image.open(cache).convert('RGB')
    yy,xx=np.mgrid[0:mh,0:mw].astype(np.float32)
    lon=x0+xx/mw*(x1-x0); lat=y1-yy/mh*(y1-y0)
    # Layered deterministic macrorelief, warm rock/green highlands, dark ocean bathymetry.
    ridge=(np.sin(lon*.85+np.sin(lat*.7)*2)*np.sin(lat*1.12)+
           .42*np.cos(lon*2.3-lat*.7)+.19*np.sin(lon*5.7+lat*3.1))
    rng=np.random.default_rng(index+1704)
    fine=rng.normal(0,1,(mh,mw)).astype(np.float32)
    grad=np.clip((lat+38)/62,0,1)
    water=np.stack([10+4*ridge,35+10*ridge,49+12*ridge],axis=-1)
    land=np.stack([64+16*ridge+30*grad+4*fine,
                   69+13*ridge+20*grad+4*fine,
                   53+8*ridge+9*grad+3*fine],axis=-1)
    ocean=Image.fromarray(np.uint8(np.clip(water,0,255)),'RGB')
    landim=Image.fromarray(np.uint8(np.clip(land,0,255)),'RGB')
    mask=Image.new('L',(mw,mh),0); md=ImageDraw.Draw(mask)
    for f in GEO:
        for ring in coords(f):
            if len(ring)>2:
                pts=[project(*p[:2],box,(mw,mh)) for p in ring]
                md.polygon(pts,fill=255)
    ocean.paste(landim,(0,0),mask)
    d=ImageDraw.Draw(ocean,'RGBA')
    # Subdued graticule and coastlines improve legibility while retaining dark relief texture.
    step=10 if index==0 else (2 if index==1 else 1)
    for lng in np.arange(math.ceil(x0/step)*step,x1,step):
        x,_=project(lng,0,box,(mw,mh)); d.line((x,0,x,mh),fill=(190,209,197,12),width=2)
    for latv in np.arange(math.ceil(y0/step)*step,y1,step):
        _,y=project(0,latv,box,(mw,mh)); d.line((0,y,mw,y),fill=(190,209,197,12),width=2)
    for f in GEO:
        for ring in coords(f):
            if len(ring)>2:
                pts=[project(*p[:2],box,(mw,mh)) for p in ring]
                d.line(pts+[pts[0]],fill=(211,225,204,80),width=2 if index<2 else 3,joint='curve')
    za=next(f for f in GEO if f['id']=='ZAF')
    ls=next(f for f in GEO if f['id']=='LSO')
    for f,fill,edge in [(za,(197,152,83,35),(241,183,107,130)),(ls,(60,231,200,125),(131,254,223,230))]:
        for ring in coords(f):
            pts=[project(*p[:2],box,(mw,mh)) for p in ring]
            d.polygon(pts,fill=fill)
            d.line(pts+[pts[0]],fill=edge,width=8 if f==ls else 5,joint='curve')
    ocean.save(cache,quality=91,subsampling=0)
    print('cached map',index,ocean.size,flush=True)
    return ocean

MAPS=[make_map(box,i) for i,box in enumerate(BOXES)]
PHOTO=Image.open(ASSET/'lesotho_highlands.png').convert('RGB')

def camera(t):
    return interpolate(t,[
        (0,18,-4,47),(5.6,24,-20,22),(11.7,28.2,-28.2,8.5),
        (17.5,28.35,-29.4,6.4),(26,28.4,-29.4,6.0),
        (34,28.4,-29.5,5.1),(39,28.4,-29.6,4.5),(DURATION,28,-29.3,12)])

def map_frame(t):
    lon,lat,vw=camera(t); vh=vw*H/W
    idx=0 if vw>17 else 1 if vw>5.7 else 2
    box=BOXES[idx]; src=MAPS[idx]; sw,sh=src.size
    cx,cy=project(lon,lat,box,src.size)
    cw=vw/(box[1]-box[0])*sw; ch=vh/(box[3]-box[2])*sh
    # Pillow's transform handles the edge of the basemap on extreme close zooms.
    left=cx-cw/2; top=cy-ch/2
    img=src.transform((W,H),Image.Transform.EXTENT,(left,top,left+cw,top+ch),Image.Resampling.BICUBIC)
    return img,(lon,lat,vw,vh)

def screen(lon,lat,cam):
    cl,ct,vw,vh=cam
    return (W/2+(lon-cl)*W/vw,H/2-(lat-ct)*H/vh)

def text(d,xy,s,font,fill=IVORY,anchor=None,stroke=0):
    d.text(xy,s,font=font,fill=fill,anchor=anchor,stroke_width=stroke,stroke_fill=(5,24,31))

def outlined_line(d,pts,fill,width):
    if len(pts)>1: d.line(pts,fill=fill,width=width,joint='curve')

LS=next(f for f in GEO if f['id']=='LSO')
RING=coords(LS)[0]

def render(t):
    photo=ease((t-26.2)/.65)*(1-ease((t-34.3)/.7))
    img,cam=map_frame(t)
    if photo>0:
        pscale=1+.07*ease((t-26)/9); pw=round(PHOTO.width/pscale); ph=round(PHOTO.height/pscale)
        p=PHOTO.crop(((PHOTO.width-pw)//2,(PHOTO.height-ph)//2,(PHOTO.width+pw)//2,(PHOTO.height+ph)//2))
        p=p.resize((W,H),Image.Resampling.BICUBIC)
        img=Image.blend(img,p,photo)
    # Consistent vignette, softened top/bottom for bright editorial typography.
    a=Image.new('RGBA',(W,H),(0,0,0,0)); ad=ImageDraw.Draw(a)
    ad.rectangle((0,0,W,250),fill=(5,15,23,122)); ad.rectangle((0,H-375,W,H),fill=(5,15,23,145))
    img=Image.alpha_composite(img.convert('RGBA'),a)
    d=ImageDraw.Draw(img,'RGBA')
    # Map remains alive: perimeter traces in a moving reveal, pulse at the coordinate, callout.
    if photo<.72:
        pts=[screen(*p[:2],cam) for p in RING]
        if t>7.5:
            n=max(2,min(len(pts),int(len(pts)*ease((t-7.5)/3.2))))
            outlined_line(d,pts[:n],(57,245,203,40),13)
            outlined_line(d,pts[:n],(114,251,214,235),3)
        x,y=screen(28.24,-29.61,cam)
        if -40<x<W+40 and -40<y<H+40:
            pulse=(t*1.8)%1
            r=20+37*pulse
            d.ellipse((x-r,y-r,x+r,y+r),outline=(108,251,216,int(170*(1-pulse))),width=2)
            d.ellipse((x-6,y-6,x+6,y+6),fill=(125,255,218,240))
        if t>6:
            for name,ll,lt in [('SOUTH AFRICA',25.2,-32.8),('LESOTHO',28.25,-29.55)]:
                x,y=screen(ll,lt,cam)
                if 36<x<W-36 and 180<y<H-235:
                    # Adjust when label sits on the center dot.
                    if name=='LESOTHO': y-=58
                    text(d,(x,y),name,F(20 if name=='SOUTH AFRICA' else 23,True),AQUA if name=='LESOTHO' else IVORY,'mm',2)
    # Chronology cards (not anachronistic historical border claims).
    if 17.3<t<26.5:
        op=ease((t-17.3)/.5)*(1-ease((t-26.0)/.5))
        cx=42; top=280
        for k,(yr,cap) in enumerate([('1868','BRITISH TERRITORY'),('1966','INDEPENDENCE')]):
            y=top+k*136
            d.rounded_rectangle((cx,y,cx+412,y+103),radius=15,fill=(8,24,31,int(210*op)),outline=(100,222,195,int(110*op)),width=2)
            text(d,(cx+22,y+15),yr,F(39,True),(255,201,105,int(255*op)))
            text(d,(cx+140,y+52),cap,F(17,True),(244,240,224,int(255*op)),anchor='lm')
        d.line((cx+206,top+103,cx+206,top+136),fill=(108,227,197,int(175*op)),width=3)
    if photo>.25:
        op=photo
        d.rounded_rectangle((32,280,W-32,442),radius=17,fill=(5,22,28,int(182*op)),outline=(210,243,223,int(70*op)),width=2)
        text(d,(53,302),'THE ENTIRE COUNTRY',F(22,True),(248,243,226,int(255*op)))
        text(d,(52,335),'ABOVE 1,000 m',F(47,True),(117,249,212,int(255*op)))
        text(d,(53,406),'ELEVATION ABOVE SEA LEVEL',F(14,True),(232,221,196,int(235*op)))
        text(d,(W-29,H-290),'ILLUSTRATIVE HIGHLANDS',F(13,True),(239,233,213,int(185*op)),anchor='ra')
    if 34<t<41:
        op=ease((t-34)/.5)*(1-ease((t-40.5)/.5))
        d.rounded_rectangle((40,288,540,410),radius=16,fill=(5,25,33,int(211*op)),outline=(112,249,215,int(120*op)),width=2)
        text(d,(61,303),'LOWEST POINT',F(20,True),(230,230,211,int(255*op)))
        text(d,(60,333),'≈ 1,400 m',F(44,True),(113,248,211,int(255*op)))
    # Header system and progress rail.
    d.line((30,84,W-30,84),fill=(236,232,212,80),width=2)
    d.ellipse((30,32,43,45),fill=(113,246,208,255))
    text(d,(53,37),'GEO / FIELD NOTES',F(18,True),IVORY,'lm')
    text(d,(W-30,37),'01 — LESOTHO',F(15,True),AQUA,'rm')
    d.rectangle((30,99,W-30,103),fill=(222,225,210,53))
    d.rectangle((30,99,30+(W-60)*t/DURATION,103),fill=(114,248,207,240))
    # Topic title, then short on-screen edit lines tied to the spoken sentences.
    if t<7.5:
        text(d,(W/2,164),'A COUNTRY',F(36,True),IVORY,'mm',2)
        text(d,(W/2,211),'INSIDE A COUNTRY',F(39,True),GOLD,'mm',2)
    elif t>41:
        text(d,(W/2,195),'THE KINGDOM',F(40,True),IVORY,'mm',2)
        text(d,(W/2,247),'IN THE SKY',F(52,True),AQUA,'mm',2)
    # Caption box uses phrase-level cuts rather than dense verbatim speech on one card.
    captions=[
      ['Look closely at southern Africa.','That patch is not a lake.','It is another country.'],
      ['This is Lesotho.','Surrounded by South Africa.','Yet completely independent.'],
      ['Basotho leaders defended','their mountain homeland','as neighboring powers expanded.'],
      ['It came under British rule,','then gained independence','in 1966.'],
      ['The map hides its greatest secret:','the only independent country','entirely above 1,000 meters.'],
      ['Even its lowest point','is about 1,400 meters','above sea level.'],
      ['One country inside another.','A kingdom in the sky.']
    ]
    active=None
    for i,(a,b,_) in enumerate(clips):
        if a-.12<=t<b+.18:
            fraction=max(0,min(.999,(t-a)/(b-a)))
            active=(captions[i][int(fraction*len(captions[i]))],i)
            break
    if active:
        cap,i=active
        d.rounded_rectangle((30,H-218,W-30,H-101),radius=18,fill=(4,18,25,222),outline=(124,234,202,75),width=2)
        d.rounded_rectangle((44,H-196,50,H-121),radius=3,fill=AQUA)
        font=F(28 if len(cap)<29 else 26,True)
        text(d,(70,H-159),cap,font,IVORY,'lm')
    text(d,(30,H-54),'28.2° E   /   29.6° S',F(14,True),(209,222,207),'lm')
    text(d,(W-30,H-54),'SOUTHERN AFRICA',F(14,True),AQUA,'rm')
    return img.convert('RGB')


def render_audio():
    sr=48000; n=int((DURATION+.15)*sr)
    rng=np.random.default_rng(23)
    x=np.arange(n,dtype=np.float32)/sr
    audio=np.zeros(n,dtype=np.float32)
    for i,(a,b,_) in enumerate(clips):
        with wave.open(str(ASSET/f'voice_{i}.wav')) as w:
            v=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
            orig=w.getframerate()
        # modest speed lift, no exaggerated TTS pacing; 16k -> 48k resampling.
        y=np.interp(np.arange(round(len(v)*sr/orig))/sr*orig,np.arange(len(v)),v)
        fade=min(int(.03*sr),len(y)//10)
        y[:fade]*=np.linspace(0,1,fade); y[-fade:]*=np.linspace(1,0,fade)
        off=int(a*sr); audio[off:off+len(y)]+=y*.86
    # Original low, non-melodic cinematic roomtone (not stock or reference music).
    noise=rng.normal(0,1,n).astype(np.float32)
    bass=(np.sin(x*2*np.pi*43)+.38*np.sin(x*2*np.pi*57))*.012
    airy=np.convolve(noise,np.ones(180,dtype=np.float32)/180,mode='same')*.026
    audio+=bass+airy
    def effect(at,dur,kind):
        start=int(at*sr); m=min(int(dur*sr),n-start)
        if m<=0: return
        z=np.arange(m,dtype=np.float32)/sr; r=rng.normal(0,1,m).astype(np.float32)
        if kind=='whoosh':
            # air sweep: band of softened noise swelling and receding.
            smooth=np.convolve(r,np.ones(42,dtype=np.float32)/42,mode='same')
            sig=(r*.018+smooth*.16)*(np.sin(np.pi*z/dur)**1.7)
        elif kind=='hit':
            sig=(np.sin(2*np.pi*(87*z-30*z*z))*.15+r*.026)*np.exp(-z*8)
        else:
            sig=np.sin(2*np.pi*720*z)*np.exp(-z*27)*.075
        audio[start:start+m]+=sig
    for at in [1.1,4.6,8.0,11.8,17.3,26.2,34.4,40.8]: effect(at,.65,'whoosh')
    for at in [5.2,11.6,26.2,34.3,41.2]: effect(at,.65,'hit')
    for at in [9.3,21.2,22.8,31.0,36.2]: effect(at,.3,'ping')
    audio=np.tanh(audio*1.22)/1.15
    audio*=.91/(max(.91,float(np.max(np.abs(audio)))))
    path=ASSET/'mix.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes(np.int16(np.clip(audio,-1,1)*32767).tobytes())
    return path

if __name__=='__main__':
    mix=render_audio()
    ff=imageio_ffmpeg.get_ffmpeg_exe()
    silent=ASSET/'lesotho_silent.mp4'
    cmd=[ff,'-y','-loglevel','error','-f','rawvideo','-pixel_format','rgb24','-video_size',f'{W}x{H}',
         '-framerate',str(FPS),'-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p','-preset','veryfast',
         '-crf','18','-movflags','+faststart',str(silent)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(DURATION*FPS):
            p.stdin.write(render(k/FPS).tobytes())
            if k%(FPS*5)==0: print('frame',k,'/',DURATION*FPS,flush=True)
        p.stdin.close()
        if p.wait()!=0: raise RuntimeError('ffmpeg video encode failed')
    finally:
        if p.poll() is None: p.kill()
    final=DEST/'LESOTHO_KINGDOM_IN_THE_SKY_720x1280.mp4'
    subprocess.run([ff,'-y','-loglevel','error','-i',str(silent),'-i',str(mix),
        '-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k',
        '-movflags','+faststart','-shortest',str(final)],check=True)
    print(final,final.stat().st_size,flush=True)

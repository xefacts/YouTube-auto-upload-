#!/usr/bin/env python3
"""Original documentary-geography short, reference-informed (not reference copied).

Cuts, dynamic map moves, moving text/route layers and natural narration are all
regenerated here. See V2_PRODUCTION_NOTES.md for exact sources and rights.
"""
from pathlib import Path
import bisect,math,subprocess,wave,json,hashlib
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from piper import PiperVoice,SynthesisConfig
from imageio_ffmpeg import get_ffmpeg_exe
import render_geography_full as g

HERE=Path(__file__).resolve().parent;W,H,FPS=1080,1920,30
FF=get_ffmpeg_exe();CACHE=HERE/'render_cache';CACHE.mkdir(exist_ok=True)
OUT=HERE/'FLORIDA_KEYS_GEOGRAPHY_V2_VOICED_1080x1920.mp4'
# Allow running from the repository while leaving the 79 MB model out of git.
MODEL=HERE.parents[1]/'work/tts_models/en_US-libritts_r-medium.onnx'
assert MODEL.exists(),f'Model missing: {MODEL}'
VOICE_SHA256='10bb85e071d616fcf4071f369f1799d0491492ab3c5d552ec19fb548fac13195'
with MODEL.open('rb') as _model_file:
    assert hashlib.file_digest(_model_file,'sha256').hexdigest()==VOICE_SHA256,'Voice model checksum mismatch'
WAVE=HERE/'assets/v2_ambient/ambience_waves_cc0.ogg'
WIND=g.SOUND/'wind.ogg'

# One original line per visual beat; selected on-source NPS/NOAA geology facts.
# 60 second reference informed pacing; never transcribed from the example clips.
BEATS=[
 ('Why does Florida end in a chain of islands?',              'globe'),
 ('From orbit, the peninsula looks like it simply stops.',   'orbital_map'),
 ('But look closer. A necklace of land curves southwest.',   'region'),
 ('These are the Florida Keys.',                              'macro_reveal'),
 ('And they are not pieces of the mainland that broke away.', 'macro_halo'),
 ('The upper keys are exposed remains of ancient coral reefs.','reef'),
 ('Farther west, limestone and sand helped form the lower islands.','reef_labels'),
 ('Long ago, warmer seas covered this shallow platform.',     'sea_high'),
 ('During the ice age, water levels fell, exposing old reefs.','sea_low'),
 ('Then the sea rose again, leaving low islands above water.','macro_islands'),
 ('Today, the Overseas Highway connects many of those islands.','road_wide'),
 ('Its bridges seem to carry the road across the sea.',       'bridge'),
 ('But the road does not reach the entire chain.',            'route_stops'),
 ('Key West is famous. Yet the keys continue farther west.',  'westward'),
 ('On the bay side: quiet shallows.',                          'bay'),
 ('On the ocean side: deeper water.',                          'straits'),
 ('What looks like a broken coastline is a record of change.','pullback'),
 ('Reefs. Rock. Changing seas. A remarkable island chain.',   'end'),
]

VOICE_PATH=CACHE/'v2_voice_48k.wav'; MIX_PATH=CACHE/'v2_mix_48k.wav'
TIMINGS_PATH=CACHE/'v2_timing.json'


def decode(path,rate=48000):
    b=subprocess.check_output([FF,'-v','error','-i',str(path),'-ac','1','-ar',str(rate),'-f','f32le','pipe:1'])
    return np.frombuffer(b,'<f4').copy()


def voice_and_timing():
    if VOICE_PATH.exists() and TIMINGS_PATH.exists():
        data=json.loads(TIMINGS_PATH.read_text())
        if len(data)==len(BEATS) and [x['text'] for x in data]==[x[0] for x in BEATS]:return data
    v=PiperVoice.load(str(MODEL));cursor=.32;lines=[];samples=[];sr=48000
    cfg=SynthesisConfig(speaker_id=0,length_scale=1.19,noise_scale=.58,noise_w_scale=.78)
    for i,(text,scene) in enumerate(BEATS):
        wav=CACHE/f'voice_{i:02d}.wav'
        with wave.open(str(wav),'wb') as f:v.synthesize_wav(text,f,syn_config=cfg)
        a=decode(wav)
        # Gentle high pass / level matching, with an inaudible segment boundary.
        from scipy.signal import butter,sosfiltfilt
        a=sosfiltfilt(butter(2,80,btype='highpass',fs=sr,output='sos'),a).astype('float32')
        peak=max(.001,float(np.max(np.abs(a))));a*=min(1.6,.64/peak)
        q=min(len(a)//4,round(.035*sr));a[:q]*=np.linspace(0,1,q);a[-q:]*=np.linspace(1,0,q)
        start=cursor;end=start+len(a)/sr;gap=.27 if i not in (4,8,12,16) else .48
        lines.append(dict(text=text,scene=scene,start=round(start,4),end=round(end,4)))
        samples.append(a);samples.append(np.zeros(round(gap*sr),np.float32));cursor=end+gap
    n=round((cursor+.52)*sr);voice=np.zeros(n,np.float32)
    for l,a in zip(lines,samples[::2]):
        off=round(l['start']*sr);voice[off:off+len(a)]+=a
    with wave.open(str(VOICE_PATH),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes(np.int16(np.clip(voice,-.99,.99)*32767).tobytes())
    TIMINGS_PATH.write_text(json.dumps(lines,indent=2)+'\n')
    return lines

TIMINGS=voice_and_timing();STARTS=[b['start'] for b in TIMINGS]
DUR=math.ceil((TIMINGS[-1]['end']+.65)*FPS)/FPS
FONT=ImageFont.truetype(g.BOLD,54);CAPFONT=ImageFont.truetype(g.FONT,42)
SMALL=ImageFont.truetype(g.BOLD,32);MED=ImageFont.truetype(g.BOLD,68)
# Each illustrated scale is separately composed: no source-video pixels.
WIDE=g.MAP_BASE
REGION=g.MAP_REGION
MACRO=g.MACRO
REEF=Image.open(HERE/'assets/keys_reef_cross_section.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
BRIDGE=Image.open(HERE/'assets/keys_overseas_bridge_aerial.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')


def ease(v):
    v=max(0,min(1,v));return v*v*(3-2*v)


def camera(img,z=1,cx=540,cy=960):
    cw,ch=W/z,H/z;cx=np.clip(cx,cw/2,W-cw/2);cy=np.clip(cy,ch/2,H-ch/2)
    return img.transform((W,H),Image.Transform.EXTENT,
         (cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)


def caption(canvas,text,opacity=1):
    # Small bottom-centered editorial subtitles, 2-5 words, restrained outline.
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    box=d.textbbox((0,0),text,font=CAPFONT);x=round((W-box[2]+box[0])/2);y=1553
    if x<70:
        # Rare longer chunk: do not clip under the Shorts controls.
        f=ImageFont.truetype(g.FONT,37);box=d.textbbox((0,0),text,font=f);x=round((W-box[2]+box[0])/2)
    else:f=CAPFONT
    d.text((x+2,y+4),text,font=f,fill=(2,22,30,220),stroke_width=4,stroke_fill=(2,22,30,200))
    d.text((x,y),text,font=f,fill=(248,251,249,255),stroke_width=1,stroke_fill=(9,40,49,220))
    layer.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
    return Image.alpha_composite(canvas,layer)


def txt(canvas,text,x,y,font=FONT,color=(248,251,249),glow=(7,190,211),align='left'):
    layer=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(layer);b=d.textbbox((0,0),text,font=font);wid=b[2]-b[0]
    if align=='center':x-=wid//2
    if align=='right':x-=wid
    mask=Image.new('L',(W,H))
    ImageDraw.Draw(mask).text((x,y),text,font=font,fill=255)
    glowim=Image.new('RGBA',(W,H),(*glow,0));glowim.putalpha(mask.filter(ImageFilter.GaussianBlur(19)).point(lambda a:round(a*.65)))
    layer=Image.alpha_composite(layer,glowim)
    ImageDraw.Draw(layer).text((x,y),text,font=font,fill=(*color,255),stroke_width=2,stroke_fill=(3,30,39,255))
    return Image.alpha_composite(canvas,layer)


def ring(canvas,x,y,r=65,color=(33,222,249),alpha=1):
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
    for rad,width,al in ((r+26,12,24),(r+8,7,90),(r,3,220)):
        d.ellipse((x-rad,y-rad,x+rad,y+rad),outline=(*color,round(al*alpha)),width=width)
    layer=layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(canvas,layer)


def guide(canvas,kind,local):
    # A different independently animated graphic layer in each shot.
    layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer,'RGBA')
    if kind=='reef':
        y=round(713+20*math.sin(local*.9));
        d.line([(70,y),(1010,y)],fill=(110,245,246,160),width=3)
        for x in range(80,1000,75):d.line([(x,y-9),(x,y+9)],fill=(193,252,247,115),width=2)
        d.ellipse((483,y-35,596,y+78),outline=(144,248,249,145),width=4)
    elif kind=='sea_high':
        y=round(740+50*ease(local/3));d.rectangle((0,y,W,H),fill=(1,132,184,round(36*ease(local/.5))))
        d.line([(0,y),(W,y)],fill=(89,241,250,220),width=6)
    elif kind=='sea_low':
        y=round(760-245*ease(local/3));d.rectangle((0,y,W,H),fill=(1,98,166,70))
        d.line([(0,y),(W,y)],fill=(235,242,214,235),width=5)
    elif kind=='bridge':
        y0=round(1660-850*ease(local/3.6))
        d.line([(540,y0),(540,1860)],fill=(74,245,249,65),width=34)
        d.line([(540,y0),(540,1860)],fill=(218,255,250,230),width=5)
        for y in range(1800,y0,-85):d.ellipse((534,y-6,546,y+6),fill=(255,250,211,225))
    elif kind=='bay':
        d.ellipse((75,490,518,1110),fill=(10,231,227,25),outline=(82,249,253,90),width=4)
    elif kind=='straits':
        d.ellipse((670,488,1130,1195),fill=(14,190,249,25),outline=(82,249,253,95),width=4)
    return Image.alpha_composite(canvas,layer)


def cloud_parallax(base,t,scale=.62):
    patch=g.CLOUD_MAP.copy()
    patch.putalpha(patch.getchannel('A').point(lambda a:round(a*scale)))
    shifted=patch.transform((W,H),Image.Transform.AFFINE,(1,0,19*math.sin(t*.36),0,1,13*math.cos(t*.24)),Image.Resampling.BILINEAR)
    return Image.alpha_composite(base,shifted)


def visual(i,t):
    beat=TIMINGS[i];typ=beat['scene'];local=t-beat['start'];length=max(.1,beat['end']-beat['start']);p=ease(local/length)
    # Motion continues throughout each shot; camera and overlays have different timing.
    if typ=='globe':
        lon=-22-35*ease(local/length);im=g.globe(lon,t)
        im=txt(im,'WHY DOES FLORIDA',540,106,MED,align='center')
        im=txt(im,'END IN ISLANDS?',540,186,MED,align='center')
        return im
    if typ=='orbital_map':
        full=camera(WIDE,1.02+.10*p,535+46*p,967-45*p)
        # First half second a mapped globe recedes behind a new atlas plate.
        if local<.48:
            old=g.globe(-57-20*ease(local/.48),t)
            full=Image.blend(old,full,ease(local/.48))
        return cloud_parallax(full,t)
    if typ=='region':
        reg=Image.blend(WIDE,REGION,ease(local/.65));im=camera(reg,1.07+.15*p,570+75*p,922-65*p)
        im=cloud_parallax(im,t)
        return txt(im,'FLORIDA',545,399,MED,align='center')
    if typ=='macro_reveal':
        mac=camera(MACRO,1.01+.06*p,540+40*p,960-30*p)
        if local<.38:
            old=camera(REGION,1.20,635,877);mac=Image.blend(old,mac,ease(local/.38))
        mac=cloud_parallax(mac,t,.52)
        mac=txt(mac,'THE FLORIDA KEYS',540,165,MED,align='center')
        return mac
    if typ=='macro_halo':
        im=MACRO.copy()
        for j,(x,y) in enumerate(((796,885),(633,1054),(500,1131),(353,1250),(242,1333))):
            if local>.17*j:im=ring(im,x,y,31,(57,246,244),ease((local-.17*j)/.5))
        im=camera(im,1.09+.06*p,591+55*p,1002+50*p)
        im=cloud_parallax(im,t,.56)
        return txt(im,'AN ISLAND CHAIN',542,190,MED,align='center')
    if typ in ('reef','reef_labels','sea_high','sea_low'):
        z=1.015+.09*p
        im=camera(REEF,z,538+42*p,958+40*p)
        im=guide(im,typ,local)
        if typ=='reef':im=txt(im,'FOSSIL CORAL REEF',540,264,MED,align='center')
        if typ=='reef_labels':
            im=txt(im,'LIMESTONE',705,964,FONT,align='center',glow=(234,182,70))
            im=txt(im,'SAND',325,1217,FONT,align='center',glow=(234,182,70))
        if typ=='sea_high':im=txt(im,'HIGHER SEAS',540,300,MED,align='center')
        if typ=='sea_low':im=txt(im,'LOWER SEAS',540,300,MED,align='center')
        return im
    if typ=='macro_islands':
        im=MACRO.copy()
        for j,(x,y) in enumerate(((779,916),(636,1051),(502,1158),(357,1273),(252,1328))):
            if local>j*.19:im=ring(im,x,y,24,(55,248,220),ease((local-j*.19)/.6))
        im=cloud_parallax(camera(im,1.16-.12*p,643-67*p,1030-80*p),t,.56)
        return txt(im,'ISLANDS REMAIN',540,168,MED,align='center')
    if typ=='road_wide':
        frac=ease(local/length);route=g.MACRO_ROUTE[round(frac*16)]
        im=Image.alpha_composite(MACRO,route)
        im=cloud_parallax(camera(im,1.02+.12*p,540+50*p,960+10*p),t,.5)
        return txt(im,'OVERSEAS HIGHWAY',540,154,MED,align='center')
    if typ=='bridge':
        im=camera(BRIDGE,1.08+.13*p,540,1055-120*p)
        im=guide(im,'bridge',local)
        return txt(im,'ROAD OVER WATER',540,172,MED,align='center')
    if typ=='route_stops':
        im=Image.alpha_composite(MACRO,g.MACRO_ROUTE[16])
        im=ring(im,250,1323,56,(255,224,127),ease(local/.45))
        im=camera(im,1.12+.1*p,598+30*p,1050+40*p)
        return txt(im,'NOT EVERY ISLAND',540,171,MED,align='center')
    if typ=='westward':
        im=camera(MACRO,1.14-.12*p,570-25*p,984-35*p)
        im=ring(im,252,1300,40,(73,240,246),1)
        im=txt(im,'KEY WEST',216,1416,FONT,align='center')
        return txt(im,'THE CHAIN CONTINUES',540,165,MED,align='center')
    if typ in ('bay','straits'):
        im=cloud_parallax(camera(MACRO,1.01+.07*p,540,960),t,.55)
        im=guide(im,typ,local)
        if typ=='bay':return txt(im,'FLORIDA BAY',294,560,MED,align='center')
        return txt(im,'STRAITS OF FLORIDA',752,1110,FONT,align='center')
    if typ=='pullback':
        im=cloud_parallax(camera(REGION,1.17-.13*p,580-40*p,921+45*p),t,.55)
        return txt(im,'ANCIENT REEFS',540,165,MED,align='center')
    # End with a coherent coastline/route final pullback, not a generic logo.
    im=cloud_parallax(camera(REGION,1.13-.10*p,565,940),t,.48)
    im=txt(im,'REEFS  •  ROCK  •  SEA',540,158,MED,align='center')
    im=txt(im,'FLORIDA KEYS',540,275,FONT,align='center')
    return im


def phrase(t,idx):
    b=TIMINGS[idx];words=b['text'].split();n=len(words)
    # Reference-like 2-5-word subtitle beats, tied to recorded narration.
    parts=[' '.join(words[k:k+4]) for k in range(0,n,4)]
    q=(t-b['start'])/max(.01,b['end']-b['start'])
    j=min(len(parts)-1,max(0,int(q*len(parts))))
    phase=q*len(parts)-j
    fade=min(1,phase/.1,(1-phase)/.11,(b['end']-t)/.16)
    return parts[j],max(0,fade)


def frame(t):
    i=max(0,min(len(TIMINGS)-1,bisect.bisect_right(STARTS,t)-1))
    if t>TIMINGS[-1]['end']:
        im=visual(len(TIMINGS)-1,TIMINGS[-1]['end'])
    else:im=visual(i,t)
    # Carefully timed dissolves connect related scales; most other beats hard-cut.
    if i and 0<t-STARTS[i]<.22 and TIMINGS[i]['scene'] in ('reef','bridge','bay','pullback'):
        old=visual(i-1,TIMINGS[i-1]['end']);im=Image.blend(old,im,ease((t-STARTS[i])/.22))
    if STARTS[i]<=t<TIMINGS[i]['end']:
        text,opacity=phrase(t,i)
        im=caption(im,text,opacity)
    return im.convert('RGB')


def mix():
    voice=decode(VOICE_PATH)
    wave_sound=decode(WAVE);wind=decode(WIND)
    n=round(DUR*48000)
    def loop(a):return np.tile(a,math.ceil(n/len(a)))[:n]
    surf=loop(wave_sound);breeze=loop(wind)
    surf-=surf.mean();breeze-=breeze.mean()
    # Recorded beach/wind only: vocal intelligibility first, quick edit-whooshes.
    a=np.zeros(n,np.float32);a[:min(n,len(voice))]=voice[:n]
    env=np.minimum(1,np.arange(n)/(.8*48000))*np.minimum(1,np.arange(n)[::-1]/(.8*48000))
    bed=(.075*surf+.03*breeze)*env
    for i,b in enumerate(TIMINGS[1:]):
        # Dynamic gust as a transition accent; attenuate beneath words.
        s=round((b['start']-.1)*48000);length=round(.41*48000)
        if 0<=s and s+length<n:
            swell=np.sin(np.linspace(0,math.pi,length))**2
            bed[s:s+length]+=.09*breeze[s:s+length]*swell
    # constrain voice peak to a natural short-form narration level
    mixL=a*.93+bed*.91;mixR=a*.98+bed
    peak=max(np.max(np.abs(mixL)),np.max(np.abs(mixR)));scale=min(1,.87/max(.001,peak))
    stereo=np.column_stack((mixL*scale,mixR*scale))
    with wave.open(str(MIX_PATH),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000)
        w.writeframes((np.clip(stereo,-.99,.99)*32767).astype('<i2').tobytes())
    return MIX_PATH


def render():
    audio=mix();total=round(DUR*FPS);print('duration',DUR,'frames',total,'lines',len(BEATS),flush=True)
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','pipe:0','-i',str(audio),'-map','0:v','-map','1:a',
         '-c:v','libx264','-threads','2','-preset','medium','-crf','18','-maxrate','9M','-bufsize','18M','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart','-shortest',str(OUT)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(total):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%120==0:print('render',k,'/',total,flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('ffmpeg encode failed')
    finally:
        if p.poll() is None:p.kill()
    print('MASTER',OUT,OUT.stat().st_size,flush=True)

if __name__=='__main__':render()

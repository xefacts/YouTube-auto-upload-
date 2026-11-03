#!/usr/bin/env python3
"""V10 Florida selected-PRISM private review with a fictional non-graphic flashback.

All 39.23s of the selected original VO are retained at the established 1.075x
pace. The output is 2160x3840, upscaled from 768/1024px source artwork;
DO NOT claim native 4K source detail or verbatim caption transcription.
"""
from pathlib import Path
import importlib.util
import math
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
EP = HERE.parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location('florida_v6', HERE/'render_v5.py')
v6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v6)
old = v6.old
FF = imageio_ffmpeg.get_ffmpeg_exe()
CACHE = HERE/'render_cache'; CACHE.mkdir(exist_ok=True)
W, H, FPS, DUR = 1080, 1920, 24, 41.0
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 94)
SANS = ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'), 28)
SMALL = ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'), 22)

# 12.65s first balcony frame ALREADY contains the user's confirmed PRISM detective.
# Locked-door and balcony/thread beats get time to breathe; no repeat watch at end.
# start, end, image, starting/ending zoom, normalized camera focal points
SHOTS = [
 (0,2.2,'exterior',1.02,1.15,(.50,.51),(.55,.44)),
 (2.2,4.23,'flashback',1.03,1.11,(.50,.54),(.52,.53)),
 (4.23,5.2,'slumped',1.05,1.12,(.54,.56),(.53,.57)),
 (5.2,5.95,'hall_open',1.04,1.08,(.51,.50),(.54,.50)),
 (5.95,6.8,'door_half',1.08,1.13,(.57,.49),(.58,.49)),
 (6.8,9.55,'prism_corridor',1.14,1.20,(.60,.51),(.59,.52)),
 (9.55,10.85,'watch_once',1.30,1.40,(.20,.69),(.20,.70)),
 (10.85,12.65,'prism_suite',1.12,1.17,(.45,.56),(.43,.57)),
 (12.65,15.20,'prism_balcony',1.04,1.10,(.43,.57),(.43,.57)),
 (15.20,15.96,'bolt_open',1.04,1.10,(.50,.51),(.50,.51)),
 (15.96,17.20,'bolt_closed',1.12,1.21,(.50,.51),(.52,.51)),
 (17.20,18.63,'wife',1.09,1.15,(.51,.53),(.51,.53)),
 (18.63,20.22,'wife_turn',1.15,1.20,(.51,.53),(.51,.52)),
 (20.22,21.85,'partner',1.07,1.13,(.51,.53),(.51,.53)),
 (21.85,24.30,'partner',1.13,1.20,(.51,.52),(.51,.52)),
 (24.30,26.05,'prism_thread',1.05,1.12,(.46,.57),(.48,.57)),
 (26.05,29.10,'rail_thread',1.55,1.88,(.70,.52),(.69,.53)),
 (29.10,31.45,'coat',1.06,1.18,(.56,.49),(.59,.50)),
 (31.45,33.65,'thread_art',1.08,1.21,(.40,.56),(.41,.56)),
 (33.65,36.60,'window',1.64,1.74,(.62,.35),(.63,.35)),
 (36.60,41.00,'end_pullback',2.38,1.02,(.62,.35),(.50,.51))
]
assert SHOTS[0][0] == 0 and SHOTS[-1][1] == DUR
assert all(a[1] == b[0] for a,b in zip(SHOTS,SHOTS[1:])), 'shot gap/overlap'

# Top-only typography, consciously sparse since the source VO does not have an
# approved word-level transcript. No lower-third or invented historical facts.
CUES = [
 (.18,1.85,'THE LOCKED SUITE'),
 (6.89,8.82,'NO FORCED ENTRY'),
 (12.85,14.72,'THE BALCONY'),
 (24.58,26.48,'A SINGLE THREAD'),
]

# Soft contrast and restrained teal shadows/warm highlights, computed ONCE per
# source image (not a framewise Instagram-style filter). Same grade for art and plates.
def grade(im):
    rgb = np.asarray(im.convert('RGB'), dtype=np.uint8)
    lut = np.interp(np.arange(256), [0,26,72,132,196,255],
                    [4,23,70,139,206,250]).astype(np.uint8)
    base = lut[rgb].astype(np.float32)
    luma = .24*base[:,:,0]+.67*base[:,:,1]+.09*base[:,:,2]
    shadow = np.clip((125-luma)/125,0,1)
    light = np.clip((luma-135)/120,0,1)
    base[:,:,0] += -4*shadow+5*light
    base[:,:,1] += 2*shadow+1*light
    base[:,:,2] += 5*shadow-5*light
    mono = base[:,:,0]*.25+base[:,:,1]*.65+base[:,:,2]*.10
    base = mono[:,:,None]+(base-mono[:,:,None])*1.09
    ans = Image.fromarray(np.uint8(np.clip(base,0,255)), 'RGB')
    if im.mode == 'RGBA':
        ans.putalpha(im.getchannel('A'))
    return ans

IM = {k:grade(v) for k,v in old.IMAGES.items() if k not in ('investigator_suite','investigator_balcony')}
IM['flashback'] = grade(Image.open(HERE/'assets/fictional_flashback_shooter.png').convert('RGB'))
IM['coat'] = grade(Image.open(EP/'phase3/11_anonymous_coat_fiber.png').convert('RGB'))
IM['thread_art'] = grade(Image.open(EP/'phase3/09_thread_on_balcony_rail.png').convert('RGB'))

# New poses use only the user's selected PRISM sheet; the older tan-coat actor
# never appears. Isolate pure-white key backdrops, retaining selected face/coat.
def prism_isolate(name):
    """Remove white holes AND the studio floor shadow from the selected art.

    The older cutout helper fills silhouette holes and retains pale cast shadows;
    those look like white wedges/hovering feet against photographic hotel floors.
    """
    im=v6.isolate(name)
    rgba=np.asarray(im).copy()
    rgb=rgba[:,:,:3].astype(np.int16)
    low=rgb.min(axis=2);high=rgb.max(axis=2)
    white_hole=(low>236)&((high-low)<24)
    yy=np.arange(im.height)[:,None]
    studio_shadow=(yy>im.height*.82)&(low>70)&((high-low)<24)
    rgba[:,:,3][white_hole|studio_shadow]=0
    return Image.fromarray(rgba,'RGBA')

SPRITES = {n:grade(prism_isolate(n)) for n in
           ('prism_corridor_stand','prism_suite_look','prism_balcony_stand')}
SPRITES.update({n:grade(v6.SPRITES[n]) for n in
                ('businessman_master','businessman_watch_pose','wife_master',
                 'wife_turn_pose','partner_master','partner_case_pose')})

ACTORS = {
 'alive':('suite',477,1310,640),
 'prism_corridor':('door_closed',326,1250,718),
 'prism_suite':('suite',525,1290,665),
 'prism_balcony':('balcony',337,1282,605),
 'prism_thread':('balcony',337,1282,605),
 'wife':('hall_open',395,1170,645),
 'wife_turn':('hall_open',395,1170,645),
 'partner':('hall_open',410,1180,670)
}

def plate_for(t,key):
    if key not in ACTORS:
        return IM['suite' if key=='watch_once' else 'balcony' if key=='rail_thread' else
                  'exterior' if key in ('window','end_pullback') else key]
    plate,x,y,height = ACTORS[key]
    pose = {
      'alive':'businessman_master' if t<2.95 else 'businessman_watch_pose',
      'prism_corridor':'prism_corridor_stand',
      'prism_suite':'prism_suite_look',
      'prism_balcony':'prism_suite_look',
      'prism_thread':'prism_balcony_stand',
      'wife':'wife_master','wife_turn':'wife_turn_pose',
      'partner':'partner_master' if t<21.85 else 'partner_case_pose'
    }[key]
    fg = SPRITES[pose]
    fg = fg.resize((round(fg.width*height/fg.height),height), Image.Resampling.LANCZOS)
    bg = IM[plate].convert('RGBA')
    px,py = round(x-fg.width/2),round(y-height)
    sh = Image.new('RGBA',bg.size)
    ImageDraw.Draw(sh).ellipse((px+fg.width*.15,y-12,px+fg.width*.85,y+12),fill=(0,0,0,133))
    bg = Image.alpha_composite(bg,sh.filter(ImageFilter.GaussianBlur(10)))
    bg.alpha_composite(fg,(px,py))
    return bg.convert('RGB')

# Reuse three composited shot plates/poses for ~60% of the runtime; intentional
# source-based pan/zoom provides movement while feet never glide on the floor.
def crop(im,zoom,focus):
    iw,ih=im.size
    cw,ch=iw/zoom,ih/zoom
    cx=np.clip(focus[0]*iw,cw/2,iw-cw/2)
    cy=np.clip(focus[1]*ih,ch/2,ih-ch/2)
    return im.transform((W,H),Image.Transform.EXTENT,
                        (cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)

# Pre-render cue art to avoid drawing high-resolution type 1,000 times.
TYPE = {}
for _,_,text in CUES:
    layer = Image.new('RGBA',(W,H))
    d = ImageDraw.Draw(layer)
    font = FONT
    while d.textbbox((0,0),text,font=font)[2]>W-150:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf',font.size-4)
    x=90;y=185
    d.rounded_rectangle((x,y-42,x+44,y-35),radius=3,fill=(221,158,84,245))
    d.text((x,y-14),'CASE NOTES',font=SANS,fill=(227,190,146,255))
    d.text((x+2,y+38),text,font=font,fill=(10,18,23,250),stroke_width=5,stroke_fill=(10,18,23,235))
    d.text((x,y+35),text,font=font,fill=(249,239,222,255))
    tw=d.textbbox((0,0),text,font=font)[2]
    d.line((x,y+158,x+min(tw,620),y+158),fill=(215,143,79,245),width=4)
    TYPE[text]=layer

# A restrained top gradient protects title contrast without obscuring the image.
TOP = Image.new('RGBA',(W,425),(4,11,16,0))
TOP.putalpha(Image.fromarray(np.uint8(np.linspace(153,0,425))[:,None].repeat(W,1),'L'))

def frame(t):
    sh=next(s for s in SHOTS if s[0]<=t<s[1]) if t<DUR else SHOTS[-1]
    a,b,key,z0,z1,p0,p1=sh
    u=old.ease((t-a)/(b-a)) if key!='end_pullback' else 1-(1-(t-a)/(b-a))**2.35
    z=z0+(z1-z0)*u
    if key=='flashback' and 3.34 <= t < 3.54:
        # A single short, damped camera kick follows the fictional gunshot.
        z += .032*math.exp(-17*(t-3.34))*math.cos((t-3.34)*53)
    c=(p0[0]+(p1[0]-p0[0])*u,p0[1]+(p1[1]-p0[1])*u)
    image=crop(plate_for(t,key),z,c)
    if key=='flashback' and 3.34 <= t < 3.48:
        # Brief muzzle flash at the anonymous shooter's weapon, with no impact
        # or victim wound. The flash is art-directed rather than a second shot.
        x,y=round(W*.73),round(H*.513)
        strength=max(0,1-(t-3.34)/.14)
        flare=Image.new('RGBA',(W,H))
        d=ImageDraw.Draw(flare)
        size=round(48*strength+17)
        d.polygon([(x-10,y),(x+size,y-20),(x+size//3,y+3),
                   (x+size//2,y+size//3),(x-14,y+7)],
                  fill=(255,216,129,round(205*strength)))
        d.ellipse((x-35,y-35,x+35,y+35),fill=(255,160,64,round(75*strength)))
        image=Image.alpha_composite(image.convert('RGBA'),flare.filter(ImageFilter.GaussianBlur(2))).convert('RGB')
    cue=next(((x,y,s) for x,y,s in CUES if x<=t<y),None)
    if cue:
        x,y,s=cue
        fade=min(1,old.ease((t-x)/.24),old.ease((y-t)/.24))
        if fade>.005:
            image=image.convert('RGBA')
            shade=TOP.copy()
            shade.putalpha(shade.getchannel('A').point(lambda a:round(a*fade)))
            image.alpha_composite(shade,(0,0))
            layer=TYPE[s].copy()
            layer.putalpha(layer.getchannel('A').point(lambda a:round(a*fade)))
            image.alpha_composite(layer)
            image=image.convert('RGB')
    if t<2.2:
        ImageDraw.Draw(image,'RGBA').text((90,100),'FICTIONAL DRAMATIZATION',
                      font=SMALL,fill=(249,232,204,225))
    return image

def soundtrack():
    """Original stereo non-melodic score and synced wood/metal/cloth Foley."""
    sr=48000;n=round(sr*DUR)
    rng=np.random.default_rng(9472)
    voice=old.read_audio(EP/'audio/voice_full_1934_edit.mp3',sr)
    percussion=old.read_audio(EP/'audio/percussion_air_draft.mp3',sr)
    a=np.zeros((n,2),np.float32)
    a[:len(voice),:]+=(.88*voice)[:,None]
    a[:min(n,len(percussion)),:]+=(.19*percussion[:n])[:,None]
    # Independent L/R rain textures plus a shared low wind bed. No third-party
    # sound or pitched theme; the selected narration remains centered and legible.
    for ch in (0,1):
        r=rng.normal(0,1,n).astype(np.float32)
        h=sosfilt(butter(2,950,fs=sr,output='sos'),r).astype(np.float32)
        a[:,ch]+=.0034*(r-h)
    r=rng.normal(0,1,n).astype(np.float32)
    wind=sosfilt(butter(2,170,fs=sr,output='sos'),r).astype(np.float32)
    a+=.15*wind[:,None]
    def add(at,sig,pan=0):
        ix=int(at*sr)
        if ix>=n:return
        sig=np.asarray(sig[:n-ix],np.float32)
        a[ix:ix+len(sig),0]+=sig*math.sqrt((1-pan)/2)
        a[ix:ix+len(sig),1]+=sig*math.sqrt((1+pan)/2)
    def thud(at,scale=.1):
        z=np.arange(int(.8*sr),dtype=np.float32)/sr
        nse=sosfilt(butter(2,480,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        x=(nse*.65+np.sin(2*np.pi*(79*z-11*z*z))*.2)*np.exp(-z*11)*scale
        add(at,x)
        add(at+.11,x*.24,pan=-.2)
    # The two optional performances are *new fictional dialogue*, not part of
    # the preserved narration. Their low level leaves the complete VO legible.
    alarm=old.read_audio(HERE/'assets/businessman_alarm.wav',sr)
    laugh=old.read_audio(HERE/'assets/anonymous_villain_laugh.wav',sr)
    add(2.26,.22*alarm,pan=-.20)
    add(3.94,.16*laugh,pan=.26)
    # One stylized gunshot at the brief muzzle flash; no victim impact sound.
    z=np.arange(int(.62*sr),dtype=np.float32)/sr
    noise=rng.normal(0,1,len(z)).astype(np.float32)
    low=sosfilt(butter(2,540,fs=sr,output='sos'),noise).astype(np.float32)
    shot=(.46*noise*np.exp(-z*84)+.48*low*np.exp(-z*12)
          +.11*np.sin(2*np.pi*(95*z-38*z*z))*np.exp(-z*10))
    add(3.34,shot,pan=.36)
    # Heavy door: hinge rub while moving through the half-closed plate, short
    # wood slam exactly at the cut to the CLOSED plate. Not a fake historical sound.
    z=np.arange(int(.92*sr),dtype=np.float32)/sr
    rub=sosfilt(butter(2,[150,1400],btype='bandpass',fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
    add(5.87,(.055*rub+.027*np.sin(2*np.pi*(182*z-47*z*z)))*(np.sin(np.pi*z/.92)**2),pan=.20)
    thud(6.80,.92)
    for at,amp in ((15.96,.074),(16.13,.025),(24.68,.026)):
        z=np.arange(int(.16*sr),dtype=np.float32)/sr
        sig=(np.sin(2*np.pi*1770*z)+.23*rng.normal(0,1,len(z)))*np.exp(-z*50)*amp
        add(at,sig,pan=.27)
    # Cinematic air-rise and soft tension drops emphasize discoveries, not every
    # single cut; wide sound narrows beneath the voice and opens after its last line.
    for at,duration,amp in ((4.75,1.2,.12),(15.26,.7,.13),(24.15,1.8,.17),
                            (29.20,1.2,.15),(35.75,1.45,.20)):
        z=np.arange(int(duration*sr),dtype=np.float32)
        q=sosfilt(butter(2,380,fs=sr,output='sos'),rng.normal(0,1,len(z))).astype(np.float32)
        add(at,amp*q*np.sin(np.pi*z/len(z))**2,pan=-.3)
    for at,level in ((0.1,.22),(9.55,.12),(29.1,.10),(36.6,.45)):
        thud(at,level)
    # Keep the last spoken line intact; only increase background after it ends.
    end=int(36.49*sr)
    air=np.clip(np.arange(n-end)/(1.5*sr),0,1).astype(np.float32)
    a[end:]+=(.14*wind[end:]*air)[:,None]
    a=np.tanh(a*1.03)
    peak=np.max(np.abs(a))
    if peak>.94:a*=.94/peak
    a[-int(.32*sr):]*=np.linspace(1,0,int(.32*sr))[:,None]
    path=CACHE/'v10_flashback_full_voice_stereo.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((a*32767).astype('<i2').tobytes())
    return path

if __name__=='__main__':
    wav=soundtrack()
    raw=CACHE/'silent_v10_1080.mp4'
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-c:v','libx264',
         '-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*5)==0:print('frame',k,flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('1080p video encoding failed')
    finally:
        if p.poll() is None:p.kill()
    out=HERE/'FLORIDA_V10_FICTIONAL_FLASHBACK_PRISM_FULL_VOICE_4K_UPSCALED_PRIVATE_REVIEW.mp4'
    # Memory-bounded 4K-size upscale, NOT native-detail 4K art. The V9 Lanczos
    # + unsharp + veryfast pipeline was OOM-killed on this smaller worker; the
    # bicubic/no-lookahead encode below was tested through full 984-frame decode.
    # Preserve the full VO, including its last line, without shifting later cuts.
    subprocess.run([FF,'-y','-loglevel','error','-threads','1','-filter_threads','1',
        '-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
        '-vf','scale=2160:3840:flags=bicubic',
        '-c:v','libx264','-threads','1','-preset','ultrafast','-crf','25',
        '-x264-params','ref=1:rc_lookahead=0:bframes=0','-pix_fmt','yuv420p',
        '-af','loudnorm=I=-18:TP=-1.5:LRA=8',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
        '-shortest',str(out)],check=True)
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

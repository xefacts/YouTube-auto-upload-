#!/usr/bin/env python3
"""V11 final-cut candidate: exact full VO runtime; consistent non-graphic flashback.

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
W, H, FPS, DUR = 1080, 1920, 24, 36.5
FONT = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf', 94)
SANS = ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'), 28)
SMALL = ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'), 22)

# 12.65s first balcony frame ALREADY contains the user's confirmed PRISM detective.
# Locked-door and balcony/thread beats get time to breathe; no repeat watch at end.
# start, end, image, starting/ending zoom, normalized camera focal points
SHOTS = [
 (0,2.2,'exterior',1.02,1.15,(.50,.51),(.55,.44)),
 (2.2,3.67,'flashback',1.03,1.10,(.50,.54),(.52,.53)),
 (3.67,4.15,'falling',1.10,1.14,(.53,.54),(.53,.56)),
 (4.15,5.2,'collapsed',1.06,1.10,(.53,.55),(.53,.55)),
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
 (29.10,30.55,'coat',1.08,1.19,(.56,.49),(.58,.50)),
 (30.55,31.55,'thread_art',1.08,1.20,(.40,.56),(.41,.56)),
 (31.55,34.10,'clue_board',1.00,1.00,(.50,.50),(.50,.50)),
 (34.10,36.50,'end_pullback',2.20,1.08,(.62,.35),(.50,.50))
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
                    [8,29,74,140,207,250]).astype(np.uint8)
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
IM['flashback'] = grade(Image.open(HERE/'assets/florida_suite_shooter_consistent.png').convert('RGB'))
IM['falling'] = grade(Image.open(HERE/'assets/florida_suite_falling_consistent.png').convert('RGB'))
IM['collapsed'] = grade(Image.open(HERE/'assets/florida_suite_collapse_consistent.png').convert('RGB'))
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

# Original, editable clue collage inspired by the reference's pacing/cutout grammar,
# not by reusing its images, text, logos or music. Panels are from our own art.
from PIL import ImageOps
paper_rng=np.random.default_rng(1103)
yy=np.arange(H,dtype=np.float32)[:,None]
xx=np.arange(W,dtype=np.float32)[None,:]
texture=paper_rng.normal(0,1.9,(H,W)).astype(np.float32)
paper=np.empty((H,W,3),dtype=np.uint8)
for ch,base in enumerate((34,42,46)):
    paper[:,:,ch]=np.uint8(np.clip(base+12*(1-yy/H)+4*(xx/W)+texture,0,255))
PAPER=Image.fromarray(paper,'RGB')
PANEL_THREAD=ImageOps.fit(IM['thread_art'],(625,840),method=Image.Resampling.LANCZOS,centering=(.58,.53))
PANEL_FIBER=ImageOps.fit(IM['coat'],(590,855),method=Image.Resampling.LANCZOS,centering=(.55,.50))
BOARD_FONT=ImageFont.truetype(str(ROOT/'assets/fonts/DMSans.ttf'),32)

def clue_board(t):
    im=PAPER.copy().convert('RGBA')
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((58,96,W-58,100),fill=(190,141,90,180))
    d.text((72,125),'THE REMAINING CLUES',font=SANS,fill=(233,218,186,255))
    # Stagger the original stills into the frame like a moving dossier.
    enter1=old.ease((t-31.55)/.46)
    enter2=old.ease((t-32.02)/.48)
    def mount(src,x,y,n):
        if n<.001:return
        x=int(x);y=int(y)
        sh=Image.new('RGBA',im.size)
        ImageDraw.Draw(sh).rounded_rectangle((x+8,y+13,x+src.width+16,y+src.height+21),
            radius=12,fill=(0,0,0,150))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
        ImageDraw.Draw(im).rectangle((x-8,y-8,x+src.width+8,y+src.height+8),fill=(211,198,171,255))
        im.paste(src,(x,y))
    mount(PANEL_THREAD,-520+615*enter1,278,enter1)
    mount(PANEL_FIBER,1015-660*enter2,790,enter2)
    # Simple annotation appears only after both panels; no bottom-frame text.
    ink=old.ease((t-32.68)/.70)
    if ink>.01:
        d=ImageDraw.Draw(im,'RGBA')
        d.arc((350,640,635,920),32,32+290*ink,fill=(169,72,62,int(210*ink)),width=7)
        d.line((570,840,620+200*ink,1020+70*ink),fill=(171,78,64,int(225*ink)),width=5)
        d.ellipse((560,830,578,848),fill=(184,76,59,int(235*ink)))
    d=ImageDraw.Draw(im,'RGBA')
    # Evidence imagery only below the upper heading; no lower-third labels.
    return im.convert('RGB')

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
    if key in ('flashback','falling'):
        # Source-space dark pistol lies on the anonymous outstretched arm;
        # its position and flash follow camera crop exactly. Only one shot.
        plate=plate_for(t,key).copy().convert('RGBA')
        g=ImageDraw.Draw(plate,'RGBA')
        g.polygon([(436,526),(481,526),(494,531),(497,539),(459,542),
                   (452,564),(439,561),(445,542),(435,539)],fill=(8,17,22,255))
        g.line([(440,529),(478,529)],fill=(62,79,77,185),width=2)
        if key=='flashback' and 3.34 <= t < 3.48:
            power=max(0,1-(t-3.34)/.14)
            glow=Image.new('RGBA',plate.size)
            gd=ImageDraw.Draw(glow)
            gd.ellipse((467,507,533,561),fill=(255,164,72,int(105*power)))
            plate=Image.alpha_composite(plate,glow.filter(ImageFilter.GaussianBlur(13)))
            g=ImageDraw.Draw(plate,'RGBA')
            g.polygon([(494,533),(528,521),(518,535),(542,543),
                       (507,546),(515,560),(493,541)],
                      fill=(255,221,135,int(240*power)))
        image=crop(plate.convert('RGB'),z,c)
    else:
        image=clue_board(t) if key=='clue_board' else crop(plate_for(t,key),z,c)
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
    # Original dark score: low harmonic drone, gentle bowed pulse and a sparse
    # two-note motif. Pulled down beneath dialogue; no borrowed sample or melody.
    z=np.arange(n,dtype=np.float32)/sr
    duck=np.ones(n,dtype=np.float32)
    duck[int(2.2*sr):int(6.0*sr)]=.38
    drone=(np.sin(2*np.pi*55*z)+.28*np.sin(2*np.pi*82.41*z))*          (.008+.004*np.sin(2*np.pi*.12*z)**2)*duck
    a[:,0]+=drone*.94
    a[:,1]+=drone*1.06
    for beat,frequency in ((.4,110),(10.9,82.41),(20.2,110),(29.2,82.41),(34.1,110)):
        ix=int(beat*sr);dur=min(int(2.25*sr),n-ix)
        if dur<=0:continue
        q=np.arange(dur,dtype=np.float32)/sr
        bell=(np.sin(2*np.pi*frequency*q)+.28*np.sin(2*np.pi*2.01*frequency*q))*             np.exp(-2.35*q)*(.018 if beat>6 else .012)
        add(beat,bell,pan=(-.17 if beat%2 else .17))
    # The two optional performances are *new fictional dialogue*, not part of
    # the preserved narration. Their low level leaves the complete VO legible.
    alarm=old.read_audio(HERE/'assets/businessman_alarm.wav',sr)
    laugh=old.read_audio(HERE/'assets/anonymous_villain_laugh.wav',sr)
    add(2.26,.22*alarm,pan=-.20)
    add(3.94,.23*laugh,pan=.26)
    # One stylized gunshot at the brief muzzle flash; no graphic impact.
    z=np.arange(int(.62*sr),dtype=np.float32)/sr
    noise=rng.normal(0,1,len(z)).astype(np.float32)
    low=sosfilt(butter(2,540,fs=sr,output='sos'),noise).astype(np.float32)
    shot=(.46*noise*np.exp(-z*84)+.48*low*np.exp(-z*12)
          +.11*np.sin(2*np.pi*(95*z-38*z*z))*np.exp(-z*10))
    add(3.34,shot,pan=-.36)
    # Cloth/chair settling supports the intermediate and final original keyframes.
    for at,amp in ((3.72,.040),(4.15,.088)):
        q=np.arange(int(.42*sr),dtype=np.float32)/sr
        rustle=sosfilt(butter(2,880,fs=sr,output='sos'),rng.normal(0,1,len(q))).astype(np.float32)
        add(at,amp*rustle*np.exp(-q*14),pan=.28)
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
    for at,level in ((0.1,.22),(9.55,.12),(29.1,.10),(31.55,.12),(34.10,.30)):
        thud(at,level)
    # Match the video's last frame to the FULL processed narration: no 4.5s tail.
    a=np.tanh(a*1.03)
    peak=np.max(np.abs(a))
    if peak>.94:a*=.94/peak
    # Only fade the last 90ms of bed/FX; never fade or cut the selected narration.
    # The full voice sample stream itself is always mixed into the last frame.
    path=CACHE/'v11_vo_matched_stereo.wav'
    with wave.open(str(path),'wb') as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr)
        w.writeframes((a*32767).astype('<i2').tobytes())
    return path

if __name__=='__main__':
    wav=soundtrack()
    raw=CACHE/'silent_v11_1080.mp4'
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
    out=HERE/'FLORIDA_V11_VO_MATCHED_PRISM_FLASHBACK_PRIVATE_REVIEW_4K_UPSCALED.mp4'
    # Memory-bounded 4K-size upscale, not native-detail 4K artwork.
    # Preserve the full VO including its last line, ending on the voice boundary.
    subprocess.run([FF,'-y','-loglevel','error','-threads','1','-filter_threads','1',
        '-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
        '-vf','scale=2160:3840:flags=bicubic',
        '-c:v','libx264','-threads','1','-preset','ultrafast','-crf','25',
        '-x264-params','ref=1:rc_lookahead=0:bframes=0','-pix_fmt','yuv420p',
        '-af','loudnorm=I=-18:TP=-1.5:LRA=8',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
        '-shortest',str(out)],check=True)
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

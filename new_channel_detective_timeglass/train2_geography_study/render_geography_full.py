#!/usr/bin/env python3
"""Original satellite-style geography explainer, 36 s, portrait 1080p/30.

3D sphere is software-rendered using a UV-sphere ray projection and NASA Earth
textures fetched from GitHub (see README). Map closeups are an illustrative
backplate, NOT GIS-verified satellite observations or a real hotel locator.
The five user-supplied Train 2 videos are style references, never source pixels.
"""
from pathlib import Path
import math,subprocess,wave
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from imageio_ffmpeg import get_ffmpeg_exe
import build_study as style
HERE=Path(__file__).resolve().parent
W,H,FPS,DUR=1080,1920,30,36
FF=get_ffmpeg_exe()
OUT=HERE/'FLORIDA_GEOGRAPHY_FULL_STYLE_STUDY_1080x1920.mp4'
CACHE=HERE/'render_cache';CACHE.mkdir(exist_ok=True)
NASA=HERE/'assets/globe_nasa'
SOUND=HERE.parent/'episodes/florida_hotel_mystery_001/v5_articulated/assets/v18_cc0_weather'
FONT=style.FONT_SANS
BOLD=style.FONT_BOLD
BASE=style.BASE.convert('RGB')
REGION=style.REGION
ROUTE_LAYERS=[style.route_layer(max(.01,i/18)) for i in range(19)]
LABELS=style.LABELS
CLOSE_LABELS=Image.new('RGBA',(W,H))
for text,x,y,size in [('FLORIDA',532,443,56),('CUBA',455,1105,47),
                      ('BAHAMAS',844,923,33),('KEY WEST',554,958,35)]:
    style.glow_text(CLOSE_LABELS,text,x,y,size)
PIN=style.PIN
DAY=cv2.cvtColor(cv2.imread(str(NASA/'earth-day-2048.jpg'),cv2.IMREAD_COLOR),cv2.COLOR_BGR2RGB)
NIGHT=cv2.imread(str(NASA/'earth-night-2048.jpg'),cv2.IMREAD_GRAYSCALE)
CLOUD=cv2.imread(str(NASA/'earth-clouds-2048.jpg'),cv2.IMREAD_GRAYSCALE)
assert DAY.shape[:2]==(1024,2048)

# Precompute an actual visible hemisphere's surface normals on a round globe,
# not a flat map disk masquerading as a 3D object. Recomputed UV coordinates
# per camera yaw; clouds rotate independently of the terrestrial sphere.
RES=920
Y,X=np.mgrid[:RES,:RES].astype(np.float32)
ux=(X-RES/2)/(RES/2-7);vy=(Y-RES/2)/(RES/2-7)
r2=ux**2+vy**2;inside=r2<=1
nz=np.sqrt(np.maximum(0,1-r2));lat=np.arcsin(np.clip(-vy,-1,1))
dlon=np.arctan2(ux,nz)
shade=np.clip(.19+.81*np.maximum(0,.22*ux-.25*vy+.87*nz),0,1).astype(np.float32)
rho=np.sqrt(r2)
alpha=np.uint8(inside*255)

font_title=ImageFont.truetype(BOLD,98)
font_section=ImageFont.truetype(BOLD,69)
font_label=ImageFont.truetype(BOLD,47)
font_caption=ImageFont.truetype(FONT,37)
font_small=ImageFont.truetype(FONT,26)

# Globe environment: deep teal nebula, sparse restrained starlight and
# separate cyan atmospheric halo. Deterministic artwork, not a stock photo.
rng=np.random.default_rng(1719)
yy,xx=np.mgrid[:H,:W]
rad=np.sqrt(((xx-W*.53)/(W*.87))**2+((yy-H*.46)/(H*.73))**2)
b=np.clip(1-rad,0,1)
BACK=np.stack((3+10*b,11+29*b,21+42*b),axis=2).astype(np.uint8)
space=Image.fromarray(BACK,'RGB').convert('RGBA')
d=ImageDraw.Draw(space,'RGBA')
for i in range(175):
    x=int(rng.uniform(35,W-35));y=int(rng.uniform(60,H-170))
    radius=1 if i%7 else 2
    d.ellipse((x-radius,y-radius,x+radius,y+radius),fill=(188,226,238,int(rng.uniform(45,130))))
SPACE=space


def globe(center_lon,t):
    # Latitude center +12 degrees so Florida is north of the center-line.
    lat_view=np.clip(lat+np.deg2rad(12),-np.pi/2,np.pi/2)
    lon=np.deg2rad(center_lon)+dlon
    mx=np.mod((lon/np.pi+1)*1024,2048).astype(np.float32)
    my=((.5-lat_view/np.pi)*1023).astype(np.float32)
    day=cv2.remap(DAY,mx,my,cv2.INTER_LINEAR,cv2.BORDER_WRAP).astype(np.float32)
    night=cv2.remap(NIGHT,mx,my,cv2.INTER_LINEAR,cv2.BORDER_WRAP).astype(np.float32)
    mx_cloud=np.mod(mx+4.5*t,2048).astype(np.float32)
    cloud=cv2.remap(CLOUD,mx_cloud,my,cv2.INTER_LINEAR,cv2.BORDER_WRAP).astype(np.float32)
    # City-light detail on the dark hemisphere; cloud opacity from independent
    # NASA cloud texture. No assertion these clouds match current conditions.
    light=shade[:,:,None]
    day*=light
    lights=np.maximum(0,.35-shade)[:,:,None]*(night[:,:,None]/255)*np.array([80,119,172])[None,None,:]
    day+=lights
    cloudmask=np.clip((cloud-45)/205,0,.68)[:,:,None]*(.23+.29*nz[:,:,None])
    day=day*(1-cloudmask)+np.array([219,234,237])[None,None,:]*cloudmask
    # Atmospheric limb is a separate layer beyond the surface sphere.
    img=Image.fromarray(np.uint8(np.clip(day,0,255)),'RGB').convert('RGBA')
    img.putalpha(Image.fromarray(alpha))
    canvas=SPACE.copy()
    ox=round((W-RES)/2);oy=round(426-48*min(1,t/5))
    atm=Image.new('RGBA',(RES+120,RES+120))
    ad=ImageDraw.Draw(atm,'RGBA')
    ad.ellipse((36,36,RES+83,RES+83),fill=(10,148,216,118))
    atm=atm.filter(ImageFilter.GaussianBlur(38))
    canvas.alpha_composite(atm,(ox-60,oy-60))
    canvas.alpha_composite(img,(ox,oy))
    rim=Image.new('RGBA',(RES,RES))
    rimarr=np.clip((rho-.89)/.11,0,1)*(rho<1)
    rimarr=np.uint8(rimarr**1.2*125)
    rim.paste((70,205,248), (0,0,RES,RES))
    rim.putalpha(Image.fromarray(rimarr))
    canvas.alpha_composite(rim,(ox,oy))
    return canvas


def ease(v):
    v=np.clip(v,0,1)
    return float(v*v*(3-2*v))

def textbox(canvas,text,y,kind='caption'):
    d=ImageDraw.Draw(canvas,'RGBA')
    f=font_caption if kind=='caption' else font_title if kind=='title' else font_section
    box=d.textbbox((0,0),text,font=f,stroke_width=1);width=box[2]-box[0]
    x=round((W-width)/2)-box[0]
    d.text((x+3,y+4),text,font=f,fill=(0,11,19,155),stroke_width=3,stroke_fill=(0,11,19,160))
    d.text((x,y),text,font=f,fill=(242,250,249,255),stroke_width=1,stroke_fill=(7,41,55,185))


def loc_label(canvas,label,x,y,color=(247,250,250),size=54):
    f=ImageFont.truetype(BOLD,size)
    mask=Image.new('L',(W,H))
    ImageDraw.Draw(mask).text((x,y),label,font=f,fill=255)
    glow=Image.new('RGBA',(W,H),(*color,0))
    glow.putalpha(mask.filter(ImageFilter.GaussianBlur(14)).point(lambda a:round(a*.8)))
    canvas.alpha_composite(glow)
    ImageDraw.Draw(canvas,'RGBA').text((x,y),label,font=f,fill=(*color,255),
                                     stroke_width=2,stroke_fill=(5,39,48,240))

# Second original relief plate: closer visual scale of the Keys, with a fresh
# vector trace. It is an illustrative match cut rather than a satellite zoom.
MACRO=Image.open(HERE/'assets/florida_keys_macro_relief.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
MACRO_KNOTS=[(860,670),(803,820),(735,918),(670,1040),(555,1115),
             (480,1180),(367,1252),(250,1323)]
MACRO_CURVE=style.smooth_curve(MACRO_KNOTS)

def macro_path(progress):
    pts=MACRO_CURVE[:max(2,round(len(MACRO_CURVE)*progress))]
    # Each dot lies over the painted island chain; optical glow remains
    # spatially attached as in the geography references.
    mask=Image.new('L',(W,H))
    ImageDraw.Draw(mask).line(pts,fill=255,width=12,joint='curve')
    blur=mask.filter(ImageFilter.GaussianBlur(20))
    gl=Image.new('RGBA',(W,H),(14,210,249,0))
    gl.putalpha(blur.point(lambda a:round(a*.87)))
    ln=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(ln,'RGBA')
    d.line(pts,fill=(67,234,254,240),width=9,joint='curve')
    d.line(pts,fill=(233,255,255,255),width=3,joint='curve')
    return Image.alpha_composite(gl,ln)
MACRO_ROUTE=[macro_path(max(.01,i/16)) for i in range(17)]

def macro_frame(t):
    progress=ease((t-24.2)/3.3)
    im=Image.alpha_composite(MACRO,MACRO_ROUTE[round(progress*16)])
    loc_label(im,'FLORIDA KEYS',112,373,(230,252,250),69)
    if t>=26.4:
        label=Image.new('RGBA',(W,H))
        loc_label(label,'KEY WEST',122,1360,(239,252,250),46)
        label.putalpha(label.getchannel('A').point(lambda a:round(a*ease((t-26.4)/.45))))
        im=Image.alpha_composite(im,label)
    z=1.02+.10*ease((t-23.5)/6.2)
    cw,ch=W/z,H/z;cx=float(np.clip(540-75*ease((t-23.5)/6.2),cw/2,W-cw/2))
    cy=float(np.clip(960+55*ease((t-23.5)/6.2),ch/2,H-ch/2))
    return im.transform((W,H),Image.Transform.EXTENT,
                        (cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)

# Geography backplate cloud shadow and fine film light: transformed separately
# from underlying land with slight parallax. Pre-render at 1:1 then shift.
raw=np.asarray(Image.open(NASA/'earth-clouds-2048.jpg').convert('L'))
patch=raw[260:690,70:620]
patch=cv2.resize(patch,(W,H),interpolation=cv2.INTER_LINEAR)
patch=cv2.GaussianBlur(patch,(0,0),17)
# Very light on top: relief remains the hero, no false weather report.
cloud_alpha=np.uint8(np.clip((patch.astype(np.float32)-105)*.22,0,45))
CLOUD_MAP=Image.new('RGBA',(W,H),(239,247,248,0))
CLOUD_MAP.putalpha(Image.fromarray(cloud_alpha))

# Reusable precomposed maps; overlaid photo texture is always original.
MAP_BASE=BASE.convert('RGBA')
MAP_REGION=Image.alpha_composite(MAP_BASE,REGION)


def map_layer(t,mode):
    if mode==0:im=MAP_BASE.copy()
    elif mode==1:im=MAP_REGION.copy()
    else:
        frac=ease((t-14.2)/6.4)
        idx=min(18,max(0,round(frac*18)))
        im=Image.alpha_composite(MAP_REGION,ROUTE_LAYERS[idx])
        if t>=20:im=style.overlay_pin(im)
    if mode>0:
        # Cloud light at map scale, 6px travel over 30 s, never a static white veil.
        shifted=CLOUD_MAP.transform((W,H),Image.Transform.AFFINE,(1,0,4*math.sin(t/8),0,1,6*math.cos(t/9)),Image.Resampling.BILINEAR)
        im=Image.alpha_composite(im,shifted)
    im=Image.alpha_composite(im,LABELS if t<22 else CLOSE_LABELS)
    if 26<=t<29:
        loc_label(im,'ATLANTIC',815,668,(134,242,253),36)
    return im


def map_camera(im,t):
    # Matching geographical focus; bounded EXTENT transform, no exposed borders.
    if t<10:zoom=1.02+.04*ease((t-5.2)/4.8);cx=540;cy=960
    elif t<22:zoom=1.06+.10*ease((t-10)/12);cx=540+58*ease((t-10)/12);cy=960-80*ease((t-10)/12)
    elif t<29:zoom=1.16+.18*ease((t-22)/7);cx=598+95*ease((t-22)/7);cy=880-70*ease((t-22)/7)
    else:zoom=1.34-.26*ease((t-29)/7);cx=693-111*ease((t-29)/7);cy=810+120*ease((t-29)/7)
    cw,ch=W/zoom,H/zoom
    cx=float(np.clip(cx,cw/2,W-cw/2));cy=float(np.clip(cy,ch/2,H-ch/2))
    return im.transform((W,H),Image.Transform.EXTENT,
                        (cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)

SCRIPT=[
    (0,4.9,'A coastline, seen from orbit.'),
    (4.9,9.5,'Then a peninsula comes into view.'),
    (9.5,14.5,'Florida points south between two waters.'),
    (14.5,19.5,'The Gulf lies to the west.'),
    (19.5,24.5,'The Atlantic opens to the east.'),
    (24.5,30,'Beyond the tip: an island chain.'),
    (30,36,'Follow the Keys toward Key West.')]

def subtitle(canvas,t):
    for a,b,text in SCRIPT:
        if a<=t<b:
            e=min(ease((t-a)/.32),ease((b-t)/.24))
            if e>.01:
                lay=Image.new('RGBA',(W,H))
                textbox(lay,text,1508,'caption')
                lay.putalpha(lay.getchannel('A').point(lambda v:round(v*e)))
                canvas=Image.alpha_composite(canvas,lay)
            break
    return canvas


def frame(t):
    if t<5.4:
        lon=-9-67*ease(t/5.2)
        can=globe(lon,t)
        if t>=3.0:
            # Globe location pin maps to ~82W/25N at the final orientation.
            opacity=ease((t-3)/1.3)
            marker=Image.new('RGBA',(W,H))
            d=ImageDraw.Draw(marker,'RGBA')
            phi=math.radians(25.0-12.0)
            delta=math.radians(-82.0-lon)
            disk_radius=RES/2-7
            px=round((W-RES)/2+RES/2+disk_radius*math.cos(phi)*math.sin(delta))
            py=round(426-48*min(1,t/5)+RES/2-disk_radius*math.sin(phi))
            for rad,alpha in ((70,round(26*opacity)),(34,round(70*opacity)),(10,round(220*opacity))):
                d.ellipse((px-rad,py-rad,px+rad,py+rad),fill=(23,220,247,alpha))
            can=Image.alpha_composite(can,marker)
            loc_label(can,'FLORIDA',px+42,py-37,(225,251,249),53)
        if t<1.7:textbox(can,'EARTH',146,'title')
        elif t<5.2:textbox(can,'THE GULF COAST',150,'section')
        if t>=4.9:
            # Globe-to-map optical match dissolve; basemap appears beneath UV sphere.
            country=map_camera(map_layer(t,0),t)
            can=Image.blend(can,country,ease((t-4.9)/.50))
    else:
        mode=0 if t<9.5 else 1 if t<14.4 else 2
        can=map_camera(map_layer(t,mode),t)
        if 9.5<=t<10.3:
            prior=map_camera(map_layer(t,0),t)
            can=Image.blend(prior,can,ease((t-9.5)/.8))
        if 23.5<=t<30:
            macro=macro_frame(t)
            if t<24.1:can=Image.blend(can,macro,ease((t-23.5)/.6))
            elif t>=29.35:can=Image.blend(macro,can,ease((t-29.35)/.65))
            else:can=macro
        if 30<=t<35.4:
            lay=Image.new('RGBA',(W,H))
            loc_label(lay,'GULF OF MEXICO',75,785,(233,246,246),40)
            loc_label(lay,'ATLANTIC OCEAN',720,832,(142,237,246),36)
            lay.putalpha(lay.getchannel('A').point(lambda a:round(a*ease((t-30)/.9))))
            can=Image.alpha_composite(can,lay)
        if t>=34.2:
            lay=Image.new('RGBA',(W,H))
            textbox(lay,'THE FLORIDA KEYS',176,'section')
            lay.putalpha(lay.getchannel('A').point(lambda a:round(a*ease((t-34.2)/.6))))
            can=Image.alpha_composite(can,lay)
    can=subtitle(can,t)
    return can.convert('RGB')


def read_sound(name):
    pcm=subprocess.check_output([FF,'-v','error','-i',str(SOUND/name),'-ac','1','-ar','48000','-f','f32le','pipe:1'])
    a=np.frombuffer(pcm,dtype='<f4').copy();a-=a.mean()
    return a

def loop(a,n,fade=.35):
    k=int(fade*48000);out=np.zeros(n,np.float32);pos=0
    while pos<n:
        end=min(n,pos+len(a));size=end-pos
        if pos and size>k:
            ramp=np.linspace(0,1,k,dtype=np.float32)
            out[pos:pos+k]=out[pos:pos+k]*(1-ramp)+a[:k]*ramp
            out[pos+k:end]=a[k:size]
        else:out[pos:end]=a[:size]
        pos=end-k if end<n else n
    return out

def soundtrack():
    sr=48000;n=sr*DUR
    rain=loop(read_sound('rain-light.ogg'),n)
    wind=loop(read_sound('wind.ogg'),n)
    t=np.arange(n,dtype=np.float32)/sr
    # Recorded natural ambience only: no instrumental music, no fabricated VO.
    env=np.minimum(1,t/.7)*np.minimum(1,(DUR-t)/.65)
    bed=(.029*rain+.040*wind)*env
    # The map close-up becomes a little warmer, never masking silent captions.
    bed*=.9+.32*np.exp(-((t-22)/7)**2)
    bed*=18.0  # text-led ambient film mix, approximately -28 LUFS.
    stereo=np.column_stack((bed*.89,bed)).astype(np.float32)
    path=CACHE/'geography_natural_ambience_48k.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(sr)
        f.writeframes((np.clip(stereo,-.99,.99)*32767).astype('<i2').tobytes())
    return path


def render():
    aud=soundtrack()
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r',str(FPS),'-i','pipe:0','-i',str(aud),
         '-map','0:v','-map','1:a','-c:v','libx264','-threads','2','-preset','medium',
         '-crf','18','-maxrate','9M','-bufsize','18M','-profile:v','high','-level:v','4.2',
         '-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-ar','48000',
         '-movflags','+faststart','-shortest',str(OUT)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(DUR*FPS):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*4)==0:print('frame',k,'/',DUR*FPS,flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('Encode failed')
    finally:
        if p.poll() is None:p.kill()
    print('FULL STUDY',OUT,OUT.stat().st_size,flush=True)

if __name__=='__main__':render()

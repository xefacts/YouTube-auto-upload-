#!/usr/bin/env python3
"""Original geography-motion style study from Train 2 references.
No Train 2 frames or audio are composited into output; backplate is an
AI-illustrated map, NOT a GIS-verified locator. Neon assets are new vectors.
"""
from pathlib import Path
import math,subprocess
import numpy as np
import cv2
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageFilter
ROOT=Path(__file__).resolve().parent
A=ROOT/'assets'; O=ROOT/'png'; O.mkdir(exist_ok=True)
BACK=A/'florida_gulf_relief_backplate.png'
W,H=1080,1920
SCALE=2
SIZE=(W*SCALE,H*SCALE)
FONT_BOLD=str(ROOT.parent/'assets/fonts/Anton-Regular.ttf')
FONT_SANS=str(ROOT.parent/'assets/fonts/DMSans.ttf')
R=Image.Resampling.LANCZOS

def make_base():
    im=Image.open(BACK).convert('RGB').resize((W,H),R)
    im=ImageEnhance.Contrast(im).enhance(1.055)
    im=ImageEnhance.Color(im).enhance(1.12)
    im=im.filter(ImageFilter.UnsharpMask(radius=1.4,percent=62,threshold=4))
    return im
BASE=make_base()

def hres():return Image.new('RGBA',SIZE)
def lo(im):return im.resize((W,H),R)
def xy(points):return [(int(x*SCALE),int(y*SCALE)) for x,y in points]
def blend(base,layer):return Image.alpha_composite(base.convert('RGBA'),layer.convert('RGBA'))

# A broadly illustrative peninsula mask aligned to the generated relief plate;
# not a surveyed boundary. Preserve internal terrain through a pale luminous tint.
FL=[(595,462),(630,453),(663,486),(690,528),(699,570),(710,608),
    (715,650),(737,697),(751,740),(764,782),(775,815),(772,857),
    (759,895),(736,910),(708,896),(685,862),(664,833),(645,797),
    (633,759),(616,732),(601,692),(592,661),(595,632),(592,604),
    (580,562),(570,529),(572,498)]

def region_layer():
    mask=Image.new('L',SIZE)
    d=ImageDraw.Draw(mask);d.polygon(xy(FL),fill=255)
    # Include green-lit terrain rather than opaque flat green.
    tint=hres();tint.paste((62,224,119,59),(0,0,*SIZE),mask=mask)
    edge=hres();e=ImageDraw.Draw(edge,'RGBA')
    for thick,alpha in ((30,52),(14,112),(6,210)):
        e.line(xy(FL+[FL[0]]),fill=(119,252,141,alpha),width=thick*SCALE,joint='curve')
    haze=edge.filter(ImageFilter.GaussianBlur(27*SCALE))
    haze.putalpha(haze.getchannel('A').point(lambda p:round(p*.85)))
    im=Image.alpha_composite(haze,tint)
    im=Image.alpha_composite(im,edge)
    return lo(im)
REGION=region_layer()

# Cubic Catmull-Rom spline follows the illustrative Florida peninsula. Distinct
# path coordinates are editor-created, not copied from any reference animation.
ROUTE_KNOTS=[(615,491),(644,515),(672,552),(692,591),(706,644),
             (730,692),(748,745),(760,795),(761,834),(750,873),(689,919),(647,929)]

def smooth_curve(pts,steps=18):
    p=[pts[0]]+pts+[pts[-1]];out=[]
    for i in range(1,len(p)-2):
        a,b,c,d=p[i-1:i+3]
        for j in range(steps):
            t=j/steps;t2=t*t;t3=t2*t
            x=.5*((2*b[0])+(-a[0]+c[0])*t+(2*a[0]-5*b[0]+4*c[0]-d[0])*t2+(-a[0]+3*b[0]-3*c[0]+d[0])*t3)
            y=.5*((2*b[1])+(-a[1]+c[1])*t+(2*a[1]-5*b[1]+4*c[1]-d[1])*t2+(-a[1]+3*b[1]-3*c[1]+d[1])*t3)
            out.append((x,y))
    out.append(pts[-1]);return out
CURVE=smooth_curve(ROUTE_KNOTS)

def route_layer(progress=1):
    k=max(2,min(len(CURVE),round(len(CURVE)*progress)))
    pts=xy(CURVE[:k]);bright=hres()
    dr=ImageDraw.Draw(bright,'RGBA')
    # Reference-like optical bloom: broad low-opacity field, color edge, white core.
    dr.line(pts,fill=(10,202,247,255),width=25*SCALE,joint='curve')
    glow=bright.filter(ImageFilter.GaussianBlur(26*SCALE))
    glow.putalpha(glow.getchannel('A').point(lambda p:round(p*.70)))
    mid=hres();d=ImageDraw.Draw(mid,'RGBA')
    d.line(pts,fill=(4,190,244,215),width=12*SCALE,joint='curve')
    d.line(pts,fill=(170,251,252,250),width=5*SCALE,joint='curve')
    out=Image.alpha_composite(glow,mid)
    # One spatially attached endpoint flare, not a decorative unrelated lens flare.
    x,y=pts[-1]
    spot=hres();sd=ImageDraw.Draw(spot,'RGBA')
    for radius,alpha in ((25,30),(15,110),(8,235)):
        sd.ellipse((x-radius*SCALE,y-radius*SCALE,x+radius*SCALE,y+radius*SCALE),
                   fill=(204,255,255,alpha))
    out=Image.alpha_composite(out,spot.filter(ImageFilter.GaussianBlur(2*SCALE)))
    return lo(out)
ROUTE=route_layer()

def magenta_trace_layer():
    """Optional neon dashed *graphic trace*, never a verified border."""
    coords=smooth_curve([(842,523),(838,631),(824,733),(803,836),(784,911)])
    mask=Image.new('L',SIZE)
    m=ImageDraw.Draw(mask)
    for k in range(0,len(coords)-9,10):
        m.line(xy(coords[k:k+8]),fill=255,width=17*SCALE,joint='curve')
    haze=Image.new('RGBA',SIZE,(255,53,147,0))
    haze.putalpha(mask.filter(ImageFilter.GaussianBlur(29*SCALE)).point(
        lambda a:min(193,round(a*1.63))))
    tight=Image.new('RGBA',SIZE,(255,94,163,0))
    tight.putalpha(mask.filter(ImageFilter.GaussianBlur(10*SCALE)).point(
        lambda a:min(211,round(a*1.4))))
    core=hres();d=ImageDraw.Draw(core,'RGBA')
    for k in range(0,len(coords)-9,10):
        d.line(xy(coords[k:k+8]),fill=(255,239,246,255),width=8*SCALE,joint='curve')
    return lo(Image.alpha_composite(Image.alpha_composite(haze,tight),core))

PINK=magenta_trace_layer()

# Isolated reusable transparent cyan marker at the route's southern endpoint.
def pin_layer():
    a=Image.new('RGBA',(400,400))
    d=ImageDraw.Draw(a,'RGBA');cx=cy=200
    for rad,alpha in ((143,24),(112,40),(80,98),(48,210)):
        d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),fill=(13,195,247,alpha))
    a=a.filter(ImageFilter.GaussianBlur(26))
    d=ImageDraw.Draw(a,'RGBA')
    for rad,width,color in ((71,5,(87,239,255,100)),(45,7,(83,238,253,225))):
        d.arc((cx-rad,cy-rad,cx+rad,cy+rad),0,360,fill=color,width=width)
    d.ellipse((cx-13,cy-13,cx+13,cy+13),fill=(243,255,255,255))
    d.line((cx,cy-72,cx,cy-103),fill=(99,242,252,175),width=3)
    d.line((cx,cy+72,cx,cy+103),fill=(99,242,252,175),width=3)
    d.line((cx-72,cy,cx-103,cy),fill=(99,242,252,175),width=3)
    d.line((cx+72,cy,cx+103,cy),fill=(99,242,252,175),width=3)
    return a
PIN=pin_layer()

def overlay_pin(image,x=647,y=929,scale=.67):
    size=round(PIN.width*scale);pin=PIN.resize((size,size),R)
    img=image.convert('RGBA');img.alpha_composite(pin,(round(x-size/2),round(y-size/2)))
    return img

def glow_text(canvas,text,x,y,size=42,color=(228,250,250),bold=True):
    font=ImageFont.truetype(FONT_BOLD if bold else FONT_SANS,size)
    mask=Image.new('L',(W,H));md=ImageDraw.Draw(mask)
    md.text((x,y),text,font=font,fill=235,stroke_width=1)
    glow=Image.new('RGBA',(W,H),(35,217,248,0))
    blur=mask.filter(ImageFilter.GaussianBlur(11))
    glow.putalpha(blur.point(lambda q:round(q*.69)))
    canvas.alpha_composite(glow)
    d=ImageDraw.Draw(canvas,'RGBA')
    d.text((x,y),text,font=font,fill=(*color,255),stroke_width=1,stroke_fill=(7,39,54,235))

def labels_layer():
    im=Image.new('RGBA',(W,H));d=ImageDraw.Draw(im,'RGBA')
    # Labels match the *illustrative* map's approximate locations, not a GIS pin.
    glow_text(im,'FLORIDA',532,443,56)
    glow_text(im,'GULF OF MEXICO',77,734,39,(200,230,231))
    glow_text(im,'CUBA',455,1105,47,(226,241,232))
    glow_text(im,'BAHAMAS',844,923,33,(222,248,249))
    glow_text(im,'KEY WEST',554,958,35,(238,252,251))
    return im
LABELS=labels_layer()

def footer(im,caption):
    canvas=im.convert('RGBA');d=ImageDraw.Draw(canvas,'RGBA')
    f=ImageFont.truetype(FONT_SANS,34)
    bb=d.textbbox((0,0),caption,font=f)
    d.text(((W-(bb[2]-bb[0]))//2,1630),caption,font=f,
           fill=(248,252,251,255),stroke_width=3,stroke_fill=(0,29,38,245))
    return canvas

def corner_tag(im,stage):
    canvas=im.convert('RGBA');d=ImageDraw.Draw(canvas,'RGBA')
    d.rounded_rectangle((48,70,657,146),radius=12,fill=(3,27,37,176),
                        outline=(120,204,210,92),width=2)
    d.text((71,84),'GULF COAST  /  STYLE STUDY',font=ImageFont.truetype(FONT_SANS,28),fill=(245,252,251,255))
    d.text((56,149),f'0{stage} / 04',font=ImageFont.truetype(FONT_SANS,22),fill=(216,236,233,225))
    return canvas

def frame(t):
    if t<1.2:
        a=BASE.convert('RGBA')
        a=Image.alpha_composite(a,LABELS)
        a=footer(a,'The Gulf Coast')
    elif t<2.4:
        a=blend(BASE,REGION)
        a=Image.alpha_composite(a,LABELS)
        a=footer(a,'a peninsula in focus')
    else:
        route=route_layer(min(1,max(.03,(t-2.38)/1.7)))
        a=blend(BASE,REGION)
        a=Image.alpha_composite(a,route)
        if t>3.6:a=overlay_pin(a)
        a=Image.alpha_composite(a,LABELS)
        a=footer(a,'then follow the coast')
    stage=1 if t<1.2 else 2 if t<2.4 else 3 if t<4.2 else 4
    # Motivated slow camera push; no background tile or jump cuts.
    z=1+.038*min(1,t/6)
    w,h=W/z,H/z;cx=min(W-w/2,max(w/2,540+(t/6)*45));cy=960
    a=a.transform((W,H),Image.Transform.EXTENT,
                  (cx-w/2,cy-h/2,cx+w/2,cy+h/2),Image.Resampling.BICUBIC)
    return a.convert('RGB')

def build():
    BASE.save(O/'00_atlas_backplate.png',optimize=True)
    REGION.save(O/'element_florida_region_glow_RGBA.png',optimize=True)
    ROUTE.save(O/'element_cyan_route_glow_RGBA.png',optimize=True)
    PIN.save(O/'element_beacon_pin_RGBA.png',optimize=True)
    PINK.save(O/'element_magenta_dashed_trace_RGBA.png',optimize=True)
    LABELS.save(O/'element_atlas_labels_RGBA.png',optimize=True)
    for i,t in enumerate((.6,1.8,3.2,5.4),1):
        frame(t).save(O/f'{i:02d}_geography_frame.png',optimize=True)
    print('PNG frames and layers saved to',O)
    ff=subprocess.run(['which','ffmpeg'],capture_output=True,text=True)
    if ff.returncode:
        from imageio_ffmpeg import get_ffmpeg_exe
        exe=get_ffmpeg_exe()
    else:exe=ff.stdout.strip()
    cmd=[exe,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s','1080x1920','-r','24','-i','pipe:0','-c:v','libx264',
         '-threads','2','-preset','fast','-crf','22','-pix_fmt','yuv420p',
         '-movflags','+faststart',str(ROOT/'GEOGRAPHY_STYLE_MOTION_PREVIEW_1080x1920.mp4')]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(144):p.stdin.write(frame(k/24).tobytes())
        p.stdin.close()
        if p.wait():raise RuntimeError('Encoding failed')
    finally:
        if p.poll() is None:p.kill()
    print('Preview video saved')
if __name__=='__main__':build()

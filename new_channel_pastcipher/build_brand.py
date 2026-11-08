#!/usr/bin/env python3
"""Build PastCipher brand art. This never calls YouTube or modifies a channel.

The square avatar and banner typography/mark are original vector-style drawing.
The 8K banner is an 8K canvas using an UPSCALED generated photographic
backplate; it is NOT a claim of native 8K photographic source detail.
"""
from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
ASSET=ROOT/'assets'
ASSET.mkdir(parents=True,exist_ok=True)
BG=ASSET/'banner_background.png'
FONT_HEAD=Path(__file__).resolve().parents[1]/'past_detour_emu_1932/final_image_edit/fonts/Anton-Regular.ttf'
FONT_BODY=Path(__file__).resolve().parents[1]/'past_detour_emu_1932/final_image_edit/fonts/DMSans.ttf'
IVORY=(241,238,220)
LIME=(207,239,113)
DEEP=(8,22,24)
BRONZE=(174,139,98)


def font(path,n):return ImageFont.truetype(str(path),n)


def draw_mark(d:ImageDraw.ImageDraw,cx:float,cy:float,s:float):
    """Open file tab + cipher keyhole, enclosed in an interrupted seal."""
    def xy(x,y):return (round(cx+x*s),round(cy+y*s))
    w=max(3,round(.035*s))
    r=.43*s
    bbox=(round(cx-r),round(cy-r),round(cx+r),round(cy+r))
    d.arc(bbox,24,277,fill=(*LIME,255),width=max(2,round(.018*s)))
    d.arc(bbox,294,336,fill=(*BRONZE,255),width=max(2,round(.014*s)))
    # Precisely drawn file-tab contour; transparent interior remains legible.
    pts=[xy(-.31,-.22),xy(-.12,-.22),xy(-.062,-.295),xy(.28,-.295),
         xy(.34,-.215),xy(.34,.275),xy(-.31,.275)]
    d.line(pts+[pts[0]],fill=(*IVORY,255),width=w,joint='curve')
    d.line((xy(-.25,-.135),xy(.265,-.135)),fill=(*IVORY,255),width=max(2,round(.019*s)))
    # Geometric keyhole: at small avatar sizes it remains a single bold signal.
    rr=.067*s
    d.ellipse((round(cx-rr),round(cy-.005*s-rr),round(cx+rr),round(cy-.005*s+rr)),fill=(*LIME,255))
    d.rounded_rectangle((round(cx-.030*s),round(cy+.045*s),
                         round(cx+.030*s),round(cy+.160*s)),
                        radius=round(.009*s),fill=(*LIME,255))
    # Tiny document-corner accent.
    d.polygon([xy(.20,-.295),xy(.28,-.295),xy(.34,-.215),xy(.27,-.215)],fill=(*LIME,255))


def gradient_avatar(n:int)->Image.Image:
    yy,xx=np.mgrid[0:n,0:n]
    dist=np.sqrt(((xx-n/2)/(n/2))**2+((yy-n/2)/(n/2))**2)
    ramp=np.clip(1-dist*.74,0,1)
    arr=np.zeros((n,n,3),dtype=np.uint8)
    for k,(outer,inner) in enumerate(((5,15),(16,38),(18,37))):
        arr[:,:,k]=np.clip(outer+(inner-outer)*ramp,0,255).astype(np.uint8)
    return Image.fromarray(arr,'RGB').convert('RGBA')


def make_profile():
    n=2048
    img=gradient_avatar(n)
    d=ImageDraw.Draw(img)
    draw_mark(d,n/2,n/2,n*.74)
    # Slight pinstripe circle is decorative and stays inside YouTube's round crop.
    img.convert('RGB').save(ROOT/'profile_2048.png',optimize=True)
    img.resize((800,800),Image.Resampling.LANCZOS).convert('RGB').save(
        ROOT/'profile_upload_800.png',optimize=True)
    tiny=img.resize((98,98),Image.Resampling.LANCZOS)
    mask=Image.new('L',(98,98),0)
    ImageDraw.Draw(mask).ellipse((0,0,97,97),fill=255)
    tiny.putalpha(mask)
    tiny.save(ROOT/'preview_profile_circle_98.png',optimize=True)


def dark_backplate()->Image.Image:
    """Generated archival atmosphere + legible center vignette at 2560px."""
    b=ImageOps.fit(Image.open(BG).convert('RGB'),(2560,1440),method=Image.Resampling.LANCZOS)
    arr=np.asarray(b).astype(np.float32)
    yy=np.arange(1440,dtype=np.float32)[:,None]
    xx=np.arange(2560,dtype=np.float32)[None,:]
    centered=np.exp(-(((xx-1280)/790)**4+((yy-720)/520)**4))
    shade=(.17+.68*centered)[...,None]
    dark=np.array(DEEP,dtype=np.float32)
    arr=np.clip(arr*(1-shade)+dark*shade,0,255).astype(np.uint8)
    return Image.fromarray(arr,'RGB')


def tracked(draw,text,origin,face,fill,spacing):
    x,y=origin
    for ch in text:
        draw.text((round(x),round(y)),ch,font=face,fill=fill)
        x+=draw.textlength(ch,font=face)+spacing
    return x


def draw_banner(base:Image.Image,scale:int)->Image.Image:
    w,h=base.size
    assert (w,h)==(2560*scale,1440*scale)
    im=base.convert('RGBA');d=ImageDraw.Draw(im)
    sx=lambda v:round(v*scale)
    # Outer ambience: precision drafting marks instead of extra logos/text.
    for x in (460,2100):
        d.arc((sx(x-138),sx(720-138),sx(x+138),sx(720+138)),
              35,295,fill=(165,186,142,83),width=sx(2))
        d.line((sx(x-180),sx(720),sx(x-127),sx(720)),fill=(165,186,142,75),width=sx(2))
    # A single restrained rule in the central mobile-safe band.
    d.line((sx(536),sx(547),sx(2024),sx(547)),fill=(*LIME,155),width=sx(3))
    d.line((sx(536),sx(894),sx(2024),sx(894)),fill=(*BRONZE,120),width=sx(2))
    draw_mark(d,sx(723),sx(724),sx(336))
    head=font(FONT_HEAD,sx(193))
    body=font(FONT_BODY,sx(42))
    eyebrow=font(FONT_BODY,sx(31))
    # Name + tagline fit INSIDE [510,2050]×[510,930] at 2560 resolution.
    d.text((sx(915),sx(562)),'PAST',font=head,fill=(*IVORY,255))
    first=d.textbbox((sx(915),sx(562)),'PAST',font=head)
    # Tight controlled kerning; bolder lime second half becomes the signature.
    d.text((first[2]+sx(14),sx(562)),'CIPHER',font=head,fill=(*LIME,255))
    d.text((sx(922),sx(786)),'HISTORY, DECODED.',font=body,fill=(*IVORY,242))
    d.line((sx(922),sx(863),sx(1160),sx(863)),fill=(*LIME,220),width=sx(7))
    tracked(d,'HEISTS  •  ESPIONAGE  •  MYSTERIES',
            (sx(1200),sx(841)),eyebrow,(*IVORY,175),sx(3))
    return im.convert('RGB')


def make_banner():
    master_bg=dark_backplate()
    upload=draw_banner(master_bg,1)
    # Export one upload-compliant original artwork. JPEG has no frame effect.
    upload.save(ROOT/'banner_upload_2560x1440.jpg',quality=94,optimize=True,
                subsampling=0,progressive=True)
    # Render all typography and vector art anew at 8K, not just upsample type.
    big_bg=master_bg.resize((7680,4320),Image.Resampling.LANCZOS)
    eight=draw_banner(big_bg,3)
    eight.save(ROOT/'banner_8k_7680x4320_upscaled_backplate.jpg',
               quality=91,optimize=True,subsampling=0,progressive=True)
    del eight,big_bg,master_bg
    # Preview ONLY; guides are never printed on the actual banner.
    preview=Image.open(ROOT/'banner_upload_2560x1440.jpg').convert('RGB')
    safe=(510,510,2050,930)  # conservative 1540 × 420 content-safe rectangle
    preview.crop(safe).save(ROOT/'preview_mobile_safe.jpg',quality=95)
    preview.crop((0,510,2560,930)).save(ROOT/'preview_desktop.jpg',quality=93)
    preview.resize((1280,720),Image.Resampling.LANCZOS).save(ROOT/'preview_tv.jpg',quality=93)
    for p in (ROOT/'banner_upload_2560x1440.jpg',
              ROOT/'banner_8k_7680x4320_upscaled_backplate.jpg'):
        print(f'{p.name}: {p.stat().st_size:,} bytes')
    assert (ROOT/'banner_upload_2560x1440.jpg').stat().st_size<=6*1024*1024


def main():
    make_profile();make_banner()

if __name__=='__main__':main()

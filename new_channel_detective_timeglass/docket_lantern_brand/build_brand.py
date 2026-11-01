#!/usr/bin/env python3
"""YouTube-safe brand outputs for The Docket Lantern, without touching a live channel."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageEnhance

R=Path(__file__).resolve().parent
F=R.parent/'assets'/'fonts'
ANTON=F/'Anton-Regular.ttf'; DM=F/'DMSans.ttf'
INK=(8,30,33); IVORY=(249,243,224); COPPER=(210,152,96); MINT=(173,203,190)

def ft(file,size):return ImageFont.truetype(str(file),size)
def text_xy(draw,text,font_,xy,fill):draw.text(xy,text,font=font_,fill=fill,stroke_width=0)

def profile():
    src=Image.open(R/'art/profile_portrait.png').convert('RGB')
    master=ImageOps.fit(src,(2048,2048),Image.Resampling.LANCZOS)
    # Minimal trim: unaltered character face, precise matching copper edge inside circular crop.
    d=ImageDraw.Draw(master)
    d.ellipse((62,62,1985,1985),outline=(55,87,86),width=17)
    d.ellipse((82,82,1964,1964),outline=COPPER,width=8)
    p=R/'PROFILE_MASTER_2048.png';master.save(p,optimize=True)
    upload=master.resize((800,800),Image.Resampling.LANCZOS)
    p=R/'PROFILE_UPLOAD_800x800.png';upload.save(p,optimize=True)
    # Actual tiny circular platform use — readability QC.
    small=upload.resize((98,98),Image.Resampling.LANCZOS)
    mask=Image.new('L',(98,98),0);ImageDraw.Draw(mask).ellipse((0,0,97,97),fill=255)
    small.putalpha(mask)
    small.save(R/'PROFILE_CIRCLE_98px_PREVIEW.png')
    return master,upload

def banner():
    src=Image.open(R/'art/banner_backplate.png').convert('RGB')
    base=ImageOps.fit(src,(2560,1440),Image.Resampling.LANCZOS,centering=(.50,.5))
    # Softer ambient illumination under type, all essential design inside centered mobile-safe rectangle.
    overlay=Image.new('RGBA',(2560,1440),(0,0,0,0)); od=ImageDraw.Draw(overlay)
    od.rounded_rectangle((533,527,2027,917),radius=7,fill=(7,31,35,103))
    base=Image.alpha_composite(base.convert('RGBA'),overlay).convert('RGB')
    d=ImageDraw.Draw(base)
    # 2560×1440 safe area: x=507..2053, y=508..931 (derived from YouTube's 1235×338 area at 2048×1152).
    # Small custom lens-lantern seal at x675, coherent with circular profile.
    cx,cy=679,718
    d.ellipse((cx-98,cy-98,cx+98,cy+98),outline=COPPER,width=10)
    d.ellipse((cx-75,cy-75,cx+75,cy+75),outline=(218,187,138),width=3)
    d.line((cx-29,cy+45,cx+27,cy-35),fill=IVORY,width=11)
    d.ellipse((cx+7,cy-63,cx+64,cy-6),outline=IVORY,width=8)
    d.ellipse((cx-99,cy-99,cx+99,cy+99),outline=(60,88,84),width=2)
    x=817
    ftop=ft(ANTON,120); fmain=ft(ANTON,180)
    text_xy(d,'THE DOCKET',ftop,(x,510),IVORY)
    text_xy(d,'LANTERN',fmain,(x-5,602),IVORY)
    d.rectangle((x+3,826,1704,831),fill=COPPER)
    text_xy(d,'HISTORY LEAVES CLUES',ft(DM,37),(x+2,838),MINT)
    # upload-ready 2560x1440 16:9 and <6MB (verified in build output)
    up=R/'BANNER_UPLOAD_2560x1440.jpg';base.save(up,'JPEG',quality=93,subsampling=0,optimize=True)
    # High-resolution resampled archive copy, explicitly labeled as such.
    master=base.resize((5120,2880),Image.Resampling.LANCZOS)
    p=R/'BANNER_MASTER_5120x2880_RESAMPLED.jpg';master.save(p,'JPEG',quality=94,subsampling=0,optimize=True)
    safe=base.crop((507,508,2053,931));safe.save(R/'BANNER_MOBILE_SAFE_PREVIEW.png',optimize=True)
    base.crop((0,508,2560,931)).save(R/'BANNER_DESKTOP_STRIP_PREVIEW.png',optimize=True)
    return base

def overview(profile,banner):
    W,H=2000,1530;out=Image.new('RGB',(W,H),(242,238,227));d=ImageDraw.Draw(out)
    d.rectangle((0,0,W,197),fill=INK)
    d.text((57,13),'THE DOCKET LANTERN',font=ft(ANTON,91),fill=IVORY)
    d.text((62,133),'PROFILE  /  BANNER  /  MOBILE-SAFE BRAND SYSTEM',font=ft(DM,25),fill=MINT)
    d.rounded_rectangle((36,220,1964,1270),radius=26,fill=(255,253,246))
    b=ImageOps.fit(banner,(1848,1040),Image.Resampling.LANCZOS);out.paste(b,(76,226))
    d.rounded_rectangle((38,1288,1964,1495),radius=18,fill=(224,231,220))
    s=Image.open(R/'PROFILE_CIRCLE_98px_PREVIEW.png').resize((160,160),Image.Resampling.LANCZOS)
    out.paste(s,(82,1312),s)
    d.text((275,1331),'DARK PETROL   /   WARM IVORY   /   COPPER LANTERN',font=ft(ANTON,38),fill=INK)
    d.text((277,1392),'Visual mascot: selected ginger detective; channel name remains a proposal.',font=ft(DM,25),fill=(73,92,90))
    out.save(R/'00_BRAND_OVERVIEW.png',optimize=True)

if __name__=='__main__':
    p,_=profile();b=banner();overview(p,b)
    for f in sorted(R.glob('*')):
        if f.is_file():print(f.name,f.stat().st_size)

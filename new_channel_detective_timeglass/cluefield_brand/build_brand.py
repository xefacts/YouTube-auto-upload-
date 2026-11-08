#!/usr/bin/env python3
"""Reproducibly build Cluefield's upload-ready YouTube channel art."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parent
F=R.parent/'assets'/'fonts'; ANTON=F/'Anton-Regular.ttf'; DM=F/'DMSans.ttf'
NAVY=(8,18,27); INK=(10,28,39); IVORY=(247,243,227); COPPER=(205,145,83); TEAL=(117,191,183)
def ft(p,n):return ImageFont.truetype(str(p),n)
def centered(draw,xy,text,font,fill,anchor='mm'):draw.text(xy,text,font=font,fill=fill,anchor=anchor)
def profile():
 src=Image.open(R/'art/profile_portrait.png').convert('RGB')
 im=ImageOps.fit(src,(1600,1600),Image.Resampling.LANCZOS,centering=(.5,.46))
 d=ImageDraw.Draw(im);d.ellipse((40,40,1560,1560),outline=COPPER,width=13);d.ellipse((60,60,1540,1540),outline=TEAL,width=4)
 im.save(R/'PROFILE_MASTER_1600.png',optimize=True)
 im.resize((800,800),Image.Resampling.LANCZOS).save(R/'PROFILE_UPLOAD_800x800.png',optimize=True)
 tiny=im.resize((98,98),Image.Resampling.LANCZOS).convert('RGBA');mask=Image.new('L',(98,98),0);ImageDraw.Draw(mask).ellipse((0,0,97,97),fill=255);tiny.putalpha(mask);tiny.save(R/'PROFILE_CIRCLE_98px_PREVIEW.png')
def banner():
 src=Image.open(R/'art/banner_backplate.png').convert('RGB')
 im=ImageOps.fit(src,(2560,1440),Image.Resampling.LANCZOS,centering=(.5,.5)).convert('RGBA')
 # Gentle centered contrast veil keeps name readable while preserving the cinematic map desk.
 veil=Image.new('RGBA',im.size,(0,0,0,0));v=ImageDraw.Draw(veil);v.rounded_rectangle((500,500,2060,940),radius=42,fill=(5,18,27,153));im=Image.alpha_composite(im,veil).convert('RGB');d=ImageDraw.Draw(im)
 # All wordmark elements remain within YouTube central 1546x423 mobile-safe area.
 cx,cy=820,720
 d.ellipse((cx-105,cy-105,cx+105,cy+105),outline=COPPER,width=9);d.ellipse((cx-83,cy-83,cx+83,cy+83),outline=TEAL,width=3)
 d.ellipse((cx-41,cy-41,cx+41,cy+41),outline=IVORY,width=8);d.line((cx+25,cy+25,cx+72,cy+72),fill=IVORY,width=11)
 centered(d,(1450,632),'CLUEFIELD',ft(ANTON,144),IVORY)
 d.rounded_rectangle((1090,722,1810,729),radius=3,fill=COPPER)
 centered(d,(1450,786),'TRUE STORIES. HIDDEN DETAILS.',ft(DM,38),TEAL)
 centered(d,(1450,855),'HISTORY  •  MYSTERIES  •  EXPLAINERS',ft(DM,23),IVORY)
 im.save(R/'BANNER_UPLOAD_2560x1440.jpg','JPEG',quality=93,subsampling=0,optimize=True)
 im.resize((5120,2880),Image.Resampling.LANCZOS).save(R/'BANNER_MASTER_5120x2880_RESAMPLED.jpg','JPEG',quality=94,subsampling=0,optimize=True)
 im.crop((507,508,2053,931)).save(R/'BANNER_MOBILE_SAFE_PREVIEW.png',optimize=True)
 im.crop((0,508,2560,931)).save(R/'BANNER_DESKTOP_STRIP_PREVIEW.jpg','JPEG',quality=92,optimize=True)
 return im
def overview():
 banner=Image.open(R/'BANNER_UPLOAD_2560x1440.jpg').convert('RGB')
 out=Image.new('RGB',(1800,1290),(244,241,232));d=ImageDraw.Draw(out)
 d.rectangle((0,0,1800,180),fill=INK);d.text((60,25),'CLUEFIELD',font=ft(ANTON,90),fill=IVORY);d.text((64,127),'A premium identity for true stories & hidden details',font=ft(DM,26),fill=TEAL)
 b=ImageOps.fit(banner,(1680,945),Image.Resampling.LANCZOS);out.paste(b,(60,210))
 p=Image.open(R/'PROFILE_CIRCLE_98px_PREVIEW.png').resize((160,160),Image.Resampling.LANCZOS);out.paste(p,(80,1085),p)
 d.text((280,1110),'NAVY  /  PETROL TEAL  /  WARM IVORY  /  COPPER',font=ft(ANTON,34),fill=INK)
 d.text((282,1170),'Short, memorable, clear in a sponsor deck and at phone size.',font=ft(DM,24),fill=(63,80,85))
 out.save(R/'00_BRAND_OVERVIEW.png',optimize=True)
if __name__=='__main__':
 profile();banner();overview()
 for p in sorted(R.glob('*')):
  if p.is_file():print(p.name,p.stat().st_size)

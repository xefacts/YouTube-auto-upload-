#!/usr/bin/env python3
"""Create the UNCASE true-crime channel brand upload files and crop proofs."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
R=Path(__file__).resolve().parent;F=R.parent/'assets/fonts'
ANT=F/'Anton-Regular.ttf';DM=F/'DMSans.ttf'
NAVY=(10,15,24);IVORY=(247,242,230);RED=(183,57,66);MUTED=(190,198,202);PALE=(232,224,209)
def font(p,s):return ImageFont.truetype(str(p),s)
def profile():
 # Bespoke vector emblem: open case file + magnifier; legible at circle-icon scale.
 im=Image.new('RGB',(1600,1600),NAVY);d=ImageDraw.Draw(im)
 d.ellipse((72,72,1528,1528),fill=(16,25,37),outline=RED,width=22)
 d.rounded_rectangle((400,385,1170,1160),radius=76,outline=IVORY,width=46)
 d.line((475,555,1090,555),fill=(89,105,120),width=27)
 d.line((475,665,940,665),fill=(89,105,120),width=27)
 # red unresolved marker across bottom-right of file, with magnifier ring
 d.ellipse((820,760,1280,1220),outline=RED,width=45)
 d.line((1185,1125,1390,1330),fill=RED,width=58)
 d.ellipse((960,900,1140,1080),fill=IVORY)
 im.save(R/'PROFILE_MASTER_1600.png',optimize=True)
 im.resize((800,800),Image.Resampling.LANCZOS).save(R/'PROFILE_UPLOAD_800x800.png',optimize=True)
 tiny=im.resize((98,98),Image.Resampling.LANCZOS).convert('RGBA');mask=Image.new('L',(98,98),0);ImageDraw.Draw(mask).ellipse((0,0,97,97),fill=255);tiny.putalpha(mask);tiny.save(R/'PROFILE_CIRCLE_98px_PREVIEW.png')
def banner():
 bg=ImageOps.fit(Image.open(R/'art/banner_backplate.png').convert('RGB'),(2560,1440),Image.Resampling.LANCZOS).convert('RGBA')
 veil=Image.new('RGBA',bg.size,(0,0,0,0));d=ImageDraw.Draw(veil);d.rounded_rectangle((480,500,2080,940),radius=44,fill=(7,13,23,188));im=Image.alpha_composite(bg,veil).convert('RGB');d=ImageDraw.Draw(im)
 # Safe area center approximately x=507..2053/y=508..931; logo and all text kept within.
 cx,cy=820,715;d.rounded_rectangle((cx-108,cy-118,cx+108,cy+118),radius=30,outline=IVORY,width=11)
 d.line((cx-68,cy-43,cx+66,cy-43),fill=(101,119,132),width=12);d.line((cx-68,cy-4,cx+36,cy-4),fill=(101,119,132),width=12)
 d.ellipse((cx+9,cy+10,cx+92,cy+93),outline=RED,width=11);d.line((cx+78,cy+79,cx+118,cy+119),fill=RED,width=13)
 d.text((1000,568),'UNCASE',font=font(ANT,158),fill=IVORY,stroke_width=0)
 d.rounded_rectangle((1006,752,1808,761),radius=4,fill=RED)
 d.text((1007,786),'UNSOLVED. RE-EXAMINED.',font=font(DM,38),fill=IVORY)
 d.text((1008,851),'TRUE CRIME  /  EVIDENCE  /  OPEN CASES',font=font(DM,23),fill=MUTED)
 im.save(R/'BANNER_UPLOAD_2560x1440.jpg','JPEG',quality=93,subsampling=0,optimize=True)
 im.resize((5120,2880),Image.Resampling.LANCZOS).save(R/'BANNER_MASTER_5120x2880_RESAMPLED.jpg','JPEG',quality=93,subsampling=0,optimize=True)
 im.crop((507,508,2053,931)).save(R/'BANNER_MOBILE_SAFE_PREVIEW.png',optimize=True)
 im.crop((0,508,2560,931)).save(R/'BANNER_DESKTOP_STRIP_PREVIEW.jpg','JPEG',quality=92,optimize=True)
 return im
def overview():
 b=Image.open(R/'BANNER_UPLOAD_2560x1440.jpg').convert('RGB');out=Image.new('RGB',(1800,1290),(238,236,231));d=ImageDraw.Draw(out)
 d.rectangle((0,0,1800,180),fill=NAVY);d.text((60,22),'UNCASE',font=font(ANT,94),fill=IVORY);d.text((64,127),'TRUE-CRIME CHANNEL BRAND SYSTEM',font=font(DM,26),fill=(202,157,158))
 out.paste(ImageOps.fit(b,(1680,945),Image.Resampling.LANCZOS),(60,210))
 p=Image.open(R/'PROFILE_CIRCLE_98px_PREVIEW.png').resize((160,160),Image.Resampling.LANCZOS);out.paste(p,(80,1085),p)
 d.text((280,1110),'MIDNIGHT NAVY  /  PAPER IVORY  /  CASE RED',font=font(ANT,34),fill=NAVY)
 d.text((282,1170),'Evidence first. Victims treated with dignity. Open cases stay open.',font=font(DM,23),fill=(72,77,87))
 out.save(R/'00_BRAND_OVERVIEW.png',optimize=True)
if __name__=='__main__':
 profile();banner();overview()
 for p in sorted(R.glob('*')):
  if p.is_file():print(p.name,p.stat().st_size)

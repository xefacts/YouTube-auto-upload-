#!/usr/bin/env python3
"""Original 9:16 Florida V15 Shorts cover. Uses video art, not real-case imagery."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SRC=ROOT/'episodes/florida_hotel_mystery_001/v5_articulated/assets/florida_suite_shooter_consistent.png'
ANTON=str(ROOT/'assets/fonts/Anton-Regular.ttf')
SANS=str(ROOT/'assets/fonts/DMSans.ttf')
im=Image.open(SRC).convert('RGB').resize((1080,1920),Image.Resampling.LANCZOS)
a=np.asarray(im).astype(np.float32)
y=np.arange(1920,dtype=np.float32)[:,None,None]
# Controlled lower-edge gradient protects large title without masking the face,
# gun arm or flashback setting. Slight warm glow and cool cinematic shadows.
fade=np.clip((y-1000)/820,0,1)**1.4*.90
shade=np.array([8,16,21],np.float32)[None,None,:]
a=np.uint8(np.clip(a*(1-fade)+shade*fade,0,255))
im=Image.fromarray(a)
d=ImageDraw.Draw(im,'RGBA')
d.rectangle((70,107,83,169),fill=(205,62,62,255))
d.text((103,111),'CASE EMBER',font=ImageFont.truetype(SANS,45),fill=(249,237,215,255))
# A purposeful red proof marker follows the shadowed hand, not the victim face.
d.arc((595,650,766,820),-32,300,fill=(218,60,61,245),width=12)
d.rounded_rectangle((66,1274,568,1344),radius=12,fill=(5,14,19,220))
d.text((78,1280),'A FICTIONAL FLORIDA MYSTERY',font=ImageFont.truetype(SANS,37),
       fill=(232,215,187,255))
d.text((67,1355),'THE LOCKED',font=ImageFont.truetype(ANTON,120),
       fill=(249,237,211,255),stroke_width=2,stroke_fill=(5,12,15,255))
d.text((66,1472),'SUITE',font=ImageFont.truetype(ANTON,237),
       fill=(230,163,106,255),stroke_width=2,stroke_fill=(5,12,15,255))
out=HERE/'FLORIDA_V15_SHORTS_COVER_1080x1920.jpg'
im.save(out,quality=93,optimize=True,subsampling=0)
im.resize((270,480),Image.Resampling.LANCZOS).save(HERE/'FLORIDA_V15_SHORTS_COVER_PHONE_PREVIEW.png')
print(out,im.size,out.stat().st_size)

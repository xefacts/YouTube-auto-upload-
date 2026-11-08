#!/usr/bin/env python3
"""Compose a readable character model sheet from three separately generated stills."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT=Path(__file__).resolve().parent
FONT_DIR=ROOT.parent/'assets/fonts'
HEAD=FONT_DIR/'Anton-Regular.ttf'
BODY=FONT_DIR/'DMSans.ttf'
W,H=3200,2300
INK=(14,36,39);MUTED=(65,87,87);PAPER=(248,247,237)
TEAL=(32,83,87);CAMEL=(201,161,110);LIME=(211,241,114);BURG=(93,45,55)

im=Image.new('RGB',(W,H),PAPER)
d=ImageDraw.Draw(im)
F=lambda path,size:ImageFont.truetype(str(path),size)
d.rectangle((0,0,W,300),fill=INK)
d.text((120,50),'THE VALE FILES',font=F(HEAD,160),fill=(247,244,229))
d.text((124,248),'DETECTIVE VALE  /  CHARACTER MODEL REFERENCE  /  DRAFT',font=F(BODY,38),fill=LIME)
d.text((2420,100),'UNVERIFIED HANDLE',font=F(BODY,33),fill=(190,215,208))
d.text((2460,150),'@TheValeFiles',font=F(BODY,46),fill=(247,244,229))

cards=[('04_Character_Front.png','FRONT','NEUTRAL • LENS UP'),('05_Character_Side.png','SIDE','LEFT PROFILE • CLUE SEARCH'),('06_Character_Back.png','BACK','OVER-SHOULDER ENTRY')]
for i,(name,view,detail) in enumerate(cards):
    x=95+i*1004;y=360;cw=940;ch=1305
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=32,fill=(255,254,250),outline=(210,213,197),width=3)
    pose=Image.open(ROOT/name).convert('RGB')
    # Preserve full-body silhouette and its plain field; one still per pose.
    pose.thumbnail((855,1060),Image.Resampling.LANCZOS)
    im.paste(pose,(x+(cw-pose.width)//2,y+24+(1090-pose.height)//2))
    d.line((x+45,y+1112,x+cw-45,y+1112),fill=(216,218,201),width=3)
    d.text((x+55,y+1130),view,font=F(HEAD,89),fill=INK)
    d.text((x+57,y+1232),detail,font=F(BODY,32),fill=MUTED)

# Footer: essential visual continuity instructions and character identity.
d.rounded_rectangle((95,1710,3105,2220),radius=32,fill=(232,236,223))
d.text((142,1750),'CANONICAL IDENTITY',font=F(HEAD,65),fill=INK)
notes=[
    'Adult American-noir male • simple original 2D ink style',
    'Same face, dot eyes, raised brow & chestnut hair in every shot',
    'Camel fedora + coat • teal band + waistcoat • burgundy tie',
    'Round black lens + compact notebook; never morph the hat/hands',
]
for j,line in enumerate(notes):
    d.text((150,1835+j*64),line,font=F(BODY,37),fill=INK)
d.text((150,2120),'PROPOSED LINE: “I’m Vale. This is The Vale Files. Case open.”',font=F(BODY,40),fill=INK)

# Original bust portrait anchors face fidelity without pretending these generated
# full-body views are a mechanically perfect turnaround.
portrait=Image.open(ROOT/'03_Canonical_Portrait.png').convert('RGB')
portrait=ImageOps.fit(portrait,(410,410),method=Image.Resampling.LANCZOS)
im.paste(portrait,(2640,1744))
d.rounded_rectangle((2640,1744,3050,2154),radius=8,outline=INK,width=5)

for j,color in enumerate((CAMEL,TEAL,BURG,LIME)):
    d.rounded_rectangle((1460+j*154,1767,1580+j*154,1803),radius=8,fill=color)
im.save(ROOT/'02_Character_Sheet.png',optimize=True)
print(ROOT/'02_Character_Sheet.png',(ROOT/'02_Character_Sheet.png').stat().st_size)

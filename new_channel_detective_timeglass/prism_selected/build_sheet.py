#!/usr/bin/env python3
"""Compose the selected Prism detective's four-angle concept art and lens macro."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent
FONTS = ROOT.parent/'assets'/'fonts'
BOLD = FONTS/'Anton-Regular.ttf'
BODY = FONTS/'DMSans.ttf'
C = {'ink':'#172a2e','cream':'#f5f1e5','card':'#fffaf0','teal':'#37b7ba','muted':'#536364','rule':'#d9d9ce'}
W,H = 4800,2700

def f(path,size): return ImageFont.truetype(str(path),size)

def crop_figure(image):
    """Crop broad parchment margins; preserve feet and held objects."""
    im = image.convert('RGB')
    # Dark figure outlines, coat, case folder and lens rim. Ignore paper texture.
    small=im.resize((im.width//4,im.height//4),Image.Resampling.LANCZOS)
    pts=[]; px=small.load()
    for y in range(small.height):
        for x in range(small.width):
            r,g,b=px[x,y]
            if min(r,g,b)<155:
                pts.append((x,y))
    if not pts: return im
    left=max(0,(min(x for x,y in pts)-7)*4)
    top=max(0,(min(y for x,y in pts)-7)*4)
    right=min(im.width,(max(x for x,y in pts)+8)*4)
    bottom=min(im.height,(max(y for x,y in pts)+8)*4)
    return im.crop((left,top,right,bottom))

def draw():
    im=Image.new('RGB',(W,H),C['cream']);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,310),fill=C['ink'])
    d.text((95,24),'02 / PRISM',font=f(BOLD,150),fill='#fffaf0')
    d.text((102,207),'SELECTED CHARACTER DIRECTION   •   FRONT / LEFT / BACK / RIGHT',font=f(BODY,48),fill='#b7dcdb')
    d.rounded_rectangle((3737,78,4700,239),radius=68,fill='#2c6569')
    d.text((3825,111),'THE SHARP ANALYST',font=f(BOLD,67),fill='#ffffff')
    views=[('01  FRONT','front.png'),('02  LEFT','left_profile.png'),('03  BACK','back.png'),('04  RIGHT','right_profile.png')]
    x0=84;cardw=848;gap=28;top=362;bottom=2237
    for i,(label,name) in enumerate(views):
        x=x0+i*(cardw+gap)
        d.rounded_rectangle((x,top,x+cardw,bottom),radius=27,fill=C['card'],outline=C['rule'],width=4)
        d.rectangle((x+22,top+25,x+33,top+97),fill=C['teal'])
        art=crop_figure(Image.open(ROOT/'art'/name))
        art=ImageOps.contain(art,(cardw-36,1600),Image.Resampling.LANCZOS)
        im.paste(art,(x+(cardw-art.width)//2,top+85+(1600-art.height)//2))
        d.line((x+40,bottom-184,x+cardw-40,bottom-184),fill=C['rule'],width=3)
        d.text((x+42,bottom-158),label,font=f(BOLD,68),fill=C['ink'])
        if i==0: note='SLATE COAT / SILVER CLASP'
        elif i==2: note='CENTER SEAM / CLEAN BACK'
        else: note='TRUE SIDE PROFILE / SAME SILHOUETTE'
        d.text((x+45,bottom-72),note,font=f(BODY,26),fill=C['muted'])
    x=3588;panelw=1128
    d.rounded_rectangle((x,top,x+panelw,bottom),radius=27,fill='#e7eae1',outline='#c7d8d2',width=4)
    d.text((x+50,top+46),'SIGNATURE OPTIC',font=f(BOLD,88),fill=C['ink'])
    d.text((x+54,top+175),'PRISM  /  MAGNIFYING LENS',font=f(BODY,40),fill='#2f777a')
    lens=Image.open(ROOT/'art'/'prism_lens.png').convert('RGB')
    lens=ImageOps.contain(lens,(960,980),Image.Resampling.LANCZOS)
    im.paste(lens,(x+(panelw-lens.width)//2,top+236+(980-lens.height)//2))
    d.line((x+55,top+1285,x+panelw-55,top+1285),fill='#bac9bf',width=4)
    for j,(head,body) in enumerate([
        ('01 / FRAME','Brushed gunmetal + champagne brass'),
        ('02 / GLASS','Clear optic with a small inset prism'),
        ('03 / ACCENT','Fine cyan refraction, not a magic beam'),
        ('04 / GRIP','Knurled dial + dark walnut handle')]):
        yy=top+1330+j*124
        d.text((x+66,yy),head,font=f(BOLD,39),fill=C['ink'])
        d.text((x+66,yy+49),body,font=f(BODY,31),fill=C['muted'])
    d.rounded_rectangle((84,2281,4716,2615),radius=25,fill='#dfe8df')
    d.text((130,2304),'MODEL NOTES',font=f(BOLD,77),fill=C['ink'])
    d.text((131,2413),'Lean adult male  /  jet-black cropped hair  /  asymmetrical high collar  /  tan case file',font=f(BODY,42),fill='#31494b')
    d.text((131,2493),'Reference-guided AI concept angles; finish the lens and harmonize seams before frame-to-frame animation.',font=f(BODY,36),fill=C['muted'])
    out=ROOT/'PRISM_SELECTED_CHARACTER_SHEET.png'
    im.save(out,optimize=True)
    print(out,out.stat().st_size)

if __name__=='__main__':draw()

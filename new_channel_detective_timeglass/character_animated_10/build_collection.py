#!/usr/bin/env python3
"""Ten handsome 2D-animation-style concept sheets; AI heroes + honest guides.

Front images are separately created concept illustrations. Alternate angles drawn
below are design/silhouette studies, not exact matching AI turnarounds or clips.
"""
from __future__ import annotations
import importlib.util,math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('guides',ROOT.parent/'character_more_versions'/'build_sheets.py')
mod=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(mod)
FONT=ROOT.parent/'assets'/'fonts'
HEAD=FONT/'Anton-Regular.ttf';BODY=FONT/'DMSans.ttf'
INK='#14282b';PAPER='#f4f1e8';WHITE='#fffdf7';MUTED='#586a6a'
C=[
 dict(id='17',name='VELVET',role='The charismatic lead',shape='longcoat',body=.93,height=1.03,skin='#ae8067',hair='#26232c',jacket='#38243f',inside='#8b283a',pants='#313238',trim='#d39a80',hat='none',face='clean',optic='AMBER IRIS',tag='Plum shoulder cape / burgundy vest / rose-petal shutter',lens='PETAL'),
 dict(id='18',name='MERIDIAN',role='The bright analyst',shape='vest',body=1.02,height=1.03,skin='#664536',hair='#20272b',jacket='#285a46',inside='#eee4cb',pants='#27333a',trim='#d7ad69',hat='none',face='clean',optic='CRESCENT',tag='Forest waistcoat / rolled sleeves / calibrated brass rim',lens='DIAL'),
 dict(id='19',name='FINCH',role='The agile observer',shape='bomber',body=.92,height=.98,skin='#d2a281',hair='#a76a3e',jacket='#39797b',inside='#e3b786',pants='#706257',trim='#bb7651',hat='none',face='moustache',optic='OFFSET',tag='Teal short field jacket / copper scarf / flip-up micro glass',lens='OVAL'),
 dict(id='20',name='NOCTIS',role='The precise investigator',shape='tactical',body=.98,height=1.06,skin='#a27861',hair='#24252c',jacket='#313843',inside='#873e48',pants='#252a2f',trim='#67bbc1',hat='none',face='clean',optic='HEX-HINGE',tag='Asymmetric charcoal blazer / red high neck / six-sided optic',lens='HEX'),
 dict(id='21',name='ATLAS',role='The field scholar',shape='duster',body=1.16,height=1.03,skin='#68442e',hair='#2d2b29',jacket='#c4aa86',inside='#275b58',pants='#433a32',trim='#c99b57',hat='none',face='beard',optic='AMBER IRIS',tag='Sand safari coat / teal waistcoat / amber split-focus glass',lens='AMBER'),
 dict(id='22',name='MARLOW',role='The coastal detective',shape='bomber',body=.94,height=1.02,skin='#ac7861',hair='#222129',jacket='#ebe5d5',inside='#25344c',pants='#363941',trim='#a8764a',hat='none',face='clean',optic='FOLD-SQUARE',tag='Ivory cropped pea jacket / indigo knit / secondary micro lens',lens='MICRO'),
 dict(id='23',name='SABLE',role='The quiet tactician',shape='bomber',body=.94,height=1.01,skin='#a47861',hair='#222027',jacket='#702f3b',inside='#565051',pants='#353539',trim='#b18955',hat='none',face='moustache',optic='CRESCENT',tag='Burgundy leather / shoulder drape / hinged green-glass shutter',lens='SHUTTER'),
 dict(id='24',name='COBALT',role='The lucid profiler',shape='longcoat',body=.94,height=1.07,skin='#604436',hair='#9b9b96',jacket='#2854a2',inside='#232731',pants='#93989a',trim='#c5c7c4',hat='none',face='clean',optic='FOLD-SQUARE',tag='Blue sleeveless overcoat / silver buckles / rectangle optic',lens='RECTANGLE'),
 dict(id='25',name='ASH',role='The restless researcher',shape='bomber',body=.91,height=1.00,skin='#b2876b',hair='#332832',jacket='#a65d3b',inside='#ede0cc',pants='#445143',trim='#d3aa75',hat='none',face='clean',optic='AMBER IRIS',tag='Copper quilted jacket / dark moss pants / three-spoke rim',lens='THREE-SPOKE'),
 dict(id='26',name='HORIZON',role='The assured historian',shape='duster',body=1.05,height=1.06,skin='#5e3b30',hair='#27272c',jacket='#e0d4bd',inside='#902f3a',pants='#31353b',trim='#c88f5f',hat='none',face='beard',optic='CRESCENT',tag='Ivory duster / crimson vest / openwork copper sun-ring',lens='SUN-RING'),
]

def font(path,n):return ImageFont.truetype(str(path),n)

def hero_image(c):
    src=Image.open(ROOT/'heroes'/f"{c['id']}_{c['name'].lower()}.png").convert('RGB')
    if c['id']=='22':src=src.crop((0,0,505,768))
    if c['id']=='23':
        src=src.crop((75,0,570,768))
        # Remove the stray edge of the second figure in the AI source; keep
        # the first detective and his raised lens untouched.
        ImageDraw.Draw(src).rectangle((478,285,src.width,600),fill='#fbf8ed')
    # Trim generous original landscape margins around painted silhouette.
    tiny=src.resize((src.width//3,src.height//3))
    pts=[];px=tiny.load()
    for y in range(tiny.height):
        for x in range(tiny.width):
            r,g,b=px[x,y]
            if min(r,g,b)<165:pts.append((x,y))
    if pts:
        x0=max(0,(min(x for x,y in pts)-7)*3)
        y0=max(0,(min(y for x,y in pts)-7)*3)
        x1=min(src.width,(max(x for x,y in pts)+8)*3)
        y1=min(src.height,(max(y for x,y in pts)+8)*3)
        src=src.crop((x0,y0,x1,y1))
    return src

def paste_art(canvas,src,area):
    x,y,w,h=area
    src=ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)
    canvas.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2))

def lens(d,cx,cy,r,c):
    k=c['lens'];gold=c['trim'];dark=INK
    def circle(x,y,rad,fill=None,outline=dark,width=15):d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=fill,outline=outline,width=width)
    if k in ('HEX','RECTANGLE'):
        if k=='HEX':
            pts=[(cx+r*math.cos(math.pi/3*i+math.pi/6),cy+r*math.sin(math.pi/3*i+math.pi/6)) for i in range(6)]
            d.polygon(pts,fill='#e2f3ee');d.line(pts+[pts[0]],fill=dark,width=21,joint='curve')
        else:
            d.rounded_rectangle((cx-r*.85,cy-r,cx+r*.85,cy+r),radius=27,fill='#e5f1ed',outline=dark,width=22)
            circle(cx+r*.52,cy-r*.62,r*.2,fill='#f5ede0',width=8)
    else:
        d.ellipse((cx-r,cy-r,cx+r,cy+r),fill='#e9f1eb',outline=dark,width=21)
        d.ellipse((cx-r*.83,cy-r*.83,cx+r*.83,cy+r*.83),outline=gold,width=9)
        if k=='PETAL':
            for a in (205,220,235):
                q=math.radians(a)
                d.ellipse((cx+math.cos(q)*r*.83-15,cy+math.sin(q)*r*.83-35,cx+math.cos(q)*r*.83+15,cy+math.sin(q)*r*.83+35),fill=gold)
        elif k=='DIAL':
            for a in range(0,360,30):
                q=math.radians(a)
                d.line((cx+math.cos(q)*r*.69,cy+math.sin(q)*r*.69,cx+math.cos(q)*r*.87,cy+math.sin(q)*r*.87),fill=dark,width=5)
            circle(cx+r*.72,cy+r*.6,r*.15,fill=gold,width=6)
        elif k=='OVAL':
            d.ellipse((cx-r*.47,cy-r*.72,cx+r*.47,cy+r*.72),outline=gold,width=7)
            circle(cx+r*.66,cy-r*.64,r*.23,fill='#edf6ec',width=8)
        elif k=='AMBER':
            circle(cx,cy,r*.48,fill='#efcb82',outline=gold,width=8)
            d.line((cx-r*.4,cy,cx+r*.44,cy),fill=dark,width=6)
        elif k=='MICRO':
            d.rounded_rectangle((cx+r*.6,cy-r*.45,cx+r*1.13,cy+r*.08),radius=12,fill='#f1eada',outline=dark,width=9)
        elif k=='SHUTTER':
            d.pieslice((cx-r*.7,cy-r*.7,cx+r*.7,cy+r*.7),90,250,fill='#2e5d53')
            circle(cx+r*.72,cy-r*.66,r*.12,fill=gold,width=5)
        elif k=='THREE-SPOKE':
            for a in (30,150,270):
                q=math.radians(a)
                d.line((cx,cy,cx+math.cos(q)*r*.75,cy+math.sin(q)*r*.75),fill=gold,width=10)
        elif k=='SUN-RING':
            for a in range(0,360,45):
                q=math.radians(a)
                d.line((cx+math.cos(q)*r*.84,cy+math.sin(q)*r*.84,cx+math.cos(q)*r*1.08,cy+math.sin(q)*r*1.08),fill=gold,width=7)
            circle(cx,cy,r*.21,fill='#e7d5b5',width=5)
    d.line((cx,cy+r*.96,cx+r*.14,cy+r*1.54),fill=dark,width=17)
    d.rounded_rectangle((cx+r*.06,cy+r*1.51,cx+r*.27,cy+r*1.78),radius=11,fill=gold,outline=dark,width=6)

def sheet(c):
    W,H=3600,1980;im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,260),fill=INK)
    d.text((75,29),f"{c['id']}  /  {c['name']}",font=font(HEAD,120),fill=WHITE)
    d.text((80,181),c['role'].upper(),font=font(BODY,36),fill='#b9d7d3')
    d.text((2815,117),'2D ANIMATED-STYLE DESIGN',font=font(BODY,31),fill='#d7e0db')
    for i,(label,view) in enumerate([('FRONT','front'),('LEFT','side'),('BACK','back'),('RIGHT','right')]):
        x=64+i*642;y=300;cw=600;ch=1333
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill=WHITE,outline='#d5dbd3',width=3)
        art=None;kind='SCHEMATIC VIEW GUIDE'
        if view=='front':art=hero_image(c);kind='GENERATED HERO CONCEPT'
        elif c['id']=='22' and view=='back':
            art=Image.open(ROOT/'heroes'/'22_marlow.png').convert('RGB').crop((994,0,1310,768));kind='GENERATED BACK STUDY'
        if art is not None:paste_art(im,art,(x+15,y+34,cw-30,1086))
        else:
            v=mod.person(c,'side' if view=='right' else view)
            if view=='right':v=ImageOps.mirror(v)
            v=v.resize((572,1035),Image.Resampling.LANCZOS)
            im.paste(v,(x+14,y+70),v)
        d.line((x+32,y+1142,x+cw-32,y+1142),fill='#d5d9d0',width=3)
        d.text((x+34,y+1153),label,font=font(HEAD,72),fill=INK)
        d.text((x+36,y+1248),kind,font=font(BODY,24),fill=MUTED)
    x=2640;y=300;cw=894;ch=1333
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill='#e3e9df',outline='#c7d4c7',width=3)
    d.text((x+57,y+57),'SIGNATURE LENS',font=font(HEAD,91),fill=INK)
    if c['id']=='23':
        src=Image.open(ROOT/'heroes'/'23_sable.png').convert('RGB').crop((857,76,1260,715))
        paste_art(im,src,(x+116,y+205,650,805))
    else:lens(d,x+449,y+542,197,c)
    d.line((x+57,y+1051,x+cw-56,y+1051),fill='#b7c5bb',width=3)
    d.text((x+56,y+1081),c['lens'],font=font(HEAD,78),fill=INK)
    for j,color in enumerate((c['skin'],c['jacket'],c['inside'],c['trim'])):
        d.rounded_rectangle((x+58+j*200,y+1220,x+215+j*200,y+1273),radius=9,fill=color)
    d.rounded_rectangle((64,1685,3534,1898),radius=23,fill='#e1e7dc')
    d.text((104,1710),c['tag'],font=font(HEAD,60),fill=INK)
    d.text((109,1801),'Four-view concept: generated hero + approximate schematic angle guides; not a finished motion clip.',font=font(BODY,31),fill='#526364')
    d.text((2700,1850),'NOT SELECTED / CHOOSE ONE',font=font(BODY,25),fill=INK)
    out=ROOT/f"{c['id']}_{c['name']}_2D_SHEET.png";im.save(out,optimize=True)
    return out

def overview(paths):
    W,H=2500,3350;im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,255),fill=INK)
    d.text((81,23),'TEN 2D DETECTIVES',font=font(HEAD,134),fill=WHITE)
    d.text((84,180),'Handsome male character options  /  4 views + unique lens per numbered sheet',font=font(BODY,35),fill='#c9dfd5')
    for i,c in enumerate(C):
        x=84+(i%2)*1175;y=292+(i//2)*590
        d.rounded_rectangle((x,y,x+1109,y+558),radius=24,fill=WHITE,outline='#d4d9d1',width=3)
        d.text((x+24,y+8),f"{c['id']}  {c['name']}",font=font(HEAD,58),fill=INK)
        src=hero_image(c);paste_art(im,src,(x+30,y+91,725,438))
        lens(d,x+905,y+257,115,c)
        d.text((x+780,y+490),c['lens'],font=font(BODY,30),fill=MUTED)
    d.text((90,3290),'Visual alternatives only — not moving animation or approved channel branding.',font=font(BODY,29),fill=MUTED)
    out=ROOT/'00_TEN_2D_ANIMATED_OPTIONS.png';im.save(out,optimize=True);return out

if __name__=='__main__':
    paths=[sheet(c) for c in C]
    overview(paths)
    for p in paths:print(p.name,p.stat().st_size)

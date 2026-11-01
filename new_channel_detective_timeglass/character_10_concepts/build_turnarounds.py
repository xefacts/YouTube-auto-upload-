#!/usr/bin/env python3
"""Ten original detective concept sheets: distinct AI hero art and schematic view guides.

Front hero illustrations are single-angle concepts, NOT mechanically consistent
turnarounds; alternate angles are vector silhouette explorations. No known
franchise character, celebrity, or reference footage is reproduced.
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parent
FONT_DIR=ROOT.parent/'assets/fonts'
HEAD=FONT_DIR/'Anton-Regular.ttf';BODY=FONT_DIR/'DMSans.ttf'
W,H=3200,1800
INK='#172a2e'; PAPER='#f5f3e9'; WHITE='#fffdf7';MUTED='#5f6b6c'

CONCEPTS=[
 dict(id='01',name='CHRONO',role='The measured investigator',skin='#8b5439',hair='#353534',coat='#213e4a',vest='#c49a64',pants='#2d3d43',accent='#c9a66d',hat='none',facial='moustache',body=1.10,lens='CLOCKWORK',tag='Brass time-ring / rotating minute hand',detail='A grounded senior investigator with a clockwork lens.'),
 dict(id='02',name='PRISM',role='The sharp analyst',skin='#d8a981',hair='#1d2830',coat='#3f5e80',vest='#d5d2bc',pants='#263f59',accent='#92ccce',hat='none',facial='clean',body=.91,lens='PRISM',tag='Triangular refracting glass / blue edge',detail='Lean silhouette and a spectral three-sided lens.'),
 dict(id='03',name='ECLIPSE',role='The midnight tracker',skin='#ac775c',hair='#1e2429',coat='#503a51',vest='#2b2d3a',pants='#282b36',accent='#d7b278',hat='bowler',facial='stubble',body=1.02,lens='ECLIPSE',tag='Obsidian aperture / moving crescent',detail='Noir figure with a half-shutter dark glass.'),
 dict(id='04',name='FOLIO',role='The archive scholar',skin='#d7b59b',hair='#b8b8a8',coat='#61705b',vest='#c9b898',pants='#494b43',accent='#a47c4b',hat='flatcap',facial='beard',body=1.02,lens='FOLDOUT',tag='Square folio glass / book-like hinges',detail='An older paper-trail specialist with a folding lens.'),
 dict(id='05',name='TIDEMARK',role='The maritime sleuth',skin='#a36d4c',hair='#25292b',coat='#2b6773',vest='#d3c49e',pants='#304751',accent='#d7a85f',hat='none',facial='clean',body=1.06,lens='COMPASS',tag='Compass-rim lens / four tiny cardinal points',detail='Broad, sea-worn coat and a navigational glass.'),
 dict(id='06',name='EMBER',role='The quiet witness',skin='#704735',hair='#252324',coat='#363c39',vest='#8d493d',pants='#262d2b',accent='#e3aa67',hat='none',facial='beard',body=1.13,lens='LANTERN',tag='Amber-lit rim / shuttered practical light',detail='Warm lamp-lens against an understated dark suit.'),
 dict(id='07',name='HEX',role='The field investigator',skin='#c68d6c',hair='#713c2f',coat='#ad7947',vest='#375b5b',pants='#374343',accent='#a4d3bd',hat='none',facial='clean',body=.98,lens='HEXAGON',tag='Six-sided glass / precise etched edges',detail='Fast contemporary silhouette with a hexagonal optic.'),
 dict(id='08',name='DUAL',role='The pattern finder',skin='#9e735c',hair='#56585b',coat='#55465f',vest='#c5ad84',pants='#3c3542',accent='#b5a8dc',hat='none',facial='goatee',body=.95,lens='SPLIT',tag='Two linked focal discs / hinged bridge',detail='A two-focus tool for double-reading every clue.'),
 dict(id='09',name='TRACE',role='The forensic cartographer',skin='#c79878',hair='#292831',coat='#567075',vest='#d8cbbb',pants='#3b4a4b',accent='#8edacc',hat='none',facial='clean',body=.93,lens='TRACE',tag='Fine cyan trace ring / tiny scan marks',detail='Clean technical silhouette without a cyberpunk suit.'),
 dict(id='10',name='SUNDIAL',role='The roaming historian',skin='#624335',hair='#2f3232',coat='#9b6347',vest='#c9b89a',pants='#463a36',accent='#ead08a',hat='none',facial='stubble',body=1.07,lens='SUNDIAL',tag='Eight-spoke sun-rim / sliding shadow mark',detail='Warm explorer shape with a striking spoked lens.'),
]


def rgb(hexstr):return tuple(bytes.fromhex(hexstr.lstrip('#')))
def font(path,size):return ImageFont.truetype(str(path),size)


def lens(draw,cx,cy,r,c):
    """Distinct, reproducible tool silhouette for all four views and detail panel."""
    edge=rgb(c['accent']);dark=rgb(INK);w=max(4,round(r*.14));name=c['lens']
    def ellipse(box,fill=None,outline=None,width=1):draw.ellipse(box,fill=fill,outline=outline,width=width)
    if name=='FOLDOUT':
        draw.rounded_rectangle((cx-r,cy-r,cx+r,cy+r),radius=round(r*.16),fill='#e9f4eb',outline=dark,width=w)
        draw.line((cx-r*.7,cy-r*.7,cx+r*.7,cy-r*.7),fill=edge,width=max(3,w//2))
        draw.ellipse((cx-r*1.19,cy-r*.9,cx-r*.91,cy-r*.63),fill=edge,outline=dark,width=max(2,w//4))
    elif name=='HEXAGON':
        pts=[(cx+r*math.cos(math.pi/3*i+math.pi/6),cy+r*math.sin(math.pi/3*i+math.pi/6)) for i in range(6)]
        draw.polygon(pts,fill='#e9f4eb');draw.line(pts+[pts[0]],fill=dark,width=w,joint='curve')
        pts2=[(cx+r*.77*math.cos(math.pi/3*i+math.pi/6),cy+r*.77*math.sin(math.pi/3*i+math.pi/6)) for i in range(6)]
        draw.line(pts2+[pts2[0]],fill=edge,width=max(2,w//3),joint='curve')
    elif name=='SPLIT':
        for dx in (-r*.48,r*.48):ellipse((cx+dx-r*.65,cy-r*.69,cx+dx+r*.65,cy+r*.69),fill='#edf0f5',outline=dark,width=w)
        draw.line((cx-r*.17,cy-r*.76,cx+r*.17,cy-r*.76),fill=edge,width=max(3,w//2))
    else:
        ellipse((cx-r,cy-r,cx+r,cy+r),fill='#e9f1e9',outline=dark,width=w)
        ellipse((cx-r*.78,cy-r*.78,cx+r*.78,cy+r*.78),outline=edge,width=max(3,w//3))
        if name=='CLOCKWORK':
            for a in range(0,360,30):
                th=math.radians(a);draw.line((cx+math.cos(th)*r*.71,cy+math.sin(th)*r*.71,cx+math.cos(th)*r*.9,cy+math.sin(th)*r*.9),fill=dark,width=max(2,w//5))
            draw.line((cx,cy,cx+r*.3,cy-r*.47),fill=dark,width=max(3,w//4));draw.line((cx,cy,cx-r*.35,cy-r*.06),fill=edge,width=max(2,w//5))
        elif name=='PRISM':
            draw.polygon([(cx,cy-r*.5),(cx-r*.54,cy+r*.41),(cx+r*.54,cy+r*.41)],outline=edge,width=max(3,w//3))
            draw.line((cx+r*.48,cy-r*.1,cx+r*.77,cy-r*.38),fill='#83bece',width=max(2,w//4))
        elif name=='ECLIPSE':
            ellipse((cx-r*.52,cy-r*.52,cx+r*.52,cy+r*.52),fill='#2e3946')
            ellipse((cx-r*.33,cy-r*.56,cx+r*.7,cy+r*.48),fill='#e9f1e9')
        elif name=='COMPASS':
            draw.line((cx-r*.66,cy,cx+r*.66,cy),fill=dark,width=max(2,w//5));draw.line((cx,cy-r*.66,cx,cy+r*.66),fill=dark,width=max(2,w//5))
            draw.polygon([(cx,cy-r*.52),(cx+r*.15,cy),(cx,cy+r*.52),(cx-r*.15,cy)],fill=edge)
        elif name=='LANTERN':
            ellipse((cx-r*.5,cy-r*.5,cx+r*.5,cy+r*.5),fill='#f8d897')
            draw.arc((cx-r*.5,cy-r*.5,cx+r*.5,cy+r*.5),150,275,fill=edge,width=max(3,w//3))
        elif name=='TRACE':
            for a in range(0,360,45):
                th=math.radians(a);draw.ellipse((cx+math.cos(th)*r*.62-4,cy+math.sin(th)*r*.62-4,cx+math.cos(th)*r*.62+4,cy+math.sin(th)*r*.62+4),fill=edge)
            draw.line((cx-r*.25,cy,cx+r*.25,cy),fill=edge,width=max(2,w//4))
        elif name=='SUNDIAL':
            for a in range(0,360,45):
                th=math.radians(a);draw.line((cx,cy,cx+math.cos(th)*r*.61,cy+math.sin(th)*r*.61),fill=edge,width=max(2,w//5))
            ellipse((cx-r*.18,cy-r*.18,cx+r*.18,cy+r*.18),fill=dark)
    draw.line((cx,cy+r*.98,cx+r*.12,cy+r*1.62),fill=dark,width=max(6,round(r*.18)))
    draw.rounded_rectangle((cx+r*.02,cy+r*1.58,cx+r*.24,cy+r*1.82),radius=max(2,round(r*.1)),fill=edge,outline=dark,width=max(2,w//4))


def figure(c,view):
    """Draw an actual three-angle model; right view mirrors the accurate side silhouette."""
    # Large intermediate size gives crisp antialiased outlines in final sheet.
    S=2;im=Image.new('RGBA',(560*S,1060*S),(0,0,0,0));d=ImageDraw.Draw(im)
    def t(coords):return tuple(round(v*S) for v in coords)
    def poly(pts,fill,outline=True):
        q=[t(p) for p in pts];d.polygon(q,fill=fill)
        if outline:d.line(q+[q[0]],fill=INK,width=5*S,joint='curve')
    def line(pts,fill=INK,width=5):d.line([t(p) for p in pts],fill=fill,width=width*S,joint='curve')
    def ell(box,fill,outline=INK,width=5):d.ellipse(t(box),fill=fill,outline=outline,width=width*S)
    skin=c['skin'];hair=c['hair'];coat=c['coat'];vest=c['vest'];pants=c['pants'];acc=c['accent'];b=c['body']
    # Grounding shadow + legs and shoes.
    d.ellipse(t((150,996,452,1028)),fill=(20,40,42,23))
    if view in ('front','back'):
        poly([(205,660),(269,660),(267,949),(205,950)],pants)
        poly([(292,660),(356,660),(365,950),(300,950)],pants)
        ell((181,941,275,1006),'#40382f');ell((291,941,393,1006),'#40382f')
        line([(235,735),(235,925)],'#667071',2);line([(332,735),(336,925)],'#667071',2)
        width=round(18*(b-1));left=122-width;right=440+width
        # Outer coat with personal silhouette via body factor and length.
        length=792 if c['hat']!='none' else 742
        poly([(179,358),(239,338),(318,338),(388,358),(right,length),(left,length)],coat)
        if view=='front':
            poly([(240,346),(322,346),(357,650),(212,650)],vest)
            poly([(257,358),(287,391),(310,358)],'#ede8db')
            poly([(282,392),(302,392),(313,533),(291,557),(279,533)],'#7e444c')
            # Open coat lapels; dynamic but replicable across poses.
            poly([(178,358),(243,350),(209,452),(256,530),(201,621),(166,470)],coat)
            poly([(389,358),(325,350),(353,448),(310,532),(359,618),(405,470)],coat)
            line([(270,558),(270,656)],'#284248',2)
            ell((280,560,288,568),INK,outline=None);ell((280,616,288,624),INK,outline=None)
            poly([(168,360),(117,398),(92,593),(140,610),(206,457)],coat)
            poly([(388,360),(441,400),(464,575),(425,590),(354,452)],coat)
            ell((112,586,154,635),skin);ell((405,568,447,618),skin)
            line([(194,690),(376,690)],INK,3)
            # Small durable casebook.
            d.rounded_rectangle(t((124,487,197,584)),radius=7*S,fill='#292f32',outline=INK,width=4*S)
            line([(138,500),(173,500)],acc,2)
        else:
            # Rear yoke and belt: no facial/waistcoat visibility.
            poly([(175,365),(390,365),(365,463),(200,463)],coat)
            line([(281,455),(281,750)],INK,3)
            d.rounded_rectangle(t((167,595,399,625)),radius=8*S,fill=acc,outline=INK,width=4*S)
            poly([(170,366),(117,399),(95,593),(141,604),(200,460)],coat)
            poly([(390,366),(448,403),(470,593),(426,604),(358,460)],coat)
            ell((111,584,153,626),skin);ell((408,585,452,626),skin)
        # Neck/head and side hair.
        poly([(263,300),(307,300),(311,354),(259,354)],skin)
        if view=='front':
            ell((218,140,358,315),skin)
            ell((210,222,227,255),skin);ell((350,222,368,255),skin)
            poly([(223,156),(241,134),(338,140),(353,185),(335,175),(315,161),(286,172),(251,164),(227,192)],hair)
            for x in (260,315):ell((x-5,220,x+5,234),INK,outline=None)
            line([(246,207),(272,205)],hair,4);line([(300,205),(325,206)],hair,4)
            line([(284,239),(280,255),(292,258)],'#805642',2)
            if c['facial']=='moustache':line([(271,275),(285,271),(301,275)],hair,3)
            elif c['facial']=='beard':
                line([(241,274),(251,298),(282,310),(319,298),(331,273)],hair,3)
            elif c['facial']=='goatee':line([(281,292),(290,303),(299,291)],hair,3)
            elif c['facial']=='stubble':
                for x in range(249,325,13):ell((x,291,x+3,294),hair,outline=None)
            line([(271,279),(291,283),(310,278)],'#704c3e',2)
        else:
            ell((222,139,360,313),hair)
            line([(239,228),(256,280),(288,290),(324,280),(344,225)],'#455052',2)
        # Hat for both sides.
        hat=c['hat']
        if hat in ('fedora','widebrim','bowler','flatcap','newsboy','beret'):
            brim=90 if hat=='widebrim' else 110
            d.ellipse(t((brim,146,459,197)),fill=coat,outline=INK,width=5*S)
            if hat in ('flatcap','newsboy','beret'):
                ell((201,105,374,175),coat)
                if hat=='beret':ell((225,103,378,161),coat)
            elif hat=='bowler':ell((207,89,367,178),coat)
            else:
                poly([(215,165),(222,80),(272,65),(329,72),(351,159)],coat)
            d.rounded_rectangle(t((219,149,351,172)),radius=5*S,fill=acc,outline=INK,width=3*S)
        if view=='front':
            lens(d,456*S,500*S,42*S,c)
        else:
            lens(d,471*S,589*S,30*S,c)
    else:
        # Side profile: genuinely different head/body geometry, not a skewed front.
        poly([(240,652),(302,652),(305,948),(247,948)],pants)
        poly([(304,652),(356,656),(358,946),(308,947)],pants)
        ell((223,941,312,999),'#40382f');ell((294,941,386,999),'#40382f')
        poly([(215,365),(312,342),(385,379),(368,795),(221,796)],coat)
        poly([(284,372),(340,374),(347,652),(286,652)],vest)
        poly([(338,405),(407,468),(437,557),(406,573),(319,473)],coat)
        ell((396,547,438,594),skin)
        poly([(226,377),(192,411),(169,583),(212,601),(283,471)],coat)
        ell((187,583,224,625),skin)
        line([(244,625),(366,625)],INK,3)
        poly([(271,299),(322,299),(321,358),(271,356)],skin)
        # Ear/neck and side silhouette facing left, including nose.
        poly([(241,160),(310,145),(357,196),(342,268),(306,306),(248,289),(229,259),(212,248),(231,227)],skin)
        ell((321,219,348,251),skin)
        poly([(236,176),(256,140),(317,146),(353,193),(318,188),(283,174),(247,189)],hair)
        ell((253,221,263,232),INK,outline=None)
        line([(241,205),(266,207)],hair,4)
        line([(232,269),(251,273),(264,268)],'#704c3e',2)
        if c['facial'] in ('beard','goatee','stubble','moustache'):
            line([(236,274),(258,285),(295,289)],hair,2)
        hat=c['hat']
        if hat!='none':
            d.ellipse(t((164 if hat=='widebrim' else 190,149,414,187)),fill=coat,outline=INK,width=5*S)
            if hat in ('fedora','widebrim'):
                poly([(233,155),(236,86),(280,72),(333,86),(350,155)],coat)
            elif hat=='bowler':ell((232,94,355,168),coat)
            else:ell((228,108,361,171),coat)
            d.rounded_rectangle(t((239,149,343,169)),radius=4*S,fill=acc,outline=INK,width=3*S)
        # Lens held in hand; notebook visible at back elbow.
        lens(d,155*S,452*S,43*S,c)
        d.rounded_rectangle(t((359,512,425,607)),radius=6*S,fill='#2e3433',outline=INK,width=4*S)
    return im.resize((560,1060),Image.Resampling.LANCZOS)


def hero_source(c):
    """Crop the one chosen person from each single-angle AI concept illustration."""
    src=Image.open(ROOT/'heroes'/f"{c['id']}_{c['name'].lower()}.png").convert('RGB')
    # The Chrono source has TWO figures; use only the left, lens-holding one.
    if c['id']=='01':src=src.crop((0,0,800,src.height))
    # Trim empty parchment to make the hero large on both overview and sheet.
    small=src.resize((src.width//3,src.height//3))
    pix=small.load();xlist=[];ylist=[]
    for y in range(small.height):
        for x in range(small.width):
            r,g,b=pix[x,y]
            if min(r,g,b)<173 and max(r,g,b)-min(r,g,b)<180:
                xlist.append(x);ylist.append(y)
    if xlist:
        scale=3
        x0=max(0,(min(xlist)-8)*scale);y0=max(0,(min(ylist)-8)*scale)
        x1=min(src.width,(max(xlist)+9)*scale);y1=min(src.height,(max(ylist)+9)*scale)
        src=src.crop((x0,y0,x1,y1))
    return src


def paste_hero(im,c,box):
    src=hero_source(c)
    x,y,w,h=box
    src=ImageOps.contain(src,(w,h),Image.Resampling.LANCZOS)
    im.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2))


def sheet(c):
    out=ROOT/f"{c['id']}_{c['name']}_turnaround.png"
    im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,225),fill=INK)
    d.text((90,35),f"{c['id']}  /  {c['name']}",font=font(HEAD,104),fill=WHITE)
    d.text((95,172),c['role'].upper(),font=font(BODY,34),fill=c['accent'])
    d.text((2270,101),'DETECTIVE OPTIONS  /  01–10',font=font(BODY,30),fill='#d9ded6')
    y=267;ch=1208
    # The hero is a single generated angle. Other views are intentionally
    # labeled as schematic explorations, not claimed to be exact AI turnarounds.
    x=70;cw=800
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill=WHITE,outline='#d6d9ce',width=3)
    paste_hero(im,c,(x+25,y+22,cw-50,1055))
    d.line((x+35,y+1090,x+cw-35,y+1090),fill='#d9dcd2',width=2)
    d.text((x+37,y+1105),'HERO  /  FRONT',font=font(HEAD,52),fill=INK)
    for label,view,x in [('LEFT','side',898),('BACK','back',1445),('RIGHT','right',1992)]:
        cw=518
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill=WHITE,outline='#d6d9ce',width=3)
        v=figure(c,'side' if view=='right' else view)
        if view=='right':v=ImageOps.mirror(v)
        v=v.resize((488,924),Image.Resampling.LANCZOS)
        im.paste(v,(x+15,y+93),v)
        d.line((x+30,y+1090,x+cw-30,y+1090),fill='#d9dcd2',width=2)
        d.text((x+32,y+1105),label+'  /  GUIDE',font=font(HEAD,46),fill=INK)
    x=2539;cw=591
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill='#eef0e8',outline='#d4d9cd',width=3)
    d.text((x+44,y+60),'SIGNATURE LENS',font=font(HEAD,65),fill=INK)
    lens(d,x+295,y+521,168,c)
    for j,color in enumerate([c['skin'],c['coat'],c['vest'],c['accent']]):
        d.rounded_rectangle((x+51+j*133,y+879,x+163+j*133,y+936),radius=8,fill=color)
    d.text((x+49,y+1002),c['lens'],font=font(HEAD,66),fill=INK)
    d.text((x+51,y+1099),'DISTINCTIVE OPTIC  /  CONCEPT',font=font(BODY,25),fill=MUTED)
    d.rounded_rectangle((70,1518,3130,1744),radius=22,fill='#e6e9df')
    d.text((108,1535),c['tag'],font=font(HEAD,58),fill=INK)
    d.text((112,1624),c['detail'],font=font(BODY,33),fill=MUTED)
    d.text((112,1691),'Concept art: AI hero + approximate side/back guides; select a design before exact-angle redraw.',font=font(BODY,26),fill='#48575a')
    im.save(out,optimize=True)
    return out


def catalog(paths):
    w,h=2300,3140
    im=Image.new('RGB',(w,h),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,w,251),fill=INK)
    d.text((77,25),'TEN DETECTIVES',font=font(HEAD,128),fill=WHITE)
    d.text((79,174),'Ten different male character directions  /  compare hero and lens',font=font(BODY,36),fill='#d5ecbc')
    cw=1054;ch=510
    for i,c in enumerate(CONCEPTS):
        x=77+(i%2)*1094;y=294+(i//2)*551
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=23,fill=WHITE,outline='#d6d9ce',width=3)
        paste_hero(im,c,(x+10,y+63,595,408))
        d.text((x+37,y+13),f"{c['id']}  {c['name']}",font=font(HEAD,59),fill=INK)
        d.text((x+625,y+84),'LENS',font=font(BODY,30),fill=MUTED)
        lens(d,x+816,y+257,112,c)
        d.text((x+610,y+414),c['lens'],font=font(HEAD,44),fill=INK)
    d.text((95,3073),'Each numbered sheet: hero front, left / back / right guides, and one special optic.',font=font(BODY,29),fill=MUTED)
    out=ROOT/'00_OVERVIEW_10_OPTIONS.png';im.save(out,optimize=True);return out

if __name__=='__main__':
    paths=[sheet(c) for c in CONCEPTS]
    catalog(paths)
    for p in paths:print(p.name,p.stat().st_size)

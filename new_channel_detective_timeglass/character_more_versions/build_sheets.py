#!/usr/bin/env python3
"""Six deliberately different, original four-angle male detective design explorations.

Vector concept art. Each sheet contains front, left, back, right and an individual
magnifying lens concept. These are NOT claims of AI-generated photographic poses.
"""
from __future__ import annotations
import math
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parent
FONTS=ROOT.parent/'assets'/'fonts'
BOLD=FONTS/'Anton-Regular.ttf'; BODY=FONTS/'DMSans.ttf'
INK='#14282b';PAPER='#f4f1e8';WHITE='#fffdf6';S=3
DATA=[
 dict(id='11',name='CROSSWIND',role='The streetwise veteran',shape='bomber',body=1.22,height=.94,skin='#9c6348',hair='#555659',jacket='#a3553c',inside='#ead0a0',pants='#253f48',trim='#e4a86b',hat='none',face='whitebeard',optic='OFFSET',lensnote='Twin-offset glass / folding copper bridge',tag='A broad, grounded silhouette; cropped leather bomber and heavy boots.'),
 dict(id='12',name='GLASSHOUSE',role='The observant strategist',shape='longcoat',body=.83,height=1.07,skin='#e0b99c',hair='#c8c7bc',jacket='#543f60',inside='#a83d45',pants='#31313a',trim='#bfc6c4',hat='none',face='spectacles',optic='FOLD-SQUARE',lensnote='Articulated square / hairline silver frame',tag='Tall, angular profile; plum coat, silver hair and a red scarf.'),
 dict(id='13',name='RANGER',role='The outdoor tracker',shape='poncho',body=1.13,height=1.02,skin='#55382d',hair='#1e292b',jacket='#456455',inside='#d4a764',pants='#3b4336',trim='#d6b46a',hat='hood',face='beard',optic='AMBER IRIS',lensnote='Warm amber optic / four brass shutter leaves',tag='Hooded field poncho; a hard-wearing investigator of remote scenes.'),
 dict(id='14',name='CHALK',role='The evidence keeper',shape='vest',body=1.30,height=.90,skin='#ba8564',hair='#e0dbca',jacket='#286d67',inside='#f1e4c7',pants='#5b5146',trim='#d0a653',hat='none',face='roundglasses',optic='HEX-HINGE',lensnote='Six-sided glass / flip-out side hinge',tag='Compact, friendly archivist; rolled sleeves, waistcoat and spectacles.'),
 dict(id='15',name='NIGHTSHIFT',role='The quick-response sleuth',shape='tactical',body=.95,height=1.04,skin='#ae7757',hair='#262428',jacket='#243c50',inside='#b34748',pants='#293543',trim='#74c4bd',hat='none',face='clean',optic='SPLIT',lensnote='Dual-focus optic / triangular alignment notch',tag='Athletic cropped jacket, functional pockets and fast-moving posture.'),
 dict(id='16',name='WHARF',role='The harbor historian',shape='duster',body=1.16,height=1.08,skin='#603d31',hair='#c3bdb1',jacket='#d2c5ad',inside='#263c4d',pants='#313d40',trim='#bd724f',hat='beanie',face='whitebeard',optic='CRESCENT',lensnote='Curved half-shutter / aged bronze setting',tag='Towering ivory duster, copper scarf, salt beard and weathered boots.'),
]

def col(h):return tuple(bytes.fromhex(h.lstrip('#')))
def ft(path,size):return ImageFont.truetype(str(path),size)

def optic(d,cx,cy,r,c):
    """Six different usable magnifying glass silhouettes, not floating logos."""
    k=c['optic'];black=INK;acc=c['trim'];w=max(5,int(r*.1))
    def ell(box,**kw):d.ellipse(box,**kw)
    if k=='FOLD-SQUARE':
        d.rounded_rectangle((cx-r,cy-r,cx+r,cy+r),radius=r*.13,fill='#dcf0ea',outline=black,width=w)
        d.rounded_rectangle((cx-r*.81,cy-r*.81,cx+r*.81,cy+r*.81),radius=r*.09,outline=acc,width=max(3,w//2))
        d.line((cx+r*.96,cy-r*.55,cx+r*1.22,cy-r*.55,cx+r*1.22,cy-r*.24),fill=black,width=max(3,w//2))
    elif k=='HEX-HINGE':
        pts=[(cx+r*math.cos(math.pi/3*i+math.pi/6),cy+r*math.sin(math.pi/3*i+math.pi/6)) for i in range(6)]
        d.polygon(pts,fill='#d9eee9');d.line(pts+[pts[0]],fill=black,width=w,joint='curve')
        d.ellipse((cx-r*1.13,cy-r*.34,cx-r*.92,cy-r*.12),fill=acc,outline=black,width=max(2,w//3))
        d.line((cx-r*.6,cy-r*.22,cx+r*.5,cy+r*.22),fill=acc,width=max(2,w//3))
    else:
        if k=='OFFSET':
            ell((cx-r,cy-r*.85,cx+r*.55,cy+r*.85),fill='#d9ece8',outline=black,width=w)
            ell((cx+r*.1,cy-r*.56,cx+r*1.12,cy+r*.56),fill='#e9f4ec',outline=black,width=max(4,int(w*.75)))
            d.line((cx+r*.2,cy-r*.8,cx+r*.66,cy-r*.64),fill=acc,width=max(3,w//2))
        elif k=='SPLIT':
            ell((cx-r,cy-r,cx+r,cy+r),fill='#d7ece9',outline=black,width=w)
            d.arc((cx-r*.85,cy-r*.85,cx+r*.85,cy+r*.85),-80,85,fill=acc,width=max(4,w//2))
            d.polygon([(cx,cy-r*.46),(cx-r*.19,cy-r*.1),(cx+r*.19,cy-r*.1)],fill=acc)
            d.line((cx,cy-r*.08,cx,cy+r*.69),fill=black,width=max(3,w//3))
        else:
            ell((cx-r,cy-r,cx+r,cy+r),fill='#f4e7c5' if k=='AMBER IRIS' else '#e8f1e5',outline=black,width=w)
            ell((cx-r*.78,cy-r*.78,cx+r*.78,cy+r*.78),outline=acc,width=max(3,w//2))
            if k=='AMBER IRIS':
                for a in range(0,360,90):
                    ang=math.radians(a)
                    d.polygon([(cx,cy),(cx+math.cos(ang)*r*.55,cy+math.sin(ang)*r*.55),
                        (cx+math.cos(ang+.55)*r*.72,cy+math.sin(ang+.55)*r*.72)],fill='#d19c5a')
                ell((cx-r*.17,cy-r*.17,cx+r*.17,cy+r*.17),fill='#edf5e8')
            else: # CRESCENT: physically shuttering half the glass
                d.arc((cx-r*.65,cy-r*.65,cx+r*.65,cy+r*.65),105,255,fill=black,width=max(4,w//2))
                d.polygon([(cx-r*.45,cy-r*.34),(cx-r*.06,cy-r*.53),(cx-r*.08,cy+r*.51),(cx-r*.45,cy+r*.35)],fill='#8d7764')
    d.line((cx,cy+r*.95,cx+r*.17,cy+r*1.58),fill=black,width=max(6,int(w*.9)))
    d.rounded_rectangle((cx+r*.04,cy+r*1.5,cx+r*.29,cy+r*1.8),radius=r*.07,fill=acc,outline=black,width=max(2,w//3))

def person(c,view):
    """Hand-drawn, wardrobe-specific 2D angles; side is mirrored for right view."""
    im=Image.new('RGBA',(620*S,1120*S),(0,0,0,0));d=ImageDraw.Draw(im)
    def t(v):return tuple(round(q*S) for q in v)
    def p(pts,fill,outline=True,width=3):
        pts=[t(z) for z in pts];d.polygon(pts,fill=fill)
        if outline:d.line(pts+[pts[0]],fill=INK,width=width*S,joint='curve')
    def l(points,fill=INK,width=3):d.line([t(q) for q in points],fill=fill,width=width*S,joint='curve')
    def e(box,fill=None,outline=INK,width=3):d.ellipse(t(box),fill=fill,outline=outline,width=width*S)
    def rr(box,fill,rad=8,outline=INK,width=3):d.rounded_rectangle(t(box),radius=rad*S,fill=fill,outline=outline,width=width*S)
    skin=c['skin'];hair=c['hair'];coat=c['jacket'];shirt=c['inside'];acc=c['trim'];tr=c['pants'];style=c['shape'];b=c['body'];side=view=='side';back=view=='back';h=c['height']
    d.ellipse(t((125,1055,490,1082)),fill=(24,45,46,32))
    if side:
        # Left-facing real side silhouette, with distinct coat lengths & builds.
        e((240,984,335,1051),'#3a3433');e((305,984,403,1052),'#3a3433')
        p([(256,695),(321,695),(328,995),(264,997)],tr)
        p([(317,702),(370,702),(379,995),(326,995)],tr)
        hem={'bomber':686,'longcoat':900,'poncho':825,'vest':706,'tactical':686,'duster':931}[style]
        if style=='poncho':
            p([(249,339),(349,339),(415,409),(493,756),(380,826),(215,814),(148,754),(218,405)],coat)
        else:
            p([(232,352),(350,352),(408,408),(411,hem),(229,hem),(202,446)],coat)
            if style in ('longcoat','duster'):l([(301,660),(301,hem-10)],'#535258',2)
        # Arms, cuff and hand; use darker stitched panels for workwear.
        p([(244,373),(198,421),(153,577),(202,605),(297,471)],coat)
        p([(348,376),(413,424),(468,600),(426,617),(340,482)],coat)
        e((177,582,222,636),skin);e((416,599,465,651),skin)
        if style in ('bomber','tactical'):rr((209,626,407,648),acc,5)
        if style=='vest':
            p([(259,373),(356,373),(388,649),(253,653)],coat)
            l([(275,390),(338,663)],'#d6c39f',6)
        if style in ('duster','longcoat'):
            l([(355,420),(280,748)],acc,4)
        if style=='poncho':l([(192,675),(475,676)],acc,6)
        # Neck, forward-pointing nose, ear, angular brows.
        p([(278,305),(329,305),(333,364),(271,364)],skin)
        p([(259,151),(340,148),(376,204),(362,265),(330,318),(275,317),(229,286),(206,269),(232,249)],skin)
        e((337,225,362,257),skin)
        p([(256,164),(287,130),(352,154),(371,204),(347,194),(304,179),(263,198)],hair)
        e((264,232,274,242),INK,outline=None)
        l([(249,221),(279,219)],hair,5)
        if c['face'] in ('beard','whitebeard','moustache'):
            l([(233,284),(260,306),(299,319),(331,296)],hair,4)
        if c['face'] in ('spectacles','roundglasses'):
            e((234,219,278,254),None,acc,3);l([(277,232),(321,231)],acc,2)
        if c['hat']=='hood':
            p([(253,170),(246,120),(290,104),(371,139),(390,215),(361,230),(357,182),(285,151)],coat)
        if c['hat']=='beanie':
            e((247,109,379,212),coat);rr((245,183,379,210),acc,4)
        optic(d,147*S,497*S,45*S,c)
    else:
        # Distinct proportions; same back silhouette viewed from behind.
        spread=(b-1)*48;L=round(164-spread);R=round(458+spread)
        e((167,988,278,1054),'#3a3433');e((339,988,450,1054),'#3a3433')
        p([(202,686),(290,686),(277,1003),(205,1003)],tr)
        p([(325,686),(413,686),(415,1003),(337,1003)],tr)
        hem={'bomber':694,'longcoat':900,'poncho':821,'vest':704,'tactical':687,'duster':934}[style]
        if style=='poncho':
            p([(218,350),(401,350),(R+58,hem-40),(R-12,hem),(L+12,hem),(L-58,hem-40)],coat)
            l([(L-20,755),(R+20,755)],acc,6)
        else:
            p([(217,354),(405,354),(R,hem),(L,hem)],coat)
        if style in ('longcoat','duster'):
            l([(310,406),(310,hem-5)],INK,3)
            p([(L+12,633),(R-13,633),(R-9,653),(L+9,653)],acc)
        if style=='bomber':
            p([(L,664),(R,664),(R-10,700),(L+10,700)],acc)
            l([(L+52,404),(R-51,404)],'#3e4448',4)
        if style=='tactical':
            rr((L+25,484,L+90,568),acc,6);rr((R-90,484,R-25,568),acc,6)
            rr((L+18,672,R-18,694),INK,5)
        if style=='vest':
            # White rolled shirt sleeves plus dark teal waistcoat.
            p([(210,356),(139,395),(110,610),(169,636),(231,486)],shirt)
            p([(408,356),(479,395),(511,610),(452,636),(386,486)],shirt)
            p([(224,349),(394,349),(R-22,hem),(L+22,hem)],coat)
            l([(221,389),(312,529),(398,389)],acc,5)
        else:
            p([(217,365),(L-20,405),(L-45,604),(L+13,635),(244,480)],coat)
            p([(406,365),(R+20,405),(R+45,604),(R-13,635),(379,480)],coat)
        e((L-27,604,L+22,657),skin);e((R-24,604,R+28,657),skin)
        if not back:
            if style=='bomber':
                p([(260,360),(363,360),(375,670),(248,670)],shirt)
                l([(308,377),(310,677)],INK,4)
                rr((L+22,517,L+115,575),'#834b39',5)
            elif style=='vest':
                p([(257,356),(363,356),(386,665),(234,665)],shirt)
                p([(240,370),(274,362),(309,588),(309,687),(212,687)],coat)
                p([(379,370),(343,362),(312,588),(312,687),(408,687)],coat)
                for y in (481,547,615):e((310,y,321,y+11),acc,outline=None)
                l([(235,665),(387,665)],INK,5)
            elif style=='poncho':
                p([(270,340),(348,340),(398,637),(222,637)],shirt)
                l([(L+45,414),(R-40,683)],acc,12)
            elif style=='tactical':
                p([(264,355),(358,355),(380,667),(244,667)],shirt)
                l([(310,376),(311,673)],INK,5)
                rr((L+35,490,L+115,553),'#203741',5);rr((R-113,499,R-37,567),'#203741',5)
            else:
                p([(255,359),(365,359),(387,660),(233,660)],shirt)
                if style=='longcoat':
                    p([(213,361),(252,356),(283,503),(230,588)],coat)
                    p([(407,361),(368,356),(340,503),(389,588)],coat)
                    l([(297,385),(333,571)],acc,7)
                else:
                    p([(211,361),(250,353),(291,514),(234,631)],coat)
                    p([(408,361),(368,353),(330,514),(386,631)],coat)
                    l([(212,750),(407,750)],acc,5)
            if style in ('longcoat','duster'):l([(L+23,hem-53),(R-23,hem-53)],INK,3)
            if style=='vest':
                # Deliberately broad face and friendly stance.
                pass
        else:
            l([(231,405),(386,405)],acc,4)
            if style=='poncho':l([(311,414),(311,810)],INK,3)
        p([(280,306),(342,306),(346,365),(276,365)],skin)
        if back:
            e((231,141,392,319),hair)
            l([(247,291),(310,317),(375,292)],'#69716d',2)
        else:
            e((235,148,386,328),skin)
            e((228,231,245,267),skin);e((377,231,394,267),skin)
            p([(238,180),(254,149),(290,132),(359,147),(383,184),(358,176),(330,164),(307,183),(270,174),(239,203)],hair)
            for x in (270,349):
                l([(x-17,231),(x+17,230)],hair,4)
                e((x-4,247,x+4,258),INK,outline=None)
            l([(309,255),(299,277),(314,280)],'#885c45',2)
            l([(289,291),(309,295),(331,289)],'#81574b',2)
            if c['face'] in ('moustache','beard','whitebeard'):
                l([(282,280),(309,275),(337,281)],hair,5)
                if c['face']!='moustache':
                    l([(267,285),(275,315),(309,330),(347,313),(355,285)],hair,7)
            if c['face'] in ('spectacles','roundglasses'):
                if c['face']=='roundglasses':
                    e((249,226,300,274),None,acc,4);e((321,226,372,274),None,acc,4)
                else:
                    rr((246,226,298,268),None,7,acc,4);rr((323,226,375,268),None,7,acc,4)
                l([(299,244),(322,244)],acc,4)
        if c['hat']=='hood':
            p([(238,179),(243,121),(286,99),(352,110),(388,152),(394,213),(365,203),(362,175),(317,154),(263,177)],coat)
        if c['hat']=='beanie':
            e((227,97,397,232),coat);rr((225,181,399,220),acc,5)
        if not back:optic(d,(R+26)*S,504*S,47*S,c)
        else:optic(d,(R+16)*S,630*S,32*S,c)
        # Style-specific extras visible on all angles.
        if style=='duster' and not back: l([(256,338),(293,394),(338,354)],acc,13)
        if style=='longcoat' and not back: rr((L+7,737,L+75,821),'#382b43',7)
    if h<1: # compact character has more room above; relative anatomy already distinctive
        pass
    return im.resize((620,1120),Image.Resampling.LANCZOS)

def sheet(c):
    W,H=3600,1980
    im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,255),fill=INK)
    d.text((76,28),f"{c['id']}  /  {c['name']}",font=ft(BOLD,123),fill=WHITE)
    d.text((79,179),c['role'].upper(),font=ft(BODY,37),fill=c['trim'])
    d.text((2890,112),'NEW MALE DETECTIVE  /  STUDY',font=ft(BODY,31),fill='#d7e1d9')
    for i,(label,view) in enumerate([('FRONT','front'),('LEFT','side'),('BACK','back'),('RIGHT','right')]):
        x=65+i*643;y=300;cw=600;ch=1330
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=22,fill=WHITE,outline='#d3d8d0',width=3)
        ai=None;flip=False
        if view=='front':ai=ROOT/'references'/f"{c['id']}_{c['name'].lower()}_solo.png"
        elif c['id']=='11':
            ai=ROOT/'angles'/f"11_{label.lower()}.png"
            # Model returned right-facing for both side prompts; mirror one.
            flip=(label=='LEFT')
        elif c['id']=='12' and label=='LEFT':ai=ROOT/'angles'/'12_left.png'
        if ai and ai.exists():
            src=Image.open(ai).convert('RGB')
            if flip:src=ImageOps.mirror(src)
            src=ImageOps.contain(src,(560,1050),Image.Resampling.LANCZOS)
            im.paste(src,(x+(cw-src.width)//2,y+52+(1050-src.height)//2))
            kind='AI CONCEPT ANGLE'
        else:
            v=person(c,'side' if view=='right' else view)
            if view=='right':v=ImageOps.mirror(v)
            v=v.resize((578,1045),Image.Resampling.LANCZOS)
            im.paste(v,(x+10,y+55),v)
            kind='SCHEMATIC VIEW GUIDE'
        d.line((x+33,y+1139,x+cw-33,y+1139),fill='#d1d7ce',width=3)
        d.text((x+35,y+1146),label,font=ft(BOLD,73),fill=INK)
        d.text((x+37,y+1241),kind,font=ft(BODY,26),fill='#566466')
    x=2644;y=300;cw=890;ch=1330
    d.rounded_rectangle((x,y,x+cw,y+ch),radius=22,fill='#e3e9df',outline='#c4d3c6',width=3)
    d.text((x+55,y+58),'SIGNATURE LENS',font=ft(BOLD,90),fill=INK)
    optic(d,x+434,y+539,201,c)
    d.line((x+55,y+1035,x+cw-55,y+1035),fill='#b3c5bd',width=3)
    d.text((x+56,y+1073),c['optic'],font=ft(BOLD,80),fill=INK)
    for i,color in enumerate((c['skin'],c['jacket'],c['inside'],c['trim'])):
        d.rounded_rectangle((x+60+i*197,y+1210,x+214+i*197,y+1262),radius=9,fill=color)
    d.rounded_rectangle((65,1684,3534,1897),radius=22,fill='#e1e6dc')
    d.text((106,1706),c['lensnote'],font=ft(BOLD,63),fill=INK)
    d.text((110,1794),c['tag'],font=ft(BODY,34),fill='#4a5d5e')
    d.text((110,1842),'AI hero with angle studies; schematic guides are approximate, not exact matched turnarounds.',font=ft(BODY,24),fill='#536666')
    d.text((2649,1850),'NEW OPTION / NOT APPROVED',font=ft(BODY,26),fill=INK)
    out=ROOT/f"{c['id']}_{c['name']}_ALL_VIEWS.png";im.save(out,optimize=True)
    return out

def overview(paths):
    W,H=2400,2260;im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,251),fill=INK)
    d.text((85,25),'SIX FRESH DETECTIVES',font=ft(BOLD,121),fill=WHITE)
    d.text((86,174),'Each numbered image: front / left / back / right + one unique magnifier',font=ft(BODY,37),fill='#dce7df')
    for i,(c,path) in enumerate(zip(DATA,paths)):
        x=78+(i%2)*1150;y=292+(i//2)*625
        d.rounded_rectangle((x,y,x+1088,y+575),radius=25,fill=WHITE,outline='#d3d8d0',width=3)
        src=Image.open(path)
        # Preview hero, side and lens in each tile; the individual sheet has all 4 views.
        front=src.crop((65,300,665,1415));front.thumbnail((340,430),Image.Resampling.LANCZOS)
        side=src.crop((708,300,1308,1415));side.thumbnail((300,430),Image.Resampling.LANCZOS)
        lens=src.crop((2644,300,3534,1630));lens.thumbnail((290,425),Image.Resampling.LANCZOS)
        im.paste(front,(x+21,y+91));im.paste(side,(x+365,y+91));im.paste(lens,(x+749,y+91))
        d.text((x+29,y+20),f"{c['id']}  {c['name']}",font=ft(BOLD,67),fill=INK)
        d.text((x+34,y+525),c['role'].upper(),font=ft(BODY,29),fill='#536666')
    d.text((85,2190),'Six distinctive male detective proposals / AI front hero + labeled view studies / choose one to refine.',font=ft(BODY,34),fill='#576766')
    out=ROOT/'00_COMPARE_SIX_FRESH_OPTIONS.png';im.save(out,optimize=True)
    return out

if __name__=='__main__':
    paths=[sheet(c) for c in DATA]
    overview(paths)
    for p in paths:print(p.name,p.stat().st_size)

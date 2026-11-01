#!/usr/bin/env python3
"""Compose the user's third 2D character (19 Finch) and three one-image intro storyboards."""
from pathlib import Path
import textwrap
from PIL import Image,ImageDraw,ImageFont,ImageOps

ROOT=Path(__file__).resolve().parent
FONT=ROOT.parent/'assets'/'fonts'
HEAD=FONT/'Anton-Regular.ttf';BODY=FONT/'DMSans.ttf'
INK='#142b2e';PAPER='#f4f1e8';WHITE='#fffdf5';TEAL='#3f9996';MUTED='#59696a';COPPER='#b7754b'

VARIANTS=[
 {'id':'A','name':'THE MISSING PAGE','scene':'scene_a_archive.png','setting':'RAINY ARCHIVE / TORN CASE FILE','evidence':'A paper fiber reveals a moved page','line':'The page is gone. The mark isn\'t.','beats':['Empty drawer + torn file','Raises the oval lens','Paper fiber comes into focus','Looks up / lens wipe'], 'prompt':'A 4.8-second vertical 9:16 identity intro set in a fictional rain-dark archive. Begin on an open drawer and torn case file. The same freckled ginger detective in his petrol-teal tailored coat raises the oval copper dual-loupe magnifier. Cut to a tiny paper fiber entering focus; no magical effect. He looks up as the physical lens wipes into the next case shot. Spoken line: “The page is gone. The mark isn’t.” Natural rain, paper and one focus click; no music or on-screen subtitles.'},
 {'id':'B','name':'THE FALSE TRAIL','scene':'scene_b_street.png','setting':'WET STREET / TWO SHOE IMPRESSIONS','evidence':'Two wet tracks diverge outside a doorway','line':'Two tracks. One false trail.','beats':['Rain street + doorway','Detective checks the ground','Two shoe impressions sharpen','Looks up / lens wipe'], 'prompt':'A 4.8-second vertical 9:16 identity intro at a fictional wet-street crime scene. Open on a lamp-lit doorway and two shoe impressions. Preserve the same handsome ginger detective, fitted petrol-teal coat, copper scarf and oval copper flip-loupe lens. Show a new crouching pose, then a close evidence insert through the real lens as the two tracks diverge. He turns toward camera; the oval lens wipes to the first case frame. Spoken line: “Two tracks. One false trail.” Rain, soft step and focus click only; no music, injury or subtitles.'},
 {'id':'C','name':'THE BROKEN SEAL','scene':'scene_c_envelope.png','setting':'EVIDENCE ROOM / OPENED ENVELOPE','evidence':'A crease crosses the disturbed wax seal','line':'The seal was opened twice.','beats':['Envelope under desk lamp','Turns the focus wheel','Crease through wax seal appears','Looks up / lens wipe'], 'prompt':'A 4.8-second vertical 9:16 identity intro in a fictional quiet evidence room. The same freckled ginger detective in his tailored petrol-teal coat and satchel finds a broken wax seal on an envelope. Show a fresh careful pose turning the teal focus dial of his functional oval copper magnifier; a crease at the seal becomes visible through normal optical focus. He glances at us and the lens wipes to the first case shot. Spoken line: “The seal was opened twice.” Paper and metal foley, no music, no gore and no on-screen subtitles.'},
]

def ft(path,size):return ImageFont.truetype(str(path),size)

def crop_person(img):
    im=img.convert('RGB');t=im.resize((im.width//3,im.height//3));px=t.load();points=[]
    for y in range(t.height):
        for x in range(t.width):
            r,g,b=px[x,y]
            if min(r,g,b)<168:points.append((x,y))
    if not points:return im
    box=(max(0,(min(x for x,y in points)-7)*3),max(0,(min(y for x,y in points)-7)*3),min(im.width,(max(x for x,y in points)+8)*3),min(im.height,(max(y for x,y in points)+8)*3))
    return im.crop(box)

def contain_paste(out,src,box):
    x,y,w,h=box;src=ImageOps.contain(src.convert('RGB'),(w,h),Image.Resampling.LANCZOS)
    out.paste(src,(x+(w-src.width)//2,y+(h-src.height)//2))

def fit_paste(out,src,box,centering=(.5,.5)):
    x,y,w,h=box;src=ImageOps.fit(src.convert('RGB'),(w,h),Image.Resampling.LANCZOS,centering=centering)
    out.paste(src,(x,y))

def character_sheet():
    W,H=4800,2670;im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,310),fill=INK)
    d.text((90,27),'19 / FINCH  •  REFINED',font=ft(HEAD,142),fill=WHITE)
    d.text((95,207),'STYLISH DETECTIVE OUTFIT   /   FOUR VIEWS   /   SIGNATURE OVAL LENS',font=ft(BODY,44),fill='#b6d9d1')
    views=[('FRONT / 3⁄4','front.png'),('LEFT PROFILE','left.png'),('DIRECT BACK','back.png'),('RIGHT PROFILE','right.png')]
    x0=82;cw=850;gap=26;top=360;bottom=2185
    for i,(label,file) in enumerate(views):
        x=x0+i*(cw+gap)
        d.rounded_rectangle((x,top,x+cw,bottom),radius=27,fill=WHITE,outline='#d4d9d0',width=4)
        source=crop_person(Image.open(ROOT/'art'/file))
        contain_paste(im,source,(x+18,top+55,cw-36,1590))
        d.line((x+39,bottom-173,x+cw-39,bottom-173),fill='#d6d9cf',width=3)
        d.text((x+40,bottom-150),label,font=ft(HEAD,66),fill=INK)
        d.text((x+43,bottom-62),'REFERENCE-GUIDED AI CONCEPT VIEW',font=ft(BODY,25),fill=MUTED)
    x=3595;w=1124
    d.rounded_rectangle((x,top,x+w,bottom),radius=27,fill='#e4ebe2',outline='#cad8ce',width=4)
    d.text((x+52,top+49),'THE FINCH LENS',font=ft(HEAD,92),fill=INK)
    d.text((x+57,top+184),'OVAL OPTIC  /  HINGED MICRO LOUPE',font=ft(BODY,34),fill='#397a76')
    contain_paste(im,Image.open(ROOT/'art'/'lens_macro.png'),(x+54,top+253,w-108,1019))
    d.line((x+57,top+1355,x+w-57,top+1355),fill='#bdcfc2',width=4)
    for j,(head,body) in enumerate([
        ('FRAME','Antique copper, engraved double rim'),
        ('EXTRA','Flip-up round loupe above oval glass'),
        ('CONTROL','Petrol-teal knurled focus wheel'),
        ('GRIP','Polished dark walnut handle')]):
        yy=top+1396+j*112
        d.text((x+65,yy),head,font=ft(HEAD,39),fill=INK)
        d.text((x+65,yy+47),body,font=ft(BODY,30),fill=MUTED)
    d.rounded_rectangle((82,2232,4718,2590),radius=25,fill='#dfe7dd')
    d.text((126,2253),'CHARACTER LOCK / COPY INTO ALL THREE INTRO PROMPTS',font=ft(HEAD,65),fill=INK)
    d.text((128,2354),'Freckled ginger male detective  •  teal eyes  •  small ginger moustache  •  warm expressive 2D face',font=ft(BODY,38),fill='#405858')
    d.text((128,2424),'Tailored petrol-teal coat + storm yoke  •  cocoa waistcoat  •  copper scarf  •  charcoal trousers',font=ft(BODY,37),fill='#405858')
    d.text((128,2500),'Concept angles: minor satchel / loupe details may drift; standardize before animation. No channel name approved.',font=ft(BODY,30),fill=MUTED)
    out=ROOT/'00_FINCH_REFINED_CHARACTER_SHEET.png';im.save(out,optimize=True);return out

def wrap(draw,text,font_,max_width):
    words=text.split();lines=[];current=''
    for word in words:
        candidate=(current+' '+word).strip()
        if draw.textbbox((0,0),candidate,font=font_)[2]>max_width and current:
            lines.append(current);current=word
        else:current=candidate
    if current:lines.append(current)
    return lines

def storyboard(v):
    W,H=3600,2350;im=Image.new('RGB',(W,H),PAPER);d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,276),fill=INK)
    d.text((73,26),f"INTRO {v['id']}  /  {v['name']}",font=ft(HEAD,113),fill=WHITE)
    d.text((80,191),'ONE-IMAGE SCENE SHEET  •  FICTIONAL 2D IDENTITY INTRO  •  4.8 SECONDS',font=ft(BODY,32),fill='#c8dfd8')
    xs=[65,940,1815,2690];w=845;top=315;h=1395
    times=['00:00–00:01.0','00:01.0–00:02.3','00:02.3–00:03.6','00:03.6–00:04.8']
    scene=Image.open(ROOT/'art'/v['scene']).convert('RGB')
    focus=Image.open(ROOT/'art'/'pose_reveal.png').convert('RGB')
    reveal=Image.open(ROOT/'art'/'pose_focus.png').convert('RGB')
    lens=Image.open(ROOT/'art'/'lens_macro.png').convert('RGB')
    for i,x in enumerate(xs):
        d.rounded_rectangle((x,top,x+w,top+h),radius=21,fill=WHITE,outline='#d1d8d0',width=3)
        box=(x+20,top+20,w-40,1130)
        if i==0:contain_paste(im,scene,box)
        elif i==1:fit_paste(im,focus,box,(.53,.5))
        elif i==2:
            # Evidence-specific insert, with the finish-target lens inset.
            crop=scene.crop((0,round(scene.height*.52),scene.width,scene.height))
            fit_paste(im,crop,box,(.5,.5))
            inset=ImageOps.contain(lens,(320,320),Image.Resampling.LANCZOS)
            ix=x+w-inset.width-30;iy=top+32
            d.rounded_rectangle((ix-10,iy-10,ix+inset.width+10,iy+inset.height+10),radius=17,fill=WHITE,outline=COPPER,width=8)
            im.paste(inset,(ix,iy))
        else:fit_paste(im,reveal,box,(.52,.5))
        d.line((x+26,top+1180,x+w-26,top+1180),fill='#d1d9d0',width=3)
        d.text((x+30,top+1195),times[i],font=ft(HEAD,42),fill=TEAL)
        d.text((x+31,top+1261),v['beats'][i],font=ft(BODY,30),fill=INK)
    d.rounded_rectangle((65,1743,3535,2293),radius=23,fill='#e1e9df')
    d.text((104,1763),f"DIALOGUE  /  “{v['line']}”",font=ft(HEAD,55),fill=INK)
    d.text((108,1842),v['setting']+'  •  '+v['evidence'],font=ft(BODY,31),fill='#436261')
    d.line((105,1909,3493,1909),fill='#c1cec2',width=3)
    d.text((106,1932),'COPY-READY VIDEO PROMPT',font=ft(HEAD,48),fill=INK)
    prompt_font=ft(BODY,27)
    lines=wrap(d,v['prompt'],prompt_font,3300)
    for j,line in enumerate(lines[:5]):d.text((109,2000+j*47),line,font=prompt_font,fill='#465c5b')
    d.text((2480,2250),'STORYBOARD / NOT A GENERATED CLIP',font=ft(BODY,24),fill=INK)
    out=ROOT/f"INTRO_{v['id']}_{v['name'].replace(' ','_')}_SCENE_SHEET.png";im.save(out,optimize=True);return out

if __name__=='__main__':
    paths=[character_sheet(),*(storyboard(v) for v in VARIANTS)]
    for p in paths:print(p.name,p.stat().st_size)

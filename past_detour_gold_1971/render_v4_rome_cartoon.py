"""Rome-V10-inspired original 2D CARTOON action edit for Past Detour.

Uses 10 new hand-inked cartoon paintings and three matched acting-pose pairs,
not the rejected realistic V3 paintings or static V2 vector puppets. Every
scene has timed character/object action, motivated reframing, or animated map.
Roman characters, imagery and audio are NEVER included in this render.

Run: .venv/bin/python past_detour_gold_1971/render_v4_rome_cartoon.py --stills
     .venv/bin/python past_detour_gold_1971/render_v4_rome_cartoon.py --render
"""
from __future__ import annotations
import argparse,hashlib,json,math,subprocess,wave
from pathlib import Path
import cv2,imageio_ffmpeg,numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont

ROOT=Path(__file__).resolve().parent
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,SR=720,1280,60,24000
FONT=ROOT/'v3_fonts/Cinzel.ttf'
IVORY=(254,241,214);GOLD=(239,180,86);RED=(188,72,48);NAVY=(12,20,33)
TIMELINE=json.loads((ROOT/'v3_timeline.json').read_text());DURATION=51.41

def ease(x):x=max(0,min(1,x));return x*x*(3-2*x)
def c(x):return max(0,min(1,x))

def load(path):
    im=Image.open(path).convert('RGB');w,h=im.size
    # 768x1376 source art -> true 9:16 framing, then animation canvas
    h2=min(h,int(w*16/9));im=im.crop((0,(h-h2)//2,w,(h+h2)//2))
    return im.resize((W,H),Image.Resampling.LANCZOS)
ART={p.stem:load(p) for p in (ROOT/'v4_assets').glob('*.png')}
F=lambda s:ImageFont.truetype(str(FONT),s)


def localized(im,t,regions):
    """Cel deformation localized to limbs/heads, stable inked background.
    regions are (x,y,rx,ry,dx,dy,phase); no overall rubber-sheet wobble.
    """
    arr=np.asarray(im); yy,xx=np.indices((H,W),dtype=np.float32)
    mx=xx.copy();my=yy.copy()
    for x,y,rx,ry,dx,dy,phase in regions:
        envelope=np.exp(-2.9*(((xx-x)/rx)**2+((yy-y)/ry)**2))
        s=math.sin(t*phase)
        mx-=dx*s*envelope;my-=dy*s*envelope
    result=cv2.remap(arr,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return Image.fromarray(result)


def shot(im,z=1,cx=360,cy=640):
    if z==1:return im.copy()
    cw=int(W/z);ch=int(H/z)
    x=max(0,min(W-cw,int(cx-cw/2)));y=max(0,min(H-ch,int(cy-ch/2)))
    return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.Resampling.BICUBIC)


def spark(d,x,y,r=11,col=GOLD):
    d.line((x-r,y,x+r,y),fill=col,width=3)
    d.line((x,y-r,x,y+r),fill=col,width=3)
    d.ellipse((x-3,y-3,x+3,y+3),fill=IVORY)

def bill(im,x,y,scale=1,ang=0):
    # Original moving drawn prop, deliberately stylized rather than copied USD.
    w=int(112*scale);h=int(59*scale)
    p=Image.new('RGBA',(w+14,h+14),(0,0,0,0));d=ImageDraw.Draw(p)
    d.rounded_rectangle((7,7,w+7,h+7),radius=4,fill='#adc0a1',outline='#172a24',width=4)
    d.rectangle((17,14,w-3,h),outline='#3c5a44',width=2)
    d.ellipse((w*.42,h*.19,w*.70,h*.92),fill='#819e7a',outline='#17342d',width=2)
    d.text((w*.49,h*.31),'$',font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',max(12,int(25*scale))),fill='#25422f')
    p=p.rotate(ang,resample=Image.Resampling.BICUBIC,expand=True)
    im.paste(p,(round(x-p.width/2),round(y-p.height/2)),p)

def bar(im,x,y,scale=1):
    w=round(104*scale);h=round(42*scale)
    d=ImageDraw.Draw(im)
    poly=[(x-w//2,y),(x+w//2,y),(x+w//2-9,y+h),(x-w//2+9,y+h)]
    d.polygon(poly,fill='#9b5924',outline='#563619')
    d.polygon([(x-w//2,y),(x-w//2+9,y-20*scale),(x+w//2-9,y-20*scale),(x+w//2,y)],fill='#f0bf56',outline='#5f3b1e')
    d.line((x-w//2+14,y-5,x+w//2-14,y-5),fill='#fff1a9',width=2)

def text(d,top,bottom,t,y=92,emph=False):
    a=ease((t-.03)/.33)
    if not a:return
    x=int(58-18*(1-a))
    if top:
        d.text((x,y),top,font=F(23),fill=IVORY,stroke_width=3,stroke_fill=NAVY)
    size=56 if not emph else 64
    while d.textbbox((0,0),bottom,font=F(size))[2]>W-100:size-=2
    dy=int((1-a)*-12)
    d.text((x+3,y+46+dy+4),bottom,font=F(size),fill=NAVY,stroke_width=6,stroke_fill=NAVY)
    d.text((x,y+46+dy),bottom,font=F(size),fill=GOLD if emph else IVORY,stroke_width=2,stroke_fill=NAVY)

def shutters(im,t,at):
    """3-frame editorial action wipe; hides a drawing pose switch on impact."""
    distance=abs(t-at)
    if distance>.075:return im
    p=1-distance/.075
    overlay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(overlay,'RGBA')
    for k in range(4):
        y=150+k*260+int(math.sin(t*26+k)*24)
        d.line((35,y,W-35,y-18),fill=(255,230,175,int(92*p)),width=max(1,int(5*p)))
    return Image.alpha_composite(im.convert('RGBA'),overlay).convert('RGB')

def door_motion(im,t):
    # Door cel is taken from the generated *closed* frame, with the banker's
    # silhouette excluded so he doesn't double before the actor's pose cut.
    if t<1.0 or t>=2.8:return im
    p=ease((t-1.0)/1.8)
    closed=ART['01_vault_closed'].copy()
    # Repair the overlapping acting-pose hand inside the moving door cel with
    # matching metal texture; the banker's pose itself changes on impact.
    closed.paste(closed.crop((505,617,573,813)),(425,617))
    layer=Image.new('RGBA',(W,H),(0,0,0,0));mask=Image.new('L',(W,H),0);d=ImageDraw.Draw(mask)
    d.rectangle((425,292,740,1075),fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(3))
    cel=closed.convert('RGBA');cel.putalpha(mask)
    x=int(160*(1-p))
    layer.alpha_composite(cel,(x,0))
    return Image.alpha_composite(im.convert('RGBA'),layer).convert('RGB')


def scene(mode,t,dur):
    if mode=='vault':
        # three real editorial camera set-ups: opening, door impact, reaction
        if t<2.8:
            base=ART['01_vault_open']
            im=shot(base,1.0 if t<1.4 else 1.06,360 if t<1.4 else 451,670)
            im=door_motion(im,t)
            im=localized(im,t,[(212,900,180,200,6,9,4.0)])
        else:
            base=ART['01_vault_closed']
            im=shot(base,1.0 if t<4.35 else 1.14,360 if t<4.35 else 245,670)
            im=localized(im,t,[(181,901,200,225,4,9,4.1)])
        d=ImageDraw.Draw(im);text(d,'ON A SUNDAY NIGHT','THE GOLD WINDOW',t,emph=True)
        if t>1.9 and t<3.2:
            for j in range(3):spark(d,512+j*23,681+j*30,9)
    elif mode=='promise':
        base=ART['02_bretton_agreement']
        im=shot(base,1.0 if t<1.8 else 1.13,360 if t<1.8 else 383,660 if t<1.8 else 805)
        im=localized(im,t,[(285,929,200,184,7,14,4.3),(575,430,120,110,2,4,2.4)])
        d=ImageDraw.Draw(im)
        if t>1.2:
            p=ease((t-1.2)/(dur-1.5))
            # Ink signature grows across the agreement, with the pen in contact.
            d.arc((308,902,500,1045),15,15+int(p*118),fill='#57402d',width=3)
            if p>.75:spark(d,540,493,13)
        text(d,'BRETTON WOODS  /  1944','THE PROMISE',t)
    elif mode=='exchange':
        second=t>3.2
        base=ART['03_gold_handoff' if second else '03_foreign_official_exchange']
        im=shot(base,1.0 if t<1.7 else (1.10 if t<3.2 else 1.13),360 if t<1.7 else 422,725)
        im=localized(im,t,[(403,665,130,140,8,7,5.3),(524,733,158,165,7,4,4.3)])
        if t<3.2:
            p=ease((t-.5)/2.3)
            bill(im,328+136*p,713-26*p,.54,-14+int(15*p))
        else:
            if t<3.75:im=shutters(im,t,3.2)
            if t>3.5 and int(t*4)%3==0:
                d=ImageDraw.Draw(im);spark(d,387,659,10)
        d=ImageDraw.Draw(im);text(d,'FOREIGN GOVERNMENTS ONLY','$35 AN OUNCE',t)
    elif mode=='ocean':
        base=ART['04_dollars_overseas']
        im=shot(base,1.0 if t<1.3 else 1.1,360 if t<1.3 else 467,641)
        im=localized(im,t,[(430,667,177,173,8,12,4.3),(578,855,160,170,5,8,3.3)])
        for j in range(4):
            p=c((t-.15-j*.45)/(dur-.40))
            if p<=0 or p>=1:continue
            bill(im,127+579*p,971-485*p-65*math.sin(p*math.pi),.42,-11+int(27*p))
        d=ImageDraw.Draw(im)
        text(d,'THE PRESSURE BUILDS','DOLLARS CROSS OCEANS',t)
    elif mode=='shortfall':
        base=ART['05_gold_shortfall']
        im=shot(base,1.0 if t<2.0 else 1.12,360 if t<2 else 282,700)
        im=localized(im,t,[(348,846,175,174,5,9,5.1)])
        for j in range(8):
            p=c((t-j*.27)/(dur-j*.27))
            if p<=0:continue
            bill(im,107+39*j,399+24*j-115*(1-ease(p)),.43,(-1)**j*8)
        d=ImageDraw.Draw(im)
        text(d,'THE FIXED PRICE','MORE DOLLARS. LESS GOLD.',t)
        if t>dur*.50:
            # Explanatory in-scene comparison, not a generic footer card.
            d.line((400,1126,400+round(231*ease((t-dur*.50)/(dur*.46))),1126),fill=(192,80,63),width=11)
            d.line((400,1151,400+round(86*ease((t-dur*.50)/(dur*.46))),1151),fill=GOLD,width=10)
    elif mode=='tv':
        # 9-second narration uses FIVE clear Rome-like editorial beats.
        beats=[0,1.9,4.1,6.15,7.65,dur]
        q=next((i for i in range(5) if t<beats[i+1]),4)
        source='06_tv_speaks' if q in [2,4] else '06_tv_announcement'
        base=ART[source]
        if q==0:im=shot(base,1.0,360,640)
        elif q==1:im=shot(base,1.28,265,700)  # viewer reaction
        elif q==2:im=shot(base,1.31,553,706)  # speaker on television
        elif q==3:im=shot(base,1.0,360,640)
        else:im=shot(base,1.16,554,722)
        im=localized(im,t,[(156,846,194,214,6,9,4.2),(554,789,125,125,3,5,5.0)])
        d=ImageDraw.Draw(im)
        text(d,'AUGUST 15, 1971','"TEMPORARY"',t,emph=True)
        if q in [2,4]:
            # A restrained traveling scan on the period TV, not archival footage.
            scan=717+int((t*105)%228)
            d.line((480,scan,708,scan),fill=(221,226,219),width=2)
        for at in beats[1:-1]:
            if abs(t-at)<.07:im=shutters(im,t,at)
    elif mode=='float':
        base=ART['07_rates_float']
        # Four contrasting action inserts: map -> running trader -> snapped chain -> reaction.
        if t<2.0:im=shot(base,1.43,450,360)
        elif t<4.2:im=shot(base,1.0,360,640)
        elif t<6.35:im=shot(base,1.38,575,797)
        else:im=shot(base,1.26,332,843)
        im=localized(im,t,[(356,889,235,188,10,15,4.1),(600,732,170,175,9,11,4.9)])
        d=ImageDraw.Draw(im)
        p=ease((t-.55)/(dur*.78))
        # Two truly independent rate curves traverse the map; broken fixed peg
        # scatters sparks while the running trader responds.
        if p>0 and t<2.1:
            d.line((70,380,70+int(520*p),280-int(43*math.sin(t*2.1))),fill=(244,197,94),width=5)
            d.line((90,466,90+int(496*p),495+int(40*math.sin(t*1.8))),fill=(198,71,54),width=5)
        # The source painting already contains flying paper; don't overlay
        # geometric scraps on the actor's face or animated world map.
        if 3.9<t<4.8:
            for j in range(3):spark(d,519+j*21,656-j*22,9)
        text(d,'BY 1973','CURRENCIES FLOAT',t)
    elif mode=='never':
        base=ART['01_vault_closed']
        if t<1.5:im=shot(base,1.47,590,708)  # immovable lock
        elif t<3.1:im=shot(base,1.43,225,877) # human reaction
        else:im=shot(base,1.0,360,640)        # consequence
        im=localized(im,t,[(530,840,180,170,8,3,4.4)])
        d=ImageDraw.Draw(im)
        text(d,'THE WORD WAS','"TEMPORARY"',t,emph=True)
        if t>1.8:
            d.text((64,1093),'IT NEVER REOPENED.',font=F(35),fill=GOLD,stroke_width=3,stroke_fill=NAVY)
            for j in range(3):spark(d,594+j*19,631+j*19,9)
    else:
        # Original animated verdict scale: character comeback and a gold/dollar
        # balance, echoing Rome V10's dramatic finale without reusing its art.
        if t<2.25:
            im=Image.new('RGB',(W,H),(13,19,31));d=ImageDraw.Draw(im)
            for j in range(22):
                th=j*math.tau/22+t*.05
                x=360+math.cos(th)*1040;y=650+math.sin(th)*1040
                d.line((360,650,x,y),fill=(34,33,42),width=2)
            for k in range(22):
                x=(k*91+int(t*23))%W;y=(k*197+int(t*43))%H
                d.ellipse((x,y,x+2,y+2),fill=(115,82,53))
        else:
            bg=shot(ART['01_vault_closed'],1.08,322,767)
            im=Image.blend(bg,Image.new('RGB',(W,H),(9,15,26)),.34)
        d=ImageDraw.Draw(im)
        tilt=ease((t-.45)/2.9);theta=-.16+.58*tilt
        # Balance enters from the lower edge, settles, then tips.
        entrance=1-ease((t-.25)/1.2)
        cx=500;cy=704+int(210*entrance)
        d.rounded_rectangle((cx-17,cy-121,cx+17,cy+315),radius=9,fill='#704d31',outline=GOLD,width=5)
        d.polygon([(cx,cy-153),(cx-42,cy-116),(cx+42,cy-116)],fill=GOLD,outline=NAVY)
        d.ellipse((cx-24,cy-62,cx+24,cy-14),fill=GOLD,outline=NAVY,width=4)
        lx=cx-int(151*math.cos(theta));ly=cy-int(151*math.sin(theta))
        rx=cx+int(151*math.cos(theta));ry=cy+int(151*math.sin(theta))
        d.line((lx,ly,rx,ry),fill=NAVY,width=25);d.line((lx,ly,rx,ry),fill=GOLD,width=13)
        for x,y in [(lx,ly),(rx,ry)]:
            d.ellipse((x-11,y-11,x+11,y+11),fill=GOLD,outline=NAVY,width=3)
            d.line((x,y+8,x,y+125),fill=GOLD,width=5)
            d.arc((x-71,y+107,x+71,y+164),2,178,fill=GOLD,width=7)
        bill(im,lx,ly+122,1.08,-int(theta*17));bar(im,rx,ry+117,.93)
        d=ImageDraw.Draw(im)
        if tilt>.56:
            bx=cx+int(49*tilt);by=cy-int(29*tilt)
            d.line((cx,cy,bx-9,by-10),fill=GOLD,width=5)
            d.line((bx+13,by+13,bx+34,by+36),fill=GOLD,width=5)
            spark(d,bx,by,12)
        text(d,'THE DOLLAR SURVIVED.','THE RULES CHANGED.',t,emph=True)
        if t>dur-2.2:
            d.text((57,1115),'WOULD YOU HAVE SEEN IT?',font=F(38),fill=IVORY,stroke_width=3,stroke_fill=NAVY)
            d.text((60,1220),'PAST DETOUR',font=F(28),fill=GOLD,stroke_width=2,stroke_fill=NAVY)
    return im


def make_audio():
    with wave.open(str(ROOT/'v3_master_audio.wav'),'rb') as wav:
        raw=np.frombuffer(wav.readframes(wav.getnframes()),'<i2').copy();assert wav.getframerate()==SR
    mix=raw.astype('float32');rng=np.random.default_rng(45197)
    def foley(sec,amp=850,hz=94):
        n=int(.33*SR);at=int(sec*SR)
        if at<0 or at+n>len(mix):return
        x=np.arange(n)/SR;noise=rng.normal(0,1,n)
        smooth=np.convolve(noise,np.ones(11)/11,'same')
        fx=(.7*np.sin(2*np.pi*(hz*x-17*x*x))+.3*smooth)*np.exp(-16*x)
        mix[at:at+n]+=fx*amp
    for mode,offsets in [('vault',[.12,2.81]),('promise',[1.7]),('exchange',[3.19]),
                         ('ocean',[.22]),('shortfall',[2.1]),('tv',[.2,4.1,7.65]),
                         ('float',[.5]),('never',[1.8]),('legacy',[.12])]:
        s=next(q for q in TIMELINE if q['mode']==mode)
        for offset in offsets:foley(s['start']+offset)
    mix=np.clip(mix,-30500,30500).astype('<i2')
    with wave.open(str(ROOT/'v4_audio.wav'),'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(SR);wav.writeframes(mix.tobytes())


def main():
    p=argparse.ArgumentParser();p.add_argument('--stills',action='store_true');p.add_argument('--render',action='store_true')
    args=p.parse_args();make_audio()
    def frame(sec):
        s=next((item for item in TIMELINE if sec<item['end']),TIMELINE[-1])
        return scene(s['mode'],max(0,sec-s['start']),max(.1,s['end']-s['start']))
    if args.stills:
        folder=ROOT/'v4_review';folder.mkdir(exist_ok=True)
        for j,s in enumerate(TIMELINE):
            for q in (.16,.50,.83):
                sec=s['start']+(s['end']-s['start'])*q
                frame(sec).save(folder/f'{j+1:02d}_{int(q*100)}.jpg',quality=91)
        print('saved storyboard review',flush=True)
    if args.render:
        path=ROOT/'Past_Detour_1971_Gold_Window_ROME_STYLE_V4.mp4'
        proc=subprocess.Popen([FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
           '-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i',str(ROOT/'v4_audio.wav'),
           '-filter:v','scale=1080:1920:flags=lanczos','-map','0:v:0','-map','1:a:0',
           '-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',
           '-c:a','aac','-ac','2','-b:a','192k','-movflags','+faststart','-shortest',str(path)],stdin=subprocess.PIPE)
        count=math.ceil(DURATION*FPS)
        try:
            for i in range(count):
                proc.stdin.write(frame(i/FPS).tobytes())
                if i%600==0:print('frame',i,'/',count,flush=True)
        finally:proc.stdin.close()
        if proc.wait():raise RuntimeError('ffmpeg failed')
        print('DONE',path,path.stat().st_size,'SHA256',hashlib.sha256(path.read_bytes()).hexdigest(),flush=True)

if __name__=='__main__':main()

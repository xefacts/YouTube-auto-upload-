#!/usr/bin/env python3
"""One-image five-beat editorial intro board; final FINCH lettering is vector typeset, not AI text."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

R=Path(__file__).resolve().parent
FONT=R.parent/'assets'/'fonts'
ANTON=FONT/'Anton-Regular.ttf'; DM=FONT/'DMSans.ttf'
IVORY='#f6f1e7'; INK='#132e31'; COPPER='#b87653'; TEAL='#297977'; GREY='#586d6b'; WHITE='#fefcf6'

def font(path,sz):return ImageFont.truetype(str(path),sz)
def wrap(d,text,f,max_w):
    result=[];line=''
    for word in text.split():
        test=(line+' '+word).strip()
        if d.textbbox((0,0),test,font=f)[2]>max_w and line:
            result.append(line);line=word
        else:line=test
    if line:result.append(line)
    return result

def make():
    W,H=5000,3060
    im=Image.new('RGB',(W,H),IVORY); d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,280),fill=INK)
    d.text((85,22),'FINCH  /  THROUGH THE LENS',font=font(ANTON,125),fill=WHITE)
    d.text((89,198),'ONE CLEAN 2D BRAND INTRO  •  FIVE ANIMATED BEATS  •  4.8 SECONDS',font=font(DM,34),fill='#c5dcd4')
    slots=[
        ('01 / SIGNATURE LENS','0.0–0.7s','A single elegant optic turns.','lens_v2.png'),
        ('02 / APPROACH','0.7–1.5s','Finch walks toward the glass.','01_approach.png'),
        ('03 / ENTER','1.5–2.5s','He steps INSIDE the lens.','02_enter_lens.png'),
        ('04 / REVEAL','2.5–3.3s','Camera crosses; he faces us.','03_inside.png'),
        ('05 / NAME','3.3–4.8s','FINCH types on; voice speaks.','04_reveal.png'),
    ]
    xs=[74+i*978 for i in range(5)]; y=326; cw=902; ch=1709
    for i,(title,time,caption,img_name) in enumerate(slots):
        x=xs[i]
        d.rounded_rectangle((x,y,x+cw,y+ch),radius=21,fill=WHITE,outline='#d2dcd2',width=4)
        art_box=(x+16,y+16,cw-32,1480)
        src=Image.open(R/'art'/img_name).convert('RGB')
        if i==0:
            d.rectangle((x+16,y+16,x+cw-16,y+1496),fill='#f6efdd')
            src=src.crop((335,36,1060,733))
            # Remove ivory source background before rotating: no diamond-shaped paste seam.
            diff=ImageChops.difference(src,Image.new('RGB',src.size,(250,243,222)))
            c=diff.split(); alpha=ImageChops.lighter(c[0],ImageChops.lighter(c[1],c[2]))
            alpha=alpha.point(lambda v:max(0,min(255,(v-13)*19)))
            src.putalpha(alpha)
            src=src.rotate(43,expand=True,resample=Image.Resampling.BICUBIC)
            bbox=src.getchannel('A').getbbox()
            src=src.crop((max(0,bbox[0]-20),max(0,bbox[1]-20),min(src.width,bbox[2]+20),min(src.height,bbox[3]+20)))
            src=ImageOps.contain(src,(810,1385),Image.Resampling.LANCZOS)
            im.paste(src,(x+cw//2-src.width//2,y+65),src)
        else:
            resized=ImageOps.fit(src,(art_box[2],art_box[3]),Image.Resampling.LANCZOS,centering=(.5,.49))
            im.paste(resized,(art_box[0],art_box[1]))
        if i==4:
            # The name is intentional real typography; image generation did not fabricate letters.
            d.text((x+60,y+636),'FINCH',font=font(ANTON,133),fill=WHITE,stroke_width=2,stroke_fill=INK)
            d.rectangle((x+64,y+800,x+380,y+806),fill=COPPER)
        d.rectangle((x+16,y+1497,x+cw-16,y+1501),fill='#d7ded5')
        d.text((x+30,y+1516),title,font=font(ANTON,46),fill=INK)
        d.text((x+31,y+1589),time,font=font(ANTON,39),fill=TEAL)
        d.text((x+31,y+1644),caption,font=font(DM,28),fill=GREY)
    d.rounded_rectangle((74,2088,4926,2992),radius=24,fill='#dfebe3')
    d.text((116,2110),'THE BRANDED LINE  /  VOICE ONLY',font=font(ANTON,73),fill=INK)
    d.text((118,2216),'“I’m Finch. Look closer.”',font=font(ANTON,88),fill='#2b6968')
    d.text((119,2333),'Name appears at 3.3s, synchronized with “Finch.”  •  FINCH is a draft name; replace after final approval.',font=font(DM,34),fill=GREY)
    d.line((118,2406,4880,2406),fill='#b9cbbd',width=4)
    d.text((119,2433),'COPY-READY ANIMATION PROMPT',font=font(ANTON,60),fill=INK)
    prompt=('4.8s, vertical 9:16, original flat hand-inked 2D title animation. Use the same ginger, freckled Finch face and petrol-teal detective coat throughout. Begin on the new single blackened-bronze/copper lens; the detective walks toward it and visibly steps through its glass. Camera crosses the optical plane into clean graphic 2D space; he turns to camera. On a cut, show him holding that exact lens while FINCH types on as real clean typography. Natural new walking/turning poses, not a sliding cutout. Voice ONLY: “I’m Finch. Look closer.” No ambience, sound effects, music, narration outside that line, extra text or subtitles.')
    f=font(DM,33)
    for j,line in enumerate(wrap(d,prompt,f,4670)):
        d.text((123,2511+j*54),line,font=f,fill='#3f5a58')
    d.text((3895,2951),'STORYBOARD  /  NOT A MOVING CLIP',font=font(DM,25),fill=GREY)
    out=R/'FINCH_BRANDED_INTRO_ONE_IMAGE_STORYBOARD.png';im.save(out,optimize=True)
    print(out.name,out.stat().st_size)

if __name__=='__main__':make()

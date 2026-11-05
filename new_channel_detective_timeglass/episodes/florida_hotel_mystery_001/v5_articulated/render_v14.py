#!/usr/bin/env python3
"""V14 dark editorial finish for the owner-only Florida mystery review.

Original Train 2/Text screenshots are inspiration for hierarchy and pacing,
never footage or text assets. No top caption. Full selected VO and private
user-supplied music/SFX remain untouched. 8K raster is explicitly an upscale.
"""
from pathlib import Path
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import render_v13 as base

HERE=Path(__file__).resolve().parent
ROOT=base.prev.ROOT
W,H,FPS,DUR=base.W,base.H,base.FPS,base.DUR
FF=base.FF
EASE=base.EASE
# Finish the typewriter title early enough to hold it legibly for ~0.95s.
base.prev.CHAR_TIMES=[.25+i*.07 for i in range(len(base.prev.TITLE.replace('\n','')))]

# Drama lives in controlled pools of light rather than hiding visual evidence:
# dark desaturated-blue case-board paper, warm rust spotlight, grain and falloff.
rng=np.random.default_rng(1414)
y,x=np.mgrid[0:H,0:W].astype(np.float32)
xx=x/W; yy=y/H
r2=((xx-.49)/.84)**2+((yy-.43)/.93)**2
light=np.maximum(0,1-r2)**2
noise=rng.normal(0,1.55,(H,W)).astype(np.float32)
warm=np.exp(-(((xx-.75)/.7)**2+((yy-.69)/.63)**2))
a=np.empty((H,W,3),dtype=np.uint8)
for c,depth in enumerate((21.,29.,33.)):
    a[:,:,c]=np.uint8(np.clip(depth+11*light+(6 if c==0 else 1)*warm+noise,0,255))
base.PAPER=Image.fromarray(a)
del a,noise,x,y,xx,yy,r2,light,warm
base.INK=(212,55,59,255)

# The Text screenshots favour immediate scale contrast. Original two-tier
# evidence lettering stays INSIDE every photo card, below the image, and stays
# legible when all five proof pictures are visible together on a mobile screen.
ANTON=str(ROOT/'assets/fonts/Anton-Regular.ttf')
SANS=str(ROOT/'assets/fonts/DMSans.ttf')
SERIF='/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
hero_pairs=[('FIBER','ON THE COAT'),('THREAD','ON THE RAIL'),
            ('SLIDE BOLT','ACROSS THE GAP'),('SUITE DOOR','IN THE HALLWAY'),
            ('FOOTPRINTS','TOWARD THE BALCONY')]

# Preserve identical photo rectangles and source crop alignment so the already
# frame-checked original SVG red circles still land on the correct evidence.
hero=[];board=[]
for photo,(major,minor) in zip(base.photos,hero_pairs):
    im=Image.new('RGBA',(752,1006),(23,31,35,255))
    # Remove a sliver of the image bottom, not the clue, for a fully visible
    # two-line label inside the print's existing fixed SVG coordinate system.
    im.paste(photo.crop((0,0,720,876)),(16,16))
    d=ImageDraw.Draw(im,'RGBA')
    d.rectangle((2,2,749,1003),outline=(207,191,158,255),width=2)
    d.rectangle((16,891,736,1000),fill=(19,26,29,250))
    d.rectangle((26,904,32,988),fill=(205,62,61,255))
    big=ImageFont.truetype(ANTON,54)
    d.text((51,891),major,font=big,fill=(250,243,222,255))
    small=ImageFont.truetype(SANS,23)
    d.text((53,958),minor,font=small,fill=(195,201,194,255))
    hero.append(im)
    thumb=ImageOps.fit(photo,(388,347),method=Image.Resampling.LANCZOS,centering=(.5,.5))
    card=Image.new('RGBA',(420,435),(24,32,35,255))
    card.paste(thumb,(16,16))
    d=ImageDraw.Draw(card,'RGBA')
    d.rectangle((2,2,417,432),outline=(188,177,151,255),width=2)
    d.rectangle((16,367,404,429),fill=(18,27,30,245))
    d.rectangle((22,374,26,421),fill=(207,62,62,255))
    d.text((38,362),major,font=ImageFont.truetype(ANTON,32),fill=(249,240,215,255))
    d.text((39,402),minor,font=ImageFont.truetype(SANS,20),fill=(192,198,194,255))
    board.append(card)
base.hero_cards=hero
base.board_cards=board

# Source-scene edge falloff is mild: do not conceal faces, shoes or prop proofs.
# A single precomputed alpha plate avoids moving shadows/flickering every frame.
xx=np.linspace(-1,1,W,dtype=np.float32)[None,:]
yy=np.linspace(-1,1,H,dtype=np.float32)[:,None]
edge=np.clip((xx*xx*.55+yy*yy*.48-.24)/.92,0,1)
edge=(edge**1.4*78).astype(np.uint8)
veil=Image.new('RGBA',(W,H),(2,11,16,0))
veil.putalpha(Image.fromarray(edge))

# Replaces the V13 pill with tasteful, TWO-LEVEL editorial typography in the
# lower image area; short labels identify visible objects, never a VO transcript.
# The entry shown at 7s is ajar; do not call it a closed-door proof.
base.nonclue_cues=[(6.98,8.75,'SUITE ENTRANCE'),(16.02,17.05,'THE SLIDE BOLT'),
                   (26.38,28.46,'THREAD ON THE RAIL')]
caption_parts={
 'SUITE ENTRANCE':('SUITE','ENTRANCE'),
 'THE SLIDE BOLT':('THE','SLIDE BOLT'),
 'THREAD ON THE RAIL':('THREAD','ON THE RAIL'),
}
caption_layers={}
for label,(small,big) in caption_parts.items():
    layer=Image.new('RGBA',(W,H))
    d=ImageDraw.Draw(layer,'RGBA')
    font=ImageFont.truetype(ANTON,66)
    smallfont=ImageFont.truetype(SERIF,33)
    bbox=d.textbbox((0,0),big,font=font);width=bbox[2]
    bx=(W-width)//2
    y0=1460
    # Semi-transparent charcoal veil is local to text, not a footer banner.
    d.rounded_rectangle((bx-48,y0-10,bx+width+48,y0+163),radius=15,
                        fill=(5,15,20,175))
    d.text((bx,y0),small,font=smallfont,fill=(216,91,78,255))
    d.text((bx,y0+43),big,font=font,fill=(249,240,218,255))
    d.line((bx,y0+139,bx+min(width,310),y0+139),fill=(204,69,65,255),width=5)
    caption_layers[label]=layer

def lower_caption(image,label,alpha=1):
    if label not in caption_layers or alpha<=0:return image
    layer=caption_layers[label].copy()
    layer.putalpha(layer.getchannel('A').point(lambda a:round(a*alpha)))
    return Image.alpha_composite(image.convert('RGBA'),layer).convert('RGB')
base.lower_caption=lower_caption

def frame(t):
    result=base.frame(t)
    # The case board is intentionally dark already; do not double-darken clue
    # photographs. Intro and crime/investigation have an unobtrusive edge falloff.
    if t<28.80:
        return Image.alpha_composite(result.convert('RGBA'),veil).convert('RGB')
    return result

if __name__=='__main__':
    wav=base.soundtrack()  # selected 36.4955s VO, supplied music and SFX
    raw=base.CACHE/'silent_v14_1080.mp4'
    cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24',
         '-s',f'{W}x{H}','-r',str(FPS),'-i','pipe:0','-c:v','libx264',
         '-threads','2','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',str(raw)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k%(FPS*4)==0:print('frame',k,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('V14 1080 animation encode failed')
    finally:
        if p.poll() is None:p.kill()
    out=HERE/'FLORIDA_V14_DARK_EDITORIAL_PRIVATE_REVIEW_8K_UPSCALED.mp4'
    subprocess.run([FF,'-y','-loglevel','error','-threads','1','-filter_threads','1',
        '-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
        '-vf','scale=4320:7680:flags=bicubic',
        '-c:v','libx264','-threads','1','-preset','ultrafast','-crf','29',
        '-x264-params','ref=1:rc_lookahead=0:bframes=0','-pix_fmt','yuv420p',
        '-af','loudnorm=I=-18:TP=-1.5:LRA=9',
        '-c:a','aac','-b:a','192k','-ar','48000','-movflags','+faststart',
        '-shortest',str(out)],check=True)
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

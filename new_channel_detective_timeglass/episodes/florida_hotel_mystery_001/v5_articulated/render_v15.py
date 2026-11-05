#!/usr/bin/env python3
"""V15 private Shorts review: sound-preserving, bandwidth-conscious 1080x1920 cut.

Entire 36.4955s selected narration is retained. After 36.5s, ONLY an original
animated COMMENT BELOW graphic plays in absolute silence. Correct PRISM's
floating lens and wife's white-key artifacts; rotate original marked evidence
prints into a clean, readable final collage. No Train 2 source pixels reused.
"""
from pathlib import Path
import math, subprocess, wave
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import render_v14 as old

HERE=Path(__file__).resolve().parent
EP=HERE.parent
A=HERE/'assets'
W,H,FPS=old.W,old.H,old.FPS
VOICE_END=36.5
DUR=39.25  # exact 942 frames @24fps; 2.75-second silent visual CTA
FF=old.FF
EASE=old.EASE
v11=old.base.v11
source_sprite=old.base.prev.v11

# On the later balcony, source 'prism_balcony_stand' had a magnifying glass
# clipped to the chest and a thin unattached line to the fingertips. Replace
# ONLY this defective source pose with the confirmed pose whose fingers wrap
# the wooden handle. Shoes remain anchored to the same balcony floor plane.
v11.SPRITES['prism_balcony_stand']=v11.SPRITES['prism_suite_look'].copy()

# White stage background on wife's burgundy coat must not travel into a dark
# corridor. Isolate main PERSON contour, fill tiny interior holes (eye/pearls),
# erode the white fringe one pixel, feather 0.55px. Drop studio floor shadows.
def wife_key(name):
    im=Image.open(A/(name+'.png')).convert('RGB')
    rgb=np.asarray(im)
    ink=(rgb.min(axis=2)<223).astype(np.uint8)*255
    ink=cv2.morphologyEx(ink,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
    contours,_=cv2.findContours(ink,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    human=max(contours,key=cv2.contourArea)
    mask=np.zeros(rgb.shape[:2],np.uint8)
    cv2.drawContours(mask,[human],-1,255,-1)
    # The gap between sleeve and waist, and between calves, can be enclosed
    # by the OUTER silhouette. Large near-white regions there are air, not
    # clothing; small highlights (eyes/pearls) are preserved.
    hi=rgb.max(axis=2).astype(np.int16)
    lo=rgb.min(axis=2).astype(np.int16)
    white=((lo>238)&((hi-lo)<22)).astype(np.uint8)
    _,groups,stats,_=cv2.connectedComponentsWithStats(white,8)
    for j in range(1,len(stats)):
        if stats[j,cv2.CC_STAT_AREA]>85:
            mask[groups==j]=0
    mask=cv2.erode(mask,np.ones((3,3),np.uint8),iterations=1)
    mask=cv2.GaussianBlur(mask,(3,3),.55)
    ys,xs=np.where(mask>2)
    bb=(max(0,int(xs.min())-2),max(0,int(ys.min())-2),
        min(im.width,int(xs.max())+3),min(im.height,int(ys.max())+3))
    result=im.convert('RGBA');result.putalpha(Image.fromarray(mask))
    result=result.crop(bb)
    return v11.grade(result)

for name in ('wife_master','wife_turn_pose'):
    v11.SPRITES[name]=wife_key(name)

# A near-black teal edge ink at sprite scale binds cutouts to the scene, but
# never creates a thick sticker halo. Source anatomy/face/clothes stay intact.
for name in ('wife_master','wife_turn_pose','prism_suite_look','prism_reach_v12'):
    im=v11.SPRITES[name]
    a=im.getchannel('A')
    rim=ImageChops.subtract(a.filter(ImageFilter.MaxFilter(3)),a)
    rim=rim.point(lambda z:round(z*.42))
    plate=Image.new('RGBA',im.size,(5,19,22,0));plate.putalpha(rim)
    v11.SPRITES[name]=Image.alpha_composite(plate,im)
# Alias must follow the newly rimmed confirmed held-lens pose.
v11.SPRITES['prism_balcony_stand']=v11.SPRITES['prism_suite_look']

# Purposeful photographic collage: the five original pictorial proofs remain
# individually labelled, each ring is attached to the image BEFORE its small
# rotation/arrival. Size and ring targeting remain readable on a phone.
PAPER=old.base.PAPER
INK=old.base.INK
positions=[(92,188,-2.2),(570,210,2.0),(97,708,1.4),(565,728,-1.7),(330,1240,1.0)]
marked=[]
for i,(name,(x,y,ang)) in enumerate(zip(old.base.names,positions)):
    card=old.base.board_cards[i].copy()
    # Original SVG paths use the V13 aligned final-board positions. Translate
    # vector points to local card coordinates, then rotate photo AND ring once.
    original=old.base.positions[i]
    pts=old.base.strokes['board-'+name]
    local=[(round(px-original[0]),round(py-original[1])) for px,py in pts]
    d=ImageDraw.Draw(card,'RGBA')
    d.line(local,fill=INK,width=5,joint='curve')
    card=card.rotate(ang,Image.Resampling.BICUBIC,expand=True)
    marked.append(card)

def final_collage(t):
    q=t-34.55
    paper=PAPER.copy().convert('RGBA')
    for i,(card,(x,y,ang)) in enumerate(zip(marked,positions)):
        reveal=EASE((q-i*.105)/.40)
        if reveal<=0:continue
        # Per-card gentle stagger, then a steady final complete layout.
        xx=round(x+(1-reveal)*(-55 if i%2==0 else 55))
        yy=round(y+(1-reveal)*40)
        layer=card.copy()
        layer.putalpha(layer.getchannel('A').point(lambda v:round(v*reveal)))
        shadow=Image.new('RGBA',paper.size)
        ImageDraw.Draw(shadow).rectangle((xx+11,yy+15,xx+card.width+13,yy+card.height+17),
                                         fill=(0,0,0,round(82*reveal)))
        paper.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(13)))
        paper.alpha_composite(layer,(xx,yy))
        # Small bronze pin above the labeled photo, for an archival paper feel.
        if reveal>.65:
            d=ImageDraw.Draw(paper,'RGBA')
            cx=xx+card.width//2
            d.ellipse((cx-6,yy+7,cx+6,yy+19),fill=(181,130,74,round(235*reveal)))
            d.ellipse((cx-2,yy+9,cx+2,yy+13),fill=(249,219,151,round(245*reveal)))
    # Settles to 100% canvas by 35.5s, then holds through the entire final word.
    z=1.035-.035*EASE(q/.95)
    return v11.crop(paper.convert('RGB'),z,(.5,.50))

# Clear, intentionally silent animated call to action. Text is CENTERED, not
# hidden behind YouTube's bottom-right Shorts action buttons or a footer bar.
COMMENT='COMMENT BELOW'
FONT=ImageFont.truetype(old.ANTON,87)
CTA_BASE=Image.new('RGB',(W,H),(15,23,29))

def comment_frame(t):
    q=t-36.90
    im=CTA_BASE.copy().convert('RGBA')
    d=ImageDraw.Draw(im,'RGBA')
    # Small dossier squares echo (do not reuse) the evidence collage.
    for i in range(5):
        u=EASE((q-.08-i*.09)/.36)
        x=220+i*144; y=620+int((1-u)*55)
        if u>.01:
            d.rounded_rectangle((x,y,x+106,y+119),radius=5,
                                fill=(39,51,56,round(210*u)),outline=(183,144,104,round(140*u)),width=2)
            d.line((x+17,y+38,x+86,y+38),fill=(189,202,194,round(90*u)),width=3)
            d.line((x+17,y+57,x+74,y+57),fill=(189,202,194,round(75*u)),width=3)
            d.arc((x+33,y+61,x+73,y+101),35,290,fill=(203,66,64,round(220*u)),width=4)
    # SVG-like original speech bubble: trace sides as smooth ease progress.
    r=EASE((q-.35)/.45)
    if r>0:
        yy=835
        d.rounded_rectangle((135,yy,945,1180),radius=70,fill=(19,31,35,round(240*r)))
        d.rounded_rectangle((135,yy,945,1180),radius=70,outline=(197,140,88,round(230*r)),width=4)
        d.polygon(((322,1176),(414,1176),(336,1260)),fill=(19,31,35,round(235*r)))
        d.line((322,1176,336,1260,412,1178),fill=(197,140,88,round(230*r)),width=4)
    k=round(len(COMMENT)*EASE((q-.72)/.63))
    if k>0:
        text=COMMENT[:k]
        bbox=d.textbbox((0,0),text,font=FONT)
        w=bbox[2]-bbox[0]
        d.text(((W-w)//2,943),text,font=FONT,fill=(249,237,213,255))
        # One deliberate red underline, not an ungrounded zoom or extra words.
        u=EASE((q-1.33)/.55)
        if u>0:d.line((218,1078,218+round(640*u),1078),fill=(212,59,61,255),width=8)
    # Short fade only at tail boundary, not over voice or clue board.
    fade=EASE((DUR-.32-t)/.28)
    if fade<1:
        overlay=Image.new('RGBA',im.size,(7,13,18,round(255*(1-fade))))
        im=Image.alpha_composite(im,overlay)
    return im.convert('RGB')

# Protect dark clothing from over-crushed shadows. Use a consistent mild LUT,
# rather than framewise brightness changes that would flicker or wash red ink.
curve=[]
for shift in (1,1,0):
    curve += [int(np.clip(np.interp(i,[0,27,77,145,222,255],
                  [4+shift,31+shift,81+shift,148,222,252]),0,255)) for i in range(256)]

def frame(t):
    if t>=36.90:return comment_frame(t)
    if t>=34.55:return final_collage(t)
    return old.frame(t).point(curve)

def soundtrack():
    # The V14 master already carries *all* selected voice words, supplied music,
    # and SFX through 36.5s. Preserve PCM bit-for-bit; append SILENCE only.
    prior=old.base.soundtrack()
    with wave.open(str(prior),'rb') as inp:
        assert inp.getnchannels()==2 and inp.getframerate()==48000 and inp.getsampwidth()==2
        pcm=inp.readframes(inp.getnframes())
    assert len(pcm)==int(VOICE_END*48000)*4
    tail=b'\0'*(int((DUR-VOICE_END)*48000)*4)
    out=old.base.CACHE/'v15_complete_vo_then_silent_comment.wav'
    with wave.open(str(out),'wb') as wav:
        wav.setnchannels(2);wav.setsampwidth(2);wav.setframerate(48000)
        wav.writeframes(pcm+tail)
    return out

if __name__=='__main__':
    audio=soundtrack()
    out=HERE/'FLORIDA_V15_SHORTS_PRIVATE_REVIEW_1080x1920.mp4'
    # CRF with VBV cap: don't inflate bitrate on static card frames; keep H.264
    # level 4.2 and 1080x1920 24fps widely decodable. +faststart for playback.
    cmd=[FF,'-y','-hide_banner','-loglevel','error','-f','rawvideo',
         '-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','pipe:0',
         '-i',str(audio),'-map','0:v','-map','1:a','-c:v','libx264','-threads','2',
         '-preset','medium','-crf','19','-maxrate','8M','-bufsize','16M',
         '-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p',
         '-c:a','aac','-b:a','160k','-ar','48000',
         '-af','loudnorm=I=-18:TP=-1.5:LRA=9',
         '-movflags','+faststart','-shortest',str(out)]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        for i in range(round(DUR*FPS)):
            p.stdin.write(frame(i/FPS).tobytes())
            if i%(FPS*5)==0:print('frame',i,'/',round(DUR*FPS),flush=True)
        p.stdin.close()
        if p.wait()!=0:raise RuntimeError('V15 Shorts encode failed')
    finally:
        if p.poll() is None:p.kill()
    print('DELIVERABLE',out,out.stat().st_size,flush=True)

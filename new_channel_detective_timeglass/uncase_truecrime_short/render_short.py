#!/usr/bin/env python3
"""Render an original 9:16 evidence-led true-crime short with layered 2.5D motion."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps,ImageFilter
from imageio_ffmpeg import get_ffmpeg_exe
import subprocess,math,json,random,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2]; HERE=Path(__file__).resolve().parent; A=HERE/'assets'
W,H,FPS=1080,1920,30
ANT=ROOT/'new_channel_detective_timeglass/assets/fonts/Anton-Regular.ttf';DM=ROOT/'new_channel_detective_timeglass/assets/fonts/DMSans.ttf'
TIMING=json.loads((A/'narration_timing.json').read_text())
IMGS=[Image.open(A/n).convert('RGB') for n in ['01_empty_wall.png','00_empty_wall_morning.png','02_worker_exit.png','03_hidden_trunk.png','04_dealer_reveal.png','05_case_closed.png','06_returned_portrait.png']]
# Speech blocks and scene plates align; later shot variation is achieved with a camera recrop and original motion graphics.
SCENE_IMG=[0,1,2,3,4,5,6]
BG=[ImageOps.fit(im,(W,H),Image.Resampling.LANCZOS) for im in IMGS]
P=ImageFont.truetype(str(ANT),70); SUB=ImageFont.truetype(str(DM),30); KICK=ImageFont.truetype(str(DM),25); HUGE=ImageFont.truetype(str(ANT),108)
IVORY=(250,246,234); RED=(226,75,82); MUTED=(181,195,202); NAVY=(8,14,24)
DURATION=67.3

def smooth(x):x=max(0,min(1,x));return x*x*(3-2*x)
def draw_fit_text(d, text, font, y, color, maxw=980, anchor='mm', x=W//2, stroke=2):
    # line-wrap without breaking words, retain typographic hierarchy
    words=text.split(); lines=[]; cur=''
    for word in words:
        test=(cur+' '+word).strip()
        if d.textbbox((0,0),test,font=font,stroke_width=stroke)[2] <= maxw:cur=test
        else:
            if cur:lines.append(cur)
            cur=word
    if cur:lines.append(cur)
    lineh=font.size*1.12; top=y-(len(lines)-1)*lineh/2
    for i,line in enumerate(lines):d.text((x,top+i*lineh),line,font=font,fill=color,anchor='mm',stroke_width=stroke,stroke_fill=(0,0,0,190))

def make_map_plate(t,canvas):
    # Schematic route interface—explicitly not a survey map.
    lay=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(lay)
    d.rounded_rectangle((95,340,985,860),radius=28,fill=(6,15,28,215),outline=(229,230,223,125),width=3)
    d.text((145,386),'RECOVERY TRAIL  /  SCHEMATIC',font=KICK,fill=MUTED)
    # minimalist nodes and route
    x1,y1=310,640;x2,y2=760,555
    d.line((x1,y1,x2,y2),fill=(220,64,76,190),width=5)
    for frac in np.linspace(0,1,24):
        x=x1+(x2-x1)*frac;y=y1+(y2-y1)*frac
        d.ellipse((x-3,y-3,x+3,y+3),fill=IVORY)
    prog=smooth((t-24.8)/8.0);x=x1+(x2-x1)*prog;y=y1+(y2-y1)*prog
    d.ellipse((x-18,y-18,x+18,y+18),fill=RED,outline=IVORY,width=4)
    d.ellipse((x1-15,y1-15,x1+15,y1+15),fill=IVORY);d.ellipse((x2-15,y2-15,x2+15,y2+15),fill=IVORY)
    d.text((x1,y1+52),'PARIS',font=fontbold(35),fill=IVORY,anchor='mm')
    d.text((x2,y2-53),'FLORENCE',font=fontbold(35),fill=IVORY,anchor='mm')
    return Image.alpha_composite(canvas.convert('RGBA'),lay).convert('RGB')
def fontbold(s):return ImageFont.truetype(str(ANT),s)

def phrases():
 import re
 out=[]
 for row in TIMING:
  # display sentence-level phrases, allocate proportionally to spoken word count; final timing is checked in QA.
  ss=[s.strip() for s in re.split(r'(?<=[.!?])\s+',row['text']) if s.strip()]
  weights=[max(1,len(x.split())**.92) for x in ss];total=sum(weights)
  start=row['start'];span=row['end']-row['start']
  for s,w in zip(ss,weights):
   end=start+span*w/total;out.append({'text':s,'start':start,'end':end,'block':row['index']});start=end
 return out
PH=phrases()
def overlay_frame(frame,t,scene_idx,scene_start,scene_end,caption):
 d=ImageDraw.Draw(frame,'RGBA')
 # Animated black vignette and editorial border framing, safe from UI edges.
 d.rectangle((0,0,W,220),fill=(5,10,18,175));d.rectangle((0,H-500,W,H),fill=(5,10,18,160))
 # label + case progress strip
 d.text((58,56),'UNCASE  /  CASE FILE 01',font=KICK,fill=IVORY)
 d.text((W-58,56),f'{int(t//10)+1:02d} / 07',font=KICK,fill=RED,anchor='ra')
 d.rounded_rectangle((58,120,W-58,128),radius=4,fill=(160,170,180,95))
 d.rounded_rectangle((58,120,58+(W-116)*min(1,t/DURATION),128),radius=4,fill=RED)
 # 2.5D rotating evidence-card motif near outer side; never covers story focal point
 drift=math.sin(t*.77)*13; d.line((W-100,260+drift,W-75,295+drift),fill=(226,75,82,170),width=4)
 d.ellipse((W-99,258+drift,W-89,268+drift),fill=RED)
 # highlight a case-specific short topic tag, fade in/out across scene
 labels=['THE EMPTY WALL','A WORKER’S EXIT','HIDDEN IN PARIS','A LETTER FROM FLORENCE','MOTIVE: PATRIOTISM?','THE VERDICT','THE FINAL TWIST']
 d.rounded_rectangle((62,240,500,296),radius=18,fill=(5,12,22,180),outline=(230,230,220,65),width=2)
 d.text((84,268),labels[scene_idx],font=KICK,fill=RED,anchor='lm')
 d.text((W//2,H-455),'ILLUSTRATIVE RECONSTRUCTION',font=KICK,fill=(220,225,230,205),anchor='mm')
 if caption:
  # Bottom subtitle plate has two lines max; no dense subtitle paragraph spam.
  txt=caption['text']; draw_fit_text(d,txt,P,H-318,IVORY,maxw=940,stroke=3)
 # mid-video explicit viewer question / pause beat
 if 37.0<=t<=44.3:
  alpha=int(255*min(smooth((t-37)/.38),smooth((44.3-t)/.38)))
  d.rounded_rectangle((100,920,980,1085),radius=25,fill=(8,12,22,alpha*3//4),outline=(226,75,82,alpha),width=4)
  d.text((W//2,968),'YOUR TURN',font=KICK,fill=(255,130,136,alpha),anchor='mm')
  d.text((W//2,1025),'PATRIOTISM OR PROFIT?',font=fontbold(53),fill=(255,255,248,alpha),anchor='mm')
 # End card
 if t>61.5:
  a=int(255*smooth((t-61.5)/.8));d.rounded_rectangle((145,1260,935,1404),radius=30,fill=(8,13,22,a*3//4),outline=(226,75,82,a),width=4)
  d.text((540,1305),'WHAT’S YOUR READ?',font=fontbold(45),fill=(255,255,245,a),anchor='mm')
  d.text((540,1360),'BELIEF  /  PROFIT  /  BOTH?',font=KICK,fill=(226,75,82,a),anchor='mm')
 return frame

def frame_at(t):
 idx=max(0,min(len(TIMING)-1,next((i for i,r in enumerate(TIMING) if r['start']<=t<r['end']),len(TIMING)-1)))
 r=TIMING[idx];local=max(0,min(1,(t-r['start'])/max(.01,r['end']-r['start'])))
 img=BG[SCENE_IMG[idx]]
 # Push-in/pan camera, distinct per beat. On each line, foreground and backplate drift at different rates.
 zoom=1.025+.105*smooth(local);w=int(W*zoom);h=int(H*zoom);img=img.resize((w,h),Image.Resampling.LANCZOS)
 panx=(idx%2*2-1)*.035*smooth(local);pany=(.02 if idx%2 else -.018)*smooth(local)
 left=int((w-W)/2+panx*w);top=int((h-H)/2+pany*h);left=max(0,min(w-W,left));top=max(0,min(h-H,top))
 frame=img.crop((left,top,left+W,top+H)).convert('RGBA')
 # Cool shadows and atmospheric film grain; subtle only so map/text remain readable.
 tint=Image.new('RGBA',(W,H),(4,12,24,30));frame=Image.alpha_composite(frame,tint).convert('RGB')
 if idx==3:frame=make_map_plate(t,frame)
 # date and case-file overlays as independent 2D motion graphics
 layer=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(layer)
 if idx==0:
  a=smooth(min(1,t/1.4));d.text((W//2,470),'21 AUGUST 1911',font=fontbold(55),fill=(*RED,int(255*a)),anchor='mm')
 if idx==2:
  # draw a slowly tightening reticle around hidden-trunk clue
  p=smooth(local);rad=int(80+75*p);cx,cy=760,1170
  d.ellipse((cx-rad,cy-rad,cx+rad,cy+rad),outline=(*RED,220),width=5)
  d.line((cx+rad-4,cy+rad-4,cx+rad+45,cy+rad+45),fill=(*RED,230),width=8)
 if idx==5:
  d.text((W//2,470),'FLORENCE  /  1914',font=fontbold(47),fill=(*IVORY,220),anchor='mm')
 frame=Image.alpha_composite(frame.convert('RGBA'),layer).convert('RGB')
 cap=next((p for p in PH if p['start']<=t<p['end']),None)
 return overlay_frame(frame,t,idx,r['start'],r['end'],cap)

def main():
 out=HERE/'UNCASE_MONA_LISA_THEFT_PRIVATE_REVIEW_1080x1920.mp4';raw=HERE/'assets/video_only.mp4'
 ff=get_ffmpeg_exe();cmd=[ff,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p',str(raw)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 n=round(DURATION*FPS)
 for i in range(n):
  p.stdin.write(np.asarray(frame_at(i/FPS),dtype=np.uint8).tobytes())
  if i%300==0:print('frame',i,'/',n,flush=True)
 p.stdin.close();assert p.wait()==0
 mixcmd=[ff,'-hide_banner','-loglevel','error','-y','-i',str(raw),'-i',str(A/'narration.wav'),'-i',str(A/'sound_design.wav'),'-filter_complex','[1:a]volume=1.0[v];[2:a]volume=0.36[b];[v][b]amix=inputs=2:duration=first:dropout_transition=0,loudnorm=I=-16:TP=-1.5:LRA=8[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','48000','-ac','2','-shortest',str(out)]
 subprocess.run(mixcmd,check=True)
 write_srt(HERE/'CAPTIONS_APPROX_WORD_TIMED.srt')
 raw.unlink(missing_ok=True);print('final',out,out.stat().st_size)

def write_srt(path):
 def fmt(t):
  ms=round(t*1000);h=ms//3600000;m=(ms%3600000)//60000;s=(ms%60000)//1000;ms%=1000;return f'{h:02}:{m:02}:{s:02},{ms:03}'
 with path.open('w') as f:
  for i,p in enumerate(PH,1):f.write(f"{i}\n{fmt(p['start'])} --> {fmt(p['end'])}\n{p['text']}\n\n")
if __name__=='__main__':main()

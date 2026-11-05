#!/usr/bin/env python3
"""Flat-relief geography edit rebuilt from all-frame reference measurements.

Original editorial graphics and script. No reference pixels or voice are copied.
A geographic Mercator flat relief atlas replaces the earlier inaccurate globe.
"""
from pathlib import Path
import math,bisect,wave,subprocess
import numpy as np,cv2
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from scipy.signal import butter,sosfiltfilt
from imageio_ffmpeg import get_ffmpeg_exe
import v3_maps as g
import generate_v3_narration as n

HERE=Path(__file__).resolve().parent;W,H,FPS=1080,1920,30;FF=get_ffmpeg_exe()
OUT=HERE/'FLORIDA_KEYS_FLAT_ATLAS_V3_PRIVATE_1080x1920.mp4';CACHE=HERE/'render_cache';CACHE.mkdir(exist_ok=True)
BEATS=n.generate();STARTS=[x['start'] for x in BEATS];DUR=math.ceil((BEATS[-1]['end']+.61)*FPS)/FPS
WORLD=Image.open(HERE/'assets/v3_world_relief_4096.png').convert('RGB')
WIDE=g.MAP_BASE;REGION=g.MAP_REGION;MACRO=g.MACRO
REEF=Image.open(HERE/'assets/keys_reef_cross_section.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
BRIDGE=Image.open(HERE/'assets/keys_overseas_bridge_aerial.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')
FONT=ImageFont.truetype(g.FONT,38);TITLE=ImageFont.truetype(g.BOLD,69);LABEL=ImageFont.truetype(g.BOLD,44)


def clamp(x):return max(0.,min(1.,x))
def smooth(x):x=clamp(x);return x*x*(3-2*x)
def blend(a,b,x):return a+(b-a)*smooth(x)

def crop_cam(img,z=1,cx=540,cy=960):
 w,h=img.size;cw,ch=W/z,H/z
 cx=float(np.clip(cx,cw/2,w-cw/2));cy=float(np.clip(cy,ch/2,h-ch/2))
 return img.transform((W,H),Image.Transform.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC).convert('RGBA')

def world_cam(t):
 # This path is one flat 4096² Mercator map; *not* a UV sphere or globe.
 # Translation/scale interpolate together, so the Florida pin follows the map.
 knots=[(0,1450,1900,1640),(3.2,1370,1910,1270),(6.8,1205,1820,685),(7.7,1190,1790,535)]
 a=knots[0];b=knots[-1]
 for q,r in zip(knots,knots[1:]):
  if q[0]<=t<r[0]:a,b=q,r;break
 p=smooth((t-a[0])/(b[0]-a[0]));cx=blend(a[1],b[1],p);cy=blend(a[2],b[2],p);cw=blend(a[3],b[3],p)
 return crop_cam(WORLD,W/cw,cx,cy)

def wide_cam(t):
 knots=[(6.45,1.02,540,960),(10.6,1.21,620,885),(17.3,1.30,688,812),(26.1,1.39,722,779),
        (51.8,1.32,666,821),(59.2,1.11,567,932),(DUR,1.02,540,960)]
 a,b=knots[0],knots[-1]
 for q,r in zip(knots,knots[1:]):
  if q[0]<=t<r[0]:a,b=q,r;break
 p=smooth((t-a[0])/(b[0]-a[0]));return [blend(a[k],b[k],p) for k in (1,2,3)]

def macro_cam(t):
 knots=[(13.9,1.06,540,960),(17.7,1.38,424,1110),
        (26.05,1.02,540,960),(33.9,1.52,465,1135),(37.17,1.26,570,1020),
        (40.87,1.27,620,1080),(45.0,1.62,425,1210),
        (48.2,1.22,510,935),(52.3,1.42,694,1160),(56,1.08,550,960)]
 a,b=knots[0],knots[-1]
 for q,r in zip(knots,knots[1:]):
  if q[0]<=t<r[0]:a,b=q,r;break
 p=smooth((t-a[0])/(b[0]-a[0]));return [blend(a[k],b[k],p) for k in (1,2,3)]

def title(im,text,y=177,size=69,color=(244,251,249),glow=(33,212,226),x=540):
 font=TITLE if size==69 else ImageFont.truetype(g.BOLD,size)
 layer=Image.new('RGBA',(W,H));mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask)
 bbox=d.textbbox((0,0),text,font=font);tx=round(x-(bbox[2]-bbox[0])/2)
 d.text((tx,y),text,font=font,fill=255)
 halo=Image.new('RGBA',(W,H),(*glow,0));halo.putalpha(mask.filter(ImageFilter.GaussianBlur(15)).point(lambda a:round(a*.59)))
 layer=Image.alpha_composite(layer,halo)
 ImageDraw.Draw(layer).text((tx,y),text,font=font,fill=(*color,255),stroke_width=2,stroke_fill=(4,32,39,245))
 return Image.alpha_composite(im,layer)

def caption(im,t):
 idx=max(0,min(len(BEATS)-1,bisect.bisect_right(STARTS,t)-1));b=BEATS[idx]
 if not b['start']<=t<b['end']:return im
 words=b['text'].split();group=[' '.join(words[i:i+4]) for i in range(0,len(words),4)]
 p=(t-b['start'])/(b['end']-b['start']);j=min(len(group)-1,int(p*len(group)))
 phase=p*len(group)-j;opacity=clamp(min(phase/.08,(1-phase)/.12,(b['end']-t)/.14))
 if opacity<.01:return im
 layer=Image.new('RGBA',(W,H));d=ImageDraw.Draw(layer)
 font=FONT;bb=d.textbbox((0,0),group[j],font=font);x=(W-bb[2]+bb[0])//2
 if x<76:
  font=ImageFont.truetype(g.FONT,34);bb=d.textbbox((0,0),group[j],font=font);x=(W-bb[2]+bb[0])//2
 y=1552
 d.text((x+2,y+3),group[j],font=font,fill=(1,20,30,210),stroke_width=4,stroke_fill=(1,20,30,190))
 d.text((x,y),group[j],font=font,fill=(247,253,253,255),stroke_width=1,stroke_fill=(3,37,46,200))
 layer.putalpha(layer.getchannel('A').point(lambda a:round(a*opacity)))
 return Image.alpha_composite(im,layer)

def line_overlay(points,progress,color=(43,232,255),dashed=False,width=9):
 pts=points[:max(2,round(len(points)*clamp(progress)))];mask=Image.new('L',(W,H));d=ImageDraw.Draw(mask)
 if dashed:
  for k in range(0,len(pts)-1,12):
   if k%36<24:d.line(pts[k:min(len(pts),k+10)],fill=255,width=width)
 else:d.line(pts,fill=255,width=width,joint='curve')
 glow=Image.new('RGBA',(W,H),(*color,0));glow.putalpha(mask.filter(ImageFilter.GaussianBlur(16)).point(lambda a:round(a*.74)))
 core=Image.new('RGBA',(W,H),(*color,0));core.putalpha(mask.point(lambda a:round(a*.9)))
 ImageDraw.Draw(core,'RGBA').line(pts,fill=(240,252,252,240),width=3,joint='curve')
 return Image.alpha_composite(glow,core)

# Geographic marker animation stays attached to the local map before camera.
MACRO_ROUTE=[line_overlay(g.MACRO_CURVE,i/24,color=(65,227,246),width=9) for i in range(25)]

def halo_marker(im,x,y,t,delay=0,r=31,c=(57,235,248)):
 k=smooth((t-delay)/.4)
 if k<=0:return im
 l=Image.new('RGBA',(W,H));d=ImageDraw.Draw(l)
 for extra,alpha,wi in ((19,25,12),(6,115,7),(0,230,3)):
  rr=r+extra;d.ellipse((x-rr,y-rr,x+rr,y+rr),outline=(*c,round(alpha*k)),width=wi)
 l=l.filter(ImageFilter.GaussianBlur(1.8));return Image.alpha_composite(im,l)

def clouds(im,t,opacity=.33):
 c=g.CLOUD_MAP.copy()
 c.putalpha(c.getchannel('A').point(lambda a:round(a*opacity)))
 # Light banks move independently of transformed terrain; no weather claim.
 c=c.transform((W,H),Image.Transform.AFFINE,(1,0,14*math.sin(t*.31),0,1,12*math.cos(t*.26)),Image.Resampling.BILINEAR)
 return Image.alpha_composite(im,c)

def wide_stage(t):
 layer=Image.blend(WIDE,REGION,smooth((t-8.2)/1.4))
 im=crop_cam(layer,*wide_cam(t))
 im=clouds(im,t)
 if t<10.7:im=title(im,'FLORIDA',y=322,size=55)
 if 52<t<55.6:
  im=title(im,'AN ISLAND CHAIN',y=152,size=57)
 return im

def macro_stage(t):
 im=MACRO.copy()
 if t<34 and t>=25.8:
  # Little islands appear as independent nodes; not five identical static frames.
  for k,(x,y) in enumerate(((807,918),(706,1021),(563,1134),(420,1218),(274,1327))):
   im=halo_marker(im,x,y,t,26.5+k*.44,30,(64,244,211))
 if 33.9<=t<48.1:
  progress=smooth((t-34.1)/3.1)
  im=Image.alpha_composite(im,MACRO_ROUTE[round(24*progress)])
 if t>=40.7:
  im=halo_marker(im,250,1323,t,40.7,48,(246,222,126))
 if 45<=t<49.0:
  il=Image.new('RGBA',(W,H));d=ImageDraw.Draw(il,'RGBA');d.ellipse((25,391,670,1175),outline=(93,244,241,130),width=6)
  im=Image.alpha_composite(im,il)
 if 48.0<=t<52.3:
  il=Image.new('RGBA',(W,H));d=ImageDraw.Draw(il,'RGBA');d.ellipse((572,593,1120,1370),outline=(94,232,249,145),width=5)
  im=Image.alpha_composite(im,il)
 im=crop_cam(im,*macro_cam(t));im=clouds(im,t,.27)
 if 14<t<17.7:
  im=title(im,'LOWER KEYS',y=182,size=52,color=(255,236,182),glow=(235,167,64))
  # An entirely separate warm selection, only over the southwest island chain.
  for j,(x,y) in enumerate(((563,1134),(420,1218),(274,1327))):
   im=halo_marker(im,int((x-macro_cam(t)[1])*macro_cam(t)[0]+540),int((y-macro_cam(t)[2])*macro_cam(t)[0]+960),t,14+j*.5,24,(250,210,100))
 if 26.4<t<29.4:im=title(im,'FLORIDA KEYS',y=168,size=56)
 if 30.0<t<33.9:
  im=title(im,'SHALLOW SHELF',y=168,size=53)
  im=halo_marker(im,470,965,t,30.1,88,(64,235,252))
 if 34<t<37.7:im=title(im,'OVERSEAS HIGHWAY',y=160,size=51)
 if 40.9<t<45.0:im=title(im,'KEY WEST',y=147,size=56)
 if 45<t<48.1:im=title(im,'FLORIDA BAY',y=680,size=51,x=300)
 if 48.2<t<52.2:im=title(im,'STRAITS OF FLORIDA',y=930,size=43,x=758)
 return im

def reef_stage(t):
 local=t-10.4
 if t<17.7:z=1.02+.075*smooth(local/7.3);cx=540+45*smooth(local/7.3);cy=960+60*smooth(local/7.3)
 elif t>=55.65:
  q=smooth((t-55.65)/3.51);z=1.07+.16*q;cx=540+75*q;cy=960+100*q
 else:z=1.09+.05*smooth((t-17.7)/8.3);cx=585-32*smooth((t-17.7)/8.3);cy=1020-75*smooth((t-17.7)/8.3)
 im=crop_cam(REEF,z,cx,cy)
 lay=Image.new('RGBA',(W,H));d=ImageDraw.Draw(lay,'RGBA')
 if t>=17.7:
  # Two opposite sea-level gestures in the diagram are matched to narration.
  if t>=55.65:y=round(550+235*smooth((t-55.65)/3.51));color=(87,244,255)
  elif t<22.1:y=round(647+125*smooth((t-17.7)/4.4));color=(87,244,255)
  else:y=round(772-266*smooth((t-22.1)/3.9));color=(250,242,198)
  d.line([(0,y),(W,y)],fill=(*color,210),width=6)
  for x in range(25,W,80):d.line([(x,y-9),(x,y+9)],fill=(*color,158),width=2)
 im=Image.alpha_composite(im,lay)
 if t<17.7:
  if t<13.9:im=title(im,'FOSSIL CORAL',y=184,size=59)
  elif t<17.6:
   im=title(im,'LIMESTONE',y=1000,size=46,x=685,color=(255,238,193),glow=(236,179,65))
   im=title(im,'SAND',y=1250,size=42,x=350,color=(255,238,193),glow=(236,179,65))
 elif t>=55.65:im=title(im,'CHANGING SEAS',y=213,size=52)
 elif t<22.2:im=title(im,'HIGHER SEAS',y=213,size=56)
 else:im=title(im,'LOWER SEAS',y=213,size=56)
 return im

def bridge_stage(t):
 p=smooth((t-37.1)/3.7);im=crop_cam(BRIDGE,1.06+.15*p,540,1010-115*p)
 l=Image.new('RGBA',(W,H));d=ImageDraw.Draw(l,'RGBA')
 y=round(1720-800*p)
 d.line([(540,y),(540,1920)],fill=(49,227,241,85),width=18)
 d.line([(540,y),(540,1920)],fill=(224,252,249,233),width=4)
 return Image.alpha_composite(im,l)

def frame(t):
 if t<6.65:
  im=world_cam(t)
  if t<3.7:im=title(im,'WHY DO THE KEYS BEND?',y=147,size=53)
  # Pin actual approximate Florida location on the *georeferenced* flat atlas.
  if t>=3.4:
   cx=1120;cy=1750
   # transform map lon/lat pin via same camera, not an independent screen position.
   knots=[(0,1450,1900,1640),(3.2,1370,1910,1270),(6.8,1205,1820,685),(7.7,1190,1790,535)]
   # calculate position using view crop found by world_cam path
   a=knots[1] if t<6.8 else knots[2];b=knots[2] if t<6.8 else knots[3]
   p=smooth((t-a[0])/(b[0]-a[0]));vcx=blend(a[1],b[1],p);vcy=blend(a[2],b[2],p);cw=blend(a[3],b[3],p)
   px=int((cx-vcx)/cw*W+W/2);py=int((cy-vcy)/(cw*H/W)*H+H/2)
   im=halo_marker(im,px,py,t,3.5,28)
   if 90<px<W-155:im=title(im,'FLORIDA',max(220,py-92),41,x=px+80)
 elif t<10.5:
  im=wide_stage(t)
  if t<7.05:
   old=world_cam(t);im=Image.blend(old,im,smooth((t-6.65)/.4))
 elif t<13.97:
  im=reef_stage(t)
  if t<10.85:im=Image.blend(wide_stage(t),im,smooth((t-10.5)/.35))
 elif t<17.75:
  im=macro_stage(t)
  if t<14.28:im=Image.blend(reef_stage(t),im,smooth((t-13.97)/.31))
 elif t<26.05:
  im=reef_stage(t)
  if t<18.1:im=Image.blend(macro_stage(t),im,smooth((t-17.75)/.35))
 elif t<37.17:
  im=macro_stage(t)
  if t<26.4:im=Image.blend(reef_stage(t),im,smooth((t-26.05)/.35))
 elif t<40.87:
  im=bridge_stage(t)
  if t<37.47:im=Image.blend(macro_stage(t),im,smooth((t-37.17)/.30))
 elif t<52.3:
  im=macro_stage(t)
  if t<41.15:im=Image.blend(bridge_stage(t),im,smooth((t-40.87)/.28))
 elif t<55.65:
  im=wide_stage(t)
  if t<52.65:im=Image.blend(macro_stage(t),im,smooth((t-52.3)/.35))
 elif t<59.16:
  im=reef_stage(t)  # editorial insert: hard cut, no ghosted double-map dissolve
 else:
  im=wide_stage(t)
  if t>59.4:im=title(im,'REEFS  •  ROCK  •  SEA',y=176,size=54)
 im=caption(im,t)
 return im.convert('RGB')

def decode(path):
 raw=subprocess.check_output([FF,'-v','error','-i',str(path),'-ac','1','-ar','48000','-f','f32le','pipe:1'])
 return np.frombuffer(raw,'<f4').copy()

def mix():
 voice=decode(n.VOICE);waves=decode(HERE/'assets/v2_ambient/ambience_waves_cc0.ogg')
 nframes=round(DUR*48000)
 a=np.zeros(nframes,np.float32);a[:len(voice)]=voice[:min(len(voice),nframes)]
 bed=np.tile(waves,math.ceil(nframes/len(waves)))[:nframes];bed=bed-bed.mean()
 # Recorded surf is 19 dB below voice RMS; no procedural score or copied audio.
 rms=lambda v:float(np.sqrt(np.mean(v*v)))
 bed*=min(1,.11*max(.02,rms(a))/max(.001,rms(bed)))
 fade=np.minimum(1,np.arange(nframes)/(.6*48000))*np.minimum(1,np.arange(nframes)[::-1]/(.6*48000));bed*=fade
 a=sosfiltfilt(butter(2,85,btype='highpass',fs=48000,output='sos'),a).astype(np.float32)
 out=np.stack((a*.91+bed*.75,a*.95+bed),axis=-1)
 peak=float(np.max(np.abs(out)));out*=min(1,.78/max(.001,peak))
 path=CACHE/'v3_voice_surf_mix.wav'
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(48000);w.writeframes(np.int16(np.clip(out,-.98,.98)*32767).tobytes())
 return path

def render():
 aud=mix();total=round(DUR*FPS)
 print('render',DUR,total,'frames',flush=True)
 cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','pipe:0','-i',str(aud),'-map','0:v','-map','1:a',
      '-c:v','libx264','-threads','2','-preset','medium','-crf','18','-maxrate','9M','-bufsize','18M','-pix_fmt','yuv420p','-af','loudnorm=I=-16:TP=-1.5:LRA=8','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(OUT)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for k in range(total):
   p.stdin.write(frame(k/FPS).tobytes())
   if k%150==0:print(k,'/',total,flush=True)
  p.stdin.close()
  if p.wait()!=0:raise RuntimeError('encode failed')
 finally:
  if p.poll() is None:p.kill()
 print('FINAL',OUT,OUT.stat().st_size)
if __name__=='__main__':render()

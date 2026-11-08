#!/usr/bin/env python3
"""V4 Florida private review: only image-to-image key stills, editorial camera moves and sound.
No cutout rigging, procedural limbs, hand-drawn door, character transforms or map animation.
"""
from pathlib import Path
import math, subprocess, wave
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
HERE=Path(__file__).resolve().parent
EP=HERE.parent
PREV=EP/'v3_dark2d/assets'
A=HERE/'assets'
TMP=HERE/'render_cache'; TMP.mkdir(exist_ok=True)
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS=720,1280,24
DUR=38.5
FONT=ImageFont.truetype(str(EP.parents[1]/'assets/fonts/DMSans.ttf'),32) if (EP.parents[1]/'assets/fonts/DMSans.ttf').exists() else ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)
PLATES={
 'exterior':PREV/'hotel_exterior.png','suite':PREV/'suite.png','hall_open':PREV/'hallway.png','balcony':PREV/'balcony.png',
 'alive':A/'02_businessman_alive.png','slumped':A/'02b_businessman_slumped.png',
 'investigator_suite':A/'03_investigator_suite.png','door_half':A/'04b_door_halfway.png',
 'door_closed':A/'04_door_closed.png','investigator_balcony':A/'05_investigator_balcony.png',
 'wife':A/'06_wife_hallway.png','wife_turn':A/'06b_wife_turn.png','partner':A/'07_partner_hallway.png'
}
IMAGES={k:Image.open(v).convert('RGB') for k,v in PLATES.items()}
# All onscreen action comes from alternate generated images. Continuity cuts use short
# defocus/whip edits, never geometrically inventing intermediate character or door frames.
# start, end, image, starting/ending zoom, starting/ending source normalized focal points, title
SHOTS=[
 (0,2.2,'exterior',1.02,1.33,(.50,.51),(.62,.34),'THE LOCKED SUITE'),
 (2.2,3.65,'alive',1.05,1.17,(.50,.53),(.53,.53),''),
 (3.65,5.2,'slumped',1.03,1.30,(.54,.56),(.50,.62),''),
 (5.2,5.75,'hall_open',1.03,1.08,(.51,.49),(.56,.49),'NO FORCED ENTRY'),
 (5.75,6.25,'door_half',1.08,1.19,(.56,.49),(.60,.50),'NO FORCED ENTRY'),
 (6.25,9.5,'door_closed',1.20,1.55,(.60,.50),(.54,.56),'NO FORCED ENTRY'),
 (9.5,10.75,'suite',1.32,1.67,(.20,.65),(.19,.73),'THE WATCH'),
 (10.75,12.65,'investigator_suite',1.1,1.38,(.49,.58),(.36,.65),'THE WATCH'),
 (12.65,13.45,'balcony',1.05,1.15,(.38,.55),(.42,.60),'FOOTPRINTS'),
 (13.45,15.2,'investigator_balcony',1.07,1.32,(.49,.58),(.45,.69),'FOOTPRINTS'),
 (15.2,17.2,'suite',1.48,1.92,(.67,.42),(.66,.47),'THE BALCONY DOOR'),
 (17.2,18.63,'wife',1.12,1.35,(.51,.53),(.52,.53),'THE WIFE'),
 (18.63,20.22,'wife_turn',1.30,1.47,(.51,.53),(.52,.52),'THE WIFE'),
 (20.22,24.3,'partner',1.06,1.36,(.51,.53),(.50,.49),'THE BUSINESS PARTNER'),
 (24.3,25.38,'investigator_balcony',1.18,1.46,(.54,.61),(.57,.65),'THE THREAD'),
 (25.38,27.25,'balcony',1.55,2.2,(.69,.51),(.70,.56),'THE THREAD'),
 (27.25,30.1,'balcony',2.10,2.42,(.70,.56),(.70,.55),''),
 (30.1,32.5,'investigator_suite',1.20,1.50,(.40,.62),(.31,.68),''),
 (32.5,33.52,'suite',1.64,2.10,(.20,.71),(.20,.74),''),
 (33.52,34.6,'suite',2.15,3.12,(.20,.74),(.21,.75),''),
 (34.6,38.5,'exterior',3.65,1.02,(.64,.32),(.50,.51),'')
]

def ease(x):
 x=max(0,min(1,x));return x*x*(3-2*x)

def crop(im,zoom,focus):
 iw,ih=im.size;cw=iw/zoom;ch=ih/zoom
 cx=focus[0]*iw;cy=focus[1]*ih
 return im.transform((W,H),Image.Transform.EXTENT,(cx-cw/2,cy-ch/2,cx+cw/2,cy+ch/2),Image.Resampling.BICUBIC)

def frame(t):
 sh=next(s for s in SHOTS if s[0]<=t<s[1]) if t<DUR else SHOTS[-1]
 a,b,key,z0,z1,p0,p1,label=sh
 u=(t-a)/(b-a)
 # Final move has an aggressive initial retreat and long eased landing.
 e=ease(u) if a<34 else 1-(1-u)**2.45
 z=z0+(z1-z0)*e
 c=(p0[0]+(p1[0]-p0[0])*e,p0[1]+(p1[1]-p0[1])*e)
 im=crop(IMAGES[key],z,c)
 # Two-frame blur hides AI perspective differences at the three captured door states.
 if key in ('door_half','door_closed') and t-a<.085:
  im=im.filter(ImageFilter.GaussianBlur(7*(1-ease((t-a)/.085))))
 if a>=34.6 and t<34.78:
  im=Image.blend(im,Image.new('RGB',(W,H),(166,180,176)),.09*(1-ease((t-34.6)/.18)))
 if label:
  d=ImageDraw.Draw(im,'RGBA')
  fade=min(1,ease((t-a)/.18),ease((b-t)/.22))
  box=d.textbbox((0,0),label,font=FONT)
  width=box[2]-box[0];x=(W-width)//2
  d.rounded_rectangle((x-21,92,x+width+21,154),radius=9,fill=(3,15,20,int(200*fade)))
  d.text((x,102),label,font=FONT,fill=(252,239,216,int(255*fade)),stroke_width=1,stroke_fill=(4,11,14,int(255*fade)))
 if t<2.2:
  d=ImageDraw.Draw(im,'RGBA')
  d.text((24,H-47),'FICTIONAL DRAMATIZATION',font=SMALL,fill=(240,231,214,210))
 return im

def read_audio(path,sr=48000):
 p=subprocess.run([FF,'-loglevel','error','-i',str(path),'-ac','1','-ar',str(sr),'-f','f32le','pipe:1'],capture_output=True,check=True)
 return np.frombuffer(p.stdout,dtype='<f4').copy()

def audio_mix():
 sr=48000;n=int(sr*DUR);rng=np.random.default_rng(1948)
 v=read_audio(EP/'audio/voice_edit_1934.mp3');b=read_audio(EP/'audio/percussion_air_draft.mp3')
 a=np.zeros(n,np.float32);a[:min(n,len(v))]+=.9*v[:n];a[:min(n,len(b))]+=.40*b[:n]
 hiss=rng.normal(0,1,n).astype(np.float32);a+=.006*(hiss-.5*np.roll(hiss,1))
 def lay(t,sig):
  o=int(t*sr);m=min(n-o,len(sig))
  if m>0:a[o:o+m]+=sig[:m]
 def impact(t,amp=.13):
  z=np.arange(int(.68*sr),dtype=np.float32)/sr
  x=(np.sin(2*np.pi*(68*z-11*z*z))*.7+rng.normal(0,.12,len(z)))*np.exp(-z*11)*amp
  lay(t,x)
 def whoosh(t,dur=.45,amp=.035):
  z=np.arange(int(dur*sr),dtype=np.float32)/sr;r=rng.normal(0,1,len(z)).astype(np.float32)
  lay(t,(r+np.roll(r,1)+np.roll(r,3))*.33*(np.sin(np.pi*z/dur)**2)*amp)
 for t in (2.17,3.62,5.18,9.47,12.63,15.18,17.18,20.18,24.27,27.2,30.08,33.5,34.57):whoosh(t)
 # Organic wood hinge from noise and a falling spectral creak; cut to the photographed closed state on slam.
 z=np.arange(int(.82*sr),dtype=np.float32)/sr
 creak=(np.sin(2*np.pi*(183*z-42*z*z))+.3*np.sin(2*np.pi*(401*z-86*z*z)))*.028
 lay(5.42,creak*np.sin(np.pi*z/.82)**1.5)
 impact(6.24,.32)
 for at in (7.2,7.72,8.22,13.5,14.12):impact(at,.035)
 for at in (3.63,10.72,18.62,25.36,33.52):impact(at,.085)
 impact(34.62,.23)
 for at in (.04,34.65):
  z=np.arange(int(1.65*sr),dtype=np.float32)/sr
  r=rng.normal(0,1,len(z)).astype(np.float32)
  soft=(r+np.roll(r,5)+np.roll(r,12))/3
  lay(at,soft*np.exp(-z*2)*.035+np.sin(2*np.pi*49*z)*np.exp(-z*3)*.06)
 end=int(34.62*sr);a[end:]+=.012*rng.normal(0,1,n-end).astype(np.float32)*np.linspace(0,1,n-end)
 a=np.tanh(a*1.12)
 a[-int(.15*sr):]*=np.linspace(1,0,int(.15*sr))
 peak=max(.01,float(np.max(np.abs(a))))
 if peak>.94:a*=.94/peak
 out=TMP/'image_motion_mix.wav'
 with wave.open(str(out),'wb') as w:
  w.setframerate(sr);w.setsampwidth(2);w.setnchannels(1);w.writeframes(np.int16(a*32767).tobytes())
 return out

if __name__=='__main__':
 wav=audio_mix();raw=TMP/'silent.mp4'
 cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
      '-r',str(FPS),'-i','pipe:0','-c:v','libx264','-preset','veryfast','-crf','18',
      '-pix_fmt','yuv420p','-movflags','+faststart',str(raw)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for k in range(round(FPS*DUR)):
   p.stdin.write(frame(k/FPS).tobytes())
   if k%(5*FPS)==0:print('frame',k,flush=True)
  p.stdin.close()
  if p.wait()!=0:raise RuntimeError('video encoder error')
 finally:
  if p.poll() is None:p.kill()
 final=HERE/'FLORIDA_V4_IMAGE_MOTION_PRIVATE_REVIEW_720x1280.mp4'
 subprocess.run([FF,'-y','-loglevel','error','-i',str(raw),'-i',str(wav),'-map','0:v','-map','1:a',
       '-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(final)],check=True)
 print(final,final.stat().st_size,flush=True)

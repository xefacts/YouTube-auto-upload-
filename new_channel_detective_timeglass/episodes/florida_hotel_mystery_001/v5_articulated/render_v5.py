#!/usr/bin/env python3
"""V6 2.5D Florida private review (V5 renderer evolved in place).
All four on-screen actors use a canonical master and an alternate pose from that same identity.
Subtle face/hand/arm/leg movement is a smooth local image warp of ORIGINAL 2D art,
not replacement faces. The existing photographic plates keep independent camera depth.
"""
from pathlib import Path
import importlib.util,subprocess,math,shutil,wave
import numpy as np
import cv2
from scipy.ndimage import binary_fill_holes, gaussian_filter
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import imageio_ffmpeg
HERE=Path(__file__).resolve().parent
EP=HERE.parent
V4=EP/'v4_image_motion/render_image_motion.py'
spec=importlib.util.spec_from_file_location('image_cut',V4)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
# The replacement closed-door keyframe retains the near walnut door and matches the half-closed plate.
old.IMAGES['door_closed']=Image.open(HERE/'assets/door_closed_match.png').convert('RGB')
# Two matching photographed lock states replace the static balcony-door still.
old.IMAGES['bolt_open']=Image.open(HERE/'assets/balcony_bolt_retracted.png').convert('RGB')
old.IMAGES['bolt_closed']=Image.open(HERE/'assets/balcony_bolt_engaged.png').convert('RGB')
old.SHOTS=[shot for shot in old.SHOTS if shot[0]!=15.2]
old.SHOTS += [
 (15.2,15.96,'bolt_open',1.02,1.13,(.49,.51),(.50,.50),'THE BALCONY LATCH'),
 (15.96,17.2,'bolt_closed',1.13,1.32,(.50,.50),(.53,.50),'THE BALCONY LATCH')]
old.SHOTS.sort(key=lambda shot:shot[0])
CACHE=HERE/'render_cache';CACHE.mkdir(exist_ok=True)
A=HERE/'assets'
W,H,FPS,DUR=old.W,old.H,old.FPS,old.DUR
FF=imageio_ffmpeg.get_ffmpeg_exe()
FONT=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',29)
SMALL=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',14)

# Appearance/style anchored by these eight generated stills. Never swap faces within a role.
ROLE={
 'businessman':('businessman_master','businessman_watch_pose'),
 'investigator':('investigator_master','investigator_reach_pose'),
 'wife':('wife_master','wife_turn_pose'),
 'partner':('partner_master','partner_case_pose')
}

def isolate(name):
 im=Image.open(A/(name+'.png')).convert('RGB');rgb=np.array(im)
 fg=np.any(rgb<235,axis=2)
 fg=binary_fill_holes(fg)
 alpha=np.uint8(np.clip(gaussian_filter(fg.astype(np.float32),.65),0,1)*255)
 ys,xs=np.where(alpha>110)
 bb=(max(0,int(xs.min())-3),max(0,int(ys.min())-3),min(im.width,int(xs.max())+4),min(im.height,int(ys.max())+4))
 im=im.convert('RGBA');im.putalpha(Image.fromarray(alpha,'L'))
 return im.crop(bb)
SPRITES={k:isolate(k) for pair in ROLE.values() for k in pair}
SPRITES['investigator_door_pose']=isolate('investigator_door_pose')

def ease(t):
 return old.ease(t)

def pose_role(t,role):
 base,act=ROLE[role]
 if role=='businessman': return act if t>=2.95 else base
 if role=='wife':return act if t>=18.5 else base
 if role=='partner':return act if t>=21.85 else base
 if role=='investigator':
  if 7.25<=t<9.5:return 'investigator_door_pose' if t>=7.92 else base
  if 13.40<=t<15.2 or 24.3<=t<25.38:return act if t>=13.7 else base
  return act if 11.85<=t<12.65 or 31.3<=t<32.5 else base
 return base

def person(t,role,height):
 """Apply bounded image warps at head, wrists, torso and knees; not a static zoom."""
 name=pose_role(t,role)
 im=SPRITES[name];w=round(im.width*height/im.height)
 h=int(height)
 im=im.resize((w,h),Image.Resampling.LANCZOS)
 arr=np.asarray(im).copy()
 yy,xx=np.mgrid[:h,:w].astype(np.float32)
 # Localized separate part displacements. Smooth kernels prevent torn shoulders/wrists.
 def blob(cx,cy,sx,sy):return np.exp(-.5*((xx-cx*w)/(sx*w))**2-.5*((yy-cy*h)/(sy*h))**2)
 phase=t*2*math.pi
 head=blob(.5,.16,.21,.13); leftarm=blob(.15,.49,.15,.26); rightarm=blob(.86,.49,.14,.26)
 torso=blob(.5,.42,.24,.23);legl=blob(.38,.82,.15,.22);legr=blob(.62,.82,.15,.22)
 # Hand/arm shifts are visible on mobile but remain bounded (roughly 2% of height).
 dx=(5.0*math.sin(phase*.68)*head + 10.0*math.sin(phase*.93+.6)*leftarm
     -10.0*math.sin(phase*.93+.6)*rightarm +5.0*math.sin(phase*.63)*legl-5.0*math.sin(phase*.63)*legr)
 dy=(4.0*math.sin(phase*.55)*head + 3.5*math.sin(phase*.7)*torso
     +12.0*math.sin(phase*.93+.7)*leftarm-11.0*math.sin(phase*.93+.7)*rightarm)
 # cv2.remap moves original artwork; border is transparent, not a duplicated silhouette.
 warped=cv2.remap(arr,xx-dx.astype(np.float32),yy-dy.astype(np.float32),
                  cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
 return Image.fromarray(warped,'RGBA')

# Source image space placements are consistent across the shot camera tracks.
PRESENT={
 'alive':('suite','businessman',490,1315,710),
 'door_closed':('door_closed','investigator',354,1260,850),
 'investigator_balcony':('balcony','investigator',470,1295,700),
 'wife':('hall_open','wife',399,1170,770),
 'wife_turn':('hall_open','wife',399,1170,770),
 'partner':('hall_open','partner',410,1185,770)
}

def background_with_person(t,key):
 plate,role,x,y,h=PRESENT[key]
 bg=old.IMAGES[plate].convert('RGBA')
 # Walk in from offscreen, then use the same investigator's matching reach pose at the handle.
 if key=='door_closed':x=-230+584*ease((t-7.12)/.95)
 # Slight atmospheric distance correction and a cast shadow, independent of the actor image.
 fg=person(t,role,h)
 if key=='door_closed' and pose_role(t,role)=='investigator_door_pose':
  fg=fg.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
 pos=(round(x-fg.width/2),round(y-fg.height))
 shade=Image.new('RGBA',bg.size,(0,0,0,0));sd=ImageDraw.Draw(shade)
 sd.ellipse((pos[0]+fg.width*.08,y-18,pos[0]+fg.width*.92,y+23),fill=(0,0,0,130))
 bg=Image.alpha_composite(bg,shade.filter(ImageFilter.GaussianBlur(13)))
 bg.alpha_composite(fg,pos)
 return bg.convert('RGB')

def frame(t):
 sh=next(s for s in old.SHOTS if s[0]<=t<s[1]) if t<DUR else old.SHOTS[-1]
 a,b,key,z0,z1,p0,p1,label=sh
 im=background_with_person(t,key) if key in PRESENT else old.IMAGES[key]
 u=(t-a)/(b-a)
 e=ease(u) if a<34 else 1-(1-u)**2.45
 z=z0+(z1-z0)*e;c=(p0[0]+(p1[0]-p0[0])*e,p0[1]+(p1[1]-p0[1])*e)
 image=old.crop(im,z,c)
 if key in ('door_half','door_closed') and t-a<.085:
  image=image.filter(ImageFilter.GaussianBlur(7*(1-ease((t-a)/.085))))
 if a>=34.6 and t<34.78:
  image=Image.blend(image,Image.new('RGB',(W,H),(166,180,176)),.09*(1-ease((t-34.6)/.18)))
 if label:
  d=ImageDraw.Draw(image,'RGBA');alpha=min(1,ease((t-a)/.18),ease((b-t)/.22))
  bb=d.textbbox((0,0),label,font=FONT);ww=bb[2]-bb[0];x=(W-ww)//2
  d.rounded_rectangle((x-21,92,x+ww+21,154),radius=9,fill=(3,15,20,int(200*alpha)))
  d.text((x,102),label,font=FONT,fill=(252,239,216,int(255*alpha)),stroke_width=1,stroke_fill=(4,11,14,int(255*alpha)))
 if t<2.2:
  ImageDraw.Draw(image,'RGBA').text((24,H-47),'FICTIONAL DRAMATIZATION',font=SMALL,fill=(240,231,214,210))
 return image

def sync_new_sfx(mix_copy):
 """Add restrained brass-lock and door-handle foley to the previously verified mix."""
 with wave.open(str(mix_copy),'rb') as w:
  sr=w.getframerate();audio=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(np.float32)/32768
 rng=np.random.default_rng(1949)
 for at,amp in ((8.06,.033),(8.18,.023),(15.96,.085),(16.12,.024)):
  length=int(sr*.19);z=np.arange(length,dtype=np.float32)/sr
  click=(np.sin(2*np.pi*1850*z)+.45*np.sin(2*np.pi*3250*z)+.25*rng.normal(0,1,length))*np.exp(-z*48)*amp
  ix=int(at*sr);audio[ix:ix+length]+=click
 audio=np.clip(audio,-.96,.96)
 with wave.open(str(mix_copy),'wb') as w:
  w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.int16(audio*32767).tobytes())

if __name__=='__main__':
 mix=old.audio_mix();mix_copy=CACHE/'mix.wav';shutil.copyfile(mix,mix_copy)
 sync_new_sfx(mix_copy)
 raw=CACHE/'silent.mp4'
 cmd=[FF,'-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
       '-r',str(FPS),'-i','pipe:0','-c:v','libx264','-preset','veryfast','-crf','18',
       '-pix_fmt','yuv420p','-movflags','+faststart',str(raw)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 try:
  for k in range(round(DUR*FPS)):
   p.stdin.write(frame(k/FPS).tobytes())
   if k%(5*FPS)==0:print('frame',k,flush=True)
  p.stdin.close()
  if p.wait()!=0:raise RuntimeError('video encoder error')
 finally:
  if p.poll() is None:p.kill()
 final=HERE/'FLORIDA_V6_CHARACTER_AND_LATCH_PRIVATE_REVIEW_720x1280.mp4'
 subprocess.run([FF,'-y','-loglevel','error','-i',str(raw),'-i',str(mix_copy),
    '-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','192k',
    '-movflags','+faststart','-shortest',str(final)],check=True)
 print(final,final.stat().st_size,flush=True)

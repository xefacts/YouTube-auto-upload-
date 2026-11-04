"""V3-only flat map assets. No spherical projection and no legacy video import.
Wide/macro plates are illustrative; the world relief is georeferenced Mercator.
"""
from pathlib import Path
import cv2,numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;A=HERE/'assets';W,H=1080,1920
FONT=str(HERE.parent/'assets/fonts/DMSans.ttf');BOLD=str(HERE.parent/'assets/fonts/Anton-Regular.ttf')
MAP_BASE=Image.open(A/'v3_wide_base.png').convert('RGBA')
REGION=Image.open(A/'v3_region_glow_rgba.png').convert('RGBA')
MAP_REGION=Image.alpha_composite(MAP_BASE,REGION)
MACRO=Image.open(A/'florida_keys_macro_relief.png').convert('RGB').resize((W,H),Image.Resampling.LANCZOS).convert('RGBA')

def smooth_curve(pts,steps=18):
 p=[pts[0]]+pts+[pts[-1]];out=[]
 for i in range(1,len(p)-2):
  a,b,c,d=p[i-1:i+3]
  for j in range(steps):
   t=j/steps;t2=t*t;t3=t2*t
   x=.5*((2*b[0])+(-a[0]+c[0])*t+(2*a[0]-5*b[0]+4*c[0]-d[0])*t2+(-a[0]+3*b[0]-3*c[0]+d[0])*t3)
   y=.5*((2*b[1])+(-a[1]+c[1])*t+(2*a[1]-5*b[1]+4*c[1]-d[1])*t2+(-a[1]+3*b[1]-3*c[1]+d[1])*t3)
   out.append((x,y))
 out.append(pts[-1]);return out

MACRO_KNOTS=[(860,670),(803,820),(735,918),(670,1040),(555,1115),(480,1180),(367,1252),(250,1323)]
MACRO_CURVE=smooth_curve(MACRO_KNOTS)
raw=np.asarray(Image.open(A/'globe_nasa/earth-clouds-2048.jpg').convert('L'))
patch=cv2.resize(raw[260:690,70:620],(W,H),interpolation=cv2.INTER_LINEAR)
patch=cv2.GaussianBlur(patch,(0,0),17)
alpha=np.uint8(np.clip((patch.astype(np.float32)-105)*.22,0,45))
CLOUD_MAP=Image.new('RGBA',(W,H),(239,247,248,0))
CLOUD_MAP.putalpha(Image.fromarray(alpha))

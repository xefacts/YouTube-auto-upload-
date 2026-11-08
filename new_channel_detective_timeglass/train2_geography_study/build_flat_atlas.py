#!/usr/bin/env python3
"""Build a georeferenced Mercator flat relief atlas from public-domain Natural Earth.
Source: github.com/msupino/NavigationApp/docs/relief z0-4.pack + index.json;
never contains pixels from the user's reference videos.
"""
from pathlib import Path
import json,io,numpy as np,cv2
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];SOURCE=ROOT/'work/relief';OUT=Path(__file__).resolve().parent/'assets/v3_world_relief_4096.png'
idx=json.loads((SOURCE/'index.json').read_text());p=idx['packs'][0];n=16;z=4
start=sum(4**zz for zz in range(z));raw=(SOURCE/p['file']).read_bytes()
out=Image.new('RGB',(4096,4096))
for x in range(n):
 for y in range(n):
  i=start+x*n+y
  b=raw[p['offsets'][i]:p['offsets'][i+1]]
  out.paste(Image.open(io.BytesIO(b)).convert('RGB'),(256*x,256*y))
a=np.asarray(out,dtype=np.float32).copy()
# Grade relief into dark bathymetric teal, earth-olive land. Gentle tonal
# transforms keep the source coastline and ocean-floor texture readable.
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2]
sea=(b>r*1.055)&(b>g*.99)
sea_rgb=np.stack((5+r*.13,15+g*.25,28+b*.39),axis=2)
land_rgb=np.stack((r*.79,g*.76,b*.64),axis=2)
# Original NASA Blue Marble color overlays the Natural Earth relief where land
# exists, adding satellite vegetation/terrain variation without copying refs.
nasa=ROOT/'new_channel_detective_timeglass/train2_geography_study/assets/globe_nasa/earth-day-2048.jpg'
day=cv2.cvtColor(cv2.imread(str(nasa)),cv2.COLOR_BGR2RGB)
xs=np.arange(4096,dtype=np.float32)*2048/4096
ys=np.arange(4096,dtype=np.float32);lat=np.arctan(np.sinh(np.pi*(1-2*ys/4096)))
ys=(.5-lat/np.pi)*1023
MX,MY=np.meshgrid(xs,ys);projected=cv2.remap(day,MX,MY,cv2.INTER_LINEAR).astype(np.float32)
land_rgb=land_rgb*.24+projected*.76
mix=np.where(sea[:,:,None],sea_rgb,land_rgb)
Image.fromarray(np.uint8(np.clip(mix,0,255)),'RGB').save(OUT,optimize=True)
print(OUT,OUT.stat().st_size)

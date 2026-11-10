import sys, time
import numpy as np
from PIL import Image
import scene as SC
from engine import render
W, H = 400, 711
sheet = Image.new("RGB", (W*4, H*2), (0,0,0))
tt=time.time()
for i,(name, fn) in enumerate(SC.SHOTS):
    t0=time.time(); objs, cam, kw = fn(0.55)
    img = render(objs, cam, W, H, **kw); print(name, "%.2fs"%(time.time()-t0))
    sheet.paste(Image.fromarray(img), ((i%4)*W, (i//4)*H))
sheet.save("/tmp/contact.png"); print("total %.1f"%(time.time()-tt))

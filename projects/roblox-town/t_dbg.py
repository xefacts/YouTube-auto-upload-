import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon-time-short"))
from PIL import Image, ImageDraw
import boxes
from boxes import Cam, Scene3D
from draw2d import Pen

W, H = 400, 400
img = Image.new("RGB", (W, H), (170, 200, 230))
d = ImageDraw.Draw(img)
p = Pen(d, s=1.0, img=img)
cam = Cam(0, 0, -5.0, 0, 0.0, 45, w=W, h=H)
sc = Scene3D(img, p, cam)
sc.box((0, 0, 0), (0.52, 0.50, 0.52), (243, 199, 165), rot=math.pi)
sc.box((0, 0.02, -0.272), (0.062, 0.085, 0.02), (54, 44, 58))
orig_poly = p.poly
def spy(pts, col, **kw):
    print("poly", [tuple(round(c,1) for c in q) for q in pts], col)
    return orig_poly(pts, col, **kw)
p.poly = spy
sc.flush()
img.save("out/stills/t_dbg.png")
print("saved")

import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon-time-short"))
from PIL import Image, ImageDraw
from boxes import Cam, Scene3D, character
from draw2d import Pen
import scenes_town as S

W, H = 540, 960
out = []
for facing in (0, 180):
    img = Image.new("RGB", (W, H), (170, 200, 230))
    d = ImageDraw.Draw(img)
    p = Pen(d, s=1.0, img=img)
    cam = Cam(0, 1.5, -5.0, 0, -0.02, 45, w=W, h=H)
    sc = Scene3D(img, p, cam)
    sc.floor(0.0, (128, 150, 118))
    character(sc, 0, 0, s=1.0, spec=S.KID, pose="idle", t=0.4, facing=facing)
    sc.flush()
    out.append(img)
sheet = Image.new("RGB", (W * 2, H))
for i, im in enumerate(out):
    sheet.paste(im, (i * W, 0))
sheet.resize((W, H // 2)).save("out/stills/t_char.png")
print("ok")

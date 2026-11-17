import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cartoon-time-short"))
from PIL import Image, ImageDraw
from boxes import Cam, Scene3D, character
from draw2d import Pen
import scenes_town as S

W, H = 360, 460
rows = []
exprs = ["smile", "grin", "shock", "sad", "worried", "idle"]
for expr in exprs:
    img = Image.new("RGB", (W, H), (150, 190, 226))
    d = ImageDraw.Draw(img); p = Pen(d, s=1.0, img=img)
    cam = Cam(0, 1.66, -1.55, 0, -0.03, 40, w=W, h=H)
    sc = Scene3D(img, p, cam, haze=None)
    character(sc, 0, 0, s=1.0, spec=dict(S.KID, expr=expr), pose="idle", t=0.3, facing=180)
    sc.flush(); rows.append(img)
sheet = Image.new("RGB", (W * len(rows), H))
for i, im in enumerate(rows):
    sheet.paste(im, (i * W, 0))
sheet.resize((W * len(rows) // 2, H // 2), Image.LANCZOS).save("out/stills/faces.png")
print("ok")

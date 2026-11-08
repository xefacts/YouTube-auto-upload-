#!/usr/bin/env python3
"""Contact sheet: one frame from the middle of every shot, labelled."""
import json, os, sys
from PIL import Image, ImageDraw, ImageFont

TL = json.load(open("work/timeline.json"))
SRC = sys.argv[1] if len(sys.argv) > 1 else "/tmp/gframes60"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out/storyboard.jpg"
COLS = 4
TW, TH = 300, 533
PAD = 10
FS = 20

rows = (len(TL["shots"]) + COLS - 1) // COLS
sheet = Image.new("RGB", (COLS * (TW + PAD) + PAD, rows * (TH + PAD + 26) + PAD), (14, 14, 16))
d = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", FS)
except Exception:
    font = ImageFont.load_default()

for i, s in enumerate(TL["shots"]):
    mid = s["f0"] + (s["f1"] - s["f0"]) // 2
    mid -= mid % 3
    p = os.path.join(SRC, "f%05d.jpg" % mid)
    x = PAD + (i % COLS) * (TW + PAD)
    y = PAD + (i // COLS) * (TH + PAD + 26)
    if os.path.exists(p):
        sheet.paste(Image.open(p).resize((TW, TH)), (x, y))
    d.text((x + 2, y + TH + 4), "%s  f%d  %s" % (s["id"], mid, s["light"]), fill=(235, 210, 150), font=font)

sheet.save(OUT, quality=90)
print(OUT, sheet.size)

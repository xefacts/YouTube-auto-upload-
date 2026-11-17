import sys
from PIL import Image
out = sys.argv[1]; files = sys.argv[2:]
cols = 3
ims = [Image.open(f).convert("RGB").resize((360, 640), Image.LANCZOS) for f in files]
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (360 * cols, 640 * rows), (0, 0, 0))
for i, im in enumerate(ims):
    sheet.paste(im, ((i % cols) * 360, (i // cols) * 640))
sheet.save(out); print(out)

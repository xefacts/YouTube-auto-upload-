#!/bin/bash
# usage: ./qa.sh out.jpg frame1 frame2 ...
set -e
OUT=$1; shift
DIR=/tmp/qa_$$
rm -rf "$DIR"; mkdir -p "$DIR"
LIST="$*"
FIRST=$(echo "$LIST" | cut -d' ' -f1)
LAST=$(echo "$LIST" | awk '{print $NF}')
LD_LIBRARY_PATH=/tmp/al2023/lib node render_batch.mjs "$DIR" "$FIRST" "$LAST" 32 0.6 0.6 0.9 >/dev/null
/home/user/.venv/bin/python - "$OUT" "$DIR" $LIST <<'PY'
import sys, os
from PIL import Image
out, d = sys.argv[1], sys.argv[2]
frames = [int(x) for x in sys.argv[3:]]
ims = []
for f in frames:
    p = os.path.join(d, f"f{f:05d}.jpg")
    ims.append(Image.open(p) if os.path.exists(p) else Image.new("RGB", (432, 768), (0, 0, 0)))
w, h = ims[0].size
cols = min(4, len(ims)); rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
for i, im in enumerate(ims):
    sheet.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
sheet.save(out, quality=92)
print("ok", out, sheet.size)
PY
rm -rf "$DIR"

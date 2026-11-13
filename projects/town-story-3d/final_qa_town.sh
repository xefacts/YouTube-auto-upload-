#!/bin/bash
# TOWN STORY FINAL QA — run AFTER render_town.mjs.
# Checks: duration/res/fps, LUFS, true peak, frozen-frame motion fraction,
# caption burn (white text over the night scene), flash peak, web size < 100 MB.
set -e
FF=/tmp/studio_env/bin/ffmpeg
FP=/tmp/studio_env/bin/ffprobe
WEB=/tmp/town_story/Town_Counts_To_Ten_FINAL_1080x1920.mp4
PASS=0; FAIL=0

# 1) container facts
DUR=$($FP -v error -show_entries format=duration -of csv=p=0 "$WEB")
RES=$($FP -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$WEB")
echo "web: dur=${DUR}s res+fps=${RES}"
python3 - "$DUR" << 'PY'
import sys
d = float(sys.argv[1])
print("PASS | duration 79.9-80.1s" if 79.9 <= d <= 80.1 else f"FAIL | duration {d}")
PY

# 2) loudness + true peak
LUFS=$($FF -hide_banner -i "$WEB" -af ebur128=peak=true -f null - 2>&1 | grep -A2 "Integrated loudness" | grep "I:" | awk '{print $2}')
TP=$($FF -hide_banner -i "$WEB" -af ebur128=peak=true -f null - 2>&1 | grep "Peak:" | head -1 | awk '{print $3}')
echo "loudness I=${LUFS} LUFS  true-peak=${TP}"
python3 - "$LUFS" << 'PY'
import sys
v = float(sys.argv[1])
print("PASS | -14.6..-13.6 LUFS" if -14.6 <= v <= -13.6 else f"FAIL | LUFS {v}")
PY

# 3) caption burn during the peek (t=27: white caption pixels over night scene)
$FF -y -v error -ss 27.0 -i "$WEB" -frames:v 1 -f rawvideo -pix_fmt gray /tmp/qa_cap_town.raw
python3 - << 'PY'
import numpy as np
a = np.fromfile('/tmp/qa_cap_town.raw', dtype=np.uint8).reshape(1920, 1080).astype(np.float32)
band = a[1050:1450, :]   # caption zone (MarginV 620 @1080p)
lum = band.mean(); bright = (band > 200).mean()
print(f"caption-zone: bandMean={lum:.1f} brightFrac={bright:.4f}")
print("PASS | caption visible" if bright > 0.008 else "FAIL | no caption pixels")
PY

# 4) flash moment actually white (t=53.0)
$FF -y -v error -ss 53.0 -i "$WEB" -frames:v 1 -f rawvideo -pix_fmt gray /tmp/qa_flash_town.raw
python3 - << 'PY'
import numpy as np
a = np.fromfile('/tmp/qa_flash_town.raw', dtype=np.uint8).reshape(1920, 1080).astype(np.float32)
print(f"flash frame mean={a.mean():.0f}")
print("PASS | flash is white" if a.mean() > 200 else "FAIL | flash not white")
PY

# 5) motion fraction (1 fps sampling; >= 85% frames must differ from previous)
$FF -y -v error -i "$WEB" -vf "fps=1,scale=270:480" -f rawvideo -pix_fmt gray /tmp/qa_mot_town.raw
python3 - << 'PY'
import numpy as np
a = np.fromfile('/tmp/qa_mot_town.raw', dtype=np.uint8).reshape(-1, 480, 270).astype(np.int16)
diff = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
moving = (diff > 0.9).mean()
print(f"motion: frames={len(a)} movingFrac={moving:.3f}")
print("PASS | >= 0.85 moving" if moving >= 0.85 else "FAIL | too many frozen frames")
PY

# 6) web size < 100 MB
SZ=$(stat -c%s "$WEB")
python3 - "$SZ" << 'PY'
import sys
s = int(sys.argv[1])
print(f"web size: {s:,} bytes ({s/1e6:.1f} MB)")
print("PASS | < 100 MB" if s < 100_000_000 else "FAIL | too big")
PY

echo "----"
echo "TOWN QA DONE (see PASS/FAIL lines above)"

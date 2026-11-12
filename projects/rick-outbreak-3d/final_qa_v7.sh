#!/bin/bash
# V7 FINAL QA — run AFTER render_full_v3.mjs + encode_v4_two_pass.sh.
# Checks: duration/res/fps, LUFS, true peak, frozen-frame motion fraction,
# caption burn (white-on-black on the 3.3s BLACK beat), web size < 100 MB.
set -e
FF=/tmp/studio_env/bin/ffmpeg
FP=/tmp/studio_env/bin/ffprobe
WEB=/tmp/rick_study/v3/Rick_Clips_Outbreak_V7_Web_1080x1920.mp4
MASTER=/tmp/rick_study/v3/Rick_Clips_Outbreak_V3_Final_1080x1920.mp4
PASS=0; FAIL=0
ok()   { echo "PASS | $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL | $1 <<< $2"; FAIL=$((FAIL+1)); }

# 1) container facts
DUR=$($FP -v error -show_entries format=duration -of csv=p=0 "$WEB")
RES=$($FP -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate -of csv=p=0 "$WEB")
echo "web: dur=${DUR}s res+fps=${RES}"
python3 - "$DUR" << 'PY'
import sys
d = float(sys.argv[1])
print("PASS | duration 269.3-269.5s" if 269.3 <= d <= 269.5 else f"FAIL | duration {d}")
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

# 3) caption burn on the BLACK beat (t=10.0 -> big white WARNING pixels on pure black)
$FF -y -v error -ss 10.0 -i "$WEB" -frames:v 1 -f rawvideo -pix_fmt gray - /tmp/qa_cap_v7.raw
python3 - << 'PY'
import numpy as np
a = np.fromfile('/tmp/qa_cap_v7.raw', dtype=np.uint8).reshape(1920, 1080).astype(np.float32)
band = a[1100:1500, :]   # caption zone (MarginV 620 from bottom => ~y1080-1300 at 1080p scale x2)
lum = band.mean(); bright = (band > 200).mean()
print(f"caption-on-black: bandMean={lum:.1f} brightFrac={bright:.4f}")
print("PASS | caption visible on black beat" if bright > 0.01 else "FAIL | no caption pixels")
PY

# 4) motion fraction (1 fps sampling; >= 85.5% frames must differ from previous)
$FF -y -v error -i "$WEB" -vf "fps=1,scale=270:480" -f rawvideo -pix_fmt gray - /tmp/qa_mot_v7.raw
python3 - << 'PY'
import numpy as np
a = np.fromfile('/tmp/qa_mot_v7.raw', dtype=np.uint8).reshape(-1, 480, 270).astype(np.int16)
diff = np.abs(a[1:] - a[:-1]).mean(axis=(1, 2))
moving = (diff > 0.9).mean()
print(f"motion: frames={len(a)} movingFrac={moving:.3f}")
print("PASS | >= 85.5% moving" if moving >= 0.855 else "FAIL | too many frozen frames")
PY

# 5) web size < 100 MB
SZ=$(stat -c%s "$WEB")
python3 - "$SZ" << 'PY'
import sys
s = int(sys.argv[1])
print(f"web size: {s:,} bytes ({s/1e6:.1f} MB)")
print("PASS | < 100 MB" if s < 100_000_000 else "FAIL | too big")
PY

echo "----"
echo "V7 QA DONE (see PASS/FAIL lines above)"

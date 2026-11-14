#!/bin/bash
# FINAL QA GATES — The Fire Lookout
set -u
FF=/tmp/studio_env/bin/ffmpeg
FP=/tmp/studio_env/bin/ffprobe
VID="${1:-/tmp/fire_lookout/Fire_Lookout_FINAL_1080x1920.mp4}"
PASS=0; FAIL=0
ok()  { echo "PASS: $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL: $1"; FAIL=$((FAIL+1)); }

echo "=== QA: $VID ==="
[ -f "$VID" ] && ok "file exists ($(du -m "$VID" | cut -f1) MB)" || { bad "file missing"; exit 1; }

# duration
DUR=$($FP -v error -show_entries format=duration -of csv=p=0 "$VID")
if awk -v d="$DUR" 'BEGIN{exit !(d>146.0 && d<147.5)}'; then ok "duration ${DUR}s (expect ~146.5)"; else bad "duration ${DUR}s"; fi

# resolution + fps + pix_fmt
RES=$($FP -v error -select_streams v:0 -show_entries stream=width,height,r_frame_rate,pix_fmt -of csv=p=0 "$VID")
echo "$RES" | grep -q "1080,1920" && ok "resolution 1080x1920" || bad "resolution: $RES"
echo "$RES" | grep -q "30/1" && ok "30 fps" || bad "fps: $RES"
echo "$RES" | grep -q "yuv420p" && ok "pix_fmt yuv420p" || bad "pix_fmt: $RES"

# audio stream
ASTR=$($FP -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels -of csv=p=0 "$VID")
echo "$ASTR" | grep -q "aac,48000,2" && ok "audio aac 48k stereo" || bad "audio: $ASTR"

# loudness
LUFS=$($FF -i "$VID" -af loudnorm=print_format=summary -f null - 2>&1 | grep "Input Integrated" | awk '{print $3}')
if awk -v l="$LUFS" 'BEGIN{exit !(l>-16 && l<-12)}'; then ok "loudness ${LUFS} LUFS (target -14)"; else bad "loudness ${LUFS} LUFS"; fi

# true peak
TP=$($FF -i "$VID" -af loudnorm=print_format=summary -f null - 2>&1 | grep "Input True Peak" | awk '{print $4}')
if awk -v t="$TP" 'BEGIN{exit !(t<-0.9)}'; then ok "true peak ${TP} dBTP"; else bad "true peak ${TP} dBTP"; fi

# black frames mid-video (allow opening/closing fades: scan 3s..142s)
BLACK=$($FF -ss 3 -t 139 -i "$VID" -vf "blackdetect=d=0.25:pic_th=0.98" -an -f null - 2>&1 | grep -c "black_start" || true)
if [ "$BLACK" -eq 0 ]; then ok "no mid-video black gaps >=0.25s"; else bad "$BLACK black gaps detected"; fi

# frozen frames (static >2s mid-video)
FROZ=$($FF -ss 5 -t 135 -i "$VID" -vf "freezedetect=n=-60dB:d=2.5" -an -f null - 2>&1 | grep -c "freeze_start" || true)
if [ "$FROZ" -eq 0 ]; then ok "no frozen segments"; else bad "$FROZ frozen segments"; fi

echo "=== RESULT: $PASS pass / $FAIL fail ==="
[ "$FAIL" -eq 0 ]

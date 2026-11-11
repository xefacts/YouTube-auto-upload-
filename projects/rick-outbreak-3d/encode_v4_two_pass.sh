#!/bin/bash
# V4 two-pass <100MB encode (proven recipe from V3: 81.5 MB @ 4:20.32).
# Input: crf20 master from render_full_v3.mjs; Output: ~81MB web master.
set -e
FF=/tmp/studio_env/bin/ffmpeg
IN=/tmp/rick_study/v3/Rick_Clips_Outbreak_V3_Final_1080x1920.mp4
OUT=/tmp/rick_study/v3/Rick_Clips_Outbreak_V6_Web_1080x1920.mp4
cd /tmp/rick_study/v3
rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree "$OUT"
"$FF" -y -hide_banner -loglevel error -i "$IN" -c:v libx264 -preset medium -b:v 2450k -pass 1 -an -f null /dev/null
"$FF" -y -hide_banner -loglevel error -i "$IN" -c:v libx264 -preset medium -b:v 2450k -pass 2 -c:a aac -b:a 160k -movflags +faststart "$OUT"
ls -la "$OUT"

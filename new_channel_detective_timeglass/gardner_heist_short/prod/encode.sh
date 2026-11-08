#!/bin/bash
# Chunked encode: the host is 2 vCPU / 3.9 GB, a single-pass full-length x264 job
# gets OOM-killed, so encode in 3 chunks and concat.
set -e
FF=/home/user/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2
FR=/tmp/gframes
OUT=out/gardner_heist_10231f.mp4
CH=out/chunks
mkdir -p out "$CH"
TOTAL=10231
STEP=3411
i=0
START=0
while [ "$START" -lt "$TOTAL" ]; do
  END=$((START + STEP - 1))
  [ "$END" -ge "$TOTAL" ] && END=$((TOTAL - 1))
  N=$((END - START + 1))
  printf 'chunk %d  %05d-%05d (%d frames)\n' "$i" "$START" "$END" "$N"
  "$FF" -y -loglevel error -threads 2 -framerate 180 -start_number "$START" -i "$FR/f%05d.jpg" \
    -frames:v "$N" -an \
    -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -profile:v high -level 5.1 \
    -x264-params "threads=2" -g 180 "$CH/c$i.mp4"
  START=$((END + 1))
  i=$((i + 1))
done
: > "$CH/list.txt"
for f in $(seq 0 $((i - 1))); do echo "file 'c$f.mp4'" >> "$CH/list.txt"; done
"$FF" -y -loglevel error -f concat -safe 0 -i "$CH/list.txt" -c copy "$CH/video.mp4"
"$FF" -y -loglevel error -i "$CH/video.mp4" -i work/audio_final.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT"
ls -la "$OUT"

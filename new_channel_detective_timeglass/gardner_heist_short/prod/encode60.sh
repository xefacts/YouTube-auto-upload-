#!/bin/bash
# Gardner short: 60 fps delivery. The master is authored at 180 fps and we sample
# every 3rd frame, so 10231 authored frames -> 3411 delivered frames at 60 fps.
# Chunked x264: single-pass full-length OOMs on this 2 vCPU / 3.9 GB host.
set -e
FF=/home/user/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2
SRC=/tmp/gframes60
SEQ=out/seq60
OUT=out/gardner_heist_60fps.mp4
CH=out/chunks60
rm -rf "$SEQ" "$CH"; mkdir -p "$SEQ" "$CH"
TOTAL=3411
i=0
for f in $(seq 0 3 10230); do printf -v s "%05d" "$i"; ln -s "$SRC/f$(printf %05d "$f").jpg" "$SEQ/f$s.jpg"; i=$((i+1)); done
echo "linked $i frames"
STEP=1200; START=0; c=0
while [ "$START" -lt "$TOTAL" ]; do
  END=$((START + STEP - 1)); [ "$END" -ge "$TOTAL" ] && END=$((TOTAL - 1))
  N=$((END - START + 1))
  echo "chunk $c  $START-$END ($N)"
  "$FF" -y -loglevel error -threads 2 -framerate 60 -start_number "$START" -i "$SEQ/f%05d.jpg" \
    -frames:v "$N" -an -c:v libx264 -preset veryfast -crf 19 -pix_fmt yuv420p \
    -profile:v high -level 5.1 -x264-params "threads=2" -g 120 "$CH/c$c.mp4"
  START=$((END + 1)); c=$((c + 1))
done
: > "$CH/list.txt"; for f in $(seq 0 $((c - 1))); do echo "file 'c$f.mp4'" >> "$CH/list.txt"; done
"$FF" -y -loglevel error -f concat -safe 0 -i "$CH/list.txt" -c copy "$CH/video.mp4"
"$FF" -y -loglevel error -i "$CH/video.mp4" -i work/audio_final.wav \
  -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$OUT"
ls -la "$OUT"

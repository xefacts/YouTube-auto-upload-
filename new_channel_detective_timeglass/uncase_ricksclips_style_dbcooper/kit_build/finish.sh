#!/usr/bin/env bash
# Final encode for the Cooper short. Usage: bash finish.sh [output-name]
set -euo pipefail
cd "$(dirname "$0")"
PY="${PYTHON:-.venv/bin/python}"
FF="$($PY -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')"
NAME="${1:-UNCASE_DB_COOPER_RICKSCLIPS_REMAKE}"
mkdir -p out
F="out/${NAME// /-}.mp4"
"$FF" -hide_banner -v error -y -i mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=7" -ar 48000 -ac 2 mix.wav
"$FF" -hide_banner -v error -y -framerate 30 -start_number 0 -i frames/f%04d.jpg -i mix.wav \
  -map 0:v:0 -map 1:a:0 -vf "scale=1080:1920:flags=lanczos,setsar=1" \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$F"
"$FF" -hide_banner -v error -i "$F" -f null -
"$PY" - <<PY
import subprocess, re
ff='$FF'; f='$F'
p=subprocess.run([ff,'-hide_banner','-i',f,'-f','null','-'],capture_output=True,text=True)
txt=p.stderr
for line in txt.splitlines():
    if 'Stream #' in line and ('Video:' in line or 'Audio:' in line): print(line.strip())
m=re.search(r'Duration: (\d+:\d+:\d+(?:\.\d+)?)',txt)
print('Duration:',m.group(1) if m else 'see ffmpeg output')
PY
"$FF" -hide_banner -v error -i "$F" -vf "freezedetect=n=0.0005:d=0.4,blackdetect=d=0.08" -an -f null - 2>out/qa_video.log || true
"$FF" -hide_banner -v error -i "$F" -af ebur128=peak=true -f null - 2>out/qa_audio.log || true
echo "Freeze/black detections (review intentional night/transition frames if any):"
grep -E 'freeze_start|black_start' out/qa_video.log || true
echo "Final file: $F"

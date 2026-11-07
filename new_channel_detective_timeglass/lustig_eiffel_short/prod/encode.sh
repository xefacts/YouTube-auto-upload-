#!/bin/bash
# Encode /tmp/frames -> final 1080x1920 90fps H.264 (BT.709, limited range) + audio.
set -e
cd "$(dirname "$0")"
FF=/home/user/YouTube-auto-upload-/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2
TOTAL=5178
SEG=$(( (TOTAL + 5) / 6 ))
OUT=out
mkdir -p $OUT/seg $OUT/vid
for i in $(seq 0 5); do
  A=$(( i * SEG )); B=$(( A + SEG - 1 )); [ $B -ge $TOTAL ] && B=$(( TOTAL - 1 ))
  if [ -s $OUT/vid/seg$i.mp4 ]; then echo "seg$i exists, skip"; continue; fi
  echo "--- seg$i  $A-$B"
  $FF -y -v error -framerate 90 -start_number $A -i /tmp/frames/f%05d.jpg -frames:v $(( B - A + 1 )) \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -threads 1 -g 180 \
    -vf "scale=1080:1920:flags=lanczos:in_range=full:out_range=limited,format=yuv420p" \
    -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
    $OUT/vid/seg$i.mp4
done
: > $OUT/vid/list.txt
for i in $(seq 0 5); do echo "file 'seg$i.mp4'" >> $OUT/vid/list.txt; done
$FF -y -v error -f concat -safe 0 -i $OUT/vid/list.txt -c copy $OUT/vid/video_only.mp4
$FF -y -v error -i $OUT/vid/video_only.mp4 -i work/audio_final.wav -c:v copy -c:a aac -b:a 192k -shortest \
  -movflags +faststart -color_range tv -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  out/lustig_eiffel_90fps.mp4
$FF -hide_banner -i out/lustig_eiffel_90fps.mp4 -f null - 2>&1 | tail -1
ls -la out/lustig_eiffel_90fps.mp4

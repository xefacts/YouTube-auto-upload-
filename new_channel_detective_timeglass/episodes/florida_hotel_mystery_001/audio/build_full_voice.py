#!/usr/bin/env python3
"""Make complete selected Adam take at the established 1.075x pace.
No atrim: all 39.23 s of the user's selected source, including its final line.
"""
from pathlib import Path
import subprocess
import imageio_ffmpeg
HERE = Path(__file__).resolve().parent
src = HERE / 'voice_original_1934.mp3'
dst = HERE / 'voice_full_1934_edit.mp3'
ff = imageio_ffmpeg.get_ffmpeg_exe()
subprocess.run([ff, '-hide_banner', '-loglevel', 'error', '-y', '-i', str(src),
                '-af', 'atempo=1.075,highpass=f=70,lowpass=f=11000,acompressor=threshold=0.06:ratio=2:attack=12:release=90,alimiter=limit=0.95',
                '-ar', '48000', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', '192k', str(dst)], check=True)
print(dst, dst.stat().st_size)

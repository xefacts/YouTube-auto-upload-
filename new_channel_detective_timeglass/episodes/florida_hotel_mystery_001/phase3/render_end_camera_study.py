"""Image-only visual ending camera study, not a finished 4K or word-synced episode.
Three original paintings + moving crop and rain overlay; no character animation.
Pillow and imageio-ffmpeg required. Edits to this motion study can be made after review.
"""
from pathlib import Path
import math, subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE=Path(__file__).resolve().parent
EP=HERE.parent
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H,FPS,DUR=720,1280,24,4.5
N=int(FPS*DUR)
imgs=[Image.open(HERE/name).convert('RGB') for name in [
    '12_watch_thread_final_clues.png',
    '13_corner_window_end_push.png',
    '14_wide_hotel_end_pullback.png']]

def smooth(t):return t*t*(3-2*t)
def render(im,z,cx,cy):
    iw,ih=im.size
    cw=min(iw,round(iw/z)); ch=min(ih,round(cw*H/W))
    if ch>ih:
        ch=min(ih,round(ih/z));cw=round(ch*W/H)
    x=min(max(0,round(cx-cw/2)),iw-cw)
    y=min(max(0,round(cy-ch/2)),ih-ch)
    return im.crop((x,y,x+cw,y+ch)).resize((W,H),Image.Resampling.BICUBIC)

def frame(i):
    t=i/FPS
    if t<1.05:
        p=t/1.05; e=p*p
        out=render(imgs[0],1+0.85*e,384+26*e,716+98*e)
        # The macro clue rushes into frame on its last few frames.
        if t>0.88:out=out.filter(ImageFilter.GaussianBlur(2.5*(t-.88)/.17))
    elif t<1.55:
        p=(t-1.05)/.50;e=smooth(p)
        out=render(imgs[1],1.22-.22*e,390-6*e,665+22*e)
        if p<.18:out=out.filter(ImageFilter.GaussianBlur(2*(.18-p)/.18))
    else:
        p=min(1,(t-1.55)/2.38);e=smooth(p)
        out=render(imgs[2],2.35-1.35*e,458-74*e,556+132*e)
        if p<.035:out=out.filter(ImageFilter.GaussianBlur(3*(.035-p)/.035))
    # Separate sparse original rain overlay, timed downward, not animation of people.
    rain=Image.new('RGBA',(W,H));d=ImageDraw.Draw(rain)
    for k in range(68):
        x=(k*327+31*k*k)%W
        y=((k*491+math.floor(t*560))%(H+140))-70
        alpha=18+((k*13)%25)
        d.line((x,y,x+3,y+21+(k%14)),fill=(192,216,213,alpha),width=1)
    out=Image.alpha_composite(out.convert('RGBA'),rain).convert('RGB')
    return out

raw=HERE/'PHASE3_END_CAMERA_SILENT_TMP.mp4'
cmd=[FF,'-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}',
     '-r',str(FPS),'-i','pipe:0','-c:v','libx264','-preset','medium','-crf','21','-pix_fmt','yuv420p',
     '-movflags','+faststart',str(raw)]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
try:
    for i in range(N):
        proc.stdin.write(frame(i).tobytes())
finally:
    proc.stdin.close()
    ret=proc.wait()
if ret:raise RuntimeError(f'ffmpeg video failed: {ret}')

bed=EP/'audio/percussion_air_draft.mp3'
out=HERE/'PHASE3_END_CAMERA_STUDY_720x1280.mp4'
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(raw),'-ss','33.50','-i',str(bed),
                '-filter_complex','[1:a]atrim=end=4.5,asetpts=PTS-STARTPTS,volume=1.2,afade=t=out:st=4.0:d=0.5[a]',
                '-map','0:v','-map','[a]','-t','4.5','-c:v','copy','-c:a','aac','-b:a','160k',
                '-movflags','+faststart',str(out)],check=True)
raw.unlink(missing_ok=True)
print('ENDING STUDY',out,out.stat().st_size)

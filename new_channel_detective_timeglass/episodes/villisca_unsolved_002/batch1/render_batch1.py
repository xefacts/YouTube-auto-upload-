"""Render Batch 1 camera/type animatic from three ORIGINAL reconstruction images.
Not the finished Short or frame-by-frame character animation. Requires ffmpeg and Pillow.
"""
from pathlib import Path
import subprocess
import imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont

HERE=Path(__file__).resolve().parent
EP=HERE.parent
ROOT=HERE.parents[2]
FONT_A=ROOT/'assets/fonts/Anton-Regular.ttf'
FONT_D=ROOT/'assets/fonts/DMSans.ttf'
assert FONT_A.exists() and FONT_D.exists(), (FONT_A,FONT_D)
FF=imageio_ffmpeg.get_ffmpeg_exe()
W,H=1080,1920
LIME=(197,226,112,255);IVORY=(249,243,224,255);COPPER=(198,139,89,255)

def overlay(name,top,bottom,minor):
    im=Image.new('RGBA',(W,H),(0,0,0,0))
    d=ImageDraw.Draw(im)
    # Minimal original editorial system, safe from Shorts top and right-side UI.
    d.rounded_rectangle((78,244,90,302),radius=5,fill=COPPER)
    small=ImageFont.truetype(str(FONT_D),31)
    huge=ImageFont.truetype(str(FONT_A),150)
    d.text((110,258),minor,font=small,fill=IVORY,stroke_width=1,stroke_fill=(16,31,27,200))
    d.text((76,340),top,font=huge,fill=LIME,stroke_width=3,stroke_fill=(8,28,23,210))
    d.text((76,488),bottom,font=huge,fill=IVORY,stroke_width=3,stroke_fill=(8,28,23,210))
    d.line((80,652,500,652),fill=COPPER,width=5)
    dst=HERE/f'{name}_type.png';im.save(dst)
    return dst

styles=[
    ('01_church_departure','TWO','SISTERS','VILLISCA   /   1912',4.7,1.045,'0.13','0.32'),
    ('02_house_arrival','THE','WALK HOME','JUNE 9   /   EVENING',4.9,1.065,'0.28','0.20'),
    ('03_silent_morning','NO','ANSWER','JUNE 10   /   MORNING',4.4,1.125,'0.55','0.40')
]
clips=[]
for idx,(slug,top,bottom,minor,dur,end_zoom,panning,vertical) in enumerate(styles):
    src=HERE/f'{slug}.png'
    typ=overlay(slug,top,bottom,minor)
    dst=HERE/f'work_scene_{idx}.mp4'
    frames=round(dur*24)
    inc=(end_zoom-1)/frames
    z=f'min(max(zoom,pzoom)+{inc:.8f},{end_zoom})'
    # Vertical moves and horizontal camera drifts are NOT the type layer.
    graph=(f'[0:v]zoompan=z=\'{z}\':x=\'(iw-iw/zoom)*{panning}\':y=\'(ih-ih/zoom)*{vertical}\':d=1:s={W}x{H}:fps=24,format=rgba[bg];'
           f'[1:v]format=rgba,fade=t=in:st=0:d=0.28:alpha=1[txt];'
           '[bg][txt]overlay=x=0:y=0:shortest=1:format=auto,format=yuv420p[v]')
    cmd=[FF,'-hide_banner','-loglevel','error','-y','-loop','1','-framerate','24','-i',str(src),'-loop','1','-framerate','24','-i',str(typ),'-filter_complex',graph,'-map','[v]','-t',str(dur),'-r','24','-c:v','libx264','-preset','ultrafast','-crf','20','-pix_fmt','yuv420p',str(dst)]
    print('scene',idx,slug,flush=True);subprocess.run(cmd,check=True)
    clips.append(dst)

listfile=HERE/'clips.txt'
listfile.write_text(''.join(f"file '{p.resolve()}'\n" for p in clips))
joined=HERE/'work_joined.mp4'
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(listfile),'-c','copy',str(joined)],check=True)
voice=EP/'audio/voice_edit_batch1.mp3'
bed=EP/'audio/original_percussion_breath_bed.mp3'
output=HERE/'BATCH1_CAMERA_TYPE_AUDIO_PREVIEW.mp4'
filter_audio='[1:a]atrim=end=14.0,asetpts=PTS-STARTPTS,volume=1.0[v];[2:a]atrim=end=14.0,asetpts=PTS-STARTPTS,volume=1.3[bed];[v][bed]amix=inputs=2:normalize=0,alimiter=limit=0.88[a]'
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(joined),'-i',str(voice),'-i',str(bed),'-filter_complex',filter_audio,'-map','0:v','-map','[a]','-t','14.0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart',str(output)],check=True)
compact=HERE/'BATCH1_REVIEW_1080x1920.mp4'
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-i',str(output),'-c:v','libx264','-preset','medium','-crf','25','-pix_fmt','yuv420p','-c:a','copy','-movflags','+faststart',str(compact)],check=True)
for tmp in [*clips,listfile,joined,output]:
    tmp.unlink(missing_ok=True)
print('DONE',compact,compact.stat().st_size)

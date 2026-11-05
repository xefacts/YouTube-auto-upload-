"""Short image-to-image motion proof (NOT the final film or VO sync).
Door closes, latch slides, wife turns, thread lifts: all from original still-image states.
Requires Pillow and imageio-ffmpeg. Transient frames go to ignored work/.
"""
from pathlib import Path
import subprocess
from PIL import Image
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
EP = HERE.parent
REPO = HERE.parents[3]
TMP = REPO / 'work/florida_action_study'
TMP.mkdir(parents=True, exist_ok=True)
FF = imageio_ffmpeg.get_ffmpeg_exe()
P1, P2 = EP/'phase1', EP/'phase2'
A = HERE/'action_sources'

sequences = [
    ('door', [A/'03a_suite_door_ajar.png', A/'03a_suite_door_ajar.png', A/'03b_suite_door_nearly_closed.png', P1/'03_intact_suite_door.png', P1/'03_intact_suite_door.png']),
    ('latch', [A/'06a_balcony_latch_retracted.png', A/'06a_balcony_latch_retracted.png', P2/'06_balcony_latch_inside.png', P2/'06_balcony_latch_inside.png']),
    ('wife', [P2/'07_wife_neutral_portrait.png', P2/'07_wife_neutral_portrait.png', A/'07a_wife_turns_head.png', A/'07a_wife_turns_head.png']),
    ('thread', [HERE/'09_thread_on_balcony_rail.png', HERE/'09_thread_on_balcony_rail.png', HERE/'10_thread_lift_action.png', HERE/'10_thread_lift_action.png'])
]
clips=[]
for name,images in sequences:
    folder=TMP/name;folder.mkdir(exist_ok=True)
    for i,path in enumerate(images):
        im=Image.open(path).convert('RGB').resize((360,640),Image.Resampling.LANCZOS)
        im.save(folder/f'frame_{i:02d}.png')
    target=TMP/f'{name}.mp4'
    cmd=[FF,'-hide_banner','-loglevel','error','-y','-framerate','3','-i',str(folder/'frame_%02d.png'),
         '-vf','minterpolate=fps=24:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,scale=720:1280:flags=lanczos,format=yuv420p',
         '-c:v','libx264','-preset','medium','-crf','21','-an',str(target)]
    subprocess.run(cmd,check=True);clips.append(target)

lst=TMP/'clips.txt';lst.write_text(''.join(f"file '{p}'\n" for p in clips))
out=HERE/'PHASE3_ACTION_STUDY_720x1280.mp4'
subprocess.run([FF,'-hide_banner','-loglevel','error','-y','-f','concat','-safe','0','-i',str(lst),
                '-c:v','libx264','-preset','medium','-crf','22','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
print('ACTION STUDY',out,out.stat().st_size)

#!/usr/bin/env python3
"""V7: ten additional matching action keys, grounded travel and filmic camera motion.

This is still edited/cutout 2D art, NOT continuous 3D or hand-drawn animation.
Keep V6's sound, photographed setting, fictional disclaimer, and visual-only ending.
"""
from pathlib import Path
import importlib.util
import math
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('florida_v6', HERE / 'render_v5.py')
v6 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v6)
old = v6.old
W, H, FPS, DUR = v6.W, v6.H, v6.FPS, v6.DUR
FF = imageio_ffmpeg.get_ffmpeg_exe()
CACHE = HERE / 'render_cache'
CACHE.mkdir(exist_ok=True)

# Each of these ten is an independently authored action pose of an established role.
NEW_POSES = (
    'v7_businessman_watch_lift', 'v7_businessman_watch_lower',
    'v7_investigator_walk_step', 'v7_investigator_handle_brace',
    'v7_investigator_balcony_crouch', 'v7_investigator_thread_inspect',
    'v7_wife_step_back', 'v7_wife_hand_to_mouth',
    'v7_partner_case_open', 'v7_partner_glance_away',
)
for name in NEW_POSES:
    v6.SPRITES[name] = v6.isolate(name)

# Different silhouettes at consecutive beats, rather than holding one sprite for seconds.
# A 0.10-s dissolving motion cut around each boundary softens the edited key poses.
POSES = {
    'businessman': [(2.20, 'businessman_master'), (2.48, NEW_POSES[0]),
                    (2.98, 'businessman_watch_pose'), (3.25, NEW_POSES[1])],
    'investigator': [(0, 'investigator_master'), (6.80, NEW_POSES[2]),
                     (7.62, 'investigator_door_pose'), (8.15, NEW_POSES[3]),
                     (9.50, 'investigator_master'), (11.85, 'investigator_reach_pose'),
                     (12.65, 'investigator_master'), (13.72, 'investigator_reach_pose'),
                     (14.17, NEW_POSES[4]), (15.20, 'investigator_master'),
                     (24.30, 'investigator_reach_pose'), (24.50, NEW_POSES[5]),
                     (25.38, 'investigator_master'), (31.30, 'investigator_reach_pose')],
    'wife': [(17.20, 'wife_master'), (17.58, NEW_POSES[6]),
             (18.40, 'wife_turn_pose'), (19.08, NEW_POSES[7])],
    'partner': [(20.22, 'partner_master'), (20.65, NEW_POSES[8]),
                (21.80, 'partner_case_pose'), (22.32, NEW_POSES[9])],
}

# The V6 warp function is reused unchanged, so these keys also breathe/shift at wrists,
# torso, head and knees. Bind its choice temporarily to render a named image.
base_person = v6.person

def named_person(t, role, height, name):
    v6.pose_role = lambda _t, _role: name
    return base_person(t, role, height)


def person(t, role, height):
    beats = POSES[role]
    index = max(i for i, (at, _name) in enumerate(beats) if at <= t)
    at, name = beats[index]
    current = named_person(t, role, height, name)
    if index and 0 <= t - at < .10:
        before = named_person(t, role, height, beats[index-1][1])
        # Both RGBA sprites are contained on equal-size transparent canvases to avoid
        # interpolation of differing crop sizes, while their feet retain their anchor.
        ww = max(before.width, current.width)
        hh = max(before.height, current.height)
        def align(im):
            canvas = Image.new('RGBA', (ww, hh))
            canvas.alpha_composite(im, ((ww-im.width)//2, hh-im.height))
            return canvas
        current = Image.blend(align(before), align(current), old.ease((t-at)/.10))
    return current


def scene_with_actor(t, key):
    plate, role, x, y, h = v6.PRESENT[key]
    bg = old.IMAGES[plate].convert('RGBA')
    # Stable shoe-ground contact; lateral travel and small stride bob belong only in
    # walking segments. The old suite-desk crouch is deliberately NOT reintroduced.
    if key == 'door_closed':
        walking = old.ease((t-6.45)/1.52)
        x = -220 + 574*walking
        if t < 7.97:
            y -= 7*abs(math.sin(2*math.pi*(t-6.45)*1.65))*walking
    elif key == 'investigator_balcony':
        x += 45*old.ease((t-13.55)/1.10) if t < 16 else 0
    elif role == 'wife':
        x -= 35*old.ease((t-17.58)/.83)
    elif role == 'partner':
        x += 24*old.ease((t-22.32)/.62)
    fg = person(t, role, h)
    # The V6 corridor's door-facing pose is mirrored; keep that orientation throughout
    # the reaching beat, while the walking keys remain the unmirrored identity.
    if key == 'door_closed' and t >= 7.62:
        fg = fg.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    px, py = round(x-fg.width/2), round(y-fg.height)
    shade = Image.new('RGBA', bg.size)
    sd = ImageDraw.Draw(shade)
    sd.ellipse((px+fg.width*.11, y-15, px+fg.width*.89, y+18), fill=(0, 0, 0, 120))
    bg = Image.alpha_composite(bg, shade.filter(ImageFilter.GaussianBlur(12)))
    bg.alpha_composite(fg, (px, py))
    return bg.convert('RGB')

# Fixed edge falloff keeps the hotel interior atmospheric without obscuring faces.
vignette = Image.new('RGBA', (W, H), (0, 0, 0, 0))
vg = ImageDraw.Draw(vignette)
for i in range(30):
    a = round(1.1*(30-i))
    vg.rounded_rectangle((i*2, i*2, W-i*2-1, H-i*2-1), radius=25,
                         outline=(2, 8, 13, a), width=2)


def frame(t):
    sh = next(s for s in old.SHOTS if s[0] <= t < s[1]) if t < DUR else old.SHOTS[-1]
    a, b, key, z0, z1, p0, p1, label = sh
    source = scene_with_actor(t, key) if key in v6.PRESENT else old.IMAGES[key]
    u = (t-a)/(b-a)
    e = old.ease(u) if a < 34 else 1-(1-u)**2.45
    z = z0+(z1-z0)*e
    cx = p0[0]+(p1[0]-p0[0])*e
    cy = p0[1]+(p1[1]-p0[1])*e
    # Micro-dolly/handheld drift rides on the established editorial camera track;
    # kept below 1% of source frame so no camera jerk or black border is exposed.
    if key in v6.PRESENT:
        z *= 1+.007*math.sin(t*2.7)
        cx += .004*math.sin(t*1.8)
        cy += .003*math.cos(t*2.4)
    if key == 'investigator_balcony' and 14.17 <= t < 15.2:
        # This generated crouch reads as unsupported when its legs are visible.
        # Use it ONLY as an intentional upper-body/hand insert, never full length.
        z = 2.10 + .12*old.ease((t-14.17)/1.03)
        cx, cy = .69, .48
    image = old.crop(source, z, (cx, cy))
    if key == 'investigator_balcony' and 14.17 <= t < 14.26:
        image = image.filter(ImageFilter.GaussianBlur(3*(1-old.ease((t-14.17)/.09))))
    if key in ('door_half', 'door_closed') and t-a < .09:
        image = image.filter(ImageFilter.GaussianBlur(6*(1-old.ease((t-a)/.09))))
    # Short focus-pull on the three character entrances, not a constantly blurry film.
    if a in (17.2, 20.22, 24.3) and t-a < .125:
        image = image.filter(ImageFilter.GaussianBlur(2.3*(1-old.ease((t-a)/.125))))
    if a >= 34.6 and t < 34.78:
        image = Image.blend(image, Image.new('RGB', (W, H), (166, 180, 176)),
                            .09*(1-old.ease((t-34.6)/.18)))
    image = Image.alpha_composite(image.convert('RGBA'), vignette).convert('RGB')
    if label:
        d = ImageDraw.Draw(image, 'RGBA')
        opacity = min(1, old.ease((t-a)/.18), old.ease((b-t)/.22))
        bb = d.textbbox((0, 0), label, font=v6.FONT)
        text_w = bb[2]-bb[0]
        x = (W-text_w)//2
        d.rounded_rectangle((x-21, 92, x+text_w+21, 154), radius=9,
                            fill=(3, 15, 20, int(200*opacity)))
        d.text((x, 102), label, font=v6.FONT, fill=(252, 239, 216, int(255*opacity)),
               stroke_width=1, stroke_fill=(4, 11, 14, int(255*opacity)))
    if t < 2.2:
        ImageDraw.Draw(image, 'RGBA').text((24, H-47), 'FICTIONAL DRAMATIZATION',
                                          font=v6.SMALL, fill=(240, 231, 214, 210))
    return image


if __name__ == '__main__':
    mix = old.audio_mix()
    mix_copy = CACHE / 'mix_v7.wav'
    shutil.copyfile(mix, mix_copy)
    v6.sync_new_sfx(mix_copy)
    raw = CACHE / 'silent_v7.mp4'
    cmd = [FF, '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
           '-s', f'{W}x{H}', '-r', str(FPS), '-i', 'pipe:0', '-c:v', 'libx264',
           '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p',
           '-movflags', '+faststart', str(raw)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    try:
        for k in range(round(DUR*FPS)):
            p.stdin.write(frame(k/FPS).tobytes())
            if k % (5*FPS) == 0:
                print('frame', k, flush=True)
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError('Video encoder failed')
    finally:
        if p.poll() is None:
            p.kill()
    final = HERE / 'FLORIDA_V7_TEN_MOTION_KEYS_PRIVATE_REVIEW_720x1280.mp4'
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', str(raw), '-i', str(mix_copy),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '192k', '-movflags', '+faststart', '-shortest', str(final)], check=True)
    print(final, final.stat().st_size, flush=True)

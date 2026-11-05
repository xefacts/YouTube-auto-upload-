#!/usr/bin/env python3
"""V8 corrective private review: planted actors, restrained edit, short story-cue type.

Cues are NOT claimed to be a verbatim transcript. Supplied 'Text' folder samples
inform hierarchy only; no reference footage, audio, logos or typography are copied.
"""
from pathlib import Path
import importlib.util
import math
import subprocess
import wave
import numpy as np
from scipy.signal import butter, sosfilt
from PIL import Image, ImageDraw, ImageFilter, ImageFont
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
FONTROOT = HERE.parents[2] / 'assets' / 'fonts'
BIG = ImageFont.truetype(str(FONTROOT / 'Anton-Regular.ttf'), 76)
MED = ImageFont.truetype(str(FONTROOT / 'Anton-Regular.ttf'), 61)
SMALL = ImageFont.truetype(str(FONTROOT / 'DMSans.ttf'), 20)
LABEL = ImageFont.truetype(str(FONTROOT / 'DMSans.ttf'), 19)
GOLD = (241, 190, 100)
WHITE = (250, 241, 220)
INK = (17, 22, 26)

# The voice edit's rough beat ranges, NOT a verified word-level transcript.
# Very brief editorial keywords; never imply an exact watch time, year or culprit.
CUES = (
    (0.15, 1.8, 'THE LOCKED', 'SUITE'),
    (2.40, 3.55, 'LOCKED', 'ROOM'),
    (6.55, 8.0, 'NO FORCED', 'ENTRY'),
    (9.85, 11.35, 'POCKET', 'WATCH'),
    (12.95, 14.12, 'FOOTPRINTS', ''),
    (15.45, 16.65, 'BALCONY', 'LATCH'),
    (17.45, 18.65, 'THE', 'WIFE'),
    (20.55, 21.75, 'BUSINESS', 'PARTNER'),
    (24.50, 25.55, 'THE', 'THREAD'),
)

# Full-length silhouettes with shoe soles in view; exclude V7's unsupported
# crouch and walking keys. No sinusoidal body warps, actor slides or jitter.
v6.SPRITES['v7_businessman_watch_lift'] = v6.isolate('v7_businessman_watch_lift')
v6.SPRITES['v7_investigator_thread_inspect'] = v6.isolate('v7_investigator_thread_inspect')

def actor(t, key):
    if key == 'alive':
        plate, name, x, y, h = 'suite', ('businessman_master' if t < 2.94 else 'v7_businessman_watch_lift'), 477, 1310, 625
    elif key == 'door_closed':
        if t < 7.15:
            return old.IMAGES['door_closed']
        plate, name, x, y, h = 'door_closed', 'investigator_master', 310, 1250, 700
    elif key == 'investigator_balcony':
        plate, name, x, y, h = 'balcony', ('investigator_master' if t < 24.30 else 'v7_investigator_thread_inspect'), 340, 1282, 605
    elif key in ('wife', 'wife_turn'):
        plate, name, x, y, h = 'hall_open', ('wife_master' if t < 18.63 else 'wife_turn_pose'), 395, 1170, 640
    elif key == 'partner':
        plate, name, x, y, h = 'hall_open', ('partner_master' if t < 21.85 else 'partner_case_pose'), 410, 1180, 660
    else:
        return old.IMAGES[key]
    bg = old.IMAGES[plate].convert('RGBA')
    fg = v6.SPRITES[name]
    fg = fg.resize((round(fg.width * h / fg.height), h), Image.Resampling.LANCZOS)
    px, py = round(x-fg.width/2), round(y-h)
    shadow = Image.new('RGBA', bg.size)
    ImageDraw.Draw(shadow).ellipse((px+fg.width*.20, y-12, px+fg.width*.80, y+12),
                                   fill=(0, 0, 0, 130))
    bg = Image.alpha_composite(bg, shadow.filter(ImageFilter.GaussianBlur(11)))
    bg.alpha_composite(fg, (px, py))
    return bg.convert('RGB')

# Reusable top gradient improves mobile readability without large black label boxes.
scrim = Image.new('RGBA', (W, 385), (0, 0, 0, 0))
scrim.putalpha(Image.fromarray(np.uint8(np.linspace(155, 0, 385))[:, None].repeat(W, 1), 'L'))

def kinetic_type(image, t):
    cue = next((row for row in CUES if row[0] <= t < row[1]), None)
    if cue is None:
        return image
    a, b, top, main = cue
    fade = min(1., old.ease((t-a)/.17), old.ease((b-t)/.18))
    if fade < .01:
        return image
    image = image.convert('RGBA')
    shade = scrim.copy()
    shade.putalpha(shade.getchannel('A').point(lambda x: round(x*fade)))
    image.alpha_composite(shade, (0, 0))
    type_layer = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(type_layer)
    top_font = MED if len(top) > 10 else BIG
    bb = d.textbbox((0, 0), top, font=top_font, stroke_width=0)
    text_w = bb[2]-bb[0]
    # Restrained 7-pixel settling motion only while the cue fades on.
    arrive = round(7*(1-old.ease((t-a)/.23)))
    x = (W-text_w)//2
    y = 154+arrive
    d.text((x+2, y+3), top, font=top_font, fill=(0, 0, 0, 140))
    d.text((x, y), top, font=top_font, fill=WHITE)
    if main:
        font = MED if len(main) > 8 else BIG
        bb = d.textbbox((0, 0), main, font=font)
        main_w = bb[2]-bb[0]
        left = (W-main_w)//2
        band_top = y+88
        d.rounded_rectangle((left-22, band_top+4, left+main_w+22, band_top+84),
                            radius=4, fill=GOLD)
        d.text((left, band_top+1), main, font=font, fill=INK)
    type_layer.putalpha(type_layer.getchannel('A').point(lambda x: round(x*fade)))
    image.alpha_composite(type_layer)
    return image.convert('RGB')

def frame(t):
    sh = next(s for s in old.SHOTS if s[0] <= t < s[1]) if t < DUR else old.SHOTS[-1]
    a, b, key, z0, z1, p0, p1, _old_title = sh
    source = actor(t, key) if key in v6.PRESENT else old.IMAGES[key]
    u = old.ease((t-a)/(b-a))
    if a >= 34.6:
        # Preserve the deliberate strong window-to-exterior closing pullback.
        u = 1-(1-(t-a)/(b-a))**2.45
        factor = 1.
    else:
        # Cut V7's always-moving zooms and handheld motion by over 60%.
        factor = .34 if key in v6.PRESENT else .50
    z = z0+(z1-z0)*u*factor
    focus = (p0[0]+(p1[0]-p0[0])*u*factor,
             p0[1]+(p1[1]-p0[1])*u*factor)
    image = old.crop(source, z, focus)
    if key in ('door_half', 'door_closed') and t-a < .065:
        image = image.filter(ImageFilter.GaussianBlur(3*(1-old.ease((t-a)/.065))))
    image = kinetic_type(image, t)
    if t < 2.2:
        ImageDraw.Draw(image, 'RGBA').text((24, H-43), 'FICTIONAL DRAMATIZATION',
                                          font=LABEL, fill=(242, 237, 224, 225))
    return image

def soundtrack():
    """Fresh original dark air/percussion/foley mix, voice remains front and center."""
    sr = 48000
    n = round(sr*DUR)
    rng = np.random.default_rng(86710)
    v = old.read_audio(v6.EP/'audio/voice_edit_1934.mp3', sr)
    percussion = old.read_audio(v6.EP/'audio/percussion_air_draft.mp3', sr)
    a = np.zeros(n, np.float32)
    a[:min(len(v),n)] += .86*v[:n]
    # No musical instruments or outside sound samples; the original restrained
    # percussion bed sits well below narration instead of pumping each 0.75 s.
    a[:min(len(percussion),n)] += .18*percussion[:n]
    noise = rng.normal(0, 1, n).astype(np.float32)
    wind = sosfilt(butter(2, 180, fs=sr, output='sos'), noise).astype(np.float32)
    rain = noise - sosfilt(butter(2, 850, fs=sr, output='sos'), noise).astype(np.float32)
    a += .024*wind + .0038*rain

    def add(at, sig):
        start = round(at*sr)
        if start < 0 or start >= n:
            return
        end = min(len(sig), n-start)
        a[start:start+end] += np.asarray(sig[:end], dtype=np.float32)

    def wood_slam(at, level):
        dur = .78
        z = np.arange(round(dur*sr), dtype=np.float32)/sr
        grit = rng.normal(0, 1, len(z)).astype(np.float32)
        grit = sosfilt(butter(3, 550, fs=sr, output='sos'), grit).astype(np.float32)
        body = np.sin(2*np.pi*(91*z-17*z*z))*.11
        hit = (grit*.60+body)*np.exp(-z*10)*level
        hit += .035*rng.normal(0, 1, len(z)).astype(np.float32)*np.exp(-z*28)*level
        add(at, hit)

    # Friction of a heavy wooden door before the photographed closing state.
    z = np.arange(round(.78*sr), dtype=np.float32)/sr
    rubbing = sosfilt(butter(2, [140, 1700], btype='bandpass', fs=sr, output='sos'),
                     rng.normal(0, 1, len(z))).astype(np.float32)
    creak = .032*np.sin(2*np.pi*(190*z-55*z*z))*np.sin(np.pi*z/.78)**2
    add(5.49, creak + .05*rubbing*np.sin(np.pi*z/.78)**2)
    wood_slam(6.24, 1.00)
    # Gentle metal touches; the balcony lock click is exactly on the 15.96 cut.
    for at, level in ((15.96, .075), (16.12, .024)):
        z = np.arange(round(.16*sr), dtype=np.float32)/sr
        click = (np.sin(2*np.pi*1670*z)+.30*rng.normal(0, 1, len(z))) * np.exp(-z*44)*level
        add(at, click)
    for at, level in ((3.65, .045), (9.50, .045), (24.30, .052), (34.62, .48)):
        wood_slam(at, level)
    # When narration ends, let the dark filtered wind rise into the visual-only
    # pullback rather than dropping into an almost silent final five seconds.
    vo_end = round(33.5*sr)
    rise = np.clip(np.arange(n-vo_end, dtype=np.float32)/(1.8*sr), 0, 1)
    a[vo_end:] += .23*wind[vo_end:]*rise
    # Low non-melodic swells only at scene changes, ending opens into darker air.
    for at, duration, level in ((5.9, 1.0, .09), (15.25, .9, .06), (24.1, 1., .07), (33.7, 1.3, .16)):
        z = np.arange(round(duration*sr), dtype=np.float32)
        swell = rng.normal(0, 1, len(z)).astype(np.float32)
        swell = sosfilt(butter(2, 220, fs=sr, output='sos'), swell).astype(np.float32)
        add(at, swell*(np.sin(np.pi*z/len(z))**2)*level)
    a = np.tanh(a*1.07)
    peak = np.max(np.abs(a))
    if peak > .95:
        a *= .95/peak
    a[-round(.3*sr):] *= np.linspace(1, 0, round(.3*sr), dtype=np.float32)
    out = CACHE/'v8_soundtrack.wav'
    with wave.open(str(out), 'wb') as w:
        w.setframerate(sr)
        w.setsampwidth(2)
        w.setnchannels(1)
        w.writeframes((a*32767).astype('<i2').tobytes())
    return out

if __name__ == '__main__':
    wav = soundtrack()
    raw = CACHE/'silent_v8.mp4'
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
    final = HERE/'FLORIDA_V8_RESTRAINED_TYPE_AND_SOUND_PRIVATE_REVIEW_720x1280.mp4'
    subprocess.run([FF, '-y', '-loglevel', 'error', '-i', str(raw), '-i', str(wav),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac',
                    '-b:a', '192k', '-movflags', '+faststart', '-shortest', str(final)], check=True)
    print(final, final.stat().st_size, flush=True)

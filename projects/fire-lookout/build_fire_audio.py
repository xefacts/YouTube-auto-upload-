#!/usr/bin/env python3
# ============================================================================
# BUILD_FIRE_AUDIO.PY — "The Fire Lookout" full audio master
# 146.5s @ 48kHz stereo:
#   - VO master (+9 dB, dominant)
#   - absolutesound suspense bed (0.40) + windy-cave base + tail fill
#   - hitslab tension accents in two windows
#   - Drone Ocean Cave swell for the final act
#   - SFX hits at story beats (knocks, radio, buzz, riser, whooshes, subs)
# Output: /tmp/fire_lookout/master_audio.wav  (+ data/captions.ass)
# ============================================================================
import json
import os
import subprocess

import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "sfx")
AUDIO = os.path.join(HERE, "audio")
OUT_DIR = "/tmp/fire_lookout"
CAPTIONS_OUT = os.path.join(HERE, "data", "captions.ass")
FFMPEG = "/tmp/studio_env/bin/ffmpeg"

SR = 48000
DUR = 146.5
N = int(DUR * SR)

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)

mix = np.zeros((N, 2), dtype=np.float64)


def load(path, mono=True):
    """decode any audio to float64 48k stereo numpy via ffmpeg"""
    out = os.path.join(OUT_DIR, "_tmp.wav")
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                    "-i", path, "-ar", str(SR), "-ac", "2", "-f", "wav", out],
                   check=True)
    d, _ = sf.read(out, dtype="float64")
    if d.ndim == 1:
        d = np.stack([d, d], axis=1)
    return d


def place(buf, t, gain=1.0, fade_in=0.02, fade_out=0.06):
    i0 = int(t * SR)
    if i0 >= N or i0 < 0:
        return
    seg = buf[: N - i0]
    if len(seg) == 0:
        return
    g = np.ones(len(seg))
    fi = min(len(seg), int(fade_in * SR))
    fo = min(len(seg), int(fade_out * SR))
    if fi > 0:
        g[:fi] = np.linspace(0, 1, fi)
    if fo > 0:
        g[-fo:] *= np.linspace(1, 0, fo)
    mix[i0:i0 + len(seg)] += seg * (gain * g)[:, None]


def sweep(buf, t, dur, gain=1.0, attack=None, release=None):
    """place with long attack/release envelope"""
    i0 = int(t * SR)
    n = min(int(dur * SR), N - i0, len(buf))
    if n <= 0:
        return
    seg = buf[:n]
    g = np.ones(n)
    a = int((attack or 0.02) * SR)
    r = int((release or 0.06) * SR)
    if a > 0:
        g[:min(a, n)] = np.linspace(0, 1, min(a, n))
    if r > 0:
        g[-min(r, n):] *= np.linspace(1, 0, min(r, n))
    mix[i0:i0 + n] += seg * (gain * g)[:, None]


print("[audio] loading sources...")
vo = load(os.path.join(AUDIO, "vo_master.mp3"))
bed = load(os.path.join(SFX, "absolutesound-suspense-tense-atmosphere-514617.mp3"))
hits = load(os.path.join(SFX, "hitslab-tension-suspense-mystery-629029.mp3"))
wind = load(os.path.join(SFX, "Noise - Windy Cave.wav"))
drone_ocean = load(os.path.join(SFX, "Drone - Ocean Cave.wav"))
drone_crystal = load(os.path.join(SFX, "Drone - Crystal Cave.wav"))
imp_deep = load(os.path.join(SFX, "Impact - Deep Down.wav"))
imp_jaw = load(os.path.join(SFX, "Impact - Jaw Breaker.wav"))
whoosh = load(os.path.join(SFX, "Whoosh - Triple Threat.wav"))
riser = load(os.path.join(SFX, "Riser - Stormy Swarmy.wav"))
malfunc = load(os.path.join(SFX, "Short - Digital Malfunction.wav"))
sub_mini = load(os.path.join(SFX, "Sub - Mini Impact.wav"))
metal = load(os.path.join(SFX, "Metal - Spooky Midnight.wav"))

print("[audio] placing layers...")

# ---- VO: +9 dB, dominant ----
place(vo, 0.0, gain=10 ** (9 / 20))

# ---- main suspense bed ----
sweep(bed, 0.35, 137.2, gain=0.40, attack=2.0, release=2.5)

# ---- base wind under everything + tail fill after bed ends ----
sweep(wind, 0.0, DUR, gain=0.10, attack=3.0, release=3.0)
sweep(wind, 132.0, DUR - 132.0, gain=0.22, attack=6.0, release=3.0)

# ---- hitslab tension accents (notebook + staircase windows) ----
sweep(hits, 52.0, 13.0, gain=0.26, attack=1.5, release=2.0)
sweep(hits, 99.0, 12.0, gain=0.28, attack=1.0, release=1.5)

# ---- drone swell for the final act ----
sweep(drone_ocean, 76.0, DUR - 76.0, gain=0.13, attack=14.0, release=4.0)

# ---- CCTV intro drone ----
sweep(drone_crystal, 0.0, 8.0, gain=0.15, attack=1.0, release=1.5)

# ---- SFX beats ----
SFX_BEATS = [
    # (clip, t, gain)
    (malfunc, 0.05, 0.35),          # CCTV glitch open
    (malfunc, 6.55, 0.30),          # CCTV cut out
    (imp_deep, 11.3, 0.75),         # truck stops
    (whoosh, 12.4, 0.34),           # tower reveal
    (sub_mini, 20.0, 0.45),         # name tag macro
    (sub_mini, 29.2, 0.45),         # keys handoff
    (malfunc, 40.75, 0.42),         # radio crackle 11:47
    (sub_mini, 44.0, 0.50),         # clock macro
    (metal, 61.6, 0.30),            # warning page
    (riser, 65.5, 0.22),            # voice returns (RED)
    (imp_jaw, 76.5, 0.50),          # knock 1
    (imp_jaw, 77.25, 0.50),         # knock 2
    (imp_jaw, 78.0, 0.55),          # knock 3
    (whoosh, 79.15, 0.40),          # flashlight beam on
    (riser, 80.4, 0.34),            # figure reveal build
    (sub_mini, 82.3, 0.60),         # FIGURE
    (whoosh, 88.15, 0.30),          # office flashback
    (malfunc, 94.55, 0.40),         # NO SERVICE
    (sub_mini, 100.9, 0.35),        # hatch glance
    (sub_mini, 103.9, 0.50),        # footstep 1
    (sub_mini, 104.6, 0.50),        # footstep 2
    (sub_mini, 105.3, 0.55),        # footstep 3
    (malfunc, 110.05, 0.42),        # phone buzz
    (sub_mini, 113.45, 0.55),       # message arrives
    (whoosh, 117.4, 0.32),          # photo open
    (imp_deep, 126.45, 0.55),       # timestamp thud
    (riser, 128.3, 0.28),           # realization build
    (imp_jaw, 132.5, 0.52),         # door knock 1
    (imp_jaw, 133.25, 0.52),        # door knock 2
    (imp_jaw, 134.0, 0.58),         # door knock 3
    (malfunc, 136.85, 0.45),        # radio turns itself on
    (metal, 142.0, 0.26),           # final dread sting
]
for clip, t, g in SFX_BEATS:
    place(clip, t, gain=g)

# ---- master fades ----
fade_out_start = int(144.8 * SR)
mix[fade_out_start:] *= np.linspace(1, 0, N - fade_out_start)[:, None]
mix[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))[:, None]

# ---- safety clip ----
peak = np.abs(mix).max()
if peak > 0.98:
    mix *= 0.98 / peak

out_wav = os.path.join(OUT_DIR, "master_audio.wav")
sf.write(out_wav, mix.astype(np.float32), SR, subtype="PCM_16")
print(f"[audio] wrote {out_wav} ({DUR}s)")

# loudness check + final normalize pass to -14 LUFS
r = subprocess.run([FFMPEG, "-hide_banner", "-i", out_wav,
                    "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=summary",
                    "-f", "null", "-"], capture_output=True, text=True)
for ln in r.stderr.splitlines():
    if "Input Integrated" in ln or "Input True Peak" in ln:
        print("[audio]", ln.strip())

final_wav = os.path.join(OUT_DIR, "master_audio_norm.wav")
subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                "-i", out_wav,
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=9",
                "-ar", str(SR), "-ac", "2", final_wav], check=True)
print(f"[audio] normalized master -> {final_wav}")

# ---------------------------------------------------------------- captions
print("[captions] building ASS...")
words = json.load(open(os.path.join(AUDIO, "captions_words.json")))

DANGER = {"KNOCK", "KNOCKS", "KNOCKING", "VOICE", "HIM", "UPSTAIRS", "DEAD", "GONE",
          "ALONE", "OUTSIDE", "SIGNAL", "FEET", "FOOTSTEPS", "BUZZED", "BUZZING",
          "DOOR", "NIGHT", "DARK", "TERRIFIED", "FEAR", "DREAD", "SILENT", "SILENCE",
          "FREEZE", "FROZE", "FROZEN", "RUN", "HIDE", "SCREAM", "BLOOD", "EYES",
          "STARING", "SMILING", "WATCHING", "NEVER", "NOBODY", "NOTHING"}
REVEAL = {"MANAGER", "ROBERT", "SAME", "JACKET", "NAME", "TAG", "PHOTO", "MESSAGE",
          "TIMESTAMP", "MINUTES", "AGO", "DOUBLE", "IDENTICAL", "COPY", "REALIZE",
          "REALIZED", "UNDERSTOOD", "TRUTH"}


def ass_time(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


events = []
for w in words:
    s = max(0.0, w["s"] - 0.015)
    e = w["e"] + 0.045
    if e - s < 0.30:
        e = s + 0.30
    txt = w["w"].upper()
    if txt in DANGER:
        color = r"\1c&H2A2AFF&"  # red (BGR)
    elif txt in REVEAL:
        color = r"\1c&H3CFF5E&"  # green
    else:
        color = ""
    tag = r"{\fscx126\fscy126\t(0,60,\fscx100\fscy100)" + color + "}"
    events.append((s, e, tag, txt))

# drop overlapping tails
clean = []
for i, (s, e, tag, txt) in enumerate(events):
    if i + 1 < len(events):
        e = min(e, events[i + 1][0] + 0.02)
    if e > s + 0.05:
        clean.append((s, e, tag, txt))

ass = f"""[Script Info]
Title: The Fire Lookout
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: OneWord,Anton,92,&H00FFFFFF,&H000000FF,&H0014141A,&H96000000,0,0,0,0,100,100,1.2,0,1,10,2.2,2,80,80,600,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for s, e, tag, txt in clean:
    ass += f"Dialogue: 0,{ass_time(s)},{ass_time(e)},OneWord,,0,0,0,,{tag}{txt}\n"

open(CAPTIONS_OUT, "w").write(ass)
print(f"[captions] {len(clean)} word events -> {CAPTIONS_OUT}")

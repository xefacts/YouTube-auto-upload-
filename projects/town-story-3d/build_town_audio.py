#!/usr/bin/env python3
# ============================================================================
# BUILD_TOWN_AUDIO.PY — "The Town That Counts To Ten" full audio master
# 80.0s @ 48kHz stereo:
#   - Narration: TTS sections pitched UP (very shrill) + tempo-fit, loud
#   - The Voice (counts): same TTS pitched DOWN -10 semitones + reverb + sub
#   - Procedural SFX: ticks, whooshes, door slams, riser, flash, birds, wind,
#     heartbeat, cane clatter, thud
#   - Procedural BGM: day plucks -> night drone -> morning resolve -> end sting
#   - Captions: word-timed from measured clip durations -> data/captions.ass
# Output: /tmp/town_story/master_audio.wav  (and data/captions.ass)
# ============================================================================
import json
import os
import subprocess
import sys

import numpy as np
import scipy.signal as signal
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
TTS_DIR = os.path.join(HERE, "tts")
OUT_DIR = "/tmp/town_story"
CAPTIONS_OUT = os.path.join(HERE, "data", "captions.ass")
FFMPEG = "/tmp/studio_env/bin/ffmpeg"

SR = 48000
DUR = 80.0
N = int(DUR * SR)

os.makedirs(OUT_DIR, exist_ok=True)
os.makedirs(os.path.join(HERE, "data"), exist_ok=True)

rng = np.random.default_rng(20260911)

# ------------------------------------------------------------------ sections
# (id, start, window_end, text)
SECTIONS = [
    ("n01", 0.40,  7.90,  "In this town, every night at nine PM, one house disappears. A voice counts down from ten. And whatever it counts... is gone."),
    ("n02", 8.00,  13.40, "Tommy just moved in. His neighbor had one warning: be inside before nine."),
    ("n03", 13.60, 16.00, "Tommy laughed. Houses don't just disappear."),
    ("n04", 16.20, 21.40, "Then dusk came. And the whole town started running."),
    ("n05", 21.60, 27.20, "Doors slammed. Lights flickered. And the voice began to count."),
    ("n06", 35.20, 38.60, "Old Mr. Finch was still outside."),
    ("n07", 42.50, 45.80, "The lamps turned... toward Finch's house."),
    ("n08", 53.80, 57.60, "And Finch's house... was gone. Only his hat remained."),
    ("n09", 58.20, 63.60, "Next morning, Tommy found it. House 147... vanished."),
    ("n10", 64.20, 69.40, "143. 145. Gone. And Tommy's own door... read 149."),
    ("n11", 73.80, 78.40, "Every night, it takes one house. And tonight... it counts again."),
]
# counts: (id, start) — deep entity voice
COUNTS = [
    ("c1", 27.60, "Ten... Nine... Eight.",     1.30),
    ("c2", 39.00, "Seven... Six... Five.",     1.30),
    ("c3", 46.30, "Four... Three.",            1.22),
    ("c4", 51.55, "Two.",                      1.12),
    ("c5", 52.28, "One.",                      1.08),
]
COUNT_WORDS = {"ten", "nine", "eight", "seven", "six", "five", "four", "three", "two", "one"}

# hardcoded visual captions (plate numbers during tracking shot) — start, end, text, color
EXTRA_CAPTIONS = [
    (65.00, 65.90, "143", "RED"),
    (66.50, 67.40, "145", "RED"),
    (67.90, 68.90, "GONE", "RED"),
]

# caption accent colors (word -> ASS &HBBGGRR&)
RED = "&H3838FF&"    # #FF3838
BLUE = "&HFFD43C&"   # #3CD4FF (web blue)
ACCENT_WORDS = {
    "gone", "running", "running.", "147.", "143...", "145...", "147...", "149.",
    "ten.", "ten", "nine", "eight", "seven", "six", "five", "four", "three",
    "one.", "two.", "voice", "voice.", "smiled", "dark", "counts",
}

# ------------------------------------------------------------------ helpers
def ffmpeg_load_mono(path):
    """decode any audio to mono float32 48k via ffmpeg pipe"""
    p = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"ffmpeg decode failed: {path}\n{p.stderr.decode()[:400]}")
    a = np.frombuffer(p.stdout, dtype=np.float32)
    return a.copy()

def ffmpeg_shrill(path, pitch=1.32, atempo=1.0):
    """pitch UP (classic speed-up chipmunk shrill), then tempo-fit"""
    af = f"asetrate={int(SR*pitch)},aresample={SR}"
    if abs(atempo - 1.0) > 0.01:
        af += f",atempo={atempo:.4f}"
    p = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-af", af, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"shrill failed: {path}\n{p.stderr.decode()[:400]}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()

def ffmpeg_deep(path, pitch=0.56, atempo=1.12):
    """pitch DOWN ~ -10 semitones, slightly tighter"""
    af = f"asetrate={int(SR*pitch)},aresample={SR},atempo={atempo:.4f}"
    p = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-af", af, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True,
    )
    if p.returncode != 0:
        raise RuntimeError(f"deep failed: {path}\n{p.stderr.decode()[:400]}")
    return np.frombuffer(p.stdout, dtype=np.float32).copy()

def env_ad(n, a, d):
    """attack/decay envelope, both in samples"""
    e = np.ones(n, dtype=np.float32)
    na, nd = int(a), int(d)
    if na > 0: e[:na] = np.linspace(0, 1, na)
    if nd > 0: e[-nd:] *= np.linspace(1, 0, nd)
    return e

def place(buf, clip, t0, gain=1.0, pan=0.0):
    """mix mono clip into stereo buffer at t0 seconds"""
    i0 = int(t0 * SR)
    if i0 >= N: return
    seg = clip[: max(0, N - i0)]
    gl = gain * (1.0 - max(0.0, pan))
    gr = gain * (1.0 + min(0.0, pan))
    buf[i0:i0 + len(seg), 0] += seg * gl
    buf[i0:i0 + len(seg), 1] += seg * gr

def rms_db(a):
    a = np.asarray(a, dtype=np.float64)
    return 20 * np.log10(max(np.sqrt((a ** 2).mean()), 1e-12))

# ------------------------------------------------------------------ SFX synth
def sfx_tick(f0=2100.0, dur=0.035, g=0.06):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    x = np.sin(2 * np.pi * f0 * t) * np.exp(-t * 130)
    x += 0.6 * np.sin(2 * np.pi * f0 * 1.62 * t) * np.exp(-t * 170)
    return (x * g).astype(np.float32)

def sfx_whoosh(dur=0.34, g=0.10, up=True):
    n = int(dur * SR)
    noise = rng.standard_normal(n).astype(np.float32)
    f_lo, f_hi = (350.0, 2600.0) if up else (2600.0, 350.0)
    lo, hi = min(f_lo, f_hi), max(f_lo, f_hi)
    sos = signal.butter(2, [lo / (SR * 0.5), hi / (SR * 0.5)], btype="bandpass", output="sos")
    x = signal.sosfilt(sos, noise)
    return (x * env_ad(n, int(0.10 * n), int(0.35 * n)) * g).astype(np.float32)

def sfx_door_slam(g=0.5):
    n = int(0.42 * SR)
    t = np.linspace(0, 0.42, n, dtype=np.float32)
    thump = (np.sin(2 * np.pi * 58 * t) * np.exp(-t * 22)).astype(np.float32)
    body = signal.sosfilt(signal.butter(2, 260.0 / (SR * 0.5), btype="low", output="sos"),
                          rng.standard_normal(n).astype(np.float32)) * np.exp(-t * 26)
    click = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 300) * 0.4
    x = thump * 0.9 + body * 0.8 + click
    return (x * g * env_ad(n, 60, int(0.2 * n))).astype(np.float32)

def sfx_riser(dur=2.9, g=0.16):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 90 * (2 ** (t / dur * 3.1))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 1.7
    noise = rng.standard_normal(n).astype(np.float32)
    sos = signal.butter(2, [600 / (SR * 0.5), 5200 / (SR * 0.5)], btype="bandpass", output="sos")
    x += signal.sosfilt(sos, noise) * (t / dur) ** 2.4 * 1.4
    return (x * g).astype(np.float32)

def sfx_flash(g=0.7):
    n = int(2.2 * SR)
    t = np.linspace(0, 2.2, n, dtype=np.float32)
    burst = rng.standard_normal(n).astype(np.float32) * np.exp(-t * 34)
    sos = signal.butter(2, 900.0 / (SR * 0.5), btype="low", output="sos")
    burst = signal.sosfilt(sos, burst) * 1.7
    f = 55 * np.exp(-t * 1.1) + 26
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.9) * 1.0
    return ((burst + sub) * g).astype(np.float32)

def sfx_bird(t0f, dur=0.16, g=0.020, pan=0.0):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    wob = t0f * (1 + 0.10 * np.sin(2 * np.pi * 26 * t))
    return (np.sin(2 * np.pi * np.cumsum(wob) / SR) * np.maximum(np.sin(np.pi * t / dur), 0) ** 1.4 * g).astype(np.float32)

def sfx_heartbeat(bpm=64, dur=3.4, g=0.30):
    n = int(dur * SR)
    x = np.zeros(n, dtype=np.float32)
    period = 60.0 / bpm
    k = 0
    while k * period < dur:
        for off, gg in [(0.0, 1.0), (0.20, 0.62)]:
            tt = k * period + off
            if tt >= dur: break
            i0 = int(tt * SR); nn = int(0.16 * SR)
            if i0 + nn > n: nn = n - i0
            if nn <= 0: break
            td = np.linspace(0, nn / SR, nn, dtype=np.float32)
            x[i0:i0 + nn] += np.sin(2 * np.pi * 52 * td) * np.exp(-td * 30) * gg
        k += 1
    return (x * g).astype(np.float32)

def sfx_cane(g=0.34):
    out = []
    for dt, gg in [(0.0, 1.0), (0.13, 0.55), (0.30, 0.30)]:
        n = int(0.09 * SR)
        t = np.linspace(0, 0.09, n, dtype=np.float32)
        x = (np.sin(2 * np.pi * 880 * t) + 0.5 * np.sin(2 * np.pi * 1410 * t)) * np.exp(-t * 90) * gg
        out.append((x, dt))
    total = np.zeros(int(0.5 * SR), dtype=np.float32)
    for x, dt in out:
        i0 = int(dt * SR)
        total[i0:i0 + len(x)] += x
    return (total * g).astype(np.float32)

def sfx_thud(g=0.30):
    n = int(0.4 * SR)
    t = np.linspace(0, 0.4, n, dtype=np.float32)
    f = 90 * np.exp(-t * 8) + 40
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * g).astype(np.float32)

def sfx_footstep(g=0.05):
    n = int(0.07 * SR)
    t = np.linspace(0, 0.07, n, dtype=np.float32)
    x = np.sin(2 * np.pi * 95 * t) * np.exp(-t * 70)
    x += 0.4 * np.sin(2 * np.pi * 210 * t) * np.exp(-t * 110)
    return (x * g).astype(np.float32)

def sfx_cane_tap(g=0.10):
    n = int(0.05 * SR)
    t = np.linspace(0, 0.05, n, dtype=np.float32)
    x = (np.sin(2 * np.pi * 1250 * t) + 0.6 * np.sin(2 * np.pi * 2100 * t)) * np.exp(-t * 220)
    return (x * g).astype(np.float32)

def sfx_lamp_buzz(dur, g=0.006):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    x = np.sin(2 * np.pi * 100 * t) + 0.45 * np.sin(2 * np.pi * 200 * t)
    am = 1 + 0.35 * np.sin(2 * np.pi * 5.2 * t)
    fade = np.minimum(1, np.minimum(t / 0.4, (dur - t) / 0.4))
    return (x * am * fade * g).astype(np.float32)

def sfx_whine(dur, g=0.006):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    f = 1975 + 22 * np.sin(2 * np.pi * 0.31 * t)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR)
    fade = np.minimum(1, np.minimum(t / 2.5, (dur - t) / 3.0))
    return (x * fade * g).astype(np.float32)

def sfx_dissonant_swell(dur, g=0.045):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    x = np.sin(2 * np.pi * 220 * t) + np.sin(2 * np.pi * 233.1 * t) + 0.4 * np.sin(2 * np.pi * 466 * t)
    ramp = (t / dur) ** 1.6
    trem = 1 + 0.25 * np.sin(2 * np.pi * 5.5 * t)
    return (x * ramp * trem * g).astype(np.float32)

# ------------------------------------------------------------------ BGM synth
def bgm_day_plucks(dur, g=0.030):
    """light major pluck pattern + soft bass (normal-life feel)"""
    n = int(dur * SR)
    x = np.zeros(n, dtype=np.float32)
    # C major-ish gentle pattern, eighth-note grid at 96bpm
    notes = [261.6, 329.6, 392.0, 329.6, 261.6, 392.0, 523.3, 392.0]
    bass = [130.8, 98.0]
    step = 60 / 96 / 2
    k = 0
    while k * step < dur:
        f = notes[k % len(notes)]
        tt = k * step
        i0 = int(tt * SR); nn = int(0.5 * SR)
        if i0 + nn > n: nn = n - i0
        if nn <= 0: break
        td = np.linspace(0, nn / SR, nn, dtype=np.float32)
        tone = (np.sin(2 * np.pi * f * td) + 0.35 * np.sin(2 * np.pi * f * 2 * td)) * np.exp(-td * 6.5)
        x[i0:i0 + nn] += tone * (0.8 if k % 4 == 0 else 0.55)
        if k % 4 == 0:  # bass on the downbeats
            bf = bass[(k // 4) % 2]
            bnn = min(nn, int(0.9 * SR))
            btd = np.linspace(0, bnn / SR, bnn, dtype=np.float32)
            btone = np.sin(2 * np.pi * bf * btd) * np.exp(-btd * 3.2)
            x[i0:i0 + bnn] += btone * 0.5
        k += 1
    return (x * g).astype(np.float32)

def bgm_night_drone(dur, g=0.052):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    x = (0.5 * np.sin(2 * np.pi * 36.7 * t) + 0.30 * np.sin(2 * np.pi * 55.0 * t + 0.8)
         + 0.18 * np.sin(2 * np.pi * 73.4 * t + 1.7))
    wob = 0.72 + 0.28 * np.sin(2 * np.pi * 0.24 * t)
    x *= wob
    # slow filter-swept noise layer
    noise = rng.standard_normal(n).astype(np.float32)
    sos = signal.butter(2, [80 / (SR * 0.5), 420 / (SR * 0.5)], btype="bandpass", output="sos")
    x += signal.sosfilt(sos, noise) * 0.020
    # eerie high whine (horror pad)
    fw = 1975 + 22 * np.sin(2 * np.pi * 0.31 * t)
    x += np.sin(2 * np.pi * np.cumsum(fw) / SR) * 0.11
    return (x * g).astype(np.float32)

def bgm_end_sting(dur=6.0, g=0.09):
    n = int(dur * SR)
    t = np.linspace(0, dur, n, dtype=np.float32)
    x = (0.6 * np.sin(2 * np.pi * 49.0 * t) + 0.4 * np.sin(2 * np.pi * 58.3 * t + 0.5)
         + 0.25 * np.sin(2 * np.pi * 98.0 * t + 1.1))
    envl = np.minimum(1, t / 0.8) * np.exp(-t * 0.55)
    # deep sub drop at the hit
    fs = 46 * np.exp(-t * 1.2) + 30
    x += np.sin(2 * np.pi * np.cumsum(fs) / SR) * np.exp(-t * 1.6) * 0.8
    # downward noise sweep (cymbal-ish release)
    noise = rng.standard_normal(n).astype(np.float32)
    sos = signal.butter(2, [400 / (SR * 0.5), 5500 / (SR * 0.5)], btype="bandpass", output="sos")
    sweep = signal.sosfilt(sos, noise) * np.exp(-t * 2.4) * 0.5
    return ((x * envl + sweep * envl) * g).astype(np.float32)

# ------------------------------------------------------------------ main build
def main():
    missing = [s[0] for s in SECTIONS if not os.path.exists(os.path.join(TTS_DIR, s[0] + ".mp3"))]
    missing += [c[0] for c in COUNTS if not os.path.exists(os.path.join(TTS_DIR, c[0] + ".mp3"))]
    if missing:
        print("MISSING TTS CLIPS:", missing)
        sys.exit(1)

    vo = np.zeros((N, 2), dtype=np.float32)   # narration + counts
    bed = np.zeros((N, 2), dtype=np.float32)  # sfx + bgm
    word_timings = []  # (start, end, word) for captions

    # ---- narration: shrill + tempo-fit ----
    print("[1/5] Narration (shrill + fast)...")
    for sid, t0, t1, text in SECTIONS:
        path = os.path.join(TTS_DIR, sid + ".mp3")
        raw = ffmpeg_load_mono(path)
        shrunk = ffmpeg_shrill(path, pitch=1.24, atempo=1.0)
        window = (t1 - t0) * 0.94
        if len(shrunk) > window * SR:
            atempo = (len(shrunk) / SR) / window
            atempo = min(1.5, atempo)
            shrunk = ffmpeg_shrill(path, pitch=1.24, atempo=atempo)
        # normalize clip level
        peak = np.abs(shrunk).max()
        if peak > 1e-6:
            shrunk = shrunk * (0.72 / peak)
        place(vo, shrunk, t0, gain=1.10)
        # word timings for captions (proportional within the placed clip)
        words = [w for w in text.split(" ") if w]
        weights = np.array([len(w) + 1.6 + (1.9 if any(c in w for c in ".…") else 0) for w in words], dtype=np.float64)
        weights /= weights.sum()
        clip_dur = len(shrunk) / SR
        wt = t0
        for w, wu in zip(words, weights):
            wd = clip_dur * wu
            word_timings.append((wt, wt + wd, w))
            wt += wd
        print(f"   {sid}: raw {len(raw)/SR:.2f}s -> shrill {clip_dur:.2f}s @ {t0:.2f}s")

    # ---- the Voice: deep counts + reverb-ish layering ----
    print("[2/5] The Voice (deep counts)...")
    try:
        from pedalboard import Reverb, Compressor
        pb_ok = True
    except Exception:
        pb_ok = False
        print("   (pedalboard unavailable — dry deep voice)")
    for cid, t0, ctext, catempo in COUNTS:
        path = os.path.join(TTS_DIR, cid + ".mp3")
        deep = ffmpeg_deep(path, pitch=0.56, atempo=catempo)
        peak = np.abs(deep).max()
        if peak > 1e-6:
            deep = deep * (0.85 / peak)
        if pb_ok:
            d2 = deep.reshape(-1, 1).repeat(2, axis=1)
            d2 = Reverb(room_size=0.55, damping=0.4, wet_level=0.42, dry_level=0.75)(d2, SR)
            deep = d2.mean(axis=1).astype(np.float32)
        place(vo, deep, t0, gain=1.15)
        # impact boom under each count word start
        place(bed, sfx_thud(0.30), t0, gain=0.78)
        # caption timings for the count words (proportional)
        cwords = [w for w in ctext.replace("...", ". ").split(" ") if w]
        cweights = np.array([len(w) + 2.4 for w in cwords], dtype=np.float64)
        cweights /= cweights.sum()
        cdur = len(deep) / SR
        wt = t0
        for w, wu in zip(cwords, cweights):
            wd = cdur * wu
            word_timings.append((wt, wt + wd, w))
            wt += wd

    # ---- SFX ----
    print("[3/5] SFX...")
    # soft cut whooshes at every hard shot boundary (subtle, fast-paced glue)
    cut_times = [4.0, 8.0, 12.0, 15.5, 19.5, 23.0, 26.0, 31.0, 36.5, 41.0,
                 46.0, 50.0, 52.6, 53.7, 58.0, 64.0, 69.5, 73.5, 76.6]
    for ct in cut_times:
        place(bed, sfx_whoosh(0.26, g=0.045, up=(ct in (4.0, 8.0, 58.0, 64.0, 69.5, 73.5, 76.6))), ct - 0.10)
    # door slams (kid 19.95, neighbors 20.55 / 20.95)
    place(bed, sfx_door_slam(0.5), 19.95)
    place(bed, sfx_door_slam(0.34), 20.55)
    place(bed, sfx_door_slam(0.28), 20.95)
    # night ticking clock 23.2 -> 52.4 (the town counting seconds)
    tt = 23.4
    while tt < 52.3:
        place(bed, sfx_tick(2100, g=0.030), tt)
        place(bed, sfx_tick(1400, g=0.018), tt + 0.5)
        tt += 1.0
    # heartbeat under the final approach
    place(bed, sfx_heartbeat(68, 6.5, 0.26), 46.1)
    # cane drop + hat thud
    place(bed, sfx_cane(), 34.65)
    place(bed, sfx_thud(0.16), 53.75)
    # riser into ONE
    place(bed, sfx_riser(2.9, 0.15), 49.70)
    # THE FLASH
    place(bed, sfx_flash(0.6), 52.60)
    # footsteps during the dusk RUN (fast taps, alternating pan)
    ft = 15.75
    k2 = 0
    while ft < 19.35:
        place(bed, sfx_footstep(0.045), ft, pan=(0.35 if k2 % 2 == 0 else -0.35))
        ft += 0.215
        k2 += 1
    # Finch's cane taps as he stumbles
    ct2 = 31.6
    while ct2 < 38.9:
        place(bed, sfx_cane_tap(0.09), ct2, pan=0.15)
        ct2 += 0.55
    # electrical lamp buzz all through the night count
    place(bed, sfx_lamp_buzz(29.2, 0.006), 23.2)
    # dissonant tension swell into ONE
    place(bed, sfx_dissonant_swell(6.4, 0.045), 46.15)
    # morning birds
    for bt, bf, bp in [(58.4, 3300, -0.3), (59.1, 2900, 0.35), (60.1, 3600, 0.15),
                       (61.2, 3050, -0.2), (62.4, 3450, 0.3), (63.6, 2800, -0.35)]:
        place(bed, sfx_bird(bf, 0.17, 0.018, bp), bt)
    # day street ambience (soft airy noise bed 4.0-13.6)
    n_amb = int(9.6 * SR)
    amb = signal.sosfilt(signal.butter(2, 480.0 / (SR * 0.5), btype="low", output="sos"),
                         rng.standard_normal(n_amb).astype(np.float32))
    amb *= (0.6 + 0.4 * np.sin(np.linspace(0, 7, n_amb, dtype=np.float32)))
    place(bed, (amb * 0.006).astype(np.float32), 4.0)
    # dusk wind 15.5-21.6
    n_w = int(6.1 * SR)
    wind = signal.sosfilt(signal.butter(2, [180 / (SR * 0.5), 900 / (SR * 0.5)], btype="bandpass", output="sos"),
                           rng.standard_normal(n_w).astype(np.float32))
    wind *= (0.5 + 0.5 * np.sin(np.linspace(0, 9, n_w, dtype=np.float32)))
    place(bed, (wind * 0.016).astype(np.float32), 15.5)

    # ---- BGM ----
    print("[4/5] BGM...")
    place(bed, bgm_day_plucks(12.9, 0.028), 0.6)
    # dusk tension: short minor pluck cluster
    place(bed, bgm_day_plucks(5.7, 0.020) * 0.8, 15.7)
    place(bed, bgm_night_drone(30.8, 0.050), 21.7)
    place(bed, bgm_day_plucks(5.6, 0.018), 58.0)  # morning eerie-calm
    place(bed, bgm_night_drone(5.6, 0.030), 64.1)  # walk home unease
    place(bed, bgm_end_sting(6.6, 0.085), 73.6)

    # ---- pre-flash moment of silence (bed ducks hard, VO stays) ----
    print("[5/5] Mix + normalize...")
    duck2 = np.ones(N, dtype=np.float32)
    i0, i1 = int(52.26 * SR), int(52.60 * SR)
    duck2[i0:i1] = np.linspace(1.0, 0.06, i1 - i0)
    i2 = int(52.95 * SR)
    duck2[i1:i2] = np.linspace(0.06, 1.0, i2 - i1)
    bed[:, 0] *= duck2
    bed[:, 1] *= duck2
    # bed ducks ~6.5 dB under narration
    mono_vo = vo.mean(axis=1)
    vo_env = np.zeros(N, dtype=np.float32)
    win = int(0.12 * SR)
    kern = np.ones(win, dtype=np.float32) / win
    vo_env = np.convolve(np.abs(mono_vo), kern, mode="same")
    vo_env = np.minimum(1.0, vo_env / max(1e-6, np.percentile(vo_env[vo_env > 1e-4], 85) if (vo_env > 1e-4).any() else 1.0))
    duck = 1.0 - 0.62 * vo_env
    mix = vo * 1.0
    mix[:, 0] += bed[:, 0] * duck
    mix[:, 1] += bed[:, 1] * duck

    # peak safety
    peak = np.abs(mix).max()
    if peak > 0.94:
        mix *= 0.94 / peak

    # write pre-norm, measure LUFS, apply gain, rewrite
    pre = os.path.join(OUT_DIR, "master_audio_prenorm.wav")
    sf.write(pre, mix, SR, subtype="FLOAT")
    import re as _re
    p = subprocess.run([FFMPEG, "-hide_banner", "-i", pre, "-af", "loudnorm=print_format=summary", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = _re.search(r"Input Integrated:\s+(-?\d+\.?\d+)", p.stderr)
    if not m:
        m = _re.search(r"I:\s+(-?\d+\.?\d*) LUFS", p.stderr)
    lufs = float(m.group(1)) if m else -18.0
    gain_db = -14.0 - lufs
    print(f"   pre-norm {lufs:.1f} LUFS -> gain {gain_db:+.1f} dB")
    mix *= 10 ** (gain_db / 20)
    try:
        from pedalboard import Limiter
        mix = Limiter(threshold_db=-1.2, release_ms=100.0)(mix, SR).astype(np.float32)
        print("   peak-limited (-1.2 dBFS)")
    except Exception:
        peak = np.abs(mix).max()
        if peak > 0.97:
            mix *= 0.97 / peak
            print(f"   peak-clamped ({20*np.log10(peak):.1f} dBFS)")

    out_wav = os.path.join(OUT_DIR, "master_audio.wav")
    sf.write(out_wav, mix, SR, subtype="FLOAT")
    print(f"   wrote {out_wav}")

    # ---- captions ----
    write_captions(word_timings)
    print(f"   wrote {CAPTIONS_OUT}")

def write_captions(word_timings):
    """1-3 word Anton captions with pop-in + accent colors, V7-style."""
    def ass_t(x):
        h = int(x // 3600); m = int((x % 3600) // 60); s = x % 60
        return f"{h}:{m:02d}:{s:05.2f}"

    # group words into cues of 1-3 words; break on sentence punctuation
    cues = []
    cur = []
    for (t0, t1, w) in word_timings:
        cur.append((t0, t1, w))
        heavy = any(c in w for c in ".…!?")
        if len(cur) >= 3 or (heavy and len(cur) >= 1):
            cues.append(cur); cur = []
    if cur: cues.append(cur)

    lines = [
        "[Script Info]",
        "Title: The Town That Counts To Ten",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "WrapStyle: 2",
        "ScaledBorderAndShadow: yes",
        "YCbCr Matrix: TV.709",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: OneWord,Anton,96,&H00FFFFFF,&H000000FF,&H0014141A,&H96000000,0,0,0,0,100,100,1.2,0,1,11,2.5,2,80,80,620,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for (xt0, xt1, xtxt, xcol) in EXTRA_CAPTIONS:
        col = RED if xcol == "RED" else BLUE
        lines.append(
            f"Dialogue: 0,{ass_t(xt0)},{ass_t(xt1)},OneWord,,0,0,0,,"
            f"{{\\fscx130\\fscy130\\t(0,70,\\fscx100\\fscy100)\\1c{col}}}{xtxt}"
        )
    for cue in cues:
        t0 = cue[0][0] - 0.02
        t1 = cue[-1][1] + 0.04
        words = [w for (_, _, w) in cue]
        txt = " ".join(words)
        color = ""
        lw = [w.lower().strip(".…!?") for w in words]
        if lw and all(w in COUNT_WORDS for w in lw):
            color = RED
        elif all(w in ACCENT_WORDS or w in ACCENT_WORDS for w in lw) and words:
            color = RED if any(c.isdigit() for c in txt) or words[0].lower() in ("gone", "running", "voice") else BLUE
        ctag = f"\\1c{color}" if color else ""
        lines.append(
            f"Dialogue: 0,{ass_t(max(0,t0))},{ass_t(t1)},OneWord,,0,0,0,,"
            f"{{\\fscx116\\fscy116\\t(0,65,\\fscx100\\fscy100){ctag}}}{txt.upper()}"
        )
    with open(CAPTIONS_OUT, "w") as f:
        f.write("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()

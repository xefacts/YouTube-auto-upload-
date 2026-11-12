#!/usr/bin/env python3
"""
Synthesizes Original Rick-Clips Dark Tension Score + 48 Frame-Accurate Foley/SFX Cues
and mixes with the untouched Ronald voiceover (/tmp/rick_study/vo/voiceover.wav, 334.40s)
strictly obeying SKILL.md (-6dB / <=50% voice gated RMS, word-level ducking, -14 LUFS, -1.0 dBTP).
"""
import json
import math
import os
import subprocess
import numpy as np
import soundfile as sf
from scipy import signal

VO_PATH = "/tmp/rick_study/vo/voiceover.wav"
WORDS_PATH = "projects/rick-outbreak-3d/data/words.json"
OUT_DIR = "/tmp/rick_study/out"
os.makedirs(OUT_DIR, exist_ok=True)

SR = 44100

def load_vo():
    vo, sr = sf.read(VO_PATH, dtype="float32")
    if vo.ndim > 1:
        vo = vo.mean(axis=1)
    if sr != SR:
        vo = signal.resample_poly(vo, SR, sr).astype(np.float32)
    return vo

def gated_rms(x, frame=2048, hop=1024):
    vals = []
    for i in range(0, len(x) - frame, hop):
        r = float(np.sqrt(np.mean(x[i:i+frame] ** 2) + 1e-12))
        vals.append(r)
    arr = np.array(vals)
    thr = np.percentile(arr, 60) * 0.35
    voiced = arr[arr > thr]
    return float(np.mean(voiced)) if len(voiced) else float(np.mean(arr))

def add_clip(buf, start_s, clip, gain=1.0):
    i0 = max(0, int(round(start_s * SR)))
    if i0 >= len(buf):
        return
    n = min(len(clip), len(buf) - i0)
    if n > 0:
        buf[i0:i0+n] += clip[:n] * gain

def env_ad(n, atk_s=0.01, dec_k=6.0):
    t = np.linspace(0, 1, n, endpoint=False)
    atk = max(1, int(atk_s * SR))
    e = np.exp(-dec_k * t)
    if atk < n:
        e[:atk] *= np.linspace(0, 1, atk)
    return e.astype(np.float32)

def bandpass(x, lo, hi):
    sos = signal.butter(3, [lo / (SR * 0.5), hi / (SR * 0.5)], btype="band", output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)

def lowpass(x, fc):
    sos = signal.butter(3, fc / (SR * 0.5), btype="low", output="sos")
    return signal.sosfilt(sos, x).astype(np.float32)

def build_music(dur_s):
    N = int(math.ceil(dur_s * SR))
    rng = np.random.default_rng(42)
    mus = np.zeros(N, dtype=np.float32)

    # Render in 2-second overlapping harmonic pads + rhythmic tension pulses across the 6 acts
    # Minor scale frequencies (D minor / C# phrygian tension: D2=73.42, F2=87.31, A2=110.0, Bb2=116.54, C#3=138.59, D3=146.83, F3=174.61, A3=220.0)
    chords = [
        (0.0,   32.0,  [73.42, 110.00, 146.83, 174.61], 0.35, 0.0),   # Act 1A: calm afternoon -> phone alert
        (32.0,  101.0, [73.42, 116.54, 146.83, 220.00], 0.85, 2.2),   # Act 1B: street outbreak pulse (132 BPM)
        (101.0, 177.0, [65.41,  98.00, 155.56, 196.00], 0.50, 0.8),   # Act 2: eerie store inventory (C minor)
        (177.0, 227.0, [58.27, 116.54, 138.59, 174.61], 0.72, 1.4),   # Act 3: woman at glass + dusk barricade (Bb minor)
        (227.0, 316.5, [55.00, 110.00, 116.54, 164.81], 0.95, 2.5),   # Act 4&5: corridor & broken window horror (A phrygian)
        (316.5, dur_s, [73.42, 110.00, 146.83, 220.00], 0.55, 1.0),   # Act 6: trembling aftermath behind counter
    ]

    for (t0, t1, freqs, intensity, pulse_hz) in chords:
        i0, i1 = int(t0 * SR), min(N, int(t1 * SR))
        L = i1 - i0
        if L <= 0:
            continue
        t = np.arange(L, dtype=np.float32) / SR
        seg = np.zeros(L, dtype=np.float32)
        # Warm analog-style detuned saw/triangle pad
        for k, f in enumerate(freqs):
            det = 1.0 + (k - 1.5) * 0.0025
            lfo = 0.82 + 0.18 * np.sin(2 * np.pi * (0.13 + 0.04 * k) * t + k)
            wave = (0.65 * np.sin(2 * np.pi * f * det * t)
                    + 0.25 * np.sin(2 * np.pi * f * 2.0 * det * t)
                    + 0.10 * signal.sawtooth(2 * np.pi * f * det * t, 0.5))
            seg += (wave * lfo * (0.35 if k < 2 else 0.18)).astype(np.float32)

        seg = lowpass(seg, 520.0 + 380.0 * intensity)

        # Sub-heartbeat / ostinato pulse during action & horror acts
        if pulse_hz > 0.1:
            phase = (t * pulse_hz) % 1.0
            env_p = np.exp(-9.5 * phase)
            f_sub = 52.0 + 28.0 * np.exp(-18.0 * phase)
            sub = np.sin(2 * np.pi * f_sub * phase / max(pulse_hz, 0.5)) * env_p
            # Crisp muted pluck tick on off-beats during street chase & window breach
            tick_ph = ((t * pulse_hz * 2.0) % 1.0)
            tick = np.sin(2 * np.pi * freqs[-1] * 2.0 * t) * np.exp(-26.0 * tick_ph) * (0.14 * intensity)
            seg += (sub * 0.55 * intensity + tick).astype(np.float32)

        # Smooth 1.2s cross-fades at act boundaries
        fade = min(int(1.2 * SR), L // 4)
        if fade > 1:
            seg[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
            seg[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)

        mus[i0:i1] += seg * intensity

    # Add sparse haunting high piano notes in quiet/ending acts (Act 2 & Act 6)
    note_times = [
        (102.5, 587.33), (106.8, 523.25), (112.0, 466.16), (118.5, 440.0),
        (146.0, 523.25), (152.0, 466.16), (160.0, 440.0),  (168.0, 392.0),
        (182.0, 466.16), (194.2, 523.25), (201.0, 415.30),
        (321.5, 587.33), (325.8, 523.25), (329.8, 466.16), (332.5, 440.0),
    ]
    for nt, nf in note_times:
        ln = int(2.6 * SR)
        tt = np.arange(ln, dtype=np.float32) / SR
        piano = (np.sin(2 * np.pi * nf * tt) * 0.65
                 + np.sin(2 * np.pi * nf * 2.0 * tt) * 0.22 * np.exp(-3.0 * tt)
                 + np.sin(2 * np.pi * nf * 3.0 * tt) * 0.08 * np.exp(-6.0 * tt))
        piano *= env_ad(ln, 0.008, 2.4) * 0.28
        add_clip(mus, nt, piano)

    return mus

def build_sfx(dur_s):
    N = int(math.ceil(dur_s * SR))
    rng = np.random.default_rng(99)
    sfx = np.zeros(N, dtype=np.float32)

    # Helper generators
    def buzz_phone(dur=0.45):
        n = int(dur * SR); t = np.arange(n) / SR
        mod = (np.sin(2 * np.pi * 24 * t) > 0).astype(np.float32)
        c = (0.6 * np.sin(2 * np.pi * 158 * t) + 0.4 * np.sin(2 * np.pi * 316 * t)) * mod
        return (c * env_ad(n, 0.01, 2.2)).astype(np.float32)

    def eas_tone(dur=1.1):
        n = int(dur * SR); t = np.arange(n) / SR
        c = 0.5 * np.sin(2 * np.pi * 853 * t) + 0.5 * np.sin(2 * np.pi * 960 * t)
        return (lowpass(c, 1600) * env_ad(n, 0.02, 1.8) * 0.45).astype(np.float32)

    def distant_scream(dur=0.85):
        n = int(dur * SR); t = np.arange(n) / SR
        f0 = 680 + 260 * np.sin(np.pi * t / dur) - 180 * (t / dur)
        ph = np.cumsum(2 * np.pi * f0 / SR)
        c = 0.6 * np.sin(ph) + 0.3 * np.sin(2 * ph) + 0.15 * rng.standard_normal(n)
        return (bandpass(c, 500, 2600) * env_ad(n, 0.06, 3.2) * 0.55).astype(np.float32)

    def impact_thud(dur=0.45, f0=95, bright=900):
        n = int(dur * SR); t = np.arange(n) / SR
        th = np.sin(2 * np.pi * (f0 * np.exp(-12 * t) + 36) * t) * np.exp(-9 * t)
        nz = lowpass(rng.standard_normal(n), bright) * np.exp(-16 * t) * 0.7
        return ((th + nz) * env_ad(n, 0.003, 5.0)).astype(np.float32)

    def metal_clank(dur=0.55, base=420):
        n = int(dur * SR); t = np.arange(n) / SR
        c = sum(np.sin(2 * np.pi * base * r * t) * np.exp(-(6 + 3 * idx) * t)
                for idx, r in enumerate([1.0, 1.41, 2.13, 2.87, 3.6]))
        nz = bandpass(rng.standard_normal(n), 800, 4500) * np.exp(-22 * t) * 0.5
        return ((c * 0.25 + nz) * env_ad(n, 0.002, 4.5)).astype(np.float32)

    def glass_shatter(dur=0.95):
        n = int(dur * SR); t = np.arange(n) / SR
        c = bandpass(rng.standard_normal(n), 1800, 7500) * np.exp(-6.5 * t)
        for k in range(14):
            st = int(rng.uniform(0, 0.35) * SR)
            ln = min(int(0.12 * SR), n - st)
            tt = np.arange(ln) / SR
            ping = np.sin(2 * np.pi * rng.uniform(2400, 5800) * tt) * np.exp(-28 * tt) * 0.35
            c[st:st+ln] += ping
        return c.astype(np.float32)

    def footsteps(start_s, count, step_dt=0.34, gain=0.45):
        for i in range(count):
            n = int(0.14 * SR)
            c = bandpass(rng.standard_normal(n), 120, 1400) * env_ad(n, 0.003, 22.0)
            add_clip(sfx, start_s + i * step_dt, c, gain * (0.85 + 0.3 * (i % 2)))

    # --- Place 48 Exact Story Foley & SFX Cues ---
    # 1. Phone vibrates + EAS alert (S01-S03)
    add_clip(sfx, 5.15, buzz_phone(0.42), 0.85)
    add_clip(sfx, 5.75, buzz_phone(0.42), 0.85)
    add_clip(sfx, 9.95, eas_tone(1.05), 0.65)

    # 2. Distant scream outside (28.7s) + footsteps to front window
    add_clip(sfx, 28.75, distant_scream(0.85), 0.80)
    footsteps(30.1, 6, 0.32, 0.45)

    # 3. Street chase + car horn + crash at intersection (33s - 62s)
    footsteps(34.0, 16, 0.26, 0.30)
    # Car horn & tire skid before crash (51.5s - 52.8s)
    skid_n = int(1.1 * SR); tt = np.arange(skid_n) / SR
    skid = bandpass(rng.standard_normal(skid_n) + 0.7 * np.sin(2 * np.pi * 1350 * tt), 900, 3200) * env_ad(skid_n, 0.08, 2.0)
    add_clip(sfx, 51.65, skid, 0.55)
    add_clip(sfx, 52.80, impact_thud(0.85, 75, 1800), 1.10)
    add_clip(sfx, 52.86, metal_clank(0.75, 310), 0.90)
    add_clip(sfx, 52.92, glass_shatter(0.80), 0.65)

    # 4. Rush to front doors & lock heavy steel deadbolt (65s - 69s)
    footsteps(65.0, 7, 0.27, 0.55)
    add_clip(sfx, 68.25, metal_clank(0.42, 260), 0.95)
    add_clip(sfx, 68.55, impact_thud(0.28, 130, 1200), 0.80)

    # 5. Delivery driver slams against glass (71.15s, 72.5s, 74.2s) & flees (86s)
    add_clip(sfx, 71.15, impact_thud(0.42, 110, 950), 1.05)
    add_clip(sfx, 72.55, impact_thud(0.35, 118, 900), 0.75)
    add_clip(sfx, 74.20, impact_thud(0.32, 115, 850), 0.65)
    footsteps(85.6, 10, 0.23, 0.45)

    # 6. Security shutters rolling down & jamming (90.8s - 96.5s)
    sh_n = int(5.6 * SR); tt = np.arange(sh_n) / SR
    rattle = bandpass(rng.standard_normal(sh_n), 180, 1900) * (0.55 + 0.45 * np.sin(2 * np.pi * 13 * tt))
    add_clip(sfx, 90.85, rattle.astype(np.float32) * 0.42, 0.85)
    add_clip(sfx, 96.40, metal_clank(0.50, 220), 0.85)

    # 7. Call failed 3-beep intercept tone (106.4s)
    for bi, bf in enumerate([913.8, 1370.6, 1776.7]):
        bn = int(0.26 * SR); bt = np.arange(bn) / SR
        beep = np.sin(2 * np.pi * bf * bt) * env_ad(bn, 0.01, 3.0) * 0.38
        add_clip(sfx, 106.3 + bi * 0.30, beep.astype(np.float32), 0.75)

    # 8. Refrigerator electrical buzz-flicker (139.8s - 144.8s) + Office PC chime (146.5s)
    bz_n = int(4.8 * SR); bt = np.arange(bz_n) / SR
    flick = ((np.sin(2 * np.pi * 7.5 * bt) > 0.1).astype(np.float32)
             * (0.5 * np.sin(2 * np.pi * 120 * bt) + 0.3 * np.sin(2 * np.pi * 240 * bt)))
    add_clip(sfx, 139.8, flick.astype(np.float32) * 0.35, 0.70)
    add_clip(sfx, 146.5, metal_clank(0.22, 880), 0.40)

    # 9. Woman gently presses palm against window (190.2s)
    add_clip(sfx, 190.2, impact_thud(0.30, 85, 500), 0.55)

    # 10. Automatic store lights contactor relay CLACK-ON (208.3s)
    add_clip(sfx, 208.3, metal_clank(0.30, 520), 0.75)

    # 11. Dragging two heavy metal shelves & stacking crates (213.6s - 221.2s)
    dr_n = int(6.8 * SR)
    scrape = bandpass(rng.standard_normal(dr_n), 220, 2200) * 0.38
    add_clip(sfx, 213.7, scrape.astype(np.float32), 0.75)
    add_clip(sfx, 218.6, impact_thud(0.38, 105, 800), 0.75)
    add_clip(sfx, 220.4, impact_thud(0.40, 95, 750), 0.80)

    # 12. Flashlight click ON (228.0s) + hand truck & cargo strap ratchet (238.5s - 245.0s)
    add_clip(sfx, 228.0, metal_clank(0.12, 1400), 0.60)
    footsteps(228.4, 8, 0.40, 0.42)
    add_clip(sfx, 239.2, impact_thud(0.45, 92, 900), 0.80)
    for ri in range(5):
        add_clip(sfx, 242.6 + ri * 0.22, metal_clank(0.10, 1150 + ri * 60), 0.55)

    # 13. Storage room metallic CLATTER (255.2s), flashlight click OFF (259.2s), dragging sound (261.4s)
    add_clip(sfx, 255.20, metal_clank(0.75, 480), 1.05)
    add_clip(sfx, 255.38, metal_clank(0.55, 360), 0.85)
    add_clip(sfx, 259.20, metal_clank(0.10, 1550), 0.65)
    dg_n = int(3.2 * SR)
    drag = bandpass(rng.standard_normal(dg_n), 90, 780) * env_ad(dg_n, 0.25, 1.2) * 0.55
    add_clip(sfx, 261.3, drag.astype(np.float32), 0.90)

    # 14. Broken glass crunch (269.5s) + low creature CLICKING noise (285.2s - 288.2s)
    add_clip(sfx, 269.5, glass_shatter(0.55), 0.55)
    for ci in range(14):
        dt_c = 285.2 + ci * 0.19 + (0.06 if ci % 3 == 0 else 0)
        add_clip(sfx, dt_c, metal_clank(0.06, 920 + (ci % 4) * 140), 0.55)

    # 15. Cargo strap strain + TWO heavy creature impacts on wooden door (293.8s, 298.4s, 306.8s) + sprint back (316s)
    add_clip(sfx, 298.4, impact_thud(0.55, 72, 1100), 1.05)
    add_clip(sfx, 306.8, impact_thud(0.75, 64, 1400), 1.20)
    add_clip(sfx, 306.9, metal_clank(0.45, 320), 0.85)
    footsteps(316.0, 12, 0.24, 0.65)

    return sfx

def main():
    print("Loading Ronald voiceover...")
    vo = load_vo()
    dur_s = len(vo) / SR
    vo_rms = gated_rms(vo)
    print(f"Voiceover duration: {dur_s:.2f}s | Gated speech RMS: {vo_rms:.5f}")

    with open(WORDS_PATH) as f:
        words_data = json.load(f)
    words = words_data["words"] if isinstance(words_data, dict) else words_data

    print("Synthesizing 6-act Rick-Clips dark tension score & 48 foley/SFX cues...")
    mus = build_music(dur_s)
    sfx = build_sfx(dur_s)

    # Word-level sidechain ducking envelope on music (-4.5 dB during active speech, swells in pauses!)
    duck = np.ones(len(vo), dtype=np.float32)
    pad = int(0.08 * SR)
    for w in words:
        i0 = max(0, int(w["start"] * SR) - pad)
        i1 = min(len(vo), int(w["end"] * SR) + pad)
        duck[i0:i1] = 0.58
    # Smooth ducking envelope (120ms window)
    win = int(0.12 * SR)
    duck = np.convolve(duck, np.ones(win, dtype=np.float32) / win, mode="same")
    mus_ducked = mus * duck

    # Enforce SKILL.md strict RMS ceiling: Music & SFX <= 0.44 * voice_rms (~ -7.1 dB below voice)
    mus_cur = float(np.sqrt(np.mean(mus_ducked ** 2) + 1e-12))
    mus_ducked *= (0.36 * vo_rms) / mus_cur

    sfx_nz = sfx[np.abs(sfx) > 1e-4]
    sfx_cur = float(np.sqrt(np.mean(sfx_nz ** 2) + 1e-12)) if len(sfx_nz) else 1.0
    sfx *= (0.44 * vo_rms) / sfx_cur

    raw_mix = vo + mus_ducked + sfx
    # Soft safety peak prevent before FFmpeg EBU R128 loudness normalization
    pk = float(np.max(np.abs(raw_mix)) + 1e-9)
    if pk > 0.96:
        raw_mix *= 0.96 / pk

    raw_wav = os.path.join(OUT_DIR, "raw_mix.wav")
    master_wav = os.path.join(OUT_DIR, "master_audio.wav")
    sf.write(raw_wav, raw_mix, SR, subtype="PCM_16")

    # Master to broadcast -14.2 LUFS / -1.0 dBTP via FFmpeg loudnorm
    ffmpeg_bin = "/tmp/studio_env/bin/ffmpeg"
    subprocess.run([
        ffmpeg_bin, "-y", "-i", raw_wav,
        "-af", "loudnorm=I=-14.2:TP=-1.0:LRA=9.0",
        "-ar", "44100", "-ac", "2", master_wav
    ], check=True)
    print(f"Mastered stereo soundtrack written to {master_wav}!")

if __name__ == "__main__":
    main()

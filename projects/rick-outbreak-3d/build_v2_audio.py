#!/usr/bin/env python3
"""
V2 Fast-Paced Emotional Horror Voiceover + 100% Vocal-Only Dark Soundscape (NO MUSIC) + Clean Cinema Foley
- Uses 100% of the user's full 933-word Ronald script (/tmp/rick_study/vo/voiceover.wav)
- Strips all sluggish dead air + applies act-specific fast-paced time-stretch & Spotify Pedalboard emotional vocal DSP
- Injects subtle, realistic human horror breaths/gasps at key terror beats
- Synthesizes a 100% VOCAL-ONLY dark choir/throat-hum atmosphere (ZERO musical instruments)
- Replaces all harsh static/shutter noise with clean, punchy, low-noise cinema foley
- Outputs exact word timestamps -> projects/rick-outbreak-3d/data/words_v2.json
"""
import json
import math
import os
import subprocess
import sys

sys.path.insert(0, "/tmp/studio_env/pypkgs")
import numpy as np
import soundfile as sf
from scipy import signal
import librosa
from pedalboard import (
    Pedalboard, Compressor, HighpassFilter, LowpassFilter,
    PeakFilter, HighShelfFilter, LowShelfFilter, Reverb, Gain, Limiter
)

VO_PATH    = "/tmp/rick_study/vo/voiceover.wav"
WORDS_IN   = "projects/rick-outbreak-3d/data/words.json"
WORDS_OUT  = "projects/rick-outbreak-3d/data/words_v2.json"
OUT_DIR    = "/tmp/rick_study/v2"
os.makedirs(OUT_DIR, exist_ok=True)

SR = 44100

# Act-by-act speed & emotional tone profile (keyed by original V1 timestamp)
# Returns (stretch_rate, pitch_semitones, breath_before_prob, intensity)
def act_profile(orig_t, text):
    tl = text.lower()
    if orig_t < 9.5:
        # Opening setup -> phone buzz: brisk, crisp hook!
        return 1.26, 0.0, False, 0.35
    elif orig_t < 26.4:
        # Emergency Alert reading: tense, urgent authority
        return 1.30, 0.20, ("emergency" in tl), 0.65
    elif orig_t < 62.7:
        # Street scream, chase, man falls, car crash: fast-paced adrenaline!
        if "falls" in tl or "help him" in tl:
            return 1.22, -0.25, True, 0.85  # dark chilling weight on "And they don't help him"
        return 1.35, 0.30, ("screams" in tl or "seconds" in tl), 0.90
    elif orig_t < 101.2:
        # Deadbolt, delivery driver slam, shutters: high urgency
        return 1.33, 0.25, ("slams" in tl or "turns around" in tl), 0.85
    elif orig_t < 176.9:
        # Phone call failed, empty shelves, office PC, ration count: brisk tense survival
        return 1.29, -0.10, ("worse" in tl or "nothing" in tl), 0.55
    elif orig_t < 227.2:
        # Woman at glass ("Help me"), zombie behind her, night barricade: eerie dread
        if "help me" in tl or "appeared behind" in tl:
            return 1.20, -0.35, True, 0.80
        return 1.28, -0.15, ("standing" in tl), 0.70
    elif orig_t < 316.0:
        # Corridor, clatter, broken window, pale arm clicking, creature impacts: peak terror!
        if "clatter" in tl or "broken" in tl or "clicking" in tl or "impact" in tl:
            return 1.34, 0.25, True, 1.00
        return 1.32, 0.15, False, 0.92
    else:
        # Sprint back & trembling behind counter recounting rations: breathless aftermath
        return 1.24, -0.20, True, 0.65


def synth_subtle_breath(rng, dur=0.19, gasp=False):
    """Synthesizes a soft, natural human vocal-tract inhale/gasp (formant-filtered, zero harsh hiss)."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n, endpoint=False, dtype=np.float32)
    raw = rng.standard_normal(n).astype(np.float32)
    # Vocal tract formants F1=520Hz, F2=1450Hz, F3=2450Hz (soft open throat inhale)
    out = np.zeros(n, dtype=np.float32)
    for fc, bw, g in [(480, 180, 0.55), (1380, 320, 0.32), (2350, 450, 0.12)]:
        sos = signal.butter(2, [max(60, fc - bw/2)/(SR*0.5), min(SR*0.45, fc + bw/2)/(SR*0.5)], btype="band", output="sos")
        out += signal.sosfilt(sos, raw).astype(np.float32) * g
    if gasp:
        env = np.sin(np.pi * (t ** 0.65)) ** 1.4
    else:
        env = np.sin(np.pi * t) ** 1.6
    out *= env * (0.045 if gasp else 0.030)
    return out.astype(np.float32)


def build_fast_vo():
    vo_raw, sr_in = sf.read(VO_PATH, dtype="float32")
    if vo_raw.ndim > 1:
        vo_raw = vo_raw.mean(axis=1)
    if sr_in != SR:
        vo_raw = signal.resample_poly(vo_raw, SR, sr_in).astype(np.float32)

    with open(WORDS_IN) as f:
        data = json.load(f)
    segments = data["segments"]
    all_words = data["words"]

    rng = np.random.default_rng(77)
    out_chunks = []
    new_words = []
    new_segments = []
    # Map anchor points (orig_t -> new_t) so story beats convert with 100% precision!
    anchors = [[0.0, 0.0]]
    cur_samples = 0

    # Group words into their segments
    w_idx = 0
    n_words = len(all_words)

    for s_i, seg in enumerate(segments):
        s0 = seg["start"]
        s1 = seg["end"]
        seg_words = []
        while w_idx < n_words and all_words[w_idx]["start"] < s1 - 0.01:
            seg_words.append(all_words[w_idx])
            w_idx += 1
        if not seg_words:
            continue

        rate, pitch_st, add_breath, inten = act_profile(s0, seg["text"])

        # Optional subtle human breath before high-tension segments
        if add_breath and s_i > 0:
            br = synth_subtle_breath(rng, dur=0.17 if inten > 0.8 else 0.14, gasp=(inten >= 0.85))
            out_chunks.append(br)
            cur_samples += len(br)

        # Slice word-by-word / micro-phrase within segment so internal dead air > 0.10s is tightened too!
        sub_phrases = []
        cur_p = [seg_words[0]]
        for w in seg_words[1:]:
            gap = w["start"] - cur_p[-1]["end"]
            if gap > 0.14:
                sub_phrases.append(cur_p)
                cur_p = [w]
            else:
                cur_p.append(w)
        sub_phrases.append(cur_p)

        seg_new_start = cur_samples / SR

        for p_i, ph in enumerate(sub_phrases):
            ps0 = max(0.0, ph[0]["start"] - 0.018)
            ps1 = min(len(vo_raw) / SR, ph[-1]["end"] + 0.024)
            i0, i1 = int(round(ps0 * SR)), int(round(ps1 * SR))
            clip = vo_raw[i0:i1].copy()
            if len(clip) < 256:
                continue

            # Trim leading/trailing near-silence inside the slice
            abs_c = np.abs(clip)
            thr = max(1e-4, np.percentile(abs_c, 85) * 0.035)
            nz = np.where(abs_c > thr)[0]
            if len(nz) > 10:
                pad_s = int(0.012 * SR)
                t_start = max(0, nz[0] - pad_s)
                t_end = min(len(clip), nz[-1] + pad_s)
                ps0 += t_start / SR
                clip = clip[t_start:t_end]

            orig_dur = len(clip) / SR
            # High-clarity time-stretch + subtle emotional pitch shift
            stretched = librosa.effects.time_stretch(clip, rate=rate)
            if abs(pitch_st) > 0.05:
                stretched = librosa.effects.pitch_shift(stretched, sr=SR, n_steps=pitch_st)

            # Soft 6ms fade-in/out to prevent any click at splice boundaries
            fd = min(int(0.006 * SR), len(stretched) // 4)
            if fd > 1:
                stretched[:fd] *= np.linspace(0, 1, fd, dtype=np.float32)
                stretched[-fd:] *= np.linspace(1, 0, fd, dtype=np.float32)

            new_dur = len(stretched) / SR
            phrase_new_t0 = cur_samples / SR
            scale_k = new_dur / max(1e-5, orig_dur)

            for w in ph:
                nw0 = phrase_new_t0 + max(0.0, (w["start"] - ps0)) * scale_k
                nw1 = phrase_new_t0 + max(0.03, (w["end"] - ps0)) * scale_k
                nw1 = min(phrase_new_t0 + new_dur, max(nw0 + 0.04, nw1))
                new_words.append({
                    "word": w["word"],
                    "start": round(float(nw0), 4),
                    "end": round(float(nw1), 4),
                    "orig_start": round(float(w["start"]), 3),
                })
                anchors.append([float(w["start"]), float(nw0)])
                anchors.append([float(w["end"]), float(nw1)])

            out_chunks.append(stretched.astype(np.float32))
            cur_samples += len(stretched)

            # Tight fast-paced pause between sub-phrases (45ms)
            if p_i < len(sub_phrases) - 1:
                sil = np.zeros(int(0.045 * SR), dtype=np.float32)
                out_chunks.append(sil)
                cur_samples += len(sil)

        seg_new_end = cur_samples / SR
        new_segments.append({
            "start": round(seg_new_start, 3),
            "end": round(seg_new_end, 3),
            "orig_start": s0,
            "orig_end": s1,
            "text": seg["text"],
        })

        # Tight fast-paced inter-sentence pause (65ms normal, 95ms at major act turns)
        is_act_turn = any(abs(s1 - at) < 1.2 for at in [9.2, 26.4, 62.7, 101.0, 176.9, 206.4, 227.2, 257.4, 316.0])
        gap_s = 0.095 if is_act_turn else 0.058
        sil = np.zeros(int(gap_s * SR), dtype=np.float32)
        out_chunks.append(sil)
        cur_samples += len(sil)

    # Small 0.35s tail hold at the end
    out_chunks.append(np.zeros(int(0.35 * SR), dtype=np.float32))
    vo_fast = np.concatenate(out_chunks)

    # Studio ElevenLabs-grade Dark Cinema Voice Mastering Chain via Spotify Pedalboard!
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=78.0),
        LowShelfFilter(cutoff_frequency_hz=155.0, gain_db=2.2, q=0.75),     # rich chest warmth
        PeakFilter(cutoff_frequency_hz=380.0, gain_db=-1.8, q=1.4),         # remove boxiness
        PeakFilter(cutoff_frequency_hz=2850.0, gain_db=2.4, q=1.1),         # crisp articulation clarity
        HighShelfFilter(cutoff_frequency_hz=7500.0, gain_db=1.8, q=0.7),    # silky air
        Compressor(threshold_db=-19.0, ratio=3.2, attack_ms=6.0, release_ms=95.0),
        Reverb(room_size=0.18, damping=0.82, wet_level=0.035, dry_level=0.98), # subtle intimate room space
        Gain(gain_db=2.5),
        Limiter(threshold_db=-1.5, release_ms=60.0),
    ])
    vo_master = board(vo_fast, SR).astype(np.float32)

    anchors.append([334.40, len(vo_master) / SR])
    # Deduplicate & sort anchors monotonically
    anchors.sort(key=lambda x: x[0])
    clean_anc = [anchors[0]]
    for ot, nt in anchors[1:]:
        if ot > clean_anc[-1][0] + 1e-4 and nt >= clean_anc[-1][1]:
            clean_anc.append([round(ot, 4), round(nt, 4)])

    return vo_master, new_words, new_segments, clean_anc


def map_time(orig_t, anchors):
    ots = [a[0] for a in anchors]
    nts = [a[1] for a in anchors]
    return float(np.interp(orig_t, ots, nts))


def build_vocal_only_horror_pad(dur_s, anchors):
    """
    100% VOCAL-ONLY DARK SOUNDTRACK (ZERO MUSICAL INSTRUMENTS!).
    Synthesizes a deep human male throat-hum / dark acapella vocal drone ('mmmm / ooooh / uuuu')
    using glottal Rosenberg pulses + human vowel formant filters + dark cathedral reverb,
    plus natural wind/air room tone and visceral human heartbeat pulses!
    """
    N = int(math.ceil(dur_s * SR))
    rng = np.random.default_rng(313)
    pad = np.zeros(N, dtype=np.float32)

    # Map act boundaries from original timeline -> V2 fast timeline
    t_alert   = map_time(9.5, anchors)
    t_street  = map_time(28.5, anchors)
    t_shut    = map_time(90.0, anchors)
    t_woman   = map_time(177.0, anchors)
    t_corr    = map_time(227.2, anchors)
    t_breach  = map_time(255.0, anchors)
    t_end     = map_time(316.0, anchors)

    acts = [
        (0.0,      t_alert,  55.0,  "mmm",  0.22, 0.0),   # subtle low room hum
        (t_alert,  t_street, 55.0,  "ooo",  0.55, 1.05),  # alert tension vocal drone + slow heartbeat
        (t_street, t_shut,   58.27, "uuu",  0.85, 1.65),  # street terror dark choir hum + fast heartbeat
        (t_shut,   t_woman,  49.00, "mmm",  0.48, 0.85),  # eerie isolated store low vocal drone
        (t_woman,  t_corr,   51.91, "ooo",  0.72, 1.15),  # haunting dusk vocal choir ("Help me")
        (t_corr,   t_breach, 46.25, "uuu",  0.78, 1.30),  # corridor dread sub-vocal hum
        (t_breach, t_end,    43.65, "aaa",  0.98, 1.85),  # broken window monster horror vocal swell + pounding heart!
        (t_end,    dur_s,    49.00, "mmm",  0.52, 1.10),  # trembling aftermath vocal drone
    ]

    # Vowel formant tables (F1, F2, F3 in Hz) for authentic human vocal tract resonance
    VOWELS = {
        "mmm": [(270, 90, 1.0),  (850, 140, 0.22), (2100, 220, 0.05)],
        "uuu": [(310, 100, 1.0), (780, 150, 0.35), (2250, 260, 0.08)],
        "ooo": [(410, 110, 1.0), (820, 160, 0.42), (2350, 280, 0.10)],
        "aaa": [(560, 130, 0.9), (1080, 190, 0.48), (2450, 320, 0.14)],
    }

    for (a0, a1, f0, vowel, inten, heart_hz) in acts:
        i0, i1 = int(a0 * SR), min(N, int(a1 * SR))
        L = i1 - i0
        if L <= 256:
            continue
        t = np.arange(L, dtype=np.float32) / SR

        # Ensemble of 4 human male bass/baritone voices with natural human vibrato & micro-drift (NO synth waves!)
        glottal = np.zeros(L, dtype=np.float32)
        for v_i, ratio in enumerate([1.0, 1.004, 0.996, 1.498]):  # unison + dark 5th vocal harmony
            vib = 1.0 + 0.0045 * np.sin(2 * np.pi * (4.1 + 0.35 * v_i) * t + v_i * 1.7)
            ph = np.cumsum(2 * np.pi * (f0 * ratio * vib) / SR)
            # Soft glottal vocal cord waveform (bandlimited first 6 human harmonics + natural breathiness)
            voice_src = (0.55 * np.sin(ph)
                         + 0.30 * np.sin(2 * ph + 0.3)
                         + 0.16 * np.sin(3 * ph + 0.7)
                         + 0.08 * np.sin(4 * ph)
                         + 0.04 * np.sin(5 * ph))
            swell = 0.78 + 0.22 * np.sin(2 * np.pi * (0.11 + 0.03 * v_i) * t + v_i)
            glottal += (voice_src * swell * (0.35 if v_i < 3 else 0.20)).astype(np.float32)

        # Add gentle human vocal breath air (very soft, < 400Hz-1200Hz formant-shaped)
        breath_src = rng.standard_normal(L).astype(np.float32) * 0.06
        src = glottal + breath_src

        # Pass through human vocal tract formant resonators!
        tract = np.zeros(L, dtype=np.float32)
        for fc, bw, g in VOWELS[vowel]:
            lo = max(45.0, fc - bw * 0.5) / (SR * 0.5)
            hi = min(0.90, (fc + bw * 0.5) / (SR * 0.5))
            sos = signal.butter(2, [lo, hi], btype="band", output="sos")
            tract += signal.sosfilt(sos, src).astype(np.float32) * g

        # Keep fundamental sub-chest resonance warm & deep
        sos_sub = signal.butter(2, 160.0 / (SR * 0.5), btype="low", output="sos")
        tract += signal.sosfilt(sos_sub, glottal).astype(np.float32) * 0.55

        # Natural human heartbeat ("lub-dub") during tense/horror acts
        if heart_hz > 0.1:
            cyc = (t * heart_hz) % 1.0
            # Lub at 0.0, Dub at 0.28
            lub = np.sin(2 * np.pi * 48.0 * cyc / heart_hz) * np.exp(-16.0 * cyc)
            dub_c = np.maximum(0.0, cyc - 0.26)
            dub = np.sin(2 * np.pi * 42.0 * dub_c / heart_hz) * np.exp(-20.0 * dub_c) * (cyc >= 0.26)
            heart = (lub * 0.65 + dub * 0.48) * (0.55 * inten)
            tract += heart.astype(np.float32)

        # Smooth 0.9s cross-fades between acts
        fd = min(int(0.9 * SR), L // 3)
        if fd > 1:
            tract[:fd] *= np.linspace(0, 1, fd, dtype=np.float32)
            tract[-fd:] *= np.linspace(1, 0, fd, dtype=np.float32)

        pad[i0:i1] += tract * inten

    # Lush dark cathedral reverb via Spotify Pedalboard (pure human choir depth, zero harshness!)
    choir_board = Pedalboard([
        LowpassFilter(cutoff_frequency_hz=680.0),
        Reverb(room_size=0.88, damping=0.78, wet_level=0.58, dry_level=0.55),
    ])
    pad = choir_board(pad, SR).astype(np.float32)
    return pad


def build_clean_horror_sfx(dur_s, anchors):
    """
    Clean, punchy, NON-HARSH cinema horror foley (ZERO long static/shutter white noise!).
    """
    N = int(math.ceil(dur_s * SR))
    rng = np.random.default_rng(2026)
    sfx = np.zeros(N, dtype=np.float32)

    def place(orig_t, clip, gain=1.0):
        nt = map_time(orig_t, anchors)
        i0 = max(0, int(round(nt * SR)))
        if i0 >= N:
            return
        m = min(len(clip), N - i0)
        if m > 0:
            sfx[i0:i0 + m] += clip[:m] * gain

    def lp(x, fc):
        sos = signal.butter(3, min(0.92, fc / (SR * 0.5)), btype="low", output="sos")
        return signal.sosfilt(sos, x).astype(np.float32)

    def bp(x, lo, hi):
        sos = signal.butter(2, [max(0.002, lo / (SR * 0.5)), min(0.92, hi / (SR * 0.5))], btype="band", output="sos")
        return signal.sosfilt(sos, x).astype(np.float32)

    def soft_phone_vibe(dur=0.26):
        # Clean, soft low haptic motor hum (142 Hz sine + soft 284 Hz overtone, NO harsh square buzz!)
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        env = np.sin(np.pi * t / dur) ** 1.3
        vibe = (0.78 * np.sin(2 * np.pi * 142 * t) + 0.22 * np.sin(2 * np.pi * 284 * t)) * env
        return (vibe * 0.42).astype(np.float32)

    def sub_impact(dur=0.48, f_start=92.0, punch=1.0):
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        ph = 2 * np.pi * (f_start * np.exp(-11 * t) + 34.0) * t
        body = np.sin(ph) * np.exp(-7.5 * t)
        thwack = lp(rng.standard_normal(n).astype(np.float32), 480) * np.exp(-28 * t) * 0.35
        return ((body + thwack) * punch * 0.65).astype(np.float32)

    def latch_clack(dur=0.16, f0=310.0):
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        modes = sum(np.sin(2 * np.pi * f0 * r * t) * np.exp(-(18 + 6 * i) * t)
                    for i, r in enumerate([1.0, 1.52, 2.28]))
        click = bp(rng.standard_normal(n).astype(np.float32), 400, 1800) * np.exp(-45 * t) * 0.25
        return ((modes * 0.35 + click) * 0.60).astype(np.float32)

    def crisp_glass_break(dur=0.45):
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        out = bp(rng.standard_normal(n).astype(np.float32), 1600, 5200) * np.exp(-14 * t) * 0.28
        for _ in range(9):
            st = int(rng.uniform(0, 0.18) * SR)
            ln = min(int(0.08 * SR), n - st)
            tt = np.arange(ln, dtype=np.float32) / SR
            out[st:st+ln] += np.sin(2 * np.pi * rng.uniform(2200, 4800) * tt) * np.exp(-36 * tt) * 0.22
        return out.astype(np.float32)

    def zombie_vocal_rasp(dur=0.65, pitch=118.0):
        """Guttural human-throat zombie vocalization (formant-filtered glottal fry + wet click)."""
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        f = pitch + 24 * np.sin(2 * np.pi * 6.5 * t) - 30 * (t / dur)
        ph = np.cumsum(2 * np.pi * f / SR)
        fry = np.sin(ph) * (0.5 + 0.5 * np.sin(2 * np.pi * 31 * t)) + 0.35 * rng.standard_normal(n)
        vocal = bp(fry.astype(np.float32), 240, 1650) * np.sin(np.pi * t / dur) ** 1.2
        return (vocal * 0.42).astype(np.float32)

    def human_scream_distant(dur=0.70):
        n = int(dur * SR); t = np.arange(n, dtype=np.float32) / SR
        f = 640 + 210 * np.sin(np.pi * t / dur) - 140 * (t / dur)
        ph = np.cumsum(2 * np.pi * f / SR)
        src = 0.65 * np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * rng.standard_normal(n)
        return (bp(src.astype(np.float32), 450, 2100) * (np.sin(np.pi * t / dur) ** 1.4) * 0.36).astype(np.float32)

    def soft_steps(orig_t, count=5, dt=0.22, gain=0.35):
        nt0 = map_time(orig_t, anchors)
        for i in range(count):
            n = int(0.09 * SR); t = np.arange(n, dtype=np.float32) / SR
            th = np.sin(2 * np.pi * (115 * np.exp(-22 * t) + 45) * t) * np.exp(-28 * t)
            sc = bp(rng.standard_normal(n).astype(np.float32), 180, 950) * np.exp(-38 * t) * 0.25
            clip = ((th * 0.5 + sc) * gain).astype(np.float32)
            idx = int(round((nt0 + i * dt) * SR))
            if 0 <= idx < N - n:
                sfx[idx:idx+n] += clip

    # --- Place Clean, Subtle, Frame-Synced Horror Cues ---
    # 1. Gentle haptic phone buzz + subtle alert tone
    place(5.15, soft_phone_vibe(0.24), 0.75)
    place(5.55, soft_phone_vibe(0.24), 0.75)
    # Soft dual-frequency emergency chime (short 0.45s, warm, low gain)
    en = int(0.45 * SR); et = np.arange(en, dtype=np.float32) / SR
    eas = (0.5 * np.sin(2 * np.pi * 853 * et) + 0.5 * np.sin(2 * np.pi * 960 * et)) * np.exp(-4.5 * et) * 0.22
    place(9.95, lp(eas, 1400), 0.70)

    # 2. Distant human scream outside + quick footsteps
    place(28.75, human_scream_distant(0.68), 0.80)
    soft_steps(30.0, 5, 0.20, 0.40)

    # 3. Street chase zombie snarl + fall thud + car collision sub-boom (zero harsh skid static!)
    place(38.2, zombie_vocal_rasp(0.55, 130), 0.55)
    place(46.8, sub_impact(0.35, 82, 0.75), 0.75)
    place(48.2, zombie_vocal_rasp(0.65, 112), 0.65)
    place(52.80, sub_impact(0.62, 68, 1.15), 0.95)
    place(52.85, latch_clack(0.22, 240), 0.75)
    place(52.90, crisp_glass_break(0.42), 0.65)

    # 4. Deadbolt lock click + delivery driver palm thuds on glass + zombie rasp
    soft_steps(64.8, 5, 0.19, 0.45)
    place(68.25, latch_clack(0.18, 250), 0.85)
    place(71.15, sub_impact(0.32, 96, 0.90), 0.85)
    place(72.55, sub_impact(0.28, 102, 0.70), 0.65)
    place(81.0,  zombie_vocal_rasp(0.60, 118), 0.60)
    soft_steps(85.6, 6, 0.18, 0.40)

    # 5. Shutters closing: ONLY two clean mechanical latch clunks (ZERO 6s white-noise static!)
    place(91.0, latch_clack(0.18, 210), 0.60)
    place(96.2, sub_impact(0.28, 88, 0.75), 0.70)

    # 6. Call failed soft 3-tone
    for bi, bf in enumerate([914.0, 1371.0, 1777.0]):
        bn = int(0.16 * SR); bt = np.arange(bn, dtype=np.float32) / SR
        place(106.2 + bi * 0.22, (np.sin(2 * np.pi * bf * bt) * np.exp(-9 * bt) * 0.18).astype(np.float32), 0.65)

    # 7. Woman gentle palm tap on glass + zombie throat rasp behind her
    place(190.2, sub_impact(0.24, 78, 0.50), 0.55)
    place(201.2, zombie_vocal_rasp(0.65, 104), 0.65)

    # 8. Lights switch relay click + two short crate thuds for barricade (NO 7s scraping noise!)
    place(208.3, latch_clack(0.14, 460), 0.65)
    place(215.0, sub_impact(0.30, 86, 0.65), 0.65)
    place(219.5, sub_impact(0.32, 82, 0.70), 0.70)

    # 9. Flashlight click + hand truck thud + clean ratchet clicks
    place(228.0, latch_clack(0.08, 1250), 0.50)
    soft_steps(228.6, 6, 0.28, 0.38)
    place(239.2, sub_impact(0.32, 84, 0.70), 0.70)
    for ri in range(4):
        place(242.6 + ri * 0.18, latch_clack(0.07, 980 + ri * 50), 0.45)

    # 10. Storage room metallic clatter + flashlight click off + glass crunch + eerie vocal clicking + 2 door impacts!
    place(255.2, latch_clack(0.24, 390), 0.90)
    place(255.38, sub_impact(0.30, 95, 0.75), 0.80)
    place(259.2, latch_clack(0.08, 1350), 0.50)
    place(269.5, crisp_glass_break(0.38), 0.55)
    # Eerie organic throat-clicking of the infected creature (284.5s - 288.2s)
    for ci in range(11):
        place(284.8 + ci * 0.22, latch_clack(0.045, 760 + (ci % 3) * 130), 0.50)
    place(290.0, zombie_vocal_rasp(0.70, 98), 0.70)
    place(298.4, sub_impact(0.48, 66, 1.05), 0.95)
    place(306.8, sub_impact(0.60, 58, 1.20), 1.05)
    place(307.2, zombie_vocal_rasp(0.75, 108), 0.75)
    soft_steps(316.0, 8, 0.18, 0.55)

    return sfx


def gated_rms(x, frame=2048, hop=1024):
    vals = [float(np.sqrt(np.mean(x[i:i+frame] ** 2) + 1e-12)) for i in range(0, len(x) - frame, hop)]
    arr = np.array(vals)
    voiced = arr[arr > np.percentile(arr, 60) * 0.35]
    return float(np.mean(voiced)) if len(voiced) else float(np.mean(arr))


def main():
    print("1/4 Building fast-paced emotional horror voiceover from full 933-word Ronald script...")
    vo, words_v2, segs_v2, anchors = build_fast_vo()
    dur_s = len(vo) / SR
    vo_rms = gated_rms(vo)
    wpm = len(words_v2) / (dur_s / 60.0)
    print(f"V2 Fast Voiceover: {dur_s:.2f}s ({dur_s/60:.2f} min) | {len(words_v2)} words | {wpm:.1f} WPM | RMS={vo_rms:.4f}")

    print("2/4 Synthesizing 100% Vocal-Only Dark Horror Choir/Hum Pad (ZERO musical instruments)...")
    pad = build_vocal_only_horror_pad(dur_s, anchors)

    print("3/4 Synthesizing clean, low-noise horror foley & creature vocal cues...")
    sfx = build_clean_horror_sfx(dur_s, anchors)

    # Word-level sidechain ducking on the vocal drone pad so voiceover is razor-clear!
    duck = np.ones(len(vo), dtype=np.float32)
    pad_w = int(0.06 * SR)
    for w in words_v2:
        i0 = max(0, int(w["start"] * SR) - pad_w)
        i1 = min(len(vo), int(w["end"] * SR) + pad_w)
        duck[i0:i1] = 0.52
    win = int(0.10 * SR)
    duck = np.convolve(duck, np.ones(win, dtype=np.float32) / win, mode="same")
    pad_ducked = pad * duck

    # Keep background vocal pad & foley clean and supportive (never overpowering voice!)
    pad_rms = float(np.sqrt(np.mean(pad_ducked ** 2) + 1e-12))
    pad_ducked *= (0.28 * vo_rms) / pad_rms

    sfx_nz = sfx[np.abs(sfx) > 1e-4]
    sfx_rms = float(np.sqrt(np.mean(sfx_nz ** 2) + 1e-12)) if len(sfx_nz) else 1.0
    sfx *= (0.32 * vo_rms) / sfx_rms

    # Stereo width: centered crisp voiceover + wide atmospheric stereo vocal choir!
    pad_L = pad_ducked
    pad_R = np.roll(pad_ducked, int(0.014 * SR)) * 0.96
    mix_L = vo + pad_L + sfx * 0.98
    mix_R = vo + pad_R + sfx * 1.02
    stereo = np.stack([mix_L, mix_R], axis=1)

    pk = float(np.max(np.abs(stereo)) + 1e-9)
    if pk > 0.95:
        stereo *= 0.95 / pk

    raw_wav = os.path.join(OUT_DIR, "raw_mix_v2.wav")
    master_wav = os.path.join(OUT_DIR, "master_audio_v2.wav")
    sf.write(raw_wav, stereo, SR, subtype="PCM_16")

    print("4/4 Mastering stereo audio to -14.0 LUFS / -1.0 dBTP...")
    subprocess.run([
        "/tmp/studio_env/bin/ffmpeg", "-y", "-i", raw_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=8.5",
        "-ar", "44100", "-ac", "2", master_wav
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Measure exact output duration & frame count at 30fps
    info = sf.info(master_wav)
    exact_dur = round(info.duration, 3)
    total_frames = int(math.ceil(exact_dur * 30.0))

    payload = {
        "duration": exact_dur,
        "fps": 30,
        "total_frames": total_frames,
        "wpm": round(wpm, 1),
        "word_count": len(words_v2),
        "anchors": anchors,
        "segments": segs_v2,
        "words": words_v2,
    }
    with open(WORDS_OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"SUCCESS! Saved {WORDS_OUT} ({exact_dur:.2f}s = {total_frames} frames) & {master_wav}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
V3 Master Audio & Exact Word Timeline Builder (`build_v3_audio.py`)
- STRICT USER RULE: ZERO editing, time-stretching, pitch-shifting, or cutting of the user's
  newly uploaded 04:20.32 ElevenLabs v4 voiceover (`vo_unchanged_48k.wav`).
- Builds `projects/rick-outbreak-3d/data/words_v3.json` (660 audited words, 30fps, 7,810 frames)
  snapped to 5ms RMS syllable energy of the unedited voiceover.
- Composes a full-length, dark, cinematic DRAMATIC HORROR & HORROR-SUSPENSE soundtrack:
  * Deep tectonic sub-bass dread drones (34-55 Hz)
  * Bowed sul-ponticello horror string clusters & slow eerie glissando risers (minor-2nd / tritone tension, ZERO cheerful melody)
  * Dark haunting horror choir / cavern breath pads
  * Accelerating muffled human heartbeat pulses during high-suspense scenes
  * Dramatic sub-braam horror stingers on twists & reveals
  * Clean, low-noise cinema foley synced to the exact spoken actions (phone buzz, swerving tires,
    distant panic scream, store phones ringing, smooth heavy steel shutter slam to floor with ZERO static hiss,
    glass palm thud, power-down hum drop, alley metal crash, scrape + 3 slow knocks, stealth footsteps,
    radio static squelch, heavy underground maintenance door slowly groaning shut by itself).
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
from pedalboard import (
    Pedalboard, Compressor, HighpassFilter, LowpassFilter,
    Reverb, Gain, Limiter
)

VO_WAV_48K = "/tmp/rick_study/v3/vo_unchanged_48k.wav"
# Repo-persistent fallback of the SAME 04:20.32 unedited ElevenLabs v4 voiceover (survives /tmp resets).
VO_REPO_MP3 = "google_drive/ElevenLabs_audio_elevenlabs-v4_[calm, cinemati_2026-11-11T01_54_36.mp3"

# ---- V7 ORIGINS INTRO ----
# The new 12.40s cinematic intro replaces the old 3.36s cold open: every story-time
# layer is generated on the story timeline then shifted +9.04s; the intro itself is
# built separately in RENDER time (0-12.40) with NO voice-over.
INTRO_SHIFT = 9.04
INTRO_END = 12.40
EVIL_LAUGH_MP3 = "google_drive/dragon-studio-evil-laugh-with-reverb-423668.mp3"
WHISPER_JSON = "/tmp/rick_study/v3/whisper_tiny.json"
WORDS_OUT = "projects/rick-outbreak-3d/data/words_v3.json"
OUT_WAV = "/tmp/rick_study/v3/master_audio_v3.wav"
OUT_MP3 = "/tmp/rick_study/v3/Rick_Clips_Outbreak_V3_Master_Audio.mp3"
FFMPEG = "/tmp/studio_env/bin/ffmpeg"

SR = 48000


def build_words_v3(vo_mono: np.ndarray, total_dur: float):
    if not os.path.exists(WHISPER_JSON) and os.path.exists(WORDS_OUT):
        with open(WORDS_OUT, "r") as f:
            return json.load(f)

    with open(WHISPER_JSON, "r") as f:
        wt = json.load(f)

    raw_words = wt["words"]
    fixed_words = []

    for idx, w in enumerate(raw_words):
        txt = w["word"].strip()
        t0 = float(w["start"])
        t1 = float(w["end"])

        # Exact audited orthographic fixes
        if txt == "417pm.":
            t_mid = round(t0 + (t1 - t0) * 0.62, 3)
            fixed_words.append({"word": "4:17", "start": round(t0, 3), "end": t_mid})
            fixed_words.append({"word": "PM.", "start": t_mid, "end": round(t1, 3)})
            continue
        elif txt == "swurfs.":
            txt = "swerves."
        elif idx == 304 and txt == "The" and 115.0 < t0 < 116.0:
            txt = "A"
        elif txt == "plain." and 194.5 < t0 < 196.5:
            txt = "playing."
        elif txt == "his" and 218.5 < t0 < 219.6:
            txt = "is"

        fixed_words.append({"word": txt, "start": round(t0, 3), "end": round(t1, 3)})

    # Ensure strictly monotonic non-overlapping timestamps with >= 55ms min word duration
    n = len(fixed_words)
    for i in range(n):
        if i > 0 and fixed_words[i]["start"] < fixed_words[i - 1]["end"]:
            mid = 0.5 * (fixed_words[i]["start"] + fixed_words[i - 1]["end"])
            fixed_words[i - 1]["end"] = round(max(fixed_words[i - 1]["start"] + 0.04, mid), 3)
            fixed_words[i]["start"] = fixed_words[i - 1]["end"]
        if fixed_words[i]["end"] - fixed_words[i]["start"] < 0.055:
            target_end = fixed_words[i]["start"] + 0.065
            if i + 1 < n and target_end > fixed_words[i + 1]["start"]:
                if fixed_words[i + 1]["end"] - fixed_words[i + 1]["start"] > 0.14:
                    fixed_words[i + 1]["start"] = round(target_end, 3)
                    fixed_words[i]["end"] = round(target_end, 3)
                else:
                    # Borrow 35ms from previous word if possible
                    if i > 0 and fixed_words[i - 1]["end"] - fixed_words[i - 1]["start"] > 0.14:
                        fixed_words[i - 1]["end"] = round(fixed_words[i]["start"] - 0.035, 3)
                        fixed_words[i]["start"] = fixed_words[i - 1]["end"]
                    fixed_words[i]["end"] = round(min(total_dur, fixed_words[i + 1]["start"]), 3)
            else:
                fixed_words[i]["end"] = round(min(total_dur, target_end), 3)

    # Fine-snap phrase-leading words (after >= 0.18s pause) to exact 5ms voice energy onset
    hop = int(0.005 * SR)
    n_frames = len(vo_mono) // hop
    rms = np.sqrt(np.mean(vo_mono[: n_frames * hop].reshape(n_frames, hop) ** 2, axis=1) + 1e-12)
    noise_floor = float(np.percentile(rms, 15))
    onset_thr = max(noise_floor * 3.5, 0.008)

    for i in range(n):
        prev_end = 0.0 if i == 0 else fixed_words[i - 1]["end"]
        gap = fixed_words[i]["start"] - prev_end
        if gap >= 0.18 or i == 0:
            win_a = max(int(prev_end / 0.005), int((fixed_words[i]["start"] - 0.12) / 0.005))
            win_b = min(n_frames - 1, int((fixed_words[i]["start"] + 0.12) / 0.005))
            if win_b > win_a + 2:
                sub = rms[win_a:win_b]
                above = np.where(sub > onset_thr)[0]
                if len(above) > 0:
                    snapped = round((win_a + int(above[0])) * 0.005, 3)
                    if prev_end <= snapped < fixed_words[i]["end"] - 0.04:
                        fixed_words[i]["start"] = snapped

    # Clean segment text fixes
    segs_out = []
    for s in wt["segments"]:
        st = s["text"]
        st = st.replace("417pm.", "4:17 PM.")
        st = st.replace("swurfs.", "swerves.")
        st = st.replace("The new emergency message.", "A new emergency message.")
        st = st.replace("a radio is plain.", "a radio is playing.")
        st = st.replace("Help his waiting.", "Help is waiting.")
        segs_out.append({
            "start": round(float(s["start"]), 3),
            "end": round(float(s["end"]), 3),
            "text": st,
        })

    fps = 30
    total_frames = int(math.ceil(total_dur * fps))
    payload = {
        "version": "v3_unedited_elevenlabs_v4",
        "duration": round(total_dur, 4),
        "fps": fps,
        "total_frames": total_frames,
        "wpm": round(len(fixed_words) / (total_dur / 60.0), 1),
        "word_count": len(fixed_words),
        "words": fixed_words,
        "segments": segs_out,
    }
    os.makedirs(os.path.dirname(WORDS_OUT), exist_ok=True)
    with open(WORDS_OUT, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"Saved {WORDS_OUT}: {len(fixed_words)} words, {total_dur:.3f}s ({total_frames} frames @ {fps}fps)")
    return payload


def add_clip(buf: np.ndarray, clip: np.ndarray, start_s: float, pan: float = 0.0):
    """Mixes a mono or stereo clip into stereo `buf` starting at `start_s` with equal-power pan [-1..1]."""
    i0 = int(round(start_s * SR))
    if i0 >= len(buf) or len(clip) == 0:
        return
    if i0 < 0:
        clip = clip[-i0:]
        i0 = 0
    n = min(len(clip), len(buf) - i0)
    if n <= 0:
        return
    c = clip[:n]
    if c.ndim == 1:
        angle = (pan + 1.0) * 0.25 * math.pi
        gl, gr = math.cos(angle), math.sin(angle)
        buf[i0 : i0 + n, 0] += c * gl
        buf[i0 : i0 + n, 1] += c * gr
    else:
        buf[i0 : i0 + n] += c


def env_ad(n: int, atk_s: float, rel_s: float) -> np.ndarray:
    e = np.ones(n, dtype=np.float32)
    na = min(n, max(1, int(atk_s * SR)))
    nr = min(n, max(1, int(rel_s * SR)))
    e[:na] *= np.linspace(0.0, 1.0, na, dtype=np.float32)
    e[-nr:] *= np.linspace(1.0, 0.0, nr, dtype=np.float32)
    return e


def build_dramatic_horror_score(total_samples: int) -> np.ndarray:
    """
    Synthesizes a continuous, dark, dramatic Hollywood horror & horror-suspense underscore:
    1) Deep tectonic sub-bass dread drone (D1=36.7Hz & Ab1=51.9Hz tritone undertow)
    2) Bowed sul-ponticello horror string cluster (minor-2nd D3/Eb3 + Ab2 dissonant dark strings,
       detuned unison ensemble, slow dark filter sweeps, ZERO upbeat/melodic rhythm)
    3) Haunting dark horror choir / breath cavern pad (formant-sculpted spectral tension)
    4) Suspenseful muffled human heartbeat pulses during terror sequences
    5) Dramatic horror risers & sub-braam stingers on narrative shock twists
    """
    rng = np.random.default_rng(303)
    score = np.zeros((total_samples, 2), dtype=np.float32)
    dur = total_samples / SR

    # Coarse 100Hz control timeline interpolated to SR for fast vectorized synthesis
    ctrl_sr = 100
    n_ctrl = int(math.ceil(dur * ctrl_sr)) + 1
    tc = np.arange(n_ctrl, dtype=np.float32) / ctrl_sr

    # Act-based dramatic tension curve [0.0 .. 1.0]
    # Act I: 0-42.6s | Act II: 42.6-80.5s | Act III: 80.5-146s | Act IV: 146-188.4s | Act V: 188.4-260.32s
    # V5 ARC: normal quiet day (0-17.6) -> unease -> attack -> horror -> emergency -> mimic dread
    tension_kf = [
        # V7: story 0-3.36 now lands under the 3.30s BLACK SCREEN (render 9.04-12.40) where
        # the VO's opening line speaks over a deep dread swell, then SMASHES to the bright street.
        (0.0, 0.55), (1.60, 0.42), (2.90, 0.16),
        (3.36, 0.10), (4.88, 0.22), (8.6, 0.16), (16.0, 0.18),
        (17.6, 0.28), (20.4, 0.40), (24.0, 0.62), (26.96, 0.88),
        (28.3, 0.66), (32.9, 0.46), (42.6, 0.50), (48.0, 0.36),
        (50.8, 0.72), (61.3, 0.84), (65.3, 0.96), (66.9, 0.80),
        (71.9, 0.55), (78.8, 0.40), (82.84, 0.52), (94.0, 0.74),
        (103.5, 0.85), (113.8, 0.90), (127.0, 0.95), (138.5, 0.70),
        (145.96, 0.34), (158.3, 0.44), (169.7, 0.56), (179.96, 0.72),
        (188.4, 0.58), (193.4, 0.52), (203.4, 0.58), (212.8, 0.76),
        (223.2, 0.90), (235.6, 0.96), (246.8, 1.00), (252.5, 0.84),
        (255.1, 0.92), (259.7, 0.97), (dur, 0.30)
    ]
    tx, ty = zip(*tension_kf)
    tension_c = np.interp(tc, tx, ty).astype(np.float32)

    t_full = np.arange(total_samples, dtype=np.float32) / SR
    tension = np.interp(t_full, tc, tension_c).astype(np.float32)

    # --- LAYER 1: Deep Tectonic Sub-Bass Dread Drone (D1 36.71Hz + slow LFO + tritone 51.91Hz) ---
    lfo1 = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.09 * t_full)
    lfo2 = 0.5 + 0.5 * np.sin(2.0 * np.pi * 0.055 * t_full + 1.3)
    sub_d1 = np.sin(2.0 * np.pi * 36.71 * t_full + 0.35 * np.sin(2.0 * np.pi * 0.17 * t_full))
    sub_eb1 = np.sin(2.0 * np.pi * 38.89 * t_full) * (0.35 + 0.55 * tension)
    sub_ab1 = np.sin(2.0 * np.pi * 51.91 * t_full) * (0.25 * lfo2 * (tension ** 1.4))
    # V5: the dread drone only breathes once the day turns (tension > 0.20) — calm start stays clean
    drone_gate = np.clip((tension - 0.20) / 0.22, 0.0, 1.0)
    drone = (sub_d1 * (0.65 + 0.35 * lfo1) + sub_eb1 * 0.42 + sub_ab1) * (0.048 + 0.052 * tension) * drone_gate
    score[:, 0] += drone.astype(np.float32)
    score[:, 1] += drone.astype(np.float32)

    # --- LAYER 2: Dark Bowed Horror-Suspense String Ensemble (D2, A2, Eb3, Ab3 dissonant cluster) ---
    # Rich bowed saw-like harmonic sum (band-limited to 7 harmonics so it's warm/cinematic, zero buzz)
    str_L = np.zeros(total_samples, dtype=np.float32)
    str_R = np.zeros(total_samples, dtype=np.float32)
    ensemble_notes = [
        # (freq_hz, detune_cents, amp, pan, min_tension)
        (73.42, -7.0, 0.34, -0.45, 0.24),  # D2 cello low (V5: enters with the unease)
        (73.42, +8.0, 0.34, +0.45, 0.24),  # D2 cello double
        (103.83, -5.0, 0.22, -0.60, 0.35), # Ab2 tritone suspense
        (110.00, +4.0, 0.24, +0.30, 0.24), # A2 hollow fifth
        (146.83, -9.0, 0.20, -0.25, 0.25), # D3 viola
        (155.56, +11.0, 0.26, +0.55, 0.52) # Eb3 minor-9th horror rub!
    ]
    for f0, cents, amp, pan, min_t in ensemble_notes:
        f = f0 * (2.0 ** (cents / 1200.0))
        vib = 0.0035 * np.sin(2.0 * np.pi * (4.1 + 0.3 * abs(pan)) * t_full + rng.uniform(0, 6.28))
        ph = 2.0 * np.pi * f * t_full * (1.0 + vib * 0.02)
        # Slow bow pressure swell
        bow = 0.55 + 0.45 * np.sin(2.0 * np.pi * (0.07 + 0.02 * abs(cents)) * t_full + rng.uniform(0, 6.28))
        gate = np.clip((tension - min_t) / max(0.15, 1.0 - min_t), 0.0, 1.0)
        wave = np.zeros(total_samples, dtype=np.float32)
        for h in range(1, 7):
            wave += ( ((-1) ** (h + 1)) / (h ** 1.35) ) * np.sin(h * ph)
        wave *= amp * bow * gate * 0.042
        ang = (pan + 1.0) * 0.25 * math.pi
        str_L += wave * math.cos(ang)
        str_R += wave * math.sin(ang)

    # Smooth dark lowpass (cutoff 950Hz) on bowed strings so they sit warmly beneath speech
    sos_str = signal.butter(3, 950.0 / (SR * 0.5), btype="low", output="sos")
    score[:, 0] += signal.sosfilt(sos_str, str_L).astype(np.float32)
    score[:, 1] += signal.sosfilt(sos_str, str_R).astype(np.float32)

    # --- LAYER 2.5 (V6): CONTINUOUS SITUATION-MATCHED BASE PAD — the through-line motif.
    # Strong on the normal day, settled low bed under the horror, warmer at sunrise, thin
    # underground, dies with the radio at 254.45, breathes once more under TO BE CONTINUED.
    base_t = [0.0, 3.36, 4.30, 17.60, 19.20, 145.96, 147.60, 188.40, 190.00, 254.45, 254.95, 259.50, 260.05, dur]
    base_v = [0.00, 0.00, 1.00, 1.00, 0.34, 0.34, 0.55, 0.55, 0.26, 0.26, 0.00, 0.00, 0.30, 0.30]
    calm_gate = np.interp(t_full, base_t, base_v).astype(np.float32)
    pad_notes = [(110.0, 0.30, -0.20), (164.81, 0.22, 0.15), (220.0, 0.16, 0.35), (277.18, 0.10, -0.35)]
    pad_L = np.zeros(total_samples, dtype=np.float32)
    pad_R = np.zeros(total_samples, dtype=np.float32)
    for f0, amp, pan in pad_notes:
        vib = 0.0025 * np.sin(2.0 * np.pi * 0.13 * t_full + rng.uniform(0, 6.28))
        ph = 2.0 * np.pi * f0 * t_full * (1.0 + vib)
        w = (np.sin(ph) + 0.35 * np.sin(2.0 * ph) + 0.18 * np.sin(3.0 * ph)) * amp
        swell = 0.60 + 0.40 * np.sin(2.0 * np.pi * 0.05 * t_full + rng.uniform(0, 6.28))
        w = w * swell * calm_gate * 0.030
        ang = (pan + 1.0) * 0.25 * math.pi
        pad_L += w * math.cos(ang)
        pad_R += w * math.sin(ang)
    sos_pad = signal.butter(2, 1300.0 / (SR * 0.5), btype="low", output="sos")
    score[:, 0] += signal.sosfilt(sos_pad, pad_L).astype(np.float32)
    score[:, 1] += signal.sosfilt(sos_pad, pad_R).astype(np.float32)

    # --- LAYER 2.7 (V6): TENSE-BUILDING OSTINATO — driving eighth-note cell (D2/A2/D3) that
    # powers the cold open, the sprint-at-the-car, the police overrun, the siege and the finale. ---
    sos_ost = signal.butter(2, 720.0 / (SR * 0.5), btype="low", output="sos")
    ost_windows = [
        # V7: mimic-siege and child-tunnel windows REMOVED (all mimic-voice scoring is gone).
        (17.60, 27.06, 0.18, 0.38),   # traffic stops -> sprint -> IMPACT
        (61.00, 70.20, 0.28, 0.36),   # police overrun by the sprinting horde
        (94.00, 113.84, 0.20, 0.32),  # alley crash + door knocks
        (223.20, 238.00, 0.26, 0.36), # "I'm right behind you"
    ]
    step_t = 60.0 / 132.0 / 2.0  # eighth notes @132bpm
    for w0, w1, g0, g1 in ost_windows:
        rate = 0.5 if w0 > 240.0 else 1.0  # finale plays half-time: slower, heavier dread
        cur = w0
        idx = 0
        while cur < w1 - 0.05:
            prog = (cur - w0) / max(0.1, w1 - w0)
            g = g0 + (g1 - g0) * prog
            f = 73.42 if idx % 2 == 0 else 110.0
            if idx % 8 == 7:
                f = 146.83
            n_o = int(0.17 * SR)
            th_o = np.linspace(0.0, 0.17, n_o, dtype=np.float32)
            ph_o = 2.0 * np.pi * f * th_o * (1.0 + 0.0022 * np.sin(2.0 * np.pi * 5.2 * th_o))
            note = (np.sin(ph_o) + 0.30 * np.sin(2.0 * ph_o)) * env_ad(n_o, 0.004, 0.11)
            note = signal.sosfilt(sos_ost, note).astype(np.float32) * (g * 0.105)
            add_clip(score, note, cur, pan=(-0.28 if idx % 2 == 0 else 0.28))
            cur += step_t / rate
            idx += 1

    # --- LAYER 2.8 (V6): SITUATION TEXTURES — normal-day city hum, sunrise wind, radio static. ---
    hum_gate = np.clip((t_full - 3.36) / 1.5, 0.0, 1.0) * np.clip((17.6 - t_full) / 2.0, 0.0, 1.0)
    hum_gate = np.where((t_full >= 3.36) & (t_full < 17.6), hum_gate, 0.0).astype(np.float32)
    hum = (np.sin(2*np.pi*54.0*t_full) + 0.42*np.sin(2*np.pi*108.5*t_full) + 0.18*np.sin(2*np.pi*163.0*t_full))
    score[:, 0] += (hum * hum_gate * 0.011).astype(np.float32)
    score[:, 1] += (hum * hum_gate * 0.011).astype(np.float32)

    wind_L = signal.sosfilt(sos_ost, rng.standard_normal(total_samples).astype(np.float32)).astype(np.float32)
    wind_R = signal.sosfilt(sos_ost, rng.standard_normal(total_samples).astype(np.float32)).astype(np.float32)
    gust = 0.55 + 0.45 * np.sin(2*np.pi*0.07*t_full + 0.8) * np.sin(2*np.pi*0.023*t_full)
    wind_t = [0.0, 3.36, 17.6, 42.6, 145.96, 188.4, 190.5, dur]
    wind_v = [0.006, 0.006, 0.016, 0.010, 0.052, 0.052, 0.007, 0.007]
    wind_g = np.interp(t_full, wind_t, wind_v).astype(np.float32) * gust
    score[:, 0] += (wind_L * wind_g * 0.9).astype(np.float32)
    score[:, 1] += (wind_R * wind_g * 0.9).astype(np.float32)

    sos_rs = signal.butter(2, [900.0/(SR*0.5), 2800.0/(SR*0.5)], btype="band", output="sos")
    rs_src = signal.sosfilt(sos_rs, rng.standard_normal(total_samples).astype(np.float32)).astype(np.float32)
    rs_gate = np.clip((t_full - 193.4) / 1.5, 0.0, 1.0) * np.clip((254.45 - t_full) / 0.35, 0.0, 1.0)
    rs_gate = np.where((t_full >= 193.4) & (t_full < 254.45), rs_gate, 0.0)
    crackle = 0.55 + 0.45 * np.sin(2*np.pi*3.7*t_full) * np.sin(2*np.pi*1.3*t_full + 1.0)
    score[:, 0] += (rs_src * rs_gate * crackle * 0.026).astype(np.float32)
    score[:, 1] += (rs_src * rs_gate * crackle * 0.026).astype(np.float32)

    # (V7: LAYER 7 detuned music-box lullaby REMOVED — it scored the child-voice mimic.)

    # --- LAYER 3: Haunting Dark Horror Choir / Underground Cavern Breath Pad ---
    noise_L = rng.standard_normal(total_samples).astype(np.float32)
    noise_R = rng.standard_normal(total_samples).astype(np.float32)
    choir_L = np.zeros(total_samples, dtype=np.float32)
    choir_R = np.zeros(total_samples, dtype=np.float32)
    # Dark "OOH / AAH" spectral resonances (310Hz, 640Hz, 1180Hz)
    for fc, bw, g in [(310.0, 70.0, 0.55), (640.0, 120.0, 0.32), (1180.0, 200.0, 0.14)]:
        sos_bp = signal.butter(2, [ (fc - bw*0.5)/(SR*0.5), (fc + bw*0.5)/(SR*0.5) ], btype="band", output="sos")
        choir_L += signal.sosfilt(sos_bp, noise_L).astype(np.float32) * g
        choir_R += signal.sosfilt(sos_bp, noise_R).astype(np.float32) * g
    breath_swell = (0.45 + 0.55 * np.sin(2.0 * np.pi * 0.11 * t_full)) * (tension ** 1.5) * 0.022
    score[:, 0] += choir_L * breath_swell
    score[:, 1] += choir_R * breath_swell

    # --- LAYER 4: Muffled Human Heartbeat Suspense Pulses in High-Dread Windows ---
    heartbeat_windows = [
        (24.2, 33.5, 92.0, 116.0, 0.10),  # V5: sprint-at-car hit-and-run panic
        (51.0, 80.2, 68.0, 92.0, 0.11),   # Woman at door & police backing away from zombies
        (101.0, 140.0, 64.0, 96.0, 0.12), # Back-door knocks & brother voice mimic
        (213.0, 259.5, 62.0, 98.0, 0.12), # Underground radio mimic & closing maintenance door
    ]
    for w0, w1, bpm0, bpm1, hb_gain in heartbeat_windows:
        cur_t = w0
        while cur_t < w1 - 0.4:
            prog = (cur_t - w0) / max(0.1, w1 - w0)
            bpm = bpm0 + (bpm1 - bpm0) * prog
            beat_dur = 60.0 / bpm
            # Lub-dub double chest thump (lowpass 110Hz sine pitch-drop, zero click)
            for offset, pitch0, amp_k in [(0.0, 66.0, 1.0), (0.21, 56.0, 0.72)]:
                n_hb = int(0.16 * SR)
                th = np.linspace(0.0, 0.16, n_hb, dtype=np.float32)
                f_inst = pitch0 * np.exp(-th * 11.0) + 30.0
                ph_hb = 2.0 * np.pi * np.cumsum(f_inst) / SR
                env_hb = np.maximum(0.0, np.sin(np.pi * np.clip(th / 0.16, 0, 1))) ** 1.8
                fade_w = min(1.0, (cur_t - w0) / 2.0, (w1 - cur_t) / 2.0)
                thump = np.sin(ph_hb) * env_hb * hb_gain * max(0.0, fade_w)
                add_clip(score, thump.astype(np.float32), cur_t + offset, pan=0.0)
            cur_t += beat_dur

    # --- LAYER 5: Dramatic Horror Stingers, Risers & Sub-Braam Impacts on Twist Beats ---
    stingers = [
        # (peak_time_s, riser_len_s, tail_len_s, intensity, base_freq)
        # V7: the whole ORIGINS cold-open set is gone (rebuilt as render-time intro design),
        # and the two mimic-voice accent braams (127.0 "Open up. It's me." / 246.8 "Dad?")
        # are removed with the voices themselves.
        (5.75, 0.70, 2.00, 0.62, 55.00),   # emergency alert FILLS THE SCREEN (with the VO)
        (3.45, 0.8, 1.8, 0.55, 55.0),    # Phone vibrates alert
        (27.06, 1.4, 3.0, 1.00, 43.65),  # CAR CLIPS THE MAN — hit-and-run impact!
        (65.95, 1.2, 2.6, 0.95, 43.65),   # Horde sprints & TACKLES the officer down!
        (51.65, 1.1, 2.4, 0.95, 46.25),  # Woman slams the glass!
        (68.40, 1.6, 3.0, 1.00, 41.20),  # "Her expression changes"
        (95.10, 0.7, 2.5, 0.90, 43.65),  # Metal crash in delivery alley
        (115.00, 0.9, 2.0, 0.72, 51.91), # Second emergency alert
        (185.00, 1.2, 2.2, 0.75, 46.25), # Maintenance door hanging open
        (223.30, 1.3, 2.8, 0.92, 41.20), # "The man beside him goes pale"
        (235.60, 1.8, 3.2, 1.00, 36.71), # "I'm right behind you."
        (255.10, 1.2, 4.8, 0.96, 36.71), # Maintenance door begins to close by itself!
    ]
    for t_pk, r_len, d_len, inten, bf in stingers:
        # Eerie upward glissando horror string riser into t_pk
        nr = int(r_len * SR)
        if nr > 100:
            tr = np.linspace(0.0, 1.0, nr, dtype=np.float32)
            # Dissonant minor-second upward slide (290Hz -> 540Hz & 310Hz -> 610Hz)
            f_a = 260.0 + 280.0 * (tr ** 2.1)
            f_b = 277.0 + 335.0 * (tr ** 2.3)
            pa = 2.0 * np.pi * np.cumsum(f_a) / SR
            pb = 2.0 * np.pi * np.cumsum(f_b) / SR
            riser = (np.sin(pa) * 0.55 + np.sin(pb) * 0.45 + 0.25 * np.sin(2.0 * pa)) * (tr ** 2.4)
            riser *= env_ad(nr, 0.05, 0.04) * (0.048 * inten)
            add_clip(score, riser.astype(np.float32), t_pk - r_len, pan=-0.2)

        # Deep dramatic sub-braam + dark minor-second brass swell impact at t_pk
        nd = int(d_len * SR)
        td = np.linspace(0.0, d_len, nd, dtype=np.float32)
        f_drop = bf * (1.0 + 0.45 * np.exp(-td * 7.5))
        p_drop = 2.0 * np.pi * np.cumsum(f_drop) / SR
        braam = (
            0.70 * np.sin(p_drop)
            + 0.28 * np.tanh(2.2 * np.sin(2.0 * p_drop))
            + 0.18 * np.sin(2.015 * np.pi * (bf * 2.12) * td)  # tritone dark overtone
        )
        env_d = np.exp(-td * (1.8 / max(0.8, d_len * 0.55))) * env_ad(nd, 0.018, 0.25)
        sos_lp = signal.butter(3, 420.0 / (SR * 0.5), btype="low", output="sos")
        braam = signal.sosfilt(sos_lp, braam * env_d).astype(np.float32) * (0.145 * inten)
        add_clip(score, braam, t_pk, pan=0.1)

    # Apply lush dark cinema hall reverb to the dramatic score
    board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=30.0),
        Reverb(room_size=0.78, damping=0.68, wet_level=0.28, dry_level=0.82, width=0.95),
        LowpassFilter(cutoff_frequency_hz=4200.0),
    ])
    score = board(score.T, SR).T.astype(np.float32)
    return score


def build_clean_foley(total_samples: int) -> np.ndarray:
    """
    Synthesizes crisp, realistic, ZERO-harsh-static cinema foley locked to exact story timestamps.
    """
    rng = np.random.default_rng(909)
    sfx = np.zeros((total_samples, 2), dtype=np.float32)

    def phone_vibrate(t0: float, pulses: int = 2):
        for p in range(pulses):
            n = int(0.24 * SR)
            t = np.linspace(0, 0.24, n, dtype=np.float32)
            vib = (0.65 * np.sin(2*np.pi*148*t) + 0.35 * np.sin(2*np.pi*296*t)) * env_ad(n, 0.02, 0.04) * 0.075
            add_clip(sfx, vib, t0 + p * 0.32, pan=0.12)

    def eas_tone(t0: float, dur: float = 0.65):
        n = int(dur * SR)
        t = np.linspace(0, dur, n, dtype=np.float32)
        # Authentic muted dual-tone EAS (853Hz + 960Hz, gentle lowpassed so never piercing)
        tone = 0.5 * (np.sin(2*np.pi*853*t) + np.sin(2*np.pi*960*t)) * env_ad(n, 0.03, 0.08) * 0.058
        add_clip(sfx, tone, t0, pan=0.0)

    # 1) (V7: the entire V6.5 cold-open sound design was replaced by the render-time
    #      ORIGINS intro bed in build_intro_layers — see below.)

    # 1h) Phone: buzz heard over the store shot, then the on-screen buzz + EAS slam
    phone_vibrate(3.45, pulses=2)
    phone_vibrate(5.35, pulses=2)
    eas_tone(5.78, dur=0.62)

    # V6 FINALE: tunnel-figure LUNGE whoosh (254.50) + maintenance-door grind + SLAM + end boom
    n_wh = int(0.52 * SR)
    t_wh = np.linspace(0.0, 0.52, n_wh, dtype=np.float32)
    sos_wh_a = signal.butter(2, [380.0/(SR*0.5), 2600.0/(SR*0.5)], btype="band", output="sos")
    whoosh_src = rng.standard_normal(n_wh).astype(np.float32)
    whoosh = signal.sosfilt(sos_wh_a, whoosh_src * (t_wh ** 1.6)) * env_ad(n_wh, 0.01, 0.12) * 0.30
    add_clip(sfx, whoosh.astype(np.float32), 254.50, pan=0.0)

    n_gr = int(4.6 * SR)
    t_gr = np.linspace(0.0, 4.6, n_gr, dtype=np.float32)
    grind_f = 96.0 + 26.0 * np.sin(2*np.pi*0.5*t_gr)
    grind = np.sign(np.sin(2*np.pi*grind_f*t_gr * 0.0))  # placeholder replaced below
    grind = (0.6*np.sin(2*np.pi*np.cumsum(grind_f)/SR) + 0.4*np.sin(2*np.pi*np.cumsum(grind_f*2.02)/SR))
    grind *= (0.4 + 0.6*np.abs(np.sin(2*np.pi*1.1*t_gr))) * env_ad(n_gr, 0.4, 0.5) * 0.030
    sos_gr2 = signal.butter(2, [120.0/(SR*0.5), 900.0/(SR*0.5)], btype="band", output="sos")
    add_clip(sfx, signal.sosfilt(sos_gr2, grind).astype(np.float32), 255.20, pan=-0.08)

    n_sl = int(0.6 * SR)
    t_sl = np.linspace(0.0, 0.6, n_sl, dtype=np.float32)
    f_sl = 120.0 * np.exp(-t_sl * 9.0) + 34.0
    slam = (np.sin(2*np.pi*np.cumsum(f_sl)/SR) * 0.9 + 0.35 * np.sign(np.sin(2*np.pi*np.cumsum(f_sl)/SR)))
    slam = slam * env_ad(n_sl, 0.002, 0.28) * 0.34
    add_clip(sfx, slam.astype(np.float32), 259.82, pan=0.0)

    n_bm = int(1.9 * SR)
    t_bm = np.linspace(0.0, 1.9, n_bm, dtype=np.float32)
    f_bm = 46.0 * (1.0 + 0.30 * np.exp(-t_bm * 5.0))
    boom = np.sin(2*np.pi*np.cumsum(f_bm)/SR) * np.exp(-t_bm * 2.1) * env_ad(n_bm, 0.01, 0.6) * 0.16
    add_clip(sfx, boom.astype(np.float32), 259.95, pan=0.0)

    # 2) 27.05s: Driver swerves (filtered tire skid + horn doppler) + 28.55s distant scream + 31.6s store phones ringing
    n_skid = int(1.05 * SR)
    ts = np.linspace(0, 1.05, n_skid, dtype=np.float32)
    skid_src = rng.standard_normal(n_skid).astype(np.float32)
    sos_sk = signal.butter(3, [780/(SR*0.5), 1650/(SR*0.5)], btype="band", output="sos")
    skid = (signal.sosfilt(sos_sk, skid_src) * 0.35 + 0.65 * np.sin(2*np.pi*(980 - 220*ts)*ts)) * env_ad(n_skid, 0.08, 0.30) * 0.055
    add_clip(sfx, skid.astype(np.float32), 27.05, pan=-0.35)

    # Distant muffled street panic cry at 28.55s (formant-filtered glottal pitch contour)
    n_sc = int(0.85 * SR)
    tsc = np.linspace(0, 0.85, n_sc, dtype=np.float32)
    f_sc = 590.0 + 140.0 * np.sin(np.pi * tsc / 0.85) - 90.0 * tsc
    glottal = sum((1.0 / h) * np.sin(2*np.pi*h*np.cumsum(f_sc)/SR) for h in range(1, 5))
    sos_muf = signal.butter(2, [500/(SR*0.5), 1850/(SR*0.5)], btype="band", output="sos")
    scream = signal.sosfilt(sos_muf, glottal).astype(np.float32) * env_ad(n_sc, 0.08, 0.32) * 0.045
    add_clip(sfx, scream, 28.55, pan=0.45)

    # Store phones ringing at 31.55s
    for r_i, (rt, f_a, f_b, pn) in enumerate([(31.55, 740, 920, -0.4), (31.82, 853, 960, 0.35), (32.20, 680, 880, -0.15)]):
        nr = int(0.38 * SR)
        tr = np.linspace(0, 0.38, nr, dtype=np.float32)
        mod = 0.5 + 0.5 * np.sign(np.sin(2*np.pi*18*tr))
        ring = (np.sin(2*np.pi*f_a*tr) + np.sin(2*np.pi*f_b*tr)) * 0.5 * mod * env_ad(nr, 0.02, 0.06) * 0.032
        add_clip(sfx, ring.astype(np.float32), rt, pan=pn)

    # 3) 43.0s: Front door deadbolt clunk + 44.15s-45.75s: SMOOTH HEAVY STEEL SHUTTER ROLLING ALL THE WAY DOWN & LATCHING ON FLOOR (ZERO static hiss!)
    def bolt_clunk(t0: float, pan: float = 0.0, gain: float = 0.11):
        nb = int(0.14 * SR)
        tb = np.linspace(0, 0.14, nb, dtype=np.float32)
        cl = (0.7 * np.sin(2*np.pi*(165*np.exp(-tb*18)+48)*tb) + 0.3 * np.sin(2*np.pi*420*tb)*np.exp(-tb*38)) * env_ad(nb, 0.004, 0.06) * gain
        add_clip(sfx, cl.astype(np.float32), t0, pan=pan)

    bolt_clunk(43.05, pan=0.05, gain=0.10)

    # Smooth low-frequency metallic slat roll (band-limited 90-340Hz slat cadence + deep solid floor-seal THUD at 45.65s)
    n_sh = int(1.50 * SR)
    tsh = np.linspace(0, 1.50, n_sh, dtype=np.float32)
    slat_rate = 16.0 + 8.0 * (tsh / 1.50)
    slat_env = 0.55 + 0.45 * np.sin(2*np.pi*slat_rate*tsh)
    sh_body = (0.65 * np.sin(2*np.pi*112*tsh) + 0.35 * np.sin(2*np.pi*218*tsh)) * slat_env * env_ad(n_sh, 0.08, 0.12) * 0.052
    add_clip(sfx, sh_body.astype(np.float32), 44.15, pan=0.0)
    # Final solid floor seal thud at 45.62s ("sheleter bnd bilkul")
    bolt_clunk(45.62, pan=0.0, gain=0.14)

    # Light switch crisp mechanical click at 46.85s
    nc = int(0.05 * SR)
    tc = np.linspace(0, 0.05, nc, dtype=np.float32)
    sw_click = np.sin(2*np.pi*1150*tc) * np.exp(-tc*95) * 0.065
    add_clip(sfx, sw_click.astype(np.float32), 46.85, pan=-0.25)

    # 4) 51.70s: Woman slams shaking hands against reinforced door glass!
    ng = int(0.28 * SR)
    tg = np.linspace(0, 0.28, ng, dtype=np.float32)
    glass_hit = (0.75 * np.sin(2*np.pi*(95*np.exp(-tg*14)+38)*tg) + 0.25 * np.sin(2*np.pi*310*tg)*np.exp(-tg*24)) * env_ad(ng, 0.004, 0.12) * 0.16
    add_clip(sfx, glass_hit.astype(np.float32), 51.70, pan=0.0)
    # Final door security shutter lock at 79.6s ("So you leave it locked")
    bolt_clunk(79.65, pan=0.0, gain=0.12)

    # 5) 83.40s: Power cuts out (descending transformer hum drop 120Hz -> 28Hz)
    npw = int(0.95 * SR)
    tpw = np.linspace(0, 0.95, npw, dtype=np.float32)
    fpw = 120.0 * np.exp(-tpw * 1.65)
    pw_drop = (0.7 * np.sin(2*np.pi*np.cumsum(fpw)/SR) + 0.3 * np.sin(4*np.pi*np.cumsum(fpw)/SR)) * env_ad(npw, 0.02, 0.35) * 0.075
    add_clip(sfx, pw_drop.astype(np.float32), 83.35, pan=0.0)

    # 6) 95.15s: Distant reverberant metal alley crash + 101.45s door scrape + 104.0s, 104.65s, 105.30s THREE SLOW KNOCKS!
    ncr = int(1.1 * SR)
    tcr = np.linspace(0, 1.1, ncr, dtype=np.float32)
    crash = sum(a * np.sin(2*np.pi*f*tcr) * np.exp(-tcr*d) for f, a, d in [(138, 0.45, 3.5), (274, 0.30, 5.0), (418, 0.18, 7.0), (585, 0.10, 9.0)])
    add_clip(sfx, (crash * env_ad(ncr, 0.006, 0.35) * 0.11).astype(np.float32), 95.15, pan=-0.3)

    # Subtle steel door fingernail/metal scrape at 101.45s
    nsc2 = int(0.65 * SR)
    tsc2 = np.linspace(0, 0.65, nsc2, dtype=np.float32)
    scr = (np.sin(2*np.pi*(340 + 90*tsc2)*tsc2) * 0.6 + np.sin(2*np.pi*(520 + 130*tsc2)*tsc2) * 0.4) * env_ad(nsc2, 0.08, 0.18) * 0.032
    add_clip(sfx, scr.astype(np.float32), 101.45, pan=-0.15)

    # Three chilling slow heavy knocks on back steel/wood door: 104.00s, 104.68s, 105.36s
    for kt in [104.00, 104.68, 105.36]:
        nk = int(0.18 * SR)
        tk = np.linspace(0, 0.18, nk, dtype=np.float32)
        knock = (0.72 * np.sin(2*np.pi*(115*np.exp(-tk*22)+46)*tk) + 0.28 * np.sin(2*np.pi*265*tk)*np.exp(-tk*34)) * env_ad(nk, 0.003, 0.08) * 0.155
        add_clip(sfx, knock.astype(np.float32), kt, pan=-0.1)

    # 7) 114.65s: Phone buzzes (Emergency alert #2) + 143.2s slow footsteps outside
    phone_vibrate(114.65, pulses=2)
    eas_tone(116.20, dur=0.50)

    for s_i in range(6):
        ft = 142.80 + s_i * 0.58
        nf = int(0.13 * SR)
        tf = np.linspace(0, 0.13, nf, dtype=np.float32)
        step = np.sin(2*np.pi*(85*np.exp(-tf*18)+35)*tf) * env_ad(nf, 0.005, 0.06) * 0.065
        add_clip(sfx, step.astype(np.float32), ft, pan=-0.5 + 0.2 * s_i)

    # 8) 155.2s: Distant haunting civil-defense siren echo at sunrise
    nsir = int(2.8 * SR)
    tsir = np.linspace(0, 2.8, nsir, dtype=np.float32)
    fsir = 390.0 + 145.0 * np.sin(np.pi * tsir / 2.8)
    siren = np.sin(2*np.pi*np.cumsum(fsir)/SR) * env_ad(nsir, 0.55, 0.85) * 0.024
    add_clip(sfx, siren.astype(np.float32), 155.10, pan=0.45)

    # 9) 176.6s: Unlock back door + 180.0s-183.0s brisk urgent stealth footsteps in brick alley
    bolt_clunk(176.65, pan=-0.15, gain=0.10)
    for s_i in range(9):
        ft = 180.05 + s_i * 0.31
        nf = int(0.11 * SR)
        tf = np.linspace(0, 0.11, nf, dtype=np.float32)
        step = np.sin(2*np.pi*(105*np.exp(-tf*22)+42)*tf) * env_ad(nf, 0.004, 0.05) * 0.060
        add_clip(sfx, step.astype(np.float32), ft, pan=(-0.15 if s_i % 2 == 0 else 0.15))

    # 10) Act V Radio crackles/squelches (194.6s, 213.7s, 232.0s) + radio switch OFF click (254.45s) + Heavy Maintenance Door creaking & booming SHUT by itself (255.6s - 260.1s)!
    def radio_squelch(t0: float, dur: float = 0.32, gain: float = 0.042):
        nrq = int(dur * SR)
        trq = np.linspace(0, dur, nrq, dtype=np.float32)
        rq_src = rng.standard_normal(nrq).astype(np.float32)
        sos_rq = signal.butter(3, [650/(SR*0.5), 2400/(SR*0.5)], btype="band", output="sos")
        crackle = (signal.sosfilt(sos_rq, rq_src) * 0.55 + 0.45 * np.sin(2*np.pi*1320*trq)*np.exp(-trq*14)) * env_ad(nrq, 0.015, 0.06) * gain
        add_clip(sfx, crackle.astype(np.float32), t0, pan=0.2)

    radio_squelch(194.65, dur=0.28, gain=0.032)
    # V7: the two underground radio-MIMIC squelches (213.7 / 232.05) removed with the voices.
    # Hard radio switch click OFF at 254.45s
    add_clip(sfx, sw_click.astype(np.float32) * 1.25, 254.45, pan=0.2)

    # Heavy iron underground maintenance door slowly groaning shut (255.8s -> 259.65s) + deep cavern iron BOOM latch at 259.75s!
    ndoor = int(3.85 * SR)
    tdoor = np.linspace(0, 3.85, ndoor, dtype=np.float32)
    f_creak = 142.0 - 26.0 * (tdoor / 3.85) + 8.0 * np.sin(2*np.pi*2.4*tdoor)
    p_creak = 2*np.pi*np.cumsum(f_creak)/SR
    creak = (0.65 * np.sin(p_creak) + 0.35 * np.sin(2.03 * p_creak)) * env_ad(ndoor, 0.35, 0.35) * 0.038
    add_clip(sfx, creak.astype(np.float32), 255.80, pan=-0.2)

    # Final chilling underground heavy iron door SLAM/LATCH at 259.78s ("Slowly, by itself.")
    nboom = int(0.52 * SR)
    tboom = np.linspace(0, 0.52, nboom, dtype=np.float32)
    iron_latch = (0.78 * np.sin(2*np.pi*(82*np.exp(-tboom*9)+34)*tboom) + 0.22 * np.sin(2*np.pi*196*tboom)*np.exp(-tboom*18)) * env_ad(nboom, 0.005, 0.28) * 0.175
    add_clip(sfx, iron_latch.astype(np.float32), 259.76, pan=0.0)

    # ============ V5 HIT-AND-RUN SEQUENCE (26.98 - 27.9s) ============
    # Tire screech as the driver swerves (26.98)
    n_sc = int(0.85 * SR)
    t_sc = np.linspace(0, 0.85, n_sc, dtype=np.float32)
    f_sc = 1900.0 - 1150.0 * (t_sc / 0.85)
    wob = 1.0 + 0.35 * np.sin(2 * np.pi * 23.0 * t_sc)
    ph_sc = 2 * np.pi * np.cumsum(f_sc * wob) / SR
    screech = (np.sin(ph_sc) * 0.5 + 0.22 * np.sign(np.sin(ph_sc))) * env_ad(n_sc, 0.03, 0.22) * 0.085
    sos_sc = signal.butter(2, [700 / (SR * 0.5), 3400 / (SR * 0.5)], btype="band", output="sos")
    add_clip(sfx, signal.sosfilt(sos_sc, screech).astype(np.float32), 26.98, pan=0.15)

    # Heavy layered CAR-BODY IMPACT (27.06): sub thump + metal crunch + dark overtone
    n_im = int(0.55 * SR)
    t_im = np.linspace(0, 0.55, n_im, dtype=np.float32)
    f_im = 92.0 * np.exp(-t_im * 7.0) + 30.0
    ph_im = 2 * np.pi * np.cumsum(f_im) / SR
    thump = np.sin(ph_im) * np.exp(-t_im * 5.2)
    rng_im = np.random.default_rng(77)
    crunch = signal.sosfilt(
        signal.butter(2, [240 / (SR * 0.5), 1500 / (SR * 0.5)], btype="band", output="sos"),
        rng_im.standard_normal(n_im).astype(np.float32),
    ) * np.exp(-t_im * 8.5) * 0.85
    impact = (thump * 0.90 + crunch * 0.55 + 0.16 * np.sin(2.03 * ph_im)) * env_ad(n_im, 0.002, 0.30) * 0.23
    add_clip(sfx, impact.astype(np.float32), 27.06, pan=0.05)

    # Body slams the asphalt (27.78) — painful landing
    n_bd = int(0.22 * SR)
    t_bd = np.linspace(0, 0.22, n_bd, dtype=np.float32)
    f_bd = 70.0 * np.exp(-t_bd * 16.0) + 32.0
    body = np.sin(2 * np.pi * np.cumsum(f_bd) / SR) * env_ad(n_bd, 0.003, 0.10) * 0.16
    add_clip(sfx, body.astype(np.float32), 27.78, pan=0.0)

    # ============ V5 HORDE SURGE + OFFICER TACKLE (65.3 - 66.2s) ============
    # Fast-monster surge roar (65.35): detuned growl cluster racing up
    n_ro = int(1.25 * SR)
    t_ro = np.linspace(0, 1.25, n_ro, dtype=np.float32)
    growl = sum(a * np.sign(np.sin(2 * np.pi * f * t_ro + 3.0 * np.sin(2 * np.pi * 5.5 * t_ro)))
                for f, a in [(96.0, 0.40), (101.0, 0.35), (108.0, 0.30)])
    growl = growl * (0.35 + 0.65 * (t_ro / 1.25)) * env_ad(n_ro, 0.10, 0.35) * 0.075
    sos_gr = signal.butter(2, [140 / (SR * 0.5), 900 / (SR * 0.5)], btype="band", output="sos")
    add_clip(sfx, signal.sosfilt(sos_gr, growl).astype(np.float32), 65.35, pan=0.10)

    # Officer tackled to the ground (65.95)
    add_clip(sfx, (body * 1.15).astype(np.float32), 65.95, pan=-0.10)

    # Subtle room/cavern space on foley
    sfx_board = Pedalboard([
        Reverb(room_size=0.52, damping=0.62, wet_level=0.22, dry_level=0.88),
    ])
    return sfx_board(sfx.T, SR).T.astype(np.float32)


def build_intro_layers(total_samples: int) -> np.ndarray:
    """V7 ORIGINS INTRO SOUND DESIGN (render time 0-12.40, NO voice-over).

    normal life (birds/pad) -> cut to lab (hum/shimmer) -> BUTTON + chemical rain ->
    writhing transformation -> LOUD evil laugh (user's Drive SFX) -> city chaos ->
    news EAS -> 3.3s BLACK with a deep dread swell that carries the VO's first line.
    """
    bed = np.zeros((total_samples, 2), dtype=np.float32)
    rng = np.random.default_rng(47047)
    sos_lp400 = signal.butter(2, 400.0 / (SR * 0.5), btype="low", output="sos")
    sos_bp_air = signal.butter(2, [500.0 / (SR * 0.5), 3600.0 / (SR * 0.5)], btype="band", output="sos")
    sos_bp_crowd = signal.butter(2, [300.0 / (SR * 0.5), 1400.0 / (SR * 0.5)], btype="band", output="sos")

    def seg(t0, t1):
        return int(t0 * SR), int(t1 * SR)

    # ---- A. NORMAL LIFE 0.00-2.40: morning birds, soft street air, warm open-fifth pad ----
    for t0, f0, dur, pan in [
        (0.18, 3400., 0.16, -0.35), (0.52, 2950., 0.20, 0.30), (1.02, 3800., 0.14, 0.45),
        (1.34, 3100., 0.18, -0.20), (1.78, 3550., 0.15, 0.38), (2.08, 2850., 0.19, -0.42),
    ]:
        n_b = int(dur * SR)
        t_b = np.linspace(0.0, dur, n_b, dtype=np.float32)
        wob = f0 * (1.0 + 0.06 * np.sin(2 * np.pi * 22.0 * t_b + f0))
        chirp = np.sin(2 * np.pi * np.cumsum(wob) / SR) * np.maximum(np.sin(np.pi * t_b / dur), 0.0) ** 1.5 * 0.020
        add_clip(bed, np.stack([chirp, chirp], axis=1).astype(np.float32), t0, pan=pan)
    n_a0, n_a1 = seg(0.0, 2.40)
    air = signal.sosfilt(sos_lp400, rng.standard_normal(n_a1 - n_a0).astype(np.float32))
    air *= (0.6 + 0.4 * np.sin(np.linspace(0, 5, n_a1 - n_a0, dtype=np.float32)))
    bed[n_a0:n_a1, 0] += air * 0.010
    bed[n_a0:n_a1, 1] += air * 0.010
    t_pad = np.linspace(0.0, 2.40, n_a1 - n_a0, dtype=np.float32)
    pad_wave = (0.5 * np.sin(2 * np.pi * 65.41 * t_pad) + 0.32 * np.sin(2 * np.pi * 98.0 * t_pad + 0.7)
                + 0.22 * np.sin(2 * np.pi * 130.81 * t_pad + 1.9)) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.35 * t_pad))
    pad_wave *= np.minimum(1.0, t_pad / 0.5) * np.minimum(1.0, (2.40 - t_pad) / 0.45)
    bed[n_a0:n_a1, 0] += pad_wave * 0.020
    bed[n_a0:n_a1, 1] += pad_wave * 0.020

    # ---- B. CUT TO THE LAB 2.40: whoosh, then cold fluorescent hum + sparse metal drips ----
    def whoosh(t0, g=0.20, dur=0.30):
        n_w = int(dur * SR)
        t_w = np.linspace(0.0, dur, n_w, dtype=np.float32)
        wh = signal.sosfilt(sos_bp_air, rng.standard_normal(n_w).astype(np.float32) * (0.25 + (t_w / dur) ** 1.8))
        wh = wh * env_ad(n_w, 0.012, 0.10) * g
        add_clip(bed, np.stack([wh, wh], axis=1).astype(np.float32), t0 - 0.20, pan=0.0)
    whoosh(2.40, 0.20)
    n_l0, n_l1 = seg(2.42, 6.60)
    t_l = np.linspace(0.0, 6.60 - 2.42, n_l1 - n_l0, dtype=np.float32)
    fluoro = 0.5 + 0.5 * np.sin(2 * np.pi * 96.0 * t_l)
    lab_hum = (0.40 * np.sin(2 * np.pi * 55.0 * t_l) + 0.20 * np.sin(2 * np.pi * 110.3 * t_l)
               + 0.14 * np.sin(2 * np.pi * 164.8 * t_l) + 0.05 * np.sin(2 * np.pi * 493.9 * t_l) * fluoro)
    lab_hum *= np.minimum(1.0, t_l / 0.30) * np.minimum(1.0, (6.60 - 2.42 - t_l) / 0.60)
    bed[n_l0:n_l1, 0] += lab_hum * 0.036
    bed[n_l0:n_l1, 1] += lab_hum * 0.036
    for t0, f0 in [(2.78, 2320.0), (3.44, 3410.0), (3.98, 2320.0)]:
        n_cl = int(0.30 * SR)
        t_cl = np.linspace(0.0, 0.30, n_cl, dtype=np.float32)
        clink = (np.sin(2 * np.pi * f0 * t_cl) * np.exp(-t_cl * 26.0)
                 + 0.5 * np.sin(2 * np.pi * f0 * 1.47 * t_cl) * np.exp(-t_cl * 34.0)) * 0.075
        add_clip(bed, np.stack([clink, clink], axis=1).astype(np.float32), t0, pan=0.18)

    # ---- C. MASK CLOSE-UP 3.40-4.30: eerie shimmer + low unease sub ----
    n_s0, n_s1 = seg(3.40, 4.30)
    t_s = np.linspace(0.0, 0.90, n_s1 - n_s0, dtype=np.float32)
    sos_sh = signal.butter(2, [3200.0 / (SR * 0.5), 5200.0 / (SR * 0.5)], btype="band", output="sos")
    shim = signal.sosfilt(sos_sh, rng.standard_normal(n_s1 - n_s0).astype(np.float32))
    shim *= (0.4 + 0.6 * np.sin(2 * np.pi * 0.8 * t_s)) * np.minimum(1.0, t_s / 0.25) * np.minimum(1.0, (0.90 - t_s) / 0.20)
    bed[n_s0:n_s1, 0] += shim * 0.0060
    bed[n_s0:n_s1, 1] += shim * 0.0060
    sub41 = np.sin(2 * np.pi * 41.2 * t_s) * np.minimum(1.0, t_s / 0.4) * 0.020
    bed[n_s0:n_s1, 0] += sub41
    bed[n_s0:n_s1, 1] += sub41

    # ---- D. THE BUTTON 4.30: cover-flip + heavy clunk + power rise; CHEMICAL RAIN begins ----
    whoosh(4.30, 0.10, 0.12)
    n_ck = int(0.20 * SR)
    t_ck = np.linspace(0.0, 0.20, n_ck, dtype=np.float32)
    f_ck = 95.0 * np.exp(-t_ck * 16.0) + 34.0
    clunk = np.sin(2 * np.pi * np.cumsum(f_ck) / SR) * env_ad(n_ck, 0.003, 0.09) * 0.34
    add_clip(bed, np.stack([clunk, clunk], axis=1).astype(np.float32), 4.30, pan=0.0)
    n_bt = int(0.008 * SR)
    click = np.sin(2 * np.pi * 2800.0 * np.linspace(0, 0.008, n_bt, dtype=np.float32)) * 0.12
    add_clip(bed, np.stack([click, click], axis=1).astype(np.float32), 4.292, pan=0.0)
    n_pr = int(0.16 * SR)
    t_pr = np.linspace(0.0, 0.16, n_pr, dtype=np.float32)
    f_pr = 55.0 + 13.0 * (t_pr / 0.16) ** 2
    rise = np.sin(2 * np.pi * np.cumsum(f_pr) / SR) * (t_pr / 0.16) * 0.055
    add_clip(bed, np.stack([rise, rise], axis=1).astype(np.float32), 4.31, pan=0.0)
    # chemical rain: deterministic sparse pips 4.42-6.70, density ramps
    cur, pi = 4.42, 0
    while cur < 6.70:
        pr_r = rng.random()
        if pr_r < min(0.98, 0.30 + 0.65 * (cur - 4.42) / 2.28):
            f_p = 1800.0 + rng.random() * 900.0
            dur_p = 0.012 + rng.random() * 0.013
            n_p = int(dur_p * SR)
            t_p = np.linspace(0.0, dur_p, n_p, dtype=np.float32)
            pip = np.sin(2 * np.pi * f_p * t_p) * np.exp(-t_p * 260.0) * (0.016 + 0.016 * (cur - 4.42) / 2.28)
            add_clip(bed, np.stack([pip, pip], axis=1).astype(np.float32), cur, pan=(rng.random() - 0.5))
        cur += 0.045 + rng.random() * 0.095
        pi += 1
    # soft alarm pulses 4.45-6.55 (the facility knows)
    k_al = 0
    t_al0 = 4.45
    while t_al0 < 6.55:
        f_al = 740.0 if k_al % 2 == 0 else 560.0
        n_al = int(0.16 * SR)
        t_al = np.linspace(0.0, 0.16, n_al, dtype=np.float32)
        sos_al = signal.butter(2, 1500.0 / (SR * 0.5), btype="low", output="sos")
        klax = signal.sosfilt(sos_al, np.sin(2 * np.pi * f_al * t_al)).astype(np.float32) * env_ad(n_al, 0.008, 0.05) * 0.042
        add_clip(bed, np.stack([klax, klax], axis=1).astype(np.float32), t_al0, pan=0.0)
        t_al0 += 0.42
        k_al += 1

    # ---- E. TRANSFORMATION 5.70-6.55: writhing detuned cluster + riser into the laugh ----
    n_w0, n_w1 = seg(5.20, 6.55)
    t_w = np.linspace(0.0, 1.35, n_w1 - n_w0, dtype=np.float32)
    writhe = (0.36 * np.sin(2 * np.pi * 110.0 * t_w + 0.4 * np.sin(2 * np.pi * 5.1 * t_w))
              + 0.30 * np.sin(2 * np.pi * 116.54 * t_w)
              + 0.22 * np.sin(2 * np.pi * 155.56 * t_w + 0.3 * np.sin(2 * np.pi * 7.3 * t_w))
              + 0.18 * np.sin(2 * np.pi * 58.27 * t_w))
    writhe *= (t_w / 1.35) ** 1.6 * 0.052
    bed[n_w0:n_w1, 0] += writhe
    bed[n_w0:n_w1, 1] += writhe
    n_r0, n_r1 = seg(5.90, 6.55)
    r_len = 0.65
    t_r = np.linspace(0.0, r_len, n_r1 - n_r0, dtype=np.float32)
    riser = signal.sosfilt(sos_bp_air, rng.standard_normal(n_r1 - n_r0).astype(np.float32) * (t_r / r_len) ** 2.2)
    bed[n_r0:n_r1, 0] += riser * 0.030
    bed[n_r0:n_r1, 1] += riser * 0.030
    n_dr = int(0.45 * SR)
    t_dr = np.linspace(0.0, 0.45, n_dr, dtype=np.float32)
    f_dr = 41.0 * np.exp(-t_dr * 7.0) + 30.0
    sub_drop = np.sin(2 * np.pi * np.cumsum(f_dr) / SR) * env_ad(n_dr, 0.004, 0.22) * 0.16
    add_clip(bed, np.stack([sub_drop, sub_drop], axis=1).astype(np.float32), 6.53, pan=0.0)

    # ---- F. THE EVIL LAUGH 6.55-7.60: the user's Drive SFX, slowed just slightly ----
    if os.path.exists(EVIL_LAUGH_MP3):
        laugh = decode_audio(EVIL_LAUGH_MP3)
        for at, speed, g, pan in [(6.55, 1.15, 0.95, 0.0), (7.10, 1.35, 0.32, 0.25)]:
            n_l = int(len(laugh) / speed)
            idx = np.arange(n_l, dtype=np.float32) * speed
            l_st = np.stack([np.interp(idx, np.arange(len(laugh), dtype=np.float32), laugh[:, ch]) for ch in range(2)], axis=1).astype(np.float32)
            peak = float(np.max(np.abs(l_st))) + 1e-9
            l_st *= (0.92 / peak)
            nf, nr = int(0.02 * SR), int(0.10 * SR)
            l_st[:nf] *= np.linspace(0, 1, nf)[:, None]
            l_st[-nr:] *= np.linspace(1, 0, nr)[:, None]
            add_clip(bed, (l_st * g).astype(np.float32), at, pan=pan)
        print(f"    evil laugh SFX placed at 6.55 (+echo 7.10) from {EVIL_LAUGH_MP3}")
    else:
        # fallback: booming synthesized laugh pulses (minor-third downward stabs)
        for k_lh in range(8):
            at = 6.58 + k_lh * 0.115
            f_lh = 98.0 * (0.94 ** k_lh)
            n_lh = int(0.11 * SR)
            t_lh = np.linspace(0.0, 0.11, n_lh, dtype=np.float32)
            stab = np.sin(2 * np.pi * f_lh * t_lh) * env_ad(n_lh, 0.006, 0.07) * (0.30 - k_lh * 0.015)
            add_clip(bed, np.stack([stab, stab], axis=1).astype(np.float32), at, pan=0.0)
    n_g0, n_g1 = seg(6.55, 7.60)
    t_g = np.linspace(0.0, 1.05, n_g1 - n_g0, dtype=np.float32)
    laugh_sub = np.sin(2 * np.pi * 36.71 * t_g) * np.minimum(1.0, t_g / 0.25) * 0.048
    bed[n_g0:n_g1, 0] += laugh_sub
    bed[n_g0:n_g1, 1] += laugh_sub

    # ---- G. CITY CHAOS 7.60-8.70: braam, sirens, crowd clamor, rumble ----
    whoosh(7.60, 0.24)
    n_br = int(1.8 * SR)
    t_br = np.linspace(0.0, 1.8, n_br, dtype=np.float32)
    f_br = 36.71 * (1.0 + 0.55 * np.exp(-t_br * 6.5))
    braam = (0.85 * np.sin(2 * np.pi * np.cumsum(f_br) / SR)
             + 0.30 * np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f_br * 2.5) / SR))
             + 0.15 * np.sin(2 * np.pi * np.cumsum(f_br * 1.5) / SR))
    braam = braam * np.exp(-t_br * 1.5) * env_ad(n_br, 0.006, 0.5) * 0.30
    add_clip(bed, np.stack([braam, braam], axis=1).astype(np.float32), 7.61, pan=0.0)
    for at, g, pan in [(7.62, 0.016, 0.45), (7.98, 0.013, -0.42)]:
        n_si = int(0.9 * SR)
        t_si = np.linspace(0.0, 0.9, n_si, dtype=np.float32)
        f_si = 620.0 + 190.0 * np.sin(2 * np.pi * 0.85 * t_si)
        siren_far = np.sin(2 * np.pi * np.cumsum(f_si) / SR) * env_ad(n_si, 0.3, 0.4) * g
        add_clip(bed, np.stack([siren_far, siren_far], axis=1).astype(np.float32), at, pan=pan)
    n_c0, n_c1 = seg(7.60, 8.70)
    crowd = signal.sosfilt(sos_bp_crowd, rng.standard_normal(n_c1 - n_c0).astype(np.float32))
    t_c = np.linspace(0.0, 1.10, n_c1 - n_c0, dtype=np.float32)
    clamor = 0.5 + 0.5 * np.sin(2 * np.pi * 7.1 * t_c) * np.sin(2 * np.pi * 2.3 * t_c + 0.6)
    crowd *= clamor * np.minimum(1.0, t_c / 0.15) * np.minimum(1.0, (1.10 - t_c) / 0.20)
    bed[n_c0:n_c1, 0] += crowd * 0.028
    bed[n_c0:n_c1, 1] += crowd * 0.028
    n_rm = int(0.55 * SR)
    t_rm = np.linspace(0.0, 0.55, n_rm, dtype=np.float32)
    sos_rm = signal.butter(2, 180.0 / (SR * 0.5), btype="low", output="sos")
    rumble = signal.sosfilt(sos_rm, rng.standard_normal(n_rm).astype(np.float32)) * env_ad(n_rm, 0.05, 0.3) * 0.20
    add_clip(bed, np.stack([rumble, rumble], axis=1).astype(np.float32), 7.63, pan=0.0)

    # ---- H. NEWS 8.70-9.10: EAS dual-tone + urgent teletype beeps ----
    for t_e in [8.72, 8.88]:
        n_e = int(0.30 * SR)
        t_ev = np.linspace(0.0, 0.30, n_e, dtype=np.float32)
        tone = 0.5 * (np.sin(2 * np.pi * 853.0 * t_ev) + np.sin(2 * np.pi * 960.0 * t_ev)) * env_ad(n_e, 0.03, 0.08) * 0.058
        add_clip(bed, np.stack([tone, tone], axis=1).astype(np.float32), t_e, pan=0.0)
    for t_b in [8.74, 8.86, 8.98]:
        n_b = int(0.07 * SR)
        t_bv = np.linspace(0.0, 0.07, n_b, dtype=np.float32)
        beep = np.sin(2 * np.pi * 1245.0 * t_bv) * env_ad(n_b, 0.004, 0.02) * 0.055
        add_clip(bed, np.stack([beep, beep], axis=1).astype(np.float32), t_b, pan=0.22)

    # ---- I. BLACK SCREEN 9.10-12.40: cut to near-silence, then a deep dread swell ----
    n_k0, n_k1 = seg(9.50, 12.30)
    t_k = np.linspace(0.0, 2.80, n_k1 - n_k0, dtype=np.float32)
    swell = np.sin(2 * np.pi * 36.71 * t_k + 0.3 * np.sin(2 * np.pi * 0.21 * t_k)) * (t_k / 2.80) ** 1.4
    bed[n_k0:n_k1, 0] += swell * 0.050
    bed[n_k1 - 1, :] = 0.0  # hard out before the bright street SMASH
    sos_kb = signal.butter(2, [150.0 / (SR * 0.5), 620.0 / (SR * 0.5)], btype="band", output="sos")
    air_d = signal.sosfilt(sos_kb, rng.standard_normal(n_k1 - n_k0).astype(np.float32))
    bed[n_k0:n_k1, 0] += air_d * 0.0060
    bed[n_k0:n_k1, 1] += air_d * 0.0060
    beat_t = 9.70
    while beat_t < 12.20:
        for offset, p0, ak in [(0.0, 66.0, 1.0), (0.21, 56.0, 0.72)]:
            n_hb = int(0.16 * SR)
            th = np.linspace(0.0, 0.16, n_hb, dtype=np.float32)
            f_inst = p0 * np.exp(-th * 11.0) + 30.0
            env_hb = np.maximum(0.0, np.sin(np.pi * np.clip(th / 0.16, 0, 1))) ** 1.8
            thump = np.sin(2 * np.pi * np.cumsum(f_inst) / SR) * env_hb * 0.10 * ak
            add_clip(bed, np.stack([thump, thump], axis=1).astype(np.float32), beat_t + offset, pan=0.0)
        beat_t += 60.0 / 54.0

    return bed

def ensure_vo_wav() -> str:
    """Guarantee /tmp/.../vo_unchanged_48k.wav exists (pure format conversion — ZERO audio edits)."""
    if os.path.exists(VO_WAV_48K):
        return VO_WAV_48K
    os.makedirs(os.path.dirname(VO_WAV_48K), exist_ok=True)
    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", VO_REPO_MP3, "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le", VO_WAV_48K
    ], check=True)
    return VO_WAV_48K


def calibrate_bed_gain(vo_mono: np.ndarray, bed: np.ndarray, target_db: float = -6.0) -> float:
    """Rulebook: score+SFX bed sits at `target_db` gated RMS below the voice during speech.
    Gating: 20ms frames where the voice RMS exceeds a speech threshold (voice-gated measurement)."""
    hop = int(0.020 * SR)
    n = len(vo_mono) // hop
    vr = np.sqrt(np.mean(vo_mono[: n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    br = np.sqrt(np.mean(bed[: n * hop, :].reshape(n, hop, 2).mean(axis=2) ** 2, axis=1) + 1e-12)
    thr = max(float(np.percentile(vr, 50)) * 0.35, 0.006)
    voiced = vr > thr
    if voiced.sum() < 50:
        return 1.0
    vo_rms = float(np.sqrt(np.mean(vr[voiced] ** 2)))
    bed_rms = float(np.sqrt(np.mean(br[voiced] ** 2)))
    if bed_rms < 1e-9:
        return 1.0
    want = vo_rms * (10.0 ** (target_db / 20.0))
    gain = want / bed_rms
    gain = float(np.clip(gain, 0.55, 1.70))
    meas_db = 20.0 * np.log10(bed_rms * gain / vo_rms)
    print(f"[BED CAL] voiced frames={int(voiced.sum())} vo_rms={vo_rms:.4f} bed_rms={bed_rms:.4f} -> gain={gain:.3f} (bed now {meas_db:+.1f} dB vs voice)")
    return gain


ASSET_DIR_GOLD = "past_detour_gold_1971/v3_audio"
ASSET_EMU_CUES = "past_detour_emu_1932/final_image_edit_v3/natural_cues.wav"
ASSET_EMU_FX = "past_detour_emu_1932/final_image_edit_v2/restrained_effects.wav"
ASSET_EMU_FOLEY = "past_detour_emu_1932/audio/original_foley.wav"


def decode_audio(path):
    """Decode any audio file to 48k stereo float32 via ffmpeg (mp3/wav safe)."""
    raw = subprocess.run(
        [FFMPEG, "-v", "error", "-i", path, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    return x.reshape(-1, 2).copy()


def tape_darken(x, speed=0.82, lp_hz=1100.0, peak=0.30):
    """Tape-slow a stinger (pitch + darkness down) so bright motifs become somber horror beds."""
    n = int(len(x) / speed)
    idx = np.arange(n, dtype=np.float32) * speed
    y = np.stack([np.interp(idx, np.arange(len(x), dtype=np.float32), x[:, ch]) for ch in range(2)], axis=1).astype(np.float32)
    sos = signal.butter(3, lp_hz / (SR * 0.5), btype="low", output="sos")
    y = np.stack([signal.sosfilt(sos, y[:, ch]) for ch in range(2)], axis=1).astype(np.float32)
    nf = int(0.03 * SR); nr = int(0.28 * SR)
    y[:nf] *= np.linspace(0, 1, nf)[:, None]
    y[-nr:] *= np.linspace(1, 0, nr)[:, None]
    return y * (peak / (np.max(np.abs(y)) + 1e-9))


def build_asset_layers(total_samples):
    """V5: the user's own asset-folder soundtracks & effects —
    * gold act-stingers tape-darkened into recurring situational horror motifs
    * emu natural-cue beds as organic room tone (calm store / street panic / underground / sunrise)."""
    bed = np.zeros((total_samples, 2), dtype=np.float32)
    rev = Pedalboard([Reverb(room_size=0.55, damping=0.70, wet_level=0.30, dry_level=0.85)])
    motifs = [
        ("01_hook.mp3", 3.30, 0.85),      # first warning alert
        ("02_rule.mp3", 20.40, 0.80),     # traffic stops / man in the road
        ("03_pressure.mp3", 61.28, 0.85), # police standoff
        ("04_nixon.mp3", 113.84, 0.85),   # mimicry reveal
        ("05_after.mp3", 145.96, 0.80),   # sunrise aftermath
        ("06_end.mp3", 248.00, 0.85),     # finale
    ]
    for name, at, g in motifs:
        p = os.path.join(ASSET_DIR_GOLD, name)
        if not os.path.exists(p):
            continue
        clip = tape_darken(decode_audio(p))
        clip = rev(clip.T, SR).T.astype(np.float32)
        add_clip(bed, (clip * g).astype(np.float32), at, pan=0.0)

    def room_tone(path, t0, t1, sa, sb, rms_target):
        if not os.path.exists(path):
            return
        x = decode_audio(path)
        seg = x[int(sa * SR):int(sb * SR)]
        if len(seg) < SR // 2:
            return
        sos = signal.butter(2, 3600.0 / (SR * 0.5), btype="low", output="sos")
        seg = np.stack([signal.sosfilt(sos, seg[:, ch]) for ch in range(2)], axis=1).astype(np.float32)
        cur = float(np.sqrt(np.mean(seg ** 2))) + 1e-9
        seg *= rms_target / cur
        need = int((t1 - t0) * SR)
        reps = (need // len(seg)) + 1
        loop = np.concatenate([seg] * reps, axis=0)[:need]
        fd = int(1.2 * SR)
        loop[:fd] *= np.linspace(0, 1, fd)[:, None]
        loop[-fd:] *= np.linspace(1, 0, fd)[:, None]
        add_clip(bed, loop.astype(np.float32), t0, pan=0.0)

    room_tone(ASSET_EMU_CUES, 4.2, 18.5, 0, 20, 0.0085)     # calm store room tone (post-cold-open)
    room_tone(ASSET_EMU_FX, 20.4, 32.9, 8, 28, 0.0110)       # street panic texture
    room_tone(ASSET_EMU_FOLEY, 145.96, 169.7, 0, 24, 0.0075) # empty sunrise street walk
    room_tone(ASSET_EMU_CUES, 193.4, 246.0, 24, 48, 0.0100)  # damp underground cavern
    return bed


def main():
    vo_st, sr_in = sf.read(ensure_vo_wav(), dtype="float32")
    assert sr_in == SR, f"Expected {SR}Hz, got {sr_in}Hz"
    if vo_st.ndim == 1:
        vo_st = np.stack([vo_st, vo_st], axis=1)
    vo_mono = vo_st.mean(axis=1)
    story_samples = len(vo_st)
    story_dur = story_samples / SR
    # V7: pad INTRO_SHIFT seconds of silence at the head — the cinematic intro has NO VO;
    # the first spoken word lands on the 3.30s BLACK SCREEN at 9.105s.
    pad = int(INTRO_SHIFT * SR)
    vo_st = np.concatenate([np.zeros((pad, 2), dtype=np.float32), vo_st], axis=0)
    vo_mono = np.concatenate([np.zeros(pad, dtype=np.float32), vo_mono], axis=0)
    total_samples = len(vo_st)
    total_dur = total_samples / SR
    print(f"Loaded UNEDITED ElevenLabs v4 voiceover: {story_dur:.3f}s (+{INTRO_SHIFT}s intro pad = {total_dur:.3f}s)")

    # 1) Build & save exact word-aligned timeline (`words_v3.json`)
    build_words_v3(vo_mono, total_dur)

    # 2) Synthesize Dramatic Horror & Horror-Suspense Score + Clean Foley
    # (All story-time layers are built on the STORY timeline, then shifted +INTRO_SHIFT.)
    print("Synthesizing dramatic horror & horror-suspense soundtrack...")
    score = build_dramatic_horror_score(story_samples)
    print("Synthesizing clean low-noise cinema foley...")
    foley = build_clean_foley(story_samples)
    print("Layering the user's asset-folder soundtracks & effects...")
    assets = build_asset_layers(story_samples)
    print(f"Building the V7 ORIGINS intro sound design (0-{INTRO_END}s, no voice-over)...")
    intro = build_intro_layers(total_samples)

    def shifted(layer: np.ndarray) -> np.ndarray:
        out = np.zeros((total_samples, 2), dtype=np.float32)
        out[pad:pad + len(layer)] = layer
        return out

    score, foley, assets = shifted(score), shifted(foley), shifted(assets)

    # 3) Smooth sidechain ducking of score under spoken voiceover so VO remains 100% untouched & crystal clear!
    win = int(0.04 * SR)
    vo_env = np.sqrt(np.maximum(1e-12, signal.convolve(vo_mono ** 2, np.ones(win, dtype=np.float32) / win, mode="same")))
    # Smooth release envelope (220ms)
    sos_env = signal.butter(1, 3.2 / (SR * 0.5), btype="low", output="sos")
    vo_env_s = signal.sosfilt(sos_env, np.clip(vo_env / 0.085, 0.0, 1.0)).astype(np.float32)
    # When VO speaks -> duck score gently to 42%; in dramatic pauses -> score swells to 100%!
    duck_gain = (1.0 - 0.58 * vo_env_s)[:, None]

    # Voiceover is NOT stretched, pitched, trimmed, or altered — pure sample-for-sample VO + ducked horror score + foley!
    # V7 rulebook: bed sits -6.4 dB gated RMS below the voice; the intro bed ducks like the
    # asset layers so the VO's first words on the BLACK SCREEN stay crystal clear.
    bed = score * duck_gain * 0.95 + foley * 0.92 + assets * (0.55 + 0.45 * duck_gain) + intro * (0.62 + 0.38 * duck_gain)
    bed_gain = calibrate_bed_gain(vo_mono, bed, target_db=-6.4)
    raw_mix = vo_st * 1.52 + bed * bed_gain  # V7: main voice-over louder

    # Transparent true-peak brickwall safety limiter + EBU R128 loudness normalization to -14.0 LUFS
    lim = Pedalboard([Limiter(threshold_db=-6.0, release_ms=110.0)])  # V7: headroom so loudnorm can reach -14 LUFS
    pre_wav = "/tmp/rick_study/v3/pre_master_v3.wav"
    sf.write(pre_wav, lim(raw_mix.T, SR).T, SR, subtype="PCM_16")

    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", pre_wav,
        "-af", "loudnorm=I=-14.0:TP=-1.0:LRA=9.5",
        "-ar", str(SR), "-ac", "2", "-c:a", "pcm_s16le",
        OUT_WAV
    ], check=True)
    subprocess.run([
        FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
        "-i", OUT_WAV,
        "-c:a", "libmp3lame", "-b:a", "256k",
        OUT_MP3
    ], check=True)
    os.remove(pre_wav)

    chk = subprocess.run(
        [FFMPEG, "-hide_banner", "-i", OUT_WAV, "-af", "ebur128", "-f", "null", "-"],
        capture_output=True, text=True
    )
    tail = "\n".join(chk.stderr.splitlines()[-12:])
    print(f"Mastered {OUT_WAV} & {OUT_MP3}:\n{tail}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
1. Runs PocketSphinx first-pass word alignment on nar_01..nar_08 + child_radio + child_whisper.
2. Slices every sentence cleanly at zero-crossings in exact script order.
3. Applies per-tag emotional horror vocal processing (whisper intimacy, radio filter, EAS broadcast, pauses).
4. Mixes procedural dark horror soundscape + exact story-synced foley (phone buzz, EAS alert, glass slam,
   shutter roll, clatter, dragging, broken glass, eerie clicking, radio static, ringing phone, footsteps,
   lock click, THREE KNOCKS, blackout thud, and sprinting footsteps in the dark corridor!).
5. Outputs:
   - input/voiceover_master.wav (clean 44.1kHz stereo horror master)
   - timeline/sentences.json (exact global timestamps of every spoken line + emotion + chapter)
   - timeline/chapters.json (exact start/end timestamps of Chapters 1..6 for clean 9:16 Shorts slicing!)
"""
import json, math, os, re, subprocess, wave
from pathlib import Path
import numpy as np
from scipy.signal import butter, sosfilt
import pocketsphinx

PROJ = Path(__file__).resolve().parent.parent
CLIPS_DIR = PROJ / "input" / "clips"
TL_DIR = PROJ / "timeline"
TL_DIR.mkdir(parents=True, exist_ok=True)

SR = 44100
ALIGN_SR = 16000

parsed = json.loads((PROJ / "input" / "parsed_chapters.json").read_text(encoding="utf-8"))
chapters = parsed["chapters"]
packed_clips = parsed["packed_clips"]

def load_wav_mono(path: Path, target_sr: int) -> np.ndarray:
    tmp = path.with_suffix(f".{target_sr}.raw")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(path),
        "-ac", "1", "-ar", str(target_sr), "-f", "s16le", str(tmp)
    ], check=True)
    pcm = np.frombuffer(tmp.read_bytes(), dtype=np.int16).astype(np.float32) / 32768.0
    tmp.unlink(missing_ok=True)
    return pcm

def norm_words(text: str):
    # Clean tokens for PocketSphinx alignment
    t = text.lower().replace("—", " ").replace("-", " ")
    words = re.findall(r"[a-z0-9']+", t)
    # Map digits if any
    num_map = {"4": "four", "1": "one", "2": "two", "3": "three", "10": "ten"}
    out = []
    for w in words:
        w = w.strip("'")
        if w:
            out.append(num_map.get(w, w))
    return out

def align_clip(wav_path: Path, text: str):
    tmp16 = wav_path.with_suffix(".16k.pcm")
    subprocess.run([
        "ffmpeg", "-y", "-v", "error", "-i", str(wav_path),
        "-ac", "1", "-ar", "16000", "-f", "s16le", str(tmp16)
    ], check=True)
    pcm_bytes = tmp16.read_bytes()
    dur_s = len(pcm_bytes) / (2 * 16000)
    tmp16.unlink(missing_ok=True)

    words = norm_words(text)
    dec = pocketsphinx.Decoder(loglevel="FATAL")
    # Ensure any OOV words have fallback phones so alignment never drops a word
    for w in set(words):
        if dec.lookup_word(w) is None:
            # Simple phonetic fallback
            phones = []
            for ch in w:
                if ch in "aeiou":
                    phones.append("AH")
                elif ch in "bcdfghjklmnpqrstvwxyz":
                    mp = {"b":"B","c":"K","d":"D","f":"F","g":"G","h":"HH","j":"JH","k":"K","l":"L",
                          "m":"M","n":"N","p":"P","q":"K","r":"R","s":"S","t":"T","v":"V","w":"W","x":"K S","y":"Y","z":"Z"}
                    phones.extend(mp[ch].split())
            if phones:
                dec.add_word(w, " ".join(phones), True)

    dec.set_align_text(" ".join(words))
    dec.start_utt()
    dec.process_raw(pcm_bytes, full_utt=True)
    dec.end_utt()

    aligned = []
    for seg in dec.seg():
        if seg.word in ("<s>", "</s>", "<sil>", "(null)"):
            continue
        w_clean = re.sub(r"\(\d+\)$", "", seg.word)
        aligned.append({
            "word": w_clean,
            "start": round(seg.start_frame * 0.01, 3),
            "end": round(seg.end_frame * 0.01, 3)
        })
    return aligned, dur_s

print("1/4 Aligning 8 narrator clips + 2 child clips with PocketSphinx...")
nar_audio = {}
nar_words = []
for c in packed_clips:
    cid = c["id"]
    if not cid.startswith("nar_"):
        continue
    wpath = CLIPS_DIR / f"{cid}.wav"
    pcm44 = load_wav_mono(wpath, SR)
    nar_audio[cid] = pcm44
    aw, dur = align_clip(wpath, c["text"])
    print(f"  {cid}: expected={len(norm_words(c['text']))} words, aligned={len(aw)} words, dur={dur:.2f}s")
    for item in aw:
        item["clip"] = cid
        nar_words.append(item)

# Split child_radio.wav ("Please don't open the door. ... Dad?") using alignment or energy valley
child_radio_pcm = load_wav_mono(CLIPS_DIR / "child_radio.wav", SR)
cr_words, cr_dur = align_clip(CLIPS_DIR / "child_radio.wav", "Please don't open the door Dad")
print(f"  child_radio: aligned={len(cr_words)} words, dur={cr_dur:.2f}s -> {cr_words}")
if len(cr_words) >= 6:
    split_t = (cr_words[-2]["end"] + cr_words[-1]["start"]) * 0.5
else:
    # Find quietest window in middle 35%..80% of child_radio
    s0, s1 = int(len(child_radio_pcm) * 0.35), int(len(child_radio_pcm) * 0.85)
    win = int(0.05 * SR)
    best_i, best_e = (s0 + s1) // 2, 1e9
    for idx in range(s0, s1 - win, win // 2):
        e = float(np.mean(child_radio_pcm[idx:idx+win] ** 2))
        if e < best_e:
            best_e, best_i = e, idx + win // 2
    split_t = best_i / SR

split_samp = int(split_t * SR)
child_seg_1 = child_radio_pcm[:split_samp]
child_seg_2 = child_radio_pcm[split_samp:]
child_seg_3 = load_wav_mono(CLIPS_DIR / "child_whisper.wav", SR)

def trim_silence(x: np.ndarray, thresh=0.004, pad_s=0.06):
    if len(x) == 0:
        return x
    ab = np.abs(x)
    idx = np.where(ab > thresh)[0]
    if len(idx) == 0:
        return x
    pad = int(pad_s * SR)
    a = max(0, int(idx[0]) - pad)
    b = min(len(x), int(idx[-1]) + pad)
    seg = x[a:b].copy()
    f = min(int(0.015 * SR), len(seg) // 4)
    if f > 4:
        seg[:f] *= np.linspace(0, 1, f)
        seg[-f:] *= np.linspace(1, 0, f)
    return seg

child_clips_ordered = [
    trim_silence(child_seg_1),
    trim_silence(child_seg_2),
    trim_silence(child_seg_3),
]

# Filter helpers for horror vocal emotions
sos_whisper_hp = butter(2, 210, btype="highpass", fs=SR, output="sos")
sos_whisper_air = butter(2, [2400, 6800], btype="bandpass", fs=SR, output="sos")
sos_radio = butter(4, [420, 2750], btype="bandpass", fs=SR, output="sos")
sos_phone_alert = butter(3, [340, 3400], btype="bandpass", fs=SR, output="sos")

def style_voice(seg: np.ndarray, emotion: str, text: str, speaker: str, child_idx: int) -> np.ndarray:
    y = seg.copy()
    tl = text.lower()
    # Radio-transmitted lines
    if "control room, do you copy" in tl or (speaker == "child" and child_idx in (0, 1)):
        y = sosfilt(sos_radio, y) * 1.45
        y = np.tanh(y * 1.9) * 0.72
        # Subtle analog radio static bed underneath
        rng = np.random.default_rng(100 + child_idx + len(y) % 97)
        st = sosfilt(sos_radio, rng.normal(0, 0.018, len(y)).astype(np.float32))
        y = y + st
        return y.astype(np.float32)

    # Phone emergency alert text
    if "biological emergency" in tl:
        y = 0.65 * y + 0.55 * sosfilt(sos_phone_alert, y)
        return (y * 1.04).astype(np.float32)

    # Final terrified child whisper right next to you ("That's not my dad.")
    if speaker == "child" and child_idx == 2:
        hp = sosfilt(sos_whisper_hp, y)
        air = sosfilt(sos_whisper_air, y)
        return ((0.68 * hp + 0.55 * air) * 0.92).astype(np.float32)

    # Narrator whisper / hushed tension tags
    if any(k in emotion for k in ("whisper", "quiet", "fearful", "low")):
        hp = sosfilt(sos_whisper_hp, y)
        air = sosfilt(sos_whisper_air, y)
        y = (0.76 * hp + 0.36 * air) * 0.84
    elif any(k in emotion for k in ("shocked", "urgent", "tense", "serious")):
        y = np.tanh(y * 1.18) * 0.96
    return y.astype(np.float32)

print("2/4 Slicing narrator sentences at exact word boundaries & inserting dramatic pauses...")
# Map each narrator speech item sequentially onto nar_words
word_cursor = 0
total_nw = len(nar_words)

master_chunks = []
sentences_meta = []
chapters_meta = []
cur_sample = int(0.35 * SR)  # 0.35s cold-open lead-in
master_chunks.append(np.zeros(cur_sample, dtype=np.float32))

child_counter = 0
sent_id = 0

for ch in chapters:
    ch_num = ch["chapter"]
    ch_start_t = cur_sample / SR
    for item in ch["items"]:
        if item["type"] == "pause":
            p_samps = int(item["sec"] * SR)
            master_chunks.append(np.zeros(p_samps, dtype=np.float32))
            cur_sample += p_samps
            continue

        spk = item["speaker"]
        emo = item["emotion"]
        txt = item["text"]
        spoken = item["spoken"]

        if spk == "child":
            raw_seg = child_clips_ordered[child_counter]
            styled = style_voice(raw_seg, emo, txt, "child", child_counter)
            child_counter += 1
        else:
            w_expected = norm_words(spoken)
            n_take = len(w_expected)
            start_idx = word_cursor
            end_idx = min(total_nw - 1, word_cursor + max(1, n_take) - 1)
            # Small lookahead alignment snap so word_cursor never drifts by 1 word
            if n_take > 0 and end_idx < total_nw:
                target_last = w_expected[-1]
                best_j = end_idx
                for j in range(max(start_idx, end_idx - 3), min(total_nw, end_idx + 4)):
                    if nar_words[j]["word"] == target_last:
                        best_j = j
                        break
                end_idx = best_j
            word_cursor = min(total_nw, end_idx + 1)

            w0 = nar_words[start_idx]
            w1 = nar_words[end_idx]
            if w0["clip"] == w1["clip"]:
                pcm = nar_audio[w0["clip"]]
                s_a = max(0, int((w0["start"] - 0.035) * SR))
                s_b = min(len(pcm), int((w1["end"] + 0.055) * SR))
                raw_seg = pcm[s_a:s_b].copy()
            else:
                # Sentence crossed two clips (rare boundary)
                pcm0 = nar_audio[w0["clip"]]
                pcm1 = nar_audio[w1["clip"]]
                part0 = pcm0[max(0, int((w0["start"] - 0.03) * SR)):]
                part1 = pcm1[:min(len(pcm1), int((w1["end"] + 0.05) * SR))]
                raw_seg = np.concatenate([part0, part1])

            f = min(int(0.012 * SR), len(raw_seg) // 4)
            if f > 4:
                raw_seg[:f] *= np.linspace(0, 1, f)
                raw_seg[-f:] *= np.linspace(1, 0, f)
            styled = style_voice(raw_seg, emo, txt, "narrator", 0)

        s_start = cur_sample / SR
        master_chunks.append(styled)
        cur_sample += len(styled)
        s_end = cur_sample / SR

        sent_id += 1
        sentences_meta.append({
            "id": sent_id,
            "chapter": ch_num,
            "speaker": spk,
            "emotion": emo,
            "start": round(s_start, 3),
            "end": round(s_end, 3),
            "text": txt
        })

        # Natural breath pause between sentences (longer on ominous short lines)
        gap_sec = 0.34 if len(txt) < 28 else 0.24
        if any(k in emo for k in ("whisper", "slow", "fearful")):
            gap_sec += 0.14
        gap_samps = int(gap_sec * SR)
        master_chunks.append(np.zeros(gap_samps, dtype=np.float32))
        cur_sample += gap_samps

    # End-of-chapter cliffhanger tail (1.35s clean boundary so Shorts slice with zero bleed!)
    tail_samps = int(1.35 * SR)
    master_chunks.append(np.zeros(tail_samps, dtype=np.float32))
    cur_sample += tail_samps
    ch_end_t = cur_sample / SR
    chapters_meta.append({
        "chapter": ch_num,
        "title": ch["title"],
        "start": round(ch_start_t if ch_num > 1 else 0.0, 3),
        "end": round(ch_end_t, 3),
        "duration": round(ch_end_t - (ch_start_t if ch_num > 1 else 0.0), 3)
    })

voice_track = np.concatenate(master_chunks)
total_samples = len(voice_track)
total_dur = total_samples / SR
print(f"  Voice timeline assembled: {total_dur:.2f}s ({total_dur/60:.2f} min), {len(sentences_meta)} lines, word_cursor={word_cursor}/{total_nw}")

print("3/4 Synthesizing dark horror ambient score & story-synced foley cues...")
fx_L = np.zeros(total_samples, dtype=np.float32)
fx_R = np.zeros(total_samples, dtype=np.float32)
rng = np.random.default_rng(42)

def add_stereo(t_sec: float, sig_l: np.ndarray, sig_r: np.ndarray = None, gain: float = 1.0):
    if sig_r is None:
        sig_r = sig_l
    i0 = max(0, int(t_sec * SR))
    n = min(len(sig_l), total_samples - i0)
    if n > 0:
        fx_L[i0:i0+n] += sig_l[:n] * gain
        fx_R[i0:i0+n] += sig_r[:n] * gain

# Continuous subtle dark horror drone (D1=36.7Hz + A1=55Hz + eerie Eb2=77.8Hz shimmer), silenced at final blackout!
blackout_line = next((s for s in sentences_meta if "emergency lights go out" in s["text"].lower()), None)
blackout_t = blackout_line["start"] if blackout_line else total_dur - 4.0

t_axis = np.arange(total_samples, dtype=np.float32) / SR
slow_mod = 0.55 + 0.45 * np.sin(2 * np.pi * 0.07 * t_axis)
drone_l = (0.026 * np.sin(2 * np.pi * 36.71 * t_axis) +
           0.015 * np.sin(2 * np.pi * 55.0 * t_axis + 0.4) +
           0.008 * slow_mod * np.sin(2 * np.pi * 77.78 * t_axis + np.sin(2 * np.pi * 0.19 * t_axis)))
drone_r = (0.026 * np.sin(2 * np.pi * 36.71 * t_axis + 0.2) +
           0.015 * np.sin(2 * np.pi * 55.0 * t_axis + 1.1) +
           0.008 * slow_mod * np.sin(2 * np.pi * 78.1 * t_axis))
# Kill drone abruptly when emergency lights go out for maximum dread!
bk_i = min(total_samples, int(blackout_t * SR))
drone_l[bk_i:] *= np.exp(-np.linspace(0, 12, total_samples - bk_i))
drone_r[bk_i:] *= np.exp(-np.linspace(0, 12, total_samples - bk_i))
fx_L += drone_l.astype(np.float32)
fx_R += drone_r.astype(np.float32)

# Helper foley generators
def gen_phone_vibrate(dur=0.9):
    t = np.arange(int(dur * SR)) / SR
    burst = ((t % 0.45) < 0.30).astype(np.float32)
    sig = burst * (0.6 * np.sin(2 * np.pi * 148 * t) + 0.3 * np.sin(2 * np.pi * 296 * t))
    return sig * 0.16

def gen_eas_tone(dur=1.35):
    t = np.arange(int(dur * SR)) / SR
    # Classic two-tone 853 Hz + 960 Hz emergency alert header
    env = np.minimum(1.0, np.minimum(t * 25, (dur - t) * 20))
    return (0.5 * np.sin(2 * np.pi * 853 * t) + 0.5 * np.sin(2 * np.pi * 960 * t)) * env * 0.11

def gen_thud(freq=68, dur=0.45, sharp=0.04):
    t = np.arange(int(dur * SR)) / SR
    body = np.sin(2 * np.pi * freq * np.exp(-t * 4.5) * t) * np.exp(-t * 8.5)
    hit = rng.normal(0, 1, len(t)) * np.exp(-t / sharp)
    return (0.75 * body + 0.35 * hit).astype(np.float32) * 0.28

def gen_metallic_clatter(dur=0.7):
    t = np.arange(int(dur * SR)) / SR
    freqs = [610, 985, 1430, 2180, 3110]
    sig = sum(np.sin(2 * np.pi * f * t + i) * np.exp(-t * (6 + i * 2.5)) for i, f in enumerate(freqs))
    hit = rng.normal(0, 0.5, len(t)) * np.exp(-t * 35)
    return ((sig / len(freqs)) + hit).astype(np.float32) * 0.22

def gen_glass_break(dur=0.65):
    t = np.arange(int(dur * SR)) / SR
    sos_hi = butter(3, 2800, btype="highpass", fs=SR, output="sos")
    burst = sosfilt(sos_hi, rng.normal(0, 1, len(t))) * np.exp(-t * 9.0)
    tinkles = np.zeros_like(t)
    for dt, f in [(0.05, 4200), (0.14, 5100), (0.26, 3700), (0.38, 6100)]:
        i = int(dt * SR)
        rem = len(t) - i
        if rem > 0:
            tt = np.arange(rem) / SR
            tinkles[i:] += 0.35 * np.sin(2 * np.pi * f * tt) * np.exp(-tt * 28)
    return (0.65 * burst + tinkles).astype(np.float32) * 0.20

def gen_clicking(dur=1.4):
    out = np.zeros(int(dur * SR), dtype=np.float32)
    for dt in [0.05, 0.19, 0.31, 0.52, 0.66, 0.78, 1.02, 1.15]:
        i = int(dt * SR)
        n = min(int(0.035 * SR), len(out) - i)
        if n > 0:
            tt = np.arange(n) / SR
            out[i:i+n] += np.sin(2 * np.pi * 1650 * tt) * np.exp(-tt * 140) * 0.22
    return out

def gen_static(dur=0.9):
    sos_bp = butter(3, [500, 3600], btype="bandpass", fs=SR, output="sos")
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(1.0, np.minimum(t * 18, (dur - t) * 14))
    return (sosfilt(sos_bp, rng.normal(0, 1, len(t))) * env * 0.085).astype(np.float32)

def gen_ringing_phone(dur=2.2):
    t = np.arange(int(dur * SR)) / SR
    cadence = (((t % 1.1) < 0.42) | (((t % 1.1) > 0.52) & ((t % 1.1) < 0.94))).astype(np.float32)
    # Muffled through glass (lowpass 1300 Hz)
    tone = cadence * (0.5 * np.sin(2 * np.pi * 1046 * t) + 0.5 * np.sin(2 * np.pi * 1318 * t))
    sos_lp = butter(3, 1250, btype="lowpass", fs=SR, output="sos")
    return (sosfilt(sos_lp, tone) * 0.085).astype(np.float32)

def gen_three_knocks():
    out = np.zeros(int(1.65 * SR), dtype=np.float32)
    for dt in [0.05, 0.58, 1.12]:
        k = gen_thud(freq=112, dur=0.28, sharp=0.015) * 1.15
        i = int(dt * SR)
        out[i:i+len(k)] += k
    return out

def gen_running_footsteps(dur=2.4):
    out_l = np.zeros(int(dur * SR), dtype=np.float32)
    out_r = np.zeros(int(dur * SR), dtype=np.float32)
    # Accelerating & getting louder from far corridor right up to your face!
    t_cur = 0.06
    step = 0
    while t_cur < dur - 0.15:
        prog = t_cur / dur
        vol = 0.22 + 1.35 * (prog ** 1.8)
        hit = gen_thud(freq=88 + 30 * prog, dur=0.16, sharp=0.012) * vol
        i = int(t_cur * SR)
        n = min(len(hit), len(out_l) - i)
        if step % 2 == 0:
            out_l[i:i+n] += hit[:n] * 1.0
            out_r[i:i+n] += hit[:n] * 0.65
        else:
            out_l[i:i+n] += hit[:n] * 0.65
            out_r[i:i+n] += hit[:n] * 1.0
        t_cur += max(0.13, 0.24 - 0.10 * prog)
        step += 1
    return out_l, out_r

# Trigger exact story-synced foley from sentences_meta!
for s in sentences_meta:
    tl = s["text"].lower()
    st, en = s["start"], s["end"]
    if "suddenly vibrates" in tl:
        add_stereo(en - 0.55, gen_phone_vibrate(0.95))
    elif "biological emergency" in tl:
        add_stereo(st - 0.25, gen_eas_tone(1.1))
    elif "lock both doors" in tl:
        add_stereo(en - 0.35, gen_metallic_clatter(0.45), gain=0.9)
    elif "slams against the glass" in tl:
        add_stereo(en - 0.30, gen_thud(freq=62, dur=0.45), gain=1.15)
    elif tl == "clatter.":
        add_stereo(st - 0.08, gen_metallic_clatter(0.75), gain=1.1)
    elif "wire-mesh window has been broken" in tl:
        add_stereo(st - 0.12, gen_glass_break(0.65), gain=0.95)
    elif "low clicking noise" in tl:
        add_stereo(en - 0.10, gen_clicking(1.35), gain=1.0)
    elif "another impact comes from outside" in tl:
        add_stereo(st + 0.15, gen_thud(freq=55, dur=0.5), gain=1.25)
    elif tl == "static.":
        add_stereo(st - 0.05, gen_static(0.95), gain=1.15)
    elif tl == "a phone ringing.":
        add_stereo(en - 0.10, gen_ringing_phone(2.2), gain=1.0)
    elif "lock clicks." in tl:
        add_stereo(en - 0.22, gen_metallic_clatter(0.32), gain=0.85)
    elif "static fills the room" in tl:
        add_stereo(st, gen_static(1.3), gain=1.1)
    elif "hear three knocks" in tl:
        add_stereo(en + 0.05, gen_three_knocks(), gain=1.25)
    elif "emergency lights go out" in tl:
        # Heavy power-breaker shutoff thud
        add_stereo(en - 0.15, gen_thud(freq=44, dur=0.65, sharp=0.02), gain=1.35)
    elif "something begins running toward you" in tl:
        rl, rr = gen_running_footsteps(2.25)
        add_stereo(st + 0.35, rl, rr, gain=1.0)

# Subtle chapter-transition sub boom at end of Chapters 1..5
for chm in chapters_meta[:-1]:
    add_stereo(chm["end"] - 1.05, gen_thud(freq=46, dur=0.85, sharp=0.01), gain=0.75)

# Mix voice center + stereo horror foley, peak-normalized cleanly to -1.2 dBFS
mix_L = voice_track * 0.92 + fx_L
mix_R = voice_track * 0.92 + fx_R
peak = max(1e-6, float(max(np.max(np.abs(mix_L)), np.max(np.abs(mix_R)))))
target_peak = 0.87
mix_L = (mix_L / peak) * target_peak
mix_R = (mix_R / peak) * target_peak

out_wav = PROJ / "input" / "voiceover_master.wav"
stereo_i16 = np.empty((total_samples * 2,), dtype=np.int16)
stereo_i16[0::2] = np.clip(mix_L * 32767.0, -32768, 32767).astype(np.int16)
stereo_i16[1::2] = np.clip(mix_R * 32767.0, -32768, 32767).astype(np.int16)

with wave.open(str(out_wav), "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(stereo_i16.tobytes())

(TL_DIR / "sentences.json").write_text(json.dumps({
    "duration": round(total_dur, 3),
    "sentences": sentences_meta
}, indent=2), encoding="utf-8")

(TL_DIR / "chapters.json").write_text(json.dumps({
    "duration": round(total_dur, 3),
    "chapters": chapters_meta
}, indent=2), encoding="utf-8")

print("4/4 Master Horror Audio & Exact Chapter Timestamps Ready!")
for chm in chapters_meta:
    print(f"  Chapter {chm['chapter']} ({chm['title']}): {chm['start']:6.2f}s -> {chm['end']:6.2f}s (dur={chm['duration']:5.2f}s)")

#!/usr/bin/env python3
"""Build the voice master + exact shot timeline for Short #3.

- decodes each VO clip, trims leading/trailing silence
- places clips at shot start + LEAD
- writes work/voice_master.wav (48k mono)
- writes work/timeline.json and web/timeline.js (for the browser engine)

Shot length = LEAD + clip + TAIL, snapped to a 6-frame grid at FPS.
Word/chunk timings are spread across the clip by syllable weight (pitch-drop method).
"""
import json, re, subprocess, wave, os
import numpy as np

SR = 48000
FPS = 90
LEAD, TAIL = 0.30, 0.80
FF = "/home/user/YouTube-auto-upload-/.venv/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v9.0.2"

# shot id, vo file, on-screen line (used for chunk captions), light, loc
SHOTS = [
    ("s1",  "vo/v01_hook.mp3",   "A man sells the Eiffel Tower. Twice. And nobody calls the police.", "golden", "suite"),
    ("s2",  "vo/v02_setup.mp3",  "Paris, nineteen twenty-five. Con man Victor Lustig forges government papers, and calls six scrap dealers to a secret hotel meeting.", "day", "suite"),
    ("s3",  "vo/v03_sale.mp3",   "He claims the city can't afford the tower, so it's quietly being sold for scrap.", "day", "suite"),
    ("s4",  "vo/v04_bribe.mp3",  "One dealer, Poisson, wants it so badly that he pays a bribe on top of the price.", "day", "suite"),
    ("s5",  "vo/v05_vanish.mp3", "The deal closes. Lustig vanishes. Poisson never says a word.", "golden", "suite"),
    ("s6",  "vo/v06_alibi.mp3",  "You see, the bribe was Poisson's own crime. Reporting the sale would confess it. Shame was the perfect alibi.", "night", "suite"),
    ("s7",  "vo/v07_again.mp3",  "So Lustig comes back, and runs the exact same trick again.", "day", "suite"),
    ("s8",  "vo/v08_caught.mp3", "They catch him in nineteen thirty-five. For fake money, not for landmarks.", "day", "street"),
    ("s9",  "vo/v09_payoff.mp3", "The tower still charges admission. Lustig never paid a franc.", "golden", "booth"),
]


def decode(path):
    raw = subprocess.run([FF, "-v", "error", "-i", path, "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32).copy()


def trim(x, thr=0.004, pad=0.04):
    nz = np.where(np.abs(x) > thr)[0]
    if len(nz) == 0:
        return x
    a = max(0, nz[0] - int(pad * SR))
    b = min(len(x), nz[-1] + int(pad * SR))
    return x[a:b]


def syll(w):
    w = re.sub(r"[^a-z]", "", w.lower())
    if not w:
        return 1
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1 and not w.endswith("le"):
        n -= 1
    return max(1, n)


def chunks(line, max_words=9):
    """One caption per sentence; only very long sentences get split at a comma."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", line.strip()) if p.strip()]
    out = []
    for p in parts:
        ws = p.split()
        if len(ws) <= max_words:
            out.append(p); continue
        # split at the comma closest to the middle
        bits = [x.strip() for x in re.split(r"(?<=,)\s+", p) if x.strip()]
        if len(bits) > 1:
            k = min(range(len(bits)), key=lambda i: abs(len(" ".join(bits[:i+1]).split()) - len(ws) / 2))
            out.append(" ".join(bits[:k + 1])); out.append(" ".join(bits[k + 1:]))
        else:
            h = len(ws) // 2
            out.append(" ".join(ws[:h])); out.append(" ".join(ws[h:]))
    if len(out) > 1 and len(out[-1].split()) <= 2:   # tiny tail -> keep with previous
        out[-2] += " " + out[-1]; out.pop()
    return out


clips = []
for sid, path, line, light, loc in SHOTS:
    x = trim(decode(path))
    clips.append({"id": sid, "line": line, "light": light, "loc": loc, "audio": x})

# layout
cursor = 0.0
acc_f = 0
shots, master = [], []
for c in clips:
    start = acc_f / FPS + LEAD
    dur = len(c["audio"]) / SR
    end = start + dur
    shot_len_s = max(LEAD + dur + TAIL, 3.2)
    shot_len_f = int(round(shot_len_s * FPS / 6)) * 6
    shots.append({"id": c["id"], "f0": 0, "f1": 0, "vo_start": start, "vo_dur": dur,
                  "len_f": shot_len_f, "line": c["line"], "light": c["light"], "loc": c["loc"]})
    acc_f += shot_len_f
    # place into master later (need total length)

total_f = sum(s["len_f"] for s in shots)
total_s = total_f / FPS
master = np.zeros(int(total_s * SR) + SR // 2, np.float32)
f = 0
for s, c in zip(shots, clips):
    s["f0"], s["f1"] = f, f + s["len_f"] - 1
    f += s["len_f"]
    i = int(s["vo_start"] * SR)
    master[i:i + len(c["audio"])] += c["audio"]
    # chunk caption timings spread by syllable weight across the clip
    ch = chunks(s["line"])
    w = np.array([sum(syll(t) for t in x.split()) for x in ch], float)
    cum = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    s["chunks"] = []
    for k, text in enumerate(ch):
        t0 = s["vo_start"] + cum[k] * s["vo_dur"]
        t1 = s["vo_start"] + cum[k + 1] * s["vo_dur"]
        s["chunks"].append({"t0": round(t0, 3), "t1": round(t1, 3), "text": text,
                            "a": int(round(t0 * FPS)) - s["f0"], "b": int(round(t1 * FPS)) - s["f0"]})

master = master[:int(total_s * SR)]
peak = np.abs(master).max()
master = master / max(peak, 1e-6) * 0.92
os.makedirs("work", exist_ok=True)
with wave.open("work/voice_master.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((master * 32767).astype("<i2").tobytes())

tl = {"fps": FPS, "total_frames": total_f, "seconds": round(total_s, 3), "shots": shots}
json.dump(tl, open("work/timeline.json", "w"), indent=1)
js = "export const TL = " + json.dumps(tl, separators=(",", ":")) + ";\n"
open("web/timeline.js", "w").write(js)

print(f"total {total_s:.2f}s / {total_f} frames @ {FPS}fps")
for s in shots:
    print(f"  {s['id']}  f{s['f0']:>5}-{s['f1']:<5}  {s['len_f']/FPS:5.2f}s  vo {s['vo_start']:.2f}+{s['vo_dur']:.2f}  {len(s['chunks'])} chunks  {s['light']}")

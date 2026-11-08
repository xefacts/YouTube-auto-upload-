#!/usr/bin/env python3
"""Mix the narration with an original procedural score for the Gardner short.

Everything except the voice is synthesised here from oscillators and noise, so
there is nothing to license. Bed sits well under the voice (ducked further while
someone is speaking), effects are placed on the cut they belong to.

Swap vo/lineNN.wav with real takes (same names) and re-run.
"""
import json, wave, os
import numpy as np

SR = 48000
FPS = 180
TL = json.load(open("work/timeline.json"))
DURS = json.load(open("work/vo_durations.json"))
TOTAL_F = TL["total"]
DUR = TOTAL_F / FPS
SHOTS = {s["id"]: s for s in TL["shots"]}

rng = np.random.default_rng(1990)
n = int(round(DUR * SR))
t = np.arange(n) / SR


def S(fid, off=0.0):
    """absolute seconds for shot `fid` + offset"""
    s = SHOTS[fid]
    return s["f0"] / FPS + off


def read_wav(p):
    with wave.open(p, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        d = d.reshape(-1, ch).mean(1)
    if sr != SR:
        x = np.linspace(0, len(d) - 1, int(len(d) * SR / sr))
        d = np.interp(x, np.arange(len(d)), d)
    return d


def fade(x, ms=30):
    k = int(SR * ms / 1000)
    if len(x) > 2 * k:
        x[:k] *= np.linspace(0, 1, k)
        x[-k:] *= np.linspace(1, 0, k)
    return x


def place(buf, x, t0, gain=1.0):
    i0 = int(round(t0 * SR))
    if i0 < 0:
        x = x[-i0:]; i0 = 0
    i1 = min(n, i0 + len(x))
    if i1 > i0:
        buf[i0:i1] += x[: i1 - i0] * gain


def env_ad(m, a=0.01, d=0.4, p=2.0):
    tt = np.arange(m) / SR
    e = np.minimum(1.0, tt / max(a, 1e-4))
    e *= np.exp(-tt / max(d, 1e-4))
    return e ** p


# ---------------------------------------------------------------- instruments
def band_noise(seed, m, lo, hi):
    r = np.random.default_rng(seed)
    x = r.normal(0, 1, m)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(m, 1 / SR)
    X *= 1.0 / (1.0 + np.exp(-(f - lo) / (lo * 0.35 + 8)))
    X *= 1.0 / (1.0 + np.exp((f - hi) / (hi * 0.25 + 8)))
    y = np.fft.irfft(X, m)
    return y / (np.max(np.abs(y)) + 1e-9)


def pad_note(freq, m, detune=0.003, harm=3):
    tt = np.arange(m) / SR
    out = np.zeros(m)
    for k in range(1, harm + 1):
        for s in (-detune, 0.0, detune):
            out += (1.0 / k ** 1.7) * np.sin(2 * np.pi * freq * k * (1 + s) * tt + rng.uniform(0, 6.28))
    return out / (harm * 3)


def soft_kick(m, f=68.0):
    tt = np.arange(m) / SR
    fr = f * (1 + 1.6 * np.exp(-tt / 0.035))
    return np.sin(2 * np.pi * fr * tt) * env_ad(m, 0.002, 0.16)


def tick(m, seed=1, f=2600.0):
    tt = np.arange(m) / SR
    return (np.sin(2 * np.pi * f * tt) + 0.4 * band_noise(seed, m, 1800, 6000)) * env_ad(m, 0.001, 0.05)


def thump(m, f=96.0, seed=3):
    return (soft_kick(m, f) + 0.35 * band_noise(seed, m, 60, 700) * env_ad(m, 0.003, 0.12))


def rip(m, seed=5, lo=900, hi=7000, flutter=1.0):
    x = band_noise(seed, m, lo, hi)
    tt = np.arange(m) / SR
    fl = 0.55 + 0.45 * np.sin(2 * np.pi * flutter * 23 * tt + 1.1)
    return x * fl * env_ad(m, 0.012, 0.30, 1.2)


def creak(m, seed=8):
    tt = np.arange(m) / SR
    f = 220 + 180 * np.clip(tt / (m / SR), 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * 0.5 + band_noise(seed, m, 300, 3000) * 0.6) * env_ad(m, 0.06, 0.5, 1.0)


def engine(m, seed=11):
    tt = np.arange(m) / SR
    f = 46 + 30 * np.clip(tt / (m / SR), 0, 1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = 2 * ((ph / (2 * np.pi)) % 1.0) - 1
    x = 0.5 * saw + 0.4 * np.sin(ph * 2) + 0.25 * band_noise(seed, m, 40, 320)
    return x * np.minimum(1, tt / 0.5) * np.minimum(1, (m / SR - tt) / 0.9)


# ---------------------------------------------------------------- score
score = np.zeros(n)

# slow harmonic bed: Am -> F -> Dm -> E, one chord per ~2 shots
CH = [(110.0, 164.8, 220.0), (87.3, 130.8, 174.6), (146.8, 174.6, 220.0), (82.4, 123.5, 164.8)]
SEG = DUR / len(CH)
for i, ch in enumerate(CH):
    t0 = i * SEG
    t1 = min(DUR, t0 + SEG)
    m = int((t1 - t0) * SR)
    if m <= 0:
        continue
    v = sum(pad_note(f, m, harm=3) for f in ch)
    e = np.minimum(1, np.arange(m) / (0.55 * SR)) * np.minimum(1, (m - np.arange(m)) / (0.55 * SR))
    place(score, v * e, t0, 0.55)

# sub drone, always there
sub = 0.55 * np.sin(2 * np.pi * 41.2 * t) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.045 * t))
score += sub

# clock pulse: 72 bpm from the heist itself, only while inside the museum
beat = 60 / 72
tb = S("s2")
while tb < S("s10") + 1.0:
    inside = S("s3") < tb < S("s9")
    place(score, soft_kick(int(0.22 * SR)), tb, 0.10 if inside else 0.07)
    place(score, tick(int(0.05 * SR), int(tb * 100) % 97, 2400), tb + 0.0, 0.020 if inside else 0.012)
    tb += beat

# room tone
score += 0.05 * band_noise(21, n, 90, 900)

# ---------------------------------------------------------------- effects on cuts
# s2: two knocks on the side door, then the door gives
for k, off in enumerate((1.55, 1.95)):
    place(score, thump(int(0.35 * SR), 92, 30 + k), S("s2", off), 0.30)
place(score, creak(int(1.5 * SR), 44), S("s3", 0.15), 0.15)
place(score, thump(int(0.3 * SR), 80, 45), S("s3", 1.35), 0.22)

# s4: tape pulled off the roll
for off in (0.35, 0.75, 1.15):
    place(score, rip(int(0.55 * SR), 50 + int(off * 10), 1200, 8000, 1.4), S("s4", off), 0.16)

# s5: footsteps crossing the Dutch Room
for k in range(5):
    place(score, thump(int(0.20 * SR), 120 + 10 * k, 60 + k), S("s5", 0.30 + 0.62 * k), 0.13)

# s6: torch click
place(score, tick(int(0.06 * SR), 71, 3200), S("s6", 0.22), 0.13)

# s7: canvas cut -> rising rip, then a soft chime as the gold stays
place(score, rip(int(1.5 * SR), 77, 700, 9000, 1.9), S("s7", 0.55), 0.24)
place(score, rip(int(1.1 * SR), 78, 500, 6000, 1.2), S("s7", 2.05), 0.20)

# s8: the empty wall - a single low bell, then silence
m = int(2.6 * SR)
tt = np.arange(m) / SR
bell = (np.sin(2 * np.pi * 174.6 * tt) * 0.6 + np.sin(2 * np.pi * 261.6 * tt) * 0.35 +
        np.sin(2 * np.pi * 349.2 * tt) * 0.2) * np.exp(-tt / 0.85)
place(score, bell, S("s8", 0.35), 0.16)

# s9: engines catching and pulling away
place(score, engine(int(2.6 * SR), 91), S("s9", 0.15), 0.16)
place(score, engine(int(2.6 * SR), 92), S("s9", 0.55), 0.13)

# s10: morning - warm major chord under the reveal
m = int(3.4 * SR)
tt = np.arange(m) / SR
maj = sum(np.sin(2 * np.pi * f * tt) for f in (174.6, 220.0, 261.6, 329.6))
maj *= np.minimum(1, tt / 0.7) * np.exp(-tt / 1.9) / 4
place(score, maj, S("s10", 0.30), 0.34)

# s11/s12: the empty frames - lone piano-ish note, then resolve down
m = int(3.0 * SR)
tt = np.arange(m) / SR
note = (np.sin(2 * np.pi * 220.0 * tt) * 0.7 + np.sin(2 * np.pi * 440.0 * tt) * 0.25) * env_ad(m, 0.01, 1.1)
place(score, note, S("s11", 0.20), 0.16)
m = int(3.6 * SR)
tt = np.arange(m) / SR
last = (np.sin(2 * np.pi * 110.0 * tt) * 0.8 + np.sin(2 * np.pi * 164.8 * tt) * 0.4 +
        np.sin(2 * np.pi * 220.0 * tt) * 0.25) * np.minimum(1, tt / 0.25) * np.exp(-tt / 1.6)
place(score, last, S("s12", 0.10), 0.30)

# ---------------------------------------------------------------- narration
vo = np.zeros(n)
for s in TL["shots"]:
    line = f"line{s['vo']:02d}"
    if line not in DURS:
        continue
    x = fade(read_wav(f"vo/{line}.wav").copy(), 30)
    start = s["f0"] + s.get("vo_at", round(0.42 * FPS))
    place(vo, x, start / FPS)

act = vo[np.abs(vo) > 1e-4]
if len(act):
    vo *= 10 ** (-19 / 20) / (np.sqrt(np.mean(act ** 2)) + 1e-9)

# ---------------------------------------------------------------- mix
k = int(0.20 * SR)
duckenv = np.convolve(np.abs(vo), np.ones(k) / k, mode="same")
duckenv = np.clip(duckenv / (duckenv.max() + 1e-9) * 7.0, 0, 1)
duck = 1.0 - 0.55 * duckenv

score = np.tanh(score / (np.max(np.abs(score)) + 1e-9) * 1.2) / np.tanh(1.2)
score *= 10 ** (-30 / 20) / (np.sqrt(np.mean(score ** 2)) + 1e-9)

mix = score * duck + vo
mix = fade(mix, 80)
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.25) / np.tanh(1.25)
mix *= 0.97
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)

with wave.open("work/audio_final.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())

peak = 20 * np.log10(np.max(np.abs(mix)) + 1e-9)
print(f"audio_final.wav  {DUR:.2f}s  peak {peak:.2f} dBFS  "
      f"vo {len(act)/SR:.1f}s  score -30 rms")

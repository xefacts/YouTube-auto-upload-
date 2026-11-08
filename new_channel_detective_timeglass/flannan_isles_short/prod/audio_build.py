#!/usr/bin/env python3
"""Mix dummy VO + procedural sea/wind bed into work/audio_final.wav.

Swap vo/lineNN.wav with real takes (same names) and re-run — the mix and the
timeline both read the same durations.
"""
import json, wave, os
import numpy as np

SR = 48000
FPS = 180
TL = json.load(open("work/timeline.json"))
DURS = json.load(open("work/vo_durations.json"))
TOTAL_F = TL["total"]
DUR = TOTAL_F / FPS

rng = np.random.default_rng(7)
n = int(round(DUR * SR))
t = np.arange(n) / SR


def read_wav(p):
    with wave.open(p, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768.0
    if ch > 1:
        d = d.reshape(-1, ch).mean(1)
    if sr != SR:                                    # cheap linear resample
        x = np.linspace(0, len(d) - 1, int(len(d) * SR / sr))
        d = np.interp(x, np.arange(len(d)), d)
    return d


def fade(x, ms=30):
    k = int(SR * ms / 1000)
    if len(x) > 2 * k:
        x[:k] *= np.linspace(0, 1, k)
        x[-k:] *= np.linspace(1, 0, k)
    return x


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc = a * acc + (1 - a) * x[i]
        y[i] = acc
    return y


# ---------------- bed: layered surf + wind -------------------------------
def surf(dur, seed, lo, hi, rate, gain):
    r = np.random.default_rng(seed)
    m = int(dur * SR)
    x = r.normal(0, 1, m)
    # band-ish noise by subtracting two one-poles
    a1 = np.exp(-2 * np.pi * hi / SR)
    a2 = np.exp(-2 * np.pi * lo / SR)
    y1 = np.empty(m); y2 = np.empty(m); acc1 = acc2 = 0.0
    for i in range(m):
        acc1 = a1 * acc1 + (1 - a1) * x[i]
        acc2 = a2 * acc2 + (1 - a2) * x[i]
        y1[i] = acc1; y2[i] = acc2
    x = y2 - y1
    x /= np.max(np.abs(x)) + 1e-9
    # swell envelope: slow random surges
    k = int(rate * SR)
    env = r.normal(0, 1, max(2, m // k + 2))
    env = np.convolve(env, np.ones(3) / 3, mode="same")
    env = np.interp(np.arange(m), np.linspace(0, m, len(env)), env)
    env = 0.55 + 0.45 * np.tanh(env * 1.6)
    return x * env * gain


bed = np.zeros(n)
bed += surf(DUR, 11, 120, 1200, 1.7, 1.00)          # body of the sea
bed += surf(DUR, 12, 700, 4200, 2.6, 0.42)          # hiss / spray
wind = surf(DUR, 13, 40, 340, 0.5, 0.55)            # low wind
bed += wind

# deep drone under everything, for weight
drone = 0.10 * np.sin(2 * np.pi * 55.0 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.06 * t))
bed += drone
bed /= np.max(np.abs(bed)) + 1e-9
BED_RMS = 10 ** (-38 / 20)                          # -38 dBFS
bed *= BED_RMS / (np.sqrt(np.mean(bed ** 2)) + 1e-9)

# ---------------- VO track ------------------------------------------------
vo = np.zeros(n)
shots = TL["shots"]
for s in shots:
    line = f"line{s['vo']:02d}"
    if line not in DURS:
        continue
    x = read_wav(f"vo/{line}.wav")
    x = fade(x.copy(), 30)
    start = s["f0"] + s.get("vo_at", round(0.42 * FPS))
    i0 = int(round(start / FPS * SR))
    i1 = min(n, i0 + len(x))
    vo[i0:i1] += x[: i1 - i0]

# level the VO per line, then to -19 dBFS rms overall
VO_RMS = 10 ** (-19 / 20)
act = vo[np.abs(vo) > 1e-4]
if len(act):
    vo *= VO_RMS / (np.sqrt(np.mean(act ** 2)) + 1e-9)

# ---------------- duck the bed under the voice ---------------------------
env = np.abs(vo)
k = int(0.18 * SR)
env = np.convolve(env, np.ones(k) / k, mode="same")
env = np.clip(env / (env.max() + 1e-9) * 6.0, 0, 1)
duck = 1.0 - 0.45 * env
mix = bed * duck + vo

# a couple of accents: distant foghorn when the light dies, bell on the reveal
def horn(t0, f0, dur, gain):
    m = int(dur * SR)
    tt = np.arange(m) / SR
    s = (np.sin(2 * np.pi * f0 * tt) + 0.5 * np.sin(2 * np.pi * f0 * 2 * tt) +
         0.22 * np.sin(2 * np.pi * f0 * 3.01 * tt))
    e = np.minimum(1, tt / 0.25) * np.exp(-tt / (dur * 0.55))
    i0 = int(t0 * SR)
    i1 = min(n, i0 + m)
    mix[i0:i1] += s[: i1 - i0] * e[: i1 - i0] * gain


horn(shots[0]["f0"] / FPS + 5.1, 92, 3.4, 0.05)     # the dark light
horn(shots[1]["f0"] / FPS + 1.3, 78, 3.0, 0.035)    # relief ship in fog
horn(shots[10]["f0"] / FPS + 0.6, 110, 2.6, 0.03)   # final beat

# ---------------- master -------------------------------------------------
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
mix *= 0.98
mix = fade(mix, 60)
pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
os.makedirs("work", exist_ok=True)
with wave.open("work/audio_final.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"audio_final.wav  {DUR:.2f}s  peak {-20*np.log10(np.max(np.abs(mix))):.2f} dBFS")

#!/usr/bin/env python3
"""Music bed + SFX for Short #3, timed from work/timeline.json, mixed under the voice.

Structure follows the story: curious march -> dead stop at "Lustig vanishes" ->
clock/drone while the shame alibi is explained -> march returns for the repeat ->
siren brake for the 1935 arrest -> warm resolve under the payoff.

Output: work/mix_raw.wav (48k stereo, music/SFX ~ -6 dB vs gated voice RMS)
"""
import json, wave, numpy as np

SR = 48000
rng = np.random.default_rng(1925)
T = json.load(open("work/timeline.json"))
DUR = T["total_frames"] / T["fps"]
N = int(DUR * SR) + SR // 10
S = {s["id"]: s for s in T["shots"]}
f2t = lambda f: f / T["fps"]

music = np.zeros(N, np.float32)
sfx = np.zeros(N, np.float32)


def place(buf, sig, t0, gain=1.0):
    i = int(max(0.0, t0) * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += sig[: j - i] * gain


def env(n, a=0.005, d=0.25, sus=0.0, r=0.05):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    e *= np.exp(-np.maximum(0, t - a) / max(d, 1e-4)) * (1 - sus) + sus
    if r > 0:
        k = int(min(n, r * SR))
        if k:
            e[-k:] *= np.linspace(1, 0, k)
    return e.astype(np.float32)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def pluck(f, dur=0.38, bright=0.5):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = sum((bright ** k) * np.sin(2 * np.pi * f * (k + 1) * t) / (k + 1) for k in range(6))
    return (s * env(n, 0.003, dur * 0.33, 0.0, 0.02)).astype(np.float32)


def brass(fs, dur, cut=1700):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for f in fs:
        ph = 2 * np.pi * f * t + 0.004 * np.sin(2 * np.pi * 5.2 * t)
        s += sum(np.sin((k + 1) * ph) / (k + 1) ** 1.3 for k in range(7))
    a = np.minimum(1, t / 0.09) * np.clip((dur - t) / 0.18, 0, 1)
    y = (s * a).astype(np.float32) / max(1, len(fs))
    X = np.fft.rfft(y)
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    X *= 1 / (1 + (fr / cut) ** 3)
    return np.fft.irfft(X, len(y)).astype(np.float32)


def kick(amp=1.0):
    n = int(0.30 * SR)
    t = np.arange(n) / SR
    f = 52 + 96 * np.exp(-t * 32)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9.5) * amp).astype(np.float32)


def snare(amp=1.0):
    n = int(0.19 * SR)
    t = np.arange(n) / SR
    s = rng.standard_normal(n) * np.exp(-t * 30) * 0.55 + np.sin(2 * np.pi * 196 * t) * np.exp(-t * 22) * 0.45
    y = s.astype(np.float32) * amp
    X = np.fft.rfft(y)
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    X *= 1 - 1 / (1 + (fr / 260) ** 4)     # high-pass
    return np.fft.irfft(X, len(y)).astype(np.float32)


def pad(fs, dur, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n, np.float32)
    for f in fs:
        for det in (-0.12, 0.0, 0.13):
            s += np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
    e = np.minimum(1, t / 0.5) * np.clip((dur - t) / 0.7, 0, 1)
    return (s / (len(fs) * 3) * e * amp).astype(np.float32)


def noise_hit(dur=0.5, cut=2600, curve=14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = (rng.standard_normal(n) * np.exp(-t * curve)).astype(np.float32)
    X = np.fft.rfft(y)
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    X *= 1 / (1 + (fr / cut) ** 3) * (1 - 1 / (1 + (fr / 180) ** 3))
    return np.fft.irfft(X, len(y)).astype(np.float32)


def whoosh(dur=0.55, up=True):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = rng.standard_normal(n).astype(np.float32)
    X = np.fft.rfft(y)
    fr = np.fft.rfftfreq(len(y), 1 / SR)
    X *= 1 / (1 + (fr / 1400) ** 2.5) * (1 - 1 / (1 + (fr / 260) ** 3))
    s = np.fft.irfft(X, len(y)).astype(np.float32)
    e = (t / dur) if up else (1 - t / dur)
    return s * (e ** 2)


def tick(amp=1.0):
    n = int(0.06 * SR)
    t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 90) * amp).astype(np.float32)


def coin(amp=1.0):
    n = int(0.7 * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 2380 * t) * np.exp(-t * 9) + 0.6 * np.sin(2 * np.pi * 3180 * t) * np.exp(-t * 12)
    return (s * amp).astype(np.float32)


def door(amp=1.0):
    parts = [noise_hit(0.34, 900, 18) * 1.0, kick(0.5)[: int(0.2 * SR)]]
    out = np.zeros(int(0.62 * SR), np.float32)
    place(out, parts[0], 0.0, amp)
    place(out, parts[1], 0.02, amp * 0.7)
    place(out, noise_hit(0.2, 520, 26), 0.34, amp * 0.5)
    return out


def siren(dur=1.4, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 620 + 230 * np.sin(2 * np.pi * 1.5 * t)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.5) / SR)
    e = np.minimum(1, t / 0.15) * np.clip((dur - t) / 0.5, 0, 1)
    return (s * e * amp).astype(np.float32)


# ---------------- music ----------------
BPM = 104
beat = 60 / BPM
bar = beat * 4
prog = [(45, [57, 60, 64]), (41, [53, 57, 60]), (43, [55, 59, 62]), (40, [52, 56, 59])]

MARCH_A = (0.0, f2t(S["s5"]["f0"]))          # setup -> just before the vanish
MARCH_B = (f2t(S["s7"]["f0"]), f2t(S["s8"]["f0"]))   # he does it again
TENSE = (f2t(S["s8"]["f0"]), f2t(S["s9"]["f0"]))     # arrest
RESOLVE = (f2t(S["s9"]["f0"]), DUR + 0.4)


def march(t0, t1, energy=1.0, hats=True):
    k = 0
    while True:
        bt = t0 + k * bar
        if bt > t1 - 0.2:
            break
        root, ch = prog[k % 4]
        place(music, brass([midi(m) for m in ch], min(bar * 0.95, t1 - bt)), bt, 0.085 * energy)
        for b in range(4):
            tb = bt + b * beat
            if tb > t1 - 0.1:
                break
            place(music, kick(0.9 if b % 2 == 0 else 0.35), tb, 0.5 * energy)
            if b % 2 == 1:
                place(music, snare(0.9), tb, 0.28 * energy)
            place(music, pluck(midi(root), 0.42, 0.42), tb, 0.33 * energy)
            place(music, pluck(midi(ch[(b + k) % 3] + 12), 0.24, 0.62), tb + beat / 2, 0.12 * energy)
            if hats:
                place(music, tick(0.9), tb + beat * 0.75, 0.05 * energy)
        k += 1


march(*MARCH_A, energy=1.0)
march(*MARCH_B, energy=0.95)

# dead stop at the vanish: little brake + silence, then clock + drone
vanish = f2t(S["s5"]["f0"])
place(music, whoosh(0.5, up=False), vanish - 0.28, 0.10)
stop_end = vanish + 0.30
i0 = int(stop_end * SR)
i1 = int(f2t(S["s6"]["f0"]) * SR)
music[i0:i1] *= 0.0

# clock tick + drone under the explanation (s6)
t_clock0, t_clock1 = f2t(S["s6"]["f0"]), f2t(S["s6"]["f1"])
tt = t_clock0 + 0.2
while tt < t_clock1 - 0.4:
    place(sfx, tick(0.8), tt, 0.045)
    place(sfx, tick(0.45), tt + 0.5, 0.03)
    tt += 1.0
place(music, pad([midi(33), midi(40), midi(45)], t_clock1 - t_clock0, 0.5), t_clock0, 0.10)

# tense brake into the arrest
t0, t1 = TENSE
place(music, pad([midi(31), midi(38), midi(43)], (t1 - t0), 0.6), t0, 0.085)
place(music, whoosh(0.6, up=True), t0 - 0.1, 0.09)
for k in range(3):
    place(music, kick(1.0), t0 + 0.4 + k * 0.62, 0.30)

# warm resolve under the payoff
t0, t1 = RESOLVE
place(music, pad([midi(45), midi(52), midi(57), midi(64)], t1 - t0, 0.9), t0, 0.13)
for k, m in enumerate([57, 64, 69, 72]):
    place(music, pluck(midi(m), 1.1, 0.35), t0 + 0.55 + k * 0.42, 0.16)

# ---------------- SFX cues ----------------
place(sfx, pad([midi(40), midi(47)], 1.0, 0.9), 0.05, 0.10)          # opening sting
place(sfx, whoosh(0.7, up=True), 0.02, 0.09)
place(sfx, noise_hit(0.30, 1500, 22), f2t(S["s2"]["f0"]) + 0.02, 0.10)   # papers slap
place(sfx, noise_hit(0.22, 2200, 26), f2t(S["s2"]["f0"]) + 0.62, 0.06)   # papers slide
place(sfx, noise_hit(0.26, 1800, 24), f2t(S["s3"]["f0"]) + 0.05, 0.07)   # paper on table
# bribe: money slide + coins
bt = f2t(S["s4"]["f0"])
place(sfx, noise_hit(0.55, 2600, 9), bt + 0.75, 0.075)
for k in range(4):
    place(sfx, coin(0.5), bt + 0.95 + k * 0.09, 0.055)
# the vanish: steps + door
vt = f2t(S["s5"]["f0"])
for k in range(4):
    place(sfx, noise_hit(0.09, 700, 40), vt + 0.25 + k * 0.3, 0.06)
place(sfx, door(0.9), vt + 0.25 + 4 * 0.3, 0.10)
# 1935: siren + cuff snap
at = f2t(S["s8"]["f0"])
place(sfx, siren(1.5, 0.6), at + 0.12, 0.055)
place(sfx, noise_hit(0.30, 3400, 20), at + 1.05, 0.11)
place(sfx, kick(1.0), at + 1.05, 0.45)
# payoff: coin ding on the last word
place(sfx, coin(0.9), DUR - 1.35, 0.06)

# ---------------- duck, mix, normalise ----------------
t_all = np.arange(N) / SR
with wave.open("work/voice_master.wav", "rb") as w:
    voice = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32) / 32768.0
voice = np.pad(voice, (0, max(0, N - len(voice))))[:N]

# gated RMS of the voice decides the music/SFX level (-6 dB below voice)
win = int(0.05 * SR)
rms = np.sqrt(np.convolve(voice ** 2, np.ones(win) / win, mode="same"))
gate = rms > (np.percentile(rms[rms > 0], 35) if np.any(rms > 0) else 1e-4)
v_rms = float(np.sqrt(np.mean(voice[gate] ** 2))) if np.any(gate) else 1e-4

def bed_rms(x):
    m = np.abs(x) > 1e-4
    return float(np.sqrt(np.mean(x[m] ** 2))) if np.any(m) else 1e-4

target = v_rms / 2.0                      # −6 dB
music *= target / max(bed_rms(music), 1e-6)
sfx *= target / max(bed_rms(sfx), 1e-6)

# duck the bed a little under speech (sidechain-ish, 120 ms smoothing)
duck = np.clip(rms / (v_rms + 1e-6), 0, 1.6)
duck = np.convolve(duck, np.ones(win * 3) / (win * 3), mode="same")
duck = 1.0 - 0.42 * np.clip(duck, 0, 1)

mixL = voice * 1.0 + (music + sfx) * duck
peak = np.abs(mixL).max()
mixL = mixL / max(peak, 1e-6) * 0.89
stereo = np.stack([mixL, mixL * 0.995 + np.roll(music * duck, int(0.004 * SR)) * 0.05], axis=1)

with wave.open("work/mix_raw.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(stereo, -1, 1) * 32767).astype("<i2").tobytes())
print(f"mix_raw.wav  {DUR:.2f}s  voice_rms={v_rms:.4f}  bed target={target:.4f}")

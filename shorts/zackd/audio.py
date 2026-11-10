"""Procedural score + SFX + voiceover mix for the short.

  python audio.py --timing timing.json --vo ../out/vo --out ../out/build/mix.wav
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000


def ffmpeg() -> str:
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()


def read_wav(path):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        ch = w.getnchannels()
        data = np.frombuffer(w.readframes(n), np.int16).astype(np.float32) / 32768.0
    if ch == 2:
        data = data.reshape(-1, 2)
    else:
        data = np.repeat(data[:, None], 2, axis=1)
    return data


def decode_audio(path, tmp="/tmp/_dec.wav"):
    subprocess.run([ffmpeg(), "-y", "-i", path, "-ar", str(SR), "-ac", "2",
                    "-c:a", "pcm_s16le", tmp], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return read_wav(tmp)


def write_wav(path, x):
    x = np.clip(x, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())


# --------------------------------------------------------------------------- #
# synthesis
# --------------------------------------------------------------------------- #

def env_ad(n, attack, decay, curve=2.0):
    a = max(int(attack * SR), 1)
    d = max(int(decay * SR), 1)
    e = np.concatenate([np.linspace(0, 1, a) ** 0.6, (np.linspace(1, 0, d) ** curve)])
    if len(e) < n:
        e = np.pad(e, (0, n - len(e)))
    return e[:n]


def boom(dur=0.9, gain=0.9):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 62 * np.exp(-t * 2.2) + 34
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.4)
    click = np.random.default_rng(1).normal(0, 1, n) * np.exp(-t * 55) * 0.5
    x = (body + click) * gain
    return np.stack([x, x], 1)


def whoosh(dur=0.7, gain=0.5, up=True):
    n = int(dur * SR)
    rng = np.random.default_rng(4)
    noise = rng.normal(0, 1, n)
    # one-pole lowpass sweep
    y = np.zeros(n)
    acc = 0.0
    coef = np.linspace(0.02, 0.5, n) if up else np.linspace(0.5, 0.02, n)
    for i in range(n):
        acc += coef[i] * (noise[i] - acc)
        y[i] = acc
    e = np.linspace(0, 1, n) ** 2 if up else np.linspace(1, 0, n) ** 2
    e *= np.linspace(1, 0.0, n) ** 0.5 if up else 1.0
    x = y * e * gain * 6.0
    return np.stack([x, x], 1)


def riser(dur=1.4, gain=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 120 * (2 ** (t / dur * 2.2))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    rng = np.random.default_rng(8)
    nz = rng.normal(0, 1, n)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):
        acc += (0.05 + 0.5 * i / n) * (nz[i] - acc)
        y[i] = acc
    e = np.linspace(0, 1, n) ** 1.6
    x = (tone + y * 2.0) * e * gain
    return np.stack([x, x], 1)


def pad_chord(dur, freqs=(55.0, 82.5, 110.0, 164.8), gain=0.10):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, f in enumerate(freqs):
        for det in (-0.35, 0.0, 0.35):
            x += np.sin(2 * np.pi * (f + det) * t + k) / (k + 1.6)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.08 * t)
    e = np.minimum(1, t / 1.5) * np.minimum(1, (dur - t) / 2.0)
    x = x * lfo * e * gain / 4.0
    return np.stack([x, x], 1)


def pulse_tick(dur=0.35, gain=0.35):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 220 * np.exp(-t * 18) + 70
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 12) * gain
    return np.stack([x, x], 1)


def beep(dur=0.22, f=1760, gain=0.45):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + np.sin(2 * np.pi * f * 2 * t) * 0.2
    x = x * env_ad(n, 0.004, dur - 0.004, 2.4) * gain
    return np.stack([x, x], 1)


def place(buf, clip, at, gain=1.0):
    i = int(at * SR)
    if i >= len(buf):
        return
    n = min(len(clip), len(buf) - i)
    if n <= 0:
        return
    buf[i:i + n] += clip[:n] * gain


# --------------------------------------------------------------------------- #

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", default=os.path.join(HERE, "timing.json"))
    ap.add_argument("--vo", default=os.path.join(HERE, "..", "out", "vo"))
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "build", "mix.wav"))
    args = ap.parse_args()

    beats = json.load(open(os.path.join(HERE, "beats.json")))["beats"]
    timing = json.load(open(args.timing)) if os.path.exists(args.timing) else {}
    starts, t = [], 0.0
    for b in beats:
        d = float(timing.get(b["id"], len(b["narration"].split()) / 2.55 + 0.75))
        starts.append((b["id"], t, d))
        t += d
    total = t + 0.6
    n = int(total * SR)
    mix = np.zeros((n, 2), np.float32)

    # ---- score -------------------------------------------------------- #
    bed = pad_chord(total, gain=0.30)
    place(mix, bed, 0.0)

    for k, (bid, st, d) in enumerate(starts):
        place(mix, boom(1.0, 0.42), st, 1.0)                      # impact on cut
        if k > 0:
            place(mix, whoosh(0.55, 0.30, up=False), st - 0.45, 1.0)
            place(mix, riser(0.85, 0.14), st - 0.85, 1.0)
        # heartbeat under the beat
        for m in range(int(d / 0.62)):
            place(mix, pulse_tick(0.32, 0.10 if m % 2 else 0.16), st + 0.15 + m * 0.62)
    # terminal beep on the "beep" beat
    for k, (bid, st, d) in enumerate(starts):
        if bid == "terminal":
            place(mix, beep(0.18, 1980, 0.32), st + d * 0.62)
            place(mix, beep(0.26, 1320, 0.26), st + d * 0.78)
    # outro riser + final hit
    place(mix, riser(1.6, 0.22), total - 1.9)
    place(mix, boom(2.4, 0.55), total - 1.1)

    # ---- voiceover ---------------------------------------------------- #
    vo_gain = 1.0
    for bid, st, d in starts:
        p = os.path.join(args.vo, f"{bid}.mp3")
        if not os.path.exists(p):
            p = os.path.join(args.vo, f"{bid}.wav")
        if not os.path.exists(p):
            print("missing VO:", bid, file=sys.stderr)
            continue
        clip = decode_audio(p)
        place(mix, clip, st + 0.10, vo_gain)

    # ---- master ------------------------------------------------------- #
    rms = np.sqrt((mix ** 2).mean())
    if rms > 0:
        mix *= min(1.0, 0.14 / rms)
    mix = np.tanh(mix * 1.15) * 0.94
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    write_wav(args.out, mix)
    print(f"wrote {args.out}  {total:.2f}s  rms={rms:.3f}")


if __name__ == "__main__":
    main()

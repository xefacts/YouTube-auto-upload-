"""VO timing + SFX (from the skill's 27 original effects) + bed -> master.wav.

Each narration clip holds two sentences; the clip is split at its longest
internal pause, so every shot gets its own line and the picture follows the voice.
"""
import json
import math
import os
import subprocess
import wave

import numpy as np

import story_town as story

HERE = os.path.dirname(os.path.abspath(__file__))
FF = open("/tmp/ffpath").read().strip()
SR = 44100
VOICE = os.path.join(HERE, "voice")
OUT = os.path.join(HERE, "out")
SFX = os.path.join(HERE, "ref", "skill", "blocky-shorts", "assets", "sfx")

LEAD, SEG_GAP, CLIP_GAP, TAIL = 0.45, 0.12, 0.26, 0.9


def rd(path):
    with wave.open(path) as w:
        ch = w.getnchannels()
        d = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
        return d.reshape(-1, ch).mean(1) if ch > 1 else d


def decode(src, dst):
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i", src, "-ac", "1",
                    "-ar", str(SR), "-c:a", "pcm_s16le", dst], check=True)


def wr(path, x):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def trim(y):
    a = np.abs(y)
    idx = np.where(a > max(0.006, a.max() * 0.02))[0]
    return y[max(0, idx[0] - int(0.02 * SR)): idx[-1] + int(0.06 * SR)]


def split_at(y, k=2):
    hop = int(0.01 * SR)
    n = len(y) // hop
    e = np.array([np.abs(y[i * hop:(i + 1) * hop]).max() for i in range(n)], np.float32)
    quiet = e < max(0.012, e.max() * 0.05)
    runs, i = [], 0
    while i < n:
        if quiet[i]:
            j = i
            while j + 1 < n and quiet[j + 1]:
                j += 1
            if j - i >= 10 and i > 6 and j < n - 6:
                runs.append((j - i, i, j))
            i = j + 1
        else:
            i += 1
    runs.sort(reverse=True)
    if len(runs) >= k - 1:
        return [((a + b) // 2) * hop for _, a, b in sorted(runs[:k - 1], key=lambda r: r[1])]
    return [int(len(y) * i / k) for i in range(1, k)]


def tone(f, dur, harm=((1, 1.0),), attack=0.006, decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n, np.float32)
    for kk, amp in harm:
        x += amp * np.sin(2 * np.pi * f * kk * t)
    e = np.ones(n, np.float32)
    na = max(1, min(n, int(attack * SR)))
    e[:na] = np.linspace(0, 1, na)
    if decay:
        nd = max(1, min(n, int(decay * SR)))
        e[:nd] *= np.linspace(1, 0.0, nd) ** 1.3
    return x * e


def add(buf, x, at, gain=1.0):
    i = int(at * SR)
    if i < 0 or i >= len(buf):
        return
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n] * gain


def main():
    os.makedirs(OUT, exist_ok=True)
    clips = sorted(f for f in os.listdir(VOICE) if f.lower().endswith((".mp3", ".wav")))
    assert len(clips) == len(story.CLIPS), (len(clips), len(story.CLIPS))
    os.makedirs(os.path.join(OUT, "vdec"), exist_ok=True)
    segs = []
    for ci, name in enumerate(clips):
        dst = os.path.join(OUT, "vdec", f"c{ci}.wav")
        decode(os.path.join(VOICE, name), dst)
        y = trim(rd(dst))
        k = story.CLIPS[ci][1] - story.CLIPS[ci][0]
        cuts = [0] + split_at(y, k) + [len(y)]
        for si in range(k):
            segs.append(y[cuts[si]:cuts[si + 1]])
    plan = story.SHOTS
    assert len(segs) == len(plan), (len(segs), len(plan))

    total = LEAD + sum(len(s) / SR for s in segs) + SEG_GAP * (len(segs) - 1) + TAIL
    n = int(total * SR)
    voice = np.zeros(n, np.float32)
    shots, t = [], LEAD
    for s in segs:
        d = len(s) / SR
        add(voice, s, t)
        shots.append({"start": round(t, 4), "dur": round(d + SEG_GAP, 4)})
        t += d + SEG_GAP
    shots[-1]["dur"] = round(shots[-1]["dur"] + TAIL, 4)
    end = shots[-1]["start"] + shots[-1]["dur"]
    timing = {"fps": 30, "shots": shots, "plan": plan,
              "total": round(end + story.END_CARD["hold"], 4),
              "end_card": {"start": round(end, 4), "dur": story.END_CARD["hold"]}}
    os.makedirs(os.path.join(HERE, "story"), exist_ok=True)
    json.dump(timing, open(os.path.join(HERE, "story", "timing.json"), "w"), indent=1)
    print("speech", round(sum(len(s) / SR for s in segs), 2), "s  video", timing["total"],
          "s  frames", int(timing["total"] * 30))

    # ------------------------------------------------------------ sfx
    sfx = np.zeros(n, np.float32)
    cache = {}
    for sh, st in zip(plan, shots):
        for cue_u, name in sh.get("sfx", []):
            path = os.path.join(SFX, name + ".wav")
            if not os.path.exists(path):
                print("missing sfx", name)
                continue
            if name not in cache:
                cache[name] = rd(path)
            add(sfx, cache[name], st["start"] + cue_u * st["dur"], 0.9)

    # ------------------------------------------------------------ bed
    bed = np.zeros(n, np.float32)
    beat = 60.0 / 104.0
    bar = beat * 4
    roots = [110.0, 146.83, 130.81, 98.0]
    k = 0
    pos = 0.0
    while pos < total:
        root = roots[k % 4]
        for b in range(4):
            at = pos + b * beat
            add(bed, tone(root / 2, beat * 0.9, ((1, 0.7), (2, 0.2)), 0.01, beat * 0.7), at, 0.5)
            if b % 2 == 0:
                add(bed, tone(root * 2, 0.16, ((1, 0.5), (2, 0.22)), 0.004, 0.14), at, 0.30)
            add(bed, tone(root * 4, 0.05, ((1, 0.3),), 0.002, 0.04), at + beat * 0.5, 0.16)
        k += 1
        pos += bar

    win = int(0.05 * SR)
    env = np.convolve(np.abs(voice), np.ones(win, np.float32) / win, mode="same")
    gate = (env > env.max() * 0.05).astype(np.float32)
    duck = 1.0 - 0.55 * np.convolve(gate, np.ones(int(0.14 * SR)) / (0.14 * SR),
                                    mode="same").clip(0, 1)
    vpk = float(np.abs(voice).max()) or 1.0
    bed *= duck
    bed *= (0.20 * vpk) / (float(np.abs(bed).max()) or 1.0)
    sfx *= (0.48 * vpk) / (float(np.abs(sfx).max()) or 1.0)
    mix = voice + bed + sfx
    pk = float(np.abs(mix).max())
    if pk > 0.99:
        mix *= 0.99 / pk
    wr(os.path.join(OUT, "mix_raw.wav"), mix)
    subprocess.run([FF, "-hide_banner", "-loglevel", "error", "-y", "-i",
                    os.path.join(OUT, "mix_raw.wav"), "-af",
                    "loudnorm=I=-14:LRA=9:TP=-1.5", "-ar", str(SR),
                    os.path.join(OUT, "master.wav")], check=True)
    print("master.wav ok  voice peak", round(vpk, 3))


if __name__ == "__main__":
    main()

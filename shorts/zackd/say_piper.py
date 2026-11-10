"""Voiceover with a local, open-source neural TTS (Piper, rhasspy/piper).

No API keys, no cloud: the Piper VITS model runs on CPU through onnxruntime.

    python say_piper.py --voice en_US-ryan-medium --out ../out/vo_piper

The script reads the narration lines from ``beats.json`` and the shot windows
from ``timing.json``, then for every beat:

1. synthesises the line with Piper at a base speed,
2. measures how far it is from the shot window and re-synthesises with a
   ``--length-scale`` that fits (clamped to a natural range),
3. applies the "narrator" chain: 5 % pitch-down (formant shift, length
   compensated), high-pass, gentle compression, presence lift, short room,
4. trims / pads to exactly the shot window with a mild ``atempo``.

Output: ``<out>/<beat>.wav``, 48 kHz mono, one file per beat, same names and
durations the timeline expects - so the rendered frames stay in sync.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import wave

import imageio_ffmpeg

HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

PITCH = 0.95                 # 5 % down -> deeper, closer to a film-trailer read
LS_MIN, LS_MAX = 1.12, 1.38  # natural length-scale range for Piper VITS
ATEMPO_MIN, ATEMPO_MAX = 0.80, 1.22


def wav_dur(path: str) -> float:
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def piper(text: str, model: str, config: str, ls: float, out: str) -> None:
    subprocess.run(
        [sys.executable, "-m", "piper", "-m", model, "-c", config,
         "-f", out, "--length-scale", f"{ls:.3f}", "--sentence-silence", "0.12",
         "--", text],
        check=True, capture_output=True,
    )


def polish(src: str, dst: str, pitch: float) -> None:
    """Pitch down with formant shift, then a light broadcast chain."""
    chain = ",".join([
        f"asetrate=22050*{pitch:.4f}",
        "aresample=48000",
        f"atempo={1.0 / pitch:.4f}",
        "highpass=f=78",
        "equalizer=f=170:t=q:w=1.2:g=2.0",     # chest
        "equalizer=f=2600:t=q:w=1.6:g=1.6",     # presence
        "equalizer=f=7200:t=q:w=2.0:g=-2.0",    # tame sibilance
        "acompressor=threshold=0.11:ratio=3.4:attack=8:release=180:makeup=1.5",
        "alimiter=limit=0.92",
    ])
    subprocess.run(
        [FFMPEG, "-y", "-v", "error", "-i", src, "-af", chain,
         "-ac", "1", "-ar", "48000", dst],
        check=True,
    )


def fit(src: str, dst: str, target: float) -> float:
    """Resample-free time fit with atempo, clamped."""
    d = wav_dur(src)
    tempo = d / target
    tempo = max(ATEMPO_MIN, min(ATEMPO_MAX, tempo))
    af = f"atempo={tempo:.4f}"
    if tempo < 0.999:
        # keep a hair of tail silence so the cut never clips a consonant
        af += ",apad=pad_dur=0.05"
    subprocess.run(
        [FFMPEG, "-y", "-v", "error", "-i", src, "-af", af,
         "-t", f"{target:.3f}", "-ac", "1", "-ar", "48000", dst],
        check=True,
    )
    return tempo


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="en_US-ryan-medium")
    ap.add_argument("--models", default=os.path.join(HERE, "..", "models"))
    ap.add_argument("--beats", default=os.path.join(HERE, "beats.json"))
    ap.add_argument("--timing", default=os.path.join(HERE, "timing.json"))
    ap.add_argument("--pad", type=float, default=0.5)
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "vo_piper"))
    ap.add_argument("--tmp", default="/tmp/piper_stage")
    args = ap.parse_args()

    model = os.path.join(args.models, f"{args.voice}.onnx")
    config = model + ".json"
    if not os.path.exists(model):
        sys.exit(f"missing model {model} - see README (voices are ~60 MB, not in git)")

    beats = json.load(open(args.beats))["beats"]
    timing = json.load(open(args.timing))
    windows = timing.get("beats", timing) if isinstance(timing, dict) else timing
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.tmp, exist_ok=True)

    for b in beats:
        bid = b["id"]
        text = b["narration"]
        slot = windows[bid]["duration"] if isinstance(windows[bid], dict) else windows[bid]
        target = slot - args.pad

        raw = os.path.join(args.tmp, f"{bid}.raw.wav")
        piper(text, model, config, 1.0, raw)
        base = wav_dur(raw)
        ls = max(LS_MIN, min(LS_MAX, target / base))
        if abs(ls - 1.0) > 0.02:
            piper(text, model, config, ls, raw)
        staged = os.path.join(args.tmp, f"{bid}.stage.wav")
        polish(raw, staged, PITCH)
        out = os.path.join(args.out, f"{bid}.wav")
        tempo = fit(staged, out, target)
        print(f"{bid:9s} ls={ls:.2f} tempo={tempo:.3f} "
              f"target={target:.2f}s got={wav_dur(out):.2f}s | {text[:52]}")

    total = sum(wav_dur(os.path.join(args.out, f"{b['id']}.wav")) for b in beats)
    print(f"done -> {args.out}  speech={total:.2f}s")


if __name__ == "__main__":
    main()

"""Audio + video analysis: audio extraction, sound-event detection (SFX candidates),
scene-cut detection, keyframe stills and optional stem separation."""
from __future__ import annotations

import re
import shutil
import subprocess
import wave
from pathlib import Path

import numpy as np

from .ffmpeg import run


def extract_audio(video: Path, wav_out: Path, *, sample_rate: int = 44100) -> Path:
    wav_out.parent.mkdir(parents=True, exist_ok=True)
    run(["-i", str(video), "-vn", "-ac", "2", "-ar", str(sample_rate), "-c:a", "pcm_s16le", str(wav_out)])
    return wav_out


def read_wav_mono(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as w:
        sr = w.getframerate()
        channels = w.getnchannels()
        raw = w.readframes(w.getnframes())
    data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        data = data.reshape(-1, channels).mean(axis=1)
    return data, sr


def detect_events(
    samples: np.ndarray,
    sr: int,
    *,
    hop_s: float = 0.02,
    min_jump_db: float = 12.0,
    within_db_of_peak: float = 30.0,
    min_gap_s: float = 0.5,
    max_events: int = 200,
) -> list[dict]:
    """Find sharp loudness onsets (hits, stingers, SFX). Returns [{t, level_db, jump_db}]."""
    hop = max(1, int(sr * hop_s))
    n = len(samples) // hop
    if n < 3:
        return []
    frames = samples[: n * hop].reshape(n, hop)
    rms = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
    db = 20 * np.log10(rms + 1e-9)
    peak_db = float(db.max())
    jump = np.diff(db, prepend=db[0])
    floor = peak_db - within_db_of_peak
    candidates = np.where((jump >= min_jump_db) & (db >= floor))[0]
    events: list[dict] = []
    last_t = -1e9
    for idx in candidates:
        t = idx * hop_s
        if t - last_t < min_gap_s:
            continue
        events.append({"t": round(float(t), 3), "level_db": round(float(db[idx]), 1), "jump_db": round(float(jump[idx]), 1)})
        last_t = t
    events.sort(key=lambda e: e["jump_db"], reverse=True)
    return sorted(events[:max_events], key=lambda e: e["t"])


def cut_sfx_clips(wav: Path, events: list[dict], out_dir: Path, *, before_s: float = 0.2, after_s: float = 1.3, limit: int = 40) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for i, ev in enumerate(events[:limit]):
        start = max(0.0, ev["t"] - before_s)
        dst = out_dir / f"event_{i:03d}_{ev['t']:.2f}s.wav"
        run(["-ss", f"{start:.3f}", "-t", f"{before_s + after_s:.3f}", "-i", str(wav), "-c:a", "pcm_s16le", str(dst)])
        ev["clip"] = dst.name
        written.append(dst.name)
    return written


def detect_scenes(video: Path, *, threshold: float = 0.35, fps: float = 2.0) -> list[float]:
    """Scene-cut timestamps. Samples at `fps` to keep long videos fast."""
    proc = run(
        ["-i", str(video), "-an", "-vf", f"fps={fps},select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
    )
    times = [float(m) for m in re.findall(r"pts_time:([0-9.]+)", proc.stderr)]
    deduped: list[float] = []
    for t in times:
        if not deduped or t - deduped[-1] > 1.0:
            deduped.append(round(t, 3))
    return deduped


def extract_keyframes(video: Path, times: list[float], out_dir: Path, *, limit: int = 60, width: int = 640) -> list[str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    names: list[str] = []
    for i, t in enumerate(times[:limit]):
        dst = out_dir / f"scene_{i:03d}_{t:.2f}s.jpg"
        run(["-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-vf", f"scale={width}:-2", str(dst)])
        names.append(dst.name)
    return names


def separate_stems(wav: Path, out_dir: Path) -> dict:
    """Optional: split vocals from the rest (music + SFX) with demucs. Needs `pip install demucs` (torch)."""
    if shutil.which("demucs") is None:
        try:
            import demucs  # noqa: F401
        except ImportError:
            return {"status": "skipped", "reason": "demucs not installed (pip install demucs)"}
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = ["python3", "-m", "demucs", "--two-stems", "vocals", "-o", str(out_dir), str(wav)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return {"status": "failed", "reason": proc.stderr[-800:]}
    stem_dir = next(out_dir.glob("*/*"), None)
    files = sorted(p.name for p in stem_dir.glob("*.wav")) if stem_dir else []
    return {"status": "ok", "dir": str(stem_dir.relative_to(out_dir)) if stem_dir else None, "files": files}

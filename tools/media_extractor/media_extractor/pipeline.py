"""End-to-end run: link or local file -> video, audio, SFX clips, scenes, keyframes, manifest."""
from __future__ import annotations

import datetime as dt
import json
import shutil
from pathlib import Path
from typing import Callable, Optional

from . import __version__
from .analyze import (
    cut_sfx_clips,
    detect_events,
    detect_scenes,
    extract_audio,
    extract_keyframes,
    read_wav_mono,
    separate_stems,
)
from .download import download
from .ffmpeg import run

ProgressFn = Callable[[str], None]


def _noop(_: str) -> None:
    return None


def is_url(source: str) -> bool:
    return source.startswith(("http://", "https://"))


def process(
    source: str,
    out_dir: Path,
    *,
    max_height: int = 1080,
    scenes: bool = True,
    events: bool = True,
    keyframes: bool = True,
    separate: bool = False,
    progress: Optional[ProgressFn] = None,
) -> dict:
    """Run the pipeline. `source` is a video URL or a path to a local video file."""
    progress = progress or _noop
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest: dict = {
        "tool": "media_extractor",
        "version": __version__,
        "source": source,
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "files": {},
        "metadata": {},
    }

    if is_url(source):
        progress("downloading")
        video, meta = download(source, out_dir, max_height=max_height)
        manifest["metadata"] = meta
        subs = sorted(p.name for p in out_dir.glob("source*.srt")) + sorted(p.name for p in out_dir.glob("source*.vtt"))
        if subs:
            manifest["files"]["subtitles"] = subs
    else:
        local = Path(source)
        if not local.exists():
            raise FileNotFoundError(source)
        video = out_dir / f"source{local.suffix.lower() or '.mp4'}"
        if local.resolve() != video.resolve():
            shutil.copyfile(local, video)
        manifest["metadata"] = {"title": local.stem}
    manifest["files"]["video"] = video.name

    progress("extracting audio")
    wav = extract_audio(video, out_dir / "audio.wav")
    manifest["files"]["audio_wav"] = wav.name
    mp3 = out_dir / "audio.mp3"
    run(["-i", str(wav), "-c:a", "libmp3lame", "-b:a", "192k", str(mp3)])
    manifest["files"]["audio_mp3"] = mp3.name

    samples, sr = read_wav_mono(wav)
    manifest["duration_s"] = round(len(samples) / sr, 2)

    if events:
        progress("detecting sound events")
        evs = detect_events(samples, sr)
        cut_sfx_clips(wav, evs, out_dir / "sfx")
        manifest["events"] = evs
        manifest["files"]["sfx_dir"] = "sfx"

    if scenes:
        progress("detecting scenes")
        cuts = detect_scenes(video)
        manifest["scenes"] = [{"t": t} for t in cuts]
        if keyframes:
            progress("extracting keyframes")
            names = extract_keyframes(video, cuts, out_dir / "keyframes")
            for item, name in zip(manifest["scenes"], names):
                item["keyframe"] = name
            manifest["files"]["keyframes_dir"] = "keyframes"

    if separate:
        progress("separating stems")
        manifest["stems"] = separate_stems(wav, out_dir / "stems")

    manifest["status"] = "done"
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    progress("done")
    return manifest

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .pipeline import process


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="media_extractor", description="Video link -> video, audio, SFX, scenes, manifest")
    p.add_argument("source", help="YouTube/video URL, or path to a local video file")
    p.add_argument("-o", "--out", default="downloads/latest", help="output folder (default: downloads/latest)")
    p.add_argument("--max-height", type=int, default=1080, help="max video height for downloads (default 1080)")
    p.add_argument("--no-events", action="store_true", help="skip sound-event / SFX clip detection")
    p.add_argument("--no-scenes", action="store_true", help="skip scene-cut detection")
    p.add_argument("--no-keyframes", action="store_true", help="skip keyframe stills")
    p.add_argument("--separate", action="store_true", help="split vocals from music/SFX with demucs (optional, heavy)")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = process(
            args.source,
            Path(args.out),
            max_height=args.max_height,
            events=not args.no_events,
            scenes=not args.no_scenes,
            keyframes=not args.no_keyframes,
            separate=args.separate,
            progress=lambda msg: print(f"[media_extractor] {msg}", file=sys.stderr),
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(f"Done. Manifest: {Path(args.out) / 'manifest.json'}")
    print(f"  duration: {manifest.get('duration_s')}s | events: {len(manifest.get('events', []))} | scenes: {len(manifest.get('scenes', []))}")
    return 0

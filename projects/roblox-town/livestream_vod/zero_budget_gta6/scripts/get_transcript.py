#!/usr/bin/env python3
"""
get_transcript.py — FREE YouTube transcript fetcher ($0.00)

Uses youtube-transcript-api (MIT, open source, NO API key, NO payment).
Fetches the timestamped caption track for a video and saves it as JSON + TXT.

Usage:
    pip install youtube-transcript-api
    python get_transcript.py --video qSyo5d-dVzA --out evidence/transcript.json

Notes:
- The stream must have ENDED and YouTube must have processed the VOD
  (captions appear 30 min – 2 h after stream end). If the stream is still
  live, this will fail with "No transcript found" — that is expected.
- This script downloads ONLY the caption text. It does NOT download video.
- Free status: https://pypi.org/project/youtube-transcript-api
"""

import argparse
import json
import os
import sys


def fmt_ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(description="Free YouTube transcript fetcher ($0)")
    ap.add_argument("--video", required=True, help="YouTube video ID (e.g. qSyo5d-dVzA)")
    ap.add_argument("--out", default="evidence/transcript.json")
    ap.add_argument("--lang", default="en", help="Caption language (default: en)")
    a = ap.parse_args()

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("youtube-transcript-api not installed. Run: pip install youtube-transcript-api",
              file=sys.stderr)
        return 2

    try:
        api = YouTubeTranscriptApi()
        transcript = api.fetch(a.video, languages=[a.lang])
    except Exception as exc:
        print(f"Failed: {exc}", file=sys.stderr)
        print("\nPossible reasons:", file=sys.stderr)
        print("  1. Stream is still LIVE (captions appear after stream ends + processing)", file=sys.stderr)
        print("  2. Video has no captions", file=sys.stderr)
        print("  3. Network issue", file=sys.stderr)
        return 1

    lines = [{"start_s": round(e.start, 1), "ts": fmt_ts(e.start), "text": e.text}
             for e in transcript]

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump({"video_id": a.video, "lang": a.lang, "lines": lines}, fh, indent=2)

    txt_path = a.out.replace(".json", ".txt")
    with open(txt_path, "w") as fh:
        for ln in lines:
            fh.write(f"[{ln['ts']}] {ln['text']}\n")

    print(f"Saved {len(lines)} lines -> {a.out} and {txt_path}")
    print(f"Duration covered: {lines[-1]['ts'] if lines else '0:00:00'}")
    print("\nPaste the .txt file contents into the chat (or the first 1-2 hours).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

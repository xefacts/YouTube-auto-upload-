#!/usr/bin/env python3
"""
verify_vod.py — timestamped evidence from a public YouTube VOD without downloading it.

Two modes, both cheap:

  transcript  Gemini reads only the transcript layer (text tokens) over a window.
              This is where mission boundaries come from.
  frames      Gemini reads only sampled frames from a window at N fps.
              This is where "MISSION COMPLETE" banners get confirmed.

Usage
-----
  export GEMINI_API_KEY=...            # or pass --api-key
  python verify_vod.py --url "https://www.youtube.com/live/qSyo5d-dVzA" \
      --mode transcript --start 0 --end 10800 --out evidence/s1_0_3h.json

  python verify_vod.py --url "..." --mode frames --start 1430 --end 1610 --fps 2 \
      --ask "List every on-screen mission banner and completion UI with MM:SS." \
      --out evidence/s3_1430_1610.json

Notes
-----
* Windows are in SECONDS from the start of the VOD; they are sent as
  `processing.start_offset` / `end_offset`, so the model only looks at that range.
* Documentation (visited 2026-11-16): https://ai.google.dev/gemini-api/docs/video-understanding
  — YouTube URLs are supported (preview, currently not billed for the URL path),
  free tier allows 8 h of YouTube video per day, paid tier has no length limit,
  per-request context for 1M models covers ~3 h, hence the windowing here.
* If your installed `google-genai` predates the Interactions API, the call will raise;
  the error is printed with the exact request body so you can translate it to
  `client.models.generate_content(...)` without guessing.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone


def build_processing(mode: str, start: int, end: int, fps: float) -> dict:
    if mode == "transcript":
        return {
            "type": "static",
            "start_offset": f"{start}s",
            "end_offset": f"{end}s",
            "content_layers": ["transcript"],
        }
    return {
        "type": "static",
        "start_offset": f"{start}s",
        "end_offset": f"{end}s",
        "fps": fps,
        "content_layers": ["frames"],
    }


def default_prompt(mode: str) -> str:
    if mode == "transcript":
        return (
            "You are auditing a livestream VOD to locate the first two missions the player "
            "completes. Return STRICT JSON only, no prose, with this shape:\n"
            '{"mission_candidates":[{"mission_name":"","start_mmss":"","end_mmss":"",'
            '"completion_evidence":"","spoken_quote":""}],'
            '"objective_mentions":[{"mmss":"","quote":""}],'
            '"fail_mentions":[{"mmss":"","quote":""}]}\n'
            "Rules: every timestamp MUST be MM:SS inside the window you were given, taken from "
            "the transcript itself. Never guess, never round to a 'nice' number. If you cannot "
            "find a completion, return an empty mission_candidates array."
        )
    return (
        "Return STRICT JSON only, no prose:\n"
        '{"events":[{"mmss":"","type":"banner|objective|fail|reward|reaction|none",'
        '"on_screen_text":"","description":""}],'
        '"crop_safe":true,"crop_notes":"","hud_position":"top|bottom|none"}\n'
        "Quote on-screen text verbatim. Use MM:SS inside the window. If no banner is visible, "
        "say so in crop_notes and return an empty events array."
    )


def run(url: str, mode: str, start: int, end: int, fps: float, ask: str,
        model: str, api_key: str, timeout_s: int) -> dict:
    from google import genai  # pip install google-genai

    client = genai.Client(api_key=api_key)
    processing = build_processing(mode, start, end, fps)
    request_body = {
        "model": model,
        "input": [
            {"type": "video", "uri": url, "processing": processing},
            {"type": "text", "text": ask or default_prompt(mode)},
        ],
    }

    t0 = time.time()
    try:
        interaction = client.interactions.create(**request_body)
    except AttributeError as exc:                      # old SDK
        print(f"[sdk] Interactions API unavailable ({exc}). Request body was:", file=sys.stderr)
        print(json.dumps(request_body, indent=2), file=sys.stderr)
        raise
    text = getattr(interaction, "output_text", None) or str(interaction)
    elapsed = round(time.time() - t0, 1)
    if elapsed > timeout_s:
        print(f"[warn] call took {elapsed}s (long windows do that)", file=sys.stderr)
    return {"raw_text": text, "processing": processing, "model": model,
            "elapsed_s": elapsed, "request": request_body}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--mode", choices=["transcript", "frames"], required=True)
    ap.add_argument("--start", type=int, required=True, help="seconds from VOD start")
    ap.add_argument("--end", type=int, required=True, help="seconds from VOD start")
    ap.add_argument("--fps", type=float, default=1.0)
    ap.add_argument("--ask", default="")
    ap.add_argument("--model", default="gemini-4-hydrogen")
    ap.add_argument("--api-key", default=os.environ.get("GEMINI_API_KEY", ""))
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    if not a.api_key:
        print("Missing GEMINI_API_KEY (or --api-key). Nothing was called.", file=sys.stderr)
        return 2
    if a.end <= a.start:
        print("--end must be greater than --start", file=sys.stderr)
        return 2
    if a.end - a.start > 3 * 3600:
        print("[warn] window > 3 h — 1M-context models cap around 3 h per request; "
              "split it.", file=sys.stderr)

    result = run(a.url, a.mode, a.start, a.end, a.fps, a.ask, a.model, a.api_key, a.timeout)
    record = {
        "source_url": a.url,
        "mode": a.mode,
        "window": {"start_s": a.start, "end_s": a.end},
        "captured_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "verification": "PARTIAL",
        "verification_note": ("single-source evidence; upgrade to VERIFIED only when a frame "
                              "probe confirms the same second"),
        **result,
    }
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(record, fh, indent=2)
    print(f"wrote {a.out}  ({len(result['raw_text'])} chars, {result['elapsed_s']}s)")
    print("Paste this file's contents back into the chat; it is small and contains no video.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

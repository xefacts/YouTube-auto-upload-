#!/usr/bin/env python3
"""
request_clips_apify.py — pull ONLY the approved time ranges out of the VOD, in the cloud.

Actor: fractalai/youtube-video-clipper  (Apify)
  * accepts a public YouTube URL + a list of clips
  * hard limits: 20 clips per run, 10 minutes per clip
  * qualities: 360p / 480p / 720p / 1080p, stream-copy (no re-encode)
  * pricing (verified 2026-11-16): 1080p $1.50/clip, 720p $1.20, 480p $1.00;
    free plan allows 3 clips/month. Always check the console's cost preview.

Safety rules baked in
---------------------
1. A row is only sent if status == APPROVED **and** src_in/src_out are real timecodes.
   Everything else (TBC / BLOCKED / HELD / UNVERIFIED) is skipped, so an unverified
   beat can never be pulled by accident.
2. --dry-run prints the request and the cost estimate, and calls nothing.
3. Clips are named `mXX_wY_HH-MM-SS_HH-MM-SS.mp4` so the source timecode survives.

Usage
-----
  export APIFY_TOKEN=...
  python request_clips_apify.py --manifest footage_requests_m01_m02.csv --dry-run
  python request_clips_apify.py --manifest footage_requests_m01_m02.csv --quality 1080p
"""

import argparse
import csv
import json
import os
import re
import sys

ACTOR = "fractalai~youtube-video-clipper"
ENDPOINT = (f"https://api.apify.com/v2/acts/{ACTOR}"
            "/run-sync-get-dataset-items")
PRICES = {"360p": 1.40, "480p": 1.00, "720p": 1.20, "1080p": 1.50}   # per clip, USD


def hms_to_sec(tc: str) -> int | None:
    m = re.fullmatch(r"(\d{1,2}):(\d{2}):(\d{2})(?:\.\d+)?", tc.strip())
    if not m:
        return None
    h, mi, s = (int(x) for x in m.groups())
    return h * 3600 + mi * 60 + s


def sec_to_name(tc: str) -> str:
    return tc.replace(":", "-").split(".")[0]


def load_rows(path: str) -> list[dict]:
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def build_clips(rows: list[dict]) -> tuple[list[dict], list[str]]:
    clips, skipped = [], []
    for r in rows:
        rid = r.get("request_id", "?")
        status = (r.get("status") or "").upper()
        verification = (r.get("verification") or "").upper()
        a, b = hms_to_sec(r.get("src_in", "")), hms_to_sec(r.get("src_out", ""))
        if status != "APPROVED":
            skipped.append(f"{rid}: status={status or 'MISSING'}")
            continue
        if verification not in {"PARTIAL", "VERIFIED"}:
            skipped.append(f"{rid}: verification={verification or 'MISSING'}")
            continue
        if a is None or b is None or b <= a:
            skipped.append(f"{rid}: bad timecodes {r.get('src_in')}→{r.get('src_out')}")
            continue
        if b - a > 600:
            skipped.append(f"{rid}: {(b - a) / 60:.1f} min > 10 min actor limit")
            continue
        clips.append({
            "name": f"{r['mission'].lower()}_{r['window_tag']}_{sec_to_name(r['src_in'])}"
                    f"_{sec_to_name(r['src_out'])}",
            "start": r["src_in"],
            "end": r["src_out"],
        })
    return clips, skipped


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="footage_requests_m01_m02.csv")
    ap.add_argument("--url", default="https://www.youtube.com/live/qSyo5d-dVzA")
    ap.add_argument("--quality", default="1080p", choices=list(PRICES))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--token", default=os.environ.get("APIFY_TOKEN", ""))
    ap.add_argument("--out", default="evidence/clip_results.json")
    a = ap.parse_args()

    rows = load_rows(a.manifest)
    clips, skipped = build_clips(rows)
    print(f"approved clips: {len(clips)}  skipped: {len(skipped)}")
    for s in skipped:
        print("  skip  " + s)
    if not clips:
        print("\nNothing is APPROVED yet — this is expected until the transcript/frame pass "
              "fills src_in/src_out. No request was made, no money was spent.")
        return 0
    if len(clips) > 20:
        print(f"\n{len(clips)} clips > 20/run limit — split the manifest into batches.")
        return 2

    payload = {"videoUrl": a.url, "clips": clips, "quality": a.quality,
               "enableFallbacks": True, "maxRetries": 3}
    est = len(clips) * PRICES[a.quality]
    print(f"\nestimated cost: {len(clips)} x ${PRICES[a.quality]:.2f} = ${est:.2f} ({a.quality})")
    if a.dry_run:
        print(json.dumps(payload, indent=2))
        print("\n--dry-run: nothing was called.")
        return 0

    if not a.token:
        print("Missing APIFY_TOKEN — nothing was called.", file=sys.stderr)
        return 2
    import requests

    resp = requests.post(ENDPOINT, params={"token": a.token}, json=payload, timeout=3600)
    if resp.status_code >= 300:
        print(f"HTTP {resp.status_code}: {resp.text[:800]}", file=sys.stderr)
        return 1
    items = resp.json()
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump({"request": payload, "items": items}, fh, indent=2)
    ok = [i for i in items if isinstance(i, dict) and not i.get("failed")]
    print(f"got {len(ok)}/{len(items)} clips -> {a.out}")
    for i in ok:
        print(f"  {i.get('name')}  {i.get('duration')}s  {i.get('actualResolution')}  "
              f"{i.get('url')}")
    print("\nDownload only these MP4s (they are the requested ranges, not the VOD).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

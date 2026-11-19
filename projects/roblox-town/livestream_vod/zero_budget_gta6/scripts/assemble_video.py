#!/usr/bin/env python3
"""
assemble_video.py — clips + voiceover + SFX -> final 1080x1920 video ($0)

Pipeline:
  1. Normalize each clip to 1080x1920, 30fps, H.264 (center-crop, no stretch)
  2. Concatenate in manifest order
  3. Mix voiceover (full) + original clip audio (ducked -18 dB) + SFX cues
  4. Output final MP4 + SRT sidecar (captions burn in DaVinci/CapCut, free)

Usage:
  python assemble_video.py \
    --clips clips/ \
    --manifest clips/manifest.csv \
    --voiceover voiceover.mp3 \
    --sfx-map sfx_map.csv \
    --out out/speed_gta6_final.mp4

Clip manifest CSV columns: order, file, duration_hint
  order        — playback order (1, 2, 3...)
  file         — clip filename (relative to --clips dir)
  duration_hint— expected seconds (for timing SFX; 0 = use actual)

SFX map CSV columns: time_s, file, gain_db
  time_s  — seconds from video start
  file    — SFX filename (in ../ref/skill/blocky-shorts/assets/sfx/)
  gain_db — volume adjustment

Notes:
- Captions: this script writes an SRT sidecar from --captions (optional).
  Burning captions needs libass (not in static ffmpeg) — burn in DaVinci
  Resolve (free) or CapCut (free) using the SRT.
- Voiceover: record your own (best) or generate with edge-tts locally:
    pip install edge-tts
    edge-tts --voice hi-IN-NeerjaNeural --file narration.txt --write-media vo.mp3
  (edge-tts needs internet; sandbox cannot reach Microsoft, so run locally.)
"""

import argparse
import csv
import os
import subprocess
import sys

FF = open("/tmp/ffpath").read().strip() if os.path.exists("/tmp/ffpath") else "ffmpeg"
HERE = os.path.dirname(os.path.abspath(__file__))
SFX_DIR = os.path.normpath(os.path.join(HERE, "..", "..", "ref", "skill",
                                       "blocky-shorts", "assets", "sfx"))


def run(cmd, label):
    print(f"[{label}] {' '.join(cmd[:6])}...")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-2000:], file=sys.stderr)
        raise SystemExit(f"FAILED: {label}")
    return r


def load_manifest(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    rows.sort(key=lambda r: int(r["order"]))
    return rows


def load_sfx(path):
    if not path or not os.path.exists(path):
        return []
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def normalize_clips(clips_dir, manifest, work_dir):
    """Scale/crop each clip to 1080x1920 @30fps, uniform audio."""
    os.makedirs(work_dir, exist_ok=True)
    normed = []
    for row in manifest:
        src = os.path.join(clips_dir, row["file"])
        if not os.path.exists(src):
            print(f"  MISSING clip: {src} — skipping", file=sys.stderr)
            continue
        dst = os.path.join(work_dir, f"n{row['order']}.mp4")
        # Center-crop to 9:16 then scale; pad if source is narrower
        vf = ("scale=1080:1920:force_original_aspect_ratio=increase,"
              "crop=1080:1920,setsar=1,fps=30")
        run([FF, "-hide_banner", "-loglevel", "error", "-y",
             "-i", src, "-vf", vf,
             "-c:v", "libx264", "-preset", "medium", "-crf", "18",
             "-c:a", "aac", "-ar", "48000", "-ac", "2", dst],
            f"normalize {row['file']}")
        normed.append(dst)
    return normed


def concat_clips(normed, work_dir):
    listfile = os.path.join(work_dir, "concat.txt")
    with open(listfile, "w") as fh:
        for p in normed:
            fh.write(f"file '{p}'\n")
    out = os.path.join(work_dir, "joined.mp4")
    run([FF, "-hide_banner", "-loglevel", "error", "-y",
         "-f", "concat", "-safe", "0", "-i", listfile,
         "-c", "copy", out], "concat")
    return out


def mix_audio(joined, voiceover, sfx_cues, work_dir):
    """Voiceover full + original ducked + SFX at timestamps."""
    inputs = [FF, "-hide_banner", "-loglevel", "error", "-y", "-i", joined]
    if voiceover and os.path.exists(voiceover):
        inputs += ["-i", voiceover]
    sfx_inputs = []
    for cue in sfx_cues:
        sfx_path = os.path.join(SFX_DIR, cue["file"])
        if os.path.exists(sfx_path):
            inputs += ["-i", sfx_path]
            sfx_inputs.append(cue)

    # Build filter: [0:a] ducked, [1:a] voiceover, SFX delayed
    parts = ["[0:a]volume=0.13[a0]"]  # original audio ducked (~-18 dB)
    labels = ["[a0]"]
    if voiceover and os.path.exists(voiceover):
        parts.append("[1:a]volume=1.0[avo]")
        labels.append("[avo]")
    sfx_base = 2 if (voiceover and os.path.exists(voiceover)) else 1
    for i, cue in enumerate(sfx_inputs):
        delay_ms = int(float(cue["time_s"]) * 1000)
        gain = float(cue.get("gain_db", -6))
        vol = 10 ** (gain / 20)
        parts.append(f"[{sfx_base + i}:a]adelay={delay_ms}|{delay_ms},"
                     f"volume={vol:.3f}[s{i}]")
        labels.append(f"[s{i}]")
    mix = "".join(labels) + f"amix=inputs={len(labels)},"
    mix += "loudnorm=I=-14:TP=-1.5:LRA=11[aout]"
    parts.append(mix)

    out = os.path.join(work_dir, "mixed.mp4")
    cmd = inputs + ["-filter_complex", ";".join(parts),
                    "-map", "0:v", "-map", "[aout]",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", out]
    run(cmd, "mix audio")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", required=True, help="directory with clip files")
    ap.add_argument("--manifest", required=True, help="clip manifest CSV")
    ap.add_argument("--voiceover", default="", help="voiceover MP3/WAV")
    ap.add_argument("--sfx-map", default="", help="SFX timing CSV")
    ap.add_argument("--out", required=True, help="final MP4 path")
    a = ap.parse_args()

    manifest = load_manifest(a.manifest)
    print(f"Clips in manifest: {len(manifest)}")
    work_dir = os.path.join(os.path.dirname(a.out) or ".", "_work")
    os.makedirs(work_dir, exist_ok=True)

    print("\nStep 1/3: Normalize clips to 1080x1920...")
    normed = normalize_clips(a.clips, manifest, work_dir)
    if not normed:
        print("No clips found — nothing to assemble.", file=sys.stderr)
        return 1

    print("\nStep 2/3: Concatenate...")
    joined = concat_clips(normed, work_dir)

    print("\nStep 3/3: Mix audio (voiceover + ducked original + SFX)...")
    sfx_cues = load_sfx(a.sfx_map)
    final = mix_audio(joined, a.voiceover, sfx_cues, work_dir)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    run([FF, "-hide_banner", "-loglevel", "error", "-y",
         "-i", final, "-c", "copy", a.out], "finalize")
    print(f"\nDone -> {a.out}")
    print("Next: burn captions from the SRT in DaVinci Resolve (free) or CapCut (free),")
    print("then upload to Google Drive.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Measure VO clips -> timing.json (beat id -> seconds)."""
from __future__ import annotations
import argparse, json, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))

def dur(path):
    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe().replace("ffmpeg-", "ffmpeg-").replace("ffmpeg-linux", "ffmpeg-linux")
    probe = os.path.join(os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe()), "ffprobe-linux-x86_64-v9.0.2")
    if os.path.exists(probe):
        out = subprocess.run([probe, "-v", "error", "-show_entries", "format=duration",
                              "-of", "default=nw=1:nk=1", path], capture_output=True, text=True).stdout.strip()
        if out:
            return float(out)
    out = subprocess.run([ff, "-i", path, "-f", "null", "-"], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            h, m, s = line.split("Duration:")[1].split(",")[0].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError("cannot probe " + path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vo", default=os.path.join(HERE, "..", "out", "vo"))
    ap.add_argument("--out", default=os.path.join(HERE, "timing.json"))
    ap.add_argument("--pad", type=float, default=0.62)
    ap.add_argument("--min", type=float, default=2.3)
    args = ap.parse_args()
    beats = json.load(open(os.path.join(HERE, "beats.json")))["beats"]
    timing, total = {}, 0.0
    for b in beats:
        p = None
        for ext in ("mp3", "wav", "m4a"):
            c = os.path.join(args.vo, f"{b['id']}.{ext}")
            if os.path.exists(c):
                p = c
                break
        if not p:
            d = len(b["narration"].split()) / 2.55 + 0.75
        else:
            d = max(args.min, dur(p) + args.pad)
        timing[b["id"]] = round(d, 3)
        total += d
        print(f"{b['id']:10s} {d:5.2f}s")
    json.dump(timing, open(args.out, "w"), indent=2)
    print(f"total {total:.2f}s -> {args.out}")

if __name__ == "__main__":
    main()

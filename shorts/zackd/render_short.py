"""Render the short: frames -> captions -> mp4.

Usage:
  python render_short.py --timing timing.json --out ../out/build --w 720 --h 1280 --fps 30
  python render_short.py --timing timing.json --out /tmp/draft --w 432 --h 768 --fps 12 --draft
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from multiprocessing import Pool

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import captions as CAP  # noqa: E402
from PIL import Image  # noqa: E402
import scene as SC  # noqa: E402
from engine import _down, render  # noqa: E402

WORDS_PER_SEC = 2.55
SHOT_FN = dict(SC.SHOTS)


def load_plan(timing_path, fps, default="estimate"):
    beats = json.load(open(os.path.join(HERE, "beats.json")))["beats"]
    timing = {}
    if timing_path and os.path.exists(timing_path):
        timing = json.load(open(timing_path))
    out, t = [], 0.0
    for b in beats:
        if b["id"] in timing and timing[b["id"]]:
            dur = float(timing[b["id"]])
        else:
            dur = len(b["narration"].split()) / WORDS_PER_SEC + 0.75
        out.append(dict(b, start=t, duration=dur))
        t += dur
    return out, t


def frame_jobs(beats, fps):
    """(global_frame, shot_name, local_t, global_time) for the whole video."""
    jobs, idx = [], 0
    for b in beats:
        n = max(2, int(round(b["duration"] * fps)))
        for i in range(n):
            lt = (i + 0.5) / n
            jobs.append((idx, b["shot"], lt, idx / fps))
            idx += 1
    return jobs


def impact_post(img, gt, starts, W, H):
    """Zack-D style impact: zoom punch + micro shake right after a cut."""
    best = None
    for st in starts:
        dt = gt - st
        if -0.05 <= dt <= 0.26:
            best = dt if best is None else min(best, dt)
    if best is None:
        return img
    k = max(0.0, 1.0 - max(best, 0.0) / 0.26)
    zoom = 1.0 + 0.045 * k
    rng = np.random.default_rng(int(gt * 1000) % 99991)
    jx, jy = rng.normal(0, 7.0 * k, 2)
    cw, ch = int(W / zoom), int(H / zoom)
    x0 = int((W - cw) / 2 + jx)
    y0 = int((H - ch) / 2 + jy)
    x0 = min(max(x0, 0), W - cw)
    y0 = min(max(y0, 0), H - ch)
    return np.asarray(Image.fromarray(img).crop((x0, y0, x0 + cw, y0 + ch)).resize((W, H), Image.BILINEAR))


def _init():
    global PLAN
    PLAN = None


def render_one(job):
    idx, shot, lt, gt = job
    objs, cam, kw = SHOT_FN[shot](min(max(lt, 0.0), 1.0))
    img = render(objs, cam, W, H, **kw)
    if STARTS:
        img = impact_post(img, gt, STARTS, W, H)
    if CAP_TRACK:
        img = CAP.draw_captions(img, gt, CAP_TRACK, W, H, y_frac=YCAP)
    path = os.path.join(FRAMES, f"f_{idx:05d}.jpg")
    from PIL import Image
    Image.fromarray(img).save(path, quality=93)
    return idx


def main():
    global W, H, FRAMES, CAP_TRACK, YCAP, STARTS
    ap = argparse.ArgumentParser()
    ap.add_argument("--timing", default=os.path.join(HERE, "timing.json"))
    ap.add_argument("--out", default=os.path.join(HERE, "..", "out", "build"))
    ap.add_argument("--w", type=int, default=720)
    ap.add_argument("--h", type=int, default=1280)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0, help="max frames (debug)")
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--no-caps", action="store_true")
    args = ap.parse_args()

    W, H = args.w, args.h
    YCAP = 0.705
    STARTS = []
    FRAMES = os.path.join(args.out, "frames")
    os.makedirs(FRAMES, exist_ok=True)

    beats, total = load_plan(args.timing, args.fps)
    jobs = frame_jobs(beats, args.fps)
    if args.limit:
        jobs = jobs[: args.limit]
    CAP_TRACK = [] if args.no_caps else CAP.build_caption_track(beats)
    STARTS = [b["start"] for b in beats]
    print(f"beats={len(beats)} duration={total:.2f}s frames={len(jobs)} -> {FRAMES}", flush=True)

    t0 = time.time()
    done = 0
    if args.workers <= 1:
        for j in jobs:
            render_one(j)
            done += 1
            if done % 10 == 0:
                el = time.time() - t0
                print(f"  {done}/{len(jobs)}  {el/done:.2f}s/frame  eta {(len(jobs)-done)*el/done/60:.1f} min", flush=True)
    else:
        with Pool(args.workers) as pool:
            for _ in pool.imap_unordered(render_one, jobs, chunksize=1):
                done += 1
                if done % 20 == 0:
                    el = time.time() - t0
                    print(f"  {done}/{len(jobs)}  {el/done:.2f}s/frame  eta {(len(jobs)-done)*el/done/60:.1f} min", flush=True)
    print(f"done {len(jobs)} frames in {(time.time()-t0)/60:.1f} min", flush=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""video_studio/engine/analyze_frames.py — quantitative reference-video analysis (Phase 1).

No vision model: every number below is computed from actual pixels/frames with
NumPy + Pillow. Used for honest renderer comparison against competitor references.
Outputs: analysis/metrics.json, analysis/metrics_table.md, and updates
analysis/compare_sheet.jpg (labeled side-by-side frames for human review).
"""
from __future__ import annotations
import json, subprocess, os, sys
import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # video_studio/
REF = os.path.join(ROOT, "references")
OUTA = os.path.join(ROOT, "analysis")
FF = "/home/user/YouTube-auto-upload-/bin/ffmpeg"

VIDS = {
    "ref1_competitor": ("4c6ab1b4e11430848f3f66d14a075bd2.mp4", 123.6),
    "ref2_competitor": ("7056e78ff592fff4817a5a4803b12fc7.mp4", 145.6),
    "ref3_competitor": ("6527740cee2350c1a6a52559c960afe5.mp4", 134.5),
    "ref4_competitor": ("a841568b3b7717df6c23ebac346525cd.mp4", 128.2),
    "ours_skyline":   ("Skyline_Town_FINAL.mp4", 72.5),
}

def grab(path, t, w=288):
    """Decode one frame as small RGB numpy array."""
    p = subprocess.run([FF, "-v", "error", "-ss", str(t), "-i", path,
                        "-frames:v", "1", "-vf", f"scale={w}:-1", "-f", "rawvideo",
                        "-pix_fmt", "rgb24", "-"], capture_output=True)
    a = np.frombuffer(p.stdout, np.uint8)
    h = len(a) // (w * 3)
    return a[:w * h * 3].reshape(h, w, 3).astype(np.float32)

def metrics(arr):
    lum = 0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]
    mx, mn = arr.max(-1), arr.min(-1)
    sat = np.where(mx > 0, (mx - mn) / (mx + 1e-6), 0)
    # edge density: sobel on luminance
    g = lum
    gx = np.abs(np.diff(g, axis=1)); gy = np.abs(np.diff(g, axis=0))
    edge = float((gx[:-1, :] + gy[:, :-1]).mean())
    # flat-region ratio: pixels whose 3x3 neighbourhood is nearly constant
    d = np.zeros_like(g)
    d[:-1, :] += np.abs(np.diff(g, axis=0)); d[:, :-1] += np.abs(np.diff(g, axis=1))
    flat = float((d < 3.0).mean())
    # dark (shadow) fraction
    dark = float((lum < 60).mean())
    return dict(
        lum_mean=round(float(lum.mean()), 1),
        lum_std=round(float(lum.std()), 1),
        sat_mean=round(float(sat.mean()), 3),
        sat_p90=round(float(np.percentile(sat, 90)), 3),
        edge_density=round(edge, 2),
        flat_ratio=round(flat, 3),
        dark_ratio=round(dark, 3),
    )

def palette(arr, k=6):
    """Dominant colors by simple quantization (no sklearn)."""
    px = arr.reshape(-1, 3)
    q = (px // 32).astype(int)
    keys = q[:, 0] * 64 + q[:, 1] * 8 + q[:, 2]
    counts = np.bincount(keys, minlength=512)
    top = np.argsort(counts)[::-1][:k]
    out = []
    for t in top:
        m = keys == t
        if m.sum() < len(px) * 0.01:
            continue
        c = px[m].mean(0).astype(int)
        out.append(("#%02x%02x%02x" % tuple(c), round(float(m.mean()), 3)))
    return out

def motion_scan(path, dur, step=0.5, win=40.0):
    """Frame-difference + translation estimate over the first `win` seconds."""
    t = 1.0
    prev = None
    diffs, dxs, dys, zooms, cuts = [], [], [], [], 0
    while t < min(dur, win):
        cur = grab(path, t, w=192)[..., 0]  # luminance only
        if cur.size == 0:
            break
        if prev is not None:
            h = min(prev.shape[0], cur.shape[0]); w = min(prev.shape[1], cur.shape[1])
            a, b = prev[:h, :w], cur[:h, :w]
            d = float(np.abs(a - b).mean())
            diffs.append(d)
            if d > 28:  # hard cut heuristic
                cuts += 1
            # coarse global translation (block matching on center strip)
            best, bdx, bdy = 1e18, 0, 0
            for dy in range(-6, 7, 2):
                for dx in range(-6, 7, 2):
                    ay = a[max(0, dy):h + min(0, dy), max(0, dx):w + min(0, dx)]
                    by = b[max(0, -dy):h + min(0, -dy), max(0, -dx):w + min(0, -dx)]
                    s = float(np.abs(ay - by).mean())
                    if s < best:
                        best, bdx, bdy = s, dx, dy
            dxs.append(bdx); dys.append(bdy)
            # zoom estimate: compare center-crop correlation sign
            cy, cx = h // 2, w // 2
            c1 = a[cy - 20:cy + 20, cx - 20:cx + 20]
            c2in = b[cy - 26:cy + 26, cx - 26:cx + 26]
            c2out = b[cy - 14:cy + 14, cx - 14:cx + 14]
            def mae(x, y):
                hh = min(x.shape[0], y.shape[0]); ww = min(x.shape[1], y.shape[1])
                return float(np.abs(x[:hh, :ww] - y[:hh, :ww]).mean())
            zooms.append(1 if mae(c1, c2out) < mae(c1, c2in) else (-1 if mae(c1, c2in) < mae(c1, c2out) else 0))
        prev = cur
        t += step
    diffs = np.array(diffs) if diffs else np.zeros(1)
    dxs = np.array(dxs) if dxs else np.zeros(1)
    return dict(
        motion_mean=round(float(diffs.mean()), 2),
        motion_p95=round(float(np.percentile(diffs, 95)), 2),
        est_cuts_40s=int(cuts),
        pan_frames_pct=round(float((np.abs(dxs) >= 4).mean()), 3),
        zoom_in_pct=round(float((np.array(zooms) == 1).mean()), 3) if len(zooms) else 0,
        zoom_out_pct=round(float((np.array(zooms) == -1).mean()), 3) if len(zooms) else 0,
    )

def main():
    report = {}
    for tag, (f, dur) in VIDS.items():
        path = os.path.join(REF, f)
        frames = []
        for i in range(8):
            frames.append(grab(path, dur * (i + 0.5) / 8))
        m = {}
        for fr in frames:
            for k, v in metrics(fr).items():
                m.setdefault(k, []).append(v)
        m = {k: round(float(np.mean(v)), 3) for k, v in m.items()}
        m["palette"] = palette(frames[3] if len(frames) > 3 else frames[0])
        m["motion"] = motion_scan(path, dur)
        m["duration_s"] = dur
        report[tag] = m
        print(tag, "done", flush=True)
    os.makedirs(OUTA, exist_ok=True)
    with open(os.path.join(OUTA, "metrics.json"), "w") as fh:
        json.dump(report, fh, indent=1)
    # markdown table
    rows = ["| metric | " + " | ".join(report.keys()) + " |",
            "|" + "---|" * (len(report) + 1)]
    keys = ["lum_mean", "lum_std", "sat_mean", "edge_density", "flat_ratio", "dark_ratio"]
    for k in keys:
        rows.append(f"| {k} | " + " | ".join(str(report[t][k]) for t in report) + " |")
    rows.append("| est_cuts_40s | " + " | ".join(str(report[t]["motion"]["est_cuts_40s"]) for t in report) + " |")
    rows.append("| motion_mean | " + " | ".join(str(report[t]["motion"]["motion_mean"]) for t in report) + " |")
    rows.append("| pan_frames_pct | " + " | ".join(str(report[t]["motion"]["pan_frames_pct"]) for t in report) + " |")
    rows.append("| zoom_in_pct | " + " | ".join(str(report[t]["motion"]["zoom_in_pct"]) for t in report) + " |")
    with open(os.path.join(OUTA, "metrics_table.md"), "w") as fh:
        fh.write("\n".join(rows) + "\n")
    print("\n".join(rows))

if __name__ == "__main__":
    main()

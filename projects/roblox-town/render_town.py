import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "cartoon-time-short"))
"""Render Hiccup Town: blocky 3D scene -> captions -> 1080x1920 30 fps MP4."""
import argparse
import json
import math
import os
import subprocess
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import boxes
import draw2d as g
import scenes_town as S
from boxes import Cam, Scene3D
from draw2d import Pen

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 540, 960                 # design space
OUT_W, OUT_H = 1080, 1920       # delivery
SCALE = float(os.environ.get("SCALE", "2.4"))   # supersample (design -> canvas)
BW, BH = int(W * SCALE), int(H * SCALE)
FPS = 30
FF = os.environ.get("FFMPEG") or open("/tmp/ffpath").read().strip()

MOODS = {
    "day": dict(top=(116, 188, 238), bot=(210, 234, 246), amb=0.74,
                tint=(1.0, 1.0, 1.0), sun=(255, 248, 214)),
    "dusk": dict(top=(88, 84, 154), bot=(246, 170, 122), amb=0.58,
                 tint=(1.03, 0.95, 0.92), sun=(255, 214, 160)),
    "night": dict(top=(16, 20, 46), bot=(46, 56, 100), amb=0.42,
                  tint=(0.88, 0.92, 1.08), sun=(226, 232, 250)),
}


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a) if b != a else 0.0))
    return t * t * (3 - 2 * t)


class CamKeys:
    def __init__(self, keys, u):
        if len(keys) == 1:
            u = 0.0
            keys = [keys[0], keys[0]]
        for i in range(len(keys) - 1):
            a, b = keys[i], keys[i + 1]
            if a[0] <= u <= b[0] or i == len(keys) - 2:
                k = smoothstep(a[0], b[0], min(max(u, a[0]), b[0]))
                vals = [a[j] + (b[j] - a[j]) * k for j in range(1, 7)]
                self.x, self.y, self.z, self.yaw, self.pitch, self.fov = vals
                return


def sky(canvas, mood, t, shake=(0, 0)):
    m = MOODS[mood]
    grad = g._lg(BW, BH, m["top"], m["bot"]).copy()
    canvas.paste(grad, (0, 0))
    d = ImageDraw.Draw(canvas)
    # sun / moon
    sx, sy = BW * 0.76, BH * 0.16
    r = BW * 0.055
    d.ellipse((sx - r, sy - r, sx + r, sy + r), fill=m["sun"])
    a = Image.new("L", (int(r * 6), int(r * 6)), 0)
    ImageDraw.Draw(a).ellipse((r * 2, r * 2, r * 4, r * 4), fill=90)
    a = a.filter(ImageFilter.GaussianBlur(r * 0.6))
    canvas.paste(Image.new("RGB", a.size, m["sun"]),
                 (int(sx - r * 3), int(sy - r * 3)), a)
    # blocky clouds
    for i, (cx, cy, w) in enumerate(((0.18, 0.12, 0.16), (0.55, 0.08, 0.12),
                                    (0.86, 0.22, 0.10))):
        x = ((cx + t * 0.004 * (1 + i * 0.3)) % 1.2 - 0.1) * BW
        y = cy * BH
        ww = w * BW
        col = (250, 250, 252) if mood != "night" else (70, 78, 116)
        for j, (ox, oy, sc) in enumerate(((0, 0, 1.0), (-0.45, 0.06, 0.7),
                                          (0.45, 0.05, 0.65), (0.15, -0.06, 0.6))):
            d.rounded_rectangle((x + ox * ww, y + oy * BW * 0.06,
                                 x + ox * ww + ww * sc, y + oy * BW * 0.06 + ww * 0.16),
                                radius=ww * 0.06, fill=col)
    return canvas


_vig = None
_grain = []


def post_assets():
    global _vig, _grain
    if _vig is not None:
        return _vig, _grain
    y, x = np.mgrid[0:OUT_H, 0:OUT_W]
    r = np.sqrt(((x - OUT_W / 2) / (OUT_W / 2)) ** 2 + ((y - OUT_H / 2) / (OUT_H / 2)) ** 2)
    v = np.clip(1.0 - 0.30 * np.clip((r - 0.55) / 0.75, 0, 1) ** 1.4, 0, 1)
    _vig = Image.fromarray((np.dstack([v] * 3) * 255).astype(np.uint8), "RGB")
    rng = np.random.RandomState(5)
    for _ in range(5):
        n = rng.normal(0, 1, (OUT_H // 3, OUT_W // 3))
        n = np.clip(128 + n * 22, 0, 255).astype(np.uint8)
        _grain.append(Image.fromarray(n, "L").resize((OUT_W, OUT_H), Image.BILINEAR))
    return _vig, _grain


_fonts = {}


def font(size):
    key = int(size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(g.FONT_BOLD, key)
    return _fonts[key]


CAP_CACHE = {}


def cap_image(word, color, size=27, stroke=3.2):
    color = tuple(int(c) for c in color)
    key = (word, color, size)
    img = CAP_CACHE.get(key)
    if img is not None:
        return img
    f = font(size * SCALE)
    pad = int(stroke * SCALE * 1.6 + 10)
    tw = f.getlength(word)
    img = Image.new("RGBA", (int(tw) + pad * 2, int(size * SCALE * 1.45) + pad * 2),
                    (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.text((pad, pad), word, font=f, fill=color + (255,),
           stroke_width=int(stroke * SCALE), stroke_fill=(18, 14, 22, 245))
    CAP_CACHE[key] = img
    return img


CAP_PLAN = {}


def cap_plan(chunks, size=27, maxw=0.78):
    """chunks = [(text, colour)] -> word rows that fit the frame."""
    key = (tuple((t, tuple(int(c) for c in col)) for t, col in chunks), size, maxw)
    if key in CAP_PLAN:
        return CAP_PLAN[key]
    f = font(size * SCALE)
    space = size * SCALE * 0.62
    limit = BW * maxw
    words = [(w, tuple(int(c) for c in col)) for text, col in chunks for w in text.split()]
    rows, cur, curw = [], [], 0.0
    for w, col in words:
        ww = f.getlength(w)
        if cur and curw + space + ww > limit:
            rows.append(cur)
            cur, curw = [], 0.0
        curw += (space + ww) if cur else ww
        cur.append([w, col, ww])
    if cur:
        rows.append(cur)
    total = sum(len(w) for w, _ in words) or 1
    acc, out = 0, []
    for row in rows:
        rw = sum(c[2] for c in row) + space * (len(row) - 1)
        items = []
        for w, col, ww in row:
            at = acc / total
            acc += len(w) + 1
            items.append((w, col, ww, at))
        out.append((items, rw, space))
    CAP_PLAN[key] = (out, size * SCALE * 1.30)
    return CAP_PLAN[key]


def draw_captions(canvas, chunks, t, born0, span, y=0.775):
    rows, lh = cap_plan(chunks)
    nl = len(rows)
    total_chars = sum(len(c[0].split()) for c in chunks) or 1
    for li, (items, rw, space) in enumerate(rows):
        x = BW / 2 - rw / 2
        cy = H * y * SCALE + (li - (nl - 1) / 2) * lh
        for w, col, ww, at in items:
            born = born0 + span * 0.86 * at
            if t < born - 0.015:
                x += ww + space
                continue
            img = cap_image(w, col)
            dt = t - born
            k = 1.0
            if dt < 0.12:
                k = 1.30 - 0.30 * (dt / 0.12)
            if k != 1.0:
                img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))),
                                 Image.BILINEAR)
            canvas.alpha_composite(img, (int(x + ww / 2 - img.width / 2),
                                         int(cy - img.height / 2)))
            x += ww + space


def shot_state(timing, t):
    for i, sh in enumerate(timing["shots"]):
        if sh["start"] <= t < sh["start"] + sh["dur"]:
            return i, (t - sh["start"]) / sh["dur"], t - sh["start"]
    if t >= timing["end_card"]["start"]:
        return -1, (t - timing["end_card"]["start"]) / timing["end_card"]["dur"], 0.0
    i = len(timing["shots"]) - 1
    return i, 1.0, 0.0


def frame(t, timing):
    idx, u, lt = shot_state(timing, t)
    if idx < 0:
        return end_card(u)
    sh = timing["plan"][idx]
    st = timing["shots"][idx]
    ck = CamKeys(sh["cam"], u)
    shake = (0.0, 0.0)
    if sh["stage"] == "mass_hic" and 0.2 < u < 0.6:
        amp = 0.02 * (1 - abs(u - 0.4) / 0.2)
        shake = (math.sin(t * 61) * amp, math.cos(t * 47) * amp)
    pull = float(os.environ.get("CAMD", "1.55"))
    cam = Cam(ck.x * 0.6 + shake[0], ck.y + shake[1] + (pull - 1) * 0.30, ck.z * pull,
              ck.yaw, ck.pitch, ck.fov, w=W, h=H)
    if st["dur"] > 1.9 and u >= 0.52:
        ck2 = CamKeys(sh["cam"], 1.0)
        side = 0.22 if (idx % 2 == 0) else -0.22
        cam = Cam(ck2.x * 0.6 + side, ck2.y + 0.14 + (pull - 1) * 0.30,
                  ck2.z * pull * 1.06, ck2.yaw - math.copysign(0.10, side),
                  ck2.pitch, ck2.fov * 0.92, w=W, h=H)
    mood = MOODS[sh["mood"]]
    canvas = Image.new("RGB", (BW, BH))
    sky(canvas, sh["mood"], t)
    d = ImageDraw.Draw(canvas)
    p = Pen(d, s=SCALE, img=canvas)
    sc = Scene3D(canvas, p, cam, ambient=mood["amb"], tint=mood["tint"])
    S.SETS[sh["set"]](sc)
    sc.flush()
    sc2 = Scene3D(canvas, p, cam, ambient=mood["amb"], tint=mood["tint"])
    S.STAGES[sh["stage"]](sc2, u, lt)
    sc2.flush()
    canvas = canvas.convert("RGBA")
    draw_captions(canvas, sh["cap"], t, st["start"] + 0.04,
                  max(0.35, st["dur"] - 0.10), y=sh.get("cap_y", 0.775))
    img = canvas.convert("RGB").resize((OUT_W, OUT_H), Image.BILINEAR)
    vig, grain = post_assets()
    img = Image.blend(img, vig, 0.16)
    gr = grain[int(t * FPS) % len(grain)]
    img = Image.blend(img, Image.merge("RGB", (gr, gr, gr)), 0.025)
    return img


def end_card(u):
    img = Image.new("RGB", (OUT_W, OUT_H), (26, 22, 34))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(g.FONT_BOLD, 118)
    d.text((OUT_W / 2, OUT_H * 0.455), "HICCUP", font=f, fill=(252, 250, 244),
           anchor="mm", stroke_width=14, stroke_fill=(16, 10, 18))
    d.text((OUT_W / 2, OUT_H * 0.535), "TOWN", font=f, fill=(245, 201, 59),
           anchor="mm", stroke_width=14, stroke_fill=(16, 10, 18))
    f2 = ImageFont.truetype(g.FONT_BOLD, 48)
    d.text((OUT_W / 2, OUT_H * 0.625), "part two tomorrow", font=f2,
           fill=(226, 232, 244), anchor="mm", stroke_width=8, stroke_fill=(16, 10, 18))
    k = smoothstep(0, 0.25, u)
    if k < 1:
        img = Image.blend(Image.new("RGB", img.size, (26, 22, 34)), img, k)
    return img


def load_timing():
    path = os.path.join(HERE, "story", "timing.json")
    return json.load(open(path))


def render(a, timing):
    total = timing["end_card"]["start"] + timing["end_card"]["dur"]
    n_total = int(round(total * FPS))
    start, n = a.start, (a.frames or (n_total - a.start))
    out = a.out or os.path.join(HERE, "out", "video_only.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = [FF, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo",
           "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}", "-r", str(FPS), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-g", "60", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    for i in range(n):
        proc.stdin.write(frame((start + i) / FPS, timing).tobytes())
        if i % 30 == 0:
            el = time.time() - t0
            print(f"  {i}/{n}  {el:5.1f}s  {i / max(el, .01):.1f} fps", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", out, os.path.getsize(out) if os.path.exists(out) else "FAILED")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--still", type=float)
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--frames", type=int, default=0)
    ap.add_argument("--out")
    a = ap.parse_args()
    tm = load_timing()
    if a.still is not None:
        os.makedirs(os.path.join(HERE, "out", "stills"), exist_ok=True)
        p = os.path.join(HERE, "out", "stills", f"t{a.still:06.2f}.png")
        frame(a.still, tm).save(p)
        print(p)
    else:
        render(a, tm)

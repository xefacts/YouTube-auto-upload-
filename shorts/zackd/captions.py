"""Burned-in captions: bold uppercase word pages with a pop-in."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def word_pages(words, max_chars=17, max_words=3):
    pages, cur = [], []
    for w in words:
        cand = " ".join(cur + [w])
        if cur and (len(cand) > max_chars or len(cur) >= max_words):
            pages.append(cur)
            cur = [w]
        else:
            cur.append(w)
    if cur:
        pages.append(cur)
    return [" ".join(p) for p in pages]


def word_times(words, duration, lead=0.06, tail=0.10):
    """Proportional word timings inside a beat, weighted by word length."""
    w = np.array([max(len(x), 2) + 1.6 for x in words], float)
    spans = w / w.sum() * max(duration - lead - tail, 0.4)
    t, out = lead, []
    for s in spans:
        out.append((t, t + s))
        t += s
    return out


def build_caption_track(beats):
    """beats: list of dicts with narration + start + duration -> caption events."""
    track = []
    for b in beats:
        raw = b["narration"].upper().replace("—", ",")
        chunks = [c.strip() for c in raw.replace(".", ",").replace("?", ",").replace(":", ",").split(",") if c.strip()]
        words, breaks = [], set()
        for c in chunks:
            parts = c.split()
            words += parts
            breaks.add(len(words) - 1)
        pages, cur = [], []
        for i, w in enumerate(words):
            cand = " ".join(cur + [w])
            if cur and (len(cand) > 17 or len(cur) >= 3 or (i - 1) in breaks):
                pages.append(cur)
                cur = [w]
            else:
                cur.append(w)
        if cur:
            pages.append(cur)
        # split narration words into pages of the same sizes
        times = word_times(words, b["duration"])
        idx = 0
        for p in pages:
            if isinstance(p, list):
                p = " ".join(p)
            n = len(p.split())
            t0 = times[idx][0]
            t1 = times[min(idx + n - 1, len(times) - 1)][1]
            track.append(dict(text=p, start=b["start"] + t0, end=b["start"] + t1 + 0.05))
            idx += n
    return track


def _render_page(text, W, H, scale=1.0, accent=False):
    size = int(W * 0.098 * scale)
    font = ImageFont.truetype(FONT_BOLD, size)
    # fit inside 88% of the frame width
    for _ in range(24):
        probe = ImageDraw.Draw(Image.new("L", (4, 4)))
        bb = probe.textbbox((0, 0), text, font=font)
        if bb[2] - bb[0] <= W * 0.88 or size < 20:
            break
        size = int(size * 0.94)
        font = ImageFont.truetype(FONT_BOLD, size)
    pad = int(size * 0.5)
    tmp = Image.new("L", (8, 8))
    d0 = ImageDraw.Draw(tmp)
    bb = d0.textbbox((0, 0), text, font=font, stroke_width=max(2, int(size * 0.15)))
    tw, th = bb[2] - bb[0] + 2 * pad, bb[3] - bb[1] + 2 * pad
    img = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    stroke = max(2, int(size * 0.15))
    d.text((pad - bb[0], pad - bb[1]), text, font=font,
           fill=(255, 255, 255, 255) if not accent else (255, 232, 120, 255),
           stroke_width=stroke, stroke_fill=(4, 6, 10, 235))
    # soft drop shadow
    sh = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    ds.text((pad - bb[0] + size * 0.045, pad - bb[1] + size * 0.055), text, font=font,
            fill=(0, 0, 0, 150), stroke_width=stroke, stroke_fill=(0, 0, 0, 150))
    from PIL import ImageFilter
    sh = sh.filter(ImageFilter.GaussianBlur(size * 0.045))
    out = Image.alpha_composite(sh, img)
    return out


_CACHE = {}


def draw_captions(frame_rgb, t, track, W, H, y_frac=0.705):
    """Composite the caption page active at time t onto a uint8 frame."""
    page = None
    for ev in track:
        if ev["start"] <= t < ev["end"]:
            page = ev
            break
    if page is None:
        return frame_rgb
    key = page["text"]
    if key not in _CACHE:
        _CACHE[key] = _render_page(key, W, H, 1.0)
    img = _CACHE[key]
    # pop-in: 1.12 -> 1.0 over the first 90 ms
    age = t - page["start"]
    s = 1.12 - 0.12 * min(age / 0.09, 1.0) if age >= 0 else 1.0
    if abs(s - 1.0) > 0.004:
        nw, nh = int(img.width * s), int(img.height * s)
        img = img.resize((nw, nh), Image.BILINEAR)
    base = Image.fromarray(frame_rgb).convert("RGBA")
    # soft scrim so the type always reads
    scrim = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(scrim)
    band_h = int(img.height * 1.9)
    top = int(H * y_frac) - band_h // 2
    for i in range(band_h):
        a = int(96 * (1 - abs(i - band_h / 2) / (band_h / 2)) ** 1.6)
        ds.line([(0, top + i), (W, top + i)], fill=(0, 0, 0, a))
    base = Image.alpha_composite(base, scrim)
    x = (W - img.width) // 2
    y = int(H * y_frac) - img.height // 2
    base.alpha_composite(img, (max(0, x), max(0, y)))
    return np.asarray(base.convert("RGB"))

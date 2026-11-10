"""Procedural textures for the short (PIL -> linear float arrays)."""
from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def srgb_to_linear(img: np.ndarray) -> np.ndarray:
    a = np.asarray(img, np.float64) / 255.0
    return np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)


def to_linear(im: Image.Image) -> np.ndarray:
    return srgb_to_linear(np.asarray(im.convert("RGB"), np.float64))


def _grad(size, top, bot):
    w, h = size
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - t) + np.array(bot)[None, None, :] * t
    return np.repeat(arr, w, axis=1)


def radial_fade(size=512, power=2.2, inner=1.0, outer=0.06):
    yy, xx = np.mgrid[0:size, 0:size] / (size - 1) * 2 - 1
    r = np.sqrt(xx ** 2 + yy ** 2) / 1.414
    v = outer + (inner - outer) * np.clip(1 - r, 0, 1) ** power
    return np.repeat(v[..., None], 3, axis=2)


def card_face(w=1200, h=756, bank="ATLAS BANK", number="4821 0034 7719 2280"):
    """Dark premium credit-card face."""
    im = Image.new("RGB", (w, h), (12, 15, 26))
    d = ImageDraw.Draw(im)
    # diagonal sheen
    sheen = Image.new("L", (w, h), 0)
    ds = ImageDraw.Draw(sheen)
    ds.polygon([(0, h * 0.15), (w * 0.75, 0), (w, h * 0.1), (w, h * 0.42), (0, h * 0.72)], fill=70)
    sheen = sheen.filter(ImageFilter.GaussianBlur(w * 0.06))
    im = Image.composite(Image.new("RGB", (w, h), (38, 48, 78)), im, sheen)
    d = ImageDraw.Draw(im)
    # fine guilloche arcs
    for k in range(9):
        col = (28 + k * 3, 36 + k * 4, 60 + k * 5)
        d.arc([int(-w * 0.2 + k * 18), int(h * 0.1 + k * 12), int(w * 1.1 - k * 10), int(h * 1.6 - k * 20)],
              start=200, end=340, fill=col, width=2)
    # gold band
    d.rectangle([0, int(h * 0.86), w, h], fill=(22, 19, 12))
    d.rectangle([0, int(h * 0.86), w, int(h * 0.862)], fill=(214, 168, 74))
    # bank name
    f = ImageFont.truetype(FONT_BOLD, int(h * 0.115))
    d.text((int(w * 0.075), int(h * 0.10)), bank, font=f, fill=(232, 214, 178))
    # chip window (drawn dark; real 3D chip sits on top)
    d.rounded_rectangle([int(w * 0.075), int(h * 0.30), int(w * 0.075 + h * 0.30), int(h * 0.30 + h * 0.235)],
                        radius=int(h * 0.03), fill=(150, 116, 46), outline=(70, 54, 24), width=3)
    # number
    f2 = ImageFont.truetype(FONT_MONO, int(h * 0.086))
    d.text((int(w * 0.075), int(h * 0.585)), number, font=f2, fill=(226, 220, 205))
    # validity / name
    f3 = ImageFont.truetype(FONT, int(h * 0.042))
    d.text((int(w * 0.075), int(h * 0.70)), "VALID THRU  09/29", font=f3, fill=(150, 148, 142))
    d.text((int(w * 0.60), int(h * 0.905)), "A. RAZA", font=f3, fill=(180, 160, 120))
    # contactless waves
    cx, cy = int(w * 0.815), int(h * 0.395)
    for k, rr in enumerate((int(h * 0.045), int(h * 0.075), int(h * 0.105))):
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=-55, end=55, fill=(210, 175, 100), width=6)
    # network marks
    d.ellipse([int(w * 0.855), int(h * 0.60), int(w * 0.855 + h * 0.16), int(h * 0.60 + h * 0.16)],
              outline=(200, 170, 100), width=7)
    d.ellipse([int(w * 0.915), int(h * 0.60), int(w * 0.915 + h * 0.16), int(h * 0.60 + h * 0.16)],
              outline=(190, 120, 70), width=7)
    return to_linear(im)


_TEXT_CACHE = {}


def black_text(lines, size=(768, 512), color=(180, 235, 255), glow=1.0, align="center",
               mono=True, spacing=1.35, bold=True):
    """Glowing type on a black plate (reads as floating 3D text). Cached."""
    key = (str(lines), size, tuple(color), glow, align, mono, spacing, bold)
    if key in _TEXT_CACHE:
        return _TEXT_CACHE[key]
    _TEXT_CACHE[key] = _black_text(lines, size, color, glow, align, mono, spacing, bold)
    return _TEXT_CACHE[key]


def _black_text(lines, size, color, glow, align, mono, spacing, bold):
    w, h = size
    im = Image.new("RGB", (w, h), (0, 0, 0))
    fnt_path = FONT_MONO if mono else (FONT_BOLD if bold else FONT)
    if isinstance(lines, str):
        lines = [lines]
    fs = int(h / (len(lines) * spacing + 0.4))
    f = ImageFont.truetype(fnt_path, max(12, fs))
    d = ImageDraw.Draw(im)
    total = len(lines) * fs * spacing
    y = (h - total) / 2 + fs * 0.06
    for ln in lines:
        bb = d.textbbox((0, 0), ln, font=f)
        tx = (w - (bb[2] - bb[0])) / 2 if align == "center" else w * 0.06
        d.text((tx, y), ln, font=f, fill=color)
        y += fs * spacing
    if glow > 0:
        g = im.filter(ImageFilter.GaussianBlur(max(1, fs * 0.12)))
        im = Image.fromarray(np.clip(np.asarray(im, np.float32) + np.asarray(g, np.float32) * 0.9 * glow, 0, 255).astype(np.uint8))
    return to_linear(im)


def terminal_screen(size=(560, 980), amount="$1,480.00", status="TAP CARD"):
    w, h = size
    im = Image.new("RGB", (w, h), (4, 6, 10))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, int(h * 0.13)], fill=(10, 40, 90))
    f0 = ImageFont.truetype(FONT_BOLD, int(h * 0.045))
    d.text((int(w * 0.06), int(h * 0.035)), "ATLAS  PAY", font=f0, fill=(180, 220, 255))
    d.text((int(w * 0.70), int(h * 0.035)), "4G", font=f0, fill=(120, 200, 160))
    f1 = ImageFont.truetype(FONT_MONO, int(h * 0.095))
    bb = d.textbbox((0, 0), amount, font=f1)
    d.text(((w - (bb[2] - bb[0])) / 2, int(h * 0.26)), amount, font=f1, fill=(245, 250, 255))
    f2 = ImageFont.truetype(FONT_BOLD, int(h * 0.06))
    bb = d.textbbox((0, 0), status, font=f2)
    d.text(((w - (bb[2] - bb[0])) / 2, int(h * 0.42)), status, font=f2, fill=(120, 220, 255))
    r = int(w * 0.26)
    cx, cy = w // 2, int(h * 0.70)
    for k in range(3):
        rr = r - k * int(r * 0.28)
        d.arc([cx - rr, cy - rr, cx + rr, cy + rr], start=-60, end=60, fill=(90, 190, 255), width=max(3, int(w * 0.012)))
    g = im.filter(ImageFilter.GaussianBlur(int(w * 0.012)))
    im = Image.fromarray(np.clip(np.asarray(im, np.float32) + np.asarray(g, np.float32) * 0.8, 0, 255).astype(np.uint8))
    return to_linear(im)


def circuit(size=(1024, 1024), color=(230, 180, 90)):
    """Chip contact pattern (geometric bars, drawn as a texture)."""
    w, h = size
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    for k in range(4):
        y = int(h * (0.14 + k * 0.19))
        d.rounded_rectangle([int(w * 0.10), y, int(w * 0.90), y + int(h * 0.10)], radius=int(h * 0.03),
                            fill=color)
    return to_linear(im)


_LEDGER_CACHE = {}


def ledger_panel(size=(900, 620)):
    if size in _LEDGER_CACHE:
        return _LEDGER_CACHE[size]
    _LEDGER_CACHE[size] = _ledger_panel(size)
    return _LEDGER_CACHE[size]


def _ledger_panel(size):
    """Vault ledger: rows of numbers on black."""
    w, h = size
    im = Image.new("RGB", (w, h), (0, 0, 0))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT_MONO, int(h * 0.055))
    rng = np.random.default_rng(3)
    rows = 9
    for i in range(rows):
        y = int(h * (0.06 + i * 0.1))
        acc = "".join(str(rng.integers(0, 10)) for _ in range(4))
        val = f"{int(rng.integers(10, 99))},{int(rng.integers(100,999))}.{int(rng.integers(10,99))}"
        line = f"{acc}  {val:>10}"
        d.text((int(w * 0.05), y), line, font=f, fill=(120, 220, 255))
    return to_linear(im)


def grid_bg(size=(1024, 1024)):
    w, h = size
    im = Image.new("RGB", (w, h), (2, 4, 8))
    d = ImageDraw.Draw(im)
    for i in range(0, w, 64):
        d.line([(i, 0), (i, h)], fill=(10, 26, 44), width=2)
    for j in range(0, h, 64):
        d.line([(0, j), (w, j)], fill=(10, 26, 44), width=2)
    return to_linear(im)

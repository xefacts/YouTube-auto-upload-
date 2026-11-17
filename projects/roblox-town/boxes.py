import os as _os, sys as _sys
_sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)),
                                  "..", "cartoon-time-short"))
"""Tiny blocky-3D renderer (Pillow): cuboid world, flat-shaded faces.

The blocky-shorts skill draws with Three.js in headless Chrome. This sandbox has
no Chrome and no GPU, so the same look is built here from boxes: axis-aligned
cuboids, three visible faces each, lambert+ambient shading, painter's sort.
"""
import math

import draw2d as g
from draw2d import Pen

LIGHT = (-0.34, 0.80, -0.50)


def _norm(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


LIGHT = _norm(LIGHT)
FLAT = set()          # unshaded (emissive) faces: eyes, highlights

FACES = [
    ((0, 1, 0), [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)]),      # top
    ((0, -1, 0), [(0, 0, 0), (1, 0, 0), (1, 0, 1), (0, 0, 1)]),     # bottom
    ((0, 0, 1), [(0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)]),      # front +z
    ((0, 0, -1), [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]),     # back -z
    ((1, 0, 0), [(1, 0, 0), (1, 0, 1), (1, 1, 1), (1, 1, 0)]),      # right +x
    ((-1, 0, 0), [(0, 0, 0), (0, 0, 1), (0, 1, 1), (0, 1, 0)]),     # left -x
]


class Cam:
    def __init__(self, x=0.0, y=1.62, z=-5.2, yaw=0.0, pitch=-0.06, fov=46.0,
                 w=540, h=960):
        self.x, self.y, self.z = x, y, z
        self.yaw, self.pitch, self.fov = yaw, pitch, fov
        self.w, self.h = w, h
        self.f = (h / 2) / math.tan(math.radians(fov) / 2)

    def to_cam(self, p):
        dx, dy, dz = p[0] - self.x, p[1] - self.y, p[2] - self.z
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x1 = dx * cy - dz * sy
        z1 = dx * sy + dz * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        y2 = dy * cp - z1 * sp
        z2 = dy * sp + z1 * cp
        return x1, y2, z2

    def project(self, p):
        return self.project_cam(self.to_cam(p))

    def project_cam(self, p):
        x, y, z = p
        if z <= 0.05:
            return None
        return (self.w / 2 + self.f * x / z, self.h / 2 - self.f * y / z, z)

    def rot_point(self, p):
        cy, sy = math.cos(self.yaw), math.sin(self.yaw)
        x1 = p[0] * cy - p[2] * sy
        z1 = p[0] * sy + p[2] * cy
        cp, sp = math.cos(self.pitch), math.sin(self.pitch)
        return (x1, p[1] * cp - z1 * sp, p[1] * sp + z1 * cp)


def shade(color, k, tint=(1.0, 1.0, 1.0)):
    r, gg, b = color[:3]
    return (max(0, min(255, int(r * k * tint[0]))),
            max(0, min(255, int(gg * k * tint[1]))),
            max(0, min(255, int(b * k * tint[2]))))


NEAR = 0.22


def clip_near(pts):
    """Sutherland-Hodgman against z = NEAR in camera space."""
    out = []
    n = len(pts)
    for i in range(n):
        a, b = pts[i], pts[(i + 1) % n]
        ina, inb = a[2] >= NEAR, b[2] >= NEAR
        if ina:
            out.append(a)
        if ina != inb:
            t = (NEAR - a[2]) / (b[2] - a[2])
            out.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, NEAR))
    return out


def mix(a, b, k):
    k = max(0.0, min(1.0, k))
    return (int(a[0] + (b[0] - a[0]) * k), int(a[1] + (b[1] - a[1]) * k),
            int(a[2] + (b[2] - a[2]) * k))


class Scene3D:
    def __init__(self, canvas, pen, cam, ambient=0.62, tint=(1.0, 1.0, 1.0),
                 haze=None, haze_from=9.0, haze_to=34.0):
        self.canvas, self.p, self.cam = canvas, pen, cam
        self.items = []
        self.ambient, self.tint = ambient, tint
        self.haze, self.haze_from, self.haze_to = haze or (206, 226, 240), haze_from, haze_to

    def _air(self, col, depth):
        k = (depth - self.haze_from) / (self.haze_to - self.haze_from)
        return mix(col, self.haze, min(0.72, max(0.0, k)) if k > 0 else 0.0)

    # ---------------------------------------------------------------- boxes
    def box(self, center, size, color, rot=0.0, glow=None, alpha=255, tag="", bias=0.0):
        self.items.append(("box", center, size, color, rot, alpha, tag, bias, glow))

    def quad(self, pts, color, alpha=255, tag="", bias=0.0):
        self.items.append(("quad", pts, None, color, 0.0, alpha, tag, bias, None))

    def _corners(self, center, size, rot):
        cx, cy, cz = center
        sx, sy, sz = size
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        cr, sr = math.cos(rot), math.sin(rot)
        out = []
        for ix in (0, 1):
            for iy in (0, 1):
                for iz in (0, 1):
                    lx = (-hx if ix == 0 else hx)
                    lz = (-hz if iz == 0 else hz)
                    wx = cx + lx * cr - lz * sr
                    wz = cz + lx * sr + lz * cr
                    wy = cy + (-hy if iy == 0 else hy)
                    out.append((wx, wy, wz))
        return out, (cr, sr)

    def flush(self):
        draw = []
        for kind, a, b, color, rot, alpha, tag, bias, glow in self.items:
            if kind == "box":
                corners, (cr, sr) = self._corners(a, b, rot)
                cam_pts = [self.cam.to_cam(c) for c in corners]
                if all(c[2] <= NEAR for c in cam_pts):
                    continue
                for n, idx4 in FACES:
                    wn = (n[0] * cr + n[2] * sr, n[1], -n[0] * sr + n[2] * cr)
                    fc = [a[0] + wn[0] * b[0] / 2, a[1] + wn[1] * b[1] / 2,
                          a[2] + wn[2] * b[2] / 2]
                    fc_cam = self.cam.to_cam(fc)
                    if wn[0] * fc_cam[0] + wn[1] * fc_cam[1] + wn[2] * fc_cam[2] >= 0:
                        continue                      # back face
                    lam = max(0.0, wn[0] * LIGHT[0] + wn[1] * LIGHT[1] + wn[2] * LIGHT[2])
                    k = self.ambient + (1 - self.ambient) * lam
                    if glow:
                        k = glow if glow is not True else 1.0
                    if abs(wn[1]) > 0.9 and wn[1] > 0:
                        k *= 1.02
                    fcam = clip_near([cam_pts[c3[0] * 4 + c3[1] * 2 + c3[2]] for c3 in idx4])
                    if len(fcam) < 3:
                        continue
                    pts = []
                    for q in fcam:
                        pj = self.cam.project_cam(q)
                        if pj is not None:
                            pts.append((pj[0], pj[1]))
                    if len(pts) < 3:
                        continue
                    depth = sum(q[2] for q in fcam) / len(fcam) + bias
                    draw.append((depth, pts,
                                 self._air(shade(color, k, self.tint), depth)))
            else:
                fcam = clip_near([self.cam.to_cam(p) for p in a])
                if len(fcam) < 3:
                    continue
                pts, ok = [], True
                for q in fcam:
                    pj = self.cam.project_cam(q)
                    if pj is None:
                        ok = False
                        break
                    pts.append((pj[0], pj[1]))
                if not ok:
                    continue
                depth = sum(q[2] for q in fcam) / len(fcam) + bias
                draw.append((depth, pts, self._air(color, depth)))
        draw.sort(key=lambda t: -t[0])
        for _, pts, col in draw:
            self.p.poly(pts, col)
        self.items = []

    # ---------------------------------------------------------------- shapes
    def floor(self, y, color, size=60, x=0, z=0, grid=None):
        self.box((x, y - 0.05, z), (size, 0.1, size), color)
        if grid:
            step = 2.0
            for i in range(-int(size / 2), int(size / 2), int(step)):
                self.box((x + i, y + 0.002, z), (0.04, 0.02, size), grid)
                self.box((x, y + 0.002, z + i), (size, 0.02, 0.04), grid)


# ---------------------------------------------------------------- characters
SKIN = (243, 199, 165)
DARK = (54, 44, 58)


def _face(sc, hx, hy, hz, s, facing, spec, expr):
    """Glossy toy face: white eyes, dark pupils, specular dot, shaped mouth."""
    sign = -1.0 if facing else 1.0
    fz = hz + sign * 0.012
    eo, eye_h, pup_h = 0.158 * s, 0.180 * s, 0.092 * s
    ey = hy + 0.020 * s
    white = spec.get("eye", (250, 250, 252))
    pupil = spec.get("pupil", (34, 30, 42))
    if expr in ("worried", "strain", "sus"):
        eye_h, pup_h, ey = 0.115 * s, 0.070 * s, hy + 0.010 * s
    xeyes = expr in ("shock", "dead", "dizzy")
    for sx in (-eo, eo):
        sc.box((hx + sx, ey, fz), (0.200 * s, eye_h, 0.02), white, glow=True)
        if xeyes:
            for dx, dy in ((-0.034, -0.034), (0.034, 0.034), (-0.034, 0.034),
                           (0.034, -0.034)):
                sc.box((hx + sx + dx * s, ey + dy * s, fz + sign * 0.006),
                       (0.048 * s, 0.048 * s, 0.02), pupil, glow=True)
        else:
            py = ey - (0.020 * s if expr in ("sad", "worried") else 0.0)
            sc.box((hx + sx, py, fz + sign * 0.006), (0.078 * s, pup_h, 0.02), pupil,
                   glow=True)
            sc.box((hx + sx - 0.030 * s, py + pup_h * 0.40, fz + sign * 0.010),
                   (0.026 * s, 0.028 * s, 0.02), (255, 255, 255), glow=True)
    my = hy - 0.150 * s
    dark = (108, 52, 58)
    if expr in ("shock", "surprised"):
        sc.box((hx, my - 0.010 * s, fz), (0.115 * s, 0.115 * s, 0.02), (96, 48, 54))
        sc.box((hx, my + 0.030 * s, fz), (0.070 * s, 0.030 * s, 0.02), (250, 248, 244))
    elif expr in ("sad", "worried", "strain"):
        sc.box((hx, my + 0.028 * s, fz), (0.150 * s, 0.032 * s, 0.02), dark)
        for sx in (-0.070, 0.070):
            sc.box((hx + sx * s, my + 0.006 * s, fz), (0.045 * s, 0.032 * s, 0.02), dark)
    elif expr in ("grin", "happy", "laugh"):
        sc.box((hx, my + 0.010 * s, fz), (0.215 * s, 0.050 * s, 0.02), dark)
        for sx in (-0.095, 0.095):
            sc.box((hx + sx * s, my + 0.052 * s, fz), (0.048 * s, 0.048 * s, 0.02), dark)
    elif expr == "smile":
        sc.box((hx, my + 0.030 * s, fz), (0.170 * s, 0.036 * s, 0.02), dark)
        for sx in (-0.074, 0.074):
            sc.box((hx + sx * s, my + 0.050 * s, fz), (0.042 * s, 0.034 * s, 0.02), dark)
    else:
        sc.box((hx, my + 0.030 * s, fz), (0.135 * s, 0.030 * s, 0.02), dark)


def character(sc, x, z, y=0.0, s=1.0, spec=None, pose="idle", t=0.0, facing=180,
              tilt=0.0):
    """Chunky-wide toy character (blocky-shorts look). Returns head-top height."""
    spec = spec or {}
    skin = spec.get("skin", SKIN)
    shirt = spec.get("shirt", (86, 156, 232))
    pants = spec.get("pants", (46, 56, 96))
    hair = spec.get("hair", (68, 48, 38))
    shoe = spec.get("shoe", (38, 38, 50))
    expr = spec.get("expr", "idle")
    hat = spec.get("hat")
    cap = spec.get("cap")
    rot = math.radians(facing)

    walk = pose in ("walk", "run")
    ph = t * (8.4 if pose == "run" else 5.4)
    swing = math.sin(ph) * (0.32 if pose == "run" else 0.20) if walk else 0.0
    bob = abs(math.sin(ph)) * 0.05 if walk else 0.0
    jump = 0.55 * math.sin(min(1.0, t / 0.7) * math.pi) if pose == "jump" else 0.0
    lean = 0.05 * math.sin(t * 9.0) if pose == "hiccup" else 0.0
    if pose == "strain":
        bob = 0.02 * math.sin(t * 22.0)
    if pose == "tremble":
        bob = 0.03 * math.sin(t * 34.0)

    base = y + jump + bob
    # legs + shoes
    for side in (-1, 1):
        off = swing * (1 if side > 0 else -1)
        sc.box((x + side * 0.170 * s, base + 0.430 * s, z + off),
               (0.175 * s, 0.600 * s, 0.200 * s), pants, rot=rot)
        sc.box((x + side * 0.170 * s, base + 0.055 * s, z + off + 0.035),
               (0.205 * s, 0.110 * s, 0.300 * s), shoe, rot=rot)
    # torso (wide + chunky)
    sc.box((x + lean, base + 1.010 * s, z), (0.880 * s, 0.545 * s, 0.440 * s), shirt,
           rot=rot)
    if spec.get("print"):
        sc.box((x + lean, base + 1.010 * s, z - 0.225 * s),
               (0.300 * s, 0.230 * s, 0.02), spec["print"], rot=rot)
    sc.box((x + lean, base + 0.760 * s, z), (0.900 * s, 0.070 * s, 0.460 * s),
           spec.get("belt", (30, 34, 52)), rot=rot)
    # arms
    arm_ang = {"point": (-100, 8), "shock": (-150, -150), "cheer": (-165, -165),
               "hiccup": (-30, -20), "hold": (-70, -70), "strain": (-20, -20),
               "clap": (-60, -60), "wave": (-150, -20)}.get(pose)
    for i, side in enumerate((-1, 1)):
        sx0, sy0 = x + side * 0.520 * s, base + 1.230 * s
        if arm_ang:
            ang = math.radians(arm_ang[i])
            ax = sx0 + side * -math.sin(ang) * 0.30 * s
            ay = sy0 + math.cos(ang) * 0.26 * s
        else:
            ax, ay = sx0, sy0 - swing * 0.6 * (1 if side > 0 else -1) * 0.5
        sc.box((ax, ay - 0.190 * s, z), (0.180 * s, 0.420 * s, 0.220 * s),
               skin if spec.get("sleeveless") else shirt, rot=rot)
        sc.box((ax, ay - 0.480 * s, z), (0.180 * s, 0.190 * s, 0.210 * s), skin, rot=rot)
    # head
    hy = base + 1.600 * s
    sc.box((x + lean * 1.2, base + 1.315 * s, z), (0.200 * s, 0.090 * s, 0.200 * s), skin)
    sc.box((x + lean * 1.2, hy, z), (0.640 * s, 0.560 * s, 0.580 * s), skin, rot=rot)
    if hair:
        sc.box((x + lean * 1.2, hy + 0.290 * s, z), (0.660 * s, 0.090 * s, 0.600 * s),
               hair, rot=rot)
        sc.box((x + lean * 1.2, hy + 0.205 * s, z - 0.293 * s),
               (0.660 * s, 0.165 * s, 0.032 * s), hair, rot=rot)
        if spec.get("long_hair"):
            sc.box((x + lean * 1.2, hy - 0.090 * s, z + 0.300 * s),
                   (0.660 * s, 0.520 * s, 0.060 * s), hair, rot=rot)
    if cap:
        sc.box((x + lean * 1.2, hy + 0.290 * s, z), (0.660 * s, 0.110 * s, 0.600 * s),
               cap, rot=rot)
        sc.box((x + lean * 1.2, hy + 0.235 * s, z - 0.390 * s),
               (0.560 * s, 0.055 * s, 0.240 * s), cap, rot=rot)
    if hat:
        sc.box((x + lean * 1.2, hy + 0.320 * s, z), (0.720 * s, 0.060 * s, 0.660 * s),
               hat, rot=rot)
        sc.box((x + lean * 1.2, hy + 0.430 * s, z), (0.520 * s, 0.190 * s, 0.500 * s),
               hat, rot=rot)
    if spec.get("glasses"):
        for sx in (-0.150, 0.150):
            sc.box((x + lean * 1.2 + sx * s, hy + 0.030 * s, z - 0.305 * s),
                   (0.215 * s, 0.150 * s, 0.02), (60, 66, 84))
            sc.box((x + lean * 1.2 + sx * s, hy + 0.030 * s, z - 0.320 * s),
                   (0.150 * s, 0.100 * s, 0.02), (236, 244, 250))
    _face(sc, x + lean * 1.2, hy, z - 0.290 * s, s, facing, spec, expr)
    return base + 1.930 * s


def hills(sc, color=(170, 184, 196), z=46.0, n=7, w=14.0):
    """Distant blocky skyline so the horizon is never empty."""
    for i in range(n):
        h = 5.0 + ((i * 37) % 5) * 1.6
        sc.box((-42 + i * w, h / 2, z + ((i * 13) % 7)),
               (w * (0.8 + ((i * 11) % 3) * 0.2), h, 3.0), color)


def shadow(sc, x, z, r=0.42, col=(92, 134, 86)):
    """Soft flat patch under a character, so blocky feet read as planted."""
    y = 0.013
    pts = [(x - r, y, z - r * 0.55), (x + r, y, z - r * 0.55),
           (x + r, y, z + r * 0.55), (x - r, y, z + r * 0.55)]
    sc.quad(pts, col)


# ---------------------------------------------------------------- props
def tree(sc, x, z, s=1.0, leaf=(64, 148, 92), trunk=(118, 84, 56)):
    sc.box((x, 0.85 * s, z), (0.32 * s, 1.70 * s, 0.32 * s), trunk)
    sc.box((x, 1.95 * s, z), (1.55 * s, 1.05 * s, 1.55 * s), leaf)
    sc.box((x, 2.62 * s, z), (1.15 * s, 0.80 * s, 1.15 * s),
           tuple(min(255, int(c * 1.14)) for c in leaf))
    sc.box((x, 3.10 * s, z), (0.70 * s, 0.55 * s, 0.70 * s),
           tuple(min(255, int(c * 1.26)) for c in leaf))


def house(sc, x, z, w=3.0, h=2.4, d=2.6, wall=(226, 214, 196), roof=(196, 86, 78),
          front=-1.0, trim=None, awning=None, chimney=True):
    trim = trim or (250, 248, 240)
    sc.box((x, h / 2, z), (w, h, d), wall)
    sc.box((x, h + 0.34, z), (w + 0.26, 0.68, d + 0.26), roof)
    sc.box((x, h + 0.80, z), (w * 0.62, 0.28, d * 0.62), roof)
    fz = z + front * (d / 2 + 0.02)
    # door + frame
    sc.box((x, 0.66, fz), (0.84, 1.32, 0.06), trim)
    sc.box((x, 0.62, fz + front * 0.04), (0.66, 1.22, 0.05), (146, 102, 72))
    sc.box((x + 0.22, 0.62, fz + front * 0.08), (0.08, 0.08, 0.04), (232, 196, 108))
    # windows
    for sx in (-w * 0.32, w * 0.32):
        sc.box((x + sx, h * 0.66, fz), (0.78, 0.80, 0.06), trim)
        sc.box((x + sx, h * 0.66, fz + front * 0.04), (0.60, 0.62, 0.05),
               (118, 166, 208))
        sc.box((x + sx, h * 0.66, fz + front * 0.07), (0.62, 0.07, 0.03), trim)
        sc.box((x + sx, h * 0.66, fz + front * 0.07), (0.07, 0.62, 0.03), trim)
    if awning:
        sc.box((x, h * 0.66 + 0.52, fz + front * 0.16), (w * 0.92, 0.10, 0.42), awning)
    if chimney:
        sc.box((x + w * 0.30, h + 1.05, z + d * 0.18), (0.36, 0.80, 0.36),
               (168, 120, 100))


def lamp(sc, x, z):
    sc.box((x, 1.5, z), (0.12, 3.0, 0.12), (72, 72, 84))
    sc.box((x, 3.05, z), (0.42, 0.16, 0.42), (250, 226, 160))


def desk(sc, x, z, rot=0.0, color=(214, 178, 128)):
    sc.box((x, 0.72, z), (1.5, 0.10, 0.8), color, rot=rot)
    for sx in (-0.62, 0.62):
        for sz in (-0.3, 0.3):
            sc.box((x + sx, 0.36, z + sz), (0.10, 0.66, 0.10), (176, 142, 100), rot=rot)


def chair(sc, x, z, rot=0.0, color=(96, 172, 168)):
    sc.box((x, 0.44, z), (0.6, 0.08, 0.6), color, rot=rot)
    sc.box((x, 0.72, z - 0.26), (0.6, 0.6, 0.08), color, rot=rot)
    for sx in (-0.24, 0.24):
        for sz in (-0.24, 0.24):
            sc.box((x + sx, 0.22, z + sz), (0.08, 0.44, 0.08), (60, 60, 70), rot=rot)


def podium(sc, x, z, top=0.0):
    y = top
    sc.box((x, y + 0.62, z), (1.4, 1.24, 0.9), (176, 128, 92))
    sc.box((x, y + 1.30, z), (1.6, 0.12, 1.1), (206, 158, 112))
    sc.box((x - 0.46, y + 1.52, z + 0.08), (0.06, 0.42, 0.06), (90, 90, 100))
    sc.box((x - 0.46, y + 1.76, z + 0.08), (0.24, 0.15, 0.18), (60, 60, 70))


def crowd(sc, n=14, z0=4.0, spread=7.0, seed=3, colors=None):
    import random
    rng = random.Random(seed)
    colors = colors or [(232, 106, 92), (86, 156, 232), (240, 186, 74),
                        (110, 190, 140), (188, 132, 216), (240, 240, 240)]
    for i in range(n):
        x = -spread / 2 + spread * (i + rng.random() * 0.6) / n
        z = z0 + rng.random() * 1.8
        character(sc, x, z, s=0.92 + rng.random() * 0.12,
                  spec=dict(shirt=colors[i % len(colors)], hair=rng.choice(
                      [(68, 48, 38), (30, 30, 36), (168, 132, 84)]),
                      expr="idle"),
                  pose="idle", t=rng.random() * 3)


def sign(sc, x, y, z, w=1.6, h=0.7, color=(250, 248, 240)):
    sc.box((x, y, z), (w, h, 0.08), color)
    sc.box((x, y, z + 0.05), (w * 0.9, h * 0.14, 0.02), (70, 62, 70))

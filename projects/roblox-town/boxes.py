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

LIGHT = (-0.42, 0.86, 0.29)


def _norm(v):
    n = math.sqrt(sum(c * c for c in v)) or 1.0
    return tuple(c / n for c in v)


LIGHT = _norm(LIGHT)

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


class Scene3D:
    def __init__(self, canvas, pen, cam, ambient=0.62, tint=(1.0, 1.0, 1.0)):
        self.canvas, self.p, self.cam = canvas, pen, cam
        self.items = []
        self.ambient, self.tint = ambient, tint

    # ---------------------------------------------------------------- boxes
    def box(self, center, size, color, rot=0.0, glow=None, alpha=255, tag="", bias=0.0):
        self.items.append(("box", center, size, color, rot, alpha, tag, bias))

    def quad(self, pts, color, alpha=255, tag="", bias=0.0):
        self.items.append(("quad", pts, None, color, 0.0, alpha, tag, bias))

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
        for kind, a, b, color, rot, alpha, tag, bias in self.items:
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
                    draw.append((depth, pts, shade(color, k, self.tint)))
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
                draw.append((depth, pts, color))
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


def _face_blocks(sc, x, y, z, s, facing, spec, expr):
    """Eyes + mouth, drawn as thin boxes just in front of the head face."""
    fz = z + (0.26 * s if facing == 0 else -0.26 * s)
    dx = 0.0 if facing == 0 else 0.0
    eo = 0.125 * s
    sign = -1.0 if facing else 1.0          # -z is the camera side
    ez = fz + sign * 0.013
    ey = y + 0.035 * s
    for sx in (-eo, eo):
        if expr == "shock":
            sc.box((x + sx, ey, ez), (0.135 * s, 0.15 * s, 0.02), (252, 252, 252))
            sc.box((x + sx, ey, ez + sign * 0.008),
                   (0.07 * s, 0.08 * s, 0.02), DARK)
        elif expr == "happy":
            sc.box((x + sx, ey, ez), (0.13 * s, 0.045 * s, 0.02), DARK)
        else:
            sc.box((x + sx, ey, ez), (0.105 * s, 0.125 * s, 0.02), DARK)
        if spec.get("brows") and expr not in ("happy",):
            sc.box((x + sx, ey + 0.10 * s, ez), (0.12 * s, 0.028 * s, 0.02), spec["brows"])
    my = y - 0.115 * s
    if expr == "sad":
        sc.box((x, my, ez), (0.11 * s, 0.03 * s, 0.02), (150, 74, 78))
    elif expr == "shock":
        sc.box((x, my, ez), (0.10 * s, 0.10 * s, 0.02), (120, 60, 66))
    else:
        sc.box((x, my, ez), (0.17 * s, 0.038 * s, 0.02), (150, 74, 78))


def character(sc, x, z, y=0.0, s=1.0, spec=None, pose="idle", t=0.0, facing=0,
              tilt=0.0):
    """Blocky toy character. Returns head-top y for framing."""
    spec = spec or {}
    skin = spec.get("skin", SKIN)
    shirt = spec.get("shirt", (86, 156, 232))
    pants = spec.get("pants", (58, 74, 122))
    hair = spec.get("hair", (68, 48, 38))
    shoe = spec.get("shoe", (44, 44, 52))
    expr = spec.get("expr", "idle")
    hat = spec.get("hat")
    rot = math.radians(facing)

    walk = pose in ("walk", "run")
    ph = t * (8.0 if pose == "run" else 5.2)
    swing = math.sin(ph) * (0.34 if pose == "run" else 0.22) if walk else 0.0
    bob = abs(math.sin(ph)) * 0.05 if walk else 0.0
    jump = 0.0
    if pose == "jump":
        jump = 0.55 * math.sin(min(1.0, t / 0.7) * math.pi)
    lean = 0.0
    if pose == "hiccup":
        lean = 0.06 * math.sin(t * 9.0)
    if pose == "strain":
        bob = 0.02 * math.sin(t * 22.0)

    base = y + jump + bob
    # legs
    for i, side in enumerate((-1, 1)):
        off = swing * (1 if side > 0 else -1)
        sc.box((x + side * 0.115 * s, base + 0.47 * s, z + off),
               (0.19 * s, 0.88 * s, 0.21 * s), pants, rot=rot)
        sc.box((x + side * 0.115 * s, base + 0.06 * s, z + off + 0.03),
               (0.21 * s, 0.12 * s, 0.29 * s), shoe, rot=rot)
    # torso
    sc.box((x + lean, base + 1.22 * s, z), (0.50 * s, 0.62 * s, 0.30 * s), shirt, rot=rot)
    if spec.get("badge"):
        sc.box((x + 0.14 * lean, base + 1.30 * s, z - 0.17 * s),
               (0.11 * s, 0.13 * s, 0.02), (250, 250, 252), rot=rot)
    if spec.get("tie"):
        sc.box((x + lean, base + 1.28 * s, z - 0.16 * s),
               (0.07 * s, 0.34 * s, 0.02), spec["tie"], rot=rot)
    # arms
    arm_ang = {"point": (-100, 8), "shock": (-150, -150), "cheer": (-165, -165),
               "hiccup": (-30, -20), "hold": (-70, -70), "strain": (-20, -20)}.get(pose)
    for i, side in enumerate((-1, 1)):
        sx0, sy0 = x + side * 0.325 * s, base + 1.42 * s
        if arm_ang:
            ang = math.radians(arm_ang[i])
            ax = sx0 + side * -math.sin(ang) * 0.34 * s
            ay = sy0 + math.cos(ang) * 0.26 * s
            sc.box((ax, ay, z), (0.17 * s, 0.24 * s, 0.19 * s), shirt, rot=rot)
            sc.box((ax, ay - 0.24 * s, z), (0.17 * s, 0.32 * s, 0.19 * s), skin, rot=rot)
        else:
            sw = -swing * 0.6
            sc.box((sx0, sy0 - 0.20 * s, z + sw), (0.17 * s, 0.42 * s, 0.19 * s),
                   shirt, rot=rot)
            sc.box((sx0, sy0 - 0.55 * s, z + sw), (0.17 * s, 0.30 * s, 0.18 * s),
                   skin, rot=rot)
    # head
    hy = base + 1.70 * s
    sc.box((x + lean * 1.4, hy, z), (0.48 * s, 0.46 * s, 0.48 * s), skin, rot=rot)
    if hair:
        sc.box((x + lean * 1.4, hy + 0.24 * s, z), (0.50 * s, 0.10 * s, 0.50 * s), hair, rot=rot)
        sc.box((x + lean * 1.4, hy + 0.13 * s, z + 0.245 * s), (0.50 * s, 0.19 * s, 0.04 * s),
               hair, rot=rot)
        if spec.get("long_hair"):
            sc.box((x + lean * 1.4, hy - 0.10 * s, z - 0.25 * s),
                   (0.52 * s, 0.42 * s, 0.06 * s), hair, rot=rot)
    if hat:
        sc.box((x + lean * 1.4, hy + 0.28 * s, z), (0.54 * s, 0.11 * s, 0.54 * s), hat, rot=rot)
        sc.box((x + lean * 1.4, hy + 0.39 * s, z), (0.32 * s, 0.15 * s, 0.32 * s), hat, rot=rot)
    _face_blocks(sc, x + lean * 1.4, hy, z, s, facing, spec, expr)
    return base + 1.95 * s


def hills(sc, color=(150, 176, 168), z=46.0, n=7, w=14.0):
    """Distant blocky skyline so the horizon is never empty."""
    for i in range(n):
        h = 5.0 + ((i * 37) % 5) * 1.6
        sc.box((-42 + i * w, h / 2, z + ((i * 13) % 7)),
               (w * (0.8 + ((i * 11) % 3) * 0.2), h, 3.0), color)


def shadow(sc, x, z, r=0.42, ground=(0, 0.012, 0), color=(96, 116, 90)):
    """Soft flat patch under a character, so blocky feet read as planted."""
    y, col = ground[1], color
    pts = [(x - r, y, z - r * 0.55), (x + r, y, z - r * 0.55),
           (x + r, y, z + r * 0.55), (x - r, y, z + r * 0.55)]
    sc.quad(pts, col)


# ---------------------------------------------------------------- props
def tree(sc, x, z, s=1.0, leaf=(64, 148, 92)):
    sc.box((x, 0.9 * s, z), (0.34 * s, 1.8 * s, 0.34 * s), (118, 84, 56))
    sc.box((x, 2.1 * s, z), (1.5 * s, 1.2 * s, 1.5 * s), leaf)
    sc.box((x, 2.85 * s, z), (1.0 * s, 0.7 * s, 1.0 * s), tuple(int(c * 1.12) for c in leaf))


def house(sc, x, z, w=3.0, h=2.4, d=2.6, wall=(226, 214, 196), roof=(196, 86, 78),
          front=-1.0):
    sc.box((x, h / 2, z), (w, h, d), wall)
    sc.box((x, h + 0.42, z), (w + 0.30, 0.84, d + 0.30), roof)
    sc.box((x, h + 0.98, z), (w * 0.55, 0.30, d * 0.55), roof)
    fz = z + front * (d / 2 + 0.02)
    sc.box((x, 0.62, fz), (0.72, 1.24, 0.06), (150, 106, 74))
    for sx in (-w * 0.30, w * 0.30):
        sc.box((x + sx, h * 0.64, fz), (0.66, 0.66, 0.06), (120, 168, 208))
        sc.box((x + sx, h * 0.64, fz + front * 0.03), (0.50, 0.50, 0.02), (176, 212, 236))


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

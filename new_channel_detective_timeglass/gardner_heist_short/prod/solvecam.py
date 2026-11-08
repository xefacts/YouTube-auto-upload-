#!/usr/bin/env python3
"""Solve Dutch-room cameras: pick pos/look/fov so the hero painting fills a target
fraction of the vertical frame and the staged actors still land inside the gate.
Vertical 9:16 -> horizontal half-width = d*tan(fov/2)*0.5625."""
import math, json

W, D = 9.0, 11.0          # Dutch room
HX = -W / 2 + 0.16        # hero wall face
VER = {"vermeer": (-0.8, 2.5, 1.8, 2.05), "storm": (2.1, 2.75, 2.3, 2.75)}

ASP = 0.5625

def cam_basis(pos, look):
    f = [look[i] - pos[i] for i in range(3)]
    n = math.sqrt(sum(v * v for v in f)); f = [v / n for v in f]
    up = [0, 1, 0]
    r = [f[1] * up[2] - f[2] * up[1], f[2] * up[0] - f[0] * up[2], f[0] * up[1] - f[1] * up[0]]
    m = math.sqrt(sum(v * v for v in r)); r = [v / m for v in r]
    u = [r[1] * f[2] - r[2] * f[1], r[2] * f[0] - r[0] * f[2], r[0] * f[1] - r[1] * f[0]]
    return f, r, u

def ndc(pos, look, fov, p):
    f, r, u = cam_basis(pos, look)
    d = [p[i] - pos[i] for i in range(3)]
    z = sum(d[i] * f[i] for i in range(3))
    if z <= 0.05: return None
    ty = math.tan(math.radians(fov) / 2)
    tx = ty * ASP
    x = sum(d[i] * r[i] for i in range(3)) / (z * tx)
    y = sum(d[i] * u[i] for i in range(3)) / (z * ty)
    return (x, y, z)

def solve(art, fill, cx_frac, fov, eye_y, pts, want=None):
    """fill: painting height / frame height. cx_frac: camera distance as a fraction
    of the wall->far-wall span. pts: named world points that must stay in frame."""
    z0, y0, w, h = VER[art]
    best = None
    for fov_t in ([fov] if fov else range(26, 56, 2)):
        for dist in [x / 20 for x in range(20, 180)]:
            for dz in [x / 10 for x in range(-25, 26, 5)]:
                pos = [HX + dist, eye_y, z0 + dz]
                if pos[0] > W / 2 - 0.5: continue
                if abs(pos[2]) > D / 2 - 0.5: continue
                look = [HX, y0 - 0.05, z0]
                top = ndc(pos, look, fov_t, [HX, y0 + h / 2, z0])
                bot = ndc(pos, look, fov_t, [HX, y0 - h / 2, z0])
                if not top or not bot: continue
                got = (top[1] - bot[1]) / 2      # ndc span -> fraction of height
                err = abs(got - fill)
                # keep the painting centred vertically, camera off the z axis a little
                err += abs((top[1] + bot[1]) / 2) * 0.6
                pen = 0
                for nm, p in pts.items():
                    v = ndc(pos, look, fov_t, p)
                    if not v: pen += 9; continue
                    if abs(v[0]) > 0.86: pen += (abs(v[0]) - 0.86) * 12
                    if v[1] > 0.72 or v[1] < -0.74: pen += max(0, abs(v[1]) - 0.72) * 8
                err += pen * 1.0
                if best is None or err < best[0]:
                    best = (err, pos, look, fov_t, got)
    return best

JOBS = {
  # shot: (art, height-fill, eye height, fov or None, extra probe points)
  "s5a": ("storm", 0.42, 2.45, None, {"tA": (-0.2, 1.55, 3.7), "tB": (0.9, 1.55, 3.1)}),
  "s5b": ("storm", 0.52, 2.40, None, {"tA": (-0.4, 1.60, 3.0), "tB": (0.6, 1.60, 2.4)}),
  "s6a": ("vermeer", 0.50, 2.45, None, {"tA": (-2.9, 1.55, 0.3)}),
  "s6b": ("vermeer", 0.62, 2.42, None, {"tA": (-1.9, 1.60, 0.1)}),
  "s7a": ("vermeer", 0.72, 2.50, None, {"tA": (-2.4, 1.60, 0.2), "tB": (-2.5, 1.60, -1.6)}),
  "s7b": ("vermeer", 0.84, 2.46, None, {"tA": (-2.0, 1.60, 0.1), "tB": (-2.1, 1.60, -1.5)}),
  "s8a": ("storm", 0.40, 2.55, None, {"tA": (-0.9, 1.55, 2.6), "tB": (-0.2, 1.55, 3.4)}),
  "s8b": ("storm", 0.50, 2.45, None, {"tA": (-0.7, 1.55, 2.2), "tB": (0.1, 1.55, 3.0)}),
  "s10a": ("storm", 0.40, 2.55, None, {}),
  "s10b": ("vermeer", 0.55, 2.45, None, {}),
  "s11a": ("storm", 0.40, 1.95, None, {"vA": (-1.5, 1.55, 1.9), "vB": (-0.4, 1.55, 2.7)}),
  "s11b": ("storm", 0.52, 1.90, None, {"vA": (-1.2, 1.55, 1.5), "vB": (-0.2, 1.55, 2.3)}),
  "s12a": ("vermeer", 0.62, 2.52, None, {}),
  "s12b": ("vermeer", 0.72, 2.50, None, {}),
}
out = {}
for k, (art, fill, ey, fov, pts) in JOBS.items():
    err, pos, look, fov_t, got = solve(art, fill, 0, fov, ey, pts)
    out[k] = {"pos": [round(v, 2) for v in pos], "look": [round(v, 2) for v in look],
              "fov": round(fov_t, 1), "fill": round(got, 2), "err": round(err, 2)}
print(json.dumps(out, indent=1))
json.dump(out, open("work/camsolved.json", "w"), indent=1)

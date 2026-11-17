"""Numpy ray-caster for the blocky-shorts look.

Painter's-algorithm polygons cannot give the reference's soft studio light, so this
module casts one ray per pixel against the same cuboids the scenes already build.
It reads the exact `Scene3D.box()` calls (via a collector with the same API), keeps a
z-buffer, shades every pixel with key + sky light, drops soft ground shadows from
character footprints and darkens contact edges. Scenes and stages stay untouched.
"""
import math

import numpy as np

NEAR = 0.05


class Collector:
    """Drop-in for Scene3D that only records geometry."""

    def __init__(self, footprints=None):
        self.boxes = []
        self.footprints = footprints if footprints is not None else []

    # Scene3D API ---------------------------------------------------------
    def box(self, center, size, color, rot=0.0, glow=None, alpha=255, tag="", bias=0.0):
        self.boxes.append((center, size, tuple(color), float(rot), float(glow or 0.0)))

    def quad(self, pts, color, alpha=255, tag="", bias=0.0):
        """Ground quads are shadow footprints: soft blobs, not geometry."""
        xs = [p[0] for p in pts]
        zs = [p[2] for p in pts]
        cx = (min(xs) + max(xs)) / 2
        cz = (min(zs) + max(zs)) / 2
        rad = max(max(xs) - min(xs), max(zs) - min(zs)) * 0.62 + 1e-3
        self.footprints.append((cx, cz, rad, 0.55))

    def flush(self):
        pass

    def floor(self, y, color, size=60, x=0, z=0, grid=None):
        pass                                   # ground is analytic in the caster


def _rays(cam, W, H):
    f = cam.f
    ax = (np.arange(W, dtype=np.float32) + 0.5 - W / 2) / f
    by = -(np.arange(H, dtype=np.float32) + 0.5 - H / 2) / f
    A, B = np.meshgrid(ax, by)
    cy, sy = math.cos(cam.yaw), math.sin(cam.yaw)
    cp, sp = math.cos(cam.pitch), math.sin(cam.pitch)
    z1 = -B * sp + cp
    dx = A * cy + z1 * sy
    dy = B * cp + sp
    dz = -A * sy + z1 * cy
    return dx.astype(np.float32), dy.astype(np.float32), dz.astype(np.float32)


def render(sky_rgb, cam, coll, ground, light=(-0.34, 0.80, -0.50), amb=0.24, kd=0.52,
           ks=0.16, fill=(0.42, 0.52, 0.72), haze=None, haze_from=14.0, haze_to=52.0,
           edge=0.86, ss=1, top=-1e9, only_ground=False, tint=(1.0, 1.0, 1.0)):
    """Composite shaded geometry over `sky_rgb` (H, W, 3 uint8). Returns uint8 image."""
    H, W = sky_rgb.shape[:2]
    if ss > 1:
        big = np.repeat(np.repeat(sky_rgb, ss, axis=0), ss, axis=1)
        out = render(big, cam, coll, ground, light, amb, kd, ks, fill, haze, haze_from,
                     haze_to, edge, 1, top, only_ground, tint)
        return out.reshape(H, ss, W, ss, 3).mean(axis=(1, 3)).astype(np.uint8)

    dx, dy, dz = _rays(cam, W, H)
    ox, oy, oz = cam.x, cam.y, cam.z
    depth = np.full((H, W), np.inf, np.float32)
    nrm = np.zeros((H, W, 3), np.float32)
    col = np.zeros((H, W, 3), np.float32)
    hit = np.zeros((H, W), bool)
    emis = np.zeros((H, W), np.float32)

    # ---- ground plane (y = 0) ------------------------------------------
    with np.errstate(divide="ignore", invalid="ignore"):
        tg = np.where(dy < -1e-4, -oy / dy, np.inf).astype(np.float32)
    gmask = np.isfinite(tg) & (tg > 0)
    if gmask.any():
        gx = ox + dx * tg
        gz = oz + dz * tg
        gcol = ground(gx, gz) if callable(ground) else np.broadcast_to(
            np.array(ground, np.float32), (H, W, 3)).copy()
        shade = np.full((H, W), 1.0, np.float32)
        for fx, fz, r, s in coll.footprints:
            d2 = (gx - fx) ** 2 + (gz - fz) ** 2
            shade *= 1.0 - s * np.exp(-d2 / (r * r))
        shade = np.clip(shade, 0.25, 1.0)[..., None]
        gc = gcol.astype(np.float32) * shade * (amb + kd * 0.92)
        sel = gmask
        depth[sel] = tg[sel]
        col[sel] = np.clip(gc[sel], 0, 255)
        hit[sel] = True
        nrm[sel] = (0, 1, 0)

    # ---- boxes ---------------------------------------------------------
    L = np.array(light, np.float32)
    L /= np.linalg.norm(L)
    f = cam.f
    for center, size, color, rot, glow in coll.boxes:
        cx, cyy, cz = center
        sx, sy, sz = size
        if sy < 0.0 or sx <= 0 or sz <= 0:
            continue
        hx, hy, hz = sx / 2, sy / 2, sz / 2
        cr, sr = math.cos(rot), math.sin(rot)
        # screen bbox from the 8 corners
        xs, ys = [], []
        for ixx in (-hx, hx):
            for iyy in (-hy, hy):
                for izz in (-hz, hz):
                    wx = cx + ixx * cr - izz * sr
                    wz = cz + ixx * sr + izz * cr
                    pj = cam.project((wx, cyy + iyy, wz))
                    if pj is not None:
                        xs.append(pj[0])
                        ys.append(pj[1])
        if len(xs) < 8:
            continue
        x0, x1 = int(max(0, min(xs) - 1)), int(min(W, max(xs) + 2))
        y0, y1 = int(max(0, min(ys) - 1)), int(min(H, max(ys) + 2))
        if x1 <= x0 or y1 <= y0:
            continue
        rdx = dx[y0:y1, x0:x1]
        rdy = dy[y0:y1, x0:x1]
        rdz = dz[y0:y1, x0:x1]
        # into object space
        px = ox - cx
        py = oy - cyy
        pz = oz - cz
        lox = px * cr + pz * sr
        loz = -px * sr + pz * cr
        ldx = rdx * cr + rdz * sr
        ldz = -rdx * sr + rdz * cr
        ldy = rdy
        with np.errstate(divide="ignore", invalid="ignore"):
            ix = 1.0 / ldx
            iy = 1.0 / ldy
            iz = 1.0 / ldz
            tx1 = (-hx - lox) * ix
            tx2 = (hx - lox) * ix
            ty1 = (-hy - py) * iy
            ty2 = (hy - py) * iy
            tz1 = (-hz - loz) * iz
            tz2 = (hz - loz) * iz
        tmin = np.maximum(np.maximum(np.minimum(tx1, tx2), np.minimum(ty1, ty2)),
                          np.minimum(tz1, tz2))
        tmax = np.minimum(np.minimum(np.maximum(tx1, tx2), np.maximum(ty1, ty2)),
                          np.maximum(tz1, tz2))
        m = (tmin > NEAR) & (tmin < tmax)
        if not m.any():
            continue
        dz_sub = depth[y0:y1, x0:x1]
        m &= tmin < dz_sub
        if not m.any():
            continue
        # normal: axis that produced tmin
        ax_x = np.minimum(tx1, tx2)
        ax_y = np.minimum(ty1, ty2)
        ax_z = np.minimum(tz1, tz2)
        nx = np.where(ax_x >= np.maximum(ax_y, ax_z),
                      np.where(ldx > 0, -1.0, 1.0), 0.0)
        ny = np.where((ny_ := (ax_y > np.maximum(ax_x, ax_z))), np.where(ldy > 0, -1.0, 1.0),
                      0.0)
        nz = np.where((ax_z > np.maximum(ax_x, ax_y)) & (ny_ == 0),
                      np.where(ldz > 0, -1.0, 1.0), 0.0)
        # back to world
        wnx = nx * cr - nz * sr
        wnz = nx * sr + nz * cr
        wny = ny
        nl = np.clip(wnx * L[0] + wny * L[1] + wnz * L[2], 0, 1)
        sky_t = np.clip(0.55 + 0.45 * wny, 0, 1)
        k = amb + kd * nl + ks * sky_t
        wy = (oy + rdy * tmin) if False else None
        # mild rim light so silhouettes separate from the background
        # soft vertical falloff: the studio light sits high, hems go darker
        yy = oy + rdy * tmin
        k = k * (0.90 + 0.10 * np.clip((yy + 0.2) / 2.2, 0, 1))
        if glow > 0:
            k = np.maximum(k, glow)
        base = np.array(color, np.float32)
        c = base[None, None, :] * k[..., None] * np.asarray(tint, np.float32)
        if haze is not None:
            t = np.clip((tmin - haze_from) / (haze_to - haze_from), 0, 0.68)
            c = c + (np.array(haze, np.float32)[None, None, :] - c) * t[..., None]
        sel = m
        depth[y0:y1, x0:x1][sel] = tmin[sel]
        col[y0:y1, x0:x1][sel] = np.clip(c[sel], 0, 255)
        nrm[y0:y1, x0:x1][sel, 0] = wnx[sel]
        nrm[y0:y1, x0:x1][sel, 1] = wny[sel]
        nrm[y0:y1, x0:x1][sel, 2] = wnz[sel]
        hit[y0:y1, x0:x1][sel] = True
        emis[y0:y1, x0:x1][sel] = glow

    out = sky_rgb.astype(np.float32).copy()
    if hit.any():
        img = np.where(hit[..., None], col, out)
        # contact edges: darken where depth jumps to a much nearer neighbour
        if edge < 1.0:
            near = np.minimum(np.minimum(
                np.roll(np.roll(depth, 1, 0), 0, 1), np.roll(np.roll(depth, -1, 0), 0, 1)),
                np.minimum(np.roll(np.roll(depth, 0, 0), 1, 1),
                           np.roll(np.roll(depth, 0, 0), -1, 1)))
            jump = (depth - near) / np.maximum(near, 0.2)
            em = (jump > 0.10) & hit & (depth < 60)
            img[em] *= edge
        out = img
    return np.clip(out, 0, 255).astype(np.uint8)

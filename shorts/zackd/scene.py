"""Scene: "What actually happens when you tap your card?" - Zack D Films style.

Every shot is a pure function of local time t in [0, 1] returning
(objects, camera, render_kwargs). The renderer is engine.py.
"""
from __future__ import annotations

import math

import numpy as np

import art
from engine import (Camera, Mesh, Obj, Rx, Ry, Rz, S, T, cylinder, disc, ease_in_out,
                    ease_out, mat, plane, plate, sphere, superellipsoid, torus, _vertex_normals)

# --------------------------------------------------------------------------- #
# shared assets (built once)
# --------------------------------------------------------------------------- #

CARD_W, CARD_H, CARD_T = 1.86, 1.17, 0.05


def _bend(mesh, kx=0.012, ky=0.018):
    m = Mesh(mesh.verts.copy(), mesh.tris, mesh.normals.copy(), mesh.uvs)
    v = m.verts
    v[:, 2] += kx * (v[:, 0] ** 2) + ky * (v[:, 1] ** 2)
    m.normals = _vertex_normals(m.verts, m.tris)
    return m


CARD_FRONT = _bend(plate(CARD_W, CARD_H, CARD_T, r=0.16, bevel=0.014, n_corner=12, faces="front"))
CARD_BACK = _bend(plate(CARD_W, CARD_H, CARD_T, r=0.16, bevel=0.014, n_corner=12, faces="back"))
CHIP_MESH = superellipsoid(0.21, 0.15, 0.0075, e1=0.30, e2=0.30, seg_u=56, seg_v=10)
BAR_MESH = plate(0.33, 0.026, 0.009, r=0.011, bevel=0.002, n_corner=4)
_COIN0 = cylinder(0.20, 0.032, 56)
_vc = _COIN0.verts.copy()
_vc = np.stack([_vc[:, 0], _vc[:, 2], -_vc[:, 1]], -1)          # lie flat: normal +Y
_nc = np.stack([_COIN0.normals[:, 0], _COIN0.normals[:, 2], -_COIN0.normals[:, 1]], -1)
COIN_MESH = Mesh(_vc, _COIN0.tris, _nc, _COIN0.uvs)
COIN_RIM = torus(0.196, 0.016, 56, 10)
RING_MESH = torus(1.0, 0.013, 96, 8)
GROUND_MESH = plane(18.0, subdiv=6)

TEX_CARD = art.card_face(1200, 756)
TEX_GROUND = art.radial_fade(256, power=3.0, inner=0.16, outer=0.0)
TEX_SCREEN = art.terminal_screen()
TEX_VAULT_LABEL = art.black_text("ATLAS  VAULT  07", size=(900, 220), color=(255, 214, 140), mono=True, glow=0.2)
TEX_LEDGER = art.ledger_panel()

# --------------------------------------------------------------------------- #
# materials
# --------------------------------------------------------------------------- #

M_CARD = mat(base=(1.0, 1.0, 1.0), rough=0.28, metal=0.30, clearcoat=0.85, tex=TEX_CARD)
M_CARD_BACK = mat(base=(0.030, 0.034, 0.045), rough=0.26, metal=0.55, clearcoat=0.85)
M_GOLD = mat(base=(1.0, 0.74, 0.30), rough=0.16, metal=1.0)
M_CHIPBODY = mat(base=(0.72, 0.53, 0.20), rough=0.32, metal=1.0)
M_GOLD_SOFT = mat(base=(0.95, 0.72, 0.32), rough=0.30, metal=1.0)
M_BRASS = mat(base=(1.0, 0.76, 0.32), rough=0.20, metal=1.0)
M_STEEL = mat(base=(0.30, 0.33, 0.38), rough=0.30, metal=1.0)
M_STEEL_DARK = mat(base=(0.03, 0.033, 0.045), rough=0.55, metal=0.70)
M_DARKPLASTIC = mat(base=(0.035, 0.038, 0.05), rough=0.32, metal=0.20, clearcoat=0.6)
M_GROUND = mat(base=(0.10, 0.13, 0.20), rough=0.78, metal=0.12, tex=TEX_GROUND)
M_NEON = mat(base=(0.01, 0.02, 0.03), rough=0.5, emis=(0.20, 0.74, 1.0), emis_str=3.0)
M_GOLDLIGHT = mat(base=(0.02, 0.02, 0.02), rough=0.6, emis=(1.0, 0.70, 0.26), emis_str=1.2)
M_SCREEN = mat(base=(0.02, 0.02, 0.03), rough=0.20, metal=0.0, emis=(1, 1, 1), emis_str=2.4, tex=TEX_SCREEN)


def card_objects(m, with_bars=True):
    """Card (front art + dark back) with its chip."""
    out = [Obj(CARD_FRONT, M_CARD, m, "card"),
           Obj(CARD_BACK, M_CARD_BACK, m, "card_back")]
    cm = m @ T(-0.52, 0.095, 0.030)
    out.append(Obj(CHIP_MESH, M_CHIPBODY, cm, "chip"))
    if with_bars:
        for k in range(4):
            y = -0.090 + k * 0.060
            out.append(Obj(BAR_MESH, M_GOLD, cm @ T(0, y, 0.0095), "chipbar"))
    return out


def coin(x=0.0, y=1.0, z=0.0, rot=(0, 0, 0), scale=1.0, mmat=None):
    m = mmat or M_GOLD
    base = T(x, y, z) @ Rz(rot[2]) @ Rx(rot[0]) @ Ry(rot[1]) @ S(scale)
    return [Obj(COIN_MESH, m, base, "coin"), Obj(COIN_RIM, m, base, "coin_rim")]


def studio(ground_y=-1.05, ground=False, mmat=None):
    objs = []
    if ground:
        objs.append(Obj(GROUND_MESH, mmat or M_GROUND, T(0, ground_y, 0), "ground"))
    return objs


STUDIO_LIGHTS = [
    dict(pos=(3.1, 4.3, 3.6), color=(1.0, 0.96, 0.90), power=5.6, radius=5.0, shadow=True),
    dict(pos=(-4.2, 1.9, 2.6), color=(0.32, 0.60, 1.0), power=2.4, radius=6.0, shadow=False),
    dict(pos=(0.6, 2.6, -4.6), color=(1.0, 0.44, 0.18), power=3.0, radius=6.0, shadow=False),
]

# --------------------------------------------------------------------------- #
# shots
# --------------------------------------------------------------------------- #


def shot_hook(t):
    """Wide hero: the card floating over a black table, coins drifting."""
    objs = studio()
    e = ease_in_out(t)
    spin = math.radians(-16 + 20 * t)
    tilt = math.radians(-8 + 5 * e)
    lift = 0.025 * math.sin(t * math.pi * 2)
    m = T(0.0, 1.05 + lift, 0.0) @ Ry(spin) @ Rx(tilt) @ Rz(math.radians(-3))
    objs += card_objects(m)
    for i, (a0, rr, yy) in enumerate(((0.5, 1.45, 0.52), (2.5, 1.62, 1.55), (4.2, 1.30, 0.88), (5.6, 1.75, 1.28))):
        a = a0 + t * 0.5
        objs += coin(math.cos(a) * rr, yy + 0.05 * math.sin(a * 2 + i), math.sin(a) * rr - 0.45,
                     rot=(math.radians(72), a * 2.2, 0), scale=0.72)
    cam = Camera(pos=(0.0, 1.50 - 0.10 * e, 5.85 - 0.75 * e), target=(0, 1.02, 0), fov=33,
                 focus=5.3 - 0.75 * e, aperture=0.12)
    return objs, cam, dict(shadow_bounds=6.0)


def shot_chip(t):
    """Macro: the chip wakes up, rings of radio energy expand."""
    objs = studio(ground=False)
    e = ease_out(t)
    m = T(0.0, 0.0, 0.0) @ Ry(math.radians(-22 + 10 * t)) @ Rx(math.radians(5 - 7 * t)) @ Rz(math.radians(-2))
    objs += card_objects(m)
    mchip = m @ T(-0.52, 0.095, 0.030)
    for k in range(4):
        phase = (t * 1.4 + k * 0.25) % 1.0
        s = 0.10 + phase * 2.4
        fade = max(0.0, 1.0 - phase) ** 1.4
        mm = M_NEON.copy()
        mm["emis_str"] = 0.3 + 3.4 * fade
        objs.append(Obj(RING_MESH, mm, mchip @ T(0, 0, 0.015) @ S(s, s, s) @ Rx(math.radians(90)), "ring"))
    cam = Camera(pos=(0.42 + 0.12 * t, 0.5, 2.55 - 0.30 * e), target=(-0.34, 0.13, 0.0), fov=30,
                 focus=2.5, aperture=0.16)
    return objs, cam, dict(shadow_bounds=5.0, bloom=1.1, exposure=0.95)


def shot_terminal(t):
    """The card taps the payment terminal - beep."""
    objs = studio(ground_y=-1.2)
    e = ease_in_out(t)
    tb = T(0.22, 1.02, -0.45) @ Rx(math.radians(-12)) @ Ry(math.radians(-18))
    objs.append(Obj(plate(1.24, 1.92, 0.15, r=0.15, bevel=0.02, n_corner=8), M_DARKPLASTIC, tb, "term"))
    objs.append(Obj(plate(1.00, 1.44, 0.02, r=0.09, bevel=0.006, n_corner=8), M_SCREEN,
                    tb @ T(0, 0.14, 0.082), "screen"))
    objs.append(Obj(torus(0.34, 0.018, 64, 8), M_STEEL, tb @ T(0, -0.60, 0.085), "slot"))
    objs.append(Obj(torus(0.30, 0.010, 64, 8), M_NEON, tb @ T(0, -0.60, 0.095), "slotlight"))
    # card taps in from the lower right
    ang = math.radians(56 - 22 * e)
    cm = T(-0.86 - 0.34 * (1 - e), 0.42 + 0.26 * e, 0.86 - 0.34 * e) @ Ry(math.radians(30)) @ Rx(math.radians(-56 + 16 * e)) @ Rz(ang)
    objs += card_objects(cm)
    flash = max(0.0, math.sin(max(0.0, (t - 0.5)) * math.pi * 1.7)) if t > 0.5 else 0.0
    if flash > 0.02:
        mm = M_NEON.copy()
        mm["emis_str"] = 6.0 * flash
        objs.append(Obj(torus(0.30, 0.02, 64, 8), mm,
                        cm @ T(-0.52, 0.095, 0.05) @ S(1 + 0.9 * flash), "flash"))
    lights = [dict(STUDIO_LIGHTS[0]),
              dict(pos=(-1.15, 1.30, 0.60), color=(0.30, 0.68, 1.0), power=2.6 + 5.0 * flash, radius=2.4, shadow=False),
              dict(pos=(2.4, 2.4, -3.0), color=(1.0, 0.45, 0.20), power=3.0, radius=6.0, shadow=False)]
    cam = Camera(pos=(0.62, 1.62, 4.0 - 0.45 * e), target=(-0.05, 1.02, 0), fov=34,
                 focus=3.9, aperture=0.11, exposure=1.0 + 0.3 * flash)
    return objs, cam, dict(lights=lights, shadow_bounds=6.0)


def shot_energy(t):
    """Extreme macro: the chip harvesting power, arcs crawling over it."""
    objs = studio(ground=False)
    objs += card_objects(T(0, 0, 0) @ Ry(math.radians(26)) @ Rx(math.radians(-7)))
    mchip = Ry(math.radians(26)) @ Rx(math.radians(-7)) @ T(-0.52, 0.095, 0.030)
    pulse = 0.5 + 0.5 * math.sin(t * math.pi * 4)
    for k in range(3):
        s = 0.09 + ((t * 1.8 + k * 0.34) % 1.0) * 0.55
        mm = M_NEON.copy()
        mm["emis_str"] = 0.8 + 3.4 * max(0.0, 1 - (s - 0.09) / 0.55)
        objs.append(Obj(RING_MESH, mm, mchip @ T(0, 0, 0.012) @ S(s, s, s) @ Rx(math.radians(90)), "arc"))
    lights = [dict(pos=(1.9, 1.5, 1.6), color=(1.0, 0.94, 0.86), power=3.4, radius=2.4, shadow=True),
              dict(pos=(0.4, 0.5, -1.8), color=(0.30, 0.70, 1.0), power=2.2 + 1.4 * pulse, radius=2.2, shadow=False),
              dict(pos=(-1.6, 1.0, 1.0), color=(1.0, 0.55, 0.2), power=2.4, radius=2.6, shadow=False)]
    cam = Camera(pos=(-0.05 + 0.12 * t, 0.56, 2.7), target=(-0.60 - 0.02 * t, 0.16, 0.05), fov=32,
                 focus=2.7, aperture=0.12, exposure=0.90)
    return objs, cam, dict(lights=lights, shadow_bounds=3.0, bloom=1.15)


def _text_plate(tex, w, h):
    return Obj(plate(w, h, 0.008, r=0.015, bevel=0.002, n_corner=4),
               mat(base=(0.012, 0.016, 0.026), rough=0.5, metal=0.1, emis=(1, 1, 1), emis_str=1.15, tex=tex))


def shot_data(t):
    """Data flying: the encrypted message streams past in 3D space."""
    objs = studio(ground=False)
    objs += card_objects(T(0.02, -0.06, -1.85) @ Ry(math.radians(-14)) @ Rx(math.radians(7)))
    rows = [("TOKEN  9F2C", (0.50, 0.15), -0.24, 0.58, 0.10, -12),
            ("$1,480.00", (0.46, 0.14), 0.30, 0.24, 0.40, 10),
            ("LIMIT  6,000", (0.48, 0.15), 0.28, -0.28, 0.66, -7),
            ("CHIP  AUTH OK", (0.50, 0.15), -0.28, -0.50, 0.92, 9)]
    for i, (s_, (w, h), x, y, z, ry) in enumerate(rows):
        o = _text_plate(art.black_text(s_, size=(900, 240), color=(150, 226, 255), glow=0.35, mono=(i % 2 == 0)), w, h)
        drift = 0.10 * math.sin(t * 2.4 + i * 1.7)
        o.matrix = T(x * (1.0 - 0.06 * t), y + drift, z) @ Ry(math.radians(ry)) @ Rx(math.radians(5))
        objs.append(o)
    lights = [dict(pos=(2.6, 3.4, 3.0), color=(0.85, 0.94, 1.0), power=4.0, radius=5.0, shadow=True),
              dict(pos=(-3.0, 1.2, 2.0), color=(0.30, 0.62, 1.0), power=2.6, radius=5.0, shadow=False),
              dict(pos=(0.4, 1.8, -4.0), color=(1.0, 0.45, 0.2), power=2.4, radius=6.0, shadow=False)]
    cam = Camera(pos=(0.0, 0.72, 4.5 - 0.5 * ease_in_out(t)), target=(0.0, 0.05, 0), fov=36,
                 focus=3.6, aperture=0.10)
    return objs, cam, dict(lights=lights, shadow_bounds=6.0, bloom=1.0,
                           bg_top=(0.010, 0.018, 0.032), bg_bot=(0.002, 0.003, 0.006))


def _vault_door(objs, base, spin=0.0):
    """Heavy brass-and-steel vault door."""
    steel = mat(base=(0.06, 0.065, 0.085), rough=0.62, metal=0.55)
    steel_lite = mat(base=(0.10, 0.11, 0.13), rough=0.55, metal=0.75)
    objs.append(Obj(cylinder(1.30, 0.30, 72), steel, base @ Rx(math.radians(90)), "door"))
    objs.append(Obj(torus(1.31, 0.075, 72, 14), M_BRASS, base, "rim"))
    objs.append(Obj(torus(0.96, 0.030, 72, 12), M_BRASS, base @ T(0, 0, 0.155), "goldring"))
    objs.append(Obj(cylinder(0.21, 0.24, 40), M_BRASS, base @ T(0, 0, 0.14) @ Rx(math.radians(90)), "hub"))
    objs.append(Obj(torus(0.21, 0.022, 40, 8), M_GOLD, base @ T(0, 0, 0.26), "hubring"))
    for k in range(3):
        a = spin + k * 2 * math.pi / 3
        objs.append(Obj(plate(1.46, 0.105, 0.07, r=0.045, bevel=0.012, n_corner=4), M_BRASS,
                        base @ T(0, 0, 0.135) @ Rz(a), "spoke"))
        objs.append(Obj(cylinder(0.048, 0.05, 14), M_GOLDLIGHT,
                        base @ T(math.cos(a) * 0.78, math.sin(a) * 0.78, 0.155) @ Rx(math.radians(90)), "bolt"))
    for k in range(10):
        a = k * math.pi / 5 + math.pi / 10
        objs.append(Obj(cylinder(0.026, 0.028, 10), M_STEEL,
                        base @ T(math.cos(a) * 1.16, math.sin(a) * 1.16, 0.155) @ Rx(math.radians(90)), "rivet"))
    objs.append(Obj(plate(0.86, 0.20, 0.02, r=0.02, bevel=0.004, n_corner=4),
                    mat(base=(0.02, 0.02, 0.025), rough=0.35, metal=0.4, emis=(1, 1, 1), emis_str=0.55,
                        tex=TEX_VAULT_LABEL),
                    base @ T(0, -0.62, 0.165), "label"))


def shot_vault(t):
    """The vault door - where everyone thinks the money is."""
    objs = studio(ground_y=-1.35)
    e = ease_in_out(t)
    base = T(0.0, 1.10, -0.25) @ Ry(math.radians(-15 + 7 * t)) @ Rx(math.radians(4))
    _vault_door(objs, base, spin=math.radians(-150 * e))
    lights = [dict(pos=(2.8, 3.2, 3.6), color=(1.0, 0.93, 0.84), power=3.6, radius=5.0, shadow=True),
              dict(pos=(-3.2, 1.4, 2.2), color=(0.26, 0.52, 1.0), power=2.2, radius=6.0, shadow=False),
              dict(pos=(-0.4, 3.0, -3.0), color=(1.0, 0.34, 0.10), power=4.6, radius=6.0, shadow=False)]
    cam = Camera(pos=(0.0, 1.62, 7.9 - 0.9 * e), target=(0.0, 1.10, 0), fov=31,
                 focus=7.4 - 0.9 * e, aperture=0.09)
    return objs, cam, dict(lights=lights, shadow_bounds=7.0)


def shot_ledger(t):
    """Reveal: there is no cash in there - only numbers."""
    objs = studio(ground=False)
    e = ease_in_out(t)
    wall = T(0.0, 1.18, -1.70) @ Ry(math.radians(-5))
    objs.append(Obj(plate(2.55, 1.85, 0.04, r=0.03, bevel=0.004, n_corner=4),
                    mat(base=(1.0, 1.0, 1.0), rough=0.35, metal=0.1, emis=(1, 1, 1), emis_str=0.75,
                        tex=TEX_LEDGER), wall, "ledger"))
    objs.append(Obj(plate(2.85, 2.15, 0.09, r=0.05, bevel=0.012, n_corner=4), M_STEEL_DARK,
                    wall @ T(0, 0, -0.06), "frame"))
    for i in range(6):
        a = i * 1.05 + t * 0.65
        objs += coin(math.cos(a) * (0.62 + 0.10 * (i % 3)), 0.92 + 0.26 * math.sin(a * 1.3) + 0.04 * i,
                     -0.35 + 0.30 * math.sin(a * 0.8),
                     rot=(math.radians(66), a * 1.6, math.radians(14)), scale=0.85)
    lights = [dict(pos=(1.9, 2.7, 2.8), color=(0.52, 0.76, 1.0), power=2.0, radius=4.0, shadow=True),
              dict(pos=(0.0, 1.3, -1.35), color=(0.28, 0.68, 1.0), power=3.2, radius=2.6, shadow=False),
              dict(pos=(-2.4, 1.5, 2.2), color=(1.0, 0.55, 0.25), power=1.6, radius=4.0, shadow=False)]
    cam = Camera(pos=(0.0, 1.35, 2.55 - 0.5 * e), target=(0.0, 1.12, -0.4), fov=34,
                 focus=2.75 - 0.45 * e, aperture=0.10)
    return objs, cam, dict(lights=lights, shadow_bounds=5.0, bloom=0.95,
                           bg_top=(0.008, 0.014, 0.026), bg_bot=(0.002, 0.003, 0.005))


def shot_outro(t):
    """Card spinning in the dark, coins orbiting - slow pull back."""
    objs = studio()
    e = ease_in_out(t)
    m = T(0.0, 1.05, 0.0) @ Ry(math.radians(-30 + 74 * e)) @ Rx(math.radians(-8 + 6 * e))
    objs += card_objects(m)
    for i in range(6):
        a = i * 1.05 + t * 1.0
        rr = 1.30 + 0.16 * (i % 3)
        objs += coin(math.cos(a) * rr, 1.02 + 0.32 * math.sin(a * 1.7 + i), math.sin(a) * rr,
                     rot=(math.radians(72), a * 2.0, 0), scale=0.66)
    cam = Camera(pos=(0.0, 1.58 + 0.12 * e, 6.1 + 1.0 * e), target=(0, 1.02, 0), fov=34,
                 focus=6.1 + 1.0 * e, aperture=0.12, exposure=1.02)
    return objs, cam, dict(shadow_bounds=6.5)


SHOTS = [
    ("hook", shot_hook),
    ("chip", shot_chip),
    ("terminal", shot_terminal),
    ("energy", shot_energy),
    ("data", shot_data),
    ("vault", shot_vault),
    ("ledger", shot_ledger),
    ("outro", shot_outro),
]

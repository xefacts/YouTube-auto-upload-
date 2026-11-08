"""City environment system for engine2: modular, reusable building/road/
prop generators with foreground/midground/background depth, built from
Scene2.mesh.add_quad_box (so they get bevels, z-buffer occlusion, point
lights, faux-AO and blob shadows automatically, same as the character).

Everything here is still boxes (no textures/UV mapping -- this renderer has
none), but facades are now built from many small boxes (window grids,
door insets, cornice trim, roof caps) rather than one flat-colored block,
which is the real, geometry-level way this class of renderer can show
"detailed facades" honestly.
"""
from __future__ import annotations
import math
import random


ROAD = (58, 58, 64)
LANE_LINE = (235, 205, 90)
SIDEWALK = (182, 178, 165)
CURB = (150, 146, 134)
TRUNK = (92, 62, 40)
LEAVES = (58, 120, 55)
LAMP_POST = (70, 70, 78)
LAMP_HEAD = (235, 225, 190)
WINDOW_LIT = (255, 221, 130)
WINDOW_DARK = (70, 95, 120)
DOOR = (90, 55, 40)


def _shuffled(seed, items):
    rnd = random.Random(seed)
    items = list(items)
    rnd.shuffle(items)
    return items


WALL_PALETTE = [(196, 142, 96), (150, 160, 172), (176, 92, 78), (120, 140, 118), (200, 188, 150)]
ROOF_PALETTE = [(90, 60, 55), (70, 78, 90), (110, 70, 50)]


def build_building(mesh, cx, cz, w, h, d, seed=0, lit_ratio=0.45, yaw=0.0):
    rnd = random.Random(seed)
    wall = WALL_PALETTE[seed % len(WALL_PALETTE)]
    roof = ROOF_PALETTE[seed % len(ROOF_PALETTE)]
    trim = tuple(min(255, int(c * 0.65)) for c in wall)

    mesh.add_quad_box((cx, h / 2, cz), (w / 2, h / 2, d / 2), wall, yaw=yaw, bevel=0.06)
    mesh.add_quad_box((cx, h + 0.06, cz), (w / 2 + 0.05, 0.06, d / 2 + 0.05), roof, yaw=yaw)

    rows = max(1, int(h // 1.0))
    cols = max(1, int(w // 0.9))
    win_w = (w * 0.86) / cols
    win_h = min(0.55, h / rows * 0.55)
    for r in range(rows):
        wy = h * 0.18 + r * (h / rows)
        if wy > h - 0.3:
            continue
        for c in range(cols):
            wx = -w / 2 + win_w * 0.6 + c * (w * 0.86 / cols)
            lit = rnd.random() < lit_ratio
            color = WINDOW_LIT if lit else WINDOW_DARK
            local = (wx, wy - h / 2, d / 2 + 0.015)
            world = _rotate_local(local, cx, cz, yaw)
            mesh.add_quad_box((world[0], wy, world[1]), (win_w * 0.34, win_h * 0.34, 0.012),
                               color, yaw=yaw, shade_top=1.0, shade_side=1.0, shade_bottom=1.0)
            mesh.add_quad_box((world[0], wy, world[1] - 0.004), (win_w * 0.42, win_h * 0.42, 0.006),
                               trim, yaw=yaw)

    door_local = (0, -h / 2 + 0.42, d / 2 + 0.02)
    dw = _rotate_local(door_local, cx, cz, yaw)
    mesh.add_quad_box((dw[0], 0.42, dw[1]), (0.22, 0.42, 0.02), DOOR, yaw=yaw)


def _rotate_local(local_xz, cx, cz, yaw_deg):
    x, y, z = local_xz
    yr = math.radians(yaw_deg)
    wx = cx + x * math.cos(yr) + z * math.sin(yr)
    wz = cz - x * math.sin(yr) + z * math.cos(yr)
    return (wx, wz)


def build_road(mesh, x0, z0, x1, z1, width=3.0):
    mx, mz = (x0 + x1) / 2, (z0 + z1) / 2
    length = math.hypot(x1 - x0, z1 - z0)
    yaw = math.degrees(math.atan2(x1 - x0, z1 - z0))
    mesh.add_quad_box((mx, -0.02, mz), (width / 2, 0.02, length / 2), ROAD, yaw=yaw)
    mesh.add_quad_box((mx, -0.005, mz), (0.06, 0.006, length / 2 * 0.92), LANE_LINE, yaw=yaw)
    for side in (-1, 1):
        sx = mx + side * (width / 2 + 0.75)
        mesh.add_quad_box((sx, 0.04, mz), (0.7, 0.04, length / 2), SIDEWALK, yaw=yaw)
        mesh.add_quad_box((sx + side * 0.7, 0.03, mz), (0.04, 0.05, length / 2), CURB, yaw=yaw)


def build_tree(mesh, x, z, scale_=1.0, seed=0):
    rnd = random.Random(seed)
    th = 0.55 * scale_
    mesh.add_quad_box((x, th / 2, z), (0.06 * scale_, th / 2, 0.06 * scale_), TRUNK)
    leaf_c = LEAVES if rnd.random() > 0.3 else (70, 135, 62)
    for i, dy in enumerate([0.0, 0.22, 0.42]):
        s = (0.34 - 0.07 * i) * scale_
        mesh.add_quad_box((x, th + dy * scale_ + s * 0.5, z), s, leaf_c, bevel=0.25)


def build_streetlight(mesh, x, z, height=2.2):
    mesh.add_quad_box((x, height / 2, z), (0.035, height / 2, 0.035), LAMP_POST)
    mesh.add_quad_box((x, height + 0.05, z), (0.12, 0.05, 0.12), LAMP_POST)
    mesh.add_quad_box((x, height - 0.04, z), (0.09, 0.04, 0.09), LAMP_HEAD, shade_top=1.0)
    return (x, height - 0.05, z)  # point-light anchor


def build_city_block(mesh, seed=10):
    """One reusable composed environment: a street flanked by buildings of
    varying height/color, sidewalks, trees, streetlights, with clear
    foreground (near sidewalk props), midground (nearest buildings), and
    background (taller distant towers) depth layers."""
    rnd = random.Random(seed)
    mesh.add_quad_box((0, -0.06, -15), (14, 0.06, 32), (96, 150, 92))  # base ground/grass fill
    build_road(mesh, 0, 10, 0, -40, width=3.2)

    light_anchors = []
    building_specs = []
    z = -4
    side_toggle = 0
    i = 0
    while z > -34:
        side = -1 if side_toggle == 0 else 1
        side_toggle ^= 1
        w = rnd.uniform(2.2, 3.4)
        h = rnd.uniform(3.0, 9.5) if abs(z) < 20 else rnd.uniform(8.0, 18.0)  # background taller
        d = rnd.uniform(2.2, 3.0)
        cx = side * (1.6 + 0.75 + w / 2 + 0.3)
        building_specs.append((cx, z, w, h, d, i))
        i += 1
        z -= rnd.uniform(3.2, 4.6)

    for (cx, cz, w, h, d, seed_i) in building_specs:
        build_building(mesh, cx, cz, w, h, d, seed=seed_i)

    for z in range(-2, -34, -6):
        for side in (-1, 1):
            tx = side * (1.6 + 0.35)
            build_tree(mesh, tx, z + rnd.uniform(-0.6, 0.6), scale_=rnd.uniform(0.8, 1.2), seed=z + side)

    for z in range(0, -34, -8):
        for side in (-1, 1):
            tx = side * (1.6 + 1.5)
            anchor = build_streetlight(mesh, tx, z)
            light_anchors.append(anchor)

    return {"building_specs": building_specs, "light_anchors": light_anchors}

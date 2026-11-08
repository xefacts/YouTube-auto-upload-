"""Reusable voxel-style props built out of Box primitives: houses, towers,
a character rig, crowd figures, the golden elevator, furniture, clouds."""
from .engine import Box, Scene
import math

SKIN = (247, 200, 160)
SHIRT_TEAL = (44, 150, 150)
PANTS = (60, 70, 95)
HAIR = (90, 55, 35)

GROUND_LOW = (120, 150, 80)
ROAD = (150, 145, 140)
HOUSE_WALLS = [(201, 164, 128), (190, 150, 140), (176, 176, 150), (205, 180, 150)]
ROOF_COLORS = [(170, 80, 65), (150, 95, 70), (120, 90, 110)]

GOLD = (230, 185, 70)
GOLD_DARK = (190, 145, 45)
SKY_WHITE = (250, 250, 250)
TOWER_BLUE = (190, 215, 235)
TOWER_GLASS = (140, 185, 215)


def person(cx, cy_ground, cz, yaw=0.0, shirt=SHIRT_TEAL, pants=PANTS, hair=HAIR,
           skin=SKIN, scale=1.0, pose_lean=0.0):
    """A simple 4-box voxel person: legs block, torso, head, ponytail.
    cy_ground is the y of the ground the character stands on."""
    boxes = []
    leg_h = 0.34 * scale
    torso_h = 0.42 * scale
    head_h = 0.26 * scale
    w = 0.22 * scale

    y0 = cy_ground
    legs_cy = y0 + leg_h
    torso_cy = y0 + 2 * leg_h + torso_h
    head_cy = y0 + 2 * leg_h + 2 * torso_h + head_h

    boxes.append(Box((cx, legs_cy, cz), (w * 0.9, leg_h, w * 0.9), pants, yaw=yaw + pose_lean))
    boxes.append(Box((cx, torso_cy, cz), (w, torso_h, w * 0.85), shirt, yaw=yaw + pose_lean))
    boxes.append(Box((cx, head_cy, cz), (w * 0.8, head_h, w * 0.8), skin, yaw=yaw))
    # ponytail
    pony_d = 0.26 * scale
    yr = math.radians(yaw)
    boxes.append(Box(
        (cx - pony_d * math.sin(yr), head_cy + 0.02, cz - pony_d * math.cos(yr)),
        (0.08 * scale, 0.16 * scale, 0.08 * scale), hair, yaw=yaw))
    return boxes


def house(cx, cz, w=1.1, d=1.1, h=1.0, wall_color=None, roof_color=None, yaw=0.0, ground_y=0.0):
    boxes = []
    wall_color = wall_color or HOUSE_WALLS[0]
    roof_color = roof_color or ROOF_COLORS[0]
    body_cy = ground_y + h / 2
    boxes.append(Box((cx, body_cy, cz), (w / 2, h / 2, d / 2), wall_color, yaw=yaw))
    roof_cy = ground_y + h + 0.14
    boxes.append(Box((cx, roof_cy, cz), (w / 2 + 0.12, 0.14, d / 2 + 0.12), roof_color, yaw=yaw))
    return boxes


def pillar_tower(cx, cz, radius=0.35, height=22.0, ground_y=0.0, color=TOWER_BLUE, band_color=GOLD):
    """A very tall thin tower (the golden pillars holding up the sky city)."""
    boxes = []
    n_segments = max(4, int(height / 2.2))
    seg_h = height / n_segments
    for i in range(n_segments):
        cy = ground_y + seg_h * (i + 0.5)
        c = color if i % 3 != 0 else band_color
        boxes.append(Box((cx, cy, cz), (radius, seg_h / 2 * 0.96, radius), c))
    return boxes


def sky_platform(cx, cy, cz, size=3.6, color=TOWER_GLASS):
    boxes = []
    boxes.append(Box((cx, cy, cz), (size, 0.25, size), GOLD_DARK))
    boxes.append(Box((cx, cy + 0.9, cz), (size * 0.8, 0.7, size * 0.8), color))
    for dx, dz in [(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)]:
        boxes.append(Box((cx + dx * size, cy + 1.6, cz + dz * size),
                          (0.22, 1.0, 0.22), (235, 235, 240)))
    return boxes


def cloud(cx, cy, cz, scale_=1.0, color=SKY_WHITE):
    boxes = []
    puffs = [(0, 0, 0, 1.0), (0.5, 0.05, 0.1, 0.7), (-0.5, 0.03, -0.1, 0.72),
             (0.2, 0.25, -0.3, 0.6), (-0.25, 0.2, 0.25, 0.55)]
    for dx, dy, dz, s in puffs:
        boxes.append(Box((cx + dx * scale_, cy + dy * scale_, cz + dz * scale_),
                          (0.5 * s * scale_, 0.32 * s * scale_, 0.5 * s * scale_), color))
    return boxes


def golden_elevator(cx, cz, ground_y=0.0, h=2.2, button_state="red"):
    boxes = []
    boxes.append(Box((cx, ground_y + h / 2, cz), (0.6, h / 2, 0.6), GOLD))
    boxes.append(Box((cx, ground_y + h + 0.1, cz), (0.68, 0.1, 0.68), GOLD_DARK))
    boxes.append(Box((cx, ground_y + h * 0.45, cz), (0.44, h * 0.4, 0.02), (210, 235, 240)))
    pedestal_h = 0.9
    boxes.append(Box((cx, ground_y + pedestal_h / 2, cz + 1.1), (0.22, pedestal_h / 2, 0.22), (70, 70, 80)))
    btn_color = (220, 60, 50) if button_state == "red" else (70, 200, 90)
    boxes.append(Box((cx, ground_y + pedestal_h + 0.08, cz + 1.1), (0.18, 0.08, 0.18), btn_color))
    return boxes


def coin_jar(cx, cy_surface, cz, fill=0.5, coin_color=GOLD):
    boxes = []
    jar_h = 0.5
    boxes.append(Box((cx, cy_surface + jar_h / 2, cz), (0.22, jar_h / 2, 0.22), (225, 240, 245)))
    n = max(1, int(fill * 6))
    for i in range(n):
        boxes.append(Box((cx, cy_surface + 0.05 + i * 0.07, cz), (0.16, 0.035, 0.16), coin_color))
    return boxes

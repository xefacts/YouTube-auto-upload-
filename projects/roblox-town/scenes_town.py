"""Sets and per-shot staging for Hiccup Town (blocky-shorts format)."""
import math

from boxes import (character, chair, crowd, desk, hills, house, lamp, podium, sign,
                   tree)

KID = dict(shirt=(232, 96, 92), pants=(58, 74, 122), hair=(60, 42, 34))
KID2 = dict(shirt=(86, 156, 232), pants=(50, 62, 104), hair=(30, 30, 36))
BABY = dict(shirt=(246, 214, 120), pants=(240, 240, 244), hair=(196, 148, 96))
MAYOR = dict(shirt=(58, 64, 100), pants=(40, 44, 70), hair=(196, 196, 204),
             hat=(48, 48, 60), expr="idle")
TEACHER = dict(shirt=(120, 190, 180), pants=(58, 70, 96), hair=(150, 108, 72),
               long_hair=True)
DENTIST = dict(shirt=(240, 244, 248), pants=(180, 196, 210), hair=(60, 60, 70))


# ---------------------------------------------------------------- sets
def set_town(sc):
    hills(sc, (170, 184, 192), z=54.0, n=7)
    sc.floor(0.0, (126, 148, 114))
    sc.box((0, 0.02, 3.6), (40, 0.04, 6.4), (96, 100, 110))        # road
    for i in range(-9, 10):
        sc.box((i * 2.6, 0.05, 3.6), (1.3, 0.02, 0.14), (236, 234, 224))
    sc.box((0, 0.10, 0.32), (40, 0.20, 0.16), (194, 190, 182))     # near kerb
    sc.box((0, 0.10, 6.88), (40, 0.20, 0.16), (194, 190, 182))     # far kerb
    sc.box((0, 0.045, 7.8), (40, 0.03, 2.0), (200, 196, 186))      # sidewalk
    # front row of houses, across the street
    for x, z, w, h, col, roof in ((-6.0, 11.0, 4.0, 2.6, (228, 214, 196), (196, 86, 78)),
                                  (-1.6, 11.8, 3.6, 2.3, (208, 220, 226), (78, 118, 168)),
                                  (2.8, 11.0, 4.2, 2.7, (232, 206, 190), (196, 86, 78)),
                                  (7.6, 11.6, 3.4, 2.4, (214, 216, 224), (78, 118, 168)),
                                  (-10.4, 11.4, 3.4, 2.5, (222, 220, 200), (196, 86, 78))):
        house(sc, x, z, w=w, h=h, d=3.0, wall=col, roof=roof)
    # far row, smaller and hazier: depth
    for x, z, w, h in ((-13.0, 19.0, 4.4, 3.2), (-5.0, 20.0, 4.8, 3.6),
                       (3.0, 19.4, 4.6, 3.3), (11.0, 20.4, 4.8, 3.5)):
        house(sc, x, z, w=w, h=h, d=3.4, wall=(198, 194, 186),
              roof=(172, 92, 84) if int(x) % 3 else (78, 106, 148))
    tree(sc, -8.4, 8.4, 1.1)
    tree(sc, 8.8, 8.6, 1.0)
    tree(sc, 14.0, 10.0, 1.3)
    lamp(sc, -4.2, 7.4)
    lamp(sc, 4.4, 7.4)


def set_class(sc):
    sc.floor(0.0, (206, 186, 150))
    sc.box((0, 1.9, 6.6), (12, 3.8, 0.2), (232, 222, 200))          # back wall
    sc.box((0, 1.7, 6.48), (4.2, 2.0, 0.06), (58, 76, 62))          # blackboard
    sc.box((0, 1.7, 6.44), (3.6, 0.10, 0.02), (206, 214, 198))
    for x in (-1.2, 0.4, 1.8):
        sc.box((x, 2.2, 6.44), (0.9, 0.06, 0.02), (206, 214, 198))
    for i, (x, z) in enumerate(((-1.7, 3.2), (0.2, 3.2), (2.0, 3.2))):
        desk(sc, x, z)
        chair(sc, x, z - 0.75)
    sc.box((-4.4, 1.2, 5.9), (1.6, 2.4, 0.3), (206, 190, 166))
    sc.box((4.2, 2.4, 6.3), (1.4, 0.9, 0.06), (250, 250, 246))      # clock plate
    sc.box((4.2, 2.4, 6.26), (0.1, 0.36, 0.04), (60, 60, 70))


def set_clinic(sc):
    sc.floor(0.0, (198, 206, 204))
    sc.box((0, 2.1, 7.0), (13, 4.2, 0.2), (234, 228, 214))          # back wall
    sc.box((0, 0.62, 7.0), (13, 1.2, 0.24), (176, 196, 196))        # wainscot
    # window with sky
    sc.box((-3.4, 2.35, 6.9), (2.4, 1.7, 0.06), (250, 250, 248))
    sc.box((-3.4, 2.35, 6.86), (2.1, 1.45, 0.06), (150, 196, 232))
    sc.box((-3.4, 2.35, 6.82), (0.08, 1.45, 0.04), (250, 250, 248))
    sc.box((-3.4, 2.35, 6.82), (2.1, 0.08, 0.04), (250, 250, 248))
    # tooth poster
    sc.box((3.2, 2.45, 6.88), (1.5, 1.5, 0.06), (252, 250, 242))
    sc.box((3.2, 2.30, 6.84), (0.80, 0.80, 0.04), (250, 248, 240))
    sc.box((3.2, 2.72, 6.84), (0.52, 0.34, 0.04), (244, 246, 248))
    sc.box((3.2, 1.98, 6.84), (0.30, 0.26, 0.04), (244, 246, 248))
    # dentist bed + lamp arm
    sc.box((-2.4, 0.66, 3.0), (1.2, 0.26, 2.6), (248, 250, 252))
    sc.box((-2.4, 1.16, 1.9), (1.1, 0.9, 0.2), (234, 240, 244))
    for sz in (2.0, 4.0):
        sc.box((-2.4, 0.30, sz), (0.2, 0.56, 0.2), (168, 180, 190))
    sc.box((2.6, 1.05, 5.2), (1.7, 2.1, 0.8), (244, 246, 248))      # cabinet
    sc.box((2.6, 1.62, 4.78), (1.30, 0.10, 0.04), (168, 198, 208))
    sc.box((2.6, 2.20, 4.78), (1.30, 0.10, 0.04), (168, 198, 208))
    sc.box((0.2, 2.72, 6.7), (1.1, 0.62, 0.10), (252, 252, 250))    # light box
    sc.box((0.2, 1.68, 3.2), (0.12, 1.7, 0.12), (140, 148, 158))
    sc.box((0.2, 2.60, 3.2), (0.9, 0.14, 0.9), (216, 224, 228))
    sc.box((-4.6, 0.55, 4.6), (0.9, 1.1, 0.9), (196, 210, 200))     # plant pot
    sc.box((-4.6, 1.55, 4.6), (1.0, 1.1, 1.0), (96, 158, 112))


def set_field(sc):
    hills(sc, (150, 176, 160), z=52.0, n=6)
    sc.floor(0.0, (86, 158, 96))
    for i in range(-7, 8):
        if i % 2 == 0:
            sc.box((i * 2.6, 0.02, 3.0), (2.6, 0.02, 22), (78, 148, 88))
    sc.box((0, 0.04, 1.4), (16, 0.02, 0.12), (238, 240, 230))       # finish line
    for x in (-6.0, 6.0):
        sc.box((x, 0.9, 1.4), (0.12, 1.8, 0.12), (240, 240, 236))
    sc.box((0, 0.02, 6.5), (7.6, 0.02, 3.4), (92, 164, 100))
    for i in range(-4, 5):                                          # stands
        sc.box((i * 1.6, 0.9, 9.2), (1.5, 1.1, 0.7), (70, 76, 96))
        sc.box((i * 1.6, 1.6, 9.2), (1.5, 0.3, 0.7), (92, 100, 126))


def set_plaza(sc):
    hills(sc, (158, 172, 178), z=50.0, n=6)
    sc.floor(0.0, (198, 190, 174))
    for i in range(-6, 7):
        sc.box((i * 2.0, 0.02, 3.0), (0.06, 0.02, 12), (186, 178, 164))
        sc.box((0, 0.02, i * 2.0 + 2.0), (14, 0.02, 0.06), (186, 178, 164))
    sc.box((0, 0.28, 5.2), (9.0, 0.56, 3.4), (208, 198, 180))       # stage
    sc.box((0, 0.58, 5.2), (9.0, 0.06, 3.4), (222, 212, 194))
    sc.box((0, 5.6, 13.0), (14.0, 1.5, 0.24), (176, 84, 78))        # banner
    for x in (-5.6, 5.6):
        sc.box((x, 2.2, 8.4), (0.18, 4.4, 0.18), (140, 132, 120))
    tree(sc, -7.2, 2.2, 1.0)
    tree(sc, 7.2, 2.4, 0.9)


SETS = dict(town=set_town, classroom=set_class, clinic=set_clinic, field=set_field,
            plaza=set_plaza)


# ---------------------------------------------------------------- effects
def puff(sc, x, z, u, y=1.0, n=9, col=(248, 248, 252)):
    """Hiccup burst: a ring of cubes that flies out, shrinks and fades."""
    if not (0.0 <= u <= 1.0):
        return
    k = max(0.0, 1.0 - u) ** 0.8
    r = 0.30 + u * 1.05
    fade = (int(col[0] * k + 226 * (1 - k)), int(col[1] * k + 236 * (1 - k)),
            int(col[2] * k + 246 * (1 - k)))
    for i in range(n):
        a = i * 2 * math.pi / n + 0.3
        rr = r * (0.75 + 0.35 * ((i * 7) % 5) / 4)
        sc.box((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.55, z + 0.12),
               (0.15 * (1 - u) + 0.07,) * 2 + (0.15 * (1 - u) + 0.07,), fade)
    if u < 0.5:
        sc.box((x, y + 0.15, z + 0.2), (0.2, 0.2, 0.2), (255, 255, 255))


# ---------------------------------------------------------------- stages
def kid_walk(sc, u, t):
    hic = 0.52 < u < 0.66
    character(sc,   0.0, 0.0, s=1.0, spec=dict(KID, expr="shock" if hic else "idle"),
              pose="hiccup" if hic else "walk", t=t, facing=180)
    if hic:
        puff(sc, 0.35, 0.1, (u - 0.52) / 0.14)


def kid_hic(sc, u, t):
    x = -0.95 if u > 0.42 else 0.0
    hic = 0.36 < u < 0.46
    character(sc, x, 0.0, s=1.0, spec=dict(KID, expr="happy" if u > 0.5 else "idle"),
              pose="hiccup" if hic else "idle", t=t, facing=180)
    puff(sc, 0.0, 0.0, (u - 0.42) / 0.3 if 0.42 < u < 0.72 else -1)


def kid_cheat(sc, u, t):
    character(sc, 0.0, 0.0, s=1.05, spec=dict(KID, expr="happy"), pose="point",
              t=t, facing=180)
    character(sc, -1.9, 1.4, s=0.95, spec=dict(TEACHER, expr="sad"), pose="idle",
              t=t, facing=180)


def quiz(sc, u, t):
    character(sc, -1.7, 2.4, s=0.98, spec=dict(KID, expr="idle"), pose="idle",
              t=t, facing=180)
    character(sc, 0.2, 2.4, s=0.98, spec=dict(KID2, expr="idle"), pose="idle",
              t=t, facing=180)
    character(sc, 2.0, 2.4, s=0.98, spec=dict(BABY, expr="happy"), pose="idle",
              t=t, facing=180)
    character(sc, -0.2, 4.9, s=1.1, spec=dict(TEACHER, expr="idle"), pose="idle",
              t=t, facing=180)
    if u > 0.55:                       # he is in the hallway now
        puff(sc, -1.7, 2.4, (u - 0.55) / 0.3)
    if 0.42 < u < 0.55:
        character(sc, -1.7, 2.4, s=0.98, spec=dict(KID, expr="shock"), pose="hiccup",
                  t=t, facing=180)


def dentist(sc, u, t):
    character(sc, -1.9, 2.6, s=1.0,
              spec=dict(KID, expr="shock" if u > 0.35 else "idle"),
              pose="hiccup" if 0.3 < u < 0.45 else "idle", t=t, facing=180)
    character(sc, 1.0, 4.2, s=1.02, spec=dict(DENTIST, expr="happy"), pose="idle",
              t=t, facing=180)
    if 0.42 < u < 0.72:
        puff(sc, -1.9, 2.6, (u - 0.42) / 0.3)
    if u > 0.62:
        for i in range(4):
            character(sc, -4.4 + i * 1.5, 7.0, s=0.62, spec=dict(crowd_color(i)),
                      pose="walk", t=t + i, facing=180)


def crowd_color(i):
    return dict(shirt=[(232, 106, 92), (86, 156, 232), (240, 186, 74), (110, 190, 140)][i % 4])


def final(sc, u, t):
    x = -0.9 + u * 2.2
    character(sc, x, 0.6, s=1.0, spec=dict(KID, expr="happy"), pose="run", t=t,
              facing=180)
    character(sc, x + 1.2, 1.6, s=0.96, spec=dict(KID2, expr="sad"), pose="run",
              t=t + 0.4, facing=180)
    for i in range(6):
        character(sc, -4.4 + i * 1.8, 8.4, s=0.7, spec=dict(crowd_color(i)),
                  pose="cheer" if i % 2 else "idle", t=t + i * 0.5, facing=180)


def baby(sc, u, t):
    character(sc, -0.6, 1.2, s=0.62, spec=dict(BABY, expr="shock" if u > 0.3 else "happy"),
              pose="hiccup" if 0.28 < u < 0.42 else "idle", t=t, facing=180)
    character(sc, 0.7, 1.4, s=1.0, spec=dict(shirt=(196, 120, 190), hair=(80, 50, 40),
                                            long_hair=True), pose="idle", t=t, facing=180)
    if u > 0.42:
        puff(sc, -0.6, 1.2, (u - 0.42) / 0.4)
    for i in range(5):
        jx = -3.4 + i * 1.6
        jolt = 0.06 if (int(t * 3 + i) % 2 == 0) else 0.0
        character(sc, jx + 0.1, 4.4, s=0.92, spec=dict(crowd_color(i),
                  expr="shock" if u > 0.5 else "idle"),
                  pose="hiccup" if u > 0.5 and i % 2 == 0 else "idle",
                  t=t + i * 0.3, facing=180)


def crowd_drift(sc, u, t):
    cols = [(232, 106, 92), (86, 156, 232), (240, 186, 74), (110, 190, 140),
            (188, 132, 216), (240, 240, 240)]
    for i in range(7):
        base = -3.6 + i * 1.2
        drift = -0.5 * max(0.0, u - i * 0.10)
        hic = ((t * 2.2 + i * 0.37) % 1.0) < 0.22
        character(sc, base + drift, 2.6 + (i % 3) * 0.7, s=0.95,
                  spec=dict(shirt=cols[i % len(cols)], expr="shock" if hic else "idle"),
                  pose="hiccup" if hic else "idle", t=t + i * 0.2, facing=180)


def mayor(sc, u, t):
    podium(sc, -0.4, 5.0, top=0.61)
    character(sc, -0.4, 6.5, y=0.61, s=1.05,
              spec=dict(MAYOR, expr="sad" if u > 0.45 else "idle"),
              pose="point" if u > 0.3 else "idle", t=t, facing=180)
    sign(sc, -0.4, 3.15, 7.6, w=3.0, h=0.85, color=(240, 238, 230))
    if u > 0.4:                        # the ban: stripes stamped across the sign
        for i in range(6):
            sc.box((-1.3 + (i % 3) * 0.95, 2.92 + (i // 3) * 0.25, 7.52),
                   (0.82, 0.14, 0.05), (198, 62, 62))
    for i in range(5):
        character(sc, -3.6 + i * 1.8, 2.6 + (i % 2) * 0.5, s=0.82,
                  spec=dict(crowd_color(i), expr="sad"), pose="idle", t=t + i * 0.4,
                  facing=180)


def hold_breath(sc, u, t):
    cols = [(232, 106, 92), (86, 156, 232), (240, 186, 74), (110, 190, 140),
            (188, 132, 216)]
    for i in range(5):
        character(sc, -2.6 + i * 1.3, 2.0 + (i % 2) * 0.5, s=0.98,
                  spec=dict(shirt=cols[i % 5], expr="sad"), pose="strain",
                  t=t + i * 0.25, facing=180)


def soda(sc, u, t):
    desk(sc, 0.4, 3.0)
    character(sc, 0.4, 4.1, s=1.0, spec=dict(shirt=(240, 186, 74), hair=(30, 30, 36),
                                             expr="happy"), pose="hold", t=t, facing=180)
    # the can sits on the desk, right in the foreground
    cx, cy, cz = 1.55, 1.00, 2.85
    sc.box((cx, cy, cz), (0.30, 0.46, 0.30), (214, 74, 74))
    sc.box((cx, cy, cz - 0.155), (0.11, 0.30, 0.02), (248, 248, 250))
    sc.box((cx, cy + 0.25, cz), (0.32, 0.05, 0.32), (198, 198, 204))
    if u > 0.5:
        k = min(1.0, (u - 0.5) / 0.3)
        sc.box((cx - 0.22 * k, cy + 0.36 + 0.14 * k, cz - 0.14 * k),
               (0.28, 0.03, 0.28), (206, 206, 212))
        for i in range(6):
            a = i * 1.05
            sc.box((cx + math.cos(a) * (0.20 + 0.45 * k),
                    cy + 0.40 + 0.28 * k + math.sin(a) * (0.15 + 0.28 * k),
                    cz + math.sin(a) * 0.2), (0.11, 0.11, 0.11),
                   (238, int(238 * (1 - k * 0.45)), int(242 * (1 - k * 0.35))))


def mass_hic(sc, u, t):
    cols = [(232, 106, 92), (86, 156, 232), (240, 186, 74), (110, 190, 140),
            (188, 132, 216), (240, 240, 240)]
    for i in range(8):
        base = -4.4 + i * 1.25
        hic = (u > 0.25) and (((t * 3.0 + i * 0.2) % 1.0) < 0.3)
        character(sc, base, 2.2 + (i % 3) * 0.8, s=0.98,
                  spec=dict(shirt=cols[i % len(cols)], expr="shock" if hic else "idle"),
                  pose="hiccup" if hic else "idle", t=t + i * 0.15, facing=180)
    if 0.25 < u < 0.5:
        puff(sc, 0.0, 2.6, (u - 0.25) / 0.25, y=1.2)


def three_years(sc, u, t):
    house(sc, -4.0, 7.4, w=3.2, h=2.5)
    house(sc, 1.2, 7.8, w=3.4, h=2.6)
    tree(sc, -7.0, 3.0, 1.1)
    tree(sc, 5.4, 3.2, 1.0)
    lamp(sc, -1.6, 1.2)
    character(sc, -0.2, 1.6, s=1.0, spec=dict(KID, expr="sad"), pose="idle", t=t,
              facing=180)


def button(sc, u, t):
    for i in range(4):
        house(sc, -6.4 + i * 4.0, 8.6, w=3.0, h=2.4,
              roof=(196, 86, 78) if i % 2 else (78, 118, 168))
    # the town has drifted off to the left: an empty road, a lonely sign
    sign(sc, 1.8, 1.15, 2.4, w=2.0, h=0.7)
    character(sc, 0.0, 0.8, s=1.05, spec=dict(KID, expr="sad"), pose="point", t=t,
              facing=180)


STAGES = dict(kid_walk=kid_walk, kid_hic=kid_hic, kid_cheat=kid_cheat, quiz=quiz,
              dentist=dentist, final=final, baby=baby, crowd_drift=crowd_drift,
              mayor=mayor, hold_breath=hold_breath, soda=soda, mass_hic=mass_hic,
              three_years=three_years, button=button)

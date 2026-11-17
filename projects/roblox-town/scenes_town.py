"""Sets and per-shot staging for Hiccup Town (blocky-shorts look, v2)."""
import math

from boxes import (character, chair, crowd, desk, hills, house, lamp, podium, shadow,
                   sign, tree)

SKIN = (243, 205, 176)
KID = dict(shirt=(228, 92, 84), pants=(48, 58, 100), hair=(52, 38, 32), cap=(226, 74, 62),
           expr="smile")
KID2 = dict(shirt=(84, 152, 232), pants=(44, 52, 88), hair=(30, 30, 36), expr="idle")
BABY = dict(shirt=(248, 214, 118), pants=(240, 240, 244), hair=(198, 150, 96),
            expr="smile", skin=(248, 212, 186))
MOM = dict(shirt=(150, 208, 178), pants=(70, 78, 116), hair=(150, 104, 70),
           long_hair=True, expr="worried")
MAYOR = dict(shirt=(64, 72, 112), pants=(40, 44, 70), hair=(206, 206, 214), hat=(46, 46, 58),
             expr="sad", print=(236, 200, 96))
TEACHER = dict(shirt=(120, 190, 180), pants=(58, 70, 96), hair=(150, 108, 72),
               long_hair=True, expr="idle", glasses=True)
DENTIST = dict(shirt=(240, 244, 248), pants=(176, 192, 208), hair=(58, 58, 68),
               expr="smile", print=(196, 64, 64))
TOWN = [(232, 106, 92), (86, 156, 232), (240, 186, 74), (110, 190, 140), (188, 132, 216),
        (240, 240, 246)]


def crowd_color(i, expr="idle"):
    return dict(shirt=TOWN[i % len(TOWN)], expr=expr, pants=(46, 56, 92))


# ---------------------------------------------------------------- sets
def set_street(sc):
    hills(sc, (176, 188, 202), z=62.0, n=8, w=16.0)
    sc.floor(0.0, (116, 166, 108))
    sc.box((0, 0.02, 4.4), (44, 0.04, 7.0), (92, 96, 106))            # road
    for i in range(-10, 11):                                          # centre line
        sc.box((i * 2.4, 0.05, 4.4), (1.2, 0.02, 0.13), (238, 236, 224))
    for i in range(-3, 4):                                            # crosswalk
        sc.box((i * 0.75 + 9.0, 0.05, 4.4), (0.34, 0.02, 6.6),
               (240, 238, 228))
    sc.box((0, 0.10, 0.75), (44, 0.20, 0.18), (206, 202, 194))        # kerbs
    sc.box((0, 0.10, 8.05), (44, 0.20, 0.18), (206, 202, 194))
    sc.box((0, 0.045, 9.05), (44, 0.03, 2.0), (212, 208, 198))        # sidewalk
    # front row of houses across the street
    for x, z, w, h, wall, roof, aw in (
            (-7.4, 12.4, 4.2, 2.7, (238, 226, 206), (196, 84, 74), (226, 122, 108)),
            (-2.6, 13.2, 3.8, 2.4, (196, 168, 214), (140, 96, 140), (210, 150, 196)),
            (2.0, 12.4, 4.4, 2.8, (176, 214, 196), (86, 110, 150), (150, 200, 180)),
            (6.8, 13.0, 3.6, 2.5, (232, 164, 148), (196, 84, 74), None),
            (-12.2, 12.8, 3.8, 2.6, (206, 206, 214), (86, 110, 150), None)):
        house(sc, x, z, w=w, h=h, d=3.2, wall=wall, roof=roof, awning=aw)
    # back row for depth
    for x, z, w, h, wall, roof in (
            (-15.0, 21.0, 5.0, 3.4, (218, 210, 200), (176, 92, 84)),
            (-6.0, 22.0, 5.4, 3.8, (206, 200, 196), (96, 118, 154)),
            (3.4, 21.4, 5.2, 3.5, (214, 206, 196), (150, 100, 146)),
            (12.6, 22.4, 5.4, 3.7, (210, 204, 196), (176, 92, 84))):
        house(sc, x, z, w=w, h=h, d=3.6, wall=wall, roof=roof)
    for x, z, s in ((-10.6, 9.4, 1.15), (-0.4, 9.8, 1.0), (8.4, 9.6, 1.2),
                    (15.4, 11.0, 1.35)):
        tree(sc, x, z, s)
    for x, z in ((-3.2, 8.6), (5.2, 8.6), (11.6, 8.8)):
        lamp(sc, x, z)
    sc.box((-5.6, 0.60, 8.9), (0.30, 1.20, 0.30), (196, 74, 66))      # hydrant
    sc.box((-5.6, 1.28, 8.9), (0.46, 0.16, 0.46), (196, 74, 66))


def set_class(sc):
    hills(sc, (188, 200, 210), z=40.0, n=6, w=14.0)
    sc.floor(0.0, (206, 176, 138))
    sc.box((0, 2.2, 8.0), (15, 4.4, 0.24), (240, 228, 204))           # back wall
    sc.box((0, 0.55, 8.0), (15, 1.1, 0.28), (176, 208, 196))          # wainscot
    sc.box((0, 2.15, 7.84), (5.2, 2.2, 0.08), (62, 84, 68))           # blackboard
    sc.box((0, 2.15, 7.78), (4.6, 0.10, 0.03), (226, 232, 220))
    sc.box((-1.2, 2.40, 7.78), (1.6, 0.08, 0.03), (226, 232, 220))
    sc.box((1.6, 1.95, 7.78), (1.2, 0.08, 0.03), (226, 232, 220))
    sc.box((4.6, 2.60, 7.90), (1.2, 0.80, 0.06), (252, 250, 242))     # clock
    sc.box((4.6, 2.60, 7.86), (0.10, 0.34, 0.03), (70, 70, 84))
    for i, (x, z) in enumerate(((-2.6, 3.4), (0.0, 3.4), (2.6, 3.4),
                                (-2.6, 5.4), (0.0, 5.4))):
        desk(sc, x, z)
        chair(sc, x, z - 0.95)
    sc.box((-5.6, 1.1, 6.6), (1.4, 2.2, 0.30), (204, 186, 158))       # bookshelf
    sc.box((5.6, 1.2, 7.2), (1.6, 2.4, 0.24), (232, 218, 192))


def set_clinic(sc):
    sc.floor(0.0, (198, 214, 210))
    sc.box((0, 2.3, 8.2), (15, 4.6, 0.24), (246, 238, 222))
    sc.box((0, 0.60, 8.2), (15, 1.2, 0.28), (128, 178, 186))
    sc.box((0, 1.35, 8.2), (15, 0.18, 0.30), (232, 118, 110))
    sc.box((-3.8, 2.45, 8.05), (2.6, 1.8, 0.08), (252, 252, 250))     # window
    sc.box((-3.8, 2.45, 8.00), (2.3, 1.5, 0.08), (150, 200, 236))
    sc.box((-3.8, 2.45, 7.96), (0.09, 1.5, 0.04), (252, 252, 250))
    sc.box((-3.8, 2.45, 7.96), (2.3, 0.09, 0.04), (252, 252, 250))
    sc.box((3.4, 2.55, 8.02), (2.0, 2.0, 0.08), (252, 250, 240))      # poster
    sc.box((3.4, 2.55, 7.96), (0.95, 0.95, 0.06), (250, 248, 242))
    sc.box((3.4, 2.95, 7.94), (0.62, 0.34, 0.05), (244, 246, 248))
    sc.box((3.4, 2.10, 7.94), (0.40, 0.30, 0.05), (238, 242, 246))
    sc.box((2.55, 1.30, 8.06), (0.55, 0.55, 0.06), (150, 206, 224))
    sc.box((-2.6, 0.62, 4.2), (1.5, 0.28, 3.0), (250, 252, 252))      # dentist chair
    sc.box((-2.6, 1.18, 2.9), (1.4, 0.95, 0.24), (232, 240, 246))
    for sz in (3.2, 5.2):
        sc.box((-2.6, 0.30, sz), (0.22, 0.60, 0.22), (158, 172, 186))
    sc.box((3.0, 1.15, 6.4), (2.0, 2.3, 0.9), (244, 248, 250))        # cabinet
    sc.box((3.0, 1.75, 5.92), (1.6, 0.10, 0.05), (160, 198, 210))
    sc.box((3.0, 2.30, 5.92), (1.6, 0.10, 0.05), (160, 198, 210))
    sc.box((0.2, 2.95, 7.6), (1.3, 0.70, 0.14), (252, 252, 250))      # light box
    sc.box((0.2, 1.75, 3.4), (0.13, 1.8, 0.13), (150, 158, 168))
    sc.box((0.2, 2.78, 3.4), (1.0, 0.16, 1.0), (222, 230, 234))
    sc.box((-5.4, 0.55, 5.4), (0.9, 1.1, 0.9), (198, 212, 202))       # plant
    sc.box((-5.4, 1.55, 5.4), (1.1, 1.2, 1.1), (98, 162, 116))


def set_field(sc):
    hills(sc, (172, 190, 176), z=60.0, n=7, w=15.0)
    sc.floor(0.0, (94, 164, 96))
    for i in range(-9, 10):                                           # mow stripes
        if i % 2 == 0:
            sc.box((i * 2.8, 0.02, 6.0), (2.8, 0.02, 26), (86, 156, 88))
    sc.box((0, 0.04, 2.0), (18, 0.02, 0.14), (240, 242, 232))         # finish line
    for x in (-7.0, 7.0):
        sc.box((x, 1.0, 2.0), (0.14, 2.0, 0.14), (244, 244, 238))
    for i in range(-5, 6):                                            # stands
        sc.box((i * 1.7, 0.95, 12.0), (1.6, 1.2, 0.8), (74, 82, 104))
        sc.box((i * 1.7, 1.68, 12.0), (1.6, 0.32, 0.8), (94, 104, 132))
    tree(sc, -11.0, 8.0, 1.3)
    tree(sc, 11.5, 9.0, 1.2)


def set_plaza(sc):
    hills(sc, (180, 190, 200), z=58.0, n=8, w=15.0)
    sc.floor(0.0, (206, 198, 182))
    for i in range(-8, 9):
        sc.box((i * 2.0, 0.02, 5.0), (0.07, 0.02, 16), (192, 184, 170))
        sc.box((0, 0.02, i * 2.0 + 3.0), (16, 0.02, 0.07), (192, 184, 170))
    sc.box((0, 0.30, 7.2), (10.0, 0.60, 3.6), (214, 204, 186))        # stage
    sc.box((0, 0.62, 7.2), (10.0, 0.06, 3.6), (228, 218, 200))
    sc.box((0, 4.9, 13.5), (15.0, 1.4, 0.3), (176, 84, 78))           # banner
    for x in (-6.2, 6.2):
        sc.box((x, 2.4, 12.6), (0.20, 4.8, 0.20), (150, 142, 130))
    for x, z, s in ((-9.0, 6.0, 1.2), (9.0, 6.4, 1.1)):
        tree(sc, x, z, s)
    for x in (-4.4, 4.4):
        lamp(sc, x, 4.2)


SETS = dict(street=set_street, classroom=set_class, clinic=set_clinic, field=set_field,
            plaza=set_plaza)


# ---------------------------------------------------------------- effects
def puff(sc, x, z, u, y=1.1, n=10, col=(252, 252, 254)):
    """Hiccup burst: cubes flying out, shrinking and fading."""
    if not (0.0 <= u <= 1.0):
        return
    k = max(0.0, 1.0 - u) ** 0.7
    r = 0.26 + u * 0.95
    fade = (int(col[0] * k + 226 * (1 - k)), int(col[1] * k + 236 * (1 - k)),
            int(col[2] * k + 246 * (1 - k)))
    for i in range(n):
        a = i * 2 * math.pi / n + 0.25
        rr = r * (0.72 + 0.4 * ((i * 7) % 5) / 4)
        d = 0.16 * (1 - u) + 0.06
        sc.box((x + math.cos(a) * rr, y + math.sin(a) * rr * 0.6, z + 0.2),
               (d, d, d), fade, glow=0.92 + 0.08 * k)
    if u < 0.45:
        sc.box((x, y + 0.2, z + 0.3), (0.22, 0.22, 0.22), (255, 255, 255), glow=True)


# ---------------------------------------------------------------- stages
def kid_walk(s, u, t):
    hic = 0.55 < u < 0.70
    shadow(s, 0, 0.0, 0.55)
    character(s, 0.0, 0.0, s=1.0, spec=dict(KID, expr="shock" if hic else "smile"),
              pose="hiccup" if hic else "walk", t=t, facing=180)
    if hic:
        puff(s, 0.42, 0.1, (u - 0.55) / 0.15)


def kid_hic(s, u, t):
    x = -1.05 if u > 0.45 else 0.0
    hic = 0.34 < u < 0.46
    shadow(s, x, 0.0, 0.55)
    character(s, x, 0.0, s=1.0, spec=dict(KID, expr="grin" if u > 0.5 else "smile"),
              pose="hiccup" if hic else "idle", t=t, facing=180)
    puff(s, 0.0, 0.0, (u - 0.45) / 0.3 if 0.45 < u < 0.75 else -1)


def kid_cheat(s, u, t):
    shadow(s, 0.0, 0.0, 0.55)
    character(s, 0.0, 0.0, s=1.0, spec=dict(KID, expr="grin"), pose="point", t=t,
              facing=180)
    shadow(s, -2.2, 1.6, 0.5)
    character(s, -2.2, 1.6, s=0.95, spec=dict(TEACHER, expr="sad"), pose="idle", t=t,
              facing=180)


def quiz(s, u, t):
    for i, (x, spec, expr) in enumerate(((-2.7, KID, "smile"), (0.0, KID2, "idle"),
                                         (2.7, BABY, "grin"))):
        shadow(s, x, 4.0, 0.5, col=(174, 148, 114))
        character(s, x, 4.0, s=0.98, spec=dict(spec, expr=expr),
                  pose="hiccup" if (i == 0 and 0.4 < u < 0.55) else "idle", t=t + i * 0.3,
                  facing=180)
    shadow(s, 0.0, 6.4, 0.55, col=(174, 148, 114))
    character(s, 0.0, 6.4, s=1.05, spec=dict(TEACHER, expr="sad"), pose="idle", t=t,
              facing=180)
    if u > 0.55:
        puff(s, -2.7, 4.0, (u - 0.55) / 0.3)


def dentist(s, u, t):
    shadow(s, -2.2, 3.2, 0.55, col=(166, 182, 180))
    character(s, -2.2, 3.2, s=1.0, spec=dict(KID, expr="shock" if u > 0.35 else "smile"),
              pose="hiccup" if 0.28 < u < 0.45 else "idle", t=t, facing=180)
    shadow(s, 1.1, 5.0, 0.55, col=(166, 182, 180))
    character(s, 1.1, 5.0, s=1.0, spec=dict(DENTIST, expr="grin"), pose="idle", t=t,
              facing=180)
    if 0.42 < u < 0.74:
        puff(s, -2.2, 3.2, (u - 0.42) / 0.32)
    if u > 0.62:
        for i in range(4):
            character(s, -4.6 + i * 1.6, 8.0, s=0.62,
                      spec=dict(crowd_color(i), expr="shock"), pose="walk",
                      t=t + i, facing=180)


def final(s, u, t):
    x = -1.4 + u * 2.8
    shadow(s, x, 2.2, 0.55, col=(76, 132, 78))
    character(s, x, 2.2, s=1.0, spec=dict(KID, expr="grin"), pose="run", t=t, facing=180)
    shadow(s, x + 1.5, 3.4, 0.5, col=(76, 132, 78))
    character(s, x + 1.5, 3.4, s=0.96, spec=dict(KID2, expr="sad"), pose="run", t=t + 0.3,
              facing=180)
    for i in range(6):
        character(s, -5.0 + i * 2.0, 11.0, s=0.72,
                  spec=dict(crowd_color(i), expr="grin"), pose="cheer" if i % 2 else "idle",
                  t=t + i * 0.5, facing=180)


def baby(s, u, t):
    shadow(s, -0.6, 1.7, 0.5)
    character(s, -0.6, 1.7, s=0.80,
              spec=dict(BABY, expr="shock" if u > 0.3 else "smile"),
              pose="hiccup" if 0.26 < u < 0.40 else "idle", t=t, facing=180)
    shadow(s, 1.1, 2.0, 0.55)
    character(s, 1.1, 2.0, s=1.02, spec=dict(MOM, expr="shock" if u > 0.45 else "worried"),
              pose="idle", t=t, facing=180)
    if u > 0.40:
        puff(s, -0.6, 1.7, (u - 0.40) / 0.4)


def crowd_drift(s, u, t):
    for i in range(7):
        base = -4.2 + i * 1.3
        drift = -0.55 * max(0.0, u - i * 0.10)
        hic = ((t * 2.2 + i * 0.37) % 1.0) < 0.22
        shadow(s, base + drift, 3.0, 0.5, col=(74, 78, 86))
        character(s, base + drift, 3.0 + (i % 3) * 0.7, s=0.95,
                  spec=dict(crowd_color(i), expr="shock" if hic else "idle"),
                  pose="hiccup" if hic else "idle", t=t + i * 0.2, facing=180)


def mayor(s, u, t):
    podium(s, -0.4, 5.6, top=0.62)
    shadow(s, -0.4, 7.2, 0.55, col=(176, 168, 152))
    character(s, -0.4, 7.2, y=0.62, s=1.05,
              spec=dict(MAYOR, expr="sad" if u > 0.45 else "idle"),
              pose="point" if u > 0.3 else "idle", t=t, facing=180)
    sign(s, -0.4, 3.35, 8.8, w=3.0, h=0.85, color=(244, 242, 234))
    if u > 0.38:
        for i in range(6):
            s.box((-1.3 + (i % 3) * 0.95, 3.15 + (i // 3) * 0.26, 8.72),
                  (0.82, 0.14, 0.05), (206, 62, 62))
    for i in range(5):
        shadow(s, -3.6 + i * 1.9, 2.6, 0.5, col=(176, 168, 152))
        character(s, -3.6 + i * 1.9, 2.6 + (i % 2) * 0.5, s=0.82,
                  spec=dict(crowd_color(i), expr="sad"), pose="idle", t=t + i * 0.4,
                  facing=180)


def hold_breath(s, u, t):
    for i in range(5):
        x = -2.8 + i * 1.4
        shadow(s, x, 2.4 + (i % 2) * 0.5, 0.5, col=(74, 78, 86))
        character(s, x, 2.4 + (i % 2) * 0.5, s=0.98,
                  spec=dict(crowd_color(i), expr="strain" if u > 0.5 else "worried"),
                  pose="strain", t=t + i * 0.25, facing=180)


def soda(s, u, t):
    desk(s, 0.6, 4.2)
    shadow(s, 0.6, 5.3, 0.55, col=(174, 148, 114))
    character(s, 0.6, 5.3, s=1.0,
              spec=dict(shirt=(240, 186, 74), pants=(48, 56, 92), hair=(30, 30, 36),
                        expr="grin"), pose="hold", t=t, facing=180)
    cx, cy, cz = 1.55, 1.20, 4.1
    s.box((cx, cy, cz), (0.42, 0.66, 0.42), (214, 74, 74))
    s.box((cx, cy, cz - 0.215), (0.15, 0.42, 0.02), (248, 248, 250))
    s.box((cx, cy + 0.35, cz), (0.44, 0.06, 0.44), (198, 198, 204))
    if u > 0.45:
        k = min(1.0, (u - 0.45) / 0.3)
        s.box((cx - 0.22 * k, cy + 0.40 + 0.16 * k, cz - 0.14 * k),
              (0.30, 0.03, 0.30), (206, 206, 212))
        for i in range(6):
            a = i * 1.05
            s.box((cx + math.cos(a) * (0.22 + 0.5 * k),
                   cy + 0.46 + 0.34 * k + math.sin(a) * (0.16 + 0.3 * k),
                   cz + math.sin(a) * 0.22), (0.11, 0.11, 0.11),
                  (240, int(240 * (1 - k * 0.4)), int(244 * (1 - k * 0.3))), glow=0.95)


def mass_hic(s, u, t):
    for i in range(8):
        base = -5.0 + i * 1.3
        hic = (u > 0.22) and (((t * 3.0 + i * 0.2) % 1.0) < 0.34)
        shadow(s, base, 2.6 + (i % 3) * 0.8, 0.5, col=(74, 78, 86))
        character(s, base, 2.6 + (i % 3) * 0.8, s=0.98,
                  spec=dict(crowd_color(i), expr="shock" if hic else "idle"),
                  pose="hiccup" if hic else "idle", t=t + i * 0.15, facing=180)
    if 0.22 < u < 0.5:
        puff(s, 0.0, 3.0, (u - 0.22) / 0.28, y=1.25)


def three_years(s, u, t):
    house(s, -4.4, 11.0, w=3.6, h=2.6, wall=(238, 226, 206), roof=(196, 84, 74))
    house(s, 1.6, 11.6, w=3.8, h=2.8, wall=(196, 168, 214), roof=(140, 96, 140))
    tree(s, -8.0, 8.4, 1.2)
    tree(s, 5.8, 8.8, 1.1)
    lamp(s, -1.2, 7.6)
    shadow(s, -0.2, 2.4, 0.55, col=(74, 78, 86))
    character(s, -0.2, 2.4, s=1.0, spec=dict(KID, expr="sad"), pose="idle", t=t,
              facing=180)


def button(s, u, t):
    for i in range(4):
        house(s, -7.4 + i * 4.6, 12.4, w=3.6, h=2.5,
              wall=[(238, 226, 206), (176, 214, 196), (232, 164, 148),
                    (206, 206, 214)][i],
              roof=[(196, 84, 74), (86, 110, 150), (196, 84, 74), (86, 110, 150)][i])
    sign(s, 2.0, 1.20, 4.2, w=2.2, h=0.72)
    shadow(s, 0.0, 3.0, 0.55, col=(74, 78, 86))
    character(s, 0.0, 3.0, s=1.05, spec=dict(KID, expr="sad"), pose="point", t=t,
              facing=180)
    tree(s, -9.0, 9.0, 1.2)
    tree(s, 8.4, 9.4, 1.1)


STAGES = dict(kid_walk=kid_walk, kid_hic=kid_hic, kid_cheat=kid_cheat, quiz=quiz,
              dentist=dentist, final=final, baby=baby, crowd_drift=crowd_drift,
              mayor=mayor, hold_breath=hold_breath, soda=soda, mass_hic=mass_hic,
              three_years=three_years, button=button)

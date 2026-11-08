"""The 8 scenes of 'Skyline Town' as procedural geometry + camera moves."""
import math
from .engine import Scene, Box
from . import figures as F

SKY_DAY_TOP = (120, 180, 235)
SKY_DAY_BOTTOM = (210, 232, 245)
SKY_DUSK_TOP = (255, 190, 130)
SKY_DUSK_BOTTOM = (255, 225, 190)
SKY_INT_TOP = (235, 225, 210)
SKY_INT_BOTTOM = (245, 240, 230)


def _ground(scene, color=F.GROUND_LOW, y=0.0, size=60):
    scene.add(Box((0, y - 0.25, 0), (size, 0.25, size), color))


def scene_1_lowtown():
    """Ground-level street, Maya walking, pillars looming in the distance."""
    sc = Scene(SKY_DAY_TOP, SKY_DAY_BOTTOM, ambient=0.6)
    _ground(sc)
    road_z = 0
    sc.add(Box((0, -0.12, road_z), (1.3, 0.05, 40), F.ROAD))
    for i, side in enumerate([-1, 1]):
        for j in range(6):
            cx = side * (2.3 + 0.4 * (j % 2))
            cz = -6 + j * 2.6
            sc.extend(F.house(cx, cz, w=1.3, d=1.2, h=0.95 + 0.1 * (j % 3),
                               wall_color=F.HOUSE_WALLS[j % len(F.HOUSE_WALLS)],
                               roof_color=F.ROOF_COLORS[j % len(F.ROOF_COLORS)],
                               yaw=90 if side < 0 else -90))
    # colossal pillars far away, hazy
    for i, (px, pz) in enumerate([(-10, -34), (-5, -38), (3, -36), (9, -33)]):
        sc.extend(F.pillar_tower(px, pz, radius=0.55, height=30, color=(200, 215, 230)))
    sc.extend(F.person(0.3, 0.0, 2.0, yaw=200))
    cam_start = dict(eye=(0.0, 1.6, 7.5), target=(0.3, 1.0, -2.0))
    cam_end = dict(eye=(0.6, 1.6, 4.2), target=(0.3, 1.0, -4.0))
    return sc, cam_start, cam_end, 46


def scene_2_reveal():
    """Tilt from the ground up the colossal pillars to the floating sky city."""
    sc = Scene(SKY_DAY_TOP, SKY_DAY_BOTTOM, ambient=0.6)
    _ground(sc)
    for j in range(5):
        cz = -3 + j * 1.6
        sc.extend(F.house(-2.0, cz, w=1.1, d=1.0, wall_color=F.HOUSE_WALLS[j % 4]))
        sc.extend(F.house(2.0, cz, w=1.1, d=1.0, wall_color=F.HOUSE_WALLS[(j + 1) % 4]))
    pillars = [(-2.4, -14), (2.6, -16), (-0.2, -20), (-5.5, -22), (5.0, -21)]
    for px, pz in pillars:
        sc.extend(F.pillar_tower(px, pz, radius=0.7, height=34, color=(205, 220, 232)))
    sc.extend(F.cloud(-2, 16, -18, scale_=2.2))
    sc.extend(F.cloud(3, 15, -20, scale_=2.0))
    sc.extend(F.cloud(0, 17.5, -16, scale_=1.6))
    sc.extend(F.sky_platform(0, 31, -18, size=4.2))
    cam_start = dict(eye=(0.3, 1.4, 5.0), target=(0.0, 3.5, -10))
    cam_end = dict(eye=(0.1, 3.0, 6.5), target=(0.0, 30.0, -18))
    return sc, cam_start, cam_end, 52


def scene_3_elevator():
    """The golden elevator pedestal, button glowing red, small crowd watching."""
    sc = Scene(SKY_DAY_TOP, SKY_DAY_BOTTOM, ambient=0.6)
    _ground(sc)
    sc.extend(F.golden_elevator(0, -2.2, button_state="red"))
    for i, (px, pz) in enumerate([(-2, -24), (2.2, -26)]):
        sc.extend(F.pillar_tower(px, pz, radius=0.6, height=30, color=(205, 220, 232)))
    crowd_positions = [(-1.3, 1.0, 20), (-0.7, 1.4, 210), (0.9, 1.1, -20), (1.5, 1.6, 170), (0.1, 1.8, 95)]
    for cx, cz, yaw in crowd_positions:
        sc.extend(F.person(cx, 0.0, cz, yaw=yaw, scale=0.95,
                            shirt=(170, 120, 90) if cx > 0 else (120, 140, 160)))
    cam_start = dict(eye=(0.3, 1.8, 6.0), target=(0.0, 1.3, -0.5))
    cam_end = dict(eye=(0.0, 1.6, 3.3), target=(0.0, 1.5, -1.8))
    return sc, cam_start, cam_end, 62


def scene_4_maya_portrait():
    """Close portrait on Maya, red light reflected, dusk tones."""
    sc = Scene(SKY_DUSK_TOP, SKY_DUSK_BOTTOM, ambient=0.5, light_dir=(0.2, 0.6, 0.7))
    _ground(sc)
    sc.extend(F.golden_elevator(0, -1.6, button_state="red"))
    sc.extend(F.person(0.0, 0.0, 0.4, yaw=190))
    cam_start = dict(eye=(1.09, 1.65, 1.96), target=(0.0, 1.55, 0.4))
    cam_end = dict(eye=(0.75, 1.62, 1.70), target=(0.0, 1.55, 0.4))
    return sc, cam_start, cam_end, 54


def scene_5_saving():
    """Cozy interior at night: coin jar filling on a windowsill."""
    sc = Scene(SKY_INT_TOP, SKY_INT_BOTTOM, ambient=0.75, light_dir=(0.3, 0.9, 0.2))
    floor_y = 0.0
    sc.add(Box((0, floor_y - 0.1, 0), (3.2, 0.1, 3.2), (150, 110, 80)))
    sc.add(Box((0, 1.4, -1.6), (3.2, 1.5, 0.12), (225, 215, 195)))  # back wall
    sc.add(Box((-1.6, 1.4, 0), (0.12, 1.5, 3.2), (210, 200, 180)))  # side wall
    sc.add(Box((1.3, 1.1, -1.5), (0.55, 0.55, 0.08), (140, 190, 220)))  # window
    sc.extend(F.coin_jar(0.6, 0.72, -1.3, fill=0.75))
    sc.add(Box((0.6, 0.6, -1.3), (0.5, 0.02, 0.4), (90, 60, 40)))  # windowsill shelf
    sc.add(Box((-0.6, 1.3, -1.52), (0.35, 0.45, 0.02), (235, 235, 230)))  # calendar
    sc.add(Box((-0.6, 1.3, -1.52), (0.28, 0.02, 0.02), (200, 60, 60)))  # calendar mark
    cam_start = dict(eye=(1.4, 1.35, 2.0), target=(0.4, 0.8, -1.2))
    cam_end = dict(eye=(0.6, 1.3, 1.2), target=(0.4, 0.8, -1.3))
    return sc, cam_start, cam_end, 58


def scene_6_green_light():
    """Golden hour: button turns green, Maya walks toward it carrying the jar."""
    sc = Scene(SKY_DUSK_TOP, SKY_DUSK_BOTTOM, ambient=0.6, light_dir=(0.6, 0.55, 0.25))
    _ground(sc)
    sc.extend(F.golden_elevator(0, -2.4, button_state="green"))
    for i, (px, pz) in enumerate([(-2, -24), (2.2, -26)]):
        sc.extend(F.pillar_tower(px, pz, radius=0.6, height=30, color=(220, 195, 170)))
    crowd_positions = [(-1.6, 10, 25), (-0.9, 30, 200), (1.2, -15, -35), (1.7, 160, 185), (-1.9, 200, 150)]
    for cx, cz, yaw in crowd_positions:
        sc.extend(F.person(cx, 0.0, cz, yaw=yaw, scale=0.95,
                            shirt=(170, 120, 90) if cx > 0 else (120, 140, 160)))
    sc.extend(F.person(0.0, 0.0, 3.0, yaw=182))
    sc.extend(F.coin_jar(0.32, 0.86, 3.05, fill=1.0))
    cam_start = dict(eye=(0.3, 1.9, 10.0), target=(0.0, 1.3, 1.5))
    cam_end = dict(eye=(0.2, 1.85, 8.3), target=(0.0, 1.35, 1.2))
    return sc, cam_start, cam_end, 56


def scene_7_empty_room():
    """Inside the sky tower: stark, almost empty luxury room."""
    sc = Scene((235, 238, 242), (250, 248, 244), ambient=0.8, light_dir=(0.2, 0.9, 0.25))
    sc.add(Box((0, -0.1, 0), (3.6, 0.1, 3.6), (245, 235, 200)))  # gold-white floor
    sc.add(Box((0, 1.8, -3.0), (3.6, 1.8, 0.1), (225, 240, 250)))  # huge window back wall
    sc.add(Box((-3.4, 1.8, 0), (0.1, 1.8, 3.6), (240, 232, 215)))
    sc.add(Box((3.4, 1.8, 0), (0.1, 1.8, 3.6), (240, 232, 215)))
    # single plain chair
    sc.add(Box((0.6, 0.35, -1.2), (0.3, 0.35, 0.3), (230, 225, 215)))
    sc.add(Box((0.6, 0.85, -1.4), (0.3, 0.15, 0.03), (230, 225, 215)))
    # sign on a stand
    sc.add(Box((-0.8, 0.55, -0.6), (0.03, 0.55, 0.03), F.GOLD))
    sc.add(Box((-0.8, 1.15, -0.6), (0.3, 0.16, 0.02), (250, 250, 245)))
    cam_start = dict(eye=(2.0, 1.4, 2.9), target=(-0.2, 1.0, -1.0))
    cam_end = dict(eye=(0.3, 1.25, 1.1), target=(-0.3, 1.0, -2.0))
    return sc, cam_start, cam_end, 72


def scene_8_final_view():
    """Maya's silhouette at the glass window, looking down at the tiny town below."""
    sc = Scene(SKY_DUSK_TOP, (255, 170, 140), ambient=0.4, light_dir=(-0.3, 0.3, 0.9))
    sc.add(Box((0, -0.1, 0), (3.6, 0.1, 3.6), (120, 90, 90)))
    sc.add(Box((0, 1.8, -2.2), (3.6, 1.8, 0.08), (255, 210, 170)))  # glass glow wall
    sc.extend(F.person(0.1, 0.0, -1.0, yaw=182, shirt=(30, 30, 35), hair=(20, 20, 20), skin=(40, 40, 45)))
    # tiny town far below, seen through the glass (illusion via small-scale cluster low & far)
    for i in range(6):
        sc.add(Box((-1.0 + i * 0.35, -2.4, -3.0), (0.1, 0.12, 0.1), (90, 70, 60)))
    for i in range(4):
        sc.extend(F.pillar_tower(-0.5 + i * 0.3, -3.0, radius=0.04, height=1.6, ground_y=-2.5,
                                  color=(200, 190, 170)))
    sc.extend(F.cloud(-1.4, -1.6, -2.6, scale_=0.5))
    sc.extend(F.cloud(1.2, -1.9, -2.8, scale_=0.4))
    cam_start = dict(eye=(4.03, 1.3, 1.75), target=(0.1, 1.0, -1.0))
    cam_end = dict(eye=(2.20, 1.2, 1.51), target=(0.0, 1.0, -1.8))
    return sc, cam_start, cam_end, 148


SCENE_BUILDERS = [
    scene_1_lowtown,
    scene_2_reveal,
    scene_3_elevator,
    scene_4_maya_portrait,
    scene_5_saving,
    scene_6_green_light,
    scene_7_empty_room,
    scene_8_final_view,
]

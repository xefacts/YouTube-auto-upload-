"""A single, original, polished Roblox-inspired character built on engine2's
Mesh/Box primitives -- reusable and posable, not "a collection of plain
cubes": it has a distinct head with a face (eyes + mouth as inset colored
panels), a separate hair shape, articulated arms with hands, legs with
feet, consistent proportions, and a pose() API driving smooth animation
(walk cycle, arm swing, head turn) via simple parametric joint angles.

Still entirely flat-shaded boxes under the hood (this renderer has no
skinning/skeletal mesh deformation) -- "articulated" means separate rigid
parts rotated around pivots per frame, which is how the reference videos'
own blocky Roblox-style rigs work too.
"""
from __future__ import annotations
import math
from dataclasses import dataclass, field

import numpy as np

from .engine import rot_y, rot_x, translate


SKIN = (0.93, 0.78, 0.64)
SKIN255 = (237, 199, 163)


def _rgb(c):
    return tuple(int(255 * x) if isinstance(x, float) and x <= 1.0 else int(x) for x in c)


@dataclass
class CharacterStyle:
    skin: tuple = (235, 198, 163)
    shirt: tuple = (35, 140, 130)
    pants: tuple = (35, 42, 66)
    hair: tuple = (60, 38, 24)
    shoes: tuple = (25, 25, 28)
    eye: tuple = (30, 30, 35)
    mouth: tuple = (150, 70, 60)
    scale: float = 1.0
    hair_style: str = "short"   # "short" | "ponytail" | "spiky"


class Character:
    """Proportions (at scale=1.0), roughly matching a stylized teen avatar:
      legs 0.70, torso 0.46, neck+head 0.42  -> total standing height ~1.58
    with a visibly distinct head (face + eyes + mouth), hair, torso, two
    articulated arms with hand blocks, two legs with shoe blocks.
    """

    def __init__(self, x, z, yaw=0.0, style: CharacterStyle = None, ground_y=0.0):
        self.x, self.z, self.yaw, self.ground_y = x, z, yaw, ground_y
        self.style = style or CharacterStyle()
        s = self.style.scale
        self.leg_h = 0.62 * s
        self.torso_h = 0.50 * s
        self.torso_w = 0.30 * s
        self.torso_d = 0.18 * s
        self.head_s = 0.24 * s
        self.hip_y = ground_y + self.leg_h
        self.shoulder_y = self.hip_y + self.torso_h
        self.neck_y = self.shoulder_y
        self.head_cy = self.neck_y + self.head_s * 0.95

        # pose state (degrees, radians internally where noted)
        self.pose = dict(
            head_turn=0.0, head_tilt=0.0,
            l_shoulder=0.0, r_shoulder=0.0,
            l_elbow=0.0, r_elbow=0.0,
            l_hip=0.0, r_hip=0.0,
            l_knee=0.0, r_knee=0.0,
            bob=0.0, lean=0.0,
        )

    def set_pose(self, **kw):
        self.pose.update(kw)
        return self

    def walk_cycle(self, phase):
        """phase in [0,1): one full stride. Drives hips/knees/shoulders."""
        a = math.sin(phase * 2 * math.pi)
        a2 = math.sin(phase * 2 * math.pi + math.pi)
        swing = 26
        knee_lift = 18
        self.set_pose(
            l_hip=swing * a, r_hip=swing * a2,
            l_knee=max(0, knee_lift * math.sin(phase * 2 * math.pi) ),
            r_knee=max(0, knee_lift * math.sin(phase * 2 * math.pi + math.pi)),
            l_shoulder=-swing * 0.6 * a, r_shoulder=-swing * 0.6 * a2,
            bob=abs(math.sin(phase * 2 * math.pi)) * 0.035,
        )
        return self

    def wave(self, phase):
        self.set_pose(r_shoulder=-110, r_elbow=-40 + 20 * math.sin(phase * 2 * math.pi * 3))
        return self

    # -- geometry emission -------------------------------------------------
    def build(self, mesh):
        s = self.style
        yaw = self.yaw
        root_pos = np.array([self.x, 0, self.z])
        Myaw = rot_y(yaw)[:3, :3]

        def world(local_xyz):
            return (Myaw @ np.array(local_xyz)) + root_pos + np.array([0, self.pose["bob"], 0])

        hip_c = world((0, self.hip_y, 0))
        mesh.add_quad_box(hip_c, (self.torso_w * 0.46, 0.06, self.torso_d * 0.46), s.pants, yaw=yaw)

        torso_c = world((0, self.hip_y + self.torso_h / 2, 0))
        mesh.add_quad_box(torso_c, (self.torso_w / 2, self.torso_h / 2, self.torso_d / 2),
                           s.shirt, yaw=yaw, bevel=0.2)

        neck_c = world((0, self.neck_y + 0.04, 0))
        mesh.add_quad_box(neck_c, (0.05, 0.05, 0.05), s.skin, yaw=yaw)

        head_yaw = yaw + self.pose["head_turn"]
        head_pitch = self.pose["head_tilt"]
        head_c = world((0, self.head_cy, 0))
        mesh.add_quad_box(head_c, self.head_s / 2, s.skin, yaw=head_yaw, pitch=head_pitch, bevel=0.25)

        Mh = rot_y(head_yaw)[:3, :3] @ rot_x(head_pitch)[:3, :3]
        face_local = np.array([0, 0, -self.head_s / 2 - 0.005])
        eye_off = self.head_s * 0.17
        for sign in (-1, 1):
            e_local = np.array([sign * eye_off, self.head_s * 0.06, -self.head_s / 2 - 0.004])
            e_world = head_c + Mh @ e_local
            mesh.add_quad_box(e_world, (self.head_s * 0.09, self.head_s * 0.07, 0.006), s.eye, yaw=head_yaw)
        mouth_local = np.array([0, -self.head_s * 0.22, -self.head_s / 2 - 0.004])
        mesh.add_quad_box(head_c + Mh @ mouth_local, (self.head_s * 0.16, self.head_s * 0.045, 0.006),
                           s.mouth, yaw=head_yaw)

        hair_style = s.hair_style
        hair_c = head_c + Mh @ np.array([0, self.head_s * 0.30, 0])
        if hair_style == "spiky":
            for i, dx in enumerate([-0.6, -0.2, 0.2, 0.6]):
                spike_c = head_c + Mh @ np.array([dx * self.head_s, self.head_s * 0.45, -0.02])
                mesh.add_quad_box(spike_c, (self.head_s * 0.10, self.head_s * 0.22, self.head_s * 0.10),
                                   s.hair, yaw=head_yaw + 8 * i)
        else:
            mesh.add_quad_box(hair_c, (self.head_s * 0.52, self.head_s * 0.28, self.head_s * 0.55),
                               s.hair, yaw=head_yaw, bevel=0.3)
            if hair_style == "ponytail":
                pony_d = 0.30 * self.head_s * 2
                yr = math.radians(head_yaw)
                pony_local = np.array([0, self.head_s * 0.05, self.head_s * 0.55])
                pony_c = head_c + Mh @ pony_local
                mesh.add_quad_box(pony_c, (self.head_s * 0.11, self.head_s * 0.35, self.head_s * 0.11),
                                   s.hair, yaw=head_yaw)

        shoulder_y_local = self.torso_h * 0.44
        for side, sign in (("l", -1), ("r", 1)):
            sh_pivot_local = (sign * (self.torso_w / 2 + 0.03), self.hip_y + self.torso_h - 0.04, 0)
            sh_pivot_world = world(sh_pivot_local)
            shoulder_deg = self.pose[f"{side}_shoulder"]
            elbow_deg = self.pose[f"{side}_elbow"]
            Marm = rot_y(yaw)[:3, :3] @ rot_x(shoulder_deg)[:3, :3]
            upper_len = 0.26 * s.scale
            upper_mid_local = np.array([0, -upper_len / 2, 0])
            upper_c = sh_pivot_world + Marm @ upper_mid_local
            mesh.add_quad_box(upper_c, (0.055 * s.scale, upper_len / 2, 0.055 * s.scale), s.skin,
                               yaw=yaw, pitch=shoulder_deg)
            elbow_world = sh_pivot_world + Marm @ np.array([0, -upper_len, 0])
            Mforearm = Marm @ rot_x(elbow_deg)[:3, :3]
            fore_len = 0.24 * s.scale
            fore_mid_local = np.array([0, -fore_len / 2, 0])
            fore_c = elbow_world + Mforearm @ fore_mid_local
            total_pitch = shoulder_deg + elbow_deg
            mesh.add_quad_box(fore_c, (0.05 * s.scale, fore_len / 2, 0.05 * s.scale), s.skin,
                               yaw=yaw, pitch=total_pitch)
            hand_world = elbow_world + Mforearm @ np.array([0, -fore_len, 0])
            mesh.add_quad_box(hand_world, (0.06 * s.scale, 0.07 * s.scale, 0.045 * s.scale), s.skin,
                               yaw=yaw, pitch=total_pitch)

        for side, sign in (("l", -1), ("r", 1)):
            hip_pivot_local = (sign * self.torso_w * 0.28, self.hip_y, 0)
            hip_pivot_world = world(hip_pivot_local)
            hip_deg = self.pose[f"{side}_hip"]
            knee_deg = self.pose[f"{side}_knee"]
            Mleg = rot_y(yaw)[:3, :3] @ rot_x(hip_deg)[:3, :3]
            thigh_len = 0.32 * s.scale
            thigh_c = hip_pivot_world + Mleg @ np.array([0, -thigh_len / 2, 0])
            mesh.add_quad_box(thigh_c, (0.075 * s.scale, thigh_len / 2, 0.075 * s.scale), s.pants,
                               yaw=yaw, pitch=hip_deg)
            knee_world = hip_pivot_world + Mleg @ np.array([0, -thigh_len, 0])
            Mshin = Mleg @ rot_x(-knee_deg)[:3, :3]
            shin_len = 0.30 * s.scale
            shin_c = knee_world + Mshin @ np.array([0, -shin_len / 2, 0])
            total_pitch = hip_deg - knee_deg
            mesh.add_quad_box(shin_c, (0.065 * s.scale, shin_len / 2, 0.065 * s.scale), s.pants,
                               yaw=yaw, pitch=total_pitch)
            foot_world = knee_world + Mshin @ np.array([0, -shin_len, 0.05])
            mesh.add_quad_box(foot_world, (0.08 * s.scale, 0.04 * s.scale, 0.13 * s.scale), s.shoes,
                               yaw=yaw, pitch=total_pitch)

        return mesh

    def feet_ground_point(self):
        return (self.x, self.z)

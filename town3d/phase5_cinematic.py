"""PHASE 5 cinematic sample: ~13s / 24fps using the v2 engine, character and
environment systems. Seven shots, each with a stated narrative purpose, per
the user's brief. Does NOT touch the original v1 pipeline that produced the
delivered "Skyline Town" video.

Run: python3 town3d/phase5_cinematic.py
Outputs: town_render/phase5_cinematic.mp4 + a handful of still frames for
review, plus a frames-list dump used by qc_artistic.check_temporal.
"""
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import imageio_ffmpeg

from town3d.engine2 import Scene2, Camera2, render_frame2, PointLight
from town3d.environment import build_city_block
from town3d.character import Character, CharacterStyle
from town3d import camera_rig as rig

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 540, 960, 24

SHOT_PLAN = [
    # (seconds, purpose)
    (1.6, "Wide aerial city shot -- establishes the whole block, scale, time of day."),
    (1.8, "Camera descends toward one building -- directs attention to where the story happens."),
    (1.6, "Character introduction at street level -- the protagonist enters frame."),
    (1.8, "Character movement (walk cycle) -- establishes they are going somewhere with purpose."),
    (1.6, "Close-up on the character -- an emotional beat, read their face."),
    (2.0, "Environmental interaction -- character stops at a streetlight/tree, grounding them in the space."),
    (2.2, "Final cinematic pull-out/orbit -- closes the sequence, leaves the world feeling lived-in."),
]


def build_scene(seed=22):
    sc = Scene2(sky_top=(130, 175, 225), sky_bottom=(225, 235, 240), ambient=0.5,
                light_dir=(0.42, 0.78, 0.32), fog_start=16, fog_end=55)
    info = build_city_block(sc.mesh, seed=seed)
    for (x, y, z) in info["light_anchors"][:8]:
        sc.point_lights.append(PointLight(pos=(x, y, z), color=(255, 215, 150), intensity=1.0, radius=5))
    char = Character(1.1, -3.2, yaw=200, style=CharacterStyle(hair_style="ponytail", shirt=(25, 140, 135)))
    return sc, char, info


def build_shot_poses():
    shots = []
    shots.append((rig.aerial_descend((6, 10, 10), (6, 10, 10), (0, 1, -14), (0, 1, -14)), 1.0))
    shots.append(("aerial", None))
    shots.append(("descend", None))
    shots.append(("intro", None))
    shots.append(("walk", None))
    shots.append(("closeup", None))
    shots.append(("interact", None))
    shots.append(("outro", None))
    return shots


def main():
    sc, char, info = build_scene()
    out_dir = ROOT / "town_render"
    out_dir.mkdir(exist_ok=True)

    char_pos = (1.1, -3.2)
    char_yaw = 200
    streetlight_xz = info["light_anchors"][1][0], info["light_anchors"][1][2]

    shots = []
    shots.append((rig.tracking_shot((7, 11, 9), (2, 8, 3), (0, 1, -16), (0, 1, -10)), "wide aerial"))
    shots.append((rig.tracking_shot((2, 8, 3), (1.6, 3.2, 0.6), (0, 1, -10), (char_pos[0], 1.2, char_pos[1])), "descend"))
    shots.append((rig.push_in((2.6, 1.8, 2.4), (1.8, 1.65, 1.6), (char_pos[0], 1.1, char_pos[1])), "intro"))
    shots.append((rig.tracking_shot((2.4, 1.55, 0.6), (0.6, 1.55, -2.6),
                                     (char_pos[0], 1.1, char_pos[1] - 1), (char_pos[0] - 1.2, 1.1, char_pos[1] - 4)), "walk"))
    # character.py places the face/eyes at LOCAL -z on the head (see face_local in
    # character.py), so the world-space facing direction is Ry(head_yaw) @ (0,0,-1) =
    # (-sin(head_yaw), -cos(head_yaw)) -- NOT (sin,cos). At yaw=200 that is (+0.342,+0.940).
    # The close-up camera must sit further along that direction from the character and
    # look back at them, otherwise it only sees the back of the head/hair.
    end_x, end_z = char_pos[0] - 1.2, char_pos[1] - 4.0
    face_dir = (0.342, 0.940)
    cu_target = (end_x, 1.42, end_z)
    cu_far = (end_x + face_dir[0] * 2.3, 1.75, end_z + face_dir[1] * 2.3)
    cu_near = (end_x + face_dir[0] * 0.95, 1.55, end_z + face_dir[1] * 0.95)
    shots.append((rig.push_in(cu_far, cu_near, cu_target), "closeup"))
    shots.append((rig.tracking_shot(cu_near, (end_x + face_dir[0] * 1.6, 1.55, end_z + face_dir[1] * 1.6 + 1.0),
                                     cu_target, (streetlight_xz[0], 1.0, streetlight_xz[1])), "interact"))
    # Final pull-out/up bookends the opening aerial: starts close on the character,
    # rises and widens to re-reveal the whole block so the world reads as lived-in.
    shots.append((rig.tracking_shot((end_x + face_dir[0] * 1.6, 1.6, end_z + face_dir[1] * 1.6 + 1.0), (7, 11, 8.5),
                                     (streetlight_xz[0], 1.1, streetlight_xz[1]), (0, 1, -10)), "outro"))

    frame_durs = [max(1, round(sec * FPS)) for sec, _ in SHOT_PLAN]

    frames = []
    camera_positions = []

    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(out_dir / "phase5_cinematic.mp4")],
        stdin=subprocess.PIPE,
    )

    t_start = time.time()
    walk_phase = 0.0
    global_frame = 0
    saved_stills = {}
    for shot_idx, ((pose_fn, _tag), n_frames) in enumerate(zip(shots, frame_durs)):
        is_walk = shot_idx == 3
        is_interact = shot_idx == 5
        for f in range(n_frames):
            t = f / max(1, n_frames - 1)
            eye, target = pose_fn(t)
            cam = Camera2(eye=eye, target=target, fov=52)

            if is_walk:
                walk_phase = (walk_phase + 0.045) % 1.0
                char.walk_cycle(walk_phase)
                cx = char_pos[0] - 1.2 * t
                cz = char_pos[1] - 4.0 * t
                char.x, char.z = cx, cz
            elif is_interact:
                char.set_pose(head_turn=15 * t, l_shoulder=0, r_shoulder=0)
            elif shot_idx == 2:
                char.set_pose(head_turn=0, l_shoulder=0, r_shoulder=0)
            char.x = char.x if is_walk else char.x
            char.yaw = char_yaw if shot_idx < 3 else (char_yaw - 25 * (1 if is_walk else 0))

            scene_snapshot = Scene2(sc.sky_top, sc.sky_bottom, ambient=sc.ambient,
                                     light_dir=tuple(sc.light_dir), fog_start=sc.fog_start, fog_end=sc.fog_end)
            scene_snapshot.mesh = sc.mesh  # reuse static city geometry (char added fresh per frame)
            scene_snapshot.point_lights = sc.point_lights
            scene_snapshot.shadow_casters = [(char.x, char.z, 0.33)]

            char_mesh_backup_len = len(sc.mesh.faces)
            char.build(sc.mesh)

            img = render_frame2(scene_snapshot, cam, W, H, supersample=2)
            arr = np.asarray(img, dtype=np.uint8)
            proc.stdin.write(arr.tobytes())

            del sc.mesh.faces[char_mesh_backup_len:]

            if global_frame % 6 == 0:
                frames.append(arr)
                camera_positions.append((eye, target))
            if shot_idx in (0, 2, 4, 6) and f == n_frames // 2:
                saved_stills[f"shot{shot_idx+1}"] = img.copy()

            global_frame += 1

    proc.stdin.close()
    proc.wait()
    elapsed = time.time() - t_start
    total_frames = global_frame

    for name, img in saved_stills.items():
        img.save(out_dir / f"phase5_{name}.jpg", quality=92)

    print(f"TOTAL_FRAMES={total_frames} ELAPSED={elapsed:.2f}s MS_PER_FRAME={elapsed/total_frames*1000:.1f}")
    return frames, camera_positions, total_frames, elapsed


if __name__ == "__main__":
    main()

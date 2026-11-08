"""PHASE 9 -- multi-worker (CPU, no GPU) parallel rendering benchmark.

This does NOT change what gets rendered (same shots, same camera rig, same
Character/Environment code as phase5_cinematic.py) -- it only changes HOW the
301 frames get rendered: split across worker processes instead of one single
process, pulling multiple CPU cores (this sandbox has 2) at once.

Honest framing, confirmed by inspecting the sandbox directly before writing
any of this (see chat): there is NO GPU here (no /dev/nvidia*, no lspci VGA
device, nvidia-smi absent) and only 2 vCPUs. So "GPU rendering" is not an
available option to test or claim. What IS available and is used here:
multiprocessing across the 2 CPU cores actually present.

Run: python3 town3d/phase9_parallel_render.py
Outputs: town_render/phase9_parallel.mp4 + timing numbers printed and saved
to town_render/phase9_timing.json (serial vs parallel, same 301 frames).
"""
import json
import multiprocessing as mp
import os
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
from town3d.phase5_cinematic import build_scene, SHOT_PLAN

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 540, 960, 24

_WORKER_STATE = {}


def _build_shots(sc, info, char_pos, char_yaw):
    _end_x, _end_z = char_pos[0] - 1.2, char_pos[1] - 4.0
    streetlight_anchor = min(info["light_anchors"], key=lambda a: (a[0] - _end_x) ** 2 + (a[2] - _end_z) ** 2)
    streetlight_xz = streetlight_anchor[0], streetlight_anchor[2]
    face_dir = (0.342, 0.940)
    end_x, end_z = char_pos[0] - 1.2, char_pos[1] - 4.0
    cu_target = (end_x, 1.42, end_z)
    cu_far = (end_x + face_dir[0] * 2.3, 1.75, end_z + face_dir[1] * 2.3)
    cu_near = (end_x + face_dir[0] * 0.95, 1.55, end_z + face_dir[1] * 0.95)

    shots = []
    shots.append((rig.tracking_shot((7, 11, 9), (2, 8, 3), (0, 1, -16), (0, 1, -10)), "wide aerial"))
    shots.append((rig.tracking_shot((2, 8, 3), (1.6, 3.2, 0.6), (0, 1, -10), (char_pos[0], 1.2, char_pos[1])), "descend"))
    shots.append((rig.push_in((2.6, 1.8, 2.4), (1.8, 1.65, 1.6), (char_pos[0], 1.1, char_pos[1])), "intro"))
    shots.append((rig.tracking_shot((2.4, 1.55, 0.6), (0.6, 1.55, -2.6),
                                     (char_pos[0], 1.1, char_pos[1] - 1), (char_pos[0] - 1.2, 1.1, char_pos[1] - 4)), "walk"))
    shots.append((rig.push_in(cu_far, cu_near, cu_target), "closeup"))
    shots.append((rig.tracking_shot(cu_near, (end_x + face_dir[0] * 1.6, 1.55, end_z + face_dir[1] * 1.6 + 1.0),
                                     cu_target, (streetlight_xz[0], 1.0, streetlight_xz[1])), "interact"))
    shots.append((rig.tracking_shot((end_x + face_dir[0] * 1.6, 1.6, end_z + face_dir[1] * 1.6 + 1.0), (7, 11, 8.5),
                                     (streetlight_xz[0], 1.1, streetlight_xz[1]), (0, 1, -10)), "outro"))
    return shots, streetlight_xz


def _frame_plan():
    """Pure-data plan: for every global frame index, which shot it belongs to
    and the local t in [0,1] within that shot. No mesh objects here -- safe
    to build once in the main process and hand indices to workers."""
    frame_durs = [max(1, round(sec * FPS)) for sec, _ in SHOT_PLAN]
    plan = []
    for shot_idx, n_frames in enumerate(frame_durs):
        for f in range(n_frames):
            t = f / max(1, n_frames - 1)
            plan.append((shot_idx, f, n_frames, t))
    return plan


def _worker_init(seed, char_pos, char_yaw, disable_aa):
    """Runs once per worker process: build the static city scene + character
    exactly once, reused for every frame that worker renders."""
    sc, char, info = build_scene(seed=seed)
    shots, streetlight_xz = _build_shots(sc, info, char_pos, char_yaw)
    _WORKER_STATE.update(sc=sc, char=char, shots=shots, streetlight_xz=streetlight_xz,
                          char_pos=char_pos, char_yaw=char_yaw, disable_aa=disable_aa)


def _render_one(args):
    global_frame, shot_idx, f, n_frames, t = args
    sc = _WORKER_STATE["sc"]
    char = _WORKER_STATE["char"]
    shots = _WORKER_STATE["shots"]
    char_pos = _WORKER_STATE["char_pos"]
    char_yaw = _WORKER_STATE["char_yaw"]

    is_walk = shot_idx == 3
    is_interact = shot_idx == 5
    pose_fn, _tag = shots[shot_idx]
    eye, target = pose_fn(t)
    cam = Camera2(eye=eye, target=target, fov=52)

    if is_walk:
        walk_phase = (0.045 * f) % 1.0
        char.walk_cycle(walk_phase)
        char.x = char_pos[0] - 1.2 * t
        char.z = char_pos[1] - 4.0 * t
    elif is_interact:
        char.set_pose(head_turn=15 * t, l_shoulder=0, r_shoulder=0)
    elif shot_idx == 2:
        char.set_pose(head_turn=0, l_shoulder=0, r_shoulder=0)
        char.x, char.z = char_pos
    else:
        char.x, char.z = char_pos
    char.yaw = char_yaw if shot_idx < 3 else (char_yaw - 25 * (1 if is_walk else 0))

    scene_snapshot = Scene2(sc.sky_top, sc.sky_bottom, ambient=sc.ambient,
                             light_dir=tuple(sc.light_dir), fog_start=sc.fog_start, fog_end=sc.fog_end)
    scene_snapshot.mesh = sc.mesh
    scene_snapshot.point_lights = sc.point_lights
    scene_snapshot.shadow_casters = [(char.x, char.z, 0.33)]

    base_len = len(sc.mesh.faces)
    char.build(sc.mesh)
    ss = 1 if _WORKER_STATE["disable_aa"] else 2
    img = render_frame2(scene_snapshot, cam, W, H, supersample=ss)
    arr = np.asarray(img, dtype=np.uint8)
    del sc.mesh.faces[base_len:]
    return global_frame, arr.tobytes()


def render_parallel(n_workers, disable_aa, out_path, char_pos=(1.1, -3.2), char_yaw=200, seed=22):
    plan = _frame_plan()
    tasks = [(i, *p) for i, p in enumerate(plan)]
    t0 = time.time()
    with mp.Pool(processes=n_workers, initializer=_worker_init,
                 initargs=(seed, char_pos, char_yaw, disable_aa)) as pool:
        results = pool.map(_render_one, tasks, chunksize=4)
    results.sort(key=lambda r: r[0])
    t_render = time.time() - t0

    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(out_path)],
        stdin=subprocess.PIPE,
    )
    for _, raw in results:
        proc.stdin.write(raw)
    proc.stdin.close()
    proc.wait()
    t_total = time.time() - t0
    return len(tasks), t_render, t_total


def render_serial(disable_aa, out_path, char_pos=(1.1, -3.2), char_yaw=200, seed=22):
    plan = _frame_plan()
    _worker_init(seed, char_pos, char_yaw, disable_aa)
    t0 = time.time()
    frames = []
    for i, p in enumerate(plan):
        _, raw = _render_one((i, *p))
        frames.append(raw)
    t_render = time.time() - t0

    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
         "-pix_fmt", "yuv420p", str(out_path)],
        stdin=subprocess.PIPE,
    )
    for raw in frames:
        proc.stdin.write(raw)
    proc.stdin.close()
    proc.wait()
    t_total = time.time() - t0
    return len(plan), t_render, t_total


if __name__ == "__main__":
    out_dir = ROOT / "town_render"
    out_dir.mkdir(exist_ok=True)
    ncpu = mp.cpu_count()
    print(f"Detected {ncpu} CPU core(s). No GPU present (verified: no nvidia-smi, no /dev/nvidia*).")

    results = {}

    n, t_render, t_total = render_serial(disable_aa=False, out_path=out_dir / "phase9_serial_AA.mp4")
    print(f"[serial, AA on ] {n} frames, render={t_render:.1f}s total={t_total:.1f}s")
    results["serial_aa_on"] = {"frames": n, "render_s": round(t_render, 1), "total_s": round(t_total, 1)}

    n, t_render, t_total = render_parallel(ncpu, disable_aa=False, out_path=out_dir / "phase9_parallel_AA.mp4")
    print(f"[{ncpu}-worker, AA on ] {n} frames, render={t_render:.1f}s total={t_total:.1f}s")
    results[f"parallel{ncpu}_aa_on"] = {"frames": n, "render_s": round(t_render, 1), "total_s": round(t_total, 1)}

    n, t_render, t_total = render_parallel(ncpu, disable_aa=True, out_path=out_dir / "phase9_parallel_noAA.mp4")
    print(f"[{ncpu}-worker, AA off] {n} frames, render={t_render:.1f}s total={t_total:.1f}s")
    results[f"parallel{ncpu}_aa_off"] = {"frames": n, "render_s": round(t_render, 1), "total_s": round(t_total, 1)}

    with open(out_dir / "phase9_timing.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved timing to town_render/phase9_timing.json")

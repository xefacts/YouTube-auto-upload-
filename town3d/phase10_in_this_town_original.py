"""PHASE 10 -- an original ~16s sample in the "In this town..." genre.

Explicitly NOT a copy of anything in the "In the town" Drive reference
folder: original story ("the red door"), original character name/styling,
original city layout (new seed), original prop (the door) that does not
exist in any reference video or in our own prior Skyline_Town_FINAL.mp4.
What IS deliberately reused from the 9 references' observed style (see
PHASE9_REFERENCE_FORENSICS_AND_SPEED.md section 3): word-by-word bold
yellow outlined captions, fast per-shot cuts, a continuously moving camera,
and a distinct lighting/color grade per shot.

What is deliberately fixed vs. the Skyline_Town_FINAL defects found in
Phase 9 section 4: the character actually performs a real walk cycle (no
multi-second frozen pose), every shot keeps real point-light and
directional lighting (no near-black / flat-silhouette stretch), and the
road is the textured build_road() asset (lane line + sidewalks + curbs),
never a long static bare plane.

Rendering uses the Phase 9 multi-worker CPU pipeline (2 processes, this
sandbox's full CPU count -- no GPU exists here, confirmed in Phase 9) with
anti-aliasing ON only for the four closer/hero shots and OFF for the four
wider/transit shots, per the Phase 9 recommendation.

Run: python3 town3d/phase10_in_this_town_original.py
Output: town_render/in_this_town_original.mp4 (576x1024, 30fps, stereo audio,
burned-in word captions).
"""
import json
import multiprocessing as mp
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

from town3d.engine2 import Scene2, Camera2, render_frame2, PointLight
from town3d.environment import build_city_block
from town3d.character import Character, CharacterStyle
from town3d import camera_rig as rig

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 576, 1024, 30
FONT_PATH = str(ROOT / "town3d" / "assets" / "Anton-Regular.ttf")
AUDIO_DIR = ROOT / "town_audio"
OUT_DIR = ROOT / "town_render"

DOOR_POS = (-1.55, 1.25, -7.2)   # original prop, doesn't exist in any reference or in Skyline_Town_FINAL
DOOR_HALF = (0.34, 0.62, 0.04)

# -- story: 8 lines, each its own shot. Durations come from the ACTUAL
# generated TTS clip lengths (measured below with ffmpeg), not guessed.
LINES = [
    "In this town, doors don't change color.",
    "Until last night.",
    "Kian saw it first.",
    "A door. Painted red.",
    "Nobody paints doors red here.",
    "Everyone knows the rule.",
    "Never knock twice.",
    "He knocked three times.",
]

# Per-shot lighting presets -- a different color grade every shot, so no
# stretch is ever flat/unlit (the Phase 9 "dull lighting" defect).
LIGHTING = [
    dict(sky_top=(120, 165, 220), sky_bottom=(225, 235, 240), ambient=0.55, light_dir=(0.40, 0.80, 0.30)),  # 1 day wide
    dict(sky_top=(70, 80, 130), sky_bottom=(230, 150, 110), ambient=0.42, light_dir=(0.30, 0.55, 0.55)),     # 2 dusk descend
    dict(sky_top=(12, 16, 38), sky_bottom=(40, 45, 70), ambient=0.30, light_dir=(0.10, 0.60, 0.30)),          # 3 night intro
    dict(sky_top=(18, 10, 18), sky_bottom=(55, 20, 22), ambient=0.34, light_dir=(0.20, 0.50, 0.40)),          # 4 door reveal, red undertone
    dict(sky_top=(10, 14, 34), sky_bottom=(35, 38, 62), ambient=0.33, light_dir=(0.15, 0.55, 0.35)),          # 5 walk, night blue
    dict(sky_top=(14, 18, 40), sky_bottom=(42, 46, 70), ambient=0.38, light_dir=(0.20, 0.65, 0.30)),          # 6 closeup worried, cooler
    dict(sky_top=(24, 10, 14), sky_bottom=(70, 24, 20), ambient=0.36, light_dir=(0.25, 0.55, 0.40)),          # 7 interact, tense red
    dict(sky_top=(30, 6, 8), sky_bottom=(90, 22, 16), ambient=0.40, light_dir=(0.20, 0.50, 0.45)),            # 8 final, deep red/orange
]

AA_ON = [False, False, False, True, False, True, True, True]  # hero/close shots keep AA; wide/transit don't

_WORKER_STATE = {}


def build_scene(seed=77):
    sc = Scene2(sky_top=(130, 175, 225), sky_bottom=(225, 235, 240), ambient=0.5,
                light_dir=(0.42, 0.78, 0.32), fog_start=16, fog_end=55)
    info = build_city_block(sc.mesh, seed=seed)
    for (x, y, z) in info["light_anchors"][:8]:
        sc.point_lights.append(PointLight(pos=(x, y, z), color=(255, 205, 140), intensity=1.05, radius=5))
    # the red door: an original prop that is not in any reference video or Skyline_Town_FINAL
    dx, dy, dz = DOOR_POS
    sc.mesh.add_quad_box((dx, dy, dz), DOOR_HALF, (168, 28, 26), yaw=90, shade_top=1.05, shade_side=1.0)
    sc.mesh.add_quad_box((dx, dy + DOOR_HALF[1] + 0.03, dz), (DOOR_HALF[0] + 0.04, 0.03, 0.05), (235, 225, 200), yaw=90)
    sc.point_lights.append(PointLight(pos=(dx + 0.4, dy + 0.3, dz), color=(255, 70, 60), intensity=0.9, radius=3.0))
    char = Character(1.1, -3.2, yaw=200, style=CharacterStyle(hair_style="spiky", shirt=(60, 90, 150),
                                                               pants=(40, 40, 45), hair=(30, 22, 18)))
    return sc, char, info


def build_shots(char_pos, char_yaw):
    end_x, end_z = char_pos[0] - 1.2, char_pos[1] - 4.0
    face_dir = (0.342, 0.940)  # verified formula: world facing = (-sin(yaw), -cos(yaw)) at yaw=200
    cu_target = (end_x, 1.42, end_z)
    cu_far = (end_x + face_dir[0] * 2.3, 1.75, end_z + face_dir[1] * 2.3)
    cu_near = (end_x + face_dir[0] * 0.95, 1.55, end_z + face_dir[1] * 0.95)
    dx, dy, dz = DOOR_POS

    shots = []
    shots.append(rig.tracking_shot((7.5, 11.5, 9.5), (2.3, 8, 3), (0, 1, -16), (0, 1, -10)))          # 1 wide aerial
    shots.append(rig.tracking_shot((2.3, 8, 3), (1.6, 3.2, 0.6), (0, 1, -10), (char_pos[0], 1.2, char_pos[1])))  # 2 descend
    shots.append(rig.push_in((2.6, 1.8, 2.4), (1.8, 1.65, 1.6), (char_pos[0], 1.1, char_pos[1])))      # 3 intro
    # Door is 0.68 wide x 1.24 tall x 0.08 deep -- at 52deg FOV, anything
    # closer than ~2.1 units overflows the frame vertically (measured from
    # the first render: a sub-1-unit camera made the door fill the whole
    # screen like a wall instead of reading as a door). Keep all door-shot
    # distances >= ~2.3 units so the door AND its surrounding wall/sidewalk
    # stay in frame.
    shots.append(rig.push_in((dx + 3.6, 2.6, dz + 3.0), (dx + 2.0, 1.7, dz + 1.7), (dx, dy, dz)))       # 4 door reveal
    shots.append(rig.tracking_shot((2.4, 1.55, 0.6), (dx + 2.1, 1.6, dz + 1.4),
                                    (char_pos[0], 1.1, char_pos[1] - 1), (dx, 1.2, dz)))                # 5 walk toward door
    shots.append(rig.push_in(cu_far, cu_near, cu_target))                                               # 6 closeup worried
    shots.append(rig.tracking_shot((end_x + face_dir[0] * 2.6, 1.8, end_z + face_dir[1] * 2.6),
                                    (end_x + face_dir[0] * 1.9, 1.65, end_z + face_dir[1] * 1.9 + 0.2),
                                    cu_target, (dx, dy, dz)))                                            # 7 interact w/ door (pulled back further still -- 1.5 units was still clipping into the head, see QC)
    shots.append(rig.pull_out((dx + 1.6, 1.8, dz + 1.6), (dx + 3.6, 3.8, dz + 4.0), (dx, dy, dz)))      # 8 final pull-out
    return shots


def _frame_plan(line_durations):
    plan = []
    for shot_idx, dur in enumerate(line_durations):
        n_frames = max(1, round(dur * FPS))
        for f in range(n_frames):
            t = f / max(1, n_frames - 1)
            plan.append((shot_idx, f, n_frames, t))
    return plan


def _worker_init(seed, char_pos, char_yaw):
    sc, char, info = build_scene(seed=seed)
    shots = build_shots(char_pos, char_yaw)
    _WORKER_STATE.update(sc=sc, char=char, shots=shots, char_pos=char_pos, char_yaw=char_yaw)


def _render_one(args):
    global_frame, shot_idx, f, n_frames, t = args
    sc = _WORKER_STATE["sc"]
    char = _WORKER_STATE["char"]
    shots = _WORKER_STATE["shots"]
    char_pos = _WORKER_STATE["char_pos"]
    char_yaw = _WORKER_STATE["char_yaw"]

    is_walk = shot_idx == 4   # shot 5 (0-indexed 4): walk toward door
    is_interact = shot_idx == 6  # shot 7: reach toward door

    pose_fn = shots[shot_idx]
    eye, target = pose_fn(t)
    cam = Camera2(eye=eye, target=target, fov=52)

    if is_walk:
        walk_phase = (0.05 * f) % 1.0
        char.walk_cycle(walk_phase)
        char.x = char_pos[0] - 1.2 * t
        char.z = char_pos[1] - 4.0 * t
    elif is_interact:
        char.set_pose(head_turn=12 * t, l_shoulder=0, r_shoulder=-10 * t)
        char.x, char.z = char_pos[0] - 1.2, char_pos[1] - 4.0
    elif shot_idx in (2, 5):
        char.set_pose(head_turn=0, l_shoulder=0, r_shoulder=0)
        char.x, char.z = char_pos
    else:
        char.x, char.z = char_pos
    char.yaw = char_yaw if shot_idx < 2 else (char_yaw - 25 * (1 if is_walk else 0))

    lp = LIGHTING[shot_idx]
    scene_snapshot = Scene2(lp["sky_top"], lp["sky_bottom"], ambient=lp["ambient"],
                             light_dir=lp["light_dir"], fog_start=sc.fog_start, fog_end=sc.fog_end)
    scene_snapshot.mesh = sc.mesh
    scene_snapshot.point_lights = sc.point_lights
    scene_snapshot.shadow_casters = [(char.x, char.z, 0.33)]

    base_len = len(sc.mesh.faces)
    char.build(sc.mesh)
    ss = 2 if AA_ON[shot_idx] else 1
    img = render_frame2(scene_snapshot, cam, W, H, supersample=ss)
    arr = np.asarray(img, dtype=np.uint8)
    del sc.mesh.faces[base_len:]
    return global_frame, arr.tobytes()


def render_all(line_durations, char_pos=(1.1, -3.2), char_yaw=200, seed=77):
    plan = _frame_plan(line_durations)
    tasks = [(i, *p) for i, p in enumerate(plan)]
    ncpu = mp.cpu_count()
    t0 = time.time()
    with mp.Pool(processes=ncpu, initializer=_worker_init, initargs=(seed, char_pos, char_yaw)) as pool:
        results = pool.map(_render_one, tasks, chunksize=4)
    results.sort(key=lambda r: r[0])
    t_render = time.time() - t0
    print(f"Rendered {len(tasks)} frames with {ncpu} workers in {t_render:.1f}s "
          f"({t_render / len(tasks) * 1000:.1f} ms/frame avg)")
    return [r[1] for r in results], t_render


def build_word_schedule(lines, line_durations, shot_start_times):
    """Evenly split each line's MEASURED TTS duration across its words.
    This is a stated approximation (we have no forced-alignment/ASR tool to
    get real per-word timestamps) -- noted here and in the report rather
    than presented as exact."""
    schedule = []
    for line, dur, t0 in zip(lines, line_durations, shot_start_times):
        words = line.split()
        per = dur / len(words)
        for i, w in enumerate(words):
            schedule.append((t0 + i * per, t0 + (i + 1) * per, w.strip(".,")))
    return schedule


def burn_captions(raw_frames, word_schedule, out_dir):
    font = ImageFont.truetype(FONT_PATH, 64)
    out_frames = []
    for i, raw in enumerate(raw_frames):
        t = i / FPS
        img = Image.frombytes("RGB", (W, H), raw).convert("RGB")
        word = next((w for (s, e, w) in word_schedule if s <= t < e), None)
        if word:
            draw = ImageDraw.Draw(img)
            bbox = draw.textbbox((0, 0), word.upper(), font=font, stroke_width=8)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (W - tw) / 2 - bbox[0]
            y = H * 0.62 - th / 2 - bbox[1]
            draw.text((x, y), word.upper(), font=font, fill=(255, 221, 51),
                       stroke_width=8, stroke_fill=(20, 20, 20))
        out_frames.append(np.asarray(img, dtype=np.uint8).tobytes())
    return out_frames


def mux_audio(video_only_mp4, line_files, out_path):
    # concat the 8 TTS clips with a tiny gap matching the frame-rounded shot
    # durations, convert to stereo, mux onto the silent video.
    concat_list = OUT_DIR / "phase10_audio_concat.txt"
    with open(concat_list, "w") as f:
        for lf in line_files:
            f.write(f"file '{Path(lf).resolve()}'\n")
    concat_wav = OUT_DIR / "phase10_audio_concat.wav"
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list),
                    "-ac", "2", "-ar", "44100", str(concat_wav)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run([FFMPEG, "-y", "-i", str(video_only_mp4), "-i", str(concat_wav),
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", "-shortest", str(out_path)],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    OUT_DIR.mkdir(exist_ok=True)
    print("CPU count:", mp.cpu_count(), "(no GPU present in this sandbox)")

    # 1) measure the ACTUAL generated TTS durations (not estimated)
    line_files = [AUDIO_DIR / f"line{i+1}.mp3" for i in range(len(LINES))]
    durations = []
    for lf in line_files:
        out = subprocess.run([FFMPEG, "-i", str(lf), "-hide_banner"], stderr=subprocess.PIPE).stderr.decode()
        dur = 2.0
        for ln in out.splitlines():
            if "Duration" in ln:
                hh, mm, ss = ln.split("Duration:")[1].split(",")[0].strip().split(":")
                dur = int(hh) * 3600 + int(mm) * 60 + float(ss)
        durations.append(dur)
    print("Measured line durations (s):", [round(d, 2) for d in durations])

    shot_start_times = [sum(durations[:i]) for i in range(len(durations))]
    total_s = sum(durations)
    print(f"Total narration-driven video length: {total_s:.2f}s")

    # 2) render frames (parallel CPU workers, Phase 9 pipeline)
    raw_frames, t_render = render_all(durations)

    # 3) burn word captions synced to measured per-line audio duration
    word_schedule = build_word_schedule(LINES, durations, shot_start_times)
    captioned = burn_captions(raw_frames, word_schedule, OUT_DIR)

    # 4) encode silent video, then mux the real narration audio on top
    silent_mp4 = OUT_DIR / "phase10_silent.mp4"
    proc = subprocess.Popen(
        [FFMPEG, "-y", "-f", "rawvideo", "-pixel_format", "rgb24",
         "-video_size", f"{W}x{H}", "-framerate", str(FPS), "-i", "-",
         "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
         "-pix_fmt", "yuv420p", str(silent_mp4)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for raw in captioned:
        proc.stdin.write(raw)
    proc.stdin.close()
    proc.wait()

    final_mp4 = OUT_DIR / "in_this_town_original.mp4"
    mux_audio(silent_mp4, line_files, final_mp4)

    t_total = time.time()
    print("Saved:", final_mp4)

    with open(OUT_DIR / "phase10_timing.json", "w") as f:
        json.dump({"frames": len(raw_frames), "render_s": round(t_render, 1),
                   "total_video_s": round(total_s, 2), "cpu_count": mp.cpu_count()}, f, indent=2)

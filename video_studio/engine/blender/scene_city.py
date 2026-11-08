#!/usr/bin/env python3
"""video_studio/engine/blender/scene_city.py — original stylized 3D scene for headless Cycles CPU rendering.

Runs in BOTH environments:
  1. Official Blender:  blender --background --python scene_city.py -- <args>
  2. bpy pip wheel:     python scene_city.py <args>

Builds an ORIGINAL Roblox-inspired blocky avatar (beveled geometry, face, hair,
clothing, walk-cycle animation) inside an original small city block (road,
sidewalks, buildings with procedural window materials, streetlights, trees,
props) with an animated cinematic camera. Deterministic (seeded).

Args (all optional):
  --frames 1-24 --width 480 --height 854 --samples 32 --outdir PATH --fps 24
"""
import os, sys, json, time, math, random

# ---- locate args (blender inserts '--' before user args) ----
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default

FRAME_START = int(arg("--frames", "1").split("-")[0])
FRAME_END   = int(arg("--frames", "1-12").split("-")[1])
WIDTH, HEIGHT = int(arg("--width", "480")), int(arg("--height", "854"))
SAMPLES     = int(arg("--samples", "32"))
FPS         = int(arg("--fps", "24"))
OUTDIR      = os.path.abspath(arg("--outdir", os.path.join(os.getcwd(), "render_out")))
os.makedirs(OUTDIR, exist_ok=True)

try:
    import bpy  # pip wheel path
except ImportError:
    pass  # blender binary path: bpy already in scope
import bpy
from mathutils import Vector, Euler

rng = random.Random(42)
LOG = {"frames": {}, "meta": {}}

# ============================== helpers ==============================
def new_mat(name, color, rough=0.55, metal=0.0, emit=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit is not None:
        e = nt.nodes.new("ShaderNodeEmission")
        e.inputs["Color"].default_value = (*emit, 1.0)
        e.inputs["Strength"].default_value = 3.0
        for l in list(nt.links):
            if l.to_node.name == "Material Output":
                nt.links.remove(l)
        nt.links.new(e.outputs[0], nt.nodes["Material Output"].inputs[0])
    return m

def add_box(name, loc, size, mat, bevel=0.03, smooth=True, rot=(0, 0, 0), scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.scale = scale
    if bevel > 0:
        bev = ob.modifiers.new("Bevel", "BEVEL")
        bev.width = bevel
        bev.segments = 2
    if smooth:
        bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob

def add_sphere(name, loc, r, mat, seg=24):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    ob = bpy.context.object
    ob.name = name
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat)
    return ob

def add_cyl(name, loc, r, h, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    ob.data.materials.append(mat)
    return ob

# ============================== scene ==============================
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene
scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.cycles.samples = SAMPLES
scn.render.resolution_x, scn.render.resolution_y = WIDTH, HEIGHT
scn.render.fps = FPS
try:
    scn.view_settings.look = "Medium High Contrast"
except Exception:
    pass

# --- world: stylized warm-morning sky gradient (flat color; cheap + controllable) ---
w = bpy.data.worlds.new("Sky")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.62, 0.76, 0.94, 1.0)
bg.inputs["Strength"].default_value = 1.0
scn.world = w

# --- materials ---
M_asphalt  = new_mat("asphalt", (0.16, 0.16, 0.18), 0.9)
M_line     = new_mat("roadline", (0.9, 0.8, 0.3), 0.4)
M_walk     = new_mat("sidewalk", (0.72, 0.70, 0.66), 0.85)
M_grass    = new_mat("grass", (0.30, 0.48, 0.24), 0.9)
M_trunk    = new_mat("trunk", (0.35, 0.24, 0.16), 0.9)
M_leaf     = new_mat("leaf", (0.22, 0.42, 0.20), 0.85)
M_pole     = new_mat("pole", (0.25, 0.26, 0.30), 0.5, 0.4)
M_lamp     = new_mat("lamp", (1.0, 0.9, 0.7), 0.3, emit=(1.0, 0.85, 0.6))
M_glass    = new_mat("glasswin", (0.15, 0.2, 0.3), 0.15, 0.1)

def window_mat(seed):
    """Procedural window grid: emissive lit windows on facade."""
    m = bpy.data.materials.new(f"facade{seed}")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexBrick")
    for key, val in (("Color1", (0.85, 0.83, 0.80, 1.0)), ("Color2", (0.75, 0.72, 0.70, 1.0)),
                     ("Offset", 0.0), ("Offset Frequency", 2), ("Squash", 3.0)):
        try:
            tex.inputs[key].default_value = val
        except Exception:
            pass  # input renamed/absent across Blender versions
    coord = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(coord.outputs["Object"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    return m

BUILDING_COLORS = [(0.80, 0.74, 0.66), (0.70, 0.62, 0.55), (0.62, 0.66, 0.70),
                   (0.78, 0.70, 0.74), (0.68, 0.72, 0.62)]

# --- ground + road + sidewalks (street runs along Y axis) ---
add_box("ground", (0, 0, -0.25), 1, M_grass, bevel=0, smooth=False, scale=(90, 90, 0.5))
add_box("road", (0, 0, 0.01), 1, M_asphalt, bevel=0, smooth=False, scale=(9, 90, 0.02))
for y in range(-40, 41, 6):  # dashed centerline
    add_box(f"line{y}", (0, y, 0.03), 1, M_line, bevel=0, smooth=False, scale=(0.18, 2.2, 0.005))
add_box("walk_left", (-5.2, 0, 0.06), 1, M_walk, bevel=0, smooth=False, scale=(1.6, 90, 0.12))
add_box("walk_right", (5.2, 0, 0.06), 1, M_walk, bevel=0, smooth=False, scale=(1.6, 90, 0.12))

# --- buildings along both sides (varied heights/colors, windows) ---
def building(x, y, w_, d_, h, color):
    bm = window_mat(rng.randrange(1000))
    bsdf = next(n for n in bm.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    ob = add_box(f"bldg{x}_{y}", (x, y, h / 2), 1, bm, bevel=0.15, scale=(w_, d_, h))
    # roof slab
    add_box(f"roof{x}_{y}", (x, y, h + 0.15), 1, new_mat(f"roofm{x}_{y}", (0.3, 0.3, 0.32), 0.9),
            bevel=0, smooth=False, scale=(w_ * 1.04, d_ * 1.04, 0.3))
    return ob

for i in range(7):
    y = -30 + i * 9.5
    building(-9.5 - rng.uniform(0, 1.5), y + rng.uniform(-1, 1), rng.uniform(3.4, 5.0),
             rng.uniform(4, 6.5), rng.uniform(8, 22), BUILDING_COLORS[i % len(BUILDING_COLORS)])
    building(9.5 + rng.uniform(0, 1.5), y + rng.uniform(-1, 1), rng.uniform(3.4, 5.0),
             rng.uniform(4, 6.5), rng.uniform(8, 22), BUILDING_COLORS[(i + 2) % len(BUILDING_COLORS)])

# --- streetlights + trees + props ---
for i in range(6):
    y = -25 + i * 10
    side = -1 if i % 2 == 0 else 1
    add_cyl(f"pole{i}", (side * 5.8, y, 2.4), 0.09, 4.8, M_pole)
    add_cyl(f"arm{i}", (side * 5.8 - side * 0.55, y, 4.7), 0.06, 1.2, M_pole, rot=(0, math.radians(90), 0))
    add_sphere(f"lamp{i}", (side * 5.8 - side * 1.0, y, 4.62), 0.16, M_lamp, seg=16)
for i in range(5):
    y = -20 + i * 10
    add_cyl(f"trk{i}", (-7.2, y, 0.8), 0.16, 1.6, M_trunk)
    add_sphere(f"lvs{i}", (-7.2, y, 2.3), 1.15, M_leaf, seg=20)
    add_sphere(f"lvs2_{i}", (-7.2 + 0.5, y - 0.4, 1.8), 0.8, M_leaf, seg=16)
add_box("bench", (6.6, 3.0, 0.45), 1, new_mat("wood", (0.5, 0.35, 0.22), 0.8),
        bevel=0.05, scale=(0.5, 1.6, 0.08))
add_box("benchback", (7.0, 3.0, 0.75), 1, new_mat("wood2", (0.5, 0.35, 0.22), 0.8),
        bevel=0.05, rot=(0, math.radians(-12), 0), scale=(0.08, 1.6, 0.5))
add_cyl("hydrant", (-6.3, -6.0, 0.42), 0.14, 0.8, new_mat("hydr", (0.8, 0.15, 0.1), 0.4))

# ============================== character (original blocky avatar) ==============================
CHAR = {}  # parts dict

def build_character(root_loc=(0, 2.5, 0)):
    skin  = new_mat("skin", (0.96, 0.80, 0.66), 0.6)
    hair  = new_mat("hair", (0.13, 0.10, 0.09), 0.65)
    jacket= new_mat("jacket", (0.85, 0.32, 0.16), 0.7)
    pants = new_mat("pants", (0.20, 0.24, 0.36), 0.8)
    shoe  = new_mat("shoe", (0.92, 0.92, 0.94), 0.5)
    white = new_mat("white", (0.97, 0.97, 0.97), 0.4)
    dark  = new_mat("dark", (0.05, 0.05, 0.06), 0.4)

    hips = add_box("hips", (root_loc[0], root_loc[1], 1.05), 1, pants, bevel=0.06, scale=(0.62, 0.36, 0.34))
    torso = add_box("torso", (root_loc[0], root_loc[1], 1.52), 1, jacket, bevel=0.07, scale=(0.66, 0.38, 0.62))
    # hoodie strings
    add_cyl("stringL", (root_loc[0] - 0.12, root_loc[1] - 0.21, 1.5), 0.014, 0.28, white)
    add_cyl("stringR", (root_loc[0] + 0.12, root_loc[1] - 0.21, 1.5), 0.014, 0.28, white)
    # neck + head
    add_cyl("neck", (root_loc[0], root_loc[1], 1.88), 0.09, 0.14, skin)
    head = add_box("head", (root_loc[0], root_loc[1], 2.22), 1, skin, bevel=0.10, scale=(0.5, 0.46, 0.44))
    # hair: cap + fringe
    add_box("haircap", (root_loc[0], root_loc[1], 2.42), 1, hair, bevel=0.08, scale=(0.55, 0.50, 0.18))
    add_box("fringe", (root_loc[0], root_loc[1] - 0.20, 2.36), 1, hair, bevel=0.05, scale=(0.52, 0.14, 0.16))
    add_box("bangL", (root_loc[0] - 0.17, root_loc[1] - 0.22, 2.24), 1, hair, bevel=0.03, scale=(0.14, 0.10, 0.14))
    add_box("bangR", (root_loc[0] + 0.17, root_loc[1] - 0.22, 2.24), 1, hair, bevel=0.03, scale=(0.14, 0.10, 0.14))
    # face: eyes (white + pupil), brows, mouth
    ey = root_loc[1] - 0.215
    add_box("eyeL", (root_loc[0] - 0.12, ey, 2.28), 1, white, bevel=0.02, scale=(0.11, 0.05, 0.085))
    add_box("eyeR", (root_loc[0] + 0.12, ey, 2.28), 1, white, bevel=0.02, scale=(0.11, 0.05, 0.085))
    add_box("pupL", (root_loc[0] - 0.12, ey - 0.05, 2.28), 1, dark, bevel=0.01, scale=(0.055, 0.03, 0.055))
    add_box("pupR", (root_loc[0] + 0.12, ey - 0.05, 2.28), 1, dark, bevel=0.01, scale=(0.055, 0.03, 0.055))
    add_box("browL", (root_loc[0] - 0.12, ey - 0.01, 2.375), 1, hair, bevel=0.01, scale=(0.12, 0.03, 0.035))
    add_box("browR", (root_loc[0] + 0.12, ey - 0.01, 2.375), 1, hair, bevel=0.01, scale=(0.12, 0.03, 0.035))
    add_box("mouth", (root_loc[0], ey - 0.02, 2.08), 1, dark, bevel=0.01, scale=(0.14, 0.03, 0.035))
    # arms (pivot at shoulder via parent empties)
    armL = add_box("armL", (root_loc[0] - 0.44, root_loc[1], 1.55), 1, jacket, bevel=0.06, scale=(0.17, 0.19, 0.58))
    armR = add_box("armR", (root_loc[0] + 0.44, root_loc[1], 1.55), 1, jacket, bevel=0.06, scale=(0.17, 0.19, 0.58))
    handL = add_box("handL", (root_loc[0] - 0.44, root_loc[1], 1.16), 1, skin, bevel=0.05, scale=(0.16, 0.17, 0.16))
    handR = add_box("handR", (root_loc[0] + 0.44, root_loc[1], 1.16), 1, skin, bevel=0.05, scale=(0.16, 0.17, 0.16))
    # legs (pivot at hip)
    legL = add_box("legL", (root_loc[0] - 0.17, root_loc[1], 0.62), 1, pants, bevel=0.06, scale=(0.22, 0.24, 0.62))
    legR = add_box("legR", (root_loc[0] + 0.17, root_loc[1], 0.62), 1, pants, bevel=0.06, scale=(0.22, 0.24, 0.62))
    shoeL = add_box("shoeL", (root_loc[0] - 0.17, root_loc[1] - 0.05, 0.10), 1, shoe, bevel=0.05, scale=(0.24, 0.34, 0.14))
    shoeR = add_box("shoeR", (root_loc[0] + 0.17, root_loc[1] - 0.05, 0.10), 1, shoe, bevel=0.05, scale=(0.24, 0.34, 0.14))
    CHAR.update(dict(hips=hips, torso=torso, head=head, armL=armL, armR=armR,
                     handL=handL, handR=handR, legL=legL, legR=legR))
    return CHAR

build_character((0, 2.5, 0))

# ---- walk-cycle animation: character walks forward along the sidewalk ----
ch = CHAR
total = FPS * 12  # 12-second sample timeline
for f in range(0, total + 1, 2):
    t = f / FPS
    ph = t * 2.0 * math.pi  # walk phase (~2 steps/sec)
    if t < 5.0:   y = 2.5 + t * 1.1        # walk
    elif t < 8.0: y = 2.5 + 5.0 * 1.1      # pause (look around)
    else:         y = 2.5 + 5.0 * 1.1 + (t - 8.0) * 1.1  # walk on
    bob = abs(math.sin(ph)) * 0.045
    # whole body translates with walk; upper body bobs
    for part in ch.values():
        part.location.y = y
        part.keyframe_insert("location", frame=f)
    # limb swings (rotation around X)
    swing = 0.55
    ch["legL"].rotation_euler.x = math.sin(ph) * swing
    ch["legR"].rotation_euler.x = -math.sin(ph) * swing
    ch["armL"].rotation_euler.x = -math.sin(ph) * swing * 0.8
    ch["armR"].rotation_euler.x = math.sin(ph) * swing * 0.8
    ch["legL"].keyframe_insert("rotation_euler", frame=f)
    ch["legR"].keyframe_insert("rotation_euler", frame=f)
    ch["armL"].keyframe_insert("rotation_euler", frame=f)
    ch["armR"].keyframe_insert("rotation_euler", frame=f)
    ch["hips"].location.z = 1.05 + bob
    ch["torso"].location.z = 1.52 + bob
    ch["head"].location.z = 2.22 + bob
    ch["hips"].keyframe_insert("location", frame=f)
    ch["torso"].keyframe_insert("location", frame=f)
    ch["head"].keyframe_insert("location", frame=f)
    # head turn: look toward camera around t=4s
    look = max(-0.4, min(0.55, (t - 5.8) * 0.9)) if 5.8 < t < 7.6 else 0.0
    ch["head"].rotation_euler.x = look
    ch["head"].keyframe_insert("rotation_euler", frame=f)

# ============================== lights ==============================
bpy.ops.object.light_add(type="SUN", location=(18, -14, 26))
sun = bpy.context.object.data
sun.energy = 2.6
sun.angle = math.radians(6.5)
bpy.context.object.rotation_euler = Euler((math.radians(55), math.radians(12), math.radians(35)))
bpy.ops.object.light_add(type="AREA", location=(-6, 8, 4))
fill = bpy.context.object.data
fill.energy = 120
fill.size = 12
bpy.context.object.rotation_euler = Euler((math.radians(50), math.radians(-30), 0))

# ============================== camera: cinematic move ==============================
cam_data = bpy.data.cameras.new("Cam")
cam_data.lens = 32
cam = bpy.data.objects.new("Cam", cam_data)
scn.collection.objects.link(cam)
scn.camera = cam

def cam_at(frame, loc, target, lens=None):
    cam.location = loc
    d = Vector(target) - Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert("location", frame=frame)
    cam.keyframe_insert("rotation_euler", frame=frame)
    if lens:
        cam_data.lens = lens
        cam_data.keyframe_insert("lens", frame=frame)

# 0-3s aerial establish + descend; 3-6s track the walker; 6-8s stop + low hero close-up; 8-12s pull-back reveal
cam_at(0,              (16, -30, 26),  (0, 2.0, 2.0))
cam_at(int(3 * FPS),   (7, -6, 3.2),   (0, 5.8, 1.7))
cam_at(int(6 * FPS),   (2.2, 3.8, 1.9), (0, 8.0, 1.7), lens=42)
cam_at(int(8 * FPS),   (-1.4, 6.2, 1.1), (0, 8.2, 1.9), lens=50)
cam_at(total,          (-6, 16, 7),    (0, 11.0, 2.2), lens=34)

# ============================== render ==============================
scn.frame_start, scn.frame_end = FRAME_START, FRAME_END
timing = {"frame_times": [], "setup_done": time.time()}
print(f"SCENE READY: frames {FRAME_START}-{FRAME_END}, {WIDTH}x{HEIGHT}, samples {SAMPLES}")

for f in range(FRAME_START, FRAME_END + 1):
    scn.frame_set(f)
    out = os.path.join(OUTDIR, f"frame_{f:04d}.png")
    scn.render.filepath = out
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t0
    timing["frame_times"].append(round(dt, 2))
    print(f"frame {f}: {dt:.1f}s", flush=True)

with open(os.path.join(OUTDIR, "timing.json"), "w") as fh:
    json.dump(timing, fh, indent=1)
print("RENDER DONE ->", OUTDIR)

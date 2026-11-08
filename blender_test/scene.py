"""Genuine headless Blender/Cycles test scene, run via GitHub Actions
(NOT in the Arena sandbox -- bpy cannot import there, see town3d/ARCHITECTURE.md).

Builds: a tiny city block (3 buildings with inset windows + a road), one
simple original character (sphere head, box torso, cylinder limbs), sun +
area lights, Principled BSDF materials, and an animated camera doing a slow
push-in while the character's arms swing through a few keyframes. Renders
the frame range to PNG with Cycles/CPU, matching what Phase 5 asks for in
miniature, purely to prove the pipeline actually runs end to end on a real
GitHub Actions runner.

Invoked as:
  blender -b -noaudio -P blender_test/scene.py -- --out DIR --frames N
"""
import sys
import math
import os

import bpy

argv = sys.argv
argv = argv[argv.index("--") + 1:] if "--" in argv else []
out_dir = "blender_test/out"
n_frames = 24
i = 0
while i < len(argv):
    if argv[i] == "--out":
        out_dir = argv[i + 1]
        i += 2
    elif argv[i] == "--frames":
        n_frames = int(argv[i + 1])
        i += 2
    else:
        i += 1

os.makedirs(out_dir, exist_ok=True)


def make_material(name, color, roughness=0.6, emission=0.0):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = emission
        if emission > 0 and "Emission Color" in bsdf.inputs:
            bsdf.inputs["Emission Color"].default_value = (*color, 1.0)
    return mat


def add_box(name, loc, size, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    if mat:
        obj.data.materials.append(mat)
    return obj


def build_building(cx, cz, w, h, d, wall_mat, window_mat):
    base = add_box(f"bldg_{cx}_{cz}", (cx, cz, h / 2), (w / 2, d / 2, h / 2), wall_mat)
    rows = max(1, int(h // 1.2))
    cols = max(1, int(w // 1.0))
    for r in range(rows):
        for c in range(cols):
            wx = cx - w / 2 + (c + 0.5) * (w / cols)
            wy = h * 0.15 + r * (h / rows)
            win = add_box(f"win_{cx}_{cz}_{r}_{c}", (wx, cz - d / 2 - 0.02, wy),
                          (w / cols * 0.3, 0.02, h / rows * 0.3), window_mat)
    return base


def build_character(cx, cz):
    skin = make_material("skin", (0.92, 0.78, 0.65), roughness=0.5)
    shirt = make_material("shirt", (0.10, 0.55, 0.50), roughness=0.7)
    pants = make_material("pants", (0.15, 0.18, 0.28), roughness=0.7)
    hair = make_material("hair", (0.25, 0.16, 0.10), roughness=0.8)

    root = bpy.data.objects.new(f"character_root_{cx}_{cz}", None)
    bpy.context.collection.objects.link(root)
    root.location = (cx, cz, 0)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(cx, cz, 1.55))
    head = bpy.context.active_object
    head.name = "head"
    head.data.materials.append(skin)
    head.parent = root

    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.24, location=(cx, cz, 1.72))
    hair_obj = bpy.context.active_object
    hair_obj.name = "hair_cap"
    hair_obj.scale = (1.0, 1.0, 0.6)
    hair_obj.data.materials.append(hair)
    hair_obj.parent = root

    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cz, 1.05))
    torso = bpy.context.active_object
    torso.name = "torso"
    torso.scale = (0.26, 0.16, 0.42)
    torso.data.materials.append(shirt)
    torso.parent = root

    arms = []
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.07, depth=0.62,
                                             location=(cx + sign * 0.33, cz, 0.0))
        arm = bpy.context.active_object
        arm.name = f"arm_{side}"
        arm.data.materials.append(skin)
        arm.location = (cx + sign * 0.33, cz, 1.05)
        arm.rotation_mode = 'XYZ'
        arm_pivot = bpy.data.objects.new(f"arm_pivot_{side}", None)
        bpy.context.collection.objects.link(arm_pivot)
        arm_pivot.location = (cx + sign * 0.33, cz, 1.3)
        arm_pivot.parent = root
        arm.parent = arm_pivot
        arm.location = (0, 0, -0.31)
        arms.append(arm_pivot)

    legs = []
    for side, sign in [("L", -1), ("R", 1)]:
        bpy.ops.mesh.primitive_cylinder_add(radius=0.09, depth=0.66,
                                             location=(cx + sign * 0.11, cz, 0.33))
        leg = bpy.context.active_object
        leg.name = f"leg_{side}"
        leg.data.materials.append(pants)
        leg.parent = root
        legs.append(leg)

    return root, arms


def animate_arms(arm_pivots, n_frames):
    swing = math.radians(28)
    keys = [0, n_frames // 4, n_frames // 2, (3 * n_frames) // 4, n_frames - 1]
    phase_signs = [1, -1]
    for pivot, sign in zip(arm_pivots, phase_signs):
        for idx, f in enumerate(keys):
            angle = sign * swing * math.sin(idx * math.pi / 2)
            pivot.rotation_euler = (angle, 0, 0)
            pivot.keyframe_insert(data_path="rotation_euler", frame=f + 1)
        for fc in pivot.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = 'SINE'


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = n_frames

    ground_mat = make_material("road", (0.22, 0.22, 0.24), roughness=0.8)
    sidewalk_mat = make_material("sidewalk", (0.68, 0.66, 0.60), roughness=0.9)
    wall_mat_a = make_material("wall_a", (0.80, 0.55, 0.35), roughness=0.75)
    wall_mat_b = make_material("wall_b", (0.55, 0.60, 0.68), roughness=0.6)
    window_mat = make_material("window", (1.0, 0.85, 0.45), roughness=0.2, emission=2.5)

    add_box("ground", (0, 0, -0.1), (20, 20, 0.1), sidewalk_mat)
    add_box("road", (0, 0, -0.08), (2.2, 20, 0.02), ground_mat)

    build_building(-5, -6, 3.2, 6.0, 3.2, wall_mat_a, window_mat)
    build_building(5, -8, 3.6, 8.5, 3.0, wall_mat_b, window_mat)
    build_building(-6.5, -14, 2.8, 4.5, 2.8, wall_mat_a, window_mat)

    root, arm_pivots = build_character(0.6, 1.5)
    animate_arms(arm_pivots, n_frames)

    sun = bpy.data.lights.new("sun", type='SUN')
    sun.energy = 3.2
    sun_obj = bpy.data.objects.new("sun", sun)
    bpy.context.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(55), 0, math.radians(35))

    fill = bpy.data.lights.new("fill", type='AREA')
    fill.energy = 150
    fill.size = 4
    fill_obj = bpy.data.objects.new("fill", fill)
    bpy.context.collection.objects.link(fill_obj)
    fill_obj.location = (-3, 4, 4)

    world = bpy.data.worlds.new("World")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.55, 0.70, 0.85, 1.0)
    bg.inputs[1].default_value = 1.0
    scene.world = world

    cam_data = bpy.data.cameras.new("cam")
    cam_data.lens = 32
    cam_obj = bpy.data.objects.new("cam", cam_data)
    bpy.context.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    import mathutils
    eye0 = mathutils.Vector((6.0, 7.0, 3.2))
    eye1 = mathutils.Vector((2.4, 3.2, 2.0))
    target = mathutils.Vector((0.6, 1.5, 1.1))
    for idx, f in enumerate([1, n_frames]):
        t = idx
        eye = eye0.lerp(eye1, t)
        cam_obj.location = eye
        direction = target - eye
        cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        cam_obj.keyframe_insert(data_path="location", frame=f)
        cam_obj.keyframe_insert(data_path="rotation_euler", frame=f)
    for fc in cam_obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = 'SINE'

    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 480
    scene.render.resolution_y = 854
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.filepath = os.path.join(out_dir, "frame_")

    print(f"[blender_test] rendering {n_frames} frames to {out_dir} with Cycles/CPU")
    bpy.ops.render.render(animation=True)
    print("[blender_test] DONE")


main()

#!/usr/bin/env python3
"""bpy_render_test.py — REAL headless Cycles CPU render test (Phase 'Blender CPU Rendering Test').

Run with the sandbox stub libs:
  LD_LIBRARY_PATH=/tmp/stublibs python bpy_render_test.py

Creates an original stylized test scene (ground + 3 beveled towers + sun + sky),
renders with Cycles CPU, saves PNG + reports timing. Success = actual image file
with non-trivial content (verified by pixel stats, printed here).
"""
import time, os, sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "bpy_test")
os.makedirs(OUT, exist_ok=True)

import bpy

print("Blender:", bpy.app.version_string, "| background:", bpy.app.background)

# --- fresh scene ---
bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene

# --- materials helper ---
def mat(name, color, rough=0.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    return m

# --- ground ---
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.context.object.data.materials.append(mat("ground", (0.20, 0.32, 0.18), 0.9))

# --- three beveled towers (original test geometry) ---
import math, mathutils
cols = [(0.85, 0.35, 0.20), (0.95, 0.75, 0.30), (0.25, 0.45, 0.75)]
for i, c in enumerate(cols):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 2.4 - 2.4, 0, 1.4 + i * 0.9))
    ob = bpy.context.object
    ob.scale = (0.9, 0.9, 1.4 + i * 0.9)
    bpy.ops.object.modifier_add(type="BEVEL")
    ob.modifiers["Bevel"].width = 0.08
    ob.modifiers["Bevel"].segments = 3
    bpy.ops.object.shade_smooth()
    ob.data.materials.append(mat(f"tower{i}", c, 0.35))

# --- sun + sky ---
bpy.ops.object.light_add(type="SUN", location=(6, -4, 10))
sun = bpy.context.object.data
sun.energy = 2.0
sun.angle = math.radians(8)  # softer shadows
w = bpy.data.worlds.new("World")
w.use_nodes = True
bg = w.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.55, 0.72, 0.92, 1.0)   # stylized soft blue sky
bg.inputs["Strength"].default_value = 1.0
bpy.context.scene.world = w

# --- camera ---
cam_data = bpy.data.cameras.new("Cam")
cam = bpy.data.objects.new("Cam", cam_data)
scn.collection.objects.link(cam)
cam.location = (8.5, -8.5, 3.2)
target = mathutils.Vector((0, 0, 2.0))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
scn.camera = cam

# --- render settings: Cycles CPU ---
scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.render.resolution_x = 405
scn.render.resolution_y = 720
scn.render.resolution_percentage = 100
scn.cycles.samples = 32
scn.render.image_settings.file_format = "PNG"
scn.render.filepath = os.path.join(OUT, "cycles_cpu_test.png")

t0 = time.time()
bpy.ops.render.render(write_still=True)
dt = time.time() - t0
print(f"Cycles CPU render: {dt:.1f}s -> {scn.render.filepath}")

# --- verify the file is a real image ---
from PIL import Image
import numpy as np
im = np.asarray(Image.open(scn.render.filepath).convert("RGB"), dtype=np.float32)
print(f"VERIFY: size={im.shape[1]}x{im.shape[0]} mean={im.mean():.1f} std={im.std():.1f}")
assert im.std() > 15, "render looks blank — FAIL"
print("RENDER TEST PASS: real image with actual content variation")

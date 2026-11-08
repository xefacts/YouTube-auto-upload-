"""
Minimal from-scratch 3D software renderer (perspective projection, flat
shading, painter's-algorithm depth sort, backface culling) used to build the
"Skyline Town" short entirely from procedural geometry -- no AI-generated
images, no Blender dependency. Pure numpy + PIL rasterization.
"""
from __future__ import annotations
import math
import numpy as np
from PIL import Image, ImageDraw


def normalize(v):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


def look_at(eye, target, up=(0, 1, 0)):
    eye = np.asarray(eye, dtype=np.float64)
    target = np.asarray(target, dtype=np.float64)
    f = normalize(target - eye)           # forward
    s = normalize(np.cross(f, up))        # right
    u = np.cross(s, f)                    # true up
    view = np.eye(4)
    view[0, :3] = s
    view[1, :3] = u
    view[2, :3] = -f
    view[0, 3] = -np.dot(s, eye)
    view[1, 3] = -np.dot(u, eye)
    view[2, 3] = np.dot(f, eye)
    return view


def perspective(fov_y_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_y_deg) / 2.0)
    m = np.zeros((4, 4))
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def rot_y(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4)
    m[0, 0] = c
    m[0, 2] = s
    m[2, 0] = -s
    m[2, 2] = c
    return m


def rot_x(deg):
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    m = np.eye(4)
    m[1, 1] = c
    m[1, 2] = -s
    m[2, 1] = s
    m[2, 2] = c
    return m


def translate(pos):
    m = np.eye(4)
    m[0, 3], m[1, 3], m[2, 3] = pos
    return m


def scale(s):
    sx, sy, sz = s if isinstance(s, (tuple, list)) else (s, s, s)
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = sx, sy, sz
    return m


# Unit cube centered at origin, faces as (indices, local normal)
_CUBE_VERTS = np.array([
    [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
], dtype=np.float64)

_CUBE_FACES = [
    ([0, 1, 2, 3], (0, 0, -1)),   # back
    ([5, 4, 7, 6], (0, 0, 1)),    # front
    ([4, 0, 3, 7], (-1, 0, 0)),   # left
    ([1, 5, 6, 2], (1, 0, 0)),    # right
    ([3, 2, 6, 7], (0, 1, 0)),    # top
    ([4, 5, 1, 0], (0, -1, 0)),   # bottom
]


class Box:
    """Axis-aligned (then rotated) box primitive, the sole building block
    of every object in the scene -- matches the blocky/voxel art direction."""

    def __init__(self, center, half_extent, color, yaw=0.0, pitch=0.0,
                 shade_top=1.15, shade_side=1.0, shade_bottom=0.75):
        self.center = np.asarray(center, dtype=np.float64)
        he = half_extent if isinstance(half_extent, (tuple, list)) else (half_extent,) * 3
        self.half_extent = np.asarray(he, dtype=np.float64)
        self.color = np.asarray(color, dtype=np.float64)
        self.yaw = yaw
        self.pitch = pitch
        self.face_shade = {"top": shade_top, "side": shade_side, "bottom": shade_bottom}

    def model_matrix(self):
        return translate(self.center) @ rot_y(self.yaw) @ rot_x(self.pitch) @ scale(tuple(self.half_extent))

    def world_faces(self):
        """Returns list of (4 world-space verts (4x3), world normal (3,), base_color)."""
        M = self.model_matrix()
        R = M[:3, :3]
        verts_h = np.hstack([_CUBE_VERTS, np.ones((8, 1))])
        world_v = (M @ verts_h.T).T[:, :3]
        out = []
        for idx, n_local in _CUBE_FACES:
            w = world_v[idx]
            n_world = normalize(R @ np.array(n_local, dtype=np.float64))
            if n_local[1] > 0.5:
                tag = "top"
            elif n_local[1] < -0.5:
                tag = "bottom"
            else:
                tag = "side"
            out.append((w, n_world, self.color * self.face_shade[tag]))
        return out


class Scene:
    def __init__(self, sky_top, sky_bottom, light_dir=(0.45, 0.8, 0.35), ambient=0.55):
        self.boxes: list[Box] = []
        self.sky_top = np.asarray(sky_top, dtype=np.float64)
        self.sky_bottom = np.asarray(sky_bottom, dtype=np.float64)
        self.light_dir = normalize(light_dir)
        self.ambient = ambient

    def add(self, box: Box):
        self.boxes.append(box)
        return box

    def extend(self, boxes):
        self.boxes.extend(boxes)


class Camera:
    def __init__(self, eye, target, fov=50.0, up=(0, 1, 0)):
        self.eye = np.array(eye, dtype=np.float64)
        self.target = np.array(target, dtype=np.float64)
        self.fov = fov
        self.up = up


def _draw_sky(img: Image.Image, top, bottom):
    w, h = img.size
    top = np.array(top)
    bottom = np.array(bottom)
    grad = np.linspace(0, 1, h)[:, None]
    row = (top[None, :] * (1 - grad) + bottom[None, :] * grad).astype(np.uint8)
    arr = np.repeat(row[:, None, :], w, axis=1)
    img.paste(Image.fromarray(arr, "RGB"), (0, 0))


def render_frame(scene: Scene, camera: Camera, width: int, height: int, near=0.3, far=400.0,
                  fog_color=None, fog_start=18.0, fog_end=70.0) -> Image.Image:
    img = Image.new("RGB", (width, height))
    _draw_sky(img, scene.sky_top, scene.sky_bottom)
    draw = ImageDraw.Draw(img)

    view = look_at(camera.eye, camera.target, camera.up)
    proj = perspective(camera.fov, width / height, near, far)

    renderables = []  # (avg_cam_z, screen_pts, color)
    fog_color = fog_color if fog_color is not None else scene.sky_bottom

    for box in scene.boxes:
        for verts_w, normal_w, base_color in box.world_faces():
            verts_h = np.hstack([verts_w, np.ones((4, 1))])
            cam_v = (view @ verts_h.T).T
            cam_xyz = cam_v[:, :3]
            # Skip faces that are (partly) behind the near plane -- our
            # scenes keep geometry well in front of the camera so this is
            # a safety net, not a hard clip.
            if np.any(cam_xyz[:, 2] > -near):
                continue
            # Backface cull using the camera-space normal.
            center_cam = cam_xyz.mean(axis=0)
            to_cam = normalize(-center_cam)
            n_cam = normalize((view[:3, :3] @ normal_w))
            if np.dot(n_cam, to_cam) <= 0.0:
                continue
            clip = (proj @ cam_v.T).T
            w_coord = clip[:, 3]
            ndc = clip[:, :3] / w_coord[:, None]
            sx = (ndc[:, 0] * 0.5 + 0.5) * width
            sy = (1.0 - (ndc[:, 1] * 0.5 + 0.5)) * height
            pts = list(zip(sx.tolist(), sy.tolist()))

            diffuse = max(0.0, float(np.dot(normal_w, scene.light_dir)))
            shade = scene.ambient + (1.0 - scene.ambient) * diffuse
            color = np.clip(base_color * shade, 0, 255)

            depth = float(center_cam[2])  # negative, farther = more negative
            dist = -depth
            if dist > fog_start:
                t = min(1.0, (dist - fog_start) / (fog_end - fog_start))
                color = color * (1 - t) + np.array(fog_color) * t

            renderables.append((depth, pts, tuple(int(c) for c in color)))

    renderables.sort(key=lambda r: r[0])  # most negative (farthest) first
    for _, pts, color in renderables:
        draw.polygon(pts, fill=color)

    return img

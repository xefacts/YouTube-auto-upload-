"""
stylize3d - a tiny dependency-free software 3D renderer (numpy only).

Built for the Zack-D-Films-style vertical short pipeline in this folder:
  * smooth primitives (super-ellipsoids, spheres, cylinders, tori, planes)
  * perspective camera with depth of field
  * z-buffered deferred shading: 3-point studio lights, GGX specular,
    fake studio environment for metals, shadow map, SSAO
  * post: bloom, DOF, ACES tonemap, chromatic aberration, vignette, grain

No GPU, no Blender, no OpenGL needed - it runs anywhere numpy runs.
"""
from __future__ import annotations

import math

import numpy as np

# --------------------------------------------------------------------------- #
# math helpers
# --------------------------------------------------------------------------- #


def norm(v, axis=-1):
    return v / np.maximum(np.linalg.norm(v, axis=axis, keepdims=True), 1e-9)


def T(x=0.0, y=0.0, z=0.0):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def S(x=1.0, y=None, z=None):
    if y is None:
        y = z = x
    m = np.eye(4)
    m[0, 0], m[1, 1], m[2, 2] = x, y, z
    return m


def Rx(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[1, 1], m[1, 2], m[2, 1], m[2, 2] = c, -s, s, c
    return m


def Ry(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[0, 0], m[0, 2], m[2, 0], m[2, 2] = c, s, -s, c
    return m


def Rz(a):
    c, s = math.cos(a), math.sin(a)
    m = np.eye(4)
    m[0, 0], m[0, 1], m[1, 0], m[1, 1] = c, -s, s, c
    return m


def look_at(eye, target, up=(0.0, 1.0, 0.0), roll=0.0):
    eye = np.asarray(eye, float)
    target = np.asarray(target, float)
    up = np.asarray(up, float)
    f = norm(target - eye)
    r = norm(np.cross(f, up))
    u = np.cross(r, f)
    if roll:
        c, s = math.cos(roll), math.sin(roll)
        r, u = c * r + s * u, -s * r + c * u
    m = np.eye(4)
    m[0, :3], m[1, :3], m[2, :3] = r, u, -f
    m[0, 3], m[1, 3], m[2, 3] = -r @ eye, -u @ eye, f @ eye
    return m


def perspective(fov_y_deg, aspect, near=0.04, far=200.0):
    f = 1.0 / math.tan(math.radians(fov_y_deg) * 0.5)
    m = np.zeros((4, 4))
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = 2 * far * near / (near - far)
    m[3, 2] = -1.0
    return m


def ortho(size, aspect, near=-50.0, far=50.0):
    m = np.eye(4)
    m[0, 0] = 1.0 / (size * aspect)
    m[1, 1] = 1.0 / size
    m[2, 2] = -2.0 / (far - near)
    m[2, 3] = -(far + near) / (far - near)
    return m


def ease_in_out(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def ease_in(t):
    t = min(max(t, 0.0), 1.0)
    return t ** 3


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


# --------------------------------------------------------------------------- #
# meshes
# --------------------------------------------------------------------------- #


class Mesh:
    __slots__ = ("verts", "normals", "tris", "uvs")

    def __init__(self, verts, tris, normals=None, uvs=None):
        self.verts = np.asarray(verts, np.float32)
        self.tris = np.asarray(tris, np.int32)
        if normals is None:
            normals = _vertex_normals(self.verts, self.tris)
        self.normals = np.asarray(normals, np.float32)
        self.uvs = None if uvs is None else np.asarray(uvs, np.float32)


def _vertex_normals(verts, tris):
    fn = np.cross(verts[tris[:, 1]] - verts[tris[:, 0]], verts[tris[:, 2]] - verts[tris[:, 0]])
    vn = np.zeros_like(verts)
    for k in range(3):
        np.add.at(vn, tris[:, k], fn)
    return norm(vn)


def _grid_faces(nu, nv, wrap_u=True, wrap_v=False, flip=False):
    """faces for a (nu x nv) vertex grid, index = i*nv + j."""
    tris = []
    for i in range(nu if wrap_u else nu - 1):
        i2 = (i + 1) % nu
        for j in range(nv if wrap_v else nv - 1):
            j2 = (j + 1) % nv
            a, b, c, d = i * nv + j, i * nv + j2, i2 * nv + j2, i2 * nv + j
            if flip:
                tris += [(a, c, b), (a, d, c)]
            else:
                tris += [(a, b, c), (a, c, d)]
    return np.array(tris, np.int32)


def sphere(radius=1.0, seg_u=48, seg_v=24, scale=(1, 1, 1)):
    us = np.linspace(0, 2 * math.pi, seg_u, endpoint=False)
    vs = np.linspace(0, math.pi, seg_v)
    U, V = np.meshgrid(us, vs, indexing="ij")
    x = np.sin(V) * np.cos(U)
    y = np.cos(V)
    z = np.sin(V) * np.sin(U)
    verts = np.stack([x * scale[0], y * scale[1], z * scale[2]], -1).reshape(-1, 3) * radius
    nrm = np.stack([x, y, z], -1).reshape(-1, 3)
    faces = _grid_faces(seg_u, seg_v, wrap_u=True, wrap_v=False)
    uvs = np.stack([U.ravel() / (2 * math.pi), 1 - V.ravel() / math.pi], -1)
    return Mesh(verts, faces, nrm, uvs)


def superellipsoid(a=1.0, b=1.0, c=1.0, e1=0.25, e2=0.25, seg_u=64, seg_v=40):
    """Rounded box / 'clay' box. e1 = vertical squareness, e2 = horizontal."""
    def f(w, m):
        return np.sign(np.cos(w)) * np.abs(np.cos(w)) ** m

    def g(w, m):
        return np.sign(np.sin(w)) * np.abs(np.sin(w)) ** m

    us = np.linspace(-math.pi, math.pi, seg_u, endpoint=False)
    vs = np.linspace(-math.pi / 2, math.pi / 2, seg_v)
    U, V = np.meshgrid(us, vs, indexing="ij")
    x = a * f(V, e1) * f(U, e2)
    y = b * g(V, e1)
    z = c * f(V, e1) * g(U, e2)
    verts = np.stack([x, y, z], -1).reshape(-1, 3)
    faces = _grid_faces(seg_u, seg_v, wrap_u=True, wrap_v=False)
    uvs = np.stack([U.ravel() / (2 * math.pi) + 0.5, V.ravel() / math.pi + 0.5], -1)
    return Mesh(verts, faces, None, uvs)


def box(sx=1.0, sy=1.0, sz=1.0):
    v = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], np.float32)
    v *= np.array([sx / 2, sy / 2, sz / 2], np.float32)
    f = np.array([
        [0, 1, 3], [0, 3, 2],  # -x
        [4, 6, 7], [4, 7, 5],  # +x
        [0, 4, 5], [0, 5, 1],  # -y
        [2, 3, 7], [2, 7, 6],  # +y
        [0, 2, 6], [0, 6, 4],  # -z
        [1, 5, 7], [1, 7, 3],  # +z
    ], np.int32)
    nrm = np.zeros((8, 3), np.float32)
    for tri in f:
        n = np.cross(v[tri[1]] - v[tri[0]], v[tri[2]] - v[tri[0]])
        for k in tri:
            nrm[k] += n
    return Mesh(v, f, norm(nrm))


def cylinder(r=1.0, h=1.0, seg=48, r_top=None, caps=True):
    r_top = r if r_top is None else r_top
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    verts, normals, uvs = [], [], []
    for j, (rr, yy) in enumerate(((r, -h / 2), (r_top, h / 2))):
        for i, a in enumerate(ang):
            nx, nz = math.cos(a), math.sin(a)
            # slope the normal for tapered cylinders
            slope = (r - r_top) / max(h, 1e-6)
            nn = np.array([nx, slope, nz])
            nn = nn / np.linalg.norm(nn)
            verts.append((rr * nx, yy, rr * nz))
            normals.append(tuple(nn))
            uvs.append((i / seg, j))
    faces = _grid_faces(seg, 2, wrap_u=True, wrap_v=False, flip=True)
    if caps:
        for rr, yy, ny in ((r, -h / 2, -1.0), (r_top, h / 2, 1.0)):
            base = len(verts)
            verts.append((0.0, yy, 0.0))
            normals.append((0.0, ny, 0.0))
            uvs.append((0.5, 0.5))
            for i, a in enumerate(ang):
                verts.append((rr * math.cos(a), yy, rr * math.sin(a)))
                normals.append((0.0, ny, 0.0))
                uvs.append((0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)))
            for i in range(seg):
                i2 = (i + 1) % seg
                faces = np.vstack([faces, [[base, base + 1 + i2, base + 1 + i]]])
    return Mesh(verts, faces, normals, uvs)


def torus(R=1.0, r=0.2, seg_R=64, seg_r=20):
    us = np.linspace(0, 2 * math.pi, seg_R, endpoint=False)
    vs = np.linspace(0, 2 * math.pi, seg_r, endpoint=False)
    U, V = np.meshgrid(us, vs, indexing="ij")
    x = (R + r * np.cos(V)) * np.cos(U)
    z = (R + r * np.cos(V)) * np.sin(U)
    y = r * np.sin(V)
    verts = np.stack([x, y, z], -1).reshape(-1, 3)
    nx = np.cos(V) * np.cos(U)
    nz = np.cos(V) * np.sin(U)
    ny = np.sin(V)
    nrm = np.stack([nx, ny, nz], -1).reshape(-1, 3)
    faces = _grid_faces(seg_R, seg_r, wrap_u=True, wrap_v=True)
    uvs = np.stack([U.ravel() / (2 * math.pi), V.ravel() / (2 * math.pi)], -1)
    return Mesh(verts, faces, nrm, uvs)


def plane(size=20.0, subdiv=1, normal_y=True):
    n = subdiv + 1
    c = np.linspace(-size / 2, size / 2, n)
    X, Z = np.meshgrid(c, c, indexing="ij")
    verts = np.stack([X.ravel(), np.zeros(n * n), Z.ravel()], -1)
    faces = _grid_faces(n, n, wrap_u=False, wrap_v=False, flip=True)
    uvs = np.stack([X.ravel() / size + 0.5, Z.ravel() / size + 0.5], -1)
    return Mesh(verts, faces, np.tile(np.array([[0.0, 1.0, 0.0]]), (n * n, 1)), uvs)


def card(w=1.7, h=1.05, t=0.05, e2=0.20, e1=0.20):
    """Credit card: w along X, h along Y (up), thin along Z. Faces -Z."""
    return superellipsoid(w / 2, h / 2, t / 2, e1=e1, e2=e2, seg_u=96, seg_v=36)


def disc(r=1.0, seg=64):
    ang = np.linspace(0, 2 * math.pi, seg, endpoint=False)
    verts = [(0.0, 0.0, 0.0)] + [(r * math.cos(a), 0.0, r * math.sin(a)) for a in ang]
    faces = [[0, i + 2 if i + 2 <= seg else 1, i + 1] for i in range(seg)]
    uvs = [(0.5, 0.5)] + [(0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)) for a in ang]
    return Mesh(verts, faces, [(0, 1, 0)] * len(verts), uvs)


def quad(w=1.0, h=1.0):
    v = np.array([[-w / 2, -h / 2, 0], [w / 2, -h / 2, 0], [w / 2, h / 2, 0], [-w / 2, h / 2, 0]], np.float32)
    f = np.array([[0, 1, 2], [0, 2, 3]], np.int32)
    nr = np.tile(np.array([[0, 0, 1.0]], np.float32), (4, 1))
    uv = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], np.float32)
    return Mesh(v, f, nr, uv)


# --------------------------------------------------------------------------- #
# materials
# --------------------------------------------------------------------------- #

DEFAULT_MAT = dict(
    base=(0.8, 0.8, 0.8),
    rough=0.35,
    metal=0.0,
    emis=(0.0, 0.0, 0.0),
    emis_str=0.0,
    tex=None,          # (H,W,3) linear float array
    spec=1.0,
    clearcoat=0.0,
)


def mat(**kw):
    m = dict(DEFAULT_MAT)
    m.update(kw)
    return m


class Obj:
    """A drawable: mesh + material + world matrix."""

    __slots__ = ("mesh", "mat", "matrix", "name")

    def __init__(self, mesh, material, matrix=None, name=""):
        self.mesh = mesh
        self.mat = material
        self.matrix = np.eye(4) if matrix is None else matrix
        self.name = name


# --------------------------------------------------------------------------- #
# rendering core
# --------------------------------------------------------------------------- #


def _rasterize(sx, sy, zinv, tris, W, H):
    """Screen-space z-buffer rasteriser. sx,sy = pixel coords, zinv = 1/view_z."""
    zbuf = np.full((H, W), -np.inf, np.float32)
    tid = np.full((H, W), -1, np.int32)
    bu = np.zeros((H, W), np.float32)
    bv = np.zeros((H, W), np.float32)

    x0 = sx[tris[:, 0]]
    y0 = sy[tris[:, 0]]
    x1 = sx[tris[:, 1]]
    y1 = sy[tris[:, 1]]
    x2 = sx[tris[:, 2]]
    y2 = sy[tris[:, 2]]
    area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    keep = np.abs(area) > 1e-9
    if not keep.any():
        return zbuf, tid, bu, bv
    xmin = np.maximum(np.floor(np.minimum(np.minimum(x0, x1), x2)), 0).astype(np.int32)
    xmax = np.minimum(np.ceil(np.maximum(np.maximum(x0, x1), x2)), W - 1).astype(np.int32)
    ymin = np.maximum(np.floor(np.minimum(np.minimum(y0, y1), y2)), 0).astype(np.int32)
    ymax = np.minimum(np.ceil(np.maximum(np.maximum(y0, y1), y2)), H - 1).astype(np.int32)
    keep &= (xmax >= xmin) & (ymax >= ymin)
    inv_area = np.where(keep, 1.0 / np.where(keep, area, 1.0), 0.0)

    for ti in np.nonzero(keep)[0]:
        xa, xb = xmin[ti], xmax[ti]
        ya, yb = ymin[ti], ymax[ti]
        xs = np.arange(xa, xb + 1, dtype=np.float32) + 0.5
        ys = np.arange(ya, yb + 1, dtype=np.float32)[:, None] + 0.5
        px0, py0 = x0[ti], y0[ti]
        w1 = ((xs[None, :] - px0) * (y2[ti] - py0) - (ys - py0) * (x2[ti] - px0)) * inv_area[ti]
        w2 = ((x1[ti] - px0) * (ys - py0) - (y1[ti] - py0) * (xs[None, :] - px0)) * inv_area[ti]
        w0 = 1.0 - w1 - w2
        m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        if not m.any():
            continue
        t = tris[ti]
        z = w0 * zinv[t[0]] + w1 * zinv[t[1]] + w2 * zinv[t[2]]
        sub_z = zbuf[ya:yb + 1, xa:xb + 1]
        depth_ok = m & (z > sub_z)
        if not depth_ok.any():
            continue
        sub_z[depth_ok] = z[depth_ok]
        tid[ya:yb + 1, xa:xb + 1][depth_ok] = ti
        bu[ya:yb + 1, xa:xb + 1][depth_ok] = w1[depth_ok]
        bv[ya:yb + 1, xa:xb + 1][depth_ok] = w2[depth_ok]
    return zbuf, tid, bu, bv


# --- studio environment (cheap IBL substitute) ----------------------------- #


def environment(dirs, warm=1.0):
    """Fake studio: dark floor, cool horizon band, two soft boxes overhead."""
    y = dirs[..., 1]
    t = np.clip(y * 0.5 + 0.5, 0, 1)[..., None]
    floor = np.array([0.035, 0.042, 0.060])
    horiz = np.array([0.18, 0.21, 0.28]) * warm
    sky = np.array([0.26, 0.30, 0.40])
    col = floor * (1 - t) + horiz * (1 - abs(2 * t - 1)) + sky * t ** 2
    for d, c, p in (
        ((0.35, 0.82, 0.45), (2.6, 2.5, 2.35), 18),
        ((-0.75, 0.35, -0.55), (0.75, 1.15, 1.9), 32),
        ((0.05, 1.0, -0.15), (1.6, 1.5, 1.4), 90),
        ((0.0, 0.15, 1.0), (0.55, 0.60, 0.70), 60),
    ):
        dd = np.array(d, float) / np.linalg.norm(d)
        k = np.maximum(dirs @ dd, 0) ** p
        col = col + k[..., None] * np.array(c)
    return col


# --------------------------------------------------------------------------- #
# scene render
# --------------------------------------------------------------------------- #


def _blur(img, radius, axis=None):
    """cheap separable box blur x3 (approx gaussian)."""
    out = img
    if axis in (0, None):
        for _ in range(3):
            out = _box(out, radius, 0)
    if axis in (1, None):
        for _ in range(3):
            out = _box(out, radius, 1)
    return out


def _box(img, r, axis):
    if r < 1:
        return img
    pad = [(0, 0)] * img.ndim
    pad[axis] = (r + 1, r)
    p = np.pad(img, pad, mode="edge")
    c = np.cumsum(p, axis=axis, dtype=np.float32)
    sl_hi = [slice(None)] * img.ndim
    sl_lo = [slice(None)] * img.ndim
    sl_hi[axis] = slice(2 * r + 1, None)
    sl_lo[axis] = slice(0, -(2 * r + 1))
    return (c[tuple(sl_hi)] - c[tuple(sl_lo)]) / (2 * r + 1)


def _up(img, f, H, W):
    """nearest-neighbour upsample then crop/pad to (H, W)."""
    out = np.repeat(np.repeat(img, f, axis=0), f, axis=1)
    if out.shape[0] < H:
        out = np.pad(out, ((0, H - out.shape[0]), (0, 0)) + ((0, 0),) * (out.ndim - 2), mode="edge")
    if out.shape[1] < W:
        out = np.pad(out, ((0, 0), (0, W - out.shape[1])) + ((0, 0),) * (out.ndim - 2), mode="edge")
    return out[:H, :W]


def _down(img, f):
    H, W = img.shape[:2]
    H2, W2 = H // f, W // f
    return img[:H2 * f, :W2 * f].reshape(H2, f, W2, f, -1).mean(axis=(1, 3))


class Camera:
    def __init__(self, pos, target, up=(0, 1, 0), fov=34.0, roll=0.0,
                 focus=None, aperture=0.0, exposure=1.0):
        self.pos = np.asarray(pos, float)
        self.target = np.asarray(target, float)
        self.up = np.asarray(up, float)
        self.fov = fov
        self.roll = roll
        self.focus = focus
        self.aperture = aperture
        self.exposure = exposure


def render(objects, cam, W, H, lights=None, bg_top=(0.020, 0.026, 0.040),
           bg_bot=(0.005, 0.006, 0.010), shadow=True, ssao=True, bloom=0.55,
           dof=True, grain=0.012, vignette=0.55, ambient=0.26, ca=0.0012,
           shadow_size=1024, ss=1, shadow_bounds=14.0, glow_tint=None, exposure=None):
    """Render one frame. objects = list[Obj]; returns uint8 (H,W,3)."""
    Ri, Gi = W, H   # raster width / height
    if exposure is not None:
        cam.exposure *= exposure
    aspect = W / H
    view = look_at(cam.pos, cam.target, cam.up, cam.roll)
    proj = perspective(cam.fov, aspect, 0.02, 400.0)
    vp = proj @ view

    # ---- gather geometry -------------------------------------------------- #
    all_v, all_n, all_uv, all_tri, mat_idx, tri_offsets = [], [], [], [], [], []
    off = 0
    for oi, o in enumerate(objects):
        m = o.matrix
        nm = np.linalg.inv(m[:3, :3]).T
        vw = (o.mesh.verts @ m[:3, :3].T) + m[:3, 3]
        nw = norm(o.mesh.normals @ nm.T)
        all_v.append(vw)
        all_n.append(nw)
        all_uv.append(o.mesh.uvs if o.mesh.uvs is not None else np.zeros((len(vw), 2), np.float32))
        all_tri.append(o.mesh.tris + off)
        mat_idx.append(np.full(len(o.mesh.tris), oi, np.int32))
        off += len(vw)
    V = np.concatenate(all_v).astype(np.float32)
    N = np.concatenate(all_n).astype(np.float32)
    UV = np.concatenate(all_uv).astype(np.float32)
    TRIS = np.concatenate(all_tri)
    MIDX = np.concatenate(mat_idx)

    vv = (V @ view[:3, :3].T) + view[:3, 3]
    depth = -vv[:, 2]
    near, far = 0.03, 300.0

    # backface cull in clip space via winding (done in raster via area sign)
    clip = (np.hstack([V, np.ones((len(V), 1))]) @ vp.T)
    w = clip[:, 3]
    valid = (w > near)[TRIS].all(axis=1) & (depth[TRIS] > near).all(axis=1)
    tris = TRIS[valid]
    midx = MIDX[valid]
    if len(tris) == 0:
        return np.zeros((H, W, 3), np.uint8)

    invw = 1.0 / w
    sx = (clip[:, 0] * invw * 0.5 + 0.5) * Ri
    sy = (0.5 - clip[:, 1] * invw * 0.5) * Gi
    zinv = (1.0 / depth).astype(np.float32)

    # two-sided: flip winding for triangles facing away (thin cards / quads)
    zbuf, tid, bu, bv = _rasterize(sx, sy, zinv, tris, Ri, Gi)

    mask = tid >= 0
    if not mask.any():
        return np.zeros((H, W, 3), np.uint8)
    fx = np.nonzero(mask.reshape(-1))[0]
    tri = tris[tid.reshape(-1)[fx]]
    u = bu.reshape(-1)[fx].astype(np.float32)
    v = bv.reshape(-1)[fx].astype(np.float32)
    w0 = 1.0 - u - v
    i0, i1, i2 = tri[:, 0], tri[:, 1], tri[:, 2]
    z0, z1, z2 = zinv[i0], zinv[i1], zinv[i2]
    s = w0 * z0 + u * z1 + v * z2
    s = np.where(np.abs(s) < 1e-12, 1e-12, s)
    p0, p1, p2 = (w0 * z0) / s, (u * z1) / s, (v * z2) / s

    P = (p0[:, None] * V[i0] + p1[:, None] * V[i1] + p2[:, None] * V[i2])
    Nn = norm(p0[:, None] * N[i0] + p1[:, None] * N[i1] + p2[:, None] * N[i2])
    TEX = (p0[:, None] * UV[i0] + p1[:, None] * UV[i1] + p2[:, None] * UV[i2])
    mid = midx[tid.reshape(-1)[fx]]

    # ---- material lookup -------------------------------------------------- #
    bases = np.array([o.mat["base"] for o in objects], np.float32)
    roughs = np.array([o.mat["rough"] for o in objects])
    metals = np.array([o.mat["metal"] for o in objects])
    emiss = np.array([o.mat["emis"] for o in objects], np.float32)
    emiss_str = np.array([o.mat["emis_str"] for o in objects])
    clcoat = np.array([o.mat["clearcoat"] for o in objects])

    alb = bases[mid]
    # textures
    for oi, o in enumerate(objects):
        if o.mat.get("tex") is not None:
            sel = mid == oi
            if not sel.any():
                continue
            tex = o.mat["tex"]
            th, tw = tex.shape[:2]
            tx = np.clip((TEX[sel, 0] % 1.0) * (tw - 1), 0, tw - 1)
            ty = np.clip((TEX[sel, 1] % 1.0) * (th - 1), 0, th - 1)
            x0i = np.floor(tx).astype(np.int32)
            y0i = np.floor(ty).astype(np.int32)
            x1i = np.minimum(x0i + 1, tw - 1)
            y1i = np.minimum(y0i + 1, th - 1)
            fxi = (tx - x0i)[:, None]
            fyi = (ty - y0i)[:, None]
            c00 = tex[y0i, x0i]
            c10 = tex[y0i, x1i]
            c01 = tex[y1i, x0i]
            c11 = tex[y1i, x1i]
            samp = (c00 * (1 - fxi) * (1 - fyi) + c10 * fxi * (1 - fyi)
                    + c01 * (1 - fxi) * fyi + c11 * fxi * fyi)
            alb[sel] = samp * bases[oi]

    rough = roughs[mid]
    metal = metals[mid]
    em = emiss[mid] * emiss_str[mid][:, None]
    em_tex = np.zeros_like(em)
    has_em_tex = np.zeros(len(P), bool)
    for oi, o in enumerate(objects):
        if o.mat.get("tex") is not None and o.mat["emis_str"] > 0:
            sel = mid == oi
            if sel.any():
                em_tex[sel] = alb[sel] * emiss_str[mid[sel]][:, None]
                has_em_tex[sel] = True
    em = np.where(has_em_tex[:, None], em_tex, em)
    cc = clcoat[mid]

    # ---- lighting --------------------------------------------------------- #
    if lights is None:
        lights = [
            dict(pos=(3.0, 4.6, 3.4), color=(1.0, 0.97, 0.93), power=5.2, radius=5.0, shadow=True),
            dict(pos=(-4.0, 1.8, 2.4), color=(0.35, 0.62, 1.0), power=2.4, radius=6.0, shadow=False),
            dict(pos=(0.8, 2.2, -4.6), color=(1.0, 0.45, 0.20), power=2.8, radius=6.0, shadow=False),
        ]
    Vd = norm(cam.pos - P)
    acc = np.zeros_like(P)

    # shadow map from the key light (directional-ish)
    shadow_txt = None
    key = lights[0]
    if shadow:
        lp = np.array(key["pos"], float)
        lview = look_at(lp, np.zeros(3), (0, 1, 0))
        lproj = ortho(shadow_bounds, 1.0, -120, 120)
        lvp = lproj @ lview
        lclip = np.hstack([V, np.ones((len(V), 1))]) @ lvp.T
        lz = lclip[:, 2]                     # grows with distance from the light
        lsx = (lclip[:, 0] * 0.5 + 0.5) * shadow_size
        lsy = (0.5 - lclip[:, 1] * 0.5) * shadow_size
        sz, _, _, _ = _rasterize(lsx, lsy, (-lz).astype(np.float32), tris, shadow_size, shadow_size)
        sz = np.where(np.isfinite(sz), sz, 1e9)
        shadow_txt = (lvp, sz)

    for li, L in enumerate(lights):
        lpos = np.array(L["pos"], float)
        lcol = np.array(L["color"], float) * L["power"]
        lv = lpos - P
        dist2 = np.maximum((lv ** 2).sum(1), 1e-4)
        Ld = lv / np.sqrt(dist2)[:, None]
        atten = 1.0 / (1.0 + dist2 / (L["radius"] ** 2))
        ndl = np.clip((Nn * Ld).sum(1), 0, 1)

        sh = np.ones(len(P))
        if shadow and L.get("shadow") and shadow_txt is not None:
            lvp, sz = shadow_txt
            lclip = np.hstack([P, np.ones((len(P), 1))]) @ lvp.T
            lzf = lclip[:, 2]
            lsx = ((lclip[:, 0] * 0.5 + 0.5) * shadow_size).astype(np.int32)
            lsy = ((0.5 - lclip[:, 1] * 0.5) * shadow_size).astype(np.int32)
            bias = 0.18
            acc_sh = np.zeros(len(P))
            inside = (lsx >= 0) & (lsx < shadow_size) & (lsy >= 0) & (lsy < shadow_size)
            xx0 = np.clip(lsx, 0, shadow_size - 1)
            yy0 = np.clip(lsy, 0, shadow_size - 1)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    xx = np.clip(xx0 + dx, 0, shadow_size - 1)
                    yy = np.clip(yy0 + dy, 0, shadow_size - 1)
                    sm = sz[yy, xx]
                    acc_sh += (lzf <= sm + bias)
            sh = np.clip(acc_sh / 9.0, 0.0, 1.0)
            sh = 0.22 + 0.78 * sh
            sh = np.where(inside, sh, 1.0)

        ndv = np.clip((Nn * Vd).sum(1), 1e-3, 1.0)
        ndh = np.clip((Nn * norm(Ld + Vd)).sum(1), 0, 1)
        a = np.maximum(rough, 0.045)
        a2 = a * a
        d = a2 / (math.pi * ((ndh ** 2 * (a2 - 1.0) + 1.0) ** 2) + 1e-7)
        k = (rough + 1.0) ** 2 / 8.0
        g = (ndl / (ndl * (1 - k) + k + 1e-6)) * (ndv / (ndv * (1 - k) + k + 1e-6))
        F0 = 0.04 * (1 - metal)[:, None] + alb * metal[:, None]
        fres = F0
        fr = fres + (1 - fres) * ((1 - np.clip((norm(Ld + Vd) * Vd).sum(1), 0, 1)) ** 5)[:, None]
        spec = (d * g)[:, None] * fr / (4.0 * ndl[:, None] * ndv[:, None] + 1e-4)
        diff = alb * (1 - metal[:, None]) / math.pi
        acc += (diff * ndl[:, None] * (1 - cc[:, None] * 0.5) + spec * ndl[:, None]) * lcol * atten[:, None] * sh[:, None]
        # rim / fresnel boost for the stylised look
        rim = (1 - ndv) ** 3.0
        acc += rim[:, None] * lcol * atten[:, None] * 0.05 * sh[:, None]

    if key:
        pass

    # env / ambient
    R = Vd - 2.0 * (Vd * (-Nn)).sum(1)[:, None] * (-Nn)
    R = norm(Vd - 2.0 * (Vd * Nn).sum(1)[:, None] * Nn)
    env = environment(R)
    spec_env = env * (0.04 * (1 - metal)[:, None] + alb * metal[:, None]) * (1.2 - rough)[:, None]
    amb_col = np.array([0.35, 0.45, 0.62]) * ambient
    hemi = (Nn[:, 1:2] * 0.5 + 0.5)
    acc += alb * amb_col * (0.25 + 0.75 * hemi) * (0.25 + 0.75 * (1 - metal)[:, None])
    acc += spec_env * 0.50
    acc += em

    # ---- pack full-res buffers ------------------------------------------- #
    def scatter(ch):
        buf = np.zeros((H * W,) + ch.shape[1:], ch.dtype)
        buf[fx] = ch
        return buf.reshape((H, W) + ch.shape[1:])

    color = scatter(acc.astype(np.float32))
    depth_full = 1.0 / np.maximum(zbuf, 1e-6)
    nrm_full = scatter(Nn.astype(np.float32))
    pos_full = scatter(P.astype(np.float32))
    emis_full = scatter(em.astype(np.float32))

    # background gradient
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    bg = np.array(bg_top, np.float32) * (1 - yy) + np.array(bg_bot, np.float32) * yy
    skymask = (~mask)[..., None]
    color = np.where(skymask, bg * np.ones((1, W, 1), np.float32), color)
    # fake back-glow behind subject
    yy2 = (np.arange(H)[:, None] / H - 0.45) * 2
    xx2 = (np.arange(W)[None, :] / W - 0.5) * 2
    glow = np.exp(-(xx2 ** 2 * 1.4 + yy2 ** 2 * 1.0) * 2.2)[..., None]
    color = np.where(skymask, color + glow * np.array([0.055, 0.075, 0.115], np.float32), color)

    # ---- SSAO ------------------------------------------------------------- #
    if ssao:
        small = _down(np.concatenate([depth_full[..., None],
                                      nrm_full, pos_full], -1), 4)
        dsmall = small[..., 0]
        nsmall = small[..., 1:4]
        ps = small[..., 4:7]
        h2, w2 = dsmall.shape
        occ = np.zeros((h2, w2), np.float32)
        rng = np.random.default_rng(7)
        up = np.array([0, 1, 0], np.float32)
        alt = np.cross(nsmall, np.array([1, 0, 0], np.float32))
        alt = np.where(np.linalg.norm(alt, axis=-1, keepdims=True) < 1e-3,
                       np.cross(nsmall, up), alt)
        alt = norm(alt)
        bit = norm(np.cross(nsmall, alt))
        nvalid = np.linalg.norm(nsmall, axis=-1) > 1e-5
        radius = 9
        for s in range(8):
            ang = 2 * math.pi * s / 8 + 0.7
            rr = (1 + (s % 3) * 2)
            dx = int(round(math.cos(ang) * rr))
            dy = int(round(math.sin(ang) * rr))
            # sample in screen space, in world units of the neighbourhood
            px = np.roll(np.roll(ps, dy, axis=0), dx, axis=1)
            pdz = np.roll(np.roll(dsmall, dy, axis=0), dx, axis=1)
            dv = px - ps
            dist = np.linalg.norm(dv, axis=-1)
            dirv = dv / np.maximum(dist, 1e-6)[..., None]
            ndl = np.clip((nsmall * dirv).sum(-1), 0, 1)
            range_ok = (dist < 1.6) & (pdz > 1e-4) & (dsmall > 1e-4)
            occ += np.where(range_ok & (pdz < dsmall * 0.999), ndl * (1.0 - dist / 1.6), 0.0)
        occ = np.clip(occ / 8.0 * 1.5, 0, 1)
        occ = _blur(occ, 3)
        occ = _up(occ, 4, H, W)
        valid = (depth_full > 1e-4).astype(np.float32)
        ao = (1.0 - 0.45 * occ)[..., None]
        color = color * np.where(skymask, 1.0, ao)

    # ---- bloom ------------------------------------------------------------ #
    if bloom > 0:
        bright = np.clip(emis_full * 0.9 + color * 0.05, 0, None)
        lum = bright.mean(-1, keepdims=True)
        bright = bright * smoothstep(0.35, 1.6, lum)
        if bright.max() > 0:
            q = _down(bright, 4)
            q = _blur(q, max(1, int(min(q.shape[:2]) / 60)))
            q2 = _blur(_down(bright, 8), max(1, int(min(q.shape[:2]) / 30)))
            b = _up(q, 4, H, W)
            b2 = _up(q2, 8, H, W)
            color = color + bloom * (b * 0.7 + b2 * 0.5)

    # ---- depth of field --------------------------------------------------- #
    if dof and cam.aperture > 0 and cam.focus:
        coc = np.clip(cam.aperture * np.abs(1.0 / np.maximum(depth_full, 0.05) - 1.0 / cam.focus) * 3.2, 0, 1)
        if np.isfinite(coc).all() and coc.max() > 0.02:
            small = _down(color, 2)
            blur = _blur(small, 5)
            blur = blur + _blur(small, 11) * 0.7
            blur = _up(blur, 2, H, W)
            k = np.clip(coc * 1.4, 0, 1)[..., None]
            color = color * (1 - k) + blur * k

    # ---- grade ------------------------------------------------------------ #
    color = color * cam.exposure
    # ACES filmic tonemap
    x = color
    color = (x * (2.51 * x + 0.03)) / (x * (2.43 * x + 0.59) + 0.14)
    color = np.clip(color, 0, 1) ** (1 / 2.2)

    # subtle warm/cool split tone
    lum = color.mean(-1, keepdims=True)
    color = color + (1 - lum) * np.array([-0.006, 0.0, 0.012]) + lum * np.array([0.012, 0.004, -0.008])
    color = np.clip(color, 0, 1)
    color = (color - 0.5) * 1.06 + 0.5
    # saturation
    lum = color.mean(-1, keepdims=True)
    color = np.clip(lum + (color - lum) * 1.08, 0, 1)

    # chromatic aberration
    if ca > 0:
        d = int(max(1, round(ca * W)))
        color[..., 0] = np.roll(color[..., 0], d, axis=1)
        color[..., 2] = np.roll(color[..., 2], -d, axis=1)

    # vignette
    if vignette > 0:
        yy = np.linspace(-1, 1, H, dtype=np.float32)[:, None]
        xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :]
        r2 = (xx ** 2 * 0.75 + yy ** 2)
        color = color * (1 - vignette * 0.35 * np.clip(r2, 0, 1.4))[..., None]

    # grain
    if grain > 0:
        rng = np.random.default_rng(1234)
        color = color + rng.normal(0, grain, color.shape[:2])[..., None]

    return (np.clip(color, 0, 1) * 255).astype(np.uint8)


def _rounded_rect_pts(w, h, r, n_corner=10):
    """CCW outline (x, y) of a w x h rounded rectangle, corner radius r."""
    r = max(min(r, w / 2 - 1e-4, h / 2 - 1e-4), 1e-4)
    cx, cy = w / 2 - r, h / 2 - r
    pts = []
    for cx0, cy0, a0 in ((cx, cy, 0.0), (-cx, cy, math.pi / 2),
                         (-cx, -cy, math.pi), (cx, -cy, 3 * math.pi / 2)):
        for k in range(n_corner + 1):
            a = a0 + (math.pi / 2) * k / n_corner
            pts.append((cx0 + r * math.cos(a), cy0 + r * math.sin(a)))
    out = []
    for p in pts:
        if not out or (abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1])) > 1e-6:
            out.append(p)
    if (abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1])) < 1e-6:
        out.pop()
    return np.array(out, np.float64)


def plate(w=1.8, h=1.1, t=0.05, r=0.14, bevel=0.012, n_corner=10, faces="both"):
    """Rounded plate (card / screen / panel) with clean front-face UVs.

    faces: "both" (single mesh), "front" or "back" (half-plate, so the two
    sides can carry different materials).
    """
    outline = _rounded_rect_pts(w, h, r, n_corner)
    inner = _rounded_rect_pts(w - 2 * bevel, h - 2 * bevel, max(r - bevel, 1e-3), n_corner)
    n = len(outline)

    if faces == "both":
        zs = [t / 2, t / 2 - bevel * 0.7, -t / 2 + bevel * 0.7, -t / 2]
        rings = [inner, outline, outline, inner]
    elif faces == "front":
        zs = [t / 2, t / 2 - bevel * 0.7, 0.0]
        rings = [inner, outline, outline]
    else:
        zs = [0.0, -t / 2 + bevel * 0.7, -t / 2]
        rings = [outline, outline, inner]

    verts, uvs = [], []
    for ring, z in zip(rings, zs):
        for (x, y) in ring:
            verts.append((x, y, z))
            uvs.append((x / (w - 2 * bevel) + 0.5, 0.5 - y / (h - 2 * bevel)))
    tris = []
    nring = len(rings)
    for k in range(nring - 1):
        a, b = k * n, (k + 1) * n
        for i in range(n):
            j = (i + 1) % n
            tris += [(a + i, b + i, b + j), (a + i, b + j, a + j)]
    if faces in ("both", "front"):
        c = len(verts)
        verts.append((0.0, 0.0, zs[0]))
        uvs.append((0.5, 0.5))
        for i in range(n):
            j = (i + 1) % n
            tris.append((c, i, j))
    if faces in ("both", "back"):
        c = len(verts)
        verts.append((0.0, 0.0, zs[-1]))
        uvs.append((0.5, 0.5))
        base = (nring - 1) * n
        for i in range(n):
            j = (i + 1) % n
            tris.append((c, base + j, base + i))
    return Mesh(np.array(verts, np.float64), np.array(tris), None, np.array(uvs))

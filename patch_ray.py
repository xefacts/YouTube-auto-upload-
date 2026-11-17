import io, re, sys

P = "projects/roblox-town/render_town.py"
s = open(P).read()

s = s.replace('SCALE = float(os.environ.get("SCALE", "3.0"))   # supersample (design -> canvas)',
              'SCALE = float(os.environ.get("SCALE", "2.0"))   # design -> render canvas\nSS = int(os.environ.get("SS", "1"))             # ray samples per pixel')
if 'SS = int(os.environ.get("SS"' not in s:
    s = s.replace('SCALE = float(os.environ.get("SCALE", "2.4"))   # supersample (design -> canvas)',
                  'SCALE = float(os.environ.get("SCALE", "2.0"))   # design -> render canvas\nSS = int(os.environ.get("SS", "1"))             # ray samples per pixel')
s = s.replace("from boxes import Cam, Scene3D\nfrom draw2d import Pen",
              "import ray\nfrom boxes import Cam")

ground = '''def _grid(x, z, step, width=0.06):
    return (np.abs((x % step) - step / 2) < width) | (np.abs((z % step) - step / 2) < width)


def make_ground(name, mood_key):
    night = mood_key == "night"

    def fn(x, z):
        x = x.astype(np.float32)
        z = z.astype(np.float32)
        if name == "street":
            road = (z > 1.0) & (z < 7.9)
            kerb = ((z > 0.86) & (z <= 1.0)) | ((z >= 7.9) & (z < 8.06))
            walk = (z >= 8.06) & (z < 10.2)
            r = np.full(x.shape, 116.0, np.float32)
            g = np.full(x.shape, 166.0, np.float32)
            b = np.full(x.shape, 108.0, np.float32)
            for arr, val in ((r, 208), (g, 205), (b, 198)):
                arr[walk] = val
            for arr, val in ((r, 202), (g, 198), (b, 190)):
                arr[kerb] = val
            for arr, val in ((r, 92), (g, 96), (b, 106)):
                arr[road] = val
            dash = road & (np.abs(z - 4.45) < 0.11) & ((x % 2.6) < 1.3)
            cross = road & (x > 7.4) & (x < 10.9) & ((x % 0.78) < 0.36)
            for arr in (r, g, b):
                arr[dash] = 236
                arr[cross] = 240
            joint = walk & _grid(x, z, 2.0, 0.05)
            r[joint] = 190; g[joint] = 187; b[joint] = 180
        elif name == "classroom":
            r = np.full(x.shape, 206.0, np.float32)
            g = np.full(x.shape, 176.0, np.float32)
            b = np.full(x.shape, 138.0, np.float32)
            plank = np.abs((x % 1.6) - 0.8) < 0.05
            r[plank] = 186; g[plank] = 158; b[plank] = 122
        elif name == "clinic":
            r = np.full(x.shape, 200.0, np.float32)
            g = np.full(x.shape, 216.0, np.float32)
            b = np.full(x.shape, 212.0, np.float32)
            joint = _grid(x, z, 1.5, 0.05)
            r[joint] = 176; g[joint] = 194; b[joint] = 190
        elif name == "field":
            stripe = (np.floor(x / 2.8) % 2) == 0
            r = np.where(stripe, 94.0, 86.0).astype(np.float32)
            g = np.where(stripe, 164.0, 156.0).astype(np.float32)
            b = np.where(stripe, 96.0, 88.0).astype(np.float32)
        else:
            r = np.full(x.shape, 206.0, np.float32)
            g = np.full(x.shape, 198.0, np.float32)
            b = np.full(x.shape, 182.0, np.float32)
            joint = _grid(x, z, 2.0, 0.05)
            r[joint] = 186; g[joint] = 178; b[joint] = 164
        out = np.stack([r, g, b], -1)
        if night:
            out = out * 0.55
        return out

    return fn


def smoothstep(a, b, x):'''
s = s.replace("def smoothstep(a, b, x):", ground, 1)

start = s.index('    mood = MOODS[sh["mood"]]')
end = s.index('    draw_captions(canvas, sh["cap"]')
new = '''    mood = MOODS[sh["mood"]]
    canvas = Image.new("RGB", (BW, BH))
    sky(canvas, sh["mood"], t)
    coll = ray.Collector()
    S.SETS[sh["set"]](coll)
    S.STAGES[sh["stage"]](coll, u, lt)
    cam_px = Cam(cam.x, cam.y, cam.z, cam.yaw, cam.pitch, cam.fov, w=BW, h=BH)
    arr = ray.render(np.asarray(canvas), cam_px, coll, make_ground(sh["set"], sh["mood"]),
                     amb=mood["amb"], haze=mood["bot"], ss=SS)
    canvas = Image.fromarray(arr).convert("RGBA")
'''
s = s[:start] + new + s[end:]
s = s.replace('    img = canvas.convert("RGB").resize((OUT_W, OUT_H), Image.BILINEAR)',
              '    img = canvas.convert("RGB")')
open(P, "w").write(s)
print("patched")

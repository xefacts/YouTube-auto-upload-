import ctypes, os, json, subprocess, wave, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, features
import espeakng_loader as el

ROOT = "/home/user/YouTube-auto-upload-"
W = f"{ROOT}/projects/roblox-town/livestream_vod/zero_budget_gta6/work"
FF = open("/tmp/ffpath").read().strip()
SRC = f"{W}/full_source.mp4"
FONT = f"{W}/fonts/NotoSans-Bold.ttf"
CAPS_EN = json.load(open(f"{W}/captions_en.json"))
beats = json.load(open(f"{W}/story_hi.json"))
BEAT_LEN = 30.0

# ---- espeak-ng (offline) Hindi TTS ----
lib = ctypes.CDLL(el.get_library_path())
assert lib.espeak_Initialize(1, 0, os.path.dirname(el.get_data_path()).encode(), 0) > 0
RATE = 22050
assert lib.espeak_SetVoiceByName(b"hi") == 0
buf = []
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
def _cb(wav, n, ev):
    if wav and n > 0: buf.append(ctypes.string_at(wav, n * 2))
    return 0
_cbf = CB(_cb)
lib.espeak_SetSynthCallback(_cbf)
lib.espeak_Synth.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]

def tts(text, path):
    buf.clear()
    b = text.encode("utf-8")
    lib.espeak_Synth(b, len(b) + 1, 0, 0, 0, 1, None, None)
    lib.espeak_Synchronize()
    pcm = np.frombuffer(b"".join(buf), dtype=np.int16).astype(np.float32)
    pk = np.max(np.abs(pcm)) or 1.0
    pcm = (pcm / pk * 0.85 * 32767).astype(np.int16)  # peak-normalize narration
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(RATE); w.writeframes(pcm.tobytes())
    return len(pcm) / RATE

# ---- caption renderer ----
font = ImageFont.truetype(FONT, 110, layout_engine=ImageFont.Layout.RAQM if features.check("raqm") else ImageFont.Layout.BASIC)
def caption_png(word, path):
    probe = ImageDraw.Draw(Image.new("RGBA", (10, 10)))
    bb = probe.textbbox((0, 0), word, font=font, stroke_width=8)
    w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((20 - bb[0], 20 - bb[1]), word, font=font, fill=(255, 221, 0, 255),
                             stroke_width=8, stroke_fill=(0, 0, 0, 255))
    img.save(path)
    return w, h

def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900)
    if r.returncode != 0:
        print(r.stderr[-1500:]); raise SystemExit(f"ffmpeg failed: {cmd[:6]}")

parts = []
only = [int(x) for x in sys.argv[1:]] or list(range(len(beats)))
for i, (start, text) in enumerate(beats):
    cap_text = CAPS_EN[i]
    if i not in only: continue
    nwav = f"{W}/narr/n_{i:02d}.wav"
    D = tts(text, nwav)
    L = BEAT_LEN
    assert D + 0.9 <= L, f"beat {i} narration too long ({D:.1f}s)"
    words = cap_text.split()
    chars = [len(x) for x in words]; tot = sum(chars)
    cum = 0; caps = []
    for k, wd in enumerate(words):
        a = 0.4 + (D - 0.2) * cum / tot
        cum += chars[k]
        b = 0.4 + (D - 0.2) * cum / tot
        png = f"{W}/caps/b{i:02d}_w{k:02d}.png"
        caption_png(wd, png)
        caps.append((png, a, b))
    out = f"{W}/beats/beat_{i:02d}.mp4"
    if os.path.exists(out) and os.path.getsize(out) > 100000 and os.path.exists(f"{W}/beats/done_{i:02d}"):
        parts.append(out); print(f"beat {i:02d} skip (done)", flush=True); continue
    cmd = [FF, "-nostdin", "-y", "-ss", str(start), "-t", str(L), "-i", SRC, "-i", nwav]
    for png, a, b in caps:
        cmd += ["-loop", "1", "-i", png]
    fc = ["[0:v]fps=30,scale=1920:1080,format=yuv420p[v0]",
          "[0:a]volume=0.10[sa]",
          "[1:a]adelay=400|400,apad,atrim=0:%s[na]" % L,
          "[sa][na]amix=inputs=2:duration=first:normalize=0[aout]"]
    prev = "v0"
    for k, (png, a, b) in enumerate(caps):
        n = f"v{k+1}"
        fc.append(f"[{prev}][{k+2}:v]overlay=x=(W-w)/2:y=H-h-150:enable='between(t,{a:.2f},{b:.2f})'[{n}]")
        prev = n
    cmd += ["-filter_complex", ";".join(fc), "-map", f"[{prev}]", "-map", "[aout]",
            "-t", str(L), "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-r", "30", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", out]
    run(cmd)
    open(f"{W}/beats/done_{i:02d}","w").close()
    print(f"beat {i:02d} ok narr={D:.1f}s words={len(words)}", flush=True)
    parts.append(out)

if len(only) == len(beats):
    lst = f"{W}/beats/list.txt"
    with open(lst, "w") as f:
        for p in parts: f.write(f"file '{p}'\n")
    final = f"{ROOT}/out/gta6_story_hindi_1080p.mp4"
    os.makedirs(os.path.dirname(final), exist_ok=True)
    run([FF, "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final])
    print("FINAL", final, os.path.getsize(final))

#!/usr/bin/env python3
"""Dummy narration for the Gardner short, spoken by espeak-ng (bundled via pypi).
Writes vo/lineNN.wav + work/vo_durations.json."""
import ctypes as C, json, os, wave, time
import espeakng_loader

e = C.CDLL(espeakng_loader.get_library_path())
DATA = espeakng_loader.get_data_path()
AUDIO_OUTPUT_RETRIEVAL = 1
espeakCHARS_UTF8 = 1
POS_CHARACTER = 1
e.espeak_Initialize.restype = C.c_int
e.espeak_Initialize.argtypes = [C.c_int, C.c_int, C.c_char_p, C.c_int]
e.espeak_SetVoiceByName.restype = C.c_int
e.espeak_SetVoiceByName.argtypes = [C.c_char_p]
e.espeak_SetParameter.argtypes = [C.c_int, C.c_int, C.c_int]
e.espeak_Synth.argtypes = [C.c_void_p, C.c_size_t, C.c_uint, C.c_int, C.c_uint, C.c_uint, C.c_void_p, C.c_void_p]
e.espeak_Synchronize.argtypes = []
e.espeak_IsPlaying.restype = C.c_int
RATE, VOLUME, PITCH = 1, 2, 3
CB = C.CFUNCTYPE(C.c_int, C.POINTER(C.c_short), C.c_int, C.c_void_p)
buf = bytearray()


def _cb(wav, n, events):
    global buf
    if n > 0 and wav:
        buf += bytes(bytearray(C.string_at(wav, n * 2)))
    return 0


cb = CB(_cb)
if e.espeak_Initialize(AUDIO_OUTPUT_RETRIEVAL, 330, DATA.encode(), 0) < 0:
    raise SystemExit("espeak init failed")
e.espeak_SetSynthCallback(cb)
for v in ("en-gb-x-rp+m3", "en-gb+m3", "en-gb", "en"):
    if e.espeak_SetVoiceByName(v.encode()) == 0:
        print("voice", v); break
e.espeak_SetParameter(RATE, 152, 0)
e.espeak_SetParameter(VOLUME, 128, 0)
e.espeak_SetParameter(PITCH, 38, 0)

LINES = [
    (1,  "Boston. One twenty-four in the morning."),
    (2,  "Two police officers ring the side door."),
    (3,  "The night guard opens it. Nobody asks which one is real."),
    (4,  "Both guards end up face down in the basement, wrapped in tape."),
    (5,  "Upstairs, in the Dutch Room, they go straight to the right wall."),
    (6,  "A Vermeer. And a Rembrandt seascape — the only one he painted."),
    (7,  "No time to unscrew a frame. They cut the canvas and leave the gold."),
    (8,  "Eighty-one minutes. Thirteen works."),
    (9,  "Five hundred million dollars. Gone."),
    (10, "No arrests. Nothing recovered. Ten million dollars is still on offer."),
    (11, "The museum hangs the empty frames anyway."),
    (12, "Paintings that never came home."),
]

os.makedirs("vo", exist_ok=True); os.makedirs("work", exist_ok=True)
durs = {}
for n, text in LINES:
    buf = bytearray()
    b = text.encode()
    e.espeak_Synth(b, len(b), 0, POS_CHARACTER, 0, espeakCHARS_UTF8, None, None)
    e.espeak_Synchronize()
    while e.espeak_IsPlaying():
        time.sleep(0.02)
    data = bytes(buf)
    with wave.open(f"vo/line{n:02d}.wav", "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050); w.writeframes(data)
    d = len(data) / 2 / 22050
    durs[f"line{n:02d}"] = round(d, 3)
    print(f"line{n:02d}  {d:5.2f}s  {text}")
json.dump(durs, open("work/vo_durations.json", "w"), indent=1)
print("total", round(sum(durs.values()), 2), "s")

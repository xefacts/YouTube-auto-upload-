#!/usr/bin/env python3
"""Dummy narration for the Flannan short, spoken by espeak-ng (bundled via pypi).
Writes vo/lineNN.wav + work/vo_durations.json.  Swap in real takes later and
re-run timeline.py — the whole cut re-times off these durations."""
import ctypes as C, json, os, wave, time
import espeakng_loader

LIB = espeakng_loader.get_library_path()
DATA = espeakng_loader.get_data_path()
e = C.CDLL(LIB)

AUDIO_OUTPUT_RETRIEVAL = 1
espeakCHARS_UTF8 = 1
espeakINITIALIZE_DONT_EXIT = 0x8000
POS_CHARACTER = 1

e.espeak_Initialize.restype = C.c_int
e.espeak_Initialize.argtypes = [C.c_int, C.c_int, C.c_char_p, C.c_int]
e.espeak_SetVoiceByName.restype = C.c_int
e.espeak_SetVoiceByName.argtypes = [C.c_char_p]
e.espeak_SetParameter.argtypes = [C.c_int, C.c_int, C.c_int]
e.espeak_Synchronize.argtypes = []
e.espeak_IsPlaying.restype = C.c_int
e.espeak_Synth.argtypes = [C.c_void_p, C.c_size_t, C.c_uint, C.c_int, C.c_uint,
                           C.c_uint, C.c_void_p, C.c_void_p]

RATE, VOLUME, PITCH = 1, 2, 3

CB = C.CFUNCTYPE(C.c_int, C.POINTER(C.c_short), C.c_int, C.c_void_p)
buf = bytearray()


def _cb(wav, n, events):
    global buf
    if n > 0 and wav:
        buf += bytes(bytearray(C.string_at(wav, n * 2)))
    return 0


cb = CB(_cb)

if e.espeak_Initialize(AUDIO_OUTPUT_RETRIEVAL, 330, DATA.encode(), espeakINITIALIZE_DONT_EXIT) < 0:
    raise SystemExit("espeak init failed")
e.espeak_SetSynthCallback(cb)
if e.espeak_SetVoiceByName("en-gb".encode()) != 0:
    e.espeak_SetVoiceByName("en".encode())
e.espeak_SetParameter(RATE, 148, 0)
e.espeak_SetParameter(VOLUME, 120, 0)
e.espeak_SetParameter(PITCH, 42, 0)

LINES = [
    (1,  "December, nineteen hundred. Twenty miles west of Scotland, three men keep a light on a bare rock."),
    (2,  "On the twenty sixth, a relief ship comes through the fog. The lighthouse is dark."),
    (3,  "No flag. No boat. No answer."),
    (4,  "They land. Nobody comes down the steps to meet them."),
    (5,  "Inside, the lamp is trimmed and filled. The wicks are clean. The oil cans are full."),
    (6,  "One oilskin is left on its peg."),
    (7,  "At the west landing, the sea has come over the rail and torn ironwork from the rock."),
    (8,  "The last entry is dated the fifteenth. Wind northwest. Weather clear."),
    (9,  "The inquiry decides a wave took all three."),
    (10, "Everything else you have heard was added in nineteen twelve."),
    (11, "The light still runs. The three men were never found."),
]

os.makedirs("vo", exist_ok=True)
os.makedirs("work", exist_ok=True)
durs = {}
for n, text in LINES:
    global_buf = []
    buf = bytearray()
    b = text.encode()
    e.espeak_Synth(b, len(b), 0, POS_CHARACTER, 0, espeakCHARS_UTF8, None, None)
    e.espeak_Synchronize()
    while e.espeak_IsPlaying():
        time.sleep(0.02)
    data = bytes(buf)
    path = f"vo/line{n:02d}.wav"
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(22050)
        w.writeframes(data)
    d = len(data) / 2 / 22050
    durs[f"line{n:02d}"] = round(d, 3)
    print(f"line{n:02d}  {d:5.2f}s  {text}")

json.dump(durs, open("work/vo_durations.json", "w"), indent=1)
print("total", round(sum(durs.values()), 2), "s")

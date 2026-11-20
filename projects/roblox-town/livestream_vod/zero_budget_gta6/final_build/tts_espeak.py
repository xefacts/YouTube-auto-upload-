import ctypes, sys, wave, espeakng_loader as el
lib = ctypes.CDLL(el.get_library_path())
data_parent = __import__('os').path.dirname(el.get_data_path())
lib.espeak_Initialize.restype = ctypes.c_int
rate = lib.espeak_Initialize(1, 0, data_parent.encode(), 0)  # RETRIEVAL output
assert rate > 0, "espeak init failed"
voice = sys.argv[3] if len(sys.argv) > 3 else "hi"
assert lib.espeak_SetVoiceByName(voice.encode()) == 0, "voice fail"
chunks = []
CB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.POINTER(ctypes.c_short), ctypes.c_int, ctypes.c_void_p)
def cb(wav, n, ev):
    if wav and n > 0:
        chunks.append(ctypes.string_at(wav, n * 2))
    return 0
cbf = CB(cb)
lib.espeak_SetSynthCallback(cbf)
text = open(sys.argv[1], encoding='utf-8').read().encode('utf-8')
lib.espeak_Synth.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint, ctypes.c_int, ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p]
lib.espeak_Synth(text, len(text) + 1, 0, 0, 0, 1, None, None)  # flags=1 UTF8
lib.espeak_Synchronize()
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
    w.writeframes(b''.join(chunks))
print("ok rate", rate, "bytes", sum(len(c) for c in chunks))

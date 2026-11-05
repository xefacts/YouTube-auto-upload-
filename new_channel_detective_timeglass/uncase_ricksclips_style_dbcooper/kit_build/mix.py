#!/usr/bin/env python3
"""Local mix.py compatibility layer for the supplied kit (its ZIP omits mix.py).
Keeps the supplied narration samples intact; synthesizes an original low-key mystery bed and timed SFX.
Usage: python mix.py [voice.wav] [mix_raw.wav]
"""
import math, sys, wave
import numpy as np

SR = 48000
VOICE = sys.argv[1] if len(sys.argv) > 1 else 'voice.wav'
OUT = sys.argv[2] if len(sys.argv) > 2 else 'mix_raw.wav'
with wave.open(VOICE, 'rb') as w:
    if w.getsampwidth() != 2:
        raise SystemExit('Expected 16-bit PCM narration')
    sr, ch, n = w.getframerate(), w.getnchannels(), w.getnframes()
    raw = np.frombuffer(w.readframes(n), dtype='<i2').astype(np.float32) / 32768.0
if sr != SR:
    raise SystemExit(f'Expected {SR} Hz narration, got {sr}')
if ch > 1:
    raw = raw.reshape(-1, ch).mean(axis=1)
N = len(raw); D = N / SR; t_all = np.arange(N, dtype=np.float32) / SR
voice_rms = float(np.sqrt(np.mean(raw * raw)))
rng = np.random.default_rng(1971)
music = np.zeros(N, np.float32)
sfx = np.zeros(N, np.float32)

def place(dst, sig, sec, gain=1.0):
    i = int(max(0, sec) * SR)
    if i >= len(dst): return
    j = min(len(dst), i + len(sig))
    dst[i:j] += sig[:j-i] * gain

def note(freq, dur, amp=1.0, decay=3.2, harmonics=(1, .24, .08)):
    n0 = max(1, int(dur * SR)); t = np.arange(n0, dtype=np.float32) / SR
    x = np.zeros(n0, np.float32)
    for k, h in enumerate(harmonics, 1):
        x += h * np.sin(2*np.pi*freq*k*t + .07*np.sin(2*np.pi*.7*t + k))
    env = np.minimum(1, t/.012) * np.exp(-t*decay)
    env *= np.minimum(1, (dur-t)/.04).clip(0)
    return (x * env * amp).astype(np.float32)

# Slow four-chord D-minor mystery palette, soft pulse and sparse plucked notes.
bpm = 76.0; beat = 60 / bpm; bar = beat * 4
chords = [([146.83,174.61,220.00], 73.42), ([116.54,146.83,174.61],58.27),
          ([87.31,110.00,130.81],43.65), ([130.81,164.81,196.00],65.41)]
for bi, start in enumerate(np.arange(0, D, bar)):
    triad, bass = chords[bi % len(chords)]
    dur = min(bar, D-start)
    i0, i1 = int(start*SR), min(N, int((start+dur)*SR))
    t = np.arange(i1-i0, dtype=np.float32)/SR
    fade = np.minimum(1, t/.5) * np.minimum(1, (dur-t)/.65).clip(0)
    pad = (0.50*np.sin(2*np.pi*triad[0]*t) + 0.25*np.sin(2*np.pi*triad[1]*t+.15) +
           0.18*np.sin(2*np.pi*triad[2]*t+.3) + 0.12*np.sin(2*np.pi*(bass/2)*t))
    music[i0:i1] += (pad*fade*.22).astype(np.float32)
    for b in range(4):
        when = start + b*beat
        if when >= D: break
        freq = triad[(b + bi) % 3]
        place(music, note(freq*2, .42, decay=4.5), when + .035, .11)
        if b in (0, 2): place(music, note(bass, .32, decay=7, harmonics=(1,.12)), when, .07)
# Gentle opening/closing fades on the music bed.
f = int(.8*SR); music[:f] *= np.linspace(0,1,f,dtype=np.float32); music[-f:] *= np.linspace(1,0,f,dtype=np.float32)
# Calibrate bed to about 42% of the voice RMS; this is separate from the narration.
music_rms = float(np.sqrt(np.mean(music*music)))
music_target = voice_rms*.42
if music_rms: music *= music_target/music_rms

# Local synthetic effects; event times follow the narration beats.
def whoosh(d=.55, seed=1):
    r = np.random.default_rng(seed); n0=int(d*SR); t=np.arange(n0,dtype=np.float32)/SR
    noise=r.standard_normal(n0).astype(np.float32)
    # simple, stable low-pass noise via a one-pole recurrence
    filt=np.empty_like(noise); a=0.13; acc=0.
    for k,v in enumerate(noise): acc += a*(float(v)-acc); filt[k]=acc
    env=np.sin(np.pi*np.clip(t/d,0,1))**2
    return (filt*env).astype(np.float32)
def thump(d=.25, f0=72):
    t=np.arange(int(d*SR),dtype=np.float32)/SR
    return (np.sin(2*np.pi*(f0+32*np.exp(-t*28))*t)*np.exp(-t*13)).astype(np.float32)
def rustle(d=.8, seed=2):
    r=np.random.default_rng(seed); n0=int(d*SR); t=np.arange(n0,dtype=np.float32)/SR
    x=r.standard_normal(n0).astype(np.float32); env=np.sin(np.pi*np.clip(t/d,0,1))**1.6
    return (x*env).astype(np.float32)
# soft scene accents: cabin/airport transitions, jump wind, discovery, evidence/archive, river ending
for ix, sec in enumerate([4.55, 8.1, 18.8, 21.35, 26.8, 33.5, 39.3, 43.45, 48.4, 49.9, 54.8, 58.7, 60.7, 63.0]):
    place(sfx, whoosh(.42, 1971+ix), sec, .14)
for ix, sec in enumerate([3.7, 13.2, 22.4, 27.5, 44.0, 50.0, 56.8]):
    place(sfx, thump(.22, 58+ix*5), sec, .12)
for ix, sec in enumerate([5.4, 45.2, 47.4, 55.7, 57.3]):
    place(sfx, rustle(.65, 41+ix), sec, .055)
# Storm/rain texture under the jump beat, slowly faded in and out.
rain_start, rain_end = 33.5, 39.3
rn=int((rain_end-rain_start)*SR); rt=np.arange(rn,dtype=np.float32)/SR
rain=rng.standard_normal(rn).astype(np.float32); filt=np.empty_like(rain); acc=0.
for k,v in enumerate(rain): acc += .24*(float(v)-acc); filt[k]=acc
rain_env=np.minimum(1,rt/.8)*np.minimum(1,(rain_end-rain_start-rt)/.8).clip(0)
place(sfx, filt*rain_env, rain_start, .11)
# A quiet river/forest wash under the recovery and final uncertainty beats.
for start, end, seed in [(4.55,8.05,83),(43.45,54.8,84),(63.0,D,85)]:
    rn=int((end-start)*SR); rt=np.arange(rn,dtype=np.float32)/SR
    r=np.random.default_rng(seed).standard_normal(rn).astype(np.float32); filt=np.empty_like(r); acc=0.
    for k,v in enumerate(r): acc += .035*(float(v)-acc); filt[k]=acc
    env=np.minimum(1,rt/.5)*np.minimum(1,(end-start-rt)/.6).clip(0)
    place(sfx, filt*env, start, .13)
# Keep narration bytes as-is. If the summed background risks peak clipping, lower only music/SFX.
bg = music + sfx
voice_peak = float(np.max(np.abs(raw)))
peak = float(np.max(np.abs(raw + bg)))
if peak > .985:
    bg *= max(0.0, .985 - voice_peak) / max(float(np.max(np.abs(bg))), 1e-6)
mix = np.clip(raw + bg, -1, 1)
with wave.open(OUT, 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix*32767).astype('<i2').tobytes())
print(f'Wrote {OUT}: {D:.2f}s, narration RMS {voice_rms:.4f}, bed target {music_target:.4f} ({(music_target/max(voice_rms,1e-9)):.0%} of voice RMS), mix peak {float(np.max(np.abs(mix))):.3f}')

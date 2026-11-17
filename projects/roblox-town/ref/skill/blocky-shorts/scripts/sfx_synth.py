#!/usr/bin/env python3
"""Synthesizes the default sound-effect pack (numpy only). Every sound is original, generated from math,
so the pack is free to use. Replace any of them by dropping a file with the same name into <project>/sfx/."""
import os, sys, wave
import numpy as np

SR = 44100
R = np.random.default_rng(42)

def t(d): return np.arange(int(SR * d)) / SR
def env(n, a=.005, d=None, curve=4.0):
    x = np.ones(n); na = max(1, int(SR * a)); x[:na] = np.linspace(0, 1, na)
    if d is None: d = n / SR - a
    nd = n - na; x[na:] = np.exp(-curve * np.linspace(0, 1, nd)) if nd > 0 else 1
    return x
def onepole_lp(x, fc):
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape); a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a[i]) * x[i] + a[i] * s; y[i] = s
    return y
def svf_bp(x, fc, q=1.2):
    fc = np.broadcast_to(np.asarray(fc, dtype=float), x.shape); y = np.zeros_like(x); lp = bp = 0.0
    for i in range(len(x)):
        f = 2 * np.sin(np.pi * min(fc[i], SR / 6) / SR); hp = x[i] - lp - bp / q; bp += f * hp; lp += f * bp; y[i] = bp
    return y
def hp(x, fc): return x - onepole_lp(x, fc)
def norm(x, peak=.9): m = np.max(np.abs(x)) + 1e-9; return x / m * peak
def reverb(x, mix=.25, size=1.0):
    y = np.copy(x); n = len(x)
    for dly, g in [(1557, .78), (1617, .77), (1491, .79), (1422, .8)]:
        d = int(dly * size); c = np.zeros(n + d)
        for i in range(n): c[i + d] = x[i] + g * c[i] if i < n else 0
        y = y + c[:n] * mix / 4
    return y
def pad(x, sec=.05): return np.concatenate([x, np.zeros(int(SR * sec))])
def noise(d): return R.standard_normal(int(SR * d))
def sweep(f0, f1, d, shape='sin', curve=1.0):
    n = int(SR * d); f = f0 + (f1 - f0) * np.linspace(0, 1, n) ** curve; ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) if shape == 'sin' else np.sign(np.sin(ph)) * .6 if shape == 'sq' else 2 * (ph / (2 * np.pi) % 1) - 1

def whoosh(d=.38, f0=300, f1=2600, f2=500):
    n = int(SR * d); x = noise(d); k = np.linspace(0, 1, n)
    fc = np.where(k < .5, f0 + (f1 - f0) * (k / .5) ** 1.5, f1 + (f2 - f1) * ((k - .5) / .5))
    y = svf_bp(x, fc, 1.6); e = np.sin(np.pi * k) ** 1.6; return norm(y * e, .8)
def clap(seed=0):
    r = np.random.default_rng(seed); d = .16; n = int(SR * d); y = np.zeros(n)
    for k, off in enumerate([0, .008, .017]):
        i = int(off * SR); m = int(SR * (.012 if k < 2 else .12)); b = r.standard_normal(m) * np.exp(-np.linspace(0, 6 if k < 2 else 9, m)); y[i:i + m] += b * (1 if k == 2 else .7)
    y = svf_bp(y, 1350 + 300 * seed, .9) + .25 * hp(y, 3000); return norm(reverb(y, .18, .5), .85)
def bell(f0, d=1.0, partials=((1, 1), (2.76, .45), (5.4, .25), (8.93, .1))):
    tt = t(d); y = sum(a * np.sin(2 * np.pi * f0 * p * tt) * np.exp(-tt * (3 + 2.2 * p)) for p, a in partials); return y
def build(out):
    os.makedirs(out, exist_ok=True); S = {}
    S['whoosh'] = whoosh(); S['whoosh_long'] = whoosh(.7, 200, 2200, 300); S['swish'] = whoosh(.18, 900, 4200, 1200)
    tt = t(.09); S['pop'] = norm(np.sin(2 * np.pi * np.cumsum(np.linspace(900, 260, len(tt))) / SR) * np.exp(-tt * 38) + .3 * noise(.09) * np.exp(-tt * 200), .8)
    tt = t(.06); S['pop_small'] = norm(np.sin(2 * np.pi * np.cumsum(np.linspace(1500, 650, len(tt))) / SR) * np.exp(-tt * 55), .6)
    S['poof'] = norm(onepole_lp(noise(.35), 900) * env(int(SR * .35), .01, curve=5), .7)
    S['ding'] = norm(reverb(bell(1568, 1.3), .3), .7)
    sp = np.zeros(int(SR * .55))
    for k in range(7):
        f = R.uniform(3200, 6800); i = int(R.uniform(0, .38) * SR); tt = t(.14); sp[i:i + len(tt)] += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 34) * R.uniform(.4, 1)
    S['sparkle'] = norm(reverb(sp, .35), .5)
    for i in range(3): S[f'clap_{i + 1}'] = clap(i)
    ap = np.zeros(int(SR * 2.6)); r2 = np.random.default_rng(9)
    for _ in range(170):
        i = int(r2.uniform(0, 2.4) * SR); c = clap(int(r2.integers(0, 3))) * r2.uniform(.2, .7); ap[i:i + len(c)] += c[:len(ap) - i]
    k = np.linspace(0, 1, len(ap)); ap *= np.minimum(1, k * 8) * np.minimum(1, (1 - k) * 2.5); S['applause'] = norm(ap + .05 * onepole_lp(noise(2.6), 2500), .8)
    tt = t(.7); body = np.sin(2 * np.pi * np.cumsum(np.linspace(90, 38, len(tt))) / SR) * np.exp(-tt * 6); crack = onepole_lp(noise(.7), 1800) * np.exp(-tt * 30)
    S['impact'] = norm(np.tanh(2.2 * (body + .6 * crack)), .9)
    tt = t(.3); S['thud'] = norm(np.sin(2 * np.pi * np.cumsum(np.linspace(120, 55, len(tt))) / SR) * np.exp(-tt * 14) + .3 * onepole_lp(noise(.3), 600) * np.exp(-tt * 25), .85)
    tt = t(.35); S['stamp'] = norm(np.sin(2 * np.pi * np.cumsum(np.linspace(140, 60, len(tt))) / SR) * np.exp(-tt * 18) + .5 * svf_bp(noise(.35), 1800, 1.2) * np.exp(-tt * 45), .9)
    tt = t(1.6); low = np.sin(2 * np.pi * 55 * tt) * .8 + .35 * (2 * (55 * tt % 1) - 1); low = onepole_lp(low, 400) * np.exp(-tt * 2.4)
    shimmer = sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3.5) for f in [1318, 1975, 2637]) * .08
    S['night_hit'] = norm(reverb(low + shimmer, .3), .9)
    S['day_chime'] = norm(reverb(np.concatenate([bell(1046.5, .18), bell(1568, .9)]) * .8, .3), .6)
    tt = t(.4); S['flash'] = norm(hp(noise(.4), 4000) * np.sin(np.pi * np.linspace(0, 1, len(tt))) ** .5 * np.exp(-tt * 4) + .2 * np.sin(2 * np.pi * 2600 * tt) * np.exp(-tt * 8), .6)
    tt = t(.6); f = 330 + 250 * np.exp(-tt * 3) * np.sin(2 * np.pi * 13 * tt); S['boing'] = norm(np.sin(2 * np.pi * np.cumsum(f + 120 * tt) / SR) * np.exp(-tt * 4.5), .75)
    tt = t(.07); S['blip'] = norm(np.sign(np.sin(2 * np.pi * 880 * tt)) * .5 * np.exp(-tt * 30), .4)
    b = np.sin(2 * np.pi * 1250 * t(.07)) * np.exp(-t(.07) * 20); S['alert'] = norm(np.concatenate([b, np.zeros(int(SR * .05)), b]), .55)
    tt = t(.14); S['boop'] = norm(np.sin(2 * np.pi * np.cumsum(np.linspace(420, 760, len(tt))) / SR) * np.exp(-tt * 14), .55)
    tt = t(1.1); sn = onepole_lp(noise(1.1), 380) * (np.sin(np.pi * np.linspace(0, 1, len(tt))) ** 2) * (1 + .6 * np.sin(2 * np.pi * 28 * tt)); S['snore'] = norm(sn, .6)
    tt = t(.5); S['grr'] = norm(np.tanh(3 * np.sin(2 * np.pi * 95 * tt) * (1 + .5 * np.sin(2 * np.pi * 31 * tt))) * env(len(tt), .02, curve=3), .5)
    tt = t(.03); S['tick'] = norm(hp(noise(.03), 2500) * np.exp(-tt * 300), .4)
    g = noise(.22); g = np.round(g * 3) / 3; g *= (R.random(len(g)) < .7); S['glitch'] = norm(svf_bp(g, 2500, .7) + .3 * np.sign(np.sin(2 * np.pi * 180 * t(.22))) * .3, .5)
    tt = t(1.2); S['riser'] = norm(svf_bp(noise(1.2), 300 + 4000 * np.linspace(0, 1, len(tt)) ** 2, 2) * np.linspace(0, 1, len(tt)) ** 2 + .2 * np.sin(2 * np.pi * np.cumsum(200 + 800 * np.linspace(0, 1, len(tt)) ** 2) / SR) * np.linspace(0, 1, len(tt)), .7)
    for name, x in S.items():
        x = pad(np.asarray(x, dtype=float), .02); x = np.clip(x, -1, 1)
        with wave.open(os.path.join(out, name + '.wav'), 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((x * 32767).astype('<i2').tobytes())
    print(f'{len(S)} sounds -> {out}: ' + ', '.join(sorted(S)))

if __name__ == '__main__': build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'sfx'))

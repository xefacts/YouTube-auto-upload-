#!/usr/bin/env python3
"""Blocky Shorts — audio + assembly CLI (needs: python3, numpy, ffmpeg).

  bs.py init     <project>                       scaffold folders + starter story.json
  bs.py script   <project>                       export voice-over scripts (build/vo_script*.txt)
  bs.py estimate <project> [--speed 1.0]         timing without VO (build/timing.json)
  bs.py align    <project> [--audio audio/vo.mp3] [--alignment el.json | --srt subs.srt]
                                                 timing from the real voice-over (build/timing.json)
  bs.py mix      <project> [--music audio/music.mp3] [--music-db -20] [--sfx-db 0] [--vo-db 0] [--no-sfx]
                                                 build/mix.wav from VO + sound events + music (ducked)
  bs.py encode   <project> [--out out/final.mp4] [--crf 18] [--no-audio]
                                                 frames + mix -> MP4
  bs.py sfx-pack [--out DIR]                     (re)generate the default synthesized SFX pack
"""
import json, os, re, sys, subprocess, shutil, math, random

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SR = 44100

def args_of(argv):
    pos, opt = [], {}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            k = a[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith('--'): opt[k] = argv[i + 1]; i += 1
            else: opt[k] = True
        else: pos.append(a)
        i += 1
    return pos, opt

def load_story(proj):
    with open(os.path.join(proj, 'story.json')) as f: return json.load(f)

def lines_of(story):
    out = []
    for si, sh in enumerate(story['shots']):
        for l in sh.get('lines', []):
            o = {'text': l} if isinstance(l, str) else dict(l)
            o['shot'] = si; out.append(o)
    return out

def plain(t): return (t or '').replace('*', '')

def need_numpy():
    try:
        import numpy as np; return np
    except ImportError:
        sys.exit('numpy is required: pip install numpy')

def ffmpeg_decode(path, sr=SR, mono=True):
    np = need_numpy()
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1' if mono else '2', '-ar', str(sr), '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    a = np.frombuffer(raw, dtype=np.float32).copy()
    return a if mono else a.reshape(-1, 2)

def write_wav(path, x, sr=SR):
    np = need_numpy(); import wave
    x = np.clip(x, -1, 1)
    if x.ndim == 1: x = np.stack([x, x], 1)
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype('<i2').tobytes())

# ------------------------------------------------------------------ init
STARTER = {
  "title": "My Short", "fps": 30,
  "style": {"caption": {"size": 50, "y": 0.725}, "clapBursts": True},
  "cast": {"hero": {"preset": "kid"}},
  "shots": [
    {"set": "plaza", "mood": "day", "lines": ["In this town,", "every time you *sneeze...*"],
     "cast": {"hero": {"spot": "front", "do": [{"do": "walk", "at": 0, "to": [-2, 0, 9], "dur": 0.8}]}},
     "extras": {"walkers": 6}, "camera": {"on": "hero", "shot": "full", "move": "push"},
     "fx": [{"punch": 0.18, "at": "sneeze..."}]}
  ]
}
def cmd_init(proj):
    for d in ['audio', 'sfx', 'build', 'out']: os.makedirs(os.path.join(proj, d), exist_ok=True)
    p = os.path.join(proj, 'story.json')
    if not os.path.exists(p):
        with open(p, 'w') as f: json.dump(STARTER, f, indent=1)
    print(f'project ready: {proj}\n  story.json   (edit me)\n  audio/       put vo.mp3 (voice-over) and optional music.mp3 here\n  sfx/         optional: your own sound files, named like the events (whoosh.wav, clap.mp3 ...)')

# ------------------------------------------------------------------ VO script export
def cmd_script(proj):
    st = load_story(proj); L = lines_of(st); os.makedirs(os.path.join(proj, 'build'), exist_ok=True)
    shots = {}
    for l in L: shots.setdefault(l['shot'], []).append(plain(l.get('text', '')).strip())
    # v3/v4 (audio tags) version: one paragraph per shot -> natural pauses at line breaks
    v3 = '\n'.join(' '.join(x for x in shots[k] if x) for k in sorted(shots))
    # v2 / flash version: explicit short breaks between shots
    v2 = ' <break time="0.25s" /> '.join(' '.join(x for x in shots[k] if x) for k in sorted(shots))
    plain_txt = ' '.join(' '.join(x for x in shots[k] if x) for k in sorted(shots))
    for name, txt in [('vo_script.txt', v3), ('vo_script_v2_breaks.txt', v2), ('vo_transcript.txt', plain_txt)]:
        with open(os.path.join(proj, 'build', name), 'w') as f: f.write(txt + '\n')
    words = len(plain_txt.split())
    print(f'wrote build/vo_script.txt (Eleven v3/v4: paste as is), build/vo_script_v2_breaks.txt (Multilingual v2 / Flash), build/vo_transcript.txt')
    print(f'{words} words  ~{words / 2.9:.1f}s at a brisk narration pace\n')
    print(v3)

# ------------------------------------------------------------------ estimate (no VO)
def est_line(text, speed=1.0):
    p = plain(text).strip()
    if not p: return 0.5
    words = len(p.split()); d = 0.1 + words * 0.25
    if re.search(r'[.!?]["\']?$', p): d += 0.12
    if re.search(r'(\.\.\.|…)$', p): d += 0.2
    if p.endswith(','): d += 0.05
    return max(0.32, d) / speed

def cmd_estimate(proj, opt):
    st = load_story(proj); L = lines_of(st); speed = float(opt.get('speed', st.get('speed', 1.0)))
    t = st.get('lead', 0); out = []
    for si, sh in enumerate(st['shots']):
        ls = [l for l in L if l['shot'] == si]
        for l in ls:
            d = l.get('dur') or est_line(l.get('text', ''), speed)
            out.append({'text': l.get('text', ''), 'start': round(t, 3), 'end': round(t + d, 3)}); t += d + l.get('pause', 0)
        t += sh.get('hold', 0) if ls else sh.get('dur', 1)
    save_timing(proj, out, 'estimate', None)

def save_timing(proj, lines, source, total, words=None):
    os.makedirs(os.path.join(proj, 'build'), exist_ok=True)
    d = {'source': source, 'lines': lines}
    if total: d['total'] = round(total, 3)
    if words: d['words'] = words
    with open(os.path.join(proj, 'build', 'timing.json'), 'w') as f: json.dump(d, f, indent=1)
    print(f'build/timing.json  ({source}, {len(lines)} lines' + (f', audio {total:.2f}s' if total else '') + ')')
    for i, l in enumerate(lines): print(f'  {i:2d}  {l["start"]:6.2f}–{l["end"]:6.2f}  {l["text"]}')

# ------------------------------------------------------------------ alignment
def tokens(text):
    return [w for w in re.findall(r"[\w'’]+(?:[.,!?…]+|\.\.\.)?", plain(text).replace('—', ' ').replace('-', ' '))]

def syllables(word):
    w = re.sub(r"[^a-z]", '', word.lower())
    if not w: return 1.0
    groups = re.findall(r'[aeiouy]+', w); n = len(groups)
    if w.endswith('e') and n > 1 and not w.endswith(('le', 'ee')): n -= 1
    if re.search(r'\d', word): n = max(n, len(word))
    return max(1, n) + 0.15 * len(w) / 4

def speech_segments(x, sr=16000):
    np = need_numpy()
    hop = int(sr * .01); win = int(sr * .03)
    n = max(1, (len(x) - win) // hop)
    e = np.array([np.sqrt(np.mean(x[i * hop:i * hop + win] ** 2) + 1e-12) for i in range(n)])
    db = 20 * np.log10(e + 1e-9)
    k = 5; dbs = np.convolve(db, np.ones(k) / k, mode='same')
    floor = np.percentile(dbs, 10); peak = np.percentile(dbs, 95)
    thr = floor + max(6, (peak - floor) * .28)
    act = dbs > thr
    segs = []; i = 0
    while i < n:
        if act[i]:
            j = i
            while j < n and act[j]: j += 1
            segs.append([i * .01, j * .01]); i = j
        else: i += 1
    merged = []
    for s in segs:
        if merged and s[0] - merged[-1][1] < .07: merged[-1][1] = s[1]
        else: merged.append(s)
    return [s for s in merged if s[1] - s[0] > .05], thr

def align_by_energy(words, x, sr=16000):
    """Map words onto detected speech: DP matches silences to likely word boundaries (punctuation / line ends)."""
    np = need_numpy()
    segs, _ = speech_segments(x, sr)
    if not segs: sys.exit('no speech detected in the audio')
    wts = [syllables(w['w']) for w in words]; cum = np.cumsum([0] + wts); total_w = cum[-1]
    seg_d = [b - a for a, b in segs]; Ts = sum(seg_d)
    # gaps between segments with their position in "speech time"
    gaps = []; acc = 0
    for i in range(len(segs) - 1):
        acc += seg_d[i]; gaps.append({'s': acc / Ts, 'len': segs[i + 1][0] - segs[i][1], 'i': i})
    K = len(words) - 1
    bpos = [cum[k + 1] / total_w for k in range(K)]
    bonus = [(2.0 if words[k].get('lineEnd') else 0) + (1.5 if re.search(r'[.!?…]$', words[k]['w']) else .8 if words[k]['w'].endswith(',') else 0) for k in range(K)]
    J = len(gaps); INF = 1e9
    def bscore(k):
        w = words[k]['w']
        if re.search(r'(\.\.\.|…|[.!?])$', w): return 1.0
        if w.endswith(','): return .6
        if words[k].get('lineEnd'): return .35
        return .08
    BS = [bscore(k) for k in range(K)]
    GS = [min(g['len'], .5) / .5 for g in gaps]
    A = float(os.environ.get('BS_ALIGN_A', 60))
    # edit-distance DP: match gap i <-> boundary k, or skip a boundary (no pause there), or skip a gap (pause inside a phrase)
    dp = np.full((J + 1, K + 1), INF); bt = np.zeros((J + 1, K + 1), dtype=np.int8); dp[0, 0] = 0
    for i in range(J + 1):
        for k in range(K + 1):
            if i == 0 and k == 0: continue
            best = INF; how = 0
            if i > 0 and k > 0:
                c = dp[i - 1, k - 1] + A * (bpos[k - 1] - gaps[i - 1]['s']) ** 2 - float(os.environ.get('BS_BONUS', 1.2)) * GS[i - 1] * BS[k - 1]
                if c < best: best, how = c, 1
            if k > 0:
                c = dp[i, k - 1] + float(os.environ.get('BS_MISS', .9)) * BS[k - 1]
                if c < best: best, how = c, 2
            if i > 0:
                c = dp[i - 1, k] + float(os.environ.get('BS_EXTRA0', .25)) + float(os.environ.get('BS_EXTRA', 1.0)) * GS[i - 1]
                if c < best: best, how = c, 3
            dp[i, k] = best; bt[i, k] = how
    anchors = {}; i, k = J, K
    while i > 0 or k > 0:
        h = bt[i, k]
        if h == 1: anchors[k - 1] = gaps[i - 1]; i -= 1; k -= 1
        elif h == 2: k -= 1
        else: i -= 1
    # convert anchors to real-time boundaries; interpolate the rest inside speech time
    def speech_to_real(s):
        s = min(max(s, 0), 1) * Ts; acc = 0
        for a, b in segs:
            d = b - a
            if s <= acc + d + 1e-9: return a + (s - acc)
            acc += d
        return segs[-1][1]
    # boundary k in speech-time: anchored -> gap position; else interpolate between anchors by weights
    keys = sorted(anchors)
    pts = [(-1, 0.0)] + [(k, anchors[k]['s']) for k in keys] + [(K, 1.0)]
    bs = []
    for k in range(K):
        if k in anchors: bs.append(anchors[k]['s']); continue
        lo = max(p for p in pts if p[0] < k); hi = min(p for p in pts if p[0] > k)
        wlo = cum[lo[0] + 1] if lo[0] >= 0 else 0; whi = cum[hi[0] + 1] if hi[0] < K else total_w
        f = (cum[k + 1] - wlo) / max(1e-9, whi - wlo); bs.append(lo[1] + (hi[1] - lo[1]) * f)
    out = []
    for i, w in enumerate(words):
        if i == 0: st = segs[0][0]
        elif (i - 1) in anchors: st = segs[anchors[i - 1]['i'] + 1][0]
        else: st = speech_to_real(bs[i - 1])
        if i == K: en = segs[-1][1]
        elif i in anchors: en = segs[anchors[i]['i']][1]
        else: en = speech_to_real(bs[i])
        out.append({'w': w['w'], 'start': round(st, 3), 'end': round(max(en, st + .05), 3)})
    return out, segs, len(anchors)

def words_from_eleven(js, words):
    """Accepts ElevenLabs /with-timestamps (alignment.characters...) or /forced-alignment (words[]) JSON."""
    if 'words' in js and js['words'] and 'start' in js['words'][0]:
        src = [{'w': x['text'], 'start': x['start'], 'end': x['end']} for x in js['words'] if x['text'].strip()]
    else:
        al = js.get('normalized_alignment') or js.get('alignment') or js
        ch = al['characters']; s = al.get('character_start_times_seconds') or [x / 1000 for x in al['char_start_times_ms']]; e = al.get('character_end_times_seconds') or [x / 1000 for x in al['char_end_times_ms']]
        src = []; cur = None
        for c, a, b in zip(ch, s, e):
            if c.strip() == '' or c in '<>':
                if cur: src.append(cur); cur = None
                continue
            if cur is None: cur = {'w': c, 'start': a, 'end': b}
            else: cur['w'] += c; cur['end'] = b
        if cur: src.append(cur)
        src = [x for x in src if re.search(r'\w', x['w']) and not re.match(r'^\[.*\]$', x['w'])]
    return match_words(words, src)

def norm(w): return re.sub(r"[^\w]", '', w.lower().replace('’', "'"))

def match_words(words, src):
    out = []; j = 0
    for w in words:
        target = norm(w['w']); found = None
        for k in range(j, min(len(src), j + 8)):
            if norm(src[k]['w']) == target or (target and norm(src[k]['w']).startswith(target[:4])): found = k; break
        if found is None and j < len(src): found = j
        if found is None: out.append({'w': w['w'], 'start': out[-1]['end'] if out else 0, 'end': (out[-1]['end'] if out else 0) + .2}); continue
        out.append({'w': w['w'], 'start': src[found]['start'], 'end': src[found]['end']}); j = found + 1
    return out

def words_from_srt(path, words):
    txt = open(path, encoding='utf-8').read(); cues = []
    for b in re.split(r'\n\s*\n', txt.strip()):
        m = re.search(r'(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)', b)
        if not m: continue
        g = list(map(int, m.groups())); a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; e = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        body = ' '.join(b.split('\n')[2:]) if re.match(r'^\d+$', b.split('\n')[0].strip()) else ' '.join(b.split('\n')[1:])
        toks = tokens(body); wt = [syllables(x) for x in toks]; tot = sum(wt) or 1; t = a
        for x, ww in zip(toks, wt): d = (e - a) * ww / tot; cues.append({'w': x, 'start': t, 'end': t + d}); t += d
    return match_words(words, cues)

def cmd_align(proj, opt):
    np = need_numpy()
    st = load_story(proj); L = lines_of(st)
    audio = opt.get('audio') or next((os.path.join('audio', f) for f in sorted(os.listdir(os.path.join(proj, 'audio'))) if f.lower().startswith('vo') and f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'))), None) if os.path.isdir(os.path.join(proj, 'audio')) else opt.get('audio')
    if not audio: sys.exit('no voice-over found: put it at audio/vo.mp3 or pass --audio')
    apath = audio if os.path.isabs(audio) else os.path.join(proj, audio)
    x16 = ffmpeg_decode(apath, 16000); total = len(x16) / 16000
    words = []
    for li, l in enumerate(L):
        toks = tokens(l.get('text', ''))
        for k, t in enumerate(toks): words.append({'w': t, 'line': li, 'lineEnd': k == len(toks) - 1})
    if not words: sys.exit('story has no words')
    if opt.get('alignment'):
        with open(opt['alignment'] if os.path.isabs(opt['alignment']) else os.path.join(proj, opt['alignment'])) as f: js = json.load(f)
        aligned = words_from_eleven(js, words); source = 'elevenlabs'
    elif opt.get('srt'):
        aligned = words_from_srt(opt['srt'] if os.path.isabs(opt['srt']) else os.path.join(proj, opt['srt']), words); source = 'srt'
    else:
        aligned, segs, nanch = align_by_energy(words, x16); source = 'energy'
        print(f'speech segments: {len(segs)}, anchored pauses: {nanch}/{len(segs) - 1}')
    for w, a in zip(words, aligned): w.update(start=a['start'], end=a['end'])
    out = []
    for li, l in enumerate(L):
        ws = [w for w in words if w['line'] == li]
        if ws: out.append({'text': l.get('text', ''), 'start': ws[0]['start'], 'end': ws[-1]['end']})
        else: out.append({'text': l.get('text', ''), 'start': None, 'end': None})
    # silent lines: place in the gap between neighbours
    for i, o in enumerate(out):
        if o['start'] is None:
            prev_end = next((out[k]['end'] for k in range(i - 1, -1, -1) if out[k]['end'] is not None), 0)
            nxt = next((out[k]['start'] for k in range(i + 1, len(out)) if out[k]['start'] is not None), prev_end + (L[i].get('dur') or .5))
            o['start'] = prev_end; o['end'] = max(prev_end + .05, nxt)
    # monotonic clean-up
    for i in range(1, len(out)):
        if out[i]['start'] < out[i - 1]['start'] + .05: out[i]['start'] = round(out[i - 1]['start'] + .05, 3)
        out[i]['end'] = max(out[i]['end'], out[i]['start'] + .05)
    first = out[0]['start'] if out else 0
    if first < .35 and st.get('lead') is None: pass
    save_timing(proj, out, source, total, words=[{k: w[k] for k in ('w', 'start', 'end', 'line')} for w in words])
    if source == 'energy': print('\nCheck the times above against the audio. For exact timing use ElevenLabs timestamps (--alignment) or an SRT (--srt).')

# ------------------------------------------------------------------ SFX library + mixer
def sfx_dirs(proj):
    return [os.path.join(proj, 'sfx'), os.path.join(SKILL, 'assets', 'sfx')]

def find_sfx(name, proj):
    for d in sfx_dirs(proj):
        if not os.path.isdir(d): continue
        files = sorted(f for f in os.listdir(d) if re.match(rf'^{re.escape(name)}(_\d+)?\.(wav|mp3|ogg|m4a|flac|aiff?)$', f, re.I))
        if files: return [os.path.join(d, f) for f in files]
    return []

def cmd_mix(proj, opt):
    np = need_numpy(); B = os.path.join(proj, 'build')
    ev_path = os.path.join(B, 'events.json'); rj = os.path.join(B, 'render.json'); inf = os.path.join(B, 'info.json')
    if not os.path.exists(ev_path): sys.exit('build/events.json missing — run: node scripts/render.mjs check <project>')
    events = json.load(open(ev_path))
    dur = json.load(open(rj))['duration'] if os.path.exists(rj) else json.load(open(inf))['duration']
    n = int(math.ceil(dur * SR)) + SR // 2; mix = np.zeros(n, dtype=np.float32)
    db = lambda x: 10 ** (float(x) / 20)
    vo = None
    vo_path = opt.get('vo') or next((os.path.join(proj, 'audio', f) for f in sorted(os.listdir(os.path.join(proj, 'audio'))) if f.lower().startswith('vo') and f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'))), None) if os.path.isdir(os.path.join(proj, 'audio')) else None
    if vo_path and not opt.get('no-vo'):
        vo = ffmpeg_decode(vo_path) * db(opt.get('vo-db', 0)); vo = vo[:n]; mix[:len(vo)] += vo
        print(f'VO: {os.path.relpath(vo_path, proj)} ({len(vo) / SR:.2f}s)')
    cache = {}; rnd = random.Random(7); missing = set(); placed = 0
    if not opt.get('no-sfx'):
        for e in events:
            files = cache.get(e['sfx'])
            if files is None:
                paths = find_sfx(e['sfx'], proj); files = [ffmpeg_decode(p) for p in paths]; cache[e['sfx']] = files
            if not files: missing.add(e['sfx']); continue
            x = files[rnd.randrange(len(files))]
            if len(files) == 1 and e['sfx'] in ('clap', 'pop_small', 'blip', 'tick'):  # light pitch variation for repeats
                r = rnd.uniform(.93, 1.07); x = np.interp(np.arange(0, len(x), r), np.arange(len(x)), x).astype(np.float32)
            i = int(e['t'] * SR); g = float(e.get('gain', 1)) * db(opt.get('sfx-db', 0)) * (0.55 if vo is not None else 0.8)
            seg = x[:max(0, n - i)] * g; mix[i:i + len(seg)] += seg; placed += 1
    print(f'SFX: {placed} placed' + (f'; no file for: {", ".join(sorted(missing))}' if missing else ''))
    mpath = opt.get('music') or (os.path.join(proj, 'audio', 'music.mp3') if os.path.exists(os.path.join(proj, 'audio', 'music.mp3')) else None)
    if mpath and not os.path.isabs(mpath) and not os.path.exists(mpath): mpath = os.path.join(proj, mpath)
    if mpath and os.path.exists(mpath):
        m = ffmpeg_decode(mpath); reps = int(math.ceil(n / max(1, len(m)))); m = np.tile(m, reps)[:n] * db(opt.get('music-db', -20))
        if vo is not None:  # sidechain duck
            env = np.zeros(n, dtype=np.float32); v = np.abs(np.pad(vo, (0, max(0, n - len(vo)))))[:n]
            hop = 441; e = np.array([v[i:i + hop].mean() for i in range(0, n, hop)]); on = (e > .02).astype(float)
            sm = np.zeros_like(on); a = 0
            for i, val in enumerate(on): a = a + (val - a) * (.5 if val > a else .06); sm[i] = a
            env = np.repeat(sm, hop)[:n]; m *= (1 - .55 * env)
        fade = int(SR * 1.0); m[-fade:] *= np.linspace(1, 0, fade); mix += m
        print(f'music: {os.path.relpath(mpath, proj)}')
    # soft limiter
    peak = np.max(np.abs(mix)) + 1e-9
    if peak > .98: mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    raw = os.path.join(B, 'mix_raw.wav'); write_wav(raw, mix[:int(dur * SR)])
    out = os.path.join(B, 'mix.wav')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.0:LRA=11', '-ar', str(SR), out], check=True)
    print(f'mix: build/mix.wav ({dur:.2f}s, normalized to -14 LUFS)')

def cmd_encode(proj, opt):
    B = os.path.join(proj, 'build'); rj = json.load(open(os.path.join(B, 'render.json')))
    frames = os.path.join(B, 'frames'); count = len([f for f in os.listdir(frames) if f.endswith('.jpg')])
    if count < rj['frames']: sys.exit(f'only {count}/{rj["frames"]} frames rendered — run render.mjs frames again first')
    st = load_story(proj); title = re.sub(r'[^\w-]+', '_', st.get('title', 'short')).strip('_').lower() or 'short'
    out = opt.get('out') or os.path.join(proj, 'out', f'{title}.mp4'); os.makedirs(os.path.dirname(out), exist_ok=True)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-framerate', str(rj['fps']), '-i', os.path.join(frames, '%05d.jpg')]
    mix = os.path.join(B, 'mix.wav'); audio = os.path.exists(mix) and not opt.get('no-audio')
    if audio: cmd += ['-i', mix]
    cmd += ['-c:v', 'libx264', '-preset', opt.get('preset', 'medium'), '-crf', str(opt.get('crf', 18)), '-pix_fmt', 'yuv420p', '-movflags', '+faststart']
    if audio: cmd += ['-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += [out]; subprocess.run(cmd, check=True)
    print(f'video: {out}  ({rj["width"]}x{rj["height"]} @ {rj["fps"]}fps, {rj["duration"]:.2f}s, audio: {"yes" if audio else "no"})')

def main():
    if len(sys.argv) < 2: print(__doc__); return
    cmd = sys.argv[1]; pos, opt = args_of(sys.argv[2:])
    if cmd == 'sfx-pack':
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); import sfx_synth
        sfx_synth.build(opt.get('out') or os.path.join(SKILL, 'assets', 'sfx')); return
    if not pos: print(__doc__); return
    proj = os.path.abspath(pos[0])
    {'init': lambda: cmd_init(proj), 'script': lambda: cmd_script(proj), 'estimate': lambda: cmd_estimate(proj, opt), 'align': lambda: cmd_align(proj, opt),
     'mix': lambda: cmd_mix(proj, opt), 'encode': lambda: cmd_encode(proj, opt)}.get(cmd, lambda: print(__doc__))()

if __name__ == '__main__': main()

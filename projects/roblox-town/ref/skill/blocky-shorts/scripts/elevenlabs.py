#!/usr/bin/env python3
"""Optional ElevenLabs helper (standard library only). Needs an API key and network access to api.elevenlabs.io.
The key is read from $ELEVENLABS_API_KEY (or --key). It is never printed or written to disk.

  elevenlabs.py voices                                         list voices on the account
  elevenlabs.py tts   <project> --voice VOICE_ID [--model eleven_multilingual_v2|eleven_v3] [--speed 1.05]
                      [--stability 0.4] [--style 0.3]          -> audio/vo.mp3 + build/el_alignment.json (exact timing)
  elevenlabs.py align <project> [--audio audio/vo.mp3]          forced alignment of a VO you made in the app
                                                                -> build/el_alignment.json
  elevenlabs.py sfx   <project> --name whoosh --prompt "fast cartoon whoosh" [--seconds 1.0] [--influence 0.6]
                                                                -> sfx/whoosh.mp3 (overrides the built-in sound)
Then run:  python3 scripts/bs.py align <project> --alignment build/el_alignment.json
"""
import json, os, sys, base64, urllib.request, urllib.error, uuid, mimetypes

API = os.environ.get('ELEVENLABS_API_BASE', 'https://api.elevenlabs.io')

def args_of(argv):
    pos, opt, i = [], {}, 0
    while i < len(argv):
        a = argv[i]
        if a.startswith('--'):
            k = a[2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith('--'): opt[k] = argv[i + 1]; i += 1
            else: opt[k] = True
        else: pos.append(a)
        i += 1
    return pos, opt

def key(opt):
    k = opt.get('key') or os.environ.get('ELEVENLABS_API_KEY')
    if not k: sys.exit('Set ELEVENLABS_API_KEY (or pass --key). Get it in ElevenLabs > Profile/Developers > API keys.')
    return k

def req(method, path, opt, body=None, headers=None, raw=False):
    h = {'xi-api-key': key(opt)}; h.update(headers or {})
    data = body
    if isinstance(body, dict): data = json.dumps(body).encode(); h['Content-Type'] = 'application/json'
    r = urllib.request.Request(API + path, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            b = resp.read(); return b if raw else json.loads(b)
    except urllib.error.HTTPError as e:
        sys.exit(f'ElevenLabs API error {e.code}: {e.read()[:400].decode(errors="ignore")}')
    except urllib.error.URLError as e:
        sys.exit(f'Cannot reach {API} ({e.reason}). If this runs in Claude\'s sandbox, the domain may need to be allowed '
                 'in claude.ai Settings > Capabilities (allowed domains), or generate the voice in the ElevenLabs app and upload the MP3.')

def multipart(fields, files):
    bnd = uuid.uuid4().hex; out = b''
    for k, v in fields.items(): out += f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
    for k, p in files.items():
        out += f'--{bnd}\r\nContent-Disposition: form-data; name="{k}"; filename="{os.path.basename(p)}"\r\nContent-Type: {mimetypes.guess_type(p)[0] or "application/octet-stream"}\r\n\r\n'.encode() + open(p, 'rb').read() + b'\r\n'
    return out + f'--{bnd}--\r\n'.encode(), {'Content-Type': f'multipart/form-data; boundary={bnd}'}

def transcript(proj):
    st = json.load(open(os.path.join(proj, 'story.json'))); parts = []
    for sh in st['shots']:
        parts.append(' '.join((l if isinstance(l, str) else l.get('text', '')).replace('*', '') for l in sh.get('lines', [])).strip())
    return [p for p in parts if p]

def main():
    if len(sys.argv) < 2: print(__doc__); return
    cmd = sys.argv[1]; pos, opt = args_of(sys.argv[2:])
    if cmd == 'voices':
        for v in req('GET', '/v1/voices', opt).get('voices', []): print(f"{v['voice_id']}  {v['name']}  ({v.get('labels', {}).get('accent', '')} {v.get('labels', {}).get('gender', '')})")
        return
    if not pos: print(__doc__); return
    proj = os.path.abspath(pos[0]); os.makedirs(os.path.join(proj, 'build'), exist_ok=True); os.makedirs(os.path.join(proj, 'audio'), exist_ok=True)
    if cmd == 'tts':
        if not opt.get('voice'): sys.exit('--voice VOICE_ID is required (see: elevenlabs.py voices)')
        model = opt.get('model', 'eleven_multilingual_v2'); parts = transcript(proj)
        sep = ' <break time="0.25s" /> ' if 'v2' in model or 'flash' in model or 'turbo' in model else '\n'
        text = sep.join(parts)
        body = {'text': text, 'model_id': model, 'voice_settings': {'stability': float(opt.get('stability', .4)), 'similarity_boost': .8, 'style': float(opt.get('style', .3)), 'use_speaker_boost': True, 'speed': float(opt.get('speed', 1.05))}}
        r = req('POST', f"/v1/text-to-speech/{opt['voice']}/with-timestamps?output_format=mp3_44100_128", opt, body)
        open(os.path.join(proj, 'audio', 'vo.mp3'), 'wb').write(base64.b64decode(r['audio_base64']))
        json.dump({k: r.get(k) for k in ('alignment', 'normalized_alignment')}, open(os.path.join(proj, 'build', 'el_alignment.json'), 'w'))
        print('wrote audio/vo.mp3 and build/el_alignment.json\nnext: python3 scripts/bs.py align ' + pos[0] + ' --alignment build/el_alignment.json')
    elif cmd == 'align':
        audio = opt.get('audio', 'audio/vo.mp3'); ap = audio if os.path.isabs(audio) else os.path.join(proj, audio)
        body, h = multipart({'text': ' '.join(transcript(proj))}, {'file': ap})
        r = req('POST', '/v1/forced-alignment', opt, body, h)
        json.dump(r, open(os.path.join(proj, 'build', 'el_alignment.json'), 'w'))
        print(f"aligned {len(r.get('words', []))} words (loss {r.get('loss')}) -> build/el_alignment.json\nnext: python3 scripts/bs.py align {pos[0]} --alignment build/el_alignment.json")
    elif cmd == 'sfx':
        if not opt.get('prompt') or not opt.get('name'): sys.exit('--name and --prompt are required')
        body = {'text': opt['prompt'], 'prompt_influence': float(opt.get('influence', .6))}
        if opt.get('seconds'): body['duration_seconds'] = float(opt['seconds'])
        b = req('POST', '/v1/sound-generation', opt, body, raw=True); os.makedirs(os.path.join(proj, 'sfx'), exist_ok=True)
        p = os.path.join(proj, 'sfx', opt['name'] + '.mp3'); open(p, 'wb').write(b); print('wrote ' + p)
    else: print(__doc__)

if __name__ == '__main__': main()

# Media Extractor

Video link do (YouTube ya koi bhi yt-dlp supported link) ya local file do.
Ye system nikalta hai:

- `source.mp4` — video (default max 1080p)
- `audio.wav` / `audio.mp3` — full audio track
- `sfx/` — sound events (hits, stingers, SFX candidates) as short WAV clips
- `keyframes/` + `scenes` — scene-cut timestamps and a still per scene
- `subtitles` (agar video mein hain)
- `metadata.json` (title, uploader, duration, license) aur `manifest.json` (sab ka index)
- optional: `stems/` — vocals vs music/SFX (demucs, heavy)

> **Rights:** Sirf wo content process karo jis ke rights tumhare paas hon ya jo licence mein allowed ho.
> YouTube ke Terms aur copyright law lagu hote hain. Ye tool kisi bhi content ki ownership nahi deta.

## Setup

```bash
cd tools/media_extractor
python3 -m pip install -r requirements.txt
# ffmpeg: system mein ho to theek; warna imageio-ffmpeg ka binary auto use hota hai
```

## CLI

```bash
# link se
python3 -m media_extractor "https://www.youtube.com/watch?v=VIDEO_ID" -o downloads/my_video

# local file se (download nahi hota)
python3 -m media_extractor ./clip.mp4 -o downloads/clip

# sirf audio + SFX, scenes skip
python3 -m media_extractor URL --no-scenes
```

Result: `downloads/my_video/manifest.json` mein sab files ki list aur har sound event / scene ka timestamp hota hai.

## Web app (paste link ya upload)

```bash
uvicorn media_extractor.web:app --host 0.0.0.0 --port 8000
# browser: http://localhost:8000
```

Endpoints: `POST /api/jobs` (form: `url` ya `file`), `GET /api/jobs/{id}`, `GET /files/{id}/{path}`.
Data `MEDIA_EXTRACTOR_DATA` (default `downloads/jobs`) mein jaata hai.

## Tests (offline)

```bash
python3 -m unittest discover -s tests -v
```

Synthetic clip banakar check karta hai: beeps → sound events, colour change → scene cut, aur sab outputs.

## Limits (honest)

- Sound events = loudness onsets (hits/stingers/SFX). Ye music ya dialogue ko "samajhta" nahi; sirf sharp jumps dhoondhta hai.
- Stems separation ke liye `demucs` + torch chahiye, aur pehli baar model download hota hai.
- Scene detection `fps=2` par sample karta hai (lambi videos ke liye fast).
- Subtitles sirf tab milte hain jab video mein captions hon.

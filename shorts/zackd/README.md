# Zack D Films–style 3D short pipeline (self-contained)

`shorts/zackd/` turns one curiosity topic into a finished vertical (9:16) 3D
animated short: curiosity-loop script → 3D hero shots → narration → burned-in
captions → impact zooms → procedural score → `mp4`.

Example output: **`shorts/out/tap_your_card.mp4`** — *"What actually happens
when you tap your card?"* (40 s, 1080×1920, 30 fps).

---

## 1. Research: which GitHub projects do this?

Searched with `gh search repos` for the projects shown in the screenshot:

| Repo | What it is | Why it is (not) used here |
| --- | --- | --- |
| [`Anil-matcha/zack-d-films-ai-video-generator`](https://github.com/Anil-matcha/zack-d-films-ai-video-generator) | An agent skill (`zackd-director`, documented in `SKILL.md`) that turns a topic into a Zack-D-style short: `beats.json` script, character sheets, 3D keyframes, Veo 3.1 motion clips, cloned voice, ffmpeg assembly. | **Used as the creative blueprint** (beat structure, 2–4 s cuts, curiosity-loop formulas, caption/impact-zoom conventions in `references/`). Its render stage needs a paid **MuAPI** key + **Google Veo 3.1**, so it can't run production here. |
| [`NoelHuwae/zack-d-films-ai-video-generator`](https://github.com/NoelHuwae/zack-d-films-ai-video-generator) | Same idea (MuAPI + Veo 3.1 + FFmpeg), single-question input. | Same API dependency. |
| [`zhuyansen/awesome-claude-video-skills`](https://github.com/zhuyansen/awesome-claude-video-skills) | Index of 180 video-making agent skills, graded. | Reference only. |
| [`imtamiliniyan/claude-video-skills`](https://github.com/imtamiliniyan/claude-video-skills) | Remotion-based editing automation (beat-timed graphics, captions, b-roll). | Editing ideas (word-timed captions, impact zooms) reused. |
| [`Neelshah1810/Claude-Video-Skills`](https://github.com/Neelshah1810/Claude-Video-Skills) | 11 skills that make motion-graphics videos as HTML + MP4. | Reference only. |

### Why not Blender?

The obvious "real 3D" route is Blender's Python module (`pip install bpy`) — no
GUI needed. It installs here, but **it cannot start in this sandbox**: the wheel
links against X11/GL shared libraries that are not present and cannot be
installed (only PyPI/npm/GitHub are reachable):

```
ImportError: libXrender.so.1: cannot open shared object file
ldd bpy/lib/*.so → libSM.so.6, libICE.so.6, libGL.so.1: not found
```

`headless-gl` (Node) fails the same way. So this folder ships its own 3D engine
instead — see below. The creative output is the same shape as the MuAPI/Veo
pipelines, without any external API key.

---

## 2. What is in here

| File | Role |
| --- | --- |
| `engine.py` | **`stylize3d`** — a dependency-free (numpy) software 3D renderer: super-ellipsoid / rounded-plate / cylinder / torus primitives, perspective camera, z-buffer rasteriser with perspective-correct attributes, deferred shading (3-point studio lights, GGX specular, fake studio HDRI for metals, PCF shadow map, SSAO), post (bloom, depth of field, ACES tonemap, split-tone, chromatic aberration, vignette, grain). |
| `art.py` | Procedural textures with PIL: card face (bank name, number, chip window, contactless waves), terminal UI, chip contacts, vault ledger, glowing type plates. |
| `scene.py` | The film: 8 shots, each a pure function of normalised time `t∈[0,1]` → `(objects, camera, render_kwargs)`. |
| `beats.json` | The curiosity-loop script: 8 beats, one narration line per shot. |
| `captions.py` | Word-timed uppercase caption pages with pop-in, auto-fit to frame width, scrim. |
| `render_short.py` | Timeline (VO duration → frames), multiprocess frame renderer, impact zoom/shake on cuts, caption burn-in, JPEG frames. |
| `audio.py` | Procedural score + SFX (impacts, risers, whooshes, heartbeat pulse, terminal beeps), VO placement, master limit → `mix.wav`. |
| `measure_voice.py` | ffprobe the VO clips → `timing.json` (beat → seconds). |
| `assemble.py` | ffmpeg: frames + mix → H.264/AAC 1080×1920 `mp4` with `+faststart`. |
| `contact.py` | One review frame per shot, as a contact sheet. |

## 3. Run it

```bash
python3 -m venv .venv && .venv/bin/pip install numpy pillow imageio-ffmpeg
cd shorts/zackd

# 1) narration (one clip per beat -> shorts/out/vo/<beat>.mp3)
#    beats: hook chip terminal energy data vault ledger outro
# 2) measure it -> timeline
.venv/bin/python measure_voice.py --vo ../out/vo --pad 0.5

# 3) optional look-dev
python contact.py

# 4) render frames (2 workers, ~1.4 s / frame at 810x1440)
python render_short.py --timing timing.json --out ../out/build --w 810 --h 1440 --fps 30 --workers 2

# 5) score + mix
python audio.py --timing timing.json --vo ../out/vo --out ../out/build/mix.wav

# 6) final cut
python assemble.py --build ../out/build --out ../out/tap_your_card.mp4
```

## 4. The film

**Topic:** *What actually happens when you tap your card?* — a personal-finance
curiosity loop (the niche of this repo) with the Zack-D anatomy-doc pacing.

| # | Shot | Beat (curiosity loop) | Camera |
| --- | --- | --- | --- |
| 1 | `hook` | "When you tap your card, your money does not move. Not one single cent." | slow push-in on the card, coins drifting |
| 2 | `chip` | "In the two seconds after the beep, your card turns into a tiny radio." | macro, NFC rings expanding |
| 3 | `terminal` | "The chip has no battery. It steals power from the machine, just to whisper." | card taps the terminal, beep flash |
| 4 | `energy` | "That whisper is an encrypted code, different every single time you pay." | extreme macro, contact bars glowing |
| 5 | `data` | "The terminal asks your bank one question: can this person pay?" | floating data plates |
| 6 | `vault` | "And your bank does not open a vault. It just edits a number." | vault wheel spinning |
| 7 | `ledger` | "Because your money was never sitting in a box with your name on it." | glowing ledger wall + coins |
| 8 | `outro` | "It is a promise. And when the promise breaks, that is when a bank dies." | pull-back, card spin |

House rules borrowed from the skill's `references/beat-layer.md`:
one curiosity loop per line, a cut every 2–4 s, camera motion alternating
push-in / macro / tilt, and a hard impact (zoom punch + sub-bass hit) on every
cut.

## 5. Swapping the topic

1. Rewrite the 8 `narration` lines in `beats.json` (keep ≈2.5 words/second).
2. Regenerate the VO clips, re-run `measure_voice.py`.
3. Adjust / add shot functions in `scene.py` (`SHOTS` maps beat → shot).

Everything else (timeline, captions, score, assembly) adapts automatically.

## 6. Feeding the upload pipeline

`shorts/out/*.mp4` is gitignored on purpose. To let the existing GitHub Actions
pipeline pick the short up, copy it into `videos/` (or Drive `Raw_Videos`); the
next run will OCR the first frame, score it with Gemini and schedule it.

# Hiccup Town — build report

Vertical 9:16 blocky-toy short built from the **Roblox skills → blocky-shorts** skill
(`_ In This Town _ Claude Skill File.zip` in the Drive folder *Roblox skills*).

**v2 (current)** — `out/hiccup_town_v2_1080p.mp4`, 1080×1920, 30 fps, 34.63 s (1039 frames),
H.264 High + AAC 192 kbps, no watermark.
Drive: https://drive.google.com/file/d/1GMJfxbgrrARiVdTVl9Z0Zl0i0sr0HQLt/view

v1 (superseded) — `out/hiccup_town_1080p.mp4`, 32.77 s.

### What changed in v2 (after studying the reference pack)
Source material studied: Drive folder **In the town**
(`12omLp1o71BisPGW6k_92yXZsRtzjDhd-`) — `The_Town_That_Counts_To_Ten_FINAL_1080x1920.mp4`
(80 s, 1080×1920) frame-sampled every 4 s, its
`CHARACTER_SHEET_The_Town_That_Counts_To_Ten.png`, plus the docs in
`" In This Town " Skill Files` (`Claude Skill Guide.docx`,
`If You Want to create with roblox studio then read this.docx`).

| Reference trait | v2 implementation |
| --- | --- |
| chunky-wide bodies, thin legs, big head | `character()` rebuilt: torso 0.88×0.545×0.44, legs 0.175, head 0.64 |
| glossy eyes (white sclera, dark pupil, specular dot) | `_face()` with unshaded (`glow`) eye boxes; 8 expression presets |
| soft front lighting, characters bright | light vector flipped to the camera side + ambient 0.74 |
| depth/haze, colour-graded dusk | `Scene3D(haze=…, haze_from=12, haze_to=46)` per mood |
| colourful village (lilac / mint / coral / cream houses) | `set_street()`: two rows of houses with awnings, windows, doors, chimneys, kerbs, crosswalk, hydrant, lamps, trees, hills |
| small uppercase captions, one yellow word | `cap_plan()`/`cap_image()`: size 23, stroke 2.4, y 0.815, highlight in `(245,201,59)` |
| title card + end card with red rule | `title_card()` (grid + glow + HICCUP/TOWN + red line + "A BLOCKY SHORT"), `end_card()` |
| punch-in cuts inside long shots | `CamKeys.resolve(cut=0.86)` hard cut at 52% of any shot longer than 1.9 s |
| framing = focus point + distance | `CamKeys` rewritten as `(u, fx, fy, fz, dist, yaw, pitch, fov)` |

## 1. What the skill asked for, and how it was met

| Skill rule (`SKILL.md`, `references/*.md`) | How this build follows it |
| --- | --- |
| vertical 9:16, 1080×1920 | design space 540×960, supersampled 3× → 1620×2880 canvas, LANCZOS down to 1080×1920 |
| blocky toy characters, flat-lit boxes | `boxes.py`: cuboid world, per-face culling, painter sort, lambert+ambient shading |
| "In this town, when you…" premise + deadpan button | Hiccup Town: hiccups shift you one step left; ends "That was three years ago. They're still two towns over." |
| script → VO → timing → frames → mix → encode | `story_town.py` → `voice/*.mp3` → `build_audio.py` (`story/timing.json`) → `render_town.py` → ffmpeg mux |
| captions 1–3 words, one highlighted word | `cap_plan` + `draw_captions`: word-by-word pop-in, highlight in yellow/teal/pink, stroked |
| cut every 0.5–1.5 s, every shot moves | 14 shots with moving camera keys **plus** a hard punch-in cut inside every shot longer than 1.9 s |
| pop-in graphics | hiccup puff bursts, ban stripes stamped on the mayor's sign, soda can lid flipping open |
| 27 SFX from the skill's `assets/sfx` | placed per shot cue in `story_town.py` (`sfx=[(u, "pop"), …]`) against the shot timeline |
| loudness target | `loudnorm=I=-14:LRA=9:TP=-1.5` (measured mean −14.7 dB, peak −1.5 dB) |

## 2. Why the skill's own renderer was not used

The skill renders with Three.js in headless Chrome (`engine/`, `scripts/render.mjs`,
puppeteer-core). This sandbox has **no Chrome and no GUI system libraries**
(`libnss3`, `libgbm`, `libatk` … all absent, no root apt), so that path cannot run.
The look was re-implemented with Pillow instead: `boxes.py` + `scenes_town.py`.

## 3. Pipeline files

| file | role |
| --- | --- |
| `boxes.py` | camera (yaw/pitch/fov, near-plane clipping), `Scene3D`, blocky `character()` with poses (walk/run/jump/point/hiccup/cheer/hold/strain) and expressions, props (`house`, `tree`, `lamp`, `desk`, `chair`, `podium`, `sign`, `crowd`, `hills`) |
| `scenes_town.py` | 5 sets (`town`, `classroom`, `clinic`, `field`, `plaza`) and 14 staged shots |
| `story_town.py` | 14 narration lines, 7 VO clips, per-shot camera keys, caption chunks, SFX cues, end card |
| `build_audio.py` | splits each VO clip at its longest pause, writes `story/timing.json`, places SFX, synthesises the 104 BPM bed, ducks it under the voice, loudness-normalises to `out/master.wav` |
| `render_town.py` | frame renderer (sky per mood, vignette, grain, captions), rawvideo pipe into x264 |

## 4. Shot list (as timed)

1. kid walks the street → hiccup puff
2. hiccup slides him left
3. "one kid found a cheat code" (teacher behind)
4. pop quiz — classroom
5. dentist — clinic, hiccup in the chair
6. final race — field, crowd, finish line
7. a baby hiccups (dusk)
8. the crowd drifts left together
9. the mayor bans hiccups (podium, sign, red ban stripes)
10. everybody holds their breath a week
11. somebody opens a soda (classroom)
12. the whole town hiccups at once (screen shake)
13. three years later, dusk street
14. button: "they're still two towns over"
15. end card: HICCUP TOWN / part two tomorrow

## 5. Reproduction

```bash
python -m venv .venv && .venv/bin/pip install pillow numpy imageio-ffmpeg
python -c "import imageio_ffmpeg as f; open('/tmp/ffpath','w').write(f.get_ffmpeg_exe())"
cd projects/roblox-town
../../.venv/bin/python build_audio.py          # timing + SFX + bed -> out/master.wav
SCALE=3.0 ../../.venv/bin/python render_town.py --out out/video_only.mp4
$(cat /tmp/ffpath) -i out/video_only.mp4 -i out/master.wav \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k \
  -af apad -shortest -movflags +faststart out/hiccup_town_1080p.mp4
```

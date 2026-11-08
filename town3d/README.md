# Past Detour: "Skyline Town" — procedurally-coded 3D short

This is a **detour from the YouTube auto-upload pipeline's actual job** (the
pipeline only schedules/uploads already-finished videos — see the repo
README). The user asked, in-chat, to reverse-engineer 4 reference videos
sitting in their Google Drive folder **"In the town"** and turn the findings
into one original, fully rendered short, built by **coding an actual 3D
scene** (real geometry + camera + lighting), not AI-generated still images.

## What was analyzed

4 vertical (576×1024) reference clips, ~2–2.5 min each, downloaded from
Drive folder `In the town` (TikTok watermark `@zaylento.yt` baked into the
source frames). Analysis method: ffmpeg contact-sheet frame sampling (no
audio transcription tool was available, so dialogue/captions were read
directly off the burned-in on-screen caption text visible in frames — this
is an approximation, not a verified transcript).

Observed shared production DNA across the 4 clips:
- **Visual style**: blocky/voxel "Roblox-avatar" 3D render, flat bright
  colors, simple geometric buildings and cube-headed characters.
- **Captions**: one word at a time, bold condensed font, yellow fill with a
  thick black stroke, centered in the lower-middle of frame, tightly timed
  to narration.
- **Camera**: mostly simple pans/push-ins/tilts, no complex rigs.
- **Narrative formula**: an inequality/mystery hook ("ground level" vs.
  "elite/above" worlds, hidden rooms, buttons/prices as stakes), escalation,
  a twist reveal, a cliffhanger or lesson close.
- **Themes seen**: billionaire sky-towers vs. tiny ground houses; a golden
  elevator with a priced button and a mysterious owner; a prank/embarrassment
  game-show; a post-apocalyptic luxury bunker for "kings" while a town
  fends for itself outside.

Only a lightweight version of the "reverse-engineering" analysis was done
(contact sheets + still-frame reading, no frame-by-frame forensic report, no
audio waveform/spectrogram analysis — those tools were not available in this
environment). This was a deliberate scope cut to prioritize actually
shipping a finished, original rendered video quickly, as asked.

## What was produced

**"Skyline Town"** (~73s, 720×1080, vertical) — an original wealth-gap
parable fitting this channel's "personal finance and business" niche:
Maya, who lives at ground level where rent eats half her paycheck, saves for
six years to afford the one elevator button up to the billionaires' floating
sky-city — only to find an almost-empty room and a sign that irony is the
real price of admission. Closes on a real, sourced statistic (U.S. Federal
Reserve / Visual Capitalist: the top 1% hold roughly 31% of national wealth
as of 2024–2025) tying the fictional story back to the channel's niche.

Script, characters, environments, and narration wording are original —
no sentences, jokes, character designs, or shot sequences were copied from
the reference clips.

## How it was rendered (no AI images, no Blender dependency)

`engine.py` is a ~200-line from-scratch software 3D renderer: perspective
projection, a `look_at` camera, per-face flat shading against a directional
light, backface culling, and painter's-algorithm depth sorting, rasterized
with Pillow. `figures.py` builds every prop (houses, towers, the golden
elevator, voxel people, furniture, clouds) out of that engine's `Box`
primitive. `scenes.py` defines the 8 shots with start/end camera keyframes.
`render.py` renders every frame procedurally, burns in word-synced captions
(timed proportionally to each narration clip's real duration), and pipes
frames straight into ffmpeg (via `imageio-ffmpeg`) as H.264, then muxes the
8 narration clips.

## Reproduce

```bash
python3 -m venv .rendervenv
.rendervenv/bin/pip install imageio-ffmpeg pillow numpy
.rendervenv/bin/python town3d/render.py            # -> town_render/video_only.mp4
# then concat town_audio/*.mp3 and mux (see the render steps in commit history)
```

Narration audio (`town_audio/*.mp3`) is generated speech from a voice
selected by the user via Arena's voice tool, not a competitor voice clone.
The caption font is Anton (SIL Open Font License, bundled at
`town3d/assets/`).

## Caveats

- Word-level caption timing is estimated (proportional to character count
  per word within each clip's real duration), not phoneme-aligned.
- The wealth-share statistic is from public Federal Reserve data reported by
  Visual Capitalist/Investopedia (2024–2025); it is a real, sourced figure,
  not fabricated, but normal diligence applies before using it elsewhere.
- No views/retention/virality is implied or promised.

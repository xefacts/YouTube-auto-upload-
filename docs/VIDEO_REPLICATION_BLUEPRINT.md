# Video Replication Blueprint — Exact Same-to-Same Claude Coding Videos

**Source:** Google Drive folder **"New content"** (`1N__5o7eEUjOI5Ebk1FkkGxdTWPYq7opL`) — 12 files analyzed on 2026-11-16.
**Purpose:** One agent-ready document. Any coding agent (Claude, or any agent with shell + code tools) follows this file and produces **the same type of videos, shot-for-shot in style, camera, characters, sound and render pipeline** — without guessing.

> **How to use this document:** Pick ONE engine (§4–§7). Follow its runbook (§16) stage by stage. Copy the prompts in §17 verbatim. Never invent a new look — the style is fixed, only the story changes.

---

## Table of contents

1. [What was analyzed (file inventory)](#1-what-was-analyzed-file-inventory)
2. [The 4 engines + 2 worked examples (map)](#2-the-4-engines--2-worked-examples-map)
3. [Forensic analysis of the 3 MP4s](#3-forensic-analysis-of-the-3-mp4s)
4. [Engine A — aiTrends 2D Studio (16:9 / 9:16 stick-figure cinematic)](#4-engine-a--aitrends-2d-studio-169--916-stick-figure-cinematic)
5. [Engine B — cartoon-audio-short (1080×1920 bean-head cards in 3D world)](#5-engine-b--cartoon-audio-short-10801920-bean-head-cards-in-3d-world)
6. [Engine C — 3d-story-shorts / Remotion (720×1280 true-fact mini-movie)](#6-engine-c--3d-story-shorts--remotion-7201280-true-fact-mini-movie)
7. [Engine D — animated-3d-story-video (Chicago-lifted style, 720×1280)](#7-engine-d--animated-3d-story-video-chicago-lifted-style-7201280)
8. [Worked examples (copy these exactly)](#8-worked-examples-copy-these-exactly)
9. [Camera shoots — master reference (all moves, numbers)](#9-camera-shoots--master-reference-all-moves-numbers)
10. [Character master reference (3 systems compared)](#10-character-master-reference-3-systems-compared)
11. [World / set building reference](#11-world--set-building-reference)
12. [Timing & voice pipeline](#12-timing--voice-pipeline)
13. [Sound design (music, SFX, mix levels)](#13-sound-design-music-sfx-mix-levels)
14. [Render pipeline (commands, speed, resume)](#14-render-pipeline-commands-speed-resume)
15. [QC checklists](#15-qc-checklists)
16. [Agent runbook — step by step (per engine)](#16-agent-runbook--step-by-step-per-engine)
17. [Copy-paste prompts for the agent](#17-copy-paste-prompts-for-the-agent)
18. [New project scaffolding (schemas)](#18-new-project-scaffolding-schemas)
19. [Integration with this repo](#19-integration-with-this-repo)
20. [Troubleshooting & traps](#20-troubleshooting--traps)
21. [Appendix — code snippets, hashes, file tree](#21-appendix--code-snippets-hashes-file-tree)

---

## 1. What was analyzed (file inventory)

Drive folder **New content** — 12 items (10 unique + 2 duplicates):

| # | File | Type | Size | What it is |
|---|------|------|------|------------|
| 1 | `2e7c07ca3cf09758262010b94ae65cfd.mp4` | video/mp4 | 6,674,373 B | Finished video — 1024×576, 30 fps, 64.5 s (see §3) |
| 2 | `f12c5efadf33b2c287aa119924de0848.mp4` | video/mp4 | 7,325,466 B | Finished video — 1024×576, 30 fps, 93.0 s |
| 3 | `f4345b115fadeb6276b150e881a48853.mp4` | video/mp4 | 7,002,453 B | Finished video — 1024×576, 30 fps, 80.5 s |
| 4 | `SKILL.md` (14,934 B) | text/markdown | 14,934 B | **cartoon-audio-short** skill — full spec for Engine B |
| 5 | `3d-story-shorts.zip` | application/zip | 458,984 B | **3d-story-shorts** skill + Remotion template + example (Engine C) |
| 6 | `3d-story-shorts (1).zip` | application/zip | 458,984 B | **Byte-identical duplicate** of #5 — ignore |
| 7 | `animated-story-video.skill.zip` | application/zip | 5,231 B | **animated-3d-story-video** skill, SKILL.md only (Engine D) |
| 8 | `cartoon-short-kit.zip` | application/zip | 444,936 B | **cartoon-short-kit** engine + Soldier example (Engine B kit) |
| 9 | `cartoon-short-kit (1).zip` | application/zip | 444,936 B | **Byte-identical duplicate** of #8 — ignore |
| 10 | `hoover_dam_short.zip` | application/zip | 6,124,522 B | **Full worked project** — Hoover Dam, 13 shots, 60.29 s, with `voiceover.wav` (Engine C in production) |
| 11 | `aitrends-2d-studio (2).plugin` | application/x-zip | 118,134 B | **aiTrends 2D Studio plugin** — 5 skills + kit (Engine A). 61 files, 266 KB uncompressed |
| 12 | `Cartoon audio short - Claude` | multipart/related (MHTML) | 3,341,587 B | Saved Claude chat (2026-11-08) — **Pitch Drop** build proof: 48 s vertical 1080×1920, flat-2D fallback, music −6 dB, −15 LUFS |

**Duplicates to ignore:** `3d-story-shorts (1).zip` and `cartoon-short-kit (1).zip` are exact copies. Keep one of each.

**Already in this repo (do not re-download):**
- `aitrends-2d-studio/` — Engine A kit, already installed (render.mjs, engine/, audio/, tools/, examples/, projects/). The plugin's `kit/render.mjs` differs slightly from the repo copy — the repo copy is the newer parallel-worker version; keep the repo copy.
- `google_drive/` — local copies of the Drive files (downloaded for analysis). **Do not commit** the zips/MP4s — see §19.
- `past_detour_emu_1932/`, `past_detour_gold_1971/`, `projects/rick-outbreak-3d/` — earlier 2D/3D experiments (image-master + cartoon renders). Useful as extra references, not part of the 4 engines.

---

## 2. The 4 engines + 2 worked examples (map)

The folder contains **four different code-rendered video systems**. They share the same philosophy — *every frame drawn by code, no image/video AI, voiceover is never re-timed* — but differ in look, aspect and stack:

| Engine | Skill / kit | Output | Stack | Characters | When to use |
|--------|-------------|--------|-------|------------|-------------|
| **A — aiTrends 2D** | `aitrends-2d-studio.plugin` → `skills/make-2d-video` + kit | **16:9 or 9:16, 720p–4K, 24 fps** | HTML canvas + Three.js, headless Chromium, ffmpeg | Black stick figures + rim light, 1 signature colour each | Long explainers, What-If, finance/business, any voiceover 30 s – 10 min |
| **B — cartoon-audio-short** | `SKILL.md` + `cartoon-short-kit.zip` | **1080×1920, 30 fps, 20–60 s** | three.js in headless Chromium (no Remotion, no GPU) | Flat 2D bean-head cards (plum outlines) in painted 3D world | Vertical Shorts, voiceover-driven, exact word sync |
| **C — 3d-story-shorts** | `3d-story-shorts.zip` (template + example) | **720×1280, 30 fps, 45–65 s** | Remotion + React Three Fiber + three.js | Flat 2D cartoon people in busy 3D worlds, one-word captions | True-fact mini-movies, YouTube Shorts / TikTok |
| **D — animated-3d-story-video** | `animated-story-video.skill.zip` (SKILL.md only) | **720×1280, 30 fps, 39–65 s** | Remotion + ThreeCanvas + postprocessing | Flat 2D people (round head, tie, hat/glasses variants) in procedural 3D | "Something physically big changes" stories (city rises, river moved) |

**Worked examples inside the zips (use as templates, never rebuild from scratch):**

| Example | Engine | Spec | Files |
|---------|--------|------|-------|
| **The Soldier Who Never Left** | B | 19.72 s, 8 shots, 592 frames @ 30 fps | `cartoon-short-kit/example/soldier/story.js` + `audio.py` + `stills.jpg` |
| **The Skyscraper Fixed in Secret** | C | ~46 s, 11 shots, 154 words | `3d-story-shorts/example/script.md` + `SHOTS.txt` + `final_look_frames.jpg` |
| **Hoover Dam** (full project) | C | 60.29 s, 13 shots, 186 words, `voiceover.wav` 60.33 s stereo 48 kHz | `hoover_dam_short.zip` → `hoover/` (src/, SHOTS.txt, timing.json, camera_plan.md) |
| **Pitch Drop** (Claude chat) | B (flat-2D fallback) | 48.07 s, 1080×1920, 30 fps, 20 MB, −15 LUFS | MHTML chat transcript — proves the fallback when the 3D kit is missing |

**Rule for the agent:** Start every new video from a copy of the matching template/example. Copy, then rewrite only the story files (shots, worlds, cast, audio cues). Never rebuild the engine.

---

## 3. Forensic analysis of the 3 MP4s

Parsed directly from the MP4 boxes (mvhd / tkhd / mdhd / stts / avcC / mp4a):

| File | Duration (mvhd) | Video | Audio | Size |
|------|-----------------|-------|-------|------|
| `2e7c07ca…mp4` | 64.527 s | 1024×576, 30.0 fps (15360 timescale, delta 512), H.264 High (avcC `64001f`) | AAC, 44.1 kHz stereo, 2,781 samples | 6.67 MB |
| `f12c5efa…mp4` | 93.018 s | 1024×576, 30.0 fps, H.264 High | AAC, 44.1 kHz stereo, 4,008 samples | 7.33 MB |
| `f4345b11…mp4` | 80.526 s | 1024×576, 30.0 fps, H.264 High | AAC, 44.1 kHz stereo, 3,470 samples | 7.00 MB |

**What this tells the agent:**

- All three are **16:9 landscape, 1024×576 (720p-class), 30 fps, H.264 + AAC 44.1 kHz** — the exact encode profile of the Remotion `render.bat` / `finish.sh` pipeline (`-c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart`). Reproduce this profile for every final MP4.
- Durations (64.5 s, 80.5 s, 93.0 s) match the **45–65 s Shorts band** of Engines C/D and the **15–25 shots/minute** pacing of Engine A. They are finished, muxed videos (video + audio tracks, `faststart`), not silent renders.
- The 1024×576 size is the **half-scale / preview render size** used by `stills.sh` / `render.mjs --scale 0.5` for contact sheets. For finals, render at full size: Engine A 1920×1080 (16:9) or 1080×1920 (9:16); Engines C/D 720×1280; Engine B 1080×1920.
- No embedded captions track — captions are **burned in** (Engine C one-word captions in `Full.jsx`; Engine A `captions: true` in config). Never ship a separate subtitle file unless asked.
- **To re-verify on any machine with ffmpeg:**
  ```bash
  ffprobe -v error -show_entries format=duration,size,bit_rate \
    -show_entries stream=codec_name,width,height,r_frame_rate,codec_type \
    -of default=noprint_wrappers=1 <file>.mp4
  ffmpeg -i <file>.mp4 -vf "fps=1/10,scale=320:-1,tile=6x5" -frames:v 1 sheet.png
  ```

---

## 4. Engine A — aiTrends 2D Studio (16:9 / 9:16 stick-figure cinematic)

**Plugin:** `aitrends-2d-studio.plugin` → 5 skills + kit (61 files). Already installed in this repo as `aitrends-2d-studio/`.

### 4.1 Skills (stage commands)

| Skill | Trigger | What it does |
|-------|---------|--------------|
| `make-2d-video` | "make a 2D video from this voiceover" | Full pipeline Stages 1–8 (this section) |
| `/new-video` | "set up a video, timestamp it" | Stages 1–4: intake, install check, timeline, story breakdown |
| `/video-styles` | "show me style options" | Stage 5: render 5-style grid, lock `config.json → style` |
| `/render-video` | "build the scenes / render" | Stages 6+8: build shots in batches, preview, final render |
| `/video-sound` | "add music / sound" | Stage 7: music plan, SFX, ambience, mix + mux |

### 4.2 The look (style bible — do not drift)

> Pure black stick figures (circle head, thick round-capped line limbs) with a **thin rim-light edge** on the light side, acting in **low-key cinematic flat-shaded vector sets**: one strong light per scene, deep purple/navy shadows, warm amber highlights, dust/rain/glows, shallow depth of field, slow camera drift, letterbox bars, film grain, vignette. One signature colour per character. Giant face close-ups, freeze-frames, glowing numbers, navy blueprint diagrams, low-poly 3D shots. *"A stick-figure film lit by a cinematographer."*

- **Characters (`engine/rig2d.js` → `drawFigure`):** head r=26 rig units, torso 15, limbs 11–13 round caps, foot stubs, no fingers except inserts. Near arm/leg pure ink; far arm/leg `inkFar` (dark purple-grey) — automatic. **Rim light on every lit figure:** `rim: { color: M.rim, dir: [dx,dy] }`, width 4–5 @1080p. Backlit → `[0,-1]`; light from left → `[-1,-0.3]`. **Never skip the rim.**
- **Signature items (exactly one saturated colour per recurring character, fixed all video):** red-orange hoodie `#d64a33`, yellow cap `#f2c21a`, pink beanie `#f29ac0`, green cap `#3fb950`, blue tee `#3a6ea5`, purple tracksuit `#8a5ad6`, white lab coat + round glasses (scientist), black trench + fedora + sunglasses (mentor/antagonist, half in shadow), headband (athlete), ponytail/bun. Kids: `kid: true` (72% size). Background crowds: plain ink, no colour.
- **Faces:** minimal — white dot/ring eyes, simple white mouth, occasional brows. Expressions change **on the beat of the words**: `neutral, smile, happy, joy, surprised, shocked, scared, worried, nervous, angry, determined, sad, cry, smirk, sleepy, thinking, confused, awe`. Blink every 2.5–4 s (`blink: (t % 3.1) > 3.0`, different period per character). Talking only for quoted lines: `talk: talkAmount(globalT, lineStart, lineEnd)` + 2–3 faint `FX.rings`. Narrator is never lip-synced.
- **Acting:** poses must read as silhouettes. `POSES` + `posesAt(t, [[0,'stand'],[0.6,'point']])`, blend ~0.3 s, wrap standing/sitting in `breathe(pose, t, 1, seed)` — nobody frozen (except freeze-time moments). Walk `walkPose(phase,{run})`, walk ≈160 u/s × s, run ≈420 u/s × s, phase = t×2π×0.9 (walk) / ×1.6 (run). Super-speed: `trail: {count:4, dx:-40}`.
- **Scale:** wide `s≈0.8–1.2` (figures 15–25% frame height); medium `s≈1.5–1.8`; close-ups via `bigFace` (radius 280–360 @1080p, head slightly below centre, shoulders cropped, rim crescent). Always grounded with contact shadow, never floating.
- **Sets:** flat shapes + soft linear gradients, no outlines/photos/clip-art/emoji. Texture only: floor lines, mullions, blinds, lit-window grids. **Value structure:** 60–75% dark mid-tones (`shade(c,-0.3)`), 1–3 bright accents (window, lamps, screens, floodlights, sunset). **Stage black figures in front of the brightest area.** Depth layers via `layer(g,cam,depth,fn)`: sky 0.1–0.2 → skyline 0.3–0.4 → back wall 0.5–0.6 → floor/props 0.8–0.9 → characters 1.0 → blurred foreground 1.5–1.8 (`blurLayer(g,8–14,fn,cam,1.7)`). Most medium shots have a soft foreground (glassware, plant, railing, crowd heads, shoulder).
- **Windows are the signature element.** Large windows + mullions + sky gradient (sunset/golden/night skyline), sun/moon glow, sometimes blinds. Night streets: facades + warm lit windows + steps + lamp posts with light cones + parked cars + round-silhouette trees.
- **Sets anchored to** `GY = E.H * V(0.8, 0.68)` (ground line) and `CX = E.W/2`. Extend walls/floors/skies past the frame so camera moves never reveal edges.
- **Atmosphere in nearly every shot:** `FX.dust` indoors, `FX.rain` storms/night, `FX.drops` time-stop, stars, `FX.lensStreak`, `FX.godRays`, fog bands.
- **Light & colour:** `M = mood('night')` → `sky[], ambient, key, rim, wall, floor, dark, practical, grass, road, fog`. Take every colour from `M`, `S()` or cast — **no hard-coded colours** (style switching breaks otherwise). One key light per shot, shown on screen + spilled: `glow()` at source, `FX.pool()` on floor, `FX.lightCone()` from lamps, `FX.godRays()` from windows/suns. Global grade (lift/gamma/gain, contrast, sat, vignette, grain, bloom) applied automatically — this is why mood colours matter.
- **5 styles (`engine/styles.js` → `STYLES`):**
  - **dusk** — Cinematic Dusk (default): mauve shadows, amber key, cream rim.
  - **midnight** — Midnight Blue: cold navy, blue-white rims, sodium practicals (night/rain/thriller).
  - **golden** — Golden Hour: warm orange + teal, big sun glows (uplifting/nostalgic).
  - **neon** — Neon Noir: deep blacks, magenta + teal rims, strong bloom (sci-fi/tech/crime).
  - **storybook** — Soft Storybook: pastel, low contrast (family-friendly).
  - Custom style: copy closest preset in `STYLES`, adjust `moods` overrides + `grade {lift,gain,gamma,sat,contrast,vignette,grain,bloom}` + `ui` colours + `rimWidth`. Re-render `--styles <newid>,<closest> --at …` to compare.
- **Fonts:** Fredoka Bold (titles/big lines, ALL CAPS), Nunito (body/captions), Playfair Display italic (end-screen question). Via `@fontsource/*` — missing fonts show as serif defaults (see §20).
- **Logical units:** 16:9 → 1920×1080; 9:16 → 1080×1920. Use `V(h,v)` for every aspect-dependent value.

### 4.3 Shot vocabulary (use all, roughly these proportions)

| # | Shot type | Share | Notes |
|---|-----------|-------|-------|
| 1 | Establishing wide | ~10% | Location + small figures, slow push. Opens each new scene. Often 3D. |
| 2 | Medium two-shot | ~25% | Side view, facing each other, conversation/action. |
| 3 | Over-the-shoulder | ~10% | Big blurred silhouette foreground (`blurLayer`, depth 1.6), other sharp. |
| 4 | Giant face close-up (`bigFace`) | 10–15% | Reactions, realisations, "you" moments, dialogue. Background blurred + darkened. |
| 5 | Insert / macro | ~10% | Hands, phone, watch, ball, cup, door handle. Big, simple, blurred bg. |
| 6 | Top-down / diagram | ~5% | Table from above, dotted trajectory + timing label. |
| 7 | Freeze frame / time-stop | 1–3 per video | Particles hanging, cool tint, corner badge (`100x`), slow rings, slow rotation, only hero moves. Enter with `flash` + `freeze` SFX. |
| 8 | 3D orbit / fly-through | ~1 per minute | Stadiums, streets, halls via `three-kit`. Same figures + palette. |
| 9 | Data card / UI | as needed | Every number the narrator says appears and animates as spoken. |
| 10 | Blueprint diagram | explanation beats | Navy grid, light-blue line art, gold highlights, labels synced to words. |
| 11 | Title card | after cold-open hook | Glowing caps title over cinematic wide. |
| 12 | End screen | final shot | Serif-italic question, comment bubble, subscribe pill, whole cast lined up. |

**Pacing:** 15–25 shots per minute. Median shot 2–3.5 s. Fast action 0.8–2 s cuts (split one phrase into several shots). Emotional/dialogue holds 4–8 s. Never >~10 s without new action/camera move. 1–3 freeze-frames per video. ~1 3D shot per minute.

### 4.4 Camera (never fully static — every shot moves)

- Slow push-in: `z` 1.0 → 1.05–1.10 over the shot. Lateral drift `x` ±20–60. Slow pull-out for reveals. Slight roll `r` ±0.02 for unease. `shake(t, amp)` for impacts. `ease.inOut` for moves, `ease.out` for snaps.
- **Transitions:** hard **cut** default (≥80%). **flash** (white) into freeze/time-stop/superpower/realisation. **dip** (black) for time skips/chapters. **fade** for gentle/dreamy + title. **whip** for energetic jumps. **zoom** to dive into explanation.
- **Continuity:** same outfits, same screen direction (hero left facing right in conversation), same set geometry for every shot in a scene.
- **Letterbox (`bars`):** `wide` (2:1) default. `scope` (2.39:1) for drama (title, freezes, climaxes, intense close-ups). `none` for full-frame UI/blueprint. Bars animate smoothly between shots.

### 4.5 On-screen graphics

- Numbers animate as spoken (`wordTime()` sync). Data cards, callouts, dimension lines, compare bars, meters, badges, bubbles, blueprint strokes — all in `engine/ui2d.js`.
- Text short, inside safe area, legible at phone size. Numbers match narration exactly.
- Captions: default **on for 9:16, off for 16:9**. Burned in via `captions` flag + `captionStyle {y,size,max}`.

### 4.6 Engine API (exact)

```js
// 2D shot
import { E, V, registerShot, mood, layer, blurLayer, veil, ease, prog, key, wordTime, talkAmount } from '/engine/core.js';
import { drawFigure, POSES, posesAt, breathe, walkPose, bigFace, headPos } from '/engine/rig2d.js';
import * as FX from '/engine/fx2d.js';
import * as UI from '/engine/ui2d.js';
import { lab } from '../sets/lab.js';
import { MAX, DOC } from '../cast.js';

registerShot('s013', {
  draw(g, t, info) {  // t = seconds into shot; info = {dur, globalT, p, line, shot, ...params}
    const cam = { z: 1 + 0.06 * ease.inOut(t / info.dur), x: -30 };
    const { GY, M } = lab(g, t, cam);
    layer(g, cam, 1, g => drawFigure(g, {
      x: E.W/2 - 40, y: GY, s: 1.4, facing: -1, outfit: DOC,
      pose: breathe(posesAt(t, [[0,'stand'],[0.4,'point']]), t),
      expr: 'smile', rim: { color: M.rim, dir: [0,-1] }
    }));
    FX.dust(g, t);
  }
});

// 3D shot (kind:'3d', T = three-kit)
registerShot('s008', {
  kind: '3d',
  init(T, info) { const st = T.stage({ mood: 'golden' }); /* build */ return { stage: st }; },
  draw(s, t, info, T) {
    T.orbit(s.stage.camera, t, { target:[0,1,0], radius:6, height:2.5, from:-0.8, to:0.3, dur: info.dur });
  },
  overlay(g, t, info, s) { /* 2D graphics on top */ }
});
```

- Every `.js` under `scenes/` loads automatically (files starting `_` skipped). Engine imports absolute (`'/engine/core.js'`), project files relative (`'../cast.js'`).
- `core.js`: `E (W,H,PX,fps,vertical,cfg,words,shots)`, `V(h,v)`, `clamp lerp prog ease{linear,in,out,inOut,sine,outBack,outElastic} key(t,[[t,v],…],ease) mixVal rng(seed) noise(x,seed) shake(t,amp,freq,seed) talkAmount(globalT,from,to) wordTime(word,afterGlobalT)`, colour `rgb css mix alpha shade`, `mood(name) S() setStyle`, draw `rr seg poly circle ring linGrad radGrad glow fillRect backdrop veil text measure FONTS`, camera `layer(g,cam,depth,fn) blurLayer(g,amount,fn,cam?,depth?)`, `registerShot getShot`.
- `rig2d.js`: `drawFigure(g,{x,y,s,facing,pose,rot,outfit,expr,talk,blink,look:[x,y],rim:{color,dir,w},dim,alpha,prop,shadow,trail})`. Poses: `POSES.{stand,relaxed,talk,explain,point,pointUp,wave,cheer,handsOnHead,crossArms,think,shrug,holdFront,phone,reach,sad,facepalm,ready,crouch,sit,sitBack,kneel,lie(+rot),dive(+rot),kick,jump,fall}` + `posesAt, blendPose, breathe, walkPose(phase,{run})`, `face(g,x,y,r,{expr,talk,blink,look,front})`, `bigFace(g,cx,cy,r,{outfit,expr,talk,blink,look,rimColor,rimSide,tilt})`, `headPos(o)→[x,y,r]`, `soccerBall(g,x,y,r,rot)`. Props: `phone,ball,paper,cup,paddle,pointer,tablet,flashlight`. Outfit: `top: hoodie|labcoat|trench|jersey|tshirt|suit|dress|tracksuit|none, color, color2, legs, head: cap|capBack|beanie|fedora|headband|visor|hood|ponytail|bun|curly|spiky|none, headColor, face: glasses|sunglasses, gloves, number, kid`. Custom pose: plain object with 11 points, e.g. `{...POSES.sit, hF:[34,-188]}`.
- `fx2d.js`: `rain drops dust snow stars fog sun moon godRays lightCone pool lensStreak sparkle lightning speedLines rings skyline hills clouds tree pine lampPost windowFrame facade door chair stool counter screen bed clock floorLines crowd`.
- `ui2d.js`: `titleCard bigLine badge readout callout dimension dataCard compareBars meter blueprint bpStroke lineFigure bubble endScreen captions`.
- `three-kit.js` (`T`): `T.stage({mood,fov,fog:[near,far],sky,keyPos,keyIntensity,ambient,bloom}) → {scene,camera,composer,sun,add(...objs),render(),dispose()}`. Builders: `box cyl cone sphere plane ground(w,d,color,tex) planks tiles windowPane(w,h,{glowColor,cols,rows,power,interior}) shaft(w,len,color,opacity) building(w,h,d,{color,win,lit}) tree3D pine3D crowd3D({rows,perRow,width,step,rise,colors}) figure3D(outfit,{rim,pose,s})→.setPose(pose)`, `mat basic canvasTex`, cameras `orbit(camera,t,{target,radius,height,from,to,dur})` and `dolly(camera,t,[[t,{pos,look,fov}],…])`. Units metres, figure ~1.7 m facing +x. Same grade/bars/grain as 2D. Keep exposure moody: windows/lamps brightest, floor dark.

### 4.7 Sound (Engine A)

- `audio/mix.py` builds soundtrack from `story/shots.json`. **Music ducked −9 dB, ambience −5 dB under voice. Master normalised to −14 LUFS** (YouTube) or `config.loudness`.
- **Music plan** (`"music"` in shots.json): contiguous `{start,end,mood,intensity}`. Moods: `mystery, tension, action, wonder, hopeful, sad, triumph, playful, calm, dark, epic`. Intensity 0–1 (adds pulse/arps/drums). Change at story turns, every 30–90 s. Audition: `python audio/music.py --mood tension --intensity 0.7 --dur 20 --out build/test_tension.wav`. User track: `config.music.file = "input/music.mp3"` (loops/trims, end fades). `config.music.gainDb` default −17 vs voice.
- **SFX cues** per shot: `{"at": <s from shot start>, "name": "<effect>", "gain": -8}` (+ optional `dur,seed,pitch`; `name` may be user WAV/MP3 path). Library (`python audio/sfx.py --list`, demo `--demo build/sfx_demo`): `whoosh, swish, impact, hit, riser, slowmo, freeze, tick, clock, heartbeat, pop, blip, counter, ding, shimmer, stinger, footstep, kick, whistle, carpass, phonebuzz, phonering, cheer, applause, murmur, rain, thunder, wind, roomtone, city, hum, powerup, glitch, flash, buzz`. Conventions: whoosh/swish on whips/fast moves; pop/blip on graphics; counter under ticking numbers; riser 1–2 s before reveal → impact/stinger on it; slowmo into slow-mo; freeze on time-stop; ding/shimmer for realisations; hit/kick/footstep on contact. Gains: UI −12…−16, normal −6…−10, big −3…−6. Max ~2 cues at same instant.
- **Ambience** per shot: `{"name":"rain|wind|city|roomtone|murmur|hum","gain":-20}` (looped, 0.4 s fades). Use on most shots, −18…−28.

### 4.8 Render commands (Engine A)

```bash
# style grid (Stage 5)
node render.mjs --project projects/<slug> --styles dusk,midnight,golden,neon,storybook --at <t1>,<t2>,<t3> --scale 0.5
# contact sheet (Stage 6 QC)
node render.mjs --project projects/<slug> --sheet --scale 0.5
# motion check
node render.mjs --project projects/<slug> --stills t1,t2,t3
node render.mjs --project projects/<slug> --from A --to B --scale 0.5   # -> build/preview.mp4
# preview checkpoint
node render.mjs --project projects/<slug> --from 0 --to 30 --scale 0.5
# final (background for long renders)
node render.mjs --project projects/<slug> [--workers N] [--format jpeg] [--gl swiftshader]
python audio/mix.py --project projects/<slug>   # -> out/<title>.mp4
# final QC sheet
ffmpeg -i out/<file>.mp4 -vf fps=1/10,scale=320:-1,tile=6x5 -frames:v 1 build/final_sheet.png
```

- Workers default half CPU threads (max 8), each a separate Chromium. RAM ~0.6–1.5 GB/worker @1080p, more @4K. No GPU → `--gl swiftshader` (Linux default). `--format jpeg` ~1.5× faster, negligible loss.
- **Speed:** 720p on 2-thread cloud CPU ≈2 frames/s (47 s ≈10 min). 1080p ~2×, 1440p ~3.5×, 4K ~8×. Modern 8-core desktop 3–5× faster. 10-min @4K = overnight.

---

## 5. Engine B — cartoon-audio-short (1080×1920 bean-head cards in 3D world)

**Skill:** `SKILL.md` (name: `cartoon-audio-short`) + `cartoon-short-kit.zip` (engine + Soldier example).

### 5.1 The look (fixed)

> Flat 2D **bean-head cartoon cards** (canvas-drawn, plum outlines) in a colourful **3D world with black ink outlines, painted textures, depth-of-field and gliding cameras**. Output **1080×1920, 30 fps, exactly as long as the voiceover**. Voice unchanged. Music + SFX synthesized at **50% of voice level**. Proven on *"The Soldier Who Never Left"* (19.7 s, 8 shots).

- **Hard rules:** stories/characters/shots always original (never recreate another creator shot-for-shot). No real named living people as characters, no brand mascots/logos. No captions unless asked. Diegetic text (carved message, sign) OK but must read correctly (not mirrored). **Never edit or re-time the voice** — picture timed to it, every visual reaction lands **0–3 frames before its word**. Audio: music at 50% voice (−6 dB gated RMS), SFX at 50% or less, peaks capped so no hit pokes over narration. **Always mix with `mix.py`, never by hand.** No ducking/compression changing the ratio — one linear gain + peak limiter on whole mix only. Keep user informed with task list. Send stills contact sheet before long render.

### 5.2 Script formula (Stage 3)

- Narration only (no stage directions in spoken text). ~3.7 words/s: 20 s ≈75 words, 30 s ≈110, 60 s ≈220.
- 1. **Hook** (sentence 1, no setup): absurd fact. 2. **Setting** 1–2 lines: when/where/who + concrete detail. 3. **Escalation** 2–4 beats, each bigger; others doubt/mock; one exaggeration joke. 4. **Mystery/pivot**: "But when…" / "You see," + real mechanism + everyday analogy. 5. **Twist/payoff**: short, ironic, last words of video.
- Plain spoken English, contractions, 8–15-word sentences, numbers as words. Never describe what viewer already sees.
- Recording tips: one steady warm narrator; ElevenLabs works well (deep narrator, speed 1.05–1.1, stability 45–55%). MP3/WAV, natural pauses, **export without music**.
- Idea generation (Stage 2): exactly 10 ideas, each: Title (5–8 words, curiosity-driven), Hook line (paradox as fact), Twist (one line), Why it animates well (2–3 big visual moments), True or legend (documented / disputed / folklore — verify with web search, never present legend as fact). Mix eras/themes. No real living people as joke butt, nothing graphic/political.

### 5.3 Timing (Stage 4.1)

```bash
python3 timing.py voice.mp3 script.txt --out work
# -> work/phrases.json (check: pauses at sentence ends; total frames = round(duration × 30))
```

- With whisper/faster-whisper: word timestamps. Without ASR: aligns script phrases (split at punctuation) to silence-detected speech segments via DP matching syllables→duration, penalising sentence-ends inside a segment and long gaps inside a phrase. **No ASR + no script → ask for script. Claude cannot hear audio.**
- `timing.py` syllable counter: vowel-group count, trailing-e rule, digits = 2 syllables. DP allows 1–3 phrases per segment, 1–2 segments per phrase group.

### 5.4 Shot plan (Stage 4.2 — `work/PLAN.md` before code)

One row per shot: frames, words, setting, light, camera move, characters/poses/expressions, effects + SFX cue.

- Frame 0 is already the hook image. Usually one shot per phrase; merge tiny phrases into next shot. Illustrate every sentence literally; props carry jokes.
- **Vary shot sizes:** hook MCU → wide reveal → two-shot → insert close-up on key object → reaction close-up → environment move for payoff.
- **Light for beats:** day = normal, golden = decline/drama, night-blue = explanation. Time jump = 6-frame white flash.
- Twist line gets a sting (music stops, low hit, push-in with roll). Last shot's physical payoff lands on final word.

### 5.5 World (`web/main.js` — Stage 4.3)

Keep engine sections: toon materials, ink contract, `add`/`tbox`, sky, lights, cards, render targets/post, `applyLight`, `drawActors`, `swapForNd`, `renderFrame`. Replace example world between `// ---------- world ----------` and `// ---------- cards ----------`, plus story parts of `worldState()`.

- Build from primitives + painted canvas textures (`paint.js`: planks, beams, rotten wood, stone, moss/ivy, grass, dirt, plaster, roof tiles, marble, banners, carved text). New painters in same flat-with-dark-seams style.
- `tbox` for constant texel density, 2-step toon gradient, fog = horizon colour.
- Background: hills (half-buried spheres), mountains (cones + snow caps), cypress/pine trees, distant houses, painted cloud billboards.
- Set pieces (collapses, falls, doors) = pivoted groups driven by 0..1 progress from `worldAt(f)`, eased + staggered parts.
- Curved diegetic text uses planar UVs. Check not mirrored.

### 5.6 Cast (`web/roman.js` → `web/toon.js` — Stage 4.4)

- `romanFront(p, outfitKey, opts)` draws on **600×1000 design canvas, soles at y=975**. Card is **2.25 m tall**, so **1 unit = 0.00225 m**.
- Outfits in `OUTFITS` (tunic/cape/armor/helmet/hair/cap/beard/apron/dress/toga) + new headgear/props in same style.
- Arm poses: hang, spear, point, up, wave, hip, belly, temple (+swirl), lift, reach (+lift), cheek, shield, cross, thumb.
- Expressions: toon.ts FACE set + snore, stubborn, squint. Extend FACE for more.
- Rebuild after edits: `cat web/toonbase.js web/roman.js > web/toon.js`. Render character test sheet before using new designs.
- Billboards turn on yaw only, get contact blob + alpha-tested shadow, never inked by world pass.
- Card keys from `q()`-rounded values (canvas redraws only on visible change).
- Detached part (lifted helmet) = own card, aligned with `headCenter(seed)`: `y = DECK + (partY − hc) × 0.00225`.

### 5.7 Motion (`web/motion.js` — Stage 4.5)

- **Cameras:** `camFromKeys(keys, f, {kicks})`. Smootherstep glides (18–45 f), `easeOut` for reveals/whips, `path` via-points (Catmull-Rom) for curved moves. Every hold creeps, nothing static 4+ frames. 3–5° rolls on drama, 7-frame flip-shakes on impacts.
- **Continuity:** prefer continuous moves (pull back from close-up into wide, rack focus, crane through deck, push into object). Hard cut only on place/time jumps, with flash.
- **Characters never freeze:** `idle(f, seed)` on every card, `blinkAt` blinks, head bobs on stressed words.
- **Actions:** anticipation → `back` overshoot → `spring` settle. Stamp = 2-frame dip + dust puff + kick. Laughs = alternating tilt + bob.
- **Secondary motion:** banner cloth waves, leaves/dust/drips/Zzz effect cards, flowing water. Something always moves.
- **Walks:** `walk()` gives distance + step phase. Feet planted, bob 3–7%.
- **Lens:** DOF on close-ups/mediums (cInf 8–14 px), focus on eyes. Wides sharp. Racks ~14 f.

### 5.8 Look check (Stage 4.6 — before full render)

```bash
node render.mjs stills/a "5,40,..."   # stills at shot middles + transitions + key actions
python3 sheet.py stills/a stills/sheet_a.jpg
```

Fix traps: **narrow vertical frame** — horizontal half-width = d·tan(hfov/2), hfov = 2·atan(tan(vfov/2)·0.5625). At 4 m, fov 40 → ±0.8 m, so stage characters in depth. Railings/posts across faces (camera inside rail or ~2.5 m up). Camera path through houses/roofs/bushes. Foreground props <2 m. Hero hidden behind pillar. Mirrored text. Detached-part offset wrong way. Extrude groups: 0 = caps, 1 = sides+top. Missing ink: debug edge-only output. Ink radius ~2.5 px @1080. Sky counts as far depth, not a card. Send sheet to user + one-line shot summary, then full render.

### 5.9 Sound (`audio.py` → stems → `mix.py` — Stage 4.7)

Rewrite cue table for story; synths stay. `audio.py` writes only stems (`music.wav`, `sfx.wav`).

- Music: short march-like loop (kick/snare, plucked bass, brass pad). Stops at twist line, then low drone continues.
- SFX on events (frames/30): whooshes on big moves, thunk on stamps, rumble+crash on collapses, scrape on metal, ting on reveals, sting on twist, creaks, snap, splash, snore, leaves, water ambience.
- Mix: `python3 mix.py voice.mp3 music.wav sfx.wav` — music exactly 50% voice gated RMS (−6 dB), SFX 50% with peaks capped at 0.7× voice peak. Confirm printout: music −6.0 dB vs voice, SFX ≤ that.
- Lock picture timing before sound. Any timing change → re-run audio.py + mix.py.

### 5.10 Render + finish (Stage 4.8)

```bash
node render.mjs frames "0-<N-1>"   # run_in_background + Monitor loop; RESUME=1 continues
bash finish.sh "Title"             # linear gain ~-14 LUFS + -1 dBFS limiter, H.264 CRF 17 + AAC, freeze/black + loudness QA -> out/qa_sheet.jpg
```

- `finish.sh` exact: `loudnorm=I=-14:TP=-1.5:LRA=7` → `libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart` → `freezedetect=n=0.0005:d=0.4,blackdetect=d=0.05` QA (empty = pass) → `ebur128` loudness → `fps=2,scale=180:-1,tile=10x4` QA sheet. Frozen spans ≥0.4 s or black frames need fix.
- Deliver MP4 + few lines per shot. Offer captions/tweaks/next idea.

### 5.11 Kit setup (Stage 4.0)

```bash
find / -name SKILL.md -path "*cartoon-audio-short*" 2>/dev/null   # locate kit/
bash <skill>/kit/tools/setup.sh ~/shorts/<slug>
```

- Copies engine + tools, installs vendored three.js r160, strips types from `toon.ts` with Node 22 `module.stripTypeScriptTypes`, links Playwright. No network needed. Fallback: npm or git clone.
- Requirements: Node 22.6+, Python 3 + numpy + Pillow, ffmpeg, Playwright + Chromium (`npm i -g playwright && npx playwright install chromium`).
- Chromium flags: `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist` → CPU WebGL ~3–10 s/frame.

### 5.12 Engine gotchas (keep if rebuilding)

- `#include <fog_vertex>` / `<fog_fragment>` on own lines. Final pass writes `linearToOutputTexel(...)` (render targets linear HalfFloat). Normal+depth pass swaps materials per mesh: world → normal/depth, cards → alpha-tested mask (rgb 0, a = depth), blobs/clouds/sky hidden, water → flat normal. Fog/shadows off during it. Ink on near side of depth jumps only. Creases from normal dot. Card neighbours skipped. Ink fades ~140–520 m. DOF 48 taps, per-sample CoC test (no foreground bleed). Sun from az/el per light preset. Shadow camera centred on each shot's action.

### 5.13 Architecture

- `web/index.html` loads `main.js` (ES module) over local HTTP. `main.js`: renderer, toon materials, world, cards (1200×2000 CanvasTexture planes, origin at soles), passes colour (RT samples 4) → normal/depth → ink+grade (sat, gain/lift, vignette, flash) → DOF to screen. Exposes `window.renderFrame(f)` + `window.ready`.
- `story.js` exports SHOTS, `shotAt`, `camAt`, `dofAt`, LIGHTS/`lightFor`, `worldAt`, `actorsAt(f,T)`, `fxAt(f,T)`. All pure functions of frame.
- `render.mjs`: Playwright → `renderFrame(f)` → `toDataURL('image/jpeg',.95)` → `frames/f0000.jpg`.
- `mix.py`: gated-RMS level lock. `finish.sh`: linear loudness gain, limiter, encode, QA.
- Characters: Pen API from `mromidev/claude-animated-shorts` `templates/bridge/toon.ts` (MIT), extended in same module scope by cast file.

---

## 6. Engine C — 3d-story-shorts / Remotion (720×1280 true-fact mini-movie)

**Skill:** `3d-story-shorts.zip` → `3d-story-shorts/SKILL.md` + `template/` (working "Skyscraper Fixed in Secret" project) + `example/` + `scripts/`.

### 6.1 The look (do not drift)

- Bright saturated colours: blue sky dome + sun + soft clouds, warm key from upper left, cool fill. Light bloom on lamps/windows, grade sat 1.2, light vignette. Nights deep blue + warm windows.
- Soft 4-band toon shading, dark ink outlines **#351f22** on everything.
- **Busy frames.** Every shot: foreground + midground + background with props/people in all three. Users reject "clean" empty sets.
- Interiors: cool walls (teal/blue) vs warm wood + shelves/papers/posters/lamps/clock.
- **Characters fill 35–50% frame height** in character shots, camera 2.5–4 m away. Wides only for buildings/establishing.
- Camera: always moving, eased in/out, net travel every shot. **Cream dip (0.4 s) at location changes.**
- Captions (in `Full.jsx`, automatic from `timing.json`): one word at a time, white Arial Black + thick dark outline, at 67% frame height below faces. If caption covers key sign, move it for that shot (`close` override).

### 6.2 Hard rules

- **Fact-check everything.** Every on-screen claim needs **two independent sources**. Leave out single-source/disputed. Keep fact map in `script.md`.
- Stay inside YouTube policy: no medical/financial advice, no invented quotes from real people, no graphic injury, no "gambling systems". Real people never shown as villains.
- Label dramatisation. Invented characters around real fact OK; never present invented events as documented history.
- Never copy another creator (scripts, designs, logos, exact sets). Style idea only.
- Don't assume audience/niche — ask or take from message.
- Simple words, one idea per sentence. Numbers as narrator says them ("nineteen seventy-eight").
- Keep approved things fixed: script, voice, timing, facts. If policy forces a change, tell user exactly what changed.
- Be honest about what was checked: stills vs full video.

### 6.3 Script beats (10–13 shots, 150–180 words, 55–65 s @ ~170 wpm)

1. **Hook (0–5 s):** strange action as plain fact. No intro, no "did you know".
2. **Optional CTA:** only if user asks, right after hook.
3. **"You see," + stakes:** rival, race, deadline.
4. **Doubt/mock:** someone laughs, or rules say it's fine. Never invent quote for real person.
5. **Escalation ladder:** "In May… by July…".
6. **Problem:** "But…" / "Then…".
7. **Second "You see,":** real science/reason + one everyday object (blowing on soup, phone sliding off table).
8. **"So…":** what they did.
9. **Twist closing line** (5–19 words). No outro. Optionally cut mid-sentence so replay loops into hook.

Outputs: `script.md` (shot table, fact map + sources, left-out-on-purpose, wording to watch), `SHOTS.txt` (`key | exact spoken text`, keys short/unique), voice-over PDF. Show shot table, ask "Make the video from this script?"

### 6.4 Voice (Stage 3)

- User records: take WAV/MP3. Otherwise TTS: 3 hook samples in different voices → user picks → **whole script in one single generation** (never changes voice between batches). Keep within credit limits.
- Run: `python3 scripts/prepare_voice.py RAW.wav SHOTS.txt <project>` (defaults 170 wpm, max 1.12× speed, pitch kept).
- Tightens pauses (0.42 s between shots, 0.2 s inside), matches every comma/full stop to a pause, writes `<project>/voiceover.wav` + `<project>/src/timing.json`.
- If "can't find a pause": `SHOTS.txt` doesn't match audio word-for-word. Fix text, re-run.
- `prepare_voice.py` internals: ffmpeg `silencedetect` (noise −35 dB, d=0.2) → DP aligns punctuation events to silences (sentence-end needs ≥0.35 s pause, comma ≤0.7 s) → rebuild speech pieces + shortened gaps → `atempo` speedup to target wpm (never above max) → `timing.json {fps:30, duration, shots:[{key,start,end,words,text}]}`.

### 6.5 Build (Stage 4 — automatic)

1. Copy `template/` → new project, `npm install`, timing from Stage 3.
2. **Plan locations:** 4–7 locations (street, office, yard, workshop, control room, ship deck…). Re-use/re-dress existing where possible. Each at own x offset in `LOC` (worlds.js).
3. **`src/camera.js` → `PLAN`:** one entry per shot key, exactly matching `timing.json`. Each: light preset (`day, night, storm, office, yard, joint, weather, morning` or custom), `anchor` for light, 3 camera keys `{p: position, l: look-at}`. `beats: 'words:<key>:0,<word index>,<last>'` so camera reaches subject when named. Shots continuing from previous go in `CONT` set (no cream dip).
4. **`src/worlds.js`:** story objects, in-world signs (`sign('TEXT', w, h, …)`), word-synced events via `wordT('<key>', wordIndex)` (label appears on number word, light off on "emptied").
5. **`src/dress.js`:** fill every location. Street = `dressStreet` (traffic, pedestrians, shop fronts, trees, hydrants). Interiors: copy office/workshop/weather patterns.
6. Replace example signs/magazine/posters with new story details.

### 6.6 Files that come with the skill

- `template/`: complete working project. `src/kit.js` (materials, ink, painted textures, signs, facades, tower), `src/char.js` (2D character: palettes, hats, glasses, idle, turns to camera), `src/props.js` (cars, taxis, buses, trees, hydrants, shop fronts, shelves, desks, lamps, tools, barrels…), `src/dress.js` (fills locations), `src/worlds.js` (locations, story objects, per-frame events tied to words), `src/camera.js` (camera plan per shot, light presets, cuts, cream dips), `src/Full.jsx` (renderer, sky, bloom, grade, vignette, captions), `src/timing.json` (written by prepare_voice.py), `render.bat` (Windows), `render.sh` (Mac/Linux), `test_render.bat`, `check.bat` (diagnostic log).
- `scripts/prepare_voice.py`, `scripts/stills.sh` (renders check frames in cloud, tiles contact sheet), `example/` (script, SHOTS.txt, approved look frames).
- If files missing, ask user once to attach starter kit zip.

### 6.7 Check stills (Stage 5 — automatic)

```bash
scripts/stills.sh <project> a <frames>
# one frame from middle of every shot + frames right after each word-synced event
```

Check: nothing hides face/label/caption; no character cut off at edge; camera not inside wall/car; no room blown out (too yellow/white) or too dark; frames busy enough; facts on screen correct. Fix + repeat. Cloud stills 20–40 s each. Never render whole video in cloud unless user can't render: ~6 s/frame, or ~1.7 s/frame without BokehPass.

### 6.8 Handover (Stage 6)

- Device tools available: `get_device_info` → confirm platform/device → request one folder (e.g. Videos) → commit project zip there, extract via `device_bash` (`python3 -c "import zipfile; zipfile.ZipFile('x.zip').extractall('.')"`). Rename old `final.mp4` first.
- Otherwise: send zip, tell user to unzip with Extract All. Windows browsers block `.bat` downloads — never send `.bat` alone; always inside zip or written into folder.
- Leave out `node_modules`, `out`, `final.mp4` from zip.
- Tell user: "The video is ready to render. Open the folder and double-click render.bat. It uses your computer's graphics card and takes a few minutes. When it finishes, tell me and I'll check it and send it with the voice-over script PDF."
- Only if asked/slow: Node.js must be installed; first run downloads packages + browser; on laptop set Remotion browser + Claude app to High performance (Settings → System → Display → Graphics), restart app.
- `render.bat`: `npm install`, then `npx remotion render src/index.jsx <Id> out\full_silent.mp4 --gl=angle --concurrency=4 --image-format=jpeg --jpeg-quality=92 --crf=17`, then `npx remotion ffmpeg -y -i out\full_silent.mp4 -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4`. CRLF line endings + `pause` at end.

### 6.9 After render

Check real video: `ffprobe` (size, fps, duration, audio) + one frame per shot contact sheet. Deliver MP4 + voice-over script PDF. Say what was checked, what is still wrong, offer one next step.

### 6.10 Template stack (exact versions)

```json
{
  "name": "story-short", "private": true,
  "scripts": { "studio": "remotion studio src/index.jsx" },
  "dependencies": {
    "@react-three/fiber": "8.17.10",
    "@remotion/cli": "4.0.242",
    "@remotion/three": "4.0.242",
    "react": "18.3.1", "react-dom": "18.3.1",
    "remotion": "4.0.242", "three": "0.169.0"
  }
}
```

Source sizes (template): kit.js 292 lines, worlds.js 310, dress.js 147, char.js 137, props.js 136, camera.js 88, Full.jsx 133. Hoover project: worlds.js 324, dress.js 224, camera.js 90 (story-specific growth).

---

## 7. Engine D — animated-3d-story-video (Chicago-lifted style, 720×1280)

**Skill:** `animated-story-video.skill.zip` → `animated-3d-story-video/SKILL.md` only (no kit — build from spec or adapt a starter project if present).

### 7.1 Reference look (fixed)

Based on finished video *"Chicago lifted itself"* (hotel lifted six feet while guests slept, then whole city raised out of mud). New videos must look/feel the same.

- **Hard rules:** never ask user for reference videos/examples/style (style is in this file). Never mention specific graphics card/user hardware — end with "your computer's graphics card". Do technical work yourself; ask only flow questions. Keep approved things fixed: script, timing, facts, characters, ink colour **#351f22**. Be honest about what was checked (stills vs full video), list known problems. Do not render full video yourself; user renders it.

### 7.2 Flow (three steps for user, everything else automatic)

1. **Ideas (start here, no questions first):** immediately 5 story ideas. If user gave topic, use it; else pick true surprising stories where something physically big changes (city rises, river moved, ship carried over land). Each: one-line title, visual hook (what moves/changes), escalation (but/then/so), 2–3 hard numbers/names. Web-search to confirm, drop single-source/unclear. Ask "Which one should I write?"
2. **Script:** per §7.3. Show shot table (shot, start, words, line, on screen) + voice-over text. Ask "Do you want me to make the video from this script?" Small edits → ask again.
3. **Make video, then say ready to render:** only after yes. Voice-over: user's file if any; else TTS if available; else estimated timing (3.35 words/s) + warn cuts must be re-timed once audio exists. Build stages A–F without stopping. Handover per §7.6.

### 7.3 Script rules (built-in rulebook)

- First word at t=0, no intro, premise in first sentence. Hook 5–23 words (aim 16), ends ~4–5 s.
- 9–12 shots, one location per shot, ~140–150 words for ~43–48 s (3.35 words/s, range 3.05–3.65). Total 39–65 s.
- Beats: **But** (shot 4), **Then** (shot 5), complaint/conflict (shot 6), pivot **"You see"** at 53–87% runtime (shot 7), **"So…"** consequence at 80–93% (shot 9), closing line 5–19 words (~9). No outro, no CTA.
- Simple words, one idea per sentence, concrete numbers/names. Every claim sourced; leave out single-source/unverifiable.
- Output: `script.md` (shot table, rulebook check, fact map, left-out-on-purpose, wording to watch) + voice-over PDF: "Chapter N - Title (start time)" + one paragraph, 2–3 chapters for short video.

### 7.4 Build stages (automatic)

**A. Timing:** transcribe voice-over with timestamps → `sentence_times.json` (starts/ends per sentence). Shot cuts from real sentence ends, one `CUTS` array; if shot holds two sentences keep both times.

**B. Art style (fixed):**
- One ink colour every outline: **#351f22**.
- Models built in code with real depth: extruded walls with window reveals/sills, door panels, awnings, cornices, chimneys, threaded jackscrews, timber crib stacks, brick vaults. Textures painted flat colours + wear (stains/chips/scratches) on canvas. Outline = inverted hull + edge lines.
- Toon shading 3-band gradient. One warm key from upper left + shadows, hemisphere fill, light vignette, fog per location.
- Depth: blurred foreground near lens, sharp midground with characters, softly blurred background (DOF pass focused at look-at distance).
- Labels inside world (painted signs, banner on two poles, names on crates, map title, desk nameplate). Never floating pills/captions.
- No flat sky/ground strips, no side-on cardboard buildings.
- Cuts: 0.4 s dip to cream at location changes; continuous camera moves where one shot flows into next.

**C. Characters (2D flat people in 3D world):**
- Built in code from flat shapes: large round pale head, calm half-lidded eyes, tiny smile, hair fringe, white collar, tie, small pear-shaped two-tone torso + pocket patch, thin tapered stick limbs, dark disc hands. Hand-drawn ink band, varying slightly wobbly thickness around every shape.
- Variants by palette, hat (top hat, bowler, cap, none) + glasses only. Never redesign base character.
- Flat shading. Idle bob/nod, arm sway. Turn toward camera, limited yaw (clamp ~0.7 rad), never edge-on. Soft contact-shadow blob.
- Size: body 40–60% frame height in medium shots, 70%+ in close shots. Three people side by side → camera ~4 m away.

**D. 3D worlds:**
- Every location in one scene at different x offsets (e.g. 0, 40, 80, 120, 200, 300, 400) so camera can travel + light switch per location.
- Shared helpers once: facade (extruded wall + window/door openings + interior backdrop), liftable building (facade + needle beams + jackscrews + timber stacks + brick foundation), lamp post, barrel, plank sidewalk, mud ground, brick tunnel, room.
- Procedural models only (cloud workspace cannot download assets).
- Door opening must be notch in outline, not hole touching bottom edge, or triangulation breaks.
- If starter project attached/present (kit.js, char3.js, world1.js, areas.js, Full.jsx), copy + adapt. Else build kit from this spec.

**E. Camera plan + animation:**
- Write `camera_plan.md`: per shot time, location, camera path (start → end), speed, foreground/midground/background objects + in-world labels.
- Rules: net travel every shot; ~10% frame width/second average (25–40% travel or push per shot); mix push (~half), crane (~third), sideways track (~fifth); carry camera from one subject to next inside location; dissolve between locations.
- Geometry for 80° vertical FOV at 9:16: frame width at subject = 0.93 × distance, frame height = 1.68 × distance.
- Sync to words: per camera key set beat time from sentence timing (word positions by proportion) so camera reaches each subject as named. Smooth with monotone cubic time warp, zero speed at first/last key (ease in/out), no straight-line blending, almost no wobble:
  ```js
  function warpU(T, t) { // T = beat times per path key; returns path position 0..1
    const n = T.length; if (t <= T[0]) return 0; if (t >= T[n-1]) return 1;
    const sec = []; for (let i = 0; i < n-1; i++) sec.push((1/(n-1)) / (T[i+1]-T[i]));
    const m = [0]; for (let i = 1; i < n-1; i++) m.push(2*sec[i-1]*sec[i]/(sec[i-1]+sec[i])); m.push(0);
    let i = 0; while (t > T[i+1]) i++;
    const h = T[i+1]-T[i], x = (t-T[i])/h, x2 = x*x, x3 = x2*x;
    return (2*x3-3*x2+1)*(i/(n-1)) + (x3-2*x2+x)*h*m[i] + (-2*x3+3*x2)*((i+1)/(n-1)) + (x3-x2)*h*m[i+1];
  }
  ```
- Tie on-screen events to words: label appears on number word, street rises on "raised", water pools on "couldn't drain", arrow drawn on "go up".
- Keep camera clear of characters/props; end every move at rest.
- Drive all animation from frame number (`useCurrentFrame`), never wall-clock. Render 3D in `ThreeCanvas`, postprocessing composer in `useFrame` at priority 1.

**F. Check it (stills):** render single frames at beat times at half scale (`npx remotion still ... --scale=0.5 --gl=swangle --browser-executable=<preinstalled chromium>`; ~90 s each in cloud, one at a time, never edit source while one renders). Tile contact sheet, look for: objects hiding name/face/label; characters cropped at edge; props behind heads; poles/lamps crossing subject; anything through lens; black polygons/empty openings; camera inside wall; wrong fact on screen. Fix by moving objects out of line of sight; repeat until clean. Never render full video in cloud (no GPU, many hours).

### 7.5 Handover

Short/plain: "The video is ready to render. Open the folder and double-click render.bat. It uses your computer's graphics card and takes a few minutes. When it finishes, tell me and I'll check it and send it with the voice-over script PDF." Only if asked/slow: Node.js required; first run downloads packages + browser; laptop → High performance for Remotion browser + Claude app (Settings → System → Display → Graphics), restart app. Folder contains `render.bat` + `test_render.bat` (30-frame test). `render.bat`: `npm install`, then `npx remotion render src/index.jsx <Id> out\full_silent.mp4 --gl=angle --concurrency=4 --image-format=jpeg --jpeg-quality=92 --crf=17`, then `npx remotion ffmpeg -y -i out\full_silent.mp4 -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4`. `.bat` CRLF + `pause`.

### 7.6 After render + known limits

Check: `ffprobe` (size, fps, duration, audio) + one frame per shot contact sheet. Deliver MP4 + voice-over PDF. Say what was checked, what is still wrong, offer one next step. **Known limits:** models procedural, not imported. Resolution 720×1280. Ground-floor openings of lifted facades once rendered as black patches (cause not found); report if appears.

---

## 8. Worked examples (copy these exactly)

### 8.1 The Soldier Who Never Left (Engine B — 19.72 s, 8 shots)

Voiceover (48 words, 3.7 w/s): *"A Roman soldier stood guard at a bridge for 30 years, refusing to leave his post. Even when the empire collapsed, he stayed. People called him crazy. But when workers finally removed his helmet, they discovered a message carved inside: The bridge is not safe. Beneath it, the wooden supports had been slowly rotting for centuries."*

| Shot | Frames | Light | Camera | Action |
|------|--------|-------|--------|--------|
| hook | 0–87 | day | MCU → pull back to wide (fov 34→44.5) | Soldier at bridge, shadow extends |
| refuse | 88–149 | day | Slow push (fov 40→38) | Refusing to leave |
| collapse | 150–227 | golden | Wide to soldier (fov 22→28.5) | Empire collapses |
| crazy | 228–277 | golden | Slow push (fov 42→40) | Crowd laughs (alternating tilt+bob) |
| workers | 278–353 | day | Push (fov 33→32) | Workers lift helmet (reach + lift) |
| inside | 354–455 | day | Push + roll −3→−4.5° (fov 40→33) | Carved message reveal (workers blurred bg) |
| shock | 456–482 | day | Push (fov 30→29) | Shock: hands to cheeks, jitter |
| under | 483–591 | day | Crane down under bridge (fov 42→39, roll +3°) | Rotting supports payoff on final word |

- `story.js`: `FPS=30, TOTAL=592, DECK=6`. LIGHTS: day (az 140, el 46, sky #c4d6f2, sun #fff1dc, sat 1.1) + golden (az 8, el 9, sun #ffb46c, sat 1.12). `lightFor` extends shadow in hook/collapse/under.
- `audio.py`: music Am–F–G–E loop @104 BPM (kick/snare, plucked bass, brass pad), stops at 14.15 s ("The bridge is not safe") → sting (41 Hz low + noise hit + brass stab) → tension drone (55/82.4/110.3 Hz) to end. SFX: thunk, rumble, crash, cuckoo, scrape, ting, creak, snap, splash, whoosh, snore, leaves, water.
- Files: `story.js` (14 KB), `audio.py` (9 KB), `stills.jpg` (406 KB contact sheet).

### 8.2 The Skyscraper Fixed in Secret (Engine C — ~46 s, 11 shots, 154 words)

| # | Start | Words | Line | On screen |
|---|-------|-------|------|-----------|
| 1 | 0.0 s | 14 | In 1978, welders secretly patched a brand new New York skyscraper, every single night. | Night city; welding sparks high on tower |
| 2 | 4.2 s | 13 | It stood fifty-nine stories high on giant stilts, and it had just opened. | Crane up tower on stilts; NOW OPEN |
| 3 | 8.1 s | 11 | The building rules only asked about wind hitting the flat sides. | Rule book: arrows hit flat sides |
| 4 | 11.3 s | 16 | But a student asked about corner winds, and the numbers showed about forty percent more force. | Student points at corner; +40% chalkboard |
| 5 | 16.1 s | 16 | Then the engineer learned the builders had swapped his welded joints for bolts to save money. | Crate BOLTS where WELDS should be |
| 6 | 20.9 s | 14 | A big enough storm could snap those bolts, right in the middle of Manhattan. | Storm clouds; bolts strain |
| 7 | 25.1 s | 19 | You see, a weld turns a joint into one solid piece. Bolts are only as strong as the bolts. | Welded vs bolted joint close-up |
| 8 | 30.7 s | 14 | Every night after the offices emptied, welders covered the bolted joints with steel plates. | Night: lights out, sparks behind curtain |
| 9 | 34.9 s | 15 | During the repair, Hurricane Ella headed for New York, and evacuation plans were drawn up. | Weather map; EVACUATION PLAN |
| 10 | 39.4 s | 10 | So everyone watched the forecasts, until the storm turned away. | Storm arrow bends away |
| 11 | 42.4 s | 12 | The repair worked, and the public didn't hear about it until 1995. | Morning tower; newspaper 1995 |

- Rulebook check: hook 14 words ends 4.2 s OK; 11 shots/154 words/~46 s OK; But=shot 4, Then=shot 5, conflict=shot 6 OK; "You see" 54% OK; "So…" 86% OK; closing 12 words OK.
- Fact map (2 sources each): Citicorp Center 1978 secret repair (Wikipedia + Futility Closet); 59 stories on stilts (OnlineEthics + Atlas Obscura); NYC code perpendicular-only (Wikipedia + OnlineEthics); student corner-wind question (Wikipedia + Atlas Obscura + Penn State); ~40% more load on 4 of 8 brace tiers (Wikipedia + Indie Hackers); bolts-for-welds swap (OnlineEthics + Wikipedia); corner wind could shear bolts (Designing Buildings + Wikipedia); night plate welding (Wikipedia + PCBB + Veritasium); Hurricane Ella + evacuation plans (Wikipedia); forecasts watched (Penn State); secret until 1995 (Wikipedia + Penn State).
- Left out: student name (accounts differ), exact topple wind speed/odds (sources differ), repair cost ($several M–$12 M range), no invented quotes.
- `SHOTS.txt` keys: hook, cta, tower, rules, but, then, storm, yousee, night, ella, so, close (12 lines incl. optional CTA).
- `camera_plan.md`: hook crane down lit tower; cta push to host under LIKE+SUBSCRIBE billboard; tower crane up stilts→crown; rules push book→model; but continue to student+chalkboard; then track WELDS→engineer→BOLTS; storm slow push up; yousee sideways track welded→bolted; night push up; ella push to map→easel; so back to map; close crane up newsstand→tower. Cream dip 0.4 s at every location change; rules→but and ella→so continuous.

### 8.3 Hoover Dam (Engine C full project — 60.29 s, 13 shots, 186 words)

`SHOTS.txt` (exact spoken text, numbers as words):

```
hook   | They poured a dam in columns, because one solid block would take one hundred and twenty-five years to cool.
heat   | You see, concrete doesn't just dry. It gets hot as it hardens.
size   | And this dam needed enough concrete to pave a highway from San Francisco to New York.
math   | Engineers did the math. Pour it all at once, and the middle would stay hot for a century.
shrink | A hot block shrinks as it cools. And shrinking concrete cracks.
crack  | But a dam that cracks, is just a very big pile of rocks.
lego   | So they built it like giant Lego. Tall columns, poured five feet at a time.
pipes  | Inside every column, they threaded one-inch steel pipes. More than five hundred miles of them.
water  | First, river water ran through the pipes. Then, ice-cold water from a refrigeration plant.
ice    | That plant could make a thousand tons of ice, in a single day.
soup   | You see, it's like blowing on hot soup. Spread it thin, and cool it fast.
grout  | Once each column cooled, they filled the pipes with grout.
twist  | And the scariest part of that dam, was never the water. It was the heat.
```

`timing.json` (fps 30, duration 60.29):

| Key | Start | End | Words |
|-----|-------|-----|-------|
| hook | 0.15 | 6.423 | 19 |
| heat | 6.843 | 10.276 | 12 |
| size | 10.646 | 15.464 | 16 |
| math | 15.884 | 20.498 | 18 |
| shrink | 20.918 | 23.853 | 11 |
| crack | 24.188 | 26.131 | 13 |
| lego | 26.487 | 30.617 | 15 |
| pipes | 31.033 | 36.587 | 15 |
| water | 36.893 | 43.536 | 14 |
| ice | 43.956 | 47.645 | 13 |
| soup | 48.065 | 51.955 | 15 |
| grout | 52.375 | 55.273 | 10 |
| twist | 55.693 | 59.541 | 15 |

- `voiceover.wav`: stereo, 48 kHz, 16-bit, 60.33 s, 11,584,362 B. Gaps between shots ~0.3–0.4 s (prepare_voice.py 0.42 s between, 0.2 s inside).
- Project = copy of `template/` with story files rewritten: `camera.js` (90 lines), `worlds.js` (324), `dress.js` (224), `Full.jsx` (133). `kit.js`/`char.js`/`props.js` unchanged (292/137/136 lines). **This is the proof that copy-template-then-rewrite-story works.**
- Note: `camera_plan.md` in the Hoover zip still shows the Skyscraper plan (template leftover) — always rewrite it for the new story; never ship a stale plan.

### 8.4 Pitch Drop (Engine B flat-2D fallback — 48.07 s vertical)

From the MHTML Claude chat (2026-11-08, user in PK, ElevenLabs voice Jesse):

- Script (bracketed tags stripped for timing): *"This experiment waited eight years for its first drop. In nineteen twenty-seven, physicist Thomas Parnell poured hot pitch into a glass funnel. It looked solid, but he wanted to prove it could flow. He let it settle for three years, then cut the stem in nineteen thirty. The first drop took eight years to reach the beaker. Later drops took years more; the eighth and ninth each took about thirteen years. Pitch can shatter when struck, yet creep downward under its own weight. In twenty fourteen, the ninth drop finally touched the old pile below. No splash, no dramatic fall—just a slow, almost invisible meeting. Nearly a century later, the experiment is still making its point: something can look solid and still flow."*
- Build: 48 s vertical **1080×1920, 30 fps, 20 MB**, voiceover unchanged, no frozen/black frames. Shots: hook (drop hanging + calendar 1930→1938 on "eight years"); 1927–1930 lab (chalked "1927", pour, lightbulb, doze + calendar flips, glass-cutter cut); first drop falls on word "beaker" (ring + sparkle); chalkboard tally (8th/9th circled, "~13 yrs") + hammer shatter on "struck" + slump; 2014 gallery (beanie visitor filming, flinch on "No splash", "SPLASH!" bubble deflates on "fall", macro contact); ending (pull back to 2026 calendar, portrait wink, finger tap on "look solid", new drop swells on "flow").
- Sound: music bed **−6.0 dB under voice**, SFX peaks capped ~3 dB under voice peak, master **−15 LUFS, −1.6 dBFS peak** after encode.
- **Differences from spec (documented honestly):** flat 2D not 3D (kit missing in that environment — built look as flat 2D with plum outlines; true 3D would take hours); chalkboard "~13 yrs" kept to match script (real gaps ~12/14 years).
- **Lesson for the agent:** if the 3D kit is missing, ship the flat-2D fallback with plum outlines and state the difference. Never block on missing kit.

---

## 9. Camera shoots — master reference (all moves, numbers)

### 9.1 Universal rules (all engines)

- **Never static.** Every shot moves: push, pull, crane, track, orbit, dolly, rack focus, or roll/shake. Holds creep. Nothing static 4+ frames (Engine B) / every shot has net travel (Engines C/D).
- **Ease everything.** Smootherstep glides 18–45 frames (B), ease in/out with zero speed at first/last key (D `warpU`), `ease.inOut` for moves + `ease.out` for snaps (A). No straight-line blending.
- **Sync to words.** Camera reaches subject when named (`beats: 'words:<key>:0,<word index>,<last>'` in C; `wordT('<key>', wordIndex)` events; `wordTime()` in A; reaction 0–3 frames before its word in B).
- **Continuity over cuts.** Prefer continuous moves (pull back close-up→wide, rack focus, crane through deck, push into object). Hard cut only on place/time jumps, with flash (B) / cream dip 0.4 s (C/D) / flash/dip/fade/whip/zoom (A).
- **End every move at rest.** Keep camera clear of characters/props; never inside wall/car; never through lens.
- **Drive from frame number**, never wall-clock (`useCurrentFrame` in D; pure functions of frame in B `story.js`; `t` seconds into shot in A).

### 9.2 Move-by-move spec

| Move | When | Parameters (exact) |
|------|------|-------------------|
| **Push in** | Default (~half of shots in D; default in A) | A: `z` 1.0→1.05–1.10 over shot. B: smootherstep glide 18–45 f. C: 3 keys `{p,l}` + `beats` to land on named subject. D: 25–40% travel/push per shot, ~10% frame width/s average. |
| **Pull out / reveal** | Endings, wide reveals | A: slow pull-out. B: pull back from close-up into wide (continuous). C: crane up from stilts→crown, newsstand→tower. |
| **Crane (vertical)** | Towers, dams, buildings, establishing | C Hoover/Skyscraper: crane down lit tower front; crane up stilts→crown. D: ~1/3 of shots. B: crane through deck; crane down under bridge (Soldier `under`). |
| **Sideways track** | Comparing two subjects, joints, crates | C: track WELDS crate→engineer→BOLTS stack; sideways welded→bolted joint. D: ~1/5 of shots. |
| **Orbit / fly-through (3D)** | Big spaces (stadium, street, hall) | A: `T.orbit(camera,t,{target,radius,height,from,to,dur})`, ~1 per minute. Same figures + palette as 2D. |
| **Dolly (keyframed)** | Precise 3D moves | A: `T.dolly(camera,t,[[t,{pos,look,fov}],…])`. B: `camFromKeys(keys,f,{kicks})` with `path` Catmull-Rom via-points for curves. |
| **Rack focus** | Shift attention within shot | B: racks ~14 f. D: DOF pass focused at look-at distance. A: `blurLayer` + `veil` for bg blur. |
| **Roll (tilt)** | Drama, unease | B: 3–5° on drama; Soldier `inside` −3→−4.5°, `under` +3°. A: `r` ±0.02. |
| **Shake / kick** | Impacts, stamps, hits | B: 7-frame flip-shakes on impacts; stamp = 2-frame dip + dust puff + kick. A: `shake(t,amp,freq,seed)`. |
| **Whip / flash / dip / fade / zoom** | Transitions | A: cut ≥80%; flash→freeze/realisation; dip→time skip; fade→dreamy/title; whip→energetic jump; zoom→explanation. B: 6-frame white flash on time jump. C/D: 0.4 s cream dip at location changes; `CONT` set = no dip (continuous). |
| **Freeze / time-stop** | Signature moments (A: 1–3/video) | Particles hanging, cool tint, corner badge, slow rings/rotation, only hero moves. Enter with flash + `freeze` SFX. |

### 9.3 Framing math (do not guess — compute)

- **Engine D (80° vertical FOV, 9:16):** frame width at subject = **0.93 × distance**, frame height = **1.68 × distance**. Three people side by side → camera ~4 m.
- **Engine B (vertical, narrow):** horizontal half-width = **d·tan(hfov/2)**, hfov = 2·atan(tan(vfov/2)·0.5625). At 4 m, fov 40 → **±0.8 m** → stage characters in depth, not side-by-side. Foreground props <2 m will block. Railings/posts at ~2.5 m up cross faces.
- **Engine C:** characters **35–50% frame height**, camera **2.5–4 m**. Wides only for buildings/establishing.
- **Engine D characters:** body **40–60%** frame height (medium), **70%+** (close).
- **Engine A:** wide `s` 0.8–1.2 (15–25% height); medium `s` 1.5–1.8; `bigFace` radius 280–360 @1080p.

### 9.4 Lens / DOF / light per shot

- **DOF:** B close-ups/mediums cInf 8–14 px, focus on eyes; wides sharp. D: blurred foreground near lens, sharp midground, softly blurred background. A: `blurLayer(g,8–14,fn,cam,1.7)` foreground; bg blurred + darkened (`veil`) behind `bigFace`.
- **Light presets:** B `day` (az 140 el 46) / `golden` (az 8 el 9) / night-blue for explanation. C `day, night, storm, office, yard, joint, weather, morning` + `anchor`. D: warm key upper-left + hemisphere fill + fog per location. A: `mood('night'|'golden'|'dusk'|'storm'|'interiorWarm'|'interiorCool'|'void'|…)` per location; one key per shot, shown + spilled.
- **Shadow camera** centred on each shot's action (B). **Sun** from az/el per preset (B).

### 9.5 Per-shot camera plan format (write before code)

**Engine C (`camera_plan.md`):**
```
| Shot | Time | Location | Move | Subjects / in-world labels |
| hook | 0.0-4.6 | Night city | Crane down the lit tower front | Tower windows, welding sparks |
```
Plus: light preset + anchor + 3 keys `{p,l}` + `beats` + `CONT` membership in `camera.js`.

**Engine D (`camera_plan.md`):** per shot: time, location, path (start→end), speed, foreground/midground/background objects + in-world labels. Plus `CUTS` array + `warpU` beat times.

**Engine B (`work/PLAN.md`):** per shot: frames, words, setting, light, camera move, characters/poses/expressions, effects + SFX cue.

**Engine A (`story/shots.json`):** per shot: `id, start, end, line, scene` (concrete one-sentence picture), `set, bars, in {type,dur,dir}, sfx, amb, params, notes`.

---

## 10. Character master reference (3 systems compared)

| | A — Stick figures | B — Bean-head cards | C/D — Flat 2D people |
|---|---|---|---|
| **Construction** | Circle head r=26, torso 15, limbs 11–13 round caps, foot stubs, no fingers (inserts only) | `romanFront` on 600×1000 canvas, soles y=975, card 2.25 m (1 u = 0.00225 m), 1200×2000 CanvasTexture planes, origin at soles | Large round pale head, half-lidded eyes, tiny smile, hair fringe, white collar, tie, pear-shaped two-tone torso + pocket, thin tapered stick limbs, dark disc hands (D); palettes/hats/glasses/idle/turn-to-camera (C) |
| **Outline** | No outline — rim light edge instead (`rim:{color,dir,w}`, w 4–5 @1080p) | Plum outlines (cards) + black ink outlines (world) | Ink **#351f22** on everything (C+D) |
| **Shading** | Flat + rim; far limbs `inkFar` (dark purple-grey) | 2-step toon gradient; ink on near side of depth jumps only; creases from normal dot; ink fades 140–520 m; radius ~2.5 px @1080 | 4-band toon (C) / 3-band toon (D); inverted hull + edge lines (D) |
| **Variants** | One signature colour each (hoodie #d64a33, cap #f2c21a, beanie #f29ac0, green cap #3fb950, blue tee #3a6ea5, purple tracksuit #8a5ad6, lab coat+glasses, trench+fedora+sunglasses, headband, ponytail/bun); `kid:true` 72% | `OUTFITS`: tunic/cape/armor/helmet/hair/cap/beard/apron/dress/toga + headgear/props; arm poses hang/spear/point/up/wave/hip/belly/temple(+swirl)/lift/reach(+lift)/cheek/shield/cross/thumb; FACE + snore/stubborn/squint | Palette + hat (top hat/bowler/cap/none) + glasses only (D); palettes/hats/glasses (C). Never redesign base (D) |
| **Faces** | White dot/ring eyes, simple white mouth, brows; 18 expressions on word beats; blink 2.5–4 s; `talkAmount` only for quoted lines + `FX.rings` | FACE set + snore/stubborn/squint; `blinkAt`; head bobs on stressed words | Calm half-lidded eyes, tiny smile (D); idle bob/nod, arm sway, turn to camera yaw clamp ~0.7 rad, never edge-on (D) |
| **Motion** | `posesAt` + `breathe` (never frozen); `walkPose` walk 160 u/s, run 420 u/s; `trail` for super-speed | `idle(f,seed)` every card; anticipation→`back` overshoot→`spring` settle; stamp 2-frame dip + dust + kick; laugh tilt+bob; `walk()` distance+phase, bob 3–7% | Idle bob/nod, arm sway (D); idle animation, turns to camera (C) |
| **Grounding** | Contact shadow automatic; never float | Contact blob + alpha-tested shadow; billboards yaw-only; never inked by world pass | Soft contact-shadow blob (D) |
| **Detached parts** | — | Own card via `headCenter(seed)`: `y = DECK + (partY − hc) × 0.00225` | — |
| **Card keys** | — | `q()`-rounded values (redraw only on visible change) | — |

**Agent rule:** never redesign the base character. Add outfits/props in the same style. Render a character test sheet before using new designs (B). Keep signature colours fixed all video (A).

---

## 11. World / set building reference

### 11.1 Engine A sets

- Reusable `scenes/sets/<location>.js`, anchored to `GY`/`CX`, walls/floors/skies extended past frame.
- Flat shapes + soft linear gradients. Texture only: floor lines, mullions, blinds, lit-window grids.
- 60–75% dark mid-tones, 1–3 bright accents. Figures staged against brightest area.
- Layers: sky 0.1–0.2 → skyline 0.3–0.4 → back wall 0.5–0.6 → floor/props 0.8–0.9 → characters 1.0 → blurred fg 1.5–1.8.
- Windows signature: large + mullions + sky gradient + sun/moon glow + blinds. Night streets: facades + warm windows + steps + lamp cones + cars + round trees.
- Atmosphere: dust/rain/drops/stars/lens streak/god rays/fog.
- Typical locations: labs, cafés, bedrooms, kitchens, classrooms, offices, hospitals, locker rooms, stadiums, streets, rooftops, piers, roads, parks, airports, space.
- 3D via `three-kit`: `stage`, `box/cyl/cone/sphere/plane/ground/planks/tiles/windowPane/shaft/building/tree3D/pine3D/crowd3D/figure3D`, `mat/basic/canvasTex`, `orbit/dolly`. Figure ~1.7 m facing +x. Moody exposure: windows/lamps brightest, floor dark.

### 11.2 Engine B world

- Keep engine sections; replace world between `// ---------- world ----------` and `// ---------- cards ----------` + story parts of `worldState()`.
- Primitives + painted canvas textures (`paint.js`: planks, beams, rotten wood, stone, moss/ivy, grass, dirt, plaster, roof tiles, marble, banners, carved text). New painters same flat-with-dark-seams style.
- `tbox` constant texel density, 2-step toon, fog = horizon colour.
- Background: hills (half-buried spheres), mountains (cones + snow caps), cypress/pine, distant houses, painted cloud billboards.
- Set pieces = pivoted groups, 0..1 progress from `worldAt(f)`, eased + staggered.
- Curved diegetic text = planar UVs, check not mirrored.
- Secondary motion always: banner cloth waves, leaves/dust/drips/Zzz effect cards, flowing water.

### 11.3 Engine C worlds + dress

- `worlds.js`: locations + story objects + per-frame events tied to words (`wordT`). In-world signs `sign('TEXT',w,h,…)`.
- `dress.js`: fill every location. Street = `dressStreet` (traffic, pedestrians, shop fronts, trees, hydrants). Interiors: copy office/workshop/weather patterns.
- `kit.js`: materials, ink, painted textures, signs, facades, tower model. `props.js`: cars/taxis/buses/trees/hydrants/shop fronts/shelves/desks/lamps/tools/barrels.
- Locations at own x offsets in `LOC`. 4–7 locations per story. Re-use/re-dress existing where possible.
- Replace example signs/magazine/posters with new story details.

### 11.4 Engine D worlds

- All locations in one scene at x offsets (0, 40, 80, 120, 200, 300, 400) for camera travel + per-location light.
- Shared helpers once: facade (extruded wall + window/door openings + interior backdrop), liftable building (facade + needle beams + jackscrews + timber stacks + brick foundation), lamp post, barrel, plank sidewalk, mud ground, brick tunnel, room.
- Procedural models only. Door = notch in outline, not hole touching bottom edge (triangulation breaks).
- Labels inside world (painted signs, banner on two poles, crate names, map title, desk nameplate). Never floating pills/captions. No flat sky/ground strips, no side-on cardboard buildings.

---

## 12. Timing & voice pipeline

### 12.1 Golden rules (all engines)

1. **Keep narration intact.** Never rewrite/add/drop/reorder spoken words. Every shot illustrates words spoken while on screen. (A)
2. **Never edit or re-time the voice.** Picture timed to it. Reactions 0–3 frames before word. (B)
3. **Keep approved things fixed:** script, voice, timing, facts. (C/D)
4. **Script drives timing.** Claude cannot hear audio — without script text, timing is guessing. (B, proven in Pitch Drop chat)

### 12.2 Engine A timeline

```bash
python tools/new_project.py --name <slug> --voice "<voiceover path>" [--script "<script path>"] --aspect 16:9 --resolution 1080p --title "<title>" [--captions]
python tools/parse_script.py --project projects/<slug> --script projects/<slug>/input/script.<ext>   # timestamped script
python tools/transcribe.py --project projects/<slug> --script projects/<slug>/input/script.txt --lang en --model small   # plain script (match must be >=90%)
python tools/transcribe.py --project projects/<slug> --lang en --model small   # no script (base on slow machines, large-v3 for hard audio)
python tools/beats.py --project projects/<slug>   # beat sheet + draft story/shots.json
```

- Check `timeline/transcript.txt` (end ≈ voiceover length). Whisper model downloads first run (~75 MB base, ~500 MB small) — needs huggingface.co.
- `story/shots.json` owns all timing. Shots contiguous (`end` = next `start`), first at 0, last ends at `duration` = voiceover + ~1.5 s. Cut on phrase boundaries, start 0.1–0.2 s before phrase. Median 2–3.5 s. Establishing shot per new location.

### 12.3 Engine B timing

```bash
python3 timing.py voice.mp3 script.txt --out work   # -> work/phrases.json
```

- Whisper/faster-whisper word timestamps if available; else DP syllable alignment (see §5.3). Check `phrases.json`: pauses at sentence ends. Total frames = round(duration × 30).

### 12.4 Engine C timing

```bash
python3 scripts/prepare_voice.py RAW.wav SHOTS.txt <project>   # defaults 170 wpm, max 1.12x
# -> <project>/voiceover.wav + <project>/src/timing.json
```

- `SHOTS.txt`: `key | exact spoken text` (numbers as words), spoken order. Tightens pauses (0.42 s between, 0.2 s inside), `atempo` to wpm, pitch kept. "Can't find pause" = SHOTS.txt ≠ audio word-for-word → fix text, re-run.

### 12.5 Engine D timing

Transcribe voice-over with timestamps → `sentence_times.json` (starts/ends per sentence). Shot cuts from real sentence ends, one `CUTS` array. No audio yet → estimated 3.35 words/s + warn to re-time.

### 12.6 Voice generation (when user has no recording)

- **B:** ElevenLabs deep narrator, speed 1.05–1.1, stability 45–55%. MP3/WAV, natural pauses, export without music.
- **C:** 3 hook samples in different voices → user picks → **whole script in one single generation**. Keep within credit limits.
- **A:** user voiceover file (any common format). Script optional (timestamped SRT/VTT/JSON/TXT with `[mm:ss]`, or plain aligned text, or none → transcribed).

---

## 13. Sound design (music, SFX, mix levels)

### 13.1 Mix levels — the numbers that must match

| Engine | Music vs voice | SFX vs voice | Master | Tool |
|--------|---------------|--------------|--------|------|
| **A** | −17 dB default (`config.music.gainDb`), ducked **−9 dB** under voice | −6 dB default (`config.sfx.gainDb`) | **−14 LUFS** (`config.loudness`) | `python audio/mix.py --project projects/<slug>` |
| **B** | **Exactly 50% voice gated RMS (−6 dB)** | 50% or less, peaks capped at **0.7× voice peak** | Linear gain ~**−14 LUFS**, **−1 dBFS** peak limiter | `python3 mix.py voice.mp3 music.wav sfx.wav` → `bash finish.sh "Title"` |
| **C/D** | Muxed with voiceover (`-c:a aac -b:a 192k`) | — (in-world events via `wordT`; no separate mix spec) | H.264 CRF 17 + AAC 192k | `render.bat` ffmpeg mux |

- **B rule:** always mix with `mix.py`, never by hand. No ducking/compression changing ratio — one linear gain + peak limiter on whole mix only. Confirm printout: music −6.0 dB vs voice, SFX ≤ that.
- **A rule:** change gains by 2–3 dB per iteration. QC: `ffmpeg -i out/<file>.mp4 -af ebur128=framelog=quiet -f null -` → integrated ≈ −14 LUFS.
- **Pitch Drop proof (B):** music −6.0 dB under voice, SFX peaks ~3 dB under voice peak, master −15 LUFS, −1.6 dBFS peak.

### 13.2 Music

- **A:** mood sections `{start,end,mood,intensity}` in `shots.json`, every 30–90 s at story turns. Moods: `mystery, tension, action, wonder, hopeful, sad, triumph, playful, calm, dark, epic`. Intensity 0–1 adds pulse/arps/drums. Audition `python audio/music.py --mood tension --intensity 0.7 --dur 20 --out build/test_tension.wav`. User track: `config.music.file = "input/music.mp3"` (loops/trims, end fades). Generated music = serviceable bed; premium → suggest user's licensed track.
- **B:** short march loop (kick/snare, plucked bass, brass pad). Stops at twist line → low drone continues. Soldier: Am–F–G–E @104 BPM, stop 14.15 s → sting → drone (55/82.4/110.3 Hz).
- **C/D:** no separate music spec in skills — voiceover + in-world SFX via word-synced events. If music needed, add as user track (A pattern) and duck under voice.

### 13.3 SFX library

- **A (36 effects):** `whoosh, swish, impact, hit, riser, slowmo, freeze, tick, clock, heartbeat, pop, blip, counter, ding, shimmer, stinger, footstep, kick, whistle, carpass, phonebuzz, phonering, cheer, applause, murmur, rain, thunder, wind, roomtone, city, hum, powerup, glitch, flash, buzz`. List: `python audio/sfx.py --list`; demo: `--demo build/sfx_demo`. Per-shot `{"at":<s from shot start>,"name":"<effect>","gain":-8}` (+`dur,seed,pitch`; name may be user WAV/MP3). Ambience `{"name":"rain|wind|city|roomtone|murmur|hum","gain":-20}` looped 0.4 s fades, −18…−28. Conventions in §4.7. Max ~2 cues at same instant.
- **B (synthesized in `audio.py`):** whoosh (big moves), thunk (stamps), rumble+crash (collapses), scrape (metal), ting (reveals), sting (twist), creaks, snap, splash, snore, leaves, water ambience. Timed in frames/30. Rewrite cue table per story; synths stay.

---

## 14. Render pipeline (commands, speed, resume)

### 14.1 Engine A

```bash
# install check (once)
python tools/verify_kit.py          # must report 29/29
python tools/doctor.py              # all lines OK; --install auto-fixes npm/playwright/pip
node render.mjs --project examples/reaction-time --sheet --scale 0.3   # self-test: 14 frames, no errors
# per-video
node render.mjs --project projects/<slug> --sheet --scale 0.5          # contact sheets -> build/sheets/sheet_XX.png
node render.mjs --project projects/<slug> --from 0 --to 30 --scale 0.5 # preview -> build/preview.mp4
node render.mjs --project projects/<slug> [--workers N] [--format jpeg] [--gl swiftshader]  # final -> build/video_silent.mp4
python audio/mix.py --project projects/<slug>                          # -> out/<title>.mp4
```

- Workers = half CPU threads (max 8). RAM 0.6–1.5 GB/worker @1080p. No GPU → `--gl swiftshader` (Linux default). `--format jpeg` ~1.5× faster.
- Speed: 720p 2-thread cloud ≈2 fps (47 s ≈10 min); 1080p ~2×; 1440p ~3.5×; 4K ~8×. Desktop 3–5× faster. Long renders: background (`nohup … &`), poll log (prints fps + ETA).
- Partial re-render: re-run whole video (safe) or `--from/--to --out build/fix.mp4` + ffmpeg splice.
- Aspect/resolution change: edit `config.json` (`resolution`, `aspect`). Aspect switch needs fresh sheet review (9:16 framing differs).

### 14.2 Engine B

```bash
bash <skill>/kit/tools/setup.sh ~/shorts/<slug>   # new project
python3 timing.py voice.mp3 script.txt --out work
node render.mjs stills/a "5,40,..."               # look-check stills
python3 sheet.py stills/a stills/sheet_a.jpg
node render.mjs frames "0-<N-1>"                  # full render (run_in_background + Monitor; RESUME=1 continues)
bash finish.sh "Title"                            # encode + QA -> out/<Title>.mp4 + out/qa_sheet.jpg
```

- Chromium: `--use-angle=swiftshader --enable-unsafe-swiftshader --ignore-gpu-blocklist` → CPU WebGL ~3–10 s/frame.
- Requirements: Node 22.6+, Python 3 + numpy + Pillow, ffmpeg, Playwright + Chromium.

### 14.3 Engine C/D (Remotion)

```bash
# C stills (cloud)
scripts/stills.sh <project> a <frames>
# D stills (cloud, half scale, one at a time)
npx remotion still ... --scale=0.5 --gl=swangle --browser-executable=<preinstalled chromium>   # ~90 s each
# user renders on their GPU machine
render.bat   # npm install; npx remotion render src/index.jsx <Id> out\full_silent.mp4 --gl=angle --concurrency=4 --image-format=jpeg --jpeg-quality=92 --crf=17
             # npx remotion ffmpeg -y -i out\full_silent.mp4 -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4
test_render.bat  # 30-frame test
```

- Cloud stills: C 20–40 s each; D ~90 s each. Never render full video in cloud (C ~6 s/frame, ~1.7 s/frame without BokehPass; D many hours, no GPU).
- `.bat` files: CRLF + `pause`. Never send `.bat` alone (Windows browsers block) — inside zip or written into folder.

### 14.4 Final encode profile (all engines — match the 3 MP4s)

- Video: **H.264, CRF 17, `yuv420p`, 30 fps** (A: 24 fps per config; B/C/D: 30 fps). `+faststart`.
- Audio: **AAC, 192k** (B) / 44.1 kHz stereo in the 3 MP4s. Master **−14 LUFS** (A/B), peak **−1 to −1.6 dBFS**.
- QA: `ffprobe` duration ≈ shots duration; audio present; `freezedetect=n=0.0005:d=0.4,blackdetect=d=0.05` empty; `ebur128` ≈ −14 LUFS; contact sheet looks right.

---

## 15. QC checklists

### 15.1 Engine A (run on every contact sheet)

- [ ] No `MISSING SHOT` / red `ERROR` frames; console printed no shot errors.
- [ ] Each picture matches its `line`; key action lands on key word.
- [ ] Characters readable: rim light present, staged against brighter areas, not cut off, not overlapping text.
- [ ] Outfits + screen direction consistent in scene; every character grounded with contact shadow.
- [ ] Moody value structure (mostly dark, 1–3 bright accents), not flat/washed out; colours from mood/style.
- [ ] Every shot has camera motion + atmosphere (dust/rain/particles/glows).
- [ ] Text short, inside safe area, legible at phone size. Numbers match narration.
- [ ] Variety: no more than 3 consecutive same-type/framing shots; close-ups + inserts sprinkled.
- [ ] 9:16: subjects in middle, nothing important under captions.
- [ ] Audio: voice clear, music ducked, no SFX pile-ups, final ≈ −14 LUFS.

### 15.2 Engine B (before full render)

- [ ] Stills at every shot middle + transitions + key actions rendered + sheet viewed.
- [ ] Narrow-frame math checked (characters staged in depth, ±0.8 m @4 m fov 40).
- [ ] No railings/posts across faces; camera path clear of houses/roofs/bushes; no foreground props <2 m; hero not behind pillar.
- [ ] No mirrored text; detached-part offsets correct; extrude groups 0=caps/1=sides+top; ink present (edge-only debug if missing).
- [ ] `phrases.json` pauses at sentence ends; reactions 0–3 frames before words.
- [ ] Mix printout: music −6.0 dB vs voice, SFX ≤ that.
- [ ] After finish: `qa_sheet.jpg` viewed; no frozen ≥0.4 s / black frames.

### 15.3 Engine C/D (stills)

- [ ] Nothing hides face/label/caption; no character cut off at edge; camera not inside wall/car.
- [ ] No room blown out (too yellow/white) or too dark; frames busy enough (fg+mg+bg).
- [ ] Facts on screen correct (2-source rule).
- [ ] Camera clear of characters/props; every move ends at rest; net travel every shot.
- [ ] After render: `ffprobe` (size/fps/duration/audio) + one frame per shot sheet; MP4 + voice-over PDF delivered; what was checked + what is still wrong stated.

---

## 16. Agent runbook — step by step (per engine)

### 16.1 Engine A runbook (8 stages)

1. **Intake (ask once):** voiceover file (required), script (timestamped/plain/none), aspect (16:9/9:16), resolution (720p/1080p/1440p/2160p), captions (on 9:16, off 16:9), music (generated/own/none), SFX (on/off), title. Don't ask style yet. Defaults: 16:9, 1080p, 24 fps, generated music+SFX, style `dusk`.
2. **Install/check:** copy `kit/` → `aitrends-2d-studio/` (skip if `render.mjs` exists; never overwrite `projects/`). `verify_kit.py` (29/29) → `doctor.py` → self-test (`examples/reaction-time --sheet --scale 0.3` → 14 frames, no errors; delete `build/` after). Report install in one short list.
3. **Project + timeline:** `new_project.py` → `parse_script.py` or `transcribe.py` (match ≥90% else tell user script≠audio) → check `transcript.txt` → `beats.py` → draft `shots.json`.
4. **Story breakdown:** read `style-bible.md` + `story-breakdown.md`. Write `story/bible.md` (logline, cast with one signature colour each, locations with moods + key lights, motifs, music plan). Write `scenes/cast.js`. Rewrite `shots.json` (contiguous, cut 0.1–0.2 s early, median 2–3.5 s, establishing per location, concrete `scene` per shot). Send 5–10 line plan summary, continue unless objection.
5. **Style choice:** build 1–2 most-used sets + 3 representative shots (wide ≥2 chars, `bigFace`, data/blueprint/3D). Render `--styles dusk,midnight,golden,neon,storybook --at <t1>,<t2>,<t3> --scale 0.5`. Open `build/styles/style_grid.png`. Show with one line per style. Save pick in `config.json → style`. Custom: add `STYLES` entry, re-render `--styles <newid>,<closest> --at …`.
6. **Build every shot (batches 8–12):** read `engine-api.md` + `examples/reaction-time/scenes/` once. Write `scenes/sets/<location>.js` (anchored `GY`/`CX`, extended past frame) + `scenes/shots/NN_<name>.js` (`registerShot`). Run `--sheet --scale 0.5`. Open every `build/sheets/sheet_XX.png` vs QC checklist. Fix MISSING/errors/composition. Motion check `--stills` / `--from --to` (`build/preview.mp4`). Non-negotiables: rim on every lit figure; colours from `mood()`/`S()`; camera move every shot; atmosphere; moody values; graphics synced via `wordTime()`; `V()` for aspect values; no `Math.random`/`Date.now`.
7. **Sound:** read `sound-design.md`. Fill `shots.json → music` (contiguous moods) + per-shot `sfx`/`amb`. `python audio/mix.py --project projects/<slug>` now to audition `build/mix.wav`.
8. **Render + deliver:** preview `--from 0 --to 30 --scale 0.5` → show user preview/sheet before long render. Final `node render.mjs --project projects/<slug>` (background, poll log, share fps/ETA). `python audio/mix.py --project projects/<slug>` → `out/<title>.mp4`. QC: duration matches, audio present, 1-frame-per-10-s sheet looks right. Deliver MP4 + plain-words location + one line on next tweak.

### 16.2 Engine B runbook (4 stages)

1. **Intake:** if audio attached → Stage 4. If script also given → use for timing. Else ask "Where are you starting from?" (Voiceover ready / Script need voiceover / Need ideas+script) + target length (default 20–30 s; 45–60 s allowed).
2. **Ideas (if needed):** exactly 10 ideas (Title, Hook, Twist, Why it animates well, True or legend). Verify true facts with web search. Ask user to reply with number (or "more").
3. **Script (after pick):** narration only, ~3.7 words/s. Reply with: script block + word count + estimated length; one-paragraph visual plan; recording tips (ElevenLabs deep narrator, speed 1.05–1.1, stability 45–55%, no music); ask "Upload the voiceover when it's ready and I'll make the full video." Keep final script text (drives timing, no ASR needed). Changed version → ask for final text.
4. **Build (after voiceover, no stopping):** 4.0 setup kit → 4.1 timing (`timing.py` → `phrases.json`) → 4.2 shot plan (`PLAN.md` before code) → 4.3 world (`main.js`) → 4.4 cast (`roman.js`→`toon.js`) → 4.5 motion (`motion.js`) → 4.6 look check (stills + sheet, send to user) → 4.7 sound (`audio.py` → `mix.py`, confirm −6 dB) → 4.8 render (`render.mjs frames`) + finish (`finish.sh` → QA sheet) → deliver MP4 + per-shot lines. Offer captions/tweaks/next idea.

### 16.3 Engine C runbook (6 steps)

1. **Ideas (start immediately):** web-search → 5 true stories (hook "[He/They] + [strange action] + [one exact detail]", what moves, twist, 2–3 confirmed numbers/names). Ask "Which one should I write?"
2. **Script:** 10–13 shots, 150–180 words, 55–65 s @170 wpm, beats §6.3. Output `script.md` + `SHOTS.txt` + voice-over PDF. Show shot table, ask "Make the video from this script?"
3. **Voice:** user WAV/MP3 or TTS (3 samples → pick → one generation). `prepare_voice.py RAW.wav SHOTS.txt <project>` → `voiceover.wav` + `timing.json`. "Can't find pause" → fix SHOTS.txt word-for-word, re-run.
4. **Build (automatic):** copy `template/` → `npm install` → timing in place → plan 4–7 locations (`LOC`) → `camera.js PLAN` (preset + anchor + 3 keys + `beats` + `CONT`) → `worlds.js` (signs + `wordT` events) → `dress.js` (fill locations) → replace example signs/magazine/posters.
5. **Check stills (automatic):** `stills.sh <project> a <frames>` (middle of every shot + after each word event). Read sheet: faces/labels/captions visible, no cut-off, camera not in wall/car, not blown out/dark, busy enough, facts correct. Fix + repeat.
6. **Handover:** device tools → `get_device_info` → request folder → commit zip + extract via `device_bash` (rename old `final.mp4` first). Else send zip (never `.bat` alone). Leave out `node_modules/out/final.mp4`. Tell user render.bat line (§6.8). After they render: `ffprobe` + per-shot sheet → deliver MP4 + PDF + what was checked/still wrong + one next step.

### 16.4 Engine D runbook (3 user steps + stages A–F)

1. **Ideas (start here, no questions):** 5 ideas (title, visual hook, escalation but/then/so, 2–3 hard numbers/names). Web-search, drop single-source. Ask "Which one should I write?"
2. **Script:** per §7.3. Show shot table + voice-over text. Ask "Do you want me to make the video from this script?" Edits → ask again.
3. **Make video (after yes):** voice-over (user file / TTS / estimated 3.35 w/s + warn re-time) → stages A (timing → `sentence_times.json` + `CUTS`) → B (art style fixed) → C (characters fixed) → D (worlds at x offsets, procedural) → E (`camera_plan.md` + `warpU` beats + word-tied events) → F (stills at half scale, one at a time, fix until clean). Handover §7.5. After render: `ffprobe` + per-shot sheet → MP4 + PDF + checked/still-wrong + one next step.

---

## 17. Copy-paste prompts for the agent

Paste these verbatim. Replace `<...>` with your values.

### 17.1 Engine A — full video

```
Make a 2D video from this voiceover using the aiTrends 2D Studio pipeline (docs/VIDEO_REPLICATION_BLUEPRINT.md §4 + §16.1).
Voiceover: <path>  Script: <path or none>  Aspect: <16:9|9:16>  Resolution: <720p|1080p|1440p|2160p>  Title: <title>
Follow Stages 1-8 exactly. Keep narration intact. Invent sets/props/actions from this script; style stays fixed.
Draft, look, fix, then render. Three checkpoints: setup choices, style grid, preview before final render.
If I am away, take defaults (16:9, 1080p, 24 fps, generated music+SFX, style dusk), state assumptions, continue.
```

### 17.2 Engine A — stage commands

```
/new-video  Voiceover: <path>  Script: <path or none>  Aspect: <16:9|9:16>  Resolution: <1080p>  Title: <title>
/video-styles  Project: projects/<slug>  (render the 5-style grid from my own shots)
/render-video  Project: projects/<slug>  (build/repair shots in batches, sheet QC, preview, final render)
/video-sound  Project: projects/<slug>  (music plan + SFX + ambience + mix/mux)
```

### 17.3 Engine B — full short

```
Make a vertical cartoon short using the cartoon-audio-short skill (docs/VIDEO_REPLICATION_BLUEPRINT.md §5 + §16.2).
Voiceover: <path>  Script text: <exact final text>  Length: <20-30s|45-60s>
Never edit/re-time the voice. Music at 50% voice (-6 dB via mix.py). Send stills contact sheet before full render.
Output: 1080x1920, 30 fps, exactly as long as voiceover.
```

### 17.4 Engine C — full Short

```
Make a 45-65s vertical story Short using the 3d-story-shorts skill (docs/VIDEO_REPLICATION_BLUEPRINT.md §6 + §16.3).
Idea: <topic or "pick 5 true stories">  Script: <approved script or "write it">
Fact-check everything (2 sources per claim, fact map in script.md). One-word captions, cream dips, busy frames.
Start from template/ copy. Render stills first, then hand over render.bat project.
```

### 17.5 Engine D — full Short

```
Make a 39-65s vertical story video using the animated-3d-story-video skill (docs/VIDEO_REPLICATION_BLUEPRINT.md §7 + §16.4).
Topic: <topic or "pick 5 big-change stories">  Script: <approved script or "write it">
9-12 shots, But/Then/You-see/So beats, warpU beat-synced camera, procedural models, ink #351f22.
Stills at half scale first. Do not render full video in cloud. Hand over render.bat project.
```

### 17.6 Universal QC prompt (after any render)

```
QC this render against docs/VIDEO_REPLICATION_BLUEPRINT.md §15. Check: duration vs shots.json/timing.json,
audio present, loudness -14 LUFS, no MISSING/ERROR frames, rim/ink present, camera moves every shot,
numbers match narration, contact sheet reviewed. List what passed, what failed, and the exact fix for each failure.
```

---

## 18. New project scaffolding (schemas)

### 18.1 Engine A project tree

```
aitrends-2d-studio/
  render.mjs  player.html  package.json
  engine/  core.js  rig2d.js  fx2d.js  ui2d.js  styles.js  three-kit.js  player.js
  audio/   mix.py  music.py  sfx.py  dsp.py
  tools/   new_project.py  parse_script.py  transcribe.py  beats.py  common.py  doctor.py  verify_kit.py
  examples/reaction-time/  (reference project — learn API, do not copy story)
  projects/<slug>/
    config.json
    input/  voiceover.*  script.*  music.* (optional)
    timeline/  transcript.txt  sentences.json (beats output)
    story/  bible.md  shots.json
    scenes/  cast.js  sets/<location>.js  shots/NN_<name>.js
    build/  sheets/  styles/  stills/  preview.mp4  video_silent.mp4  mix.wav
    out/  <title>.mp4
```

`config.json`:
```json
{ "title": "…", "aspect": "16:9", "resolution": "1080p", "fps": 24, "style": "dusk",
  "voiceover": "input/voiceover.mp3", "script": "input/script.txt", "duration": 312.4,
  "captions": false, "captionStyle": { "y": 0.82, "size": 42, "max": 2 },
  "bars": "wide", "fadeIn": 0.5, "fadeOut": 0.8,
  "music": { "enabled": true, "gainDb": -17 }, "sfx": { "enabled": true, "gainDb": -6 },
  "loudness": -14 }
```

`story/shots.json`:
```json
{ "title": "…", "duration": 312.4,
  "shots": [ { "id": "s001", "start": 0, "end": 3.4, "line": "spoken words",
               "scene": "what we see", "set": "cafe", "bars": null,
               "in": { "type": "cut", "dur": 0.4, "dir": 1 },
               "sfx": [{ "at": 0.4, "name": "buzz", "gain": -10 }],
               "amb": { "name": "murmur", "gain": -26 },
               "params": {}, "vignette": true, "captions": true, "notes": "" } ],
  "music": [{ "start": 0, "end": 42, "mood": "mystery", "intensity": 0.4 }],
  "sfx": [{ "t": 120.5, "name": "impact", "gain": -6 }] }
```
`in.type`: `cut|fade|dip|dipWhite|flash|whip|zoom`. `bars`: `null|"wide"|"scope"|"none"|number`.

### 18.2 Engine B project tree

```
~/shorts/<slug>/
  web/  index.html  main.js  story.js  roman.js  toon.js  toonbase.js  motion.js  paint.js  lib/three.module.js
  work/  phrases.json  words.json  PLAN.md
  stills/  a/  sheet_a.jpg
  frames/  f0000.jpg …
  audio.py  mix_raw.wav  mix.wav
  out/  <Title>.mp4  qa_sheet.jpg
```

`story.js` exports: `FPS, TOTAL, SHOTS [{id,a,b,light}], shotAt, camAt, dofAt, LIGHTS/lightFor, worldAt, actorsAt(f,T), fxAt(f,T)`. All pure functions of frame.

### 18.3 Engine C/D project tree

```
<project>/
  src/  index.jsx  Root.jsx  Full.jsx  kit.js  char.js  props.js  dress.js  worlds.js  camera.js  timing.json
  voiceover.wav
  SHOTS.txt  script.md  camera_plan.md  voiceover_script.pdf
  render.bat  render.sh  test_render.bat  check.bat
  out/  full_silent.mp4  final.mp4
```

`SHOTS.txt`: `key | exact spoken text` (numbers as words), spoken order.
`timing.json`: `{ "fps": 30, "duration": 60.29, "shots": [{ "key": "hook", "start": 0.15, "end": 6.423, "words": 19, "text": "…" }] }`.
`camera.js PLAN`: one entry per key: light preset + `anchor` + 3 keys `{p,l}` + `beats: 'words:<key>:0,<word index>,<last>'` + `CONT` set.

---

## 19. Integration with this repo

### 19.1 What already exists

- **`aitrends-2d-studio/`** — Engine A kit installed (render.mjs parallel-worker version, engine/, audio/, tools/, examples/reaction-time, projects/neurological-outbreak, reaction-time-100x, zombie-4-minutes). **Use this for Engine A videos.** The Drive plugin's kit is the same studio (verify with `python tools/verify_kit.py` → 29/29). Do not overwrite `projects/`.
- **`main.py`** — YouTube auto-upload pipeline (personal finance/business niche, max 2/day at 14:00/20:00 ET, AI score ≥85, one topic = one video, Gemini SEO, Sheet history `15jAt6HUoOrucNA-79y8u7hunq7vUUIBMrTOOeiG-618`). Scans Drive `Raw_Videos` + local `videos/`, first-frame OCR + first-20s audio → Gemini score, schedules `publishAt`, moves uploaded files to `Processed`.
- **`google_drive/`** — local copies of Drive files for analysis. **Do not commit** zips/MP4s (large binaries, `.gitignore` already ignores `*.mp4`; add `*.zip`/`*.plugin` if needed). This blueprint (`docs/VIDEO_REPLICATION_BLUEPRINT.md`) is the committed artifact.
- **`past_detour_*`, `projects/rick-outbreak-3d`, `deliverables/`** — earlier experiments. Keep as references; new videos go in `aitrends-2d-studio/projects/<slug>/` (A) or `~/shorts/<slug>/` (B) or `<project>/` (C/D).

### 19.2 Recommended workflow (render → upload)

1. Render with the chosen engine (§14) → `out/<title>.mp4` (A/B) or `final.mp4` (C/D). QC per §15.
2. Copy final MP4 to Drive `Raw_Videos` (or local `videos/`).
3. Run pipeline: `DRY_RUN=true python main.py` (dry) or live via Actions (`repository_dispatch` `publish` with `dry_run=false`, or Actions UI). Never push-triggered live.
4. Pipeline scores (≥85), dedupes topic (first-frame text / first spoken line), books 14:00/20:00 ET slots, writes Gemini title/description/tags, uploads as private with `publishAt`, logs to Sheet, moves file to `Processed`.

### 19.3 Secrets (repo → Settings → Secrets and variables → Actions)

`GOOGLE_CREDENTIALS_JSON` (service account, Drive+Sheet), `GEMINI_API_KEY`, `YOUTUBE_TOKEN_JSON` (live only; must contain `client_id`/`client_secret`/`refresh_token`; split-secret `YOUTUBE_REFRESH_TOKEN` + `YOUTUBE_CLIENT_ID/SECRET` also honoured). Service-account email needs Sheet + Raw/Processed folders as Editor.

---

## 20. Troubleshooting & traps

| Symptom | Cause | Fix |
|---------|-------|-----|
| Fonts look like serif defaults (A) | `@fontsource` missing | `npm install` in `aitrends-2d-studio` |
| `Player failed to boot` (A) | JSON syntax error in shots/config or bad import path | Read message; scene import errors listed at end of render |
| WebGL / 3D shot black (A) | Missing `--gl swiftshader` or Three.js error | Add `--gl swiftshader`; check console (misspelt builder / missing `return {stage}` in init) |
| OOM / crashes at 4K (A) | Too many workers / huge blur | `--workers 1` or `2`; reduce blur on 4K |
| Whisper slow (A) | `small` model | `--model base` |
| Script match <90% (A) | Wrong script or audio | Ask user; re-transcribe |
| Video longer/shorter than audio (A) | `story.duration` ≠ last shot `end` | `beats.py --force` or fix by hand |
| PyAV/`av` errors (A) | ffmpeg not on PATH | Ensure ffmpeg on PATH (tools decode via ffmpeg) |
| Windows paths (A) | Spaces unquoted | Quote paths; use `python`/`py -3` not `python3` |
| "Can't find pause" (C) | SHOTS.txt ≠ audio word-for-word | Fix text, re-run `prepare_voice.py` |
| Mirrored diegetic text (B) | Planar UV flip | Flip UVs; check every sign |
| Missing ink (B) | Edge-only pass broken | Debug edge-only output; ink radius ~2.5 px @1080; sky = far depth, not card |
| Camera inside wall / through lens (all) | Path not checked | Move camera/objects out of line of sight; re-render stills |
| Hero hidden behind pillar / props <2 m (B) | Narrow-frame staging | Stage in depth (±0.8 m @4 m); move fg props back |
| Railings/posts across faces (B) | Camera inside rail or ~2.5 m up | Lower/raise camera or move rail |
| Black polygons / empty openings (D) | Door hole touching bottom edge; facade triangulation | Door = notch, not hole to bottom edge |
| Ground-floor black patches on lifted facades (D) | Known limit, cause not found | Report if appears |
| Frozen spans ≥0.4 s / black frames (B) | Static hold / missing frames | Fix motion; `RESUME=1` re-render; check `qa_sheet.jpg` |
| `.bat` download blocked (C/D) | Windows browsers block `.bat` | Send inside zip or write into folder |
| Render slow on laptop (C/D) | GPU not used | High performance for Remotion browser + Claude app (Settings → System → Display → Graphics), restart app |
| `invalid_grant` YouTube token (repo pipeline) | Refresh token dead / wrong OAuth client / Testing consent (7-day expiry) | Re-mint with same client (Playground "Use your own OAuth credentials" first) or `tools/get_youtube_token.py`; move consent to Production |
| Actions job fails in ~2 s "payments failed" | Billing, not repo | Settings → Billing & plans; settle payment / raise limit |

---

## 21. Appendix — code snippets, hashes, file tree

### 21.1 Key code snippets (copy exactly)

**Engine D `warpU` (monotone cubic time warp, zero speed at ends):**
```js
function warpU(T, t) { // T = beat times per path key; returns path position 0..1
  const n = T.length; if (t <= T[0]) return 0; if (t >= T[n-1]) return 1;
  const sec = []; for (let i = 0; i < n-1; i++) sec.push((1/(n-1)) / (T[i+1]-T[i]));
  const m = [0]; for (let i = 1; i < n-1; i++) m.push(2*sec[i-1]*sec[i]/(sec[i-1]+sec[i])); m.push(0);
  let i = 0; while (t > T[i+1]) i++;
  const h = T[i+1]-T[i], x = (t-T[i])/h, x2 = x*x, x3 = x2*x;
  return (2*x3-3*x2+1)*(i/(n-1)) + (x3-2*x2+x)*h*m[i] + (-2*x3+3*x2)*((i+1)/(n-1)) + (x3-x2)*h*m[i+1];
}
```

**Engine B detached-part alignment:**
```js
y = DECK + (partY - hc) * 0.00225   // hc = headCenter(seed); 1 unit = 0.00225 m
```

**Engine B rebuild cast:**
```bash
cat web/toonbase.js web/roman.js > web/toon.js
```

**Engine C `render.bat` (CRLF + pause):**
```bat
npm install
npx remotion render src/index.jsx <Id> out\full_silent.mp4 --gl=angle --concurrency=4 --image-format=jpeg --jpeg-quality=92 --crf=17
npx remotion ffmpeg -y -i out\full_silent.mp4 -i voiceover.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.mp4
pause
```

**Engine B `finish.sh` encode + QA:**
```bash
ffmpeg -v error -y -i mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=7" -ar 48000 -ac 2 mix.wav
ffmpeg -v error -y -framerate 30 -i frames/f%04d.jpg -i mix.wav -map 0:v:0 -map 1:a:0 -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "out/<Title>.mp4"
ffmpeg -i "out/<Title>.mp4" -vf "freezedetect=n=0.0005:d=0.4,blackdetect=d=0.05" -an -f null - 2>&1 | grep -E "freeze_start|black_start" || true
ffmpeg -i "out/<Title>.mp4" -af ebur128 -f null - 2>&1 | grep -E "^\s+I:" | tail -1
ffmpeg -v error -y -i "out/<Title>.mp4" -vf "fps=2,scale=180:-1,tile=10x4" -frames:v 1 out/qa_sheet.jpg
```

**Engine A final QC sheet:**
```bash
ffmpeg -i out/<file>.mp4 -vf fps=1/10,scale=320:-1,tile=6x5 -frames:v 1 build/final_sheet.png
ffmpeg -i out/<file>.mp4 -af ebur128=framelog=quiet -f null -
```

### 21.2 Drive file hashes (sizes — verify duplicates)

| File | Size (bytes) |
|------|--------------|
| `2e7c07ca…mp4` | 6,674,373 |
| `f12c5efa…mp4` | 7,325,466 |
| `f4345b11…mp4` | 7,002,453 |
| `SKILL.md` | 14,934 |
| `3d-story-shorts.zip` = `3d-story-shorts (1).zip` | 458,984 (identical) |
| `animated-story-video.skill.zip` | 5,231 |
| `cartoon-short-kit.zip` = `cartoon-short-kit (1).zip` | 444,936 (identical) |
| `hoover_dam_short.zip` | 6,124,522 |
| `aitrends-2d-studio (2).plugin` | 118,134 |
| `Cartoon audio short - Claude` (MHTML) | 3,341,587 |

### 21.3 Uncompressed file trees (what's inside each zip)

**`3d-story-shorts.zip` (30 files, 610,610 B):**
```
3d-story-shorts/SKILL.md
3d-story-shorts/scripts/prepare_voice.py  stills.sh  SHOTS_example.txt
3d-story-shorts/example/SHOTS.txt  script.md  voiceover_script.pdf  final_look_frames.jpg
3d-story-shorts/template/src/kit.js  char.js  props.js  dress.js  worlds.js  camera.js  Full.jsx  Root.jsx  index.jsx  timing.json
3d-story-shorts/template/package.json  package-lock.json  render.bat  render.sh  test_render.bat  check.bat  camera_plan.md
```

**`cartoon-short-kit.zip` (19 files, 508,309 B):**
```
cartoon-short-kit/README.md
cartoon-short-kit/engine/main.js  roman.js  motion.js  paint.js  index.html
cartoon-short-kit/example/soldier/story.js  audio.py  stills.jpg
cartoon-short-kit/tools/setup.sh  timing.py  render.mjs  sheet.py  finish.sh
```

**`animated-story-video.skill.zip` (1 file, 10,578 B):**
```
animated-3d-story-video/SKILL.md
```

**`hoover_dam_short.zip` (21 files, 11,790,738 B):**
```
hoover/SHOTS.txt  camera_plan.md  voiceover.wav (11,584,362 B)
hoover/src/kit.js  char.js  props.js  dress.js  worlds.js  camera.js  Full.jsx  Root.jsx  index.jsx  timing.json
hoover/package.json  package-lock.json  render.bat  render.sh  test_render.bat  check.bat
```

**`aitrends-2d-studio.plugin` (61 files, 266,181 B):**
```
.claude-plugin/plugin.json  README.md
skills/make-2d-video/SKILL.md  references/{install,style-bible,story-breakdown,engine-api,sound-design,render-qc}.md
skills/make-2d-video/kit/engine/{core,rig2d,fx2d,ui2d,styles,three-kit,player}.js
skills/make-2d-video/kit/audio/{mix,music,sfx,dsp}.py
skills/make-2d-video/kit/tools/{new_project,parse_script,transcribe,beats,common,doctor,verify_kit}.py
skills/make-2d-video/kit/render.mjs  player.html  package.json
skills/make-2d-video/kit/examples/reaction-time/{config.json,story/{bible.md,shots.json},scenes/{cast.js,sets/{cafe,lab}.js,shots/{01_cafe,02_orbit3d,03_explain}.js}}
skills/{new-video,render-video,video-sound,video-styles}/SKILL.md
```

---

*End of blueprint. Follow §16 runbook + §17 prompts. Style is fixed — only the story changes.*

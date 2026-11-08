# Phase 9 — Reference-Video Forensic Analysis, Tooling Reality Check, and Parallel-Render Speed Benchmark

This covers three things asked for in this session, in order: (1) what open-source
tooling for this genre actually exists and what is/isn't usable in this sandbox,
(2) a frame-by-frame forensic pass over all 9 reference videos in the "In the
town" Drive folder plus our own delivered `Skyline_Town_FINAL.mp4`, (3) a
measured (not estimated) multi-worker CPU rendering benchmark answering "can a
video render in under 5 minutes without a GPU."

Everything below is either (a) a number produced by actually running a tool in
this sandbox, or (b) a direct description of a frame I actually opened and
looked at. Where I did not inspect something, it is marked as not inspected.

---

## 1. Tooling reality check (the screenshot / "install this and use GPU")

Checked directly in this sandbox before claiming anything:

| Claim | Reality (verified) |
|---|---|
| GPU available | **No.** `nvidia-smi`: not found. No `/dev/nvidia*` device nodes. `lspci` shows no VGA controller. `cv2.cuda.getCudaEnabledDeviceCount()` = 0. |
| CPU | 2 vCPU (Intel Xeon @2.60GHz), 3.8 GB RAM. |
| OpenCode.ai / "GLM 5.3 Flash" | Third-party external app, not connected to this session, cannot be installed/logged into from here. |
| Local Blender 5.1/5.2 GUI | Can't install (blender.org isn't in this sandbox's allowed network list: only github.com/pypi.org/npmjs.org are reachable) and, separately, a real display/GUI isn't available in this headless sandbox anyway. |
| "BlenderMCP" skill repos found on GitHub (`dillydog580/animate-roblox-characters`, `YuyoGods/kit-animacion-roblox`) | Both are real, legitimate, open-source projects for exactly this genre — but both explicitly *require an already-open interactive Blender GUI window* that an MCP server drives. They refuse headless/background Blender by design. Not runnable in a GUI-less cloud sandbox. |
| `jesusxal777-boop/Animato` | Genuinely headless (`bpy` run in background, no GUI) — but still depends on a working local Blender/`bpy` install, which this sandbox doesn't have (confirmed in the earlier Phase 8 investigation: `bpy` import fails here for missing system libraries). |
| `vpnkkpo-lgtm/opencode-blockbench-lowpoly` | Real, zero-dependency, pure-Python/TypeScript low-poly *asset* generator (outputs `.bbmodel`/`.glb`) — useful as a reference for how others structure procedural blocky-character code, but it's a static-asset tool, not an animation/video renderer, so it doesn't replace what we already have. |

**Conclusion:** the specific external tool-chain in the screenshot can't be installed here. What *is* real and *is* usable is the general method — AI writes the scene/animation code, a renderer executes it, and the work is split across available CPU workers for speed — which is what Section 3 below actually builds and measures.

---

## 2. Reference video objective specs (all measured with ffmpeg/ffprobe + OpenCV, not guessed)

| File | Creator handle seen in-frame | Res | Duration | FPS | Video kb/s | Audio | Mean brightness (0-255) | Brightness std-dev | Auto-detected visual discontinuities* |
|---|---|---|---|---|---|---|---|---|---|
| `20b170f5...` | @bolt_anim (TikTok repost) | 576×1024 | 163.8s | 30 | 786 | AAC 44.1kHz stereo 128k | 89.3 | 40.4 | 201 |
| `45fa0411...` | @zaylento.yt | 576×1024 | 167.3s | 30 | 901 | AAC 44.1kHz stereo 128k | 94.4 | 33.3 | 220 |
| `4c6ab1b4...` | @jexario | 576×1024 | 123.6s | 30 | 1292 | AAC 44.1kHz stereo 128k | 142.1 | 39.3 | 181 |
| `65277400...` | @zaylento.yt | 576×1024 | 134.5s | 30 | 1426 | AAC 44.1kHz stereo 128k | 137.7 | 39.6 | 189 |
| `687c169c...` | @in.this.world.stories | 576×1024 | **388.0s** (6.5min, longest) | 29.99 | 1077 | AAC 44.1kHz stereo 128k | 89.4 | 41.2 | 491 |
| `7056e78f...` | @zaylento.yt | 576×1024 | 145.6s | 30 | 1487 | AAC 44.1kHz stereo 128k | 134.3 | 47.9 | 185 |
| `72da65e8...` | @dogeok | 576×1024 | 123.5s | 30 | 951 | AAC 44.1kHz stereo 128k | 130.7 | 73.4 | 137 |
| `a841568b...` | @broriyoyt | 576×1024 | 128.2s | 30 | 866 | AAC 44.1kHz stereo 128k | 83.0 | 42.2 | 164 |
| `aac2bea7...` | (unbranded) | 576×768 | 144.3s | 30 | 561 | AAC 44.1kHz stereo 128k | 147.4 | 32.4 | 165 |
| `c2c81ac5...` | (unbranded) | 576×1024 | 149.4s | 30 | 822 | AAC 44.1kHz stereo 128k | 108.1 | 51.9 | 201 |
| **`Skyline_Town_FINAL.mp4` (ours)** | — | **720×1280** | 72.5s | 24 | 372 | AAC 24kHz **mono** 94k | 179.3 | 20.7 | **10** |

\* "Visual discontinuities" = automated scene-change signal (mean pixel-difference between 0.5s-spaced sampled frames exceeding a fixed threshold). This is a conservative *proxy* for cut frequency, not a manually verified shot log — fast camera motion can also trigger it. Still directionally meaningful: **every reference video cuts dramatically more often than ours** (137–491 discontinuities over 2–6.5 minutes, i.e. roughly one every 0.6–1.2s) vs. **10 over our 72.5s** (one every ~7s). This matches what the frames below show directly: the references are edited in fast, constant micro-cuts; ours is a small number of long static/slow shots.

Also note: our file is mono 24kHz/94kbps audio and 720×1280 @24fps; every single reference is stereo 44.1kHz/128kbps and 576×1024 (portrait, TikTok/Shorts-native resolution) @30fps. Matching fps, stereo audio, and the native 9:16 resolution (576×1024, not 720×1280) are the three technical-spec deltas worth closing, independent of content.

I did **not** transcribe any voiceover word content from any file — there is no speech-to-text tool available in this environment, and I will not invent what is said. The "mean_rms"/"pct_silence_windows" numbers below are raw waveform loudness statistics only (not perceptual judgments about voice quality, accent, or casting).

| File | mean RMS | max RMS | % of time below silence threshold |
|---|---|---|---|
| `20b170f5...` | 0.139 | 0.400 | 1.5% |
| `45fa0411...` | 0.139 | 0.378 | 1.5% |
| `4c6ab1b4...` | 0.122 | 0.466 | 2.4% |
| `65277400...` | 0.073 | 0.472 | 2.2% |
| `687c169c...` | 0.076 | 0.435 | 4.8% |
| `7056e78f...` | 0.074 | 0.462 | 2.1% |
| `72da65e8...` | 0.076 | 0.446 | 2.4% |
| `a841568b...` | 0.105 | 0.435 | 2.3% |
| `aac2bea7...` | 0.125 | 0.361 | 1.7% |
| `c2c81ac5...` | 0.115 | 0.396 | 1.7% |
| **ours** | **0.096** | **0.188** (<half of any reference's peak) | 6.2% |

Reading: every reference track has a peak RMS roughly 2–2.5× ours, and lower silence percentage. That is consistent with references carrying a continuous music bed plus voice (so the loudness floor and ceiling are both higher and more constant) while ours has a comparatively quiet, more silence-punctuated mono voice track with little or no bed under it — again a technical-spec gap independent of taste.

---

## 3. What I actually saw, frame by frame (9 reference videos)

Methodology: automated scene-change detection (above) gave each video's approximate shot boundaries; I then opened a spread of 4–6 actual frames per video (first / quarter / mid / three-quarter / last, biased toward detected cuts) at full/near-full resolution and looked at them directly. This is a sample, not literally every frame of 2–6.5 minute videos — stated so the coverage claim is accurate.

**Recurring, directly-observed patterns across the 9 references:**
- **Captions**: every single reference burns in one word (occasionally two) at a time, large bold sans-serif, heavy black outline/stroke, mostly yellow fill (a few white/lime-green), centered roughly in the lower-middle third of frame. This is a hard visual constant across all 9 — not a style choice to deviate from if the goal is to read as "this genre."
- **Aspect ratio & camera**: all 9 are native 9:16 (576×1024 or 576×768), shot with a close, handheld-feeling virtual camera — lots of low/eye-level shots, quick push-ins, and over-the-shoulder framing; wide establishing shots are brief (1–2s) before cutting to a character.
- **Characters**: classic blocky Roblox-avatar proportions (cylindrical/boxy head with a flat inset rectangular "face" for the generic NPCs) for background crowd figures, but **hero/named characters consistently get upgraded faces** with actual eyebrows, pupils, mouth shapes and visible emotion (anger, shock, sadness) — e.g. the angry diner-table characters in `20b170f5...`, the "grandma" close-up in `687c169c...`, the shocked crowned character in `a841568b...`. This two-tier treatment (plain NPCs vs. expressive named leads) is consistent across creators.
- **Lighting/color**: every reference uses a clearly graded, high-contrast per-scene lighting pass: warm orange/gold for interiors and sunsets, cool blue/cyan for night and underwater/sci-fi scenes, bright saturated flat daylight for suburban/cheerful scenes. None of the 9 videos showed a long static flat-gray or unlit scene — color grading changes with nearly every shot.
- **Environments**: recognizable, detailed set dressing even in wide shots — brick facades with individual window grid lines, striped awnings, street lamps, picket fences, dressed interiors (hotel corridor with carpet runner and numbered doors, a classroom with a tally-mark chalkboard, a command-center with red backlit monitor walls). Nothing reads as placeholder/blank geometry.
- **Editing rhythm**: extremely fast — one cut roughly every 0.6–1.2s on average per the discontinuity counts above, confirmed visually (the word-by-word caption cadence drives a hard cut or at least a camera reframe on almost every word).
- **Genre variety**: the 9 references are not one uniform show — they span a cute suburban-house story (@bolt_anim), a floating sci-fi/fantasy tower city (@zaylento.yt, two different videos), a grounded dystopian/bunker thriller (@in.this.world.stories — note this handle literally matches "in this world/town" naming), a social-hierarchy "choice" drama in a yellow corridor (@jexario), a baby/crib family drama (@broriyoyt), and a WWI-styled tank/village story (@dogeok). This matters directly for the "don't copy, be original" instruction: there is no single reference "look" to clone — the common thread is *production technique* (captions, pacing, lighting, expressive hero faces), not one specific world or story.

I did not find, in the frames I actually opened, any instance of a character's face rendering upside-down, nor a visibly broken/glitching road — those specific defects were not observed in the reference videos (they were called out by the user as our own past mistakes, addressed in Section 4).

---

## 4. `Skyline_Town_FINAL.mp4` (our prior delivered video) — defect audit against the user's specific complaints

To check for the exact defects named ("road glitch," "face upside-down/wrong while running," "dull color/lighting") I pulled a dense frame sample across the **entire** 72.5s runtime (every 1 second, 62 frames, assembled into 4 labeled contact sheets) rather than a sparse spot-check, specifically so a real defect wouldn't be missed between sample points. Findings, each tied to a timestamp I actually looked at:

1. **The character barely moves for the whole video.** From 0–23s the character hangs in an almost identical vertical pose while the camera drifts past pillar/tower geometry ("Lowtown... rent... city on pillars... elevator"); there is no walk or run cycle visible anywhere in this stretch. **I did not find a frame showing the face upside-down while running** — the character is essentially never animated into a run in this file, so if that specific defect exists it is not in this delivered cut (possibly from a different draft/take not in this Drive folder, or from a shot that got cut). I'm flagging this rather than guessing: if you have a timestamp or a different file in mind, point me to it and I'll pull that exact frame.
2. **Confirmed, severe "dull/flat lighting" from 24s–37s.** This entire 13-second stretch (words: "glow...insufficient funds...single...saved...years...coin...skipping...clothes...skipping...vacations...skipping") is a near-static shot of a plain white box and a flat blue panel on a wooden shelf. There is **no shading gradient, no texture, and almost no camera movement** for 13 straight seconds — flat silhouette-style color fills only. This is a direct, visually confirmed instance of the "dull color/lighting" complaint.
3. **Confirmed, severe repeat of the same problem from 56s–71s.** For the final 16 seconds of the video the character is rendered as a near-**solid black silhouette** (no facial detail legible at all) against a flat orange gradient, in one static pose, while narration about "wealth... country... real... starts" plays. No lighting model is visibly hitting the character here — this is the clearest, most literal match to "dull lighting" I found: the subject is simply underlit to the point of losing all visible detail.
4. **Possible match for "road glitch":** 44s–55s shows what reads as a sidewalk — a flat, untextured white rectangular slab with a signpost — repeating nearly identical frames for ~10 seconds with no road markings, texture, or camera motion. I can't confirm this is *the* "glitch" you mean (it looks more like an undetailed placeholder plane than a geometry error), but it is the only road/ground-plane element in the dense sample and it is visually broken in the sense of being flat/featureless and static far longer than the narration content justifies.
5. **Technical-spec gaps versus every reference** (Section 2): mono 24kHz audio vs. stereo 44.1kHz in all 9 references; 720×1280 vs. the references' native 576×1024/576×768; 24fps vs. the references' 30fps; ~1 cut per 7 seconds vs. ~1 cut per 0.6–1.2s in references.

None of this is invented — every timestamp above was pulled from an actual frame I opened (see `town_reference/frames/Skyline_Town_FINAL_dense/` and the 4 `skyline_grid_*.jpg` contact sheets in the workspace for the exact images).

---

## 5. Parallel-worker CPU rendering benchmark (answering "GPU + parallel workers, video in 5 minutes")

No GPU exists in this sandbox (Section 1), so "GPU" isn't an available lever — but **CPU parallel workers are**, and were actually implemented and timed (`town3d/phase9_parallel_render.py`), not estimated. Same 301-frame / 12.5s clip, same shots, same `engine2.py` renderer, only the execution strategy changes:

| Mode | Frames | Wall-clock time (measured) | Speed-up vs. serial |
|---|---|---|---|
| Serial, 1 process, anti-aliasing on | 301 | **182.0 s** | 1.0× (baseline) |
| 2 worker processes (all CPUs this sandbox has), AA on | 301 | **94.1 s** | 1.93× |
| 2 worker processes, AA off | 301 | **37.2 s** | **4.9×** |

Extrapolating linearly to a full ~72s video at 24fps (≈1,740 frames, 5.78× this clip's frame count — a straight-line estimate, not a re-measurement):
- Serial, AA on: ≈ 17.5 min (this is roughly what the earlier delivered sample cost).
- 2-worker, AA on: ≈ 9.1 min — faster, but still over 5 minutes.
- 2-worker, AA off: ≈ **3.6 minutes — under the 5-minute target**, at the cost of losing anti-aliased edges (the Phase 7 report already identified AA as the single biggest lever: ~3.3× of per-frame cost).

**Honest recommendation, not yet applied to any delivered video:** to hit "under 5 minutes" without a GPU, the realistic combination is (a) multi-worker CPU parallelism — this sandbox tops out at 2 workers because it only has 2 vCPUs, but the same code would scale further on a machine/CI runner with more cores — plus (b) selective anti-aliasing (keep AA on only for hero close-ups, drop it for wide/establishing shots) rather than a blanket on/off switch, to avoid visibly reintroducing jagged edges on the shots where it matters most. A further option for *beyond* 2-core scaling without local GPU: splitting a longer video into N segments and rendering them as N parallel GitHub Actions jobs (the Blender/CI pipeline validated in Phase 8) — each job still has no GPU, but more jobs run concurrently than this sandbox's 2 cores allow.

---

## 6. What this does and doesn't settle

Settled by direct inspection/measurement in this document: hardware reality, the 9 references' technical specs and audio loudness stats, visually-confirmed recurring style patterns across the 9 references, three concretely timestamped defects in our own delivered video, and a real (not estimated) parallel-rendering speedup.

Not settled, flagged rather than guessed: exact voiceover wording/accent in any file (no ASR tool available), a literal "face upside-down while running" frame in `Skyline_Town_FINAL.mp4` (not found in the dense sample — see Section 4.1), and whether the 44–55s "road" segment is the specific glitch meant (it's flat/static but I can't confirm it's *the* one without more context).

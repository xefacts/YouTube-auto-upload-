# Phase 1 Report — Reference Analysis + Engine Ground Truth

Date: 2026-11-08 · Branch: `arena/e214acd9-youtube-auto-upload`
Scope: reverse-engineer target look, establish what renders for real, pick the
engine by **test results, not assumptions**. No video has been produced for
approval yet — sample first, full render only after user sign-off.

---

## 1. Reference look analysis (real pixel measurements)

Source: 4 vertical reference clips from Drive folder "In the town" — contact
sheets in `video_studio/analysis/` (ours vs top reference:
`compare_sheet.jpg`, second reference: `flannan_sheet.jpg`).

| Metric (8-frame avg) | ref1 (Flannan-style) | ref2 | ref3 | ref4 (dark) | ours (Skyline Town, town3d) |
|---|---|---|---|---|---|
| Luminance mean (0-255) | 156.1 | 131.2 | 117.0 | 57.4 | 177.8 |
| Luminance std (contrast) | 49.4 | 52.9 | 60.2 | 42.9 | 47.6 |
| Saturation mean | 0.394 | 0.435 | 0.494 | 0.548 | 0.325 |
| Edge density (px %) | 8.52 | 9.89 | 7.66 | 6.12 | **2.81** |
| Flat-color ratio | 0.64 | 0.69 | 0.67 | 0.75 | **0.93** |
| Dark-pixel ratio | 6.6% | 25% | 30.3% | 63.4% | 7.2% |
| Palette top colors | #90c8fa #74b9fd #aed1f5 (sky blues) | … | … | … | sky blue + flats |

**Reading (technical, not artistic):**
- Target look = bright pastel-blue sky, saturated flat colors, moderate
  contrast, ~64-75% flat shading with ~7-10% detail edges.
- Our existing town3d software renders are **flatter (93%) and blander
  (edge 2.8% vs 8.5%)** than the reference style: the refs carry more surface
  detail, baked AO/edge lighting and richer color separation.
- Motion: references average ~1.5 cuts/pan-heavy camera per 2 s; ours is
  slower (this is a composition choice, measurable in `metrics.json`).

**Methodology note (no vision in this session):** all numbers above are
computed by code (Pillow/NumPy histograms, gradients, palette k-means) on
real frames — no human or AI "looked" at the frames and scored them. This is
deliberate: technical QC must be measurable; it cannot certify artistic
quality. Artistic judgment stays with the user at the sample-approval gate.

## 2. Engine ground truth (what actually renders)

Two real candidates exist today; both have produced rendered pixels:

| Test | Result |
|---|---|
| `bpy` 5.0.1 wheel in this sandbox | **WORKS after stub-lib fix** — `import bpy` + Cycles CPU renders verified locally. ~5.9 s/frame @320×568×16spp, ~12.7 s @405×720×32spp (2 cores). Stub recipe persisted: `video_studio/engine/stublibs/rebuild.sh`. |
| Official portable Blender on GitHub Actions (ubuntu-latest, Cycles CPU) | **WORKS** — JOB-0001 (72 frames, 480×854, 32 spp) ran end-to-end: download → headless render → ffmpeg mp4 → artifact. See §3. |
| town3d software renderer (numpy+Pillow rasterizer) | WORKS — produced the full 73 s "Skyline Town" short (parallel session branch `arena/0abc33e0`, `town3d/`). |
| GPU anywhere | **Not present** in sandbox; Actions standard runners = CPU only. No fake "GPU rendering" is claimed anywhere. |
| ModernGL / GPU in sandbox | Dead (no libGL device, no /dev/dri) — confirmed by audit, not retried. |

**Engine selection principle (per user rule):** chosen by measured results —
render time, visual fidelity vs §1 targets, reliability, cost. Actions-Blender
gives true raytraced lighting/materials (closes the edge-density/flatness gap
to the reference look); town3d is faster to iterate and already integrated
with captions/narration. Comparison sample renders are the deciding evidence.

## 3. JOB-0001 — Blender CPU render on GitHub Actions

- Workflow: `.github/workflows/blender_render.yml` (push-trigger on
  `video_studio/**` changes + manual dispatch once merged to main).
- Job spec: `video_studio/render_jobs/JOB-0001-blender-cpu-test/job.json`
  (scene_city, frames 1-72, 480×854, 32 spp, 24 fps).
- Scene: `video_studio/engine/blender/scene_city.py` — original blocky avatar
  (original design: head/hair/face/jacket/limbs/shoes), city block (road,
  sidewalks, ~14 procedural-facade buildings, streetlights, trees, bench,
  hydrant), walk-cycle with narrative pause+head-turn, cinematic camera
  (aerial establish → track → low hero close-up → pull-back), sun+area
  lights, flat sky. Deterministic (seed 42), writes `timing.json`.
- Runs: 42464590811 (render ok, encode fixed) + 42466623847 (full success).
  Artifact `blender-render` (72 PNGs + mp4 + report, 31 MB).
- Deliverables published to branch by `publish_render.yml` (Actions runner
  downloads the artifact and commits it — the sandbox allowlist blocks
  blob.core.windows.net, so artifacts are otherwise unreachable from here):
  `video_studio/outputs/JOB-0001/` (sample.mp4, render_report.json,
  timing.json, render_log.txt, contact_sheet.jpg).
- **RESULT: pipeline WORKS end-to-end on Blender 5.2.3 LTS / 4-core runner —
  72 frames @ 480x854x32spp, avg 21.3 s/frame, 25.5 min total, free.**
- **Real defect found by pixel QC and fixed:** frames 48-62 (~2.0-2.6 s) were
  pure black — the camera's first aerial key (16,-30,26) descended diagonally
  straight through a building in the right row (buildings occupy x≈7..13.5).
  Camera path re-routed to stay over the road corridor (|x|<=4.4) whenever
  below rooftop height; re-verified locally (f1/40/56/60/72 all mean 129-135,
  std 42-47, zero dark/blank flags). JOB-0002 re-render queued.
- Sandbox-vs-cloud note: same scene rendered identically on bpy 5.0.1
  (sandbox) and Blender 5.2.3 LTS (runner) — the defensive node-input code
  paid off; the black frames reproduced in BOTH, proving it was a scene bug,
  not a version difference.

## 4. Local vs cloud render comparison

| Configuration | Resolution | Samples | s/frame | Cores |
|---|---|---|---|---|
| Sandbox bpy (stub libs) | 320×568 | 16 | 5.9 | 2 |
| Sandbox bpy (stub libs) | 405×720 | 32 | 12.7 | 2 |
| Actions Blender 5.2.3 LTS (JOB-0001) | 480×854 | 32 | 21.3 | 4 |

Cloud ≈ free (public repo standard runners), durable artifacts, survives
sandbox resets → **Actions is the primary production renderer; sandbox bpy is
the dev/QC loop.**

## 5. What Phase 1 does NOT claim

- No claim the renders are "beautiful" — brightness/sharpness stats cannot
  grade art. The sample goes to the user for the artistic verdict.
- No GPU claim. No Whisper/transcription claim (network-blocked weights).
- OpenCV video decode remains broken in-sandbox (QC runs on in-memory
  arrays / PNG frames — same approach as town3d/qc.py).

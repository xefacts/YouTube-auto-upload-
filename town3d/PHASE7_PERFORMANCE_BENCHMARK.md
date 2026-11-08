# Phase 7 — Performance Benchmark (v1 vs v2), measured, not estimated

All numbers below were produced by actually running both renderers in this
sandbox and timing them with `time.time()` / `time.process_time()` /
`resource.getrusage()`. No number in this document is estimated or
extrapolated from documentation.

## Method

Both renderers were benchmarked **at the same 540×960 output resolution**,
rendering 60 frames of a representative scene, with timing isolated to the
render call itself (no ffmpeg encoding or disk I/O inside the timed loop).

- v1: `town3d/engine.py` `render_frame()`, scene = `scenes.scene_1_lowtown()`
  (82 `Box` primitives — houses, pillars, a person, ground/road).
- v2: `town3d/engine2.py` `render_frame2()`, scene = a full
  `build_city_block()` (buildings/road/sidewalks/trees/streetlights) plus one
  `Character` plus 8 `PointLight`s plus a shadow blob — 2,924 triangulated
  faces total, with 2×2 supersampled anti-aliasing (the setting actually used
  for the delivered Phase 5 sample).

## Results

| Metric | v1 (`engine.py`) | v2 (`engine2.py`, AA on) | v2 (`engine2.py`, AA off) |
|---|---|---|---|
| Resolution | 540×960 | 540×960 | 540×960 |
| Scene complexity | 82 boxes (~492 faces) | 2,924 faces | 2,924 faces |
| Frames rendered | 60 | 60 | 60 |
| Total render time | 1.10 s | 35.71 s | 10.93 s |
| Time per frame | **18.3 ms** | **595.2 ms** | 182.2 ms |
| Frame rate | **54.8 fps** | **1.68 fps** | 5.49 fps |
| CPU time / wall time | 104.2% (effectively 1 core) | 99.9% (1 core, no parallelism) | — |
| Peak resident memory | 38.2 MB | 357.1 MB | — |

(Isolating the AA cost: disabling the 2×2 supersample drops v2's per-frame
time from 595.2 ms to 182.2 ms — anti-aliasing alone accounts for roughly
3.3× of v2's total per-frame cost. The remaining ~182 ms vs. v1's 18.3 ms,
about 10× even with AA off, is the real cost of the much larger scene: ~6×
more faces, per-pixel z-buffering against all of them, up to 8 per-pixel
point lights with real distance attenuation, near-plane polygon clipping,
and blob-shadow compositing — none of which v1 does at all.)

For reference, the full Phase 5 pipeline (301 frames at 540×960, piped
live into ffmpeg/libx264 encoding concurrently with rendering) took 180.1 s
end-to-end, i.e. 598 ms/frame including encode overhead — consistent with
the isolated 595.2 ms/frame render-only number above, meaning encoding adds
negligible overhead on top of rendering in this pipeline.

## Honest interpretation

**v2 is roughly 32× slower per frame than v1 at matched resolution**, and
uses about 9× more peak memory. This is a real, substantial cost — not
hidden or minimized. It buys real, inspected visual improvements (Phase 1
comparison): a textured-looking face instead of a blank box, windowed
building facades instead of flat walls, multiple real point lights with
distance falloff instead of a single ambient+directional term, anti-aliased
edges instead of jagged ones, and correct near-plane polygon clipping
instead of whole-face rejection.

Per the standing instruction not to sacrifice visual quality for speed, no
attempt was made to strip v2 back down to v1's frame budget — the honest
trade-off is reported as-is. If render time becomes a hard constraint for a
full-length video, the available levers, in order of expected impact with
least quality loss, are: (1) drop supersampling from 2× to disable it only
on interior/establishing shots where edges matter less (~3.3× saved), (2)
cap point lights actually evaluated per pixel via a cheaper broad-phase
culling (today all 8 lights are evaluated against every lit pixel
regardless of distance), (3) render at a lower resolution and let ffmpeg
upscale for non-hero shots. None of these were applied to the delivered
Phase 5 sample, which was rendered at full intended quality.

## Why GPU rendering was not used to close this gap

No GPU is available in this sandbox (confirmed previously: ModernGL/GPU
context creation fails) and GitHub Actions' standard hosted runners are
CPU-only (see `PHASE8_RENDERER_INVESTIGATION.md`) — so neither renderer in
this comparison had GPU acceleration available, and none was assumed.

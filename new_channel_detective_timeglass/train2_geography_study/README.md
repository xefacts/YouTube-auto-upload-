# Train 2 — experimental geography motion style study

An **original, private style test** based on the nine user-supplied Train 2 videos. It does not revise the Florida mystery episode or publish anything to YouTube. Deliverables are four 1080×1920 PNG sequence keyframes, a terrain backplate, five modular transparent RGBA overlays, and a silent six-second motion test (144 frames/24 fps). The source videos remain in the user's Drive folder; **their actual video pixels, logos, edit UI, characters, narration, maps and text are not pasted into the deliverables**.

## What was studied

The five geography shorts share the most relevant visual grammar:

| Reference | Observed treatment | What was translated into this test |
| --- | --- | --- |
| `Why Animals Don't Cross This Invisible Border` | Satellite-like terrain/bathymetry, bright segmented pink-white boundary with bloom, localized cutout evidence, a moving crop, small white lower subtitle. | Optional independent magenta dash overlay with a broad soft glow and white hot core; no animals or Wallace geography copied. |
| `The Darien Gap` | Green region glow over land, thick yellow tracing route and close-to-wide geographic moves. | Land-highlight overlay that retains texture beneath the glow; route draw-on replaces that video's yellow highway. |
| `Who Celebrates New Year First` | Cyan precise stepped line, bright point nodes, coastal turquoise shelves, short lower captions. | Cyan route with a white optical core and a reusable beacon pin over an original Gulf/Florida study image. |
| `Why Do Time Zones Look So Strange` | Thin geographic overlays and grids on textured maps, quick move between global and regional scales, readable subject hierarchy. | Separate transparent labels/route/region, restrained push-in instead of a busy grid over the entire shot. |
| `The Distance Between the US and Russia is Less Than You Think` | Zoom from a large map to small coast details and focused contrasting labels. | Distinct overview, region and route stages with one focal change per beat. |

The remaining four (`Tuk-Tuk Vox Style`, `Thai Ghosts`, `Would you buy it`, `The Midnight Monster Show`) are primarily **screen recordings of their editing timelines** and use archival collage/comic cuts. Their software chrome is not part of this geography look. They reinforced the need for deliberate sequencing and one focal visual at a time, but none of their figures or collage art are used here.

## Outputs

- `png/00_atlas_backplate.png` — high-resolution graded illustrative base, 1080×1920 RGB.
- `png/01..04_geography_frame.png` — full-frame progression: overview → Florida region glow → route draw-on → endpoint beacon; 1080×1920 RGB.
- `png/element_florida_region_glow_RGBA.png` — 1080×1920 RGBA tinted region and rim; keeps underlying terrain visible.
- `png/element_cyan_route_glow_RGBA.png` — 1080×1920 RGBA optical route bloom and core, separately animatable.
- `png/element_magenta_dashed_trace_RGBA.png` — **optional** 1080×1920 RGBA segmented glow (not composited into the main sample; not a claimed political or biological boundary).
- `png/element_atlas_labels_RGBA.png` — 1080×1920 RGBA typography over transparent map space.
- `png/element_beacon_pin_RGBA.png` — 400×400 reusable RGBA endpoint marker; place its center at `(647,929)` for this sample.
- `GEOGRAPHY_STYLE_MOTION_PREVIEW_1080x1920.mp4` — silent six-second continuous camera/route animation, **not** a new episode or a licensed replacement for the reference videos.

The underlying `assets/florida_gulf_relief_backplate.png` is newly AI-illustrated using user-provided map-video frames as **style references**, then all highlights, labels, glow passes, elements and motion were drawn in code. It resembles a textured atlas but is **not GIS-verified satellite imagery**. The route/marker and any boundary motif are design demonstrations, **not factual hotel coordinates, travel paths, political borders or geospatial claims**. Before any geographic claim is published, replace the illustrative backplate with rights-cleared verified map data and georeferenced labels. The user requested visual similarity; exact source pixels or a guaranteed pixel-perfect clone are intentionally not asserted.

Rebuild: `python build_study.py` with Pillow, NumPy, OpenCV and ffmpeg (or imageio-ffmpeg) installed. Each overlay has true alpha; stack over `00_atlas_backplate.png` and animate its opacity/scale. The provided motion test intentionally has no audio.

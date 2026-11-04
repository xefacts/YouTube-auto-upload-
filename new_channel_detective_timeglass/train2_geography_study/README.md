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

## Complete 36-second geography edit (private, caption-led)

`FLORIDA_GEOGRAPHY_FULL_STYLE_STUDY_1080x1920.mp4` is a separate, complete short film, **not** the mystery episode and not an extension of the six-second preview. The master is 1080×1920 H.264 at 30 fps, with 48 kHz stereo AAC; 1,080 frames / 36.00 seconds. It is a **caption-led** original explainer: no voice-over, no melody or composed score. The natural rain/wind bed is approximately −28.4 LUFS integrated, −15.0 dBFS true peak. It has not been published to YouTube.

Original spoken-style captions, drawn on screen as the full script:

> A coastline, seen from orbit. / Then a peninsula comes into view. / Florida points south between two waters. / The Gulf lies to the west. / The Atlantic opens to the east. / Beyond the tip: an island chain. / Follow the Keys toward Key West.

Shot plan: 0–5.4 s UV-projected Earth with independently drifting clouds and an orbital camera yaw; 4.9–9.5 s Earth-to-Florida optical dissolve and a slow map push; 9.5–14.5 s glowing Florida-region reveal; 14.5–23.5 s cyan route drawing across land and a Key West beacon; 23.5–30 s a separately illustrated closer Keys plate with its own route draw-on and gently tracking camera; 30–36 s pullback to Gulf/Atlantic context and title. Individual captions, vector layers, cloud overlay, match dissolves, endpoint effects and camera extents are authored in [`render_geography_full.py`](render_geography_full.py). The globe is a **software-rendered spherical projection with normals and NASA UV textures**, not an imported Blender mesh or a flat disk and not a realtime Earth observation. The map-scale cloud layer drifts slightly and is for visual atmosphere only.

### Source assets and rights context

- NASA day/night/cloud textures were fetched from the GitHub repository [`Depal-Jakub/orbital-bloom`](https://github.com/Depal-Jakub/orbital-bloom), whose [asset inventory](https://github.com/Depal-Jakub/orbital-bloom/blob/main/ASSET_INVENTORY.md) records exact upstream NASA sources, treatments and checksums. Local files are `assets/globe_nasa/earth-{day,night,clouds}-2048.jpg`, all 2048×1024. Day: NASA Blue Marble by Reto Stöckli with enhancements by Robert Simmon; source `https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/land_ocean_ice_2048.jpg`, SHA-256 `d4dc80a6ef571939d0abe04a9bed3d3d1e6cd63e59514be1c5e43a6b069e6f1e`. Night: NASA Earth Observatory Black Marble 2016 / Joshua Stevens, Suomi NPP VIIRS data from Miguel Román, NASA GSFC; mirrored grayscale/downsampled derivative, SHA-256 `62d3c882d9f0acce57322b0b27d0a8f97329b9b23e0a04537f703cb1f761665f`. Clouds: NASA Blue Marble / Stöckli and Simmon; source `https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57747/cloud_combined_2048.jpg`, SHA-256 `daddaad84d7a33bbbc86cdda3f591099f57cee8607b7bcf3b67eb7e4f7a1c793`. The images are used as texture data with acknowledgement, not as a NASA-produced or endorsed video; follow [NASA media guidelines](https://www.nasa.gov/nasa-brand-center/images-and-media/) before republishing.
- Wide Gulf/Florida relief and new `assets/florida_keys_macro_relief.png` are **new AI-illustrated** atlas plates; text, route, labels, stars, color effects, camera choreography, edits and compositing are authored locally. Neither illustrated plate is a georeferenced GIS dataset. The 9 user-supplied Train 2 clips are used **only as visual reference**, not copied into the final video.
- Recorded ambient source: `rain-light.ogg` by rubberduck, “40 CC0 water / splash / slime SFX”; `wind.ogg` by SketchMan3, “Wind whoosh loop”. Both are credited as CC0 in the [source repository's credits](https://github.com/nahuelcio/ymmo/blob/main/client/public/audio/CREDITS.txt), and local copies were carried over from the prior private review's `v18_cc0_weather` directory. No mystery-episode score is reused.

**Accuracy caveat:** Textured continental shapes, coastlines and latitude cues on the NASA globe are illustrative global imagery; both local relief plates, the traced route, Key West marker, cloud timing and close-up island geometry are *graphic treatments*, **not survey-accurate map claims, current weather, a factual itinerary, real hotel coordinates or evidence of an event**. Verify names, bounds and route positions against a licensed/georeferenced GIS source before publishing an educational geography claim. This is an independently edited stylistic study, not a pixel-perfect replica of the reference shorts.

Rebuild in this folder using an environment with Pillow, NumPy, OpenCV and imageio-ffmpeg installed: `python render_geography_full.py`. The source expects the preceding study assets, the three checked-in globe textures, the separate Keys plate and the two local CC0 recorded effects under the prior episode's `assets/v18_cc0_weather/`. Intermediate uncompressed ambience is stored in ignored `render_cache/`; the MP4 is ignored by Git and delivered separately for private review.

# Train 2 reference forensic pass — every decoded frame, 9 supplied videos

**Method:** `analyze_refs.py` decoded *every* available frame of all nine user-supplied MP4s (12,571 total). For each frame it wrote the timestamp, mean RGB change from the previous frame, blue/green histogram correlation, edge churn, an optical-flow/RANSAC partial-affine estimate of camera drift/scale sampled every third frame, median saturation, and a white-subtitle-region fraction. Original reference pixels are only in private ignored `google_drive/` and `work/train2_study/reference_forensics/`, never in the new artwork or Git. `summary.json` and full per-frame CSVs, plus 2-second sampling sheets, are in that ignored work directory. Optical flow cannot separate map camera motion from independently moving overlays; estimated values are *diagnostics*, not source keyframes or recovered proprietary project files. Cuts hidden inside scale wipes/dissolves are undercounted by conservative hard-cut detection.

## Readout

| Clip | Frames / rate | Strong frame-to-frame visual resets | Flow interpretation |
| --- | --- | --- | --- |
| The Darien Gap | 1,806 / 30 fps | 5 very strong candidates, many more scale wipes | Repeated coastline-following push/pull, continuous map drifts, route and region as separate layers. |
| Diomede Islands | 1,831 / 30 fps | 2 strong, many animated scale changes | Globe-free flat relief atlas to tiny islands to photo-like aerial and back to map. |
| New Year First | 1,810 / 30 fps | 0 conservative hard cuts, but numerous map/graphic scene transitions | World flat atlas, International Date Line geometry, glowing islands, fireworks, coastal jump-ins. Continuous interpolation hides many edits. |
| Wallace Line | 1,814 / 30 fps | 4 strong | Reframing southeast Asia, animated pink dashed trace, independent animal cutouts, simple geological diagram, map return. |
| Time Zones | 1,817 / 30 fps | 5 strong | Flat world atlas, grids/vertical line overlays, local California inset, then different country close-ups. |
| Thai Ghosts, Midnight Monster, Tuk-Tuk, Would you buy it | 874/375/1245/999 frames (25 or 30 fps) | Recorded screen/timeline framing confounds cut estimation | These are primarily different collage/editing UI styles, not instructions to add a 3D globe to the geography edit. |

## Editorial grammar observed at 2-second and full-resolution spot checks

- **There is no 3D globe in the five geography clips**. They use an equirectangular-style, detailed, top-down relief/bathymetry world map, often cropped tight. Removing our globe is therefore required, not optional.
- Motion comes from coherent *map camera paths* (position, scale, occasional rotated lines/graphics), not a stack of disconnected Ken Burns crops. Map land, localized region and route may track together; clouds/fireworks/icons/labels move separately. The background must keep moving across text beats, with smooth easing in and out of focus rather than stopping at every caption.
- Average semantic change is about 2–4 seconds, but many are **overlay beats within one continuous camera move**, not a hard cut every 2 seconds. Small bottom subtitles update about once a spoken phrase. Large labels are sparse and geographically tethered; they are not giant generic titles on every shot.
- Distinct palettes have semantic jobs: yellow roads, cyan borders or travel, green selected land, magenta segmented boundaries, white measurements and red negative markers. They are precise and local, not blanket neon tint. Bloom has a bright narrow center and a dimmer feathered halo.
- Examples: `Darien` 0–6 s world-to-route overview; 6–11 region select and risk icon; 12–21 continuous yellow Pan-American highway path and return to gap; 22–38 alternate real terrain insert and graphic overlay; 40–60 road/context and denser cutout evidence. `New Year` 0–6 world/firework hook; 6–14 full map plus bright date line; 16–31 island push and explanation; 33–42 US context; 44–60 small-island comparison. `Wallace` 0–8 southeast Asia and red boundary; 10–22 line and animal layers; 24–35 local line plus measurement; 37–51 simplified diagram; 52–60 map return. The variations are content-dependent, not an exact shot order to copy.

## Rebuild contract

The replacement film should be an original **flat-relief geography film**, no sphere/globe. Keep the camera visibly moving while the script advances: geographic world-scale reveal → regional map drift → coastline-following push → local island detail → diagrammatic geological explanation → tracked route/bridge → final pullback. Labels and animated glow should be pinned to map coordinates through the transform; ocean texture and clouds have their own subtle motion. Use the higher-quality Apache-2.0 Kokoro model obtained from npm shards instead of the previous Piper voice (the previous voice was explicitly rejected). Reference narration is not sampled, cloned or transcribed. Keep all private previews owner-only; the map plates are illustrative, not GIS survey imagery.

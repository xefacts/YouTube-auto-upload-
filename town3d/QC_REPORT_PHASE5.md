# Phase 6 — QC Report for the Phase 5 Cinematic Sample

Covers `town_render/phase5_cinematic.mp4` (301 frames, 540×960, 24fps,
~12.5s, 7 shots). Technical and artistic QC are reported **separately**, as
required — technical success is never used as evidence of artistic success.

## Technical QC (objective, pixel/container-level)

Method: `town3d/qc.py` (OpenCV-based, operates on real decoded frame arrays
— not on the renderer's own claim of success). Since this sandbox's OpenCV
build cannot decode mp4 via `cv2.VideoCapture` (no system libavcodec), the
actual encoded file was decoded back into raw frames using the same ffmpeg
binary already relied on for encoding (`imageio_ffmpeg`), a different and
working code path, so this genuinely re-reads the delivered file rather
than re-using in-memory frames from the render step.

| Check | Result |
|---|---|
| Frame count | **301 / 301** decoded, exact match to the renderer's own count, 0 remainder bytes (rules out truncation/corruption) |
| Resolution | 540×960, confirmed from decoded byte count |
| Frames too dark / too bright | 0 |
| Frames near-blank (degenerate contrast) | 0 |
| Frames degenerate (near-zero Laplacian sharpness) | 0 |
| Average brightness / contrast / sharpness | 129.8 / 47.2 / 208.4 (all within the pass thresholds in `qc.py`) |
| **Overall technical QC** | **PASS, 301/301, 0 flags** |

## Artistic QC (separate from the above; not inferred from brightness/sharpness)

### Semi-automated temporal checks (`town3d/qc_artistic.check_temporal`)

This measures something an eye actually cares about — sudden, unmotivated
jumps — not a brightness/sharpness score. It compares each frame's visual
change and camera-motion change against a local windowed expectation (not
one global average, which was tried first and produced false positives at
ordinary shot cuts — see commit history), explicitly excluding the 7
intentional hard cuts between shots.

**First rendering of the sample: FAILED this check**, for a real reason: it
flagged a flicker at frame 217 with no explanation from local camera
motion. Manually inspecting frames 216–222 (`/tmp/frame_21*.jpg` at the
time) showed the "environmental interaction" shot briefly framed nothing
but flat grass/sidewalk/road color bands — the camera had been pointed at a
streetlight anchor far from where the character actually ends up after the
walk shot, so the eye/target interpolation swept across a large empty gap.
Root-caused to `phase5_cinematic.py` picking `light_anchors[1]` (near the
start of the street) instead of the anchor nearest the character's actual
end position. Fixed by selecting the nearest anchor; re-rendered; re-ran
the check.

**Final rendering of the sample (the one delivered to Drive): PASS.**
`town_compare/phase5_temporal_qc.json`:
```
frames_checked: 301
shot_boundaries_excluded: [38, 81, 119, 162, 200, 248, 301]
flicker_events: []
discontinuity_events: []
pass: true
```

### Manual / visually-inspected checklist

Each item below was checked by actually opening the relevant frame(s), not
inferred:

| Criterion | Status | Evidence |
|---|---|---|
| Geometry defects | PASS | `phase5_shot1/3/5/7.jpg` show clean beveled boxes, no inverted normals or missing faces observed |
| Character deformation | PASS (with a caveat) | Walk-cycle limb bending (`character_test2_walk.jpg`) and the close-up (`phase5_shot5.jpg`, corrected version) look anatomically plausible; initial close-up framing was wrong (camera saw the back of the head due to a face-direction sign error) and was fixed before delivery — see `phase5_cinematic.py` comments |
| Camera clipping | PASS | Near-plane Sutherland–Hodgman clipping (`engine2._clip_near`) was added this session specifically to fix whole-face rejection; verified via `engine2_ground_fixed.jpg` and `city_test4_clipfix.jpg` |
| Shadow artifacts | PASS, with a known limitation | Blob shadows render consistently under the character across all shots; the limitation (fixed shape regardless of light direction, no object-to-object cast shadows) is a known approximation, not a bug, and is disclosed in `PHASE1_REFERENCE_COMPARISON.md` |
| Character consistency | PASS | Same `CharacterStyle` (ponytail, teal shirt, navy pants) used across all 7 shots in the one Python process, so colors/proportions cannot drift between shots |
| Visual composition | PASS, with one disclosed nitpick | All 7 shots keep a legible subject in frame after the frame-217 fix; the character stands on the road/lane-line rather than the sidewalk throughout (not re-blocked this round) |
| Narration relevance | N/A — not scored | This sample has no narration track (explicitly a silent visual proof-of-concept per "do not render a full video yet"); narration-sync QC will apply once a real script is attached to a scene spec |

### Artistic QC verdict

**Approved as a representative sample**, with the limitations above
explicitly disclosed rather than hidden. One genuine defect was found and
fixed during this QC pass (the frame-217 empty-gap shot); the fix is
committed and the delivered video reflects the corrected version.

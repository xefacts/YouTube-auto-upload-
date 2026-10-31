# Emu War — smoother voice-aligned final edit (v4)

**Final exports:** `Emu_War_Smooth_Final_v4_8K_Portrait.mp4` (4320 × 7680) and `Emu_War_Smooth_Final_v4_1080p_Preview.mp4` (1080 × 1920), both 48 seconds at **30 fps**. The 8K master is **upscaled** from predominantly 768 × 1376 AI-generated stills, *not* native 8K image detail. These MP4s are delivered separately on Drive; the repo contains source assets.

## What changed after v3 feedback

- Recut to **35 unique still-image shots, none reused**, around the actual spoken beats: comeback and withdrawal (0–7 s), damaged crops and farmer pressure (7–11 s), small team returning (11–14 s), Meredith's report (14–17 s), continuing migration (17–22 s), newsprint and farmers still needing help (22–26 s), skyward/downward setting transition to 1934 supplies (26–31 s), bounty claims (31–35 s), fencing (35–42 s), and an unresolved quiet ending (42–48 s). Five **new generated stills** in `images_new/` show migration scale, farmers reacting to the newspaper, supply handover, claims clerk and a long fence. These five images were created for the narrated beats, not as generic filler.
- Whole-image camera travel is eased and directional rather than frantic. The base editor renders at **30 fps**, then makes a 1080p preview and upscaled 8K master. Eight short **five-frame (~167 ms) image-to-image dissolves** bridge changes of place or topic; adjacent poses, ledger and fence actions remain cuts-on-action. Transition frames blend two moving image crops, without extending or shortening the **48-second** narration. Each scene source image occurs once.
- The warm/cool grade is consistent across shots. Editorial dates/figures are *baked onto selected stills before camera movement*, not independent timed captions. `text_baked_stills/` shows the finalized `NOVEMBER 1932` opening, illustrative `REPORTED 986` report, `EMU WAR` newsprint, `CLAIMS 57,000+` ledger and a graded supply still with in-image `YEAR 1934`. The opening/date is not repeated. No additional subtitle layer.
- **The same spoken English narration** and factual story remain. Sound design remains non-melodic: low original wind/paper/wire cues and four original **synthesized emu-inspired** vocal textures in the bird sections, mixed under the narrator. They are **not real wildlife field recordings**, songs, music or imported sound samples. This follows the requested halal-conscious preference; it is **not a religious certification or ruling**.

The illustrated documents are not authentic historical records. `57,000+` describes bounty **claims**, not a verified count of individual birds. Backgrounds, humans and emus are illustrative; no reference footage, narration, soundtrack, logos or watermarks are copied. There are no rigged or hand-drawn frame-by-frame character animations—apparent action comes from adjacent generated poses and whole-image motion.

## Re-render

The source ZIP preserves repository-relative paths and includes all 35 required scene PNGs, the original narration, the editor, font licensing, sound and visual examples. From repository root:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/final_image_edit_v4/render_smooth.py
```

The intermediate `staged/` JPEGs and the generated `natural_cues.wav` are reproducible. Historical notes are in `../phase2/README.md`, with supplied visual references audited in `../final_image_edit/REFERENCE_AUDIT.md`.

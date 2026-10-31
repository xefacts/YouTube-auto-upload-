# Past Detour: 1971 Gold Window — V4 source project

This is the source for a **previous Past Detour gold-window draft**, not a newly approved episode. The user has since asked for another historical video with recurring Rome characters and for frame-by-frame analysis of the Rome versions; its **topic and exact cast are not yet confirmed**. Do not treat this V4 draft as approval of that later request.

V4 was produced after reviewing the Rome Gunpowder V10 visual reference. It uses **new** period-appropriate cartoon characters, 10 original illustrated source frames, key-pose switches, a moving vault door, props, local limb deformation, the 1973 rates/map beat, and a closing balance. The actual Roman characters, footage, emblems, audio, and maps are not bundled or reused. The gold-window historical facts and sources are in `V4_ROME_CARTOON_MASTER_NOTES.txt`.

## Render

Python 3.11 and FFmpeg (provided by `imageio-ffmpeg`) are needed. Rendering dependencies are isolated so they don't alter the main YouTube upload pipeline:

```bash
python3 -m venv .venv
.venv/bin/pip install -r past_detour_gold_1971/requirements-render.txt
.venv/bin/python past_detour_gold_1971/render_v4_rome_cartoon.py --stills
.venv/bin/python past_detour_gold_1971/render_v4_rome_cartoon.py --render
```

`--stills` writes 27 review JPEGs into `v4_review/`. `--render` writes `Past_Detour_1971_Gold_Window_ROME_STYLE_V4.mp4` next to the script. Both are ignored by Git. The renderer reads `v4_assets/`, the six narration clips in `v3_audio/`, the licensed Cinzel font and `OFL.txt` in `v3_fonts/`, and the 51.41-second voice master/timing in `v3_master_audio.wav` and `v3_timeline.json`. These inputs are tracked so the project is reproducible. The output is **1080 × 1920, 60 fps**, not native 4K: illustrated sources were 768 × 1376.

The existing uploaded V4 master and an optional source archive are also available on [Google Drive](https://drive.google.com/drive/folders/1MkixttvDrtdmJ7ZI4XK7MQIACe5_OSZZ). Older versions in that folder are marked `OLD_...DO_NOT_UPLOAD`. Video output, archived ZIPs, and review frames are not committed to this repository.

## Scope and editorial cautions

- The gold exchange at $35/oz concerned foreign monetary authorities, not shoppers. August 15, 1971 suspended that exchange; major currencies floated by 1973.
- Illustrations are reconstructions, not archival recordings or photographs. Some decorative printed microtext in generated art is not an historical quote.
- Frame-by-frame character animation was **not** produced here: it is an illustrated key-pose/cutout animation edit. The later user request specifically calls for more faithful Rome-version character and motion analysis and is still pending.
- No views, retention, engagement, or RPM result is guaranteed.

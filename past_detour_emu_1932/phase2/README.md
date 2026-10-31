# The Emu War — Phase 2 Short: What Happened Next?

**Finished video:** `Emu_War_1932_Phase2_Short.mp4` — 48 seconds, 720 × 1280 portrait, 24 fps, H.264/AAC, English narration and original non-melodic effects. **No music.** This is a separate follow-up to the Phase 1 MP4, not a replacement or a set of still images.

The video is assembled from **ten new AI-generated scene stills** in `images/`, plus one previously generated Phase 1 emu-field still for a brief recap. Simplified 2D characters wear 1930s period clothes in realistic-looking Western Australian farm, office and fencing settings. Motion is limited to whole-image camera crops/zooms and hard cuts: no independently drawn, rigged or frame-by-frame character animation. The supplied Rome video/character sheet informed only the broad explainer-art language; none of its footage, people, dialogue or soundtrack appears here. The farmer and other portrayed figures are illustrative, not identified historical participants.

## English voiceover

> Remember the Emu War? The soldiers actually came back. After the first embarrassing withdrawal in November 1932, farmers insisted the crop damage was still serious. The small gun team returned. By December, Major Meredith reported nine hundred and eighty six emus killed. That was not zero, but it was nowhere near enough to stop the migration. Newspapers loved the story. The farmers still needed protection. In 1934, the government supplied ammunition and paid bounties for emu hunting. More than fifty seven thousand bounty claims were made in six months. But the lasting physical defence was not another machine gun. It was longer fencing across the farm country. The so-called war ended; the fight to protect crops did not.

`audio/narration.mp3` uses the previously selected historical-explainer English voice for continuity, not a clone of any reference video. `audio/original_foley.wav` is original programmatically synthesized wind, rustling paper and restrained fence/wood contact sounds. Neither music nor imported samples are used. On-screen editorial cards **summarize the narration**; they are not exact timed closed captions.

## Factual notes / visual disclosure

- Main source: [Encyclopaedia Britannica, “Emu War”](https://www.britannica.com/topic/Emu-War), consulted 31 October 2026. Meredith's detachment first withdrew on November 8, 1932, then returned after farmers complained. The final reported military tally was **986 emus killed** (not zero). The small campaign did not resolve the farmers' problem.
- Britannica reports that by **1934** the government supplied farmers with ammunition and established bounties; approximately **57,000 claims for dead emus were made in six months**. This film calls them bounty *claims*, not an independently verified species-wide count. Long-distance fencing is described by Britannica as the only permanent physical defence; the film does not imply it was all finished in 1934.
- Scenes, interior offices, ledgers, uniforms, figures, fences and emu placements are AI visual reconstructions, **not archival photos** or records of a particular meeting. The numerical overlays `986` and `57,000+` were typed by the editor using the source figures; no source document is reproduced. Hunting or harm is not depicted.

## Re-render

From the repository root, with the Phase 1 `images/02_migration.png` also present:

```bash
python -m venv .venv
.venv/bin/pip install pillow numpy imageio-ffmpeg
.venv/bin/python past_detour_emu_1932/phase2/render_phase2.py
```

The script composes 12 image-edit beats from the generated stills, creates original effects, mixes the existing narrator MP3 and writes the finished MP4. The source stills, narration and Foley are stored alongside it in this Phase 2 directory. The source ZIP delivered separately also includes the reused Phase 1 image for self-contained rendering.

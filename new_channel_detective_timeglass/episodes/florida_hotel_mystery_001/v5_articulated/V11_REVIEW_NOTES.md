# Florida V11 — full voice matched private review

**Owner-only review:** https://drive.google.com/file/d/1Kc8eSqhkoAfR5IIP1cWpZ8vvR5IlH9O0/view?usp=drivesdk (36.50 s, 24 fps, 2160 × 3840 H.264 + stereo AAC, 74,955,876 bytes). This is an **upscale** from ~768 × 1376 painted/photographic plates; not native 4K detail and not frame-by-frame hand-drawn animation. The case and shooting scene are fictional; no named suspect is assigned guilt. **No YouTube publication or public sharing.** V9/V10 private reviews remain available for comparison.

## Final-cut pass

- **Selected voice untouched as source:** the existing `audio/voice_original_1934.mp3` and untrimmed processed `audio/voice_full_1934_edit.mp3` are unchanged. All **36.4955 s** of the processed narration, including its final spoken syllable, feed the 36.50 s edit (876 frames). The earlier 41 s export's ~4.5 s post-narration tail is gone; no alternate narrator or truncated last line was substituted. The user's “last p” was not identified as a separable non-speech artifact in the supplied track, so no actual spoken phoneme was cut. This avoids an irreversible VO change. Music/effects are mixed separately.
- **Gunshot and aftermath:** original suite-matched threat, falling and collapsed keyframes show the same businessman in a brown-charcoal suit/teal tie, the same desk/brass lamp/rainy balcony doors, and an anonymous dark shooter silhouette. A small source-anchored illustrated handgun and **one** flash occur at 3.34 s with a synchronized procedural gunshot. Two generated character performances from V10, chair/cloth foley and the final slumped pose make the non-graphic death clear. No visible wound, blood or graphic impact. The rest of the episode keeps the selected PRISM detective in his slate-blue coat, present from the first balcony frame at 12.65 s.
- **Visual finish:** the suite and detective plates share a restrained lifted-shadow teal/amber grade; the three new keyframes form a consistent pose progression, with bounded camera movement. 31.55–34.10 s is a new *original* moving dossier of balcony/thread and coat-fiber clues, followed by a 34.10–36.50 s hotel pullback on the final narration. The Train 2 Tuk-Tuk and Thai Ghosts clips were examined for the **idea** of staggered collage entry/annotation; none of their footage, logos, graphics, sound, people or text appears. There is no lower-frame text and no claim of word-synced captions. The watch is not repeated in the ending.
- **Original sound:** unchanged centered narration over quiet procedural dark drone/two-tone motifs, rain/air, shot, hinge/door, chair/cloth, balcony latch and sparse clue-change accents. No copyrighted reference soundtrack/SFX were reused. Final export is approximately −18.3 LUFS integrated and −1.6 dBFS true peak.

## QA and rebuild

`ffprobe` reports 36.500000 s, 876 H.264 frames at 2160 × 3840/24 fps and stereo AAC. All **876 exported video frames decoded** without errors; no all-black segments were found. Actual-export contacts from threat, muzzle flash, falling/collapsed poses, PRISM's first balcony frame, thread and final clue-board/hotel shots were inspected. The original processed voice correlates with the final mix in early, middle, and late portions (0.85–0.92, despite added original music/FX), including 34–36.25 s. SHA-256 of the review MP4: `edd5c49fa248e81d990c544a92dfc6866bafcc0bfa01f0b7cd4fe31f122de8ba`. Both the Drive folder and this file have owner-only permissions, verified after upload.

```sh
python3 -m venv .venv-video
.venv-video/bin/pip install -r tooling/creative/video-requirements.txt
.venv-video/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v11.py
```

A fresh rebuild will generate new procedural noise textures deterministically (seeded RNG) but exact x264/AAC bitstreams may depend on FFmpeg version. The production MP4 and inspected QA contacts stay ignored as build outputs; source art, code, and character audio remain tracked.

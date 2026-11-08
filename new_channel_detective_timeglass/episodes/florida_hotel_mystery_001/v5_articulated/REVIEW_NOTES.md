# Florida locked suite — V9 PRISM full-voice 4K-size private review

**Current private review:** [FLORIDA_V9_PRISM_FULL_VOICE_4K_UPSCALED_PRIVATE_REVIEW.mp4](https://drive.google.com/file/d/1yZxC2zq6tkuUWoopIiQLJ7jQbifyk5oq/view?usp=drivesdk). 41.0 s, 24 fps, 2160 × 3840 H.264/AAC stereo, owner-only access. **This is an upscaled 4K-size output, not native 4K source detail:** most hotel source plates are ~768 × 1376 and the selected-character poses are 848/1024 px wide. This remains a **fictional dramatization/private review**, not a verified real case or a YouTube upload.

## Changes requested after V8

- **The user's actual selected detective is PRISM, option 02**, confirmed in this session. Three new matching poses (`assets/prism_corridor_stand.png`, `prism_suite_look.png`, `prism_balcony_stand.png`) were built from `new_channel_detective_timeglass/prism_selected/art/front.png`. The identical slate-blue high-collar coat, silver clasp, black cropped hair, case file and prism magnifier identify him throughout. The earlier tan-coat investigator is absent from the new edit, including the suite shot (which no longer uses its baked-in tan-coat image). White-background holes and studio cast shadows were removed from the new key art before compositing. The actor is already on the floor of the **first** balcony frame at 12.65 s, not added halfway through the balcony shot.
- **The full chosen voice is present.** `audio/voice_original_1934.mp3` is an unchanged copy of the user's selected earlier 19:34 Adam recording (~39.23 s, SHA-256 `743dadbea357ba10d281ca66b8a3f8a3c68a414d7d0a3ec3ad018a108c804061`). `audio/build_full_voice.py` applies the established 1.075× pace and gentle EQ/compression **without trimming**, making `audio/voice_full_1934_edit.mp3` (~36.50 s). The last spoken phrase is retained, followed by ~4.5 s of visual-only ending. The newer 19:45 alternate was not substituted.
- **Picture:** consistent filmic teal shadow/warm lamp grade is applied once to original plates *and* character art, with gentle contrast/saturation. Camera movement is motivated and less frantic through the characters; the 5.2–9.55 s locked-room door progression and 24.3–29.1 s thread study get longer holds, with a strong 36.6–41 s camera retreat on the same photographed hotel. The clock/watch gets **one continuous appearance** around 9.55–12.65 s and is never repeated in the ending. The selected Train 2 folder's sample videos were inspected for editorial pacing and compositional ideas; none of their footage, logos, people, audio or exact motion was copied.
- **Text:** only four original styled editorial *story-cue* cards, all high in the frame; **nothing is placed as a lower-third/bottom caption**. The small opening fiction notice is also at the top. Captions are deliberately sparse because no independently approved word-by-word VO transcript exists; do **not** call them exact subtitles. Their cue times are based on earlier rough scene-beat notes. No exact year, watch time or suspect guilt is typeset.
- **Sound:** fresh original stereo dark noise/air/rain/percussion sound design with a heavy hinge creak into a wood door slam exactly on the **6.80 s** closed-door cut, metal latch at **15.96 s**, subtle lens focus at **24.68 s**, sparse scene accents and a longer visual-ending rise. Voice stays centered and full-length; final audio measured about **−18.4 LUFS integrated, −2.8 dBTP**, and the AAC stream decoded without errors. All effects are procedural and non-melodic; no reference-video audio or purported real-incident recording is used.

**QA:** 984 frames fully decoded at 2160 × 3840 with stereo AAC, 41.0 s; extracted 21-frame contact and full-size PRISM feet/door/balcony compositions inspected. The first unbounded 4K encoding attempt was killed by memory pressure; the reproducible renderer now limits FFmpeg decoding/filter/encoding threads and the second encode completed successfully. Higher-resolution *new source art* and a human VO transcript/listening pass would still be needed for native-detail 4K and verified word-synced captions.

V8's generated Drive video was moved to **recoverable Trash only after V9 uploaded and owner-only permissions were verified**. The user's voice source and Train 2 reference files remain preserved. Old review source scripts and generated poses are retained for reproducibility; old local V8 MP4 may be removed because the replaced video is safely in Drive Trash. MP4s and `render_cache/` are ignored build outputs.

Rebuild from the repository root:

```sh
python -m venv .venv
.venv/bin/pip install numpy pillow scipy opencv-python-headless imageio-ffmpeg
.venv/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/audio/build_full_voice.py
.venv/bin/python new_channel_detective_timeglass/episodes/florida_hotel_mystery_001/v5_articulated/render_v9.py
```

Output: `v5_articulated/FLORIDA_V9_PRISM_FULL_VOICE_4K_UPSCALED_PRIVATE_REVIEW.mp4`.

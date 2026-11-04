# UNCASE creator skills & toolchain

Reusable, review-gated skills for evidence-led true-crime Shorts and long-form documentaries. Includes topic selection, source tracking, factual script-writing, attention design, narration, edit/camera transitions, animation, audience care and technical QA.

## Installed and checked in this workspace

- **MoviePy 2.1.2 / FFmpeg** — cut, composite, audio mix, encode. Tested render path.
- **OpenCV 5.0.0 / Pillow / NumPy / SciPy** — tracking, masks, image plates, procedural animation/audio. Installed.
- **Kokoro ONNX 0.6.1 + Apache-2.0 q8 model/voice** — local free offline original narration; checksum verified. Emotion direction comes from sentence design, punctuation, tempo and take-level editing; not a voice clone or ElevenLabs.
- **yt-dlp 2026.10.26** — metadata for authorized/public pages only. Not a license to download or reuse competitor footage/audio.
- **Trafilatura 2.3.1** — extract permitted text for research; retain source URLs and confirm against primary sources.
- **CrewAI 1.15.34** — optional writer/research/reviewer orchestration; installed, but requires an explicitly configured LLM provider and credentials. No model API key is supplied or stored. Never let an agent invent citations or make final guilt assertions.
- **Remotion 4.0.540 and OpenFilm 0.2.7** — npm packages installed. Remotion's commercial license eligibility depends on business size; check upstream terms before use. OpenFilm CLI works, but its browser renderer is not installed in this sandbox. Neither was used to render the delivered film.
- **ffprobe npm binary** — installed, permission-fixed in ignored workspace tool path.

No ElevenLabs account, API key, quota, or subscription is available in this workspace. We did not claim or use ElevenLabs. For zero-cost offline VO, this project uses Kokoro. ElevenLabs is an optional paid/account-gated alternate; obtain an account, confirm current terms/pricing, and choose a licensed synthetic voice before use. Never clone a real victim, suspect, investigator, creator, or reference narrator.

## Skill playbooks

- [`skills/01_topic_finder.md`](skills/01_topic_finder.md)
- [`skills/02_fact_research_and_source_control.md`](skills/02_fact_research_and_source_control.md)
- [`skills/03_short_script_retention.md`](skills/03_short_script_retention.md)
- [`skills/04_longform_documentary_script.md`](skills/04_longform_documentary_script.md)
- [`skills/05_voice_performance.md`](skills/05_voice_performance.md)
- [`skills/06_camera_animation_editing.md`](skills/06_camera_animation_editing.md)
- [`skills/07_responsible_crime_storytelling.md`](skills/07_responsible_crime_storytelling.md)
- [`skills/08_preflight_quality_control.md`](skills/08_preflight_quality_control.md)

## Setup

```bash
python3 -m venv .venv-video
.venv-video/bin/pip install -r tooling/creative/video-requirements.txt
.venv-video/bin/pip install kokoro-onnx==0.6.1
npm ci --prefix tooling/creative --ignore-scripts
```

CrewAI stays isolated:

```bash
python3 -m venv .venv
.venv/bin/pip install -r tooling/creative/agent-requirements.txt
```

No source is automatically scraped. Respect rate limits, site terms, privacy and copyright. This is a research/production helper, not investigative authority, legal counsel, police database access, or a promise to solve open cases.

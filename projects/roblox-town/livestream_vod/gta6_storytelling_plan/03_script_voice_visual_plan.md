# 03 — Script Structure, Voice, Visuals and Thumbnail (Sections C, D, E, H, J)

## C. Script — structure only (script text BLOCKED until footage review)

Target: ~28 min. Bands from the brief. Each band lists its purpose and the story question it answers. No script text is
written here, because the content depends on verified footage and mission names.

| Band | Time | Purpose | Story question it must answer | Content source |
|---|---|---|---|---|
| Hook | 00:00–00:40 | Strong moment from authorized footage, one curiosity question. No long greeting. | What is at stake right now? | One verified clip |
| Story intro | 00:40–02:00 | Introduce Jason and Lucia and the Leonida setting | Who are they, and what is their situation? | Verified profiles and on-screen footage |
| Opening story | 02:00–06:00 | Opening events in chronological order | What happened first? | Footage, verified mission titles |
| Main progression | 06:00–12:00 | First important missions and transitions | How does the job start and go wrong? | Footage |
| Character development | 12:00–17:00 | Jason, Lucia and their interactions | How does their relationship change? | Original dialogue |
| Important events | 17:00–22:00 | Main developments and consequences | What changes for the story? | Footage |
| Exploration | 22:00–26:00 | Meaningful locations and details | Why is this place important? | Footage |
| Conclusion | 26:00–28:00 | What the viewer experienced; the next question | What is still unanswered? | Verified facts only |

Rules: do not add missions, dialogue, or outcomes. Do not cut events in a way that changes their meaning. Keep driving only
when it carries conversation, a new place, or a story event.

## D. ElevenLabs V4 voiceover — BLOCKED

- Blocked by: script (C), and the budget conflict (README decision 4). ElevenLabs is paid; the budget is $0.00.
- The plan uses Arena voices (`add_voice` audition, then `generate_speech`). Arena's voice tool does not take ElevenLabs
  tags. Emotion will come from the wording and punctuation. This is a deliberate change from the brief.
- Any invented line must be labeled as illustrative, never shown as game dialogue (brief Part 9).

## E. Character voice bible (draft)

| Voice | Role | Gender | Delivery | Used for |
|---|---|---|---|---|
| NARRATOR | Main storyteller | Masculine or neutral, to be auditioned | Natural Hinglish, energetic in hook and reveals, calm in explanation. Three styles: energetic gamer, natural storyteller, viewer engagement. | Narration (70% third person, 20% first, 10% second) |
| JASON | Playable protagonist | Masculine, separate from NARRATOR | Grounded, calm, serious at key moments | Only for original dialogue, if permitted |
| LUCIA | Playable protagonist | Feminine | Confident, expressive, emotionally direct | Only for original dialogue, if permitted |
| SUPPORTING | Cal, Brian, Boobie Ike, others | Assigned per scene | Each distinct, no copying of real actors or streamers | Only if dialogue is original and permitted |

Voice identities are chosen by audition once approved. Keep the same voice for the same character across the series.

## F. Clip selection

See `F_clip_selection_log.csv`. Columns follow the brief (source file, timestamp, start, end, mission, character, scene,
story importance, commentary, audio quality, rights status, decision). All content columns are `NOT REVIEWED`.
Priority order for picking clips (brief Part 4): opening cinematics, character introductions, main conversations,
mission beginnings, important progression, reactions, meaningful driving, location reveals, funny or unexpected moments,
emotional scenes, mission endings, environmental details.

## G. Timeline — BLOCKED (depends on F)

## H. Visual and sound design

**Visual mix (brief Part 10):** 70–85% authorized gameplay. The rest: story cards, original character cards, location
illustrations, mission timeline graphics, short transitions. Original graphics only.

**Screen rules:**
- Keep the HUD, mission objectives, character names, subtitles, notifications, and minimap clear of labels.
- No unnecessary zooms or artificial camera moves.
- Font: one consistent Latin font (NotoSans Bold is already in `work/fonts/`). No Devanagari.

**Caption rule (brief Part 11):** preserve original game subtitles. No permanent extra captions. Occasional one-word labels
("WAIT", "IMPORTANT", "NEW MISSION", "STORY DETAIL"), away from HUD and subtitles, on screen only when needed.
Note: this differs from the earlier v2/v3 videos (one English word on every line). See README decision 5.

**Sound (brief Part 12):**
- No background music, no soundtrack, no licensed audio. Earlier builds used no music, which matches the brief.
- Narration clearly audible. Lower the game audio under narration.
- Use only appropriate, non-musical sound effects and quiet ambience where permitted.
- Mute profanity and any explicit dialogue. Cut or obscure sexual or graphic content.

**Content restrictions (brief Part 12):** no gambling promotion, no glorification of crime, no graphic violence, no
misleading thumbnails. Use conservative clean editing per the creator's stated preferences. This plan does not issue any
religious ruling.

## J. Thumbnail concept (draft)

- Original art only: a split frame with two stylized figures (Jason and Lucia, drawn, not a game screenshot) against a
  Leonida skyline silhouette. Text: 2–4 words of the actual story question, Latin script.
- No game logo unless licensed. No fake "leak" or "early access" claims unless verified. No shocked faces of real people.
- Hold until the script (C) confirms the hook.

## Remotion and skills references (brief Part 15)

Remotion is an option for titles, timelines, and diagrams. Check its license and dependencies before adding it. Not
installed; no change in this turn. Video-Editing-Automation is GPL-3.0; read its license before reusing any code.

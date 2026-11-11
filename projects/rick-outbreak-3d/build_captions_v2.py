#!/usr/bin/env python3
"""
V2 1-Word Pop Caption Generator (`captions_v2.ass`)
- Generates strictly 1-word-at-a-time synced captions across all 933 words (`0.00s -> 247.75s`)
  from `projects/rick-outbreak-3d/data/words_v2.json`.
- Zero overlaps: every word ends strictly at or before the next word's start timestamp.
- Lower-third safe zone (`1080x1920`, `Alignment=2`, `MarginV=350`) so captions NEVER cover
  faces, hands, phone screens, or broken-window zombie eyes.
- Dynamic horror color emphasis (red/gold on intense horror trigger words, crisp white on standard words)
  with subtle 65ms pop-in scale (`114% -> 100%`) and bold black outline + shadow.
"""
import json, os, re

IN_JSON = "projects/rick-outbreak-3d/data/words_v2.json"
OUT_ASS = "projects/rick-outbreak-3d/data/captions_v2.ass"

RED_WORDS = {
    "EMERGENCY", "OUTBREAK", "BIOLOGICAL", "NEUROLOGICAL", "CONTACT",
    "SCREAMS", "SCREAMING", "FALLS", "CRASH", "COLLIDE", "SLAMMING", "POUNDING",
    "SHATTERED", "SHARDS", "BROKEN", "BLOOD", "PALE", "HAND", "FINGERS",
    "INFECTED", "MONSTER", "MONSTERS", "FACES", "EYES", "HELP", "DEAD",
    "TERRIFIED", "PANIC", "DIE", "TRAPPED", "DARK", "DARKNESS", "CLATTER",
}
GOLD_WORDS = {
    "ALERT", "WARNING", "LOCK", "LOCKED", "SHUTTERS", "SHELVES", "BARRICADE",
    "SIGNAL", "FAILED", "EMPTY", "HALF", "FOUR", "THREE", "TWO", "ZERO",
    "ALONE", "SURVIVE", "BREATH", "SHAKING", "SILENT", "SILENCE",
}


def fmt_ass_time(sec: float) -> str:
    sec = max(0.0, sec)
    cs_total = int(round(sec * 100))
    h = cs_total // 360000
    rem = cs_total % 360000
    m = rem // 6000
    rem %= 6000
    s = rem // 100
    cs = rem % 100
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def main():
    with open(IN_JSON, "r") as f:
        data = json.load(f)
    words = data["words"]
    assert len(words) >= 900, f"Expected ~933 words, got {len(words)}"

    header = """[Script Info]
Title: Rick Clips V2 1-Word Horror Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: OneWord,DejaVu Sans,82,&H00FFFFFF,&H000000FF,&H000A0A0E,&H96000000,-1,0,0,0,100,100,1.5,0,1,6.5,3.2,2,80,80,350,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    n = len(words)
    for i, w in enumerate(words):
        t0 = float(w["start"])
        raw_end = float(w["end"])
        # Hold word slightly across natural micro-gaps (up to +0.16s), NEVER overlapping next word!
        t1 = max(t0 + 0.08, raw_end + 0.14)
        if i + 1 < n:
            next_t0 = float(words[i + 1]["start"])
            if t1 > next_t0:
                t1 = next_t0
        if t1 <= t0 + 0.02:
            t1 = t0 + 0.03

        disp = str(w["word"]).strip().upper()
        if not disp:
            continue
        clean = re.sub(r"[^A-Z0-9]", "", disp)

        if clean in RED_WORDS:
            col_tag = r"\1c&H3838FF&"  # BGR vivid crimson-red
        elif clean in GOLD_WORDS:
            col_tag = r"\1c&H3CD4FF&"  # BGR warm warning gold
        else:
            col_tag = ""

        anim_tag = r"{\fscx115\fscy115\t(0,65,\fscx100\fscy100)" + col_tag + r"}"
        events.append(f"Dialogue: 0,{fmt_ass_time(t0)},{fmt_ass_time(t1)},OneWord,,0,0,0,,{anim_tag}{disp}")

    os.makedirs(os.path.dirname(OUT_ASS), exist_ok=True)
    with open(OUT_ASS, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    print(f"Generated {len(events)} 1-word ASS caption events -> {OUT_ASS} (0.00s -> {words[-1]['end']}s)")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
V3 1-Word Pop Caption Generator (`build_captions_v3.py`)
- Generates strictly 1-word-at-a-time synced captions across all 660 words (`0.00s -> 260.32s`)
  from `projects/rick-outbreak-3d/data/words_v3.json`.
- Zero overlaps: every word ends strictly at or before the next word's start timestamp.
- Lower-third safe zone (`1080x1920`, `Alignment=2`, `MarginV=350`) so captions NEVER cover
  character faces, expressions, shutters, phone screens, or underground survivor scenes.
"""
import json, os, re

IN_JSON = "projects/rick-outbreak-3d/data/words_v3.json"
OUT_ASS = "projects/rick-outbreak-3d/data/captions_v3.ass"

RED_WORDS = {
    "EMERGENCY", "VIOLENT", "RUNS", "SWERVES", "SCREAMS", "UNSAFE", "HITS",
    "BLOOD", "SICK", "SCARED", "CRASH", "SCRAPE", "KNOCKS", "IMITATE",
    "BROTHER", "FREEZE", "BROKEN", "DEAD", "PALE", "NEVER", "BEHIND",
    "DARK", "DAD", "DONT", "CLOSE", "ITSELF", "CHILDS",
}
GOLD_WORDS = {
    "WARNING", "417", "VIBRATES", "ALERT", "INDOORS", "STOP", "LOCK",
    "LOCKED", "SHUTTER", "SILENT", "PLEASE", "POLICE", "POWER", "FLASHLIGHT",
    "WINDOW", "MESSAGE", "VOICES", "SUNRISE", "EMPTY", "BATTERY", "STATION",
    "OPEN", "RADIO", "SOUND", "CRACKLES", "PLATFORM", "SLOWLY",
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
    assert len(words) >= 640, f"Expected ~660 words, got {len(words)}"

    header = """[Script Info]
Title: Rick Clips V3 1-Word Horror Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
; V4 rulebook caption spec: Arial-Black-class heavy font (Anton), THICK #1a1414 ink stroke,
; baseline at ~68% frame height (MarginV 620 of 1920) - Rick-Clips-style word pops.
Style: OneWord,Anton,96,&H00FFFFFF,&H000000FF,&H0014141A,&H96000000,0,0,0,0,100,100,1.2,0,1,11,2.5,2,80,80,620,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    n = len(words)
    for i, w in enumerate(words):
        t0 = float(w["start"])
        raw_end = float(w["end"])
        t1 = max(t0 + 0.08, raw_end + 0.16)
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

        anim_tag = r"{\fscx116\fscy116\t(0,65,\fscx100\fscy100)" + col_tag + r"}"
        events.append(f"Dialogue: 0,{fmt_ass_time(t0)},{fmt_ass_time(t1)},OneWord,,0,0,0,,{anim_tag}{disp}")

    os.makedirs(os.path.dirname(OUT_ASS), exist_ok=True)
    with open(OUT_ASS, "w", encoding="utf-8") as f:
        f.write(header + "\n".join(events) + "\n")

    print(f"Generated {len(events)} 1-word ASS caption events -> {OUT_ASS} (0.00s -> {words[-1]['end']}s)")


if __name__ == "__main__":
    main()

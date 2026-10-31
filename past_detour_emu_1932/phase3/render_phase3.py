#!/usr/bin/env python3
"""Final-pass caption edit on the existing Phase 2 film.

No new story, pictures, speech, music or sound. The original video is retained;
only its pixels are re-encoded to burn in verbatim timed captions with small
hand-authored type animations. The audio stream is copied byte-for-byte.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "phase2" / "Emu_War_1932_Phase2_Short.mp4"
OUTPUT = ROOT / "Emu_War_1932_Final_Phase3_Short.mp4"
ASS = ROOT / "captions_final.ass"
SRT = ROOT / "captions_final.srt"
FF = imageio_ffmpeg.get_ffmpeg_exe()

# Onsets and final voiced syllables measured from isolated narration.mp3's
# 10 ms RMS envelope (pause threshold 0.005). Each line is copied VERBATIM
# from the Phase 2 voiceover; on-screen editorial headings remain untouched.
# Whitespace and \N here only split display lines, never change spoken words.
CUES = [
    (0.17, 1.30, "Remember the Emu War?", "War?"),
    (1.62, 3.44, "The soldiers actually came back.", "back."),
    (3.84, 7.25, "After the first embarrassing withdrawal in November 1932,", "1932,"),
    (7.61, 10.29, "farmers insisted the crop damage was still serious.", "serious."),
    (10.76, 12.14, "The small gun team returned.", "returned."),
    (12.54, 13.35, "By December,", "December,"),
    (13.68, 17.08, "Major Meredith reported nine hundred and eighty six emus killed.", "six"),
    (17.56, 18.65, "That was not zero,", "zero,"),
    (18.98, 21.40, "but it was nowhere near enough to stop the migration.", "migration."),
    (21.87, 23.49, "Newspapers loved the story.", "story."),
    (23.93, 25.65, "The farmers still needed protection.", "protection."),
    (26.13, 27.20, "In 1934,", "1934,"),
    (27.51, 30.83, "the government supplied ammunition and paid bounties for emu hunting.", "bounties"),
    (31.30, 34.94, "More than fifty seven thousand bounty claims were made in six months.", "months."),
    (35.35, 38.84, "But the lasting physical defence was not another machine gun.", "gun."),
    (39.26, 41.84, "It was longer fencing across the farm country.", "fencing"),
    (42.26, 43.82, "The so-called war ended;", "ended;"),
    (43.82, 47.08, "the fight to protect crops did not.", "not."),
]

# Production lock: only the existing voiceover's transcript can appear in
# final captions. The check fails if a cue is added/reworded or a line omitted.
VOICEOVER = (
    "Remember the Emu War? The soldiers actually came back. After the first embarrassing withdrawal "
    "in November 1932, farmers insisted the crop damage was still serious. The small gun team returned. "
    "By December, Major Meredith reported nine hundred and eighty six emus killed. That was not zero, "
    "but it was nowhere near enough to stop the migration. Newspapers loved the story. The farmers still "
    "needed protection. In 1934, the government supplied ammunition and paid bounties for emu hunting. "
    "More than fifty seven thousand bounty claims were made in six months. But the lasting physical "
    "defence was not another machine gun. It was longer fencing across the farm country. The so-called war "
    "ended; the fight to protect crops did not."
)


def timecode(t, srt=False):
    total = round(t * (1000 if srt else 100))
    if srt:
        hours, rest = divmod(total, 3600000)
        minutes, rest = divmod(rest, 60000)
        seconds, milliseconds = divmod(rest, 1000)
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"
    hours, rest = divmod(total, 360000)
    minutes, rest = divmod(rest, 6000)
    seconds, centiseconds = divmod(rest, 100)
    return f"{hours}:{minutes:02}:{seconds:02}.{centiseconds:02}"


def validate():
    plain = " ".join(cue[2].replace("\\N", " ") for cue in CUES)
    assert re.sub(r"\s+", " ", plain).strip() == VOICEOVER
    assert all(0 <= a < b < 48 for a, b, _, _ in CUES)
    assert all(CUES[i][1] <= CUES[i+1][0] for i in range(len(CUES)-1))


def wrap_text(text, max_width=600):
    """Fit every caption inside the portrait's title-safe area (2–3 lines)."""
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 39)
    lines = []
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if line and font.getlength(candidate) > max_width:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    assert len(lines) <= 3, (text, lines)
    assert all(font.getlength(line) <= max_width for line in lines)
    return "\\N".join(lines)


def highlight(text, phrase):
    """Color one existing spoken word, never add or rewrite any words."""
    marker = "{\\c&H9EE8C9&}"
    reset = "{\\c&H00F7F8F7&}"
    # Color only when exact contiguous words occur on one displayed line.
    assert phrase in text, (phrase, text)
    return text.replace(phrase, marker + phrase + reset, 1)


def build_tracks():
    validate()
    srt_blocks = []
    for i, (a, b, text, _) in enumerate(CUES, 1):
        displayed = wrap_text(text).replace("\\N", "\n")
        srt_blocks.append(f"{i}\n{timecode(a, True)} --> {timecode(b, True)}\n{displayed}\n")
    SRT.write_text("\n".join(srt_blocks) + "\n", encoding="utf-8")
    header = """[Script Info]
Title: Emu War final phase — exact Phase 2 narration
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,DejaVu Sans,39,&H00F7F8F7,&H009EE8C9,&H0010191B,&H8C10191B,-1,0,0,0,100,100,0,0,3,10,0,2,30,30,0,1
Style: Accent,DejaVu Sans,20,&H009EE8C9,&H009EE8C9,&H0010191B,&H0010191B,-1,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for i, (start, voiced_end, text, key) in enumerate(CUES):
        # Keep captions over brief breath pauses, but anchor onset to voice.
        next_start = CUES[i+1][0] if i + 1 < len(CUES) else 47.12
        end = max(voiced_end, next_start - .06)
        animation = r"{\an2\pos(360,842)\fscx92\fscy92\t(0,160,\fscx100\fscy100)\fad(45,90)}"
        events.append("Dialogue: 0,{},{},Caption,,0,0,0,,{}{}".format(
            timecode(start), timecode(end), animation, highlight(wrap_text(text), key)))
        # The small mint underline draws itself in at each spoken cue. This and
        # the text pop are the only hand-authored motion; no scene is animated.
        sweep = (r"{\an5\pos(360,871)\p1\c&H9EE8C9&\fscx0"
                 r"\t(0,180,\fscx100)\fad(40,120)}"
                 r"m -54 0 l 54 0 l 54 4 l -54 4")
        events.append("Dialogue: 1,{},{},Accent,,0,0,0,,{}".format(
            timecode(start), timecode(end), sweep))
    ASS.write_text(header + "\n".join(events) + "\n", encoding="utf-8")
    print(f"Authored {len(CUES)} verbatim captions and {len(CUES)} tiny text underline animations")


def render():
    if not SOURCE.is_file():
        raise FileNotFoundError(f"Phase 2 input is missing: {SOURCE}")
    build_tracks()
    # Original audio: stream copy. Original scene order/content: unchanged.
    subprocess.run([
        FF, "-hide_banner", "-loglevel", "error", "-y", "-i", str(SOURCE),
        "-vf", f"ass={ASS}", "-map", "0:v:0", "-map", "0:a:0",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart",
        str(OUTPUT)
    ], check=True)
    print(f"Rendered {OUTPUT.name} ({OUTPUT.stat().st_size/1024/1024:.1f} MiB)")


if __name__ == "__main__":
    render()

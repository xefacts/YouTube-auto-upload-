#!/usr/bin/env python3
"""
Parses raw_tagged_script.txt into:
1. 6 episodic Shorts / Chapters (split at '---') with exact emotion + pause metadata
2. Packed <=1485-char TTS clips (8 narrator clips + 1 child clip = 9 clips total, fitting <=10/turn cap!)
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
raw = (ROOT / "raw_tagged_script.txt").read_text(encoding="utf-8")
raw_chapters = [c.strip() for c in raw.split("---") if c.strip()]

CHAPTER_TITLES = [
    "Part 1: Aisle Four — Biological Emergency",
    "Part 2: Half Stock — The Woman at the Glass",
    "Part 3: The Storage Room Window",
    "Part 4: Midnight Map — The Ringing Phone",
    "Part 5: Dead Street — Are You Alone?",
    "Part 6: Control Room — That's Not My Dad",
]

CHILD_LINES = {
    '"Please don\'t open the door."',
    '"Dad?"',
    '"That\'s not my dad."',
}

chapters_out = []
narrator_sentences = []
child_sentences = []

for ci, ch_text in enumerate(raw_chapters):
    lines = [ln.strip() for ln in ch_text.splitlines() if ln.strip()]
    cur_emotion = "calm"
    items = []
    for ln in lines:
        m_pause = re.fullmatch(r"\[pause(?:\s+([\d.]+)s)?\]", ln, flags=re.I)
        if m_pause:
            sec = float(m_pause.group(1)) if m_pause.group(1) else 0.85
            items.append({"type": "pause", "sec": sec, "emotion": cur_emotion})
            continue
        m_tag = re.match(r"^\[([^\]]+)\]\s*(.*)$", ln)
        if m_tag:
            cur_emotion = m_tag.group(1).strip().lower()
            rest = m_tag.group(2).strip()
            if not rest:
                continue
            ln = rest
        clean_ln = re.sub(r"\[[^\]]+\]", "", ln).strip()
        speaker = "child" if clean_ln in CHILD_LINES else "narrator"
        entry = {
            "type": "speech",
            "chapter": ci + 1,
            "speaker": speaker,
            "emotion": cur_emotion,
            "text": clean_ln,
            "spoken": clean_ln.replace('"', '')
        }
        items.append(entry)
        if speaker == "child":
            child_sentences.append(entry["spoken"])
        else:
            narrator_sentences.append((ci + 1, entry["spoken"]))
    chapters_out.append({
        "chapter": ci + 1,
        "title": CHAPTER_TITLES[ci],
        "items": items
    })

# Pack narrator sentences into <= 1485 char clips (never exceeding 1500 limit)
packed_clips = []
buf = []
buf_len = 0
clip_idx = 1
for ch_num, sent in narrator_sentences:
    add_len = len(sent) + (1 if buf else 0)
    if buf and (buf_len + add_len > 1485):
        packed_clips.append({
            "id": f"nar_{clip_idx:02d}",
            "speaker": "narrator",
            "chars": buf_len,
            "text": " ".join(buf)
        })
        clip_idx += 1
        buf = [sent]
        buf_len = len(sent)
    else:
        buf.append(sent)
        buf_len += add_len

if buf:
    packed_clips.append({
        "id": f"nar_{clip_idx:02d}",
        "speaker": "narrator",
        "chars": buf_len,
        "text": " ".join(buf)
    })

# 3 child lines in 3 crisp separate clips? Wait: 9 + 1 = 10 max! Let's check how many narrator clips we got!
if len(packed_clips) + len(child_sentences) <= 10:
    for j, cs in enumerate(child_sentences, 1):
        packed_clips.append({
            "id": f"child_{j:02d}",
            "speaker": "child",
            "chars": len(cs),
            "text": cs
        })
else:
    # Combine child lines with long ellipsis pauses so silencedetect splits them cleanly
    joined_child = "Please don't open the door... ... ... Dad?... ... ... That's not my dad."
    packed_clips.append({
        "id": "child_all",
        "speaker": "child",
        "chars": len(joined_child),
        "text": joined_child
    })

(ROOT / "parsed_chapters.json").write_text(json.dumps({
    "chapters": chapters_out,
    "packed_clips": packed_clips
}, indent=2), encoding="utf-8")

print(f"Chapters: {len(chapters_out)} | Total Packed TTS Clips: {len(packed_clips)} (limit = 10)")
for c in packed_clips:
    print(f"  {c['id']:12s} | spk={c['speaker']:8s} | chars={c['chars']:4d}")

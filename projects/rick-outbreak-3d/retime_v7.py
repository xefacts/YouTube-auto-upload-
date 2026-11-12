#!/usr/bin/env python3
"""
V7 INTRO RETIMER — global +9.04s dialogue shift.

The new 12.40s cinematic ORIGINS intro replaces the old 3.36s cold open, so the
render timeline is: [0, 12.40) intro, then story content shifted by exactly
12.40 - 3.36 = +9.04s. Every caption cue and word timing must move with it —
never hand-edit 660 cues.

Idempotence: this script is meant to run ONCE on the V6.5 data. Re-running
would shift again; guard below detects an already-shifted file.
"""
import json, re, sys

DELTA = 9.04
WORDS = "data/words_v3.json"
CAPS = "data/captions_v3.ass"

def ass_t(s):
    h, m, rest = s.split(":")
    sec = float(rest)
    return ((int(h) * 60 + int(m)) * 60) + sec

def to_ass_t(t):
    t = round(t, 2) + 1e-9
    cs = int(round(t * 100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, cs = divmod(rem, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

def main():
    # ---- words ----
    with open(WORDS) as f:
        data = json.load(f)
    first = data["words"][0]["start"]
    if first > 5.0:
        print(f"[skip] {WORDS} already retimed (first start {first})")
    else:
        for w in data["words"]:
            w["start"] = round(w["start"] + DELTA, 3)
            w["end"] = round(w["end"] + DELTA, 3)
        data["version"] = "v7_origins_intro_shift+9.04"
        data["duration"] = round(data["duration"] + DELTA, 2)
        data["total_frames"] = 8081
        with open(WORDS, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[ok] words shifted +{DELTA}: first cue now {data['words'][0]['start']}s")

    # ---- captions ----
    with open(CAPS) as f:
        lines = f.read().splitlines()
    out, shifted, seen = [], 0, 0
    dlg = re.compile(r"^(Dialogue:\s*0,)([\d:.]+),([\d:.]+)(,.*)$")
    for ln in lines:
        m = dlg.match(ln)
        if m:
            seen += 1
            t0, t1 = ass_t(m.group(2)), ass_t(m.group(3))
            if t0 > 5.0 and seen == 1:
                print(f"[skip] {CAPS} already retimed (first cue {m.group(2)})")
                out.append(ln)
                continue
            out.append(m.group(1) + to_ass_t(t0 + DELTA) + "," + to_ass_t(t1 + DELTA) + m.group(4))
            shifted += 1
        else:
            out.append(ln)
    with open(CAPS, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"[ok] captions shifted: {shifted} cues, first start now {out[[i for i, l in enumerate(out) if l.startswith('Dialogue')][0]].split(',')[1]}")
    print("DONE — V7 dialogue retime complete.")

if __name__ == "__main__":
    main()

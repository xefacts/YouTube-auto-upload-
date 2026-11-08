#!/usr/bin/env python3
"""Timeline source of truth: shot durations -> work/timeline.json + web/timeline.js"""
import json, os

FPS = 180
LEAD_S = 0.30
TAIL_S = 0.90
PAD_S = 0.72
MIN_S = 3.0

SHOTS = [   # id, light, loc, vo line
    ("s1",  "streetNight", "street", 1),
    ("s2",  "streetDoor",  "street", 2),
    ("s3",  "hallNight",   "hall",   3),
    ("s4",  "cellarDim",   "cellar", 4),
    ("s5",  "dutchNight",  "dutch",  5),
    ("s6",  "dutchNight",  "dutch",  6),
    ("s7",  "dutchNight",  "dutch",  7),
    ("s8",  "dutchNight",  "dutch",  8),
    ("s9",  "streetNight", "street", 9),
    ("s10", "dutchDawn",   "dutch",  10),
    ("s11", "dutchDay",    "dutch",  11),
    ("s12", "dutchDay",    "dutch",  12),
]

def main():
    durs = json.load(open("work/vo_durations.json"))
    a = round(LEAD_S * FPS)
    shots = []
    for sid, light, loc, vo in SHOTS:
        sec = max(MIN_S, durs[f"line{vo:02d}"] + PAD_S)
        n = round(sec * FPS)
        shots.append({"id": sid, "f0": a, "f1": a + n - 1, "len_f": n,
                      "light": light, "loc": loc, "vo": vo, "vo_at": round(0.42 * FPS)})
        a += n
    total = a + round(TAIL_S * FPS)
    tl = {"fps": FPS, "total": total, "lead": round(LEAD_S * FPS), "shots": shots}
    os.makedirs("work", exist_ok=True)
    json.dump(tl, open("work/timeline.json", "w"), indent=1)
    open("web/timeline.js", "w").write("export const TL = " + json.dumps(tl, separators=(",", ":")) + ";\n")
    print(f"FPS {FPS}  total {total} frames = {total/FPS:.2f}s  shots {len(shots)}")
    for s in shots:
        print(f"  {s['id']:>3} {s['f0']:5d}-{s['f1']:5d}  {s['len_f']/FPS:5.2f}s  {s['light']:<12} {s['loc']}")

if __name__ == "__main__":
    main()

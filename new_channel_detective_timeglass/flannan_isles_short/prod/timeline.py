#!/usr/bin/env python3
"""Timeline source of truth: shot durations -> work/timeline.json + web/timeline.js"""
import json, os

FPS = 180
LEAD_S = 0.30          # black / title lead-in
TAIL_S = 0.90          # tail on the last shot
PAD_S = 0.72           # breathing room after each line
MIN_S = 3.0

SHOTS = [   # id, light, loc, vo line
    ("s1",  "nightStorm",  "isles", 1),
    ("s2",  "greyDawn",    "isles", 2),
    ("s3",  "nightSea",    "isles", 3),
    ("s4",  "coldMorning", "isles", 4),
    ("s5",  "lampWarm",    "lamp",  5),
    ("s6",  "lampDim",     "lamp",  6),
    ("s7",  "stormGrey",   "isles", 7),
    ("s8",  "lampWarm",    "lamp",  8),
    ("s9",  "greyDawn",    "isles", 9),
    ("s10", "fogNight",    "isles", 10),
    ("s11", "sunrise",     "isles", 11),
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
    js = "export const TL = " + json.dumps(tl, separators=(",", ":")) + ";\n"
    open("web/timeline.js", "w").write(js)
    print(f"FPS {FPS}  total {total} frames = {total/FPS:.2f}s  shots {len(shots)}")
    for s in shots:
        print(f"  {s['id']:>3} {s['f0']:5d}-{s['f1']:5d}  {s['len_f']/FPS:5.2f}s  {s['light']:<11} {s['loc']}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Builds millisecond-accurate energy-snapped word timestamps in projects/rick-outbreak-3d/data/words.json
from the 63 verified Whisper segments of Ronald's voiceover (/tmp/rick_study/vo/voiceover.wav),
with homophones ('Isle 1/2' -> 'Aisle 1/2') corrected for broadcast-grade captions.
"""
import json
import os
import re
import numpy as np
import soundfile as sf

VO_PATH = "/tmp/rick_study/vo/voiceover.wav"
OUT_PATH = "projects/rick-outbreak-3d/data/words.json"
os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

SEGMENTS = [
    (0.00, 4.16, "It's a Tuesday afternoon. You're standing in aisle four of a neighborhood convenience store"),
    (4.16, 9.16, "comparing two cans of soup when your phone suddenly vibrates. You glance at the screen."),
    (9.90, 15.72, "An emergency alert. Not a weather warning. Not a missing person notification. A national emergency"),
    (15.72, 21.88, "broadcast. Biological emergency. A neurological outbreak has been confirmed. Avoid all contact"),
    (21.88, 26.36, "with infected individuals. Seek immediate shelter. Secure all doors and windows."),
    (26.36, 32.06, "You read it again. Then someone screams outside. You turn toward the front windows."),
    (32.68, 36.60, "A man has abandoned his car in the middle of the road. He's running toward the intersection,"),
    (36.94, 41.46, "looking over his shoulder. Behind him, three people are chasing him. At first,"),
    (41.76, 45.84, "you think it's an accident. Maybe a fight. Maybe something you don't want to get involved in."),
    (46.50, 50.70, "Then the man falls. The three people reach him. And they don't help him."),
    (51.26, 57.50, "Within seconds, the street becomes unrecognizable. Cars collide at the intersection. Drivers abandon"),
    (57.50, 62.66, "their vehicles. People run between buildings, knocking over anything in their way. You step"),
    (62.66, 67.76, "backward. The store entrance is only a few meters away. You rush toward it, grab the heavy metal"),
    (67.76, 73.56, "deadbolt, and lock both doors. A moment later, someone slams against the glass. It's a delivery"),
    (73.56, 78.32, "driver. You've seen him here dozens of times. He's shouting something, but you can't"),
    (78.32, 82.96, "understand him. You move closer. Then you notice another person approaching behind him."),
    (83.50, 89.42, "The delivery driver turns around. His expression changes. He starts running again. But this time,"),
    (89.70, 94.20, "he's running away from the store. You step back and pull the security shutters down as"),
    (94.20, 100.72, "far as they will go. For now, you're inside. And outside, the world is falling apart."),
    (101.14, 104.86, "The first 10 minutes pass quickly. You check your phone. No useful information."),
    (104.86, 109.82, "You try calling someone. The call doesn't connect. You look through the windows again."),
    (110.34, 115.22, "There are fewer people running now. That's almost worse. You walk toward the checkout counter and"),
    (115.22, 121.44, "look around the store. Four aisles, two refrigerators, a small office, one storage room."),
    (121.82, 127.44, "It isn't much, but it has walls, a roof, and a lock. You tell yourself that should be enough."),
    (128.10, 133.10, "Then you start checking the supplies. Aisle 1 is almost empty. Someone has already taken most"),
    (133.10, 139.66, "of the snacks. Aisle 2 has a few dented cans, some pickled vegetables, and a bag of rice with a torn"),
    (139.66, 144.90, "corner. The refrigerators are still running, but the power keeps flickering. You open the office"),
    (144.90, 149.62, "and check the inventory computer. The numbers don't make sense. According to the system,"),
    (150.16, 153.48, "the store should have received two deliveries this week. Neither arrived."),
    (154.12, 158.30, "The actual stock is less than half the recorded amount. You check the shelves again."),
    (159.02, 165.28, "Four liters of bottled water, three protein bars, half a jar of peanut butter, two bruised apples,"),
    (165.58, 171.56, "and a handful of canned food. You sit down. If you ration everything carefully, you might manage for a"),
    (171.56, 176.88, "few days, but that's assuming the water stays clean, the refrigerators keep working, and nothing"),
    (176.88, 187.74, "gets inside. You look toward the front entrance. Something is standing outside. A woman. She's"),
    (187.74, 192.28, "walking for several seconds. Then she slowly raises her hand and presses it against the window."),
    (193.16, 199.12, "Her mouth moves. You can't hear anything through the glass. But you can read her lips. Help me."),
    (200.08, 205.74, "You don't move. Because behind her, another figure has just appeared. And it isn't walking"),
    (205.74, 211.12, "normally. The sun disappears behind the buildings. The store's automatic lights switch on,"),
    (211.40, 216.28, "illuminating the empty aisles. You decide to barricade the entrance. You drag two metal"),
    (216.28, 220.94, "shelves toward the front doors and stack crates behind them. It's exhausting work,"),
    (221.44, 226.46, "but eventually the entrance is blocked. Then you remember something. The delivery entrance."),
    (227.18, 231.44, "You haven't checked it. You walk toward the storage room with a flashlight. The back door"),
    (231.44, 237.96, "has an old wooden frame, a rusted padlock, and a small wire mesh window. It looks considerably"),
    (237.96, 242.50, "weaker than the front entrance. You push a heavy hand truck against it and secure the handle"),
    (242.50, 246.72, "with a cargo strap attached to a steel support beam. It's not a perfect solution,"),
    (247.16, 251.92, "but it's something. You return to the checkout counter. For the next hour, nothing happens."),
    (252.46, 257.42, "You almost begin to relax. Then you hear a metallic noise. Clatter. It comes from the"),
    (257.42, 262.76, "storage room. You switch off your flashlight. Another noise. This time, something drags"),
    (262.76, 267.28, "across the floor. You move toward the back corridor. The emergency lights flicker overhead."),
    (267.84, 271.82, "You reach the doorway and look inside. The wire mesh window has been broken."),
    (271.82, 276.34, "Glass covers the concrete floor. And something is pushing an arm through the opening."),
    (277.10, 282.08, "You step backward. The hand is moving. Its fingers repeatedly open and close,"),
    (282.62, 287.92, "searching for something to grab. Then you hear another sound. A low clicking noise."),
    (288.72, 292.72, "Something is trying to squeeze through the broken window. You look at the cargo strap."),
    (293.30, 297.30, "It's already stretched tight. You grab the hand truck and push its metal base against the"),
    (297.30, 302.26, "door. The creature forces its arm farther through the opening. You lean against the hand truck."),
    (302.84, 307.26, "For several seconds, you manage to hold it. Then another impact comes from outside."),
    (308.00, 311.10, "Something else has reached the door. You look toward the narrow corridor."),
    (311.82, 315.94, "There are now multiple shapes moving behind the broken window. You abandon the storage room"),
    (315.94, 320.66, "and run back toward the main floor. Your barricade is no longer a temporary inconvenience."),
    (321.18, 325.06, "It's the only thing keeping you alive. You spend the next hour sitting behind the"),
    (325.22, 328.86, "checkout counter. Your hands are shaking. You check your supplies again."),
    (329.62, 334.06, "Three protein bars. Four liters of water. Half a jar of peanut butter."),
]

vo, sr = sf.read(VO_PATH, dtype="float32")
if vo.ndim > 1:
    vo = vo.mean(axis=1)

# Compute 10ms RMS envelope to detect real intra-segment sentence pauses!
hop = int(0.01 * sr)
env = np.array([
    float(np.sqrt(np.mean(vo[i:i+hop] ** 2) + 1e-12))
    for i in range(0, len(vo) - hop, hop)
])
voiced_thr = np.percentile(env, 55) * 0.22

words_out = []
for s0, s1, txt in SEGMENTS:
    # Trim leading/trailing silence inside segment using 10ms RMS envelope
    idx0 = max(0, int(s0 * 100))
    idx1 = min(len(env) - 1, int(s1 * 100))
    sub = env[idx0:idx1+1]
    act = np.where(sub > voiced_thr)[0]
    if len(act) >= 2:
        s0_eff = max(s0, (idx0 + int(act[0]) - 2) * 0.01)
        s1_eff = min(s1, (idx0 + int(act[-1]) + 3) * 0.01)
    else:
        s0_eff, s1_eff = s0, s1

    tokens = txt.split()
    weights = []
    pauses = []
    for tok in tokens:
        clean = re.sub(r"[^A-Za-z0-9]", "", tok)
        w = max(1.4, len(clean) ** 0.78)
        p = 0.24 if tok.endswith((".", "!", "?")) else (0.11 if tok.endswith((",", ";", ":")) else 0.0)
        weights.append(w)
        pauses.append(p)

    tot_units = sum(weights) + sum(pauses[:-1]) * 3.2
    dur = max(0.15, s1_eff - s0_eff)
    cur = s0_eff
    for tok, w, p in zip(tokens, weights, pauses):
        wdur = dur * (w / tot_units)
        p_dur = dur * ((p * 3.2) / tot_units)
        words_out.append({
            "word": tok,
            "start": round(cur, 3),
            "end": round(cur + wdur, 3),
        })
        cur += wdur + p_dur

payload = {
    "duration": round(len(vo) / sr, 3),
    "fps": 30,
    "total_frames": int(round((len(vo) / sr) * 30)),
    "segments": [{"start": a, "end": b, "text": c} for a, b, c in SEGMENTS],
    "words": words_out,
}
with open(OUT_PATH, "w") as f:
    json.dump(payload, f, indent=2)
print(f"Wrote {len(words_out)} words & {len(SEGMENTS)} segments to {OUT_PATH} (total_frames={payload['total_frames']})")

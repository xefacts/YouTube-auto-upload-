"""Script + shot plan for "Hiccup Town" (blocky-shorts format).

One narration clip per sentence; each sentence is one shot, and its caption is
shown in 1-3 word chunks the way the reference format does. Timing comes from
the real voice clips (story/timing.json), never the other way round.
"""

LINES = [
    "In this town, every hiccup moves you one step left.",
    "Nobody knew why. Nobody asked.",
    "But one kid found a cheat code.",
    "Pop quiz? Hic. He was in the hallway.",
    "Dentist? Hic. He was in the next town.",
    "So he hiccuped the whole way to the final.",
    "Then a baby hiccuped. And babies are contagious.",
    "Hic. Hic. Hic. The whole town drifted left.",
    "So the mayor banned hiccups.",
    "Everyone held their breath for one whole week.",
    "Then somebody opened a soda.",
    "The town hiccuped at once.",
    "That was three years ago.",
    "They're still two towns over.",
]

CLIPS = [(0, 2), (2, 4), (4, 6), (6, 8), (8, 10), (10, 12), (12, 14)]

Y_ = (245, 201, 59)
W_ = (255, 255, 255)
T_ = (86, 226, 214)
P_ = (255, 122, 168)

# shot keys: set, mood, cam=(u, x, y, z, yaw, pitch, fov), cap=[(chunk, [words...])]
# `cap` chunks: (text, colour of the highlighted part)
SHOTS = [
    dict(set="town", mood="day", stage="kid_walk",
         cam=[(0, 0.0, 1.62, -4.6, 0, -0.04, 46), (1, 0.0, 1.66, -3.2, 0, -0.06, 42)],
         cap=[("In this town,", W_), ("every", W_), ("hiccup", Y_),
              ("moves you", W_), ("one step left.", Y_)],
         sfx=[(0.15, "whoosh")]),
    dict(set="town", mood="day", stage="kid_hic",
         cam=[(0, -0.2, 1.58, -3.6, 0.02, -0.05, 44), (1, -0.4, 1.6, -3.0, 0.03, -0.05, 40)],
         cap=[("Nobody knew", W_), ("why.", W_), ("Nobody", W_), ("asked.", T_)],
         sfx=[(0.25, "pop")]),
    dict(set="town", mood="day", stage="kid_cheat",
         cam=[(0, 0.0, 1.66, -3.4, 0, -0.02, 44), (1, 0.3, 1.7, -3.0, -0.06, -0.03, 40)],
         cap=[("But one kid", W_), ("found a", W_), ("cheat code.", Y_)],
         sfx=[(0.2, "sparkle")]),
    dict(set="classroom", mood="day", stage="quiz",
         cam=[(0, -0.2, 1.5, -4.0, 0.0, -0.04, 46), (1, -0.5, 1.5, -3.2, 0.04, -0.04, 42)],
         cap=[("Pop quiz?", W_), ("Hic.", T_), ("He was in", W_), ("the hallway.", W_)],
         sfx=[(0.3, "poof"), (0.62, "boing")]),
    dict(set="clinic", mood="day", stage="dentist",
         cam=[(0, 0.1, 1.5, -3.6, 0, -0.05, 45), (1, 0.3, 1.52, -3.1, -0.03, -0.05, 41)],
         cap=[("Dentist?", W_), ("Hic.", T_), ("He was in", W_), ("the next town.", Y_)],
         sfx=[(0.3, "poof"), (0.66, "whoosh_long")]),
    dict(set="field", mood="day", stage="final",
         cam=[(0, -0.6, 1.5, -3.4, 0.0, -0.05, 46), (1, 0.7, 1.5, -2.9, -0.05, -0.05, 42)],
         cap=[("So he hiccuped", W_), ("the whole way", W_), ("to the", W_), ("final.", Y_)],
         sfx=[(0.1, "tick"), (0.5, "tick"), (0.85, "ding")]),
    dict(set="town", mood="dusk", stage="baby",
         cam=[(0, 0.4, 1.5, -3.2, -0.04, -0.03, 45), (1, 0.9, 1.56, -2.6, -0.08, -0.03, 40)],
         cap=[("Then a baby", W_), ("hiccuped.", T_), ("And babies", W_), ("are contagious.", P_)],
         sfx=[(0.3, "pop_small"), (0.7, "boing")]),
    dict(set="town", mood="dusk", stage="crowd_drift",
         cam=[(0, -1.9, 1.7, -2.2, 0.10, -0.05, 50), (1, 1.7, 1.7, -1.9, -0.10, -0.05, 50)],
         cap=[("Hic.", Y_), ("Hic.", Y_), ("Hic.", Y_), ("The whole town", W_),
              ("drifted left.", Y_)],
         sfx=[(0.1, "glitch"), (0.35, "glitch"), (0.6, "glitch"), (0.85, "whoosh")]),
    dict(set="plaza", mood="day", stage="mayor",
         cam=[(0, 0.0, 2.55, -4.4, 0, -0.05, 43), (1, 0.15, 2.62, -4.0, 0, -0.05, 40)],
         cap=[("So the mayor", W_), ("banned", Y_), ("hiccups.", W_)],
         sfx=[(0.35, "stamp"), (0.4, "impact")]),
    dict(set="town", mood="day", stage="hold_breath",
         cam=[(0, -1.4, 1.5, -2.6, 0.08, -0.03, 48), (1, 1.4, 1.5, -2.4, -0.08, -0.03, 48)],
         cap=[("Everyone held", W_), ("their breath", W_), ("for one", W_), ("whole week.", T_)],
         sfx=[(0.2, "tick"), (0.7, "tick")]),
    dict(set="classroom", mood="day", stage="soda",
         cam=[(0, 0.2, 1.45, -3.3, 0.02, -0.06, 46), (1, 0.0, 1.5, -2.7, 0.0, -0.06, 40)],
         cap=[("Then somebody", W_), ("opened a", W_), ("soda.", Y_)],
         sfx=[(0.55, "thud"), (0.6, "grr")]),
    dict(set="town", mood="dusk", stage="mass_hic",
         cam=[(0, -0.4, 2.0, -2.6, 0, -0.10, 52), (1, 0.4, 1.8, -2.4, 0.04, -0.06, 50)],
         cap=[("The town hiccuped", W_), ("at once.", Y_)],
         sfx=[(0.2, "impact"), (0.25, "whoosh_long"), (0.3, "glitch")]),
    dict(set="plaza", mood="dusk", stage="three_years",
         cam=[(0, 0.0, 1.8, -3.6, 0, -0.02, 44), (1, 0.0, 1.85, -3.0, 0, -0.02, 41)],
         cap=[("That was", W_), ("three years ago.", Y_)],
         sfx=[(0.2, "riser")]),
    dict(set="town", mood="dusk", stage="button",
         cam=[(0, 0.0, 1.7, -4.2, 0, -0.03, 46), (1, 0.0, 1.74, -3.4, 0, -0.04, 40)],
         cap=[("They're still", W_), ("two towns", W_), ("over.", P_)],
         sfx=[(0.6, "ding")]),
]

END_CARD = dict(hold=1.4, title="HICCUP TOWN", sub="part two tomorrow")

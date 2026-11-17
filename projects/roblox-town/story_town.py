"""Hiccup Town: narration, shot list and camera keys (blocky-shorts v2 look)."""

W_ = (250, 250, 248)
Y_ = (245, 201, 59)
T_ = (126, 226, 214)
P_ = (244, 152, 196)

LINES = [
    "In this town, every hiccup moves you one step left.",
    "Nobody knew why. Nobody asked.",
    "But one kid found a cheat code.",
    "Pop quiz? Hic. He was in the hallway.",
    "Dentist? Hic. He was in the next town.",
    "So he hiccuped the whole way to the final.",
    "Then a baby hiccuped.",
    "And babies are contagious.",
    "Hic. Hic. Hic. The whole town drifted left.",
    "So the mayor banned hiccups.",
    "Everyone held their breath for one whole week.",
    "Then somebody opened a soda.",
    "The town hiccuped at once.",
    "That was three years ago.",
    "They're still two towns over.",
]

CLIPS = [(0, 2), (2, 4), (4, 6), (6, 9), (9, 11), (11, 13), (13, 15)]

# shot: set, mood, stage, camera keys (u, x, y, z, yaw, pitch, fov), caption chunks, sfx
SHOTS = [
    dict(set="street", mood="day", stage="kid_walk",
         cam=[(0, 0.2, 1.05, 2.4, 11.5, 0.14, -0.04, 42), (1, 0.1, 1.05, 1.6, 9.6, 0.10, -0.03, 41)],
         cap=[("In this town,", W_), ("every", W_), ("hiccup", Y_), ("moves you", W_),
              ("one step", W_), ("left.", Y_)],
         sfx=[(0.0, "whoosh"), (0.55, "pop")]),

    dict(set="street", mood="day", stage="kid_hic",
         cam=[(0, 0.1, 1.30, 0.1, 4.9, 0.02, 0.00, 40), (1, 0.0, 1.32, 0.1, 4.3, 0.01, 0.00, 39)],
         cap=[("Nobody", W_), ("knew", W_), ("why.", Y_), ("Nobody", W_), ("asked.", W_)],
         sfx=[(0.3, "blip")]),

    dict(set="street", mood="day", stage="kid_cheat",
         cam=[(0, -0.8, 1.10, 1.0, 7.6, 0.16, -0.02, 42), (1, -0.6, 1.12, 0.9, 6.6, 0.12, -0.02, 41)],
         cap=[("But one kid", W_), ("found a", W_), ("cheat code.", Y_)],
         sfx=[(0.1, "sparkle")]),

    dict(set="classroom", mood="day", stage="quiz",
         cam=[(0, 0.0, 1.02, 4.2, 8.6, 0.02, -0.01, 42), (1, 0.2, 1.05, 4.1, 7.8, 0.00, -0.01, 41)],
         cap=[("Pop quiz?", W_), ("Hic.", T_), ("He was in", W_), ("the hallway.", W_)],
         sfx=[(0.4, "pop"), (0.55, "whoosh")]),

    dict(set="clinic", mood="day", stage="dentist",
         cam=[(0, -0.3, 1.02, 4.0, 7.0, 0.02, -0.01, 42), (1, 0.2, 1.05, 4.0, 6.2, 0.03, -0.01, 41)],
         cap=[("Dentist?", W_), ("Hic.", T_), ("He was in", W_), ("the next town.", Y_)],
         sfx=[(0.35, "pop"), (0.5, "whoosh_long")]),

    dict(set="field", mood="day", stage="final",
         cam=[(0, 0.4, 0.95, 3.2, 8.2, 0.04, 0.06, 44), (1, 0.9, 1.0, 3.0, 7.0, 0.02, 0.05, 43)],
         cap=[("So he hiccuped", W_), ("the whole way", W_), ("to the", W_), ("final.", Y_)],
         sfx=[(0.0, "riser"), (0.5, "ding")]),

    dict(set="street", mood="dusk", stage="baby",
         cam=[(0, -0.2, 0.98, 1.9, 5.6, 0.04, -0.01, 42), (1, -0.1, 1.02, 1.9, 4.8, 0.03, -0.01, 41)],
         cap=[("Then a baby", W_), ("hiccuped.", T_)],
         sfx=[(0.25, "pop_small")]),

    dict(set="street", mood="dusk", stage="crowd_drift",
         cam=[(0, 0.6, 1.05, 3.6, 11.5, 0.12, -0.03, 43), (1, -0.6, 1.05, 3.6, 10.5, -0.10, -0.03, 43)],
         cap=[("And babies", W_), ("are contagious.", P_), ("Hic.", Y_), ("Hic.", Y_),
              ("Hic.", Y_)],
         sfx=[(0.2, "pop"), (0.45, "pop"), (0.7, "pop")]),

    dict(set="street", mood="dusk", stage="mass_hic",
         cam=[(0, 0.0, 1.05, 3.4, 11.5, 0.02, -0.03, 44), (1, 0.0, 1.10, 3.2, 10.0, 0.00, -0.03, 43)],
         cap=[("The whole town", W_), ("drifted", Y_), ("left.", Y_)],
         sfx=[(0.3, "impact"), (0.5, "whoosh_long")]),

    dict(set="plaza", mood="day", stage="mayor",
         cam=[(0, -0.4, 1.50, 6.4, 7.6, 0.02, -0.01, 42), (1, -0.3, 1.55, 6.4, 6.8, 0.00, -0.01, 41)],
         cap=[("So the mayor", W_), ("banned", Y_), ("hiccups.", W_)],
         sfx=[(0.35, "stamp"), (0.5, "thud")]),

    dict(set="street", mood="day", stage="hold_breath",
         cam=[(0, 0.0, 1.05, 2.7, 8.2, 0.10, -0.02, 42), (1, 0.0, 1.05, 2.7, 7.2, -0.10, -0.02, 42)],
         cap=[("Everyone held", W_), ("their breath", W_), ("for one", W_),
              ("whole week.", T_)],
         sfx=[(0.15, "tick"), (0.55, "tick")]),

    dict(set="classroom", mood="day", stage="soda",
         cam=[(0, 0.8, 1.05, 4.2, 5.4, -0.04, -0.01, 41), (1, 0.9, 1.08, 4.2, 4.7, -0.03, -0.01, 40)],
         cap=[("Then somebody", W_), ("opened a", W_), ("soda.", Y_)],
         sfx=[(0.45, "pop"), (0.55, "flash")]),

    dict(set="street", mood="day", stage="mass_hic",
         cam=[(0, 0.0, 1.05, 3.2, 9.4, 0.0, -0.02, 43), (1, 0.0, 1.10, 3.0, 8.2, 0.0, -0.02, 42)],
         cap=[("The town", W_), ("hiccuped", Y_), ("at once.", Y_)],
         sfx=[(0.1, "impact"), (0.35, "stamp")]),

    dict(set="street", mood="dusk", stage="three_years",
         cam=[(0, -0.1, 1.05, 2.5, 7.4, 0.05, -0.02, 42), (1, 0.0, 1.08, 2.5, 6.5, 0.02, -0.02, 41)],
         cap=[("That was", W_), ("three years ago.", Y_)],
         sfx=[(0.2, "night_hit")]),

    dict(set="street", mood="dusk", stage="button",
         cam=[(0, 0.1, 1.10, 3.2, 8.4, 0.04, -0.02, 42), (1, 0.2, 1.12, 3.2, 7.4, 0.02, -0.02, 41)],
         cap=[("They're still", W_), ("two towns", P_), ("over.", P_)],
         sfx=[(0.2, "pop_small")]),
]

END_CARD = dict(hold=1.7, title="HICCUP TOWN", sub="part two tomorrow")

NARRATION = [
    ("town_audio/01_hook.mp3",
     "Down here in Lowtown, rent eats half your paycheck before the month even starts."),
    ("town_audio/02_reveal.mp3",
     "But a thousand feet above the clouds, an entire city floats on golden pillars."),
    ("town_audio/03_elevator.mp3",
     "The only way up is one golden elevator, and its single button costs more than most of us earn in a year."),
    ("town_audio/04_maya.mp3",
     "Maya grew up watching that button glow red: insufficient funds, every single time."),
    ("town_audio/05_saving.mp3",
     "So she saved for six years, coin by coin, skipping new clothes, skipping vacations, skipping everything."),
    ("town_audio/06_green.mp3",
     "The day that button finally turned green, the whole street stopped just to watch her walk inside."),
    ("town_audio/07_empty.mp3",
     "At the top, she found no mansion, no luxury. Just an empty room, and a sign: the view is free, but silence costs extra."),
    ("town_audio/08_lesson.mp3",
     "The gap between the ground and the clouds was never about height. It was about access. "
     "Today the top one percent hold roughly a third of all wealth in the country. "
     "The real climb starts long before any elevator opens."),
]


def word_timings(text: str, duration: float):
    tokens = text.split()
    weights = []
    for t in tokens:
        w = len(t) + 2.0
        if t and t[-1] in ",;:":
            w += 3.0
        if t and t[-1] in ".!?":
            w += 5.0
        weights.append(w)
    total = sum(weights) or 1.0
    out = []
    t0 = 0.0
    for tok, w in zip(tokens, weights):
        d = duration * w / total
        out.append((t0, t0 + d, tok.strip(".,;:!?\"'")))
        t0 += d
    return out

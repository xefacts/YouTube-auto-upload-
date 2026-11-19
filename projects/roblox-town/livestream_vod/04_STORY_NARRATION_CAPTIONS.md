# Story, narration, captions — first two completed missions

**Status:** every line below is a *template with slots*. Slots are filled from
`evidence/*.json` only. Until a slot is filled, the line cannot ship — that is the whole
point: we write the shape of the story now, and the facts arrive from the transcript/frame
pass, not from my imagination.

## 1. Series spine (two shorts, one look)

| | M1 short | M2 short |
|---|---|---|
| Length | 52 s | 48 s |
| Hook | the completion banner, out of context | the second completion banner, mirrored |
| Middle | attempts → fail → the one change → clutch | setup → complication → setback → the switch → clutch |
| Payoff | banner + reaction + "1 down" | banner + reaction + "2 for 2" |
| Button | "Mission two, same town." | "Next stream, mission three." |
| Caption font | Inter Display ExtraBold, uppercase, 1 yellow word | same |
| Aspect | 1080×1920, 30 fps, −14 LUFS | same |

Voice: the existing pack's narration style — short, deadpan, second person off, ~2.6 words
per second. No hype words ("insane", "crazy") and no fake stakes.

## 2. Slot dictionary (what fills what)

| Slot | Filled from | Example of a legal value |
|---|---|---|
| `{{MISSION_NAME}}` | on-screen mission title (S3 frame text), verbatim | `"DELIVERY RUN"` |
| `{{ATTEMPTS}}` / `{{M2_ATTEMPTS}}` | count of visible attempts inside the extracted window, or the transcript's own number | `6` (only if countable in the window) |
| `{{OBJECTIVE_VERBATIM}}` | on-screen objective text | `"deliver 3 pizzas before 6pm"` |
| `{{FIRST_ATTEMPT_ACTION}}` | transcript line describing the attempt | `"he goes straight for the shortcut"` |
| `{{FAIL_CONSEQUENCE_VERBATIM}}` | transcript line or on-screen fail text | `"timer reset"` |
| `{{THE_CHANGE}}` | transcript: what he changed | `"he took the long way"` |
| `{{SECONDS_LEFT}}` | a visible counter | `4` |
| `{{COMPLETION_VERBATIM}}` | banner text + the clip's own final action | `"MISSION COMPLETE — 1 of 4"` |
| `{{REACTION_VERBATIM}}` | transcript, quoted or tightly paraphrased | `"no way, no way"` |
| `{{TOTAL_LEFT}}` | visible counter | `3` |
| `{{M2_*}}` | same rules, M2 window | — |

**Writing rules**

1. Never state a mechanic the footage does not show (no "boss", no "team" unless seen).
2. Never state a number that is not visible or spoken in the window.
3. Slots that stay empty are *deleted with their sentence* — the timing budget absorbs it
   (that is why the EDL has 52/48 s targets with ±6 s slack).
4. No real names, no chat handles, no third-party brands read on screen.

## 3. M1 narration (final text, slots unfilled)

```
M1-01  {{MISSION_NAME}} took him {{ATTEMPTS}} tries.
M1-02  Mission {{MISSION_NUMBER}}: {{OBJECTIVE_VERBATIM}}.
M1-03  First try: {{FIRST_ATTEMPT_ACTION}}.
M1-04  {{FAIL_CONSEQUENCE_VERBATIM}}.
M1-05  Again. And again.
M1-06  Then he changed one thing: {{THE_CHANGE}}.
M1-07  {{SECONDS_LEFT}} seconds left.
M1-08  And then — {{COMPLETION_VERBATIM}}.
M1-09  {{REACTION_VERBATIM}}
M1-10  One down. {{TOTAL_LEFT}} to go.
M1-11  Same banner. Different man.
M1-12  Mission two, same town.
```

## 4. M2 narration (final text, slots unfilled)

```
M2-01  Second mission. {{M2_ATTEMPTS}} tries.
M2-02  {{M2_OBJECTIVE_VERBATIM}}
M2-03  {{M2_COMPLICATION_VERBATIM}}
M2-04  {{M2_SETBACK_VERBATIM}}
M2-05  So he stopped {{OLD_METHOD}}. Started {{NEW_METHOD}}.
M2-06  This was the run.
M2-07  {{M2_COMPLETION_VERBATIM}}
M2-08  {{M2_REACTION_VERBATIM}}
M2-09  Two missions. One session.
M2-10  Next stream, mission three.
```

## 5. Captions

| Rule | Value |
|---|---|
| Chars per line | ≤ 18, max 2 lines, max 7 words |
| Case | UPPERCASE |
| Highlight | exactly one word per caption in brand yellow `#FFD24A` |
| Position | baseline at 81.5 % frame height (same as the Hiccup Town pack) |
| Timing | appears 40 ms after the cut, holds until 100 ms before the next cut |
| Numbers | digits, never spelled out |
| Slot captions | if a slot is empty, its caption is deleted with it |

Caption text per beat is already in `03_EDL_M01_M02.csv` (column `caption`).

## 6. End cards (our own assets — no footage, no slots)

- M1: `MISSION 2 →` · subline: `same town, same stream`
- M2: `MISSION 3 →` · subline: `next stream`
- Both: 6 s, freeze frame at 92 % brightness, 3 % scale drift, `swish.wav`, no music tail.

## 7. If cloud verification never becomes available

Then these two shorts ship as **`UNVERIFIED` cuts** only if you supply the windows yourself,
because the honest fallback is: *the editor saw the window, so the editor may describe the
window.* In that case the narration collapses to three sentences that are true of any window
you hand over (attempt, fail, completion) and the rest of the beats are cut — the shorts run
~30 s each and are labelled in the description as "cut from livestream VOD". What we never do
is narrate a specific event, number or name we have not seen.

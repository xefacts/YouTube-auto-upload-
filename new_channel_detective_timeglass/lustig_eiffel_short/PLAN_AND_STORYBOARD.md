# PLAN + STORYBOARD — Short #3: "The Man Who Sold the Eiffel Tower"
Status: **AWAITING APPROVAL** — kuch bhi render nahi hua. Approval ke baad: VO → timing → stills sheet → full render.

---

## 1. Concept

**Title:** THE MAN WHO SOLD THE EIFFEL TOWER (twice)
**Format:** 9:16 animated short, ~55 s, Rick-Clips style (2D bean-head characters in painted 3D world, world ink, DOF, gliding cameras), V2 text system (captions + counter + labels).

**Hook (absurd fact, sentence 1):** *A man sells the Eiffel Tower. Twice — and nobody calls the police.*

**Why it works (viral potential, no promises):**
- Paradox stated as fact + escalating stakes (six dealers → bribe → vanishing → he does it AGAIN)
- Props carry the joke: forged papers with wax stamp, money stacks, identical second meeting framed like a photograph (visual rhyme)
- Everyday mechanism everyone feels: **shame as an alibi** — the victim stays silent because reporting it would confess his own crime
- Ironic payoff: caught for fake money, never for the landmark; callback gag — the tower still charges admission, Lustig paid nothing
- Fits channel identity (detective/history shorts — D.B. Cooper lineage)

**True or legend:** Based on the famous account first recorded in book form in **1961**; the **second sale is disputed** (some records say a buyer got suspicious and he fled). We show one small honesty label, bottom-left, during setup:
> `BASED ON THE 1961 ACCOUNT`
(Exactly the honesty-label pattern from the tech-explainer skill.)

**Facts verified (web):**
- 1925, Paris; posed as Deputy Director-General, Ministry of Posts and Telegraphs; forged government papers; invited **six** scrap dealers to a confidential meeting at a grand hotel ✓
- Buyer **André Poisson** (name from the 1961 account), paid price + a **bribe** ✓
- Victim too embarrassed to report → Lustig returned to Paris and attempted the same con again ✓ (outcome of attempt 2 disputed → covered by honesty label)
- Caught **May 1935** in New York — for **counterfeiting**, not the tower ✓
- Sources: Smithsonian-adjacent retellings, Times of India, sinistercrimes timeline, funfactz, AOL — see search results this session

---

## 2. Script (ready to record — ~140 words ≈ 55 s at your take pace ≈2.55 w/s)

```
A man sells the Eiffel Tower. Twice — and nobody calls the police.

Paris, nineteen twenty-five. Con man Victor Lustig forges government papers
and calls six scrap dealers to a secret hotel meeting.

He claims the city can't afford the tower — so it's quietly being sold
for scrap. One dealer, Poisson, wants it so badly he pays a bribe on top
of the price.

The deal closes. Lustig vanishes. Poisson never says a word.

You see, the bribe was Poisson's own crime — reporting the sale would
confess it. Shame was the perfect alibi.

So Lustig comes back and runs the exact same trick again.

They catch him in nineteen thirty-five — for fake money, not for landmarks.

The tower still charges admission. Lustig never paid a franc.
```

Beat formula check: hook paradox ✓ · setting (time/place/named everyman/numbers) ✓ · escalation (bribe = the "dare" exaggeration joke) ✓ · mystery beat ("Poisson never says a word") ✓ · pivot "You see," → mechanism ✓ · second escalation (he returns) ✓ · ironic payoff (caught for fake money) ✓ · callback twist (admission gag, ends on last word) ✓.

VO options: **(A)** main TTS narrator voice se bana doon (fastest), **(B)** aap script paste karke ElevenLabs se record kar do (dono takes ka pattern: 123 w ≈47 s, yeh ≈55 s).

---

## 3. Look & style spec

- **Same as V2 engine** (cartoon-audio-short kit + v2 overlay layer — kit survives in `uncase_ricksclips_style_dbcooper/kit_build`; v2 code reconstructible):
- Day/golden/night-blue light presets with 10-frame crossfades; world ink ~3 px @1080; DOF 12–16 on CUs; camera smootherstep glides, holds creep, flash cuts only on time jumps; sheen highlights on key props (papers, money)
- **Text layer (V2):** word captions (white bold + outline, lower-middle) · title card `THE MAN WHO SOLD THE EIFFEL TOWER · PARIS 1925` · **year counter** top-left: rolls 1925 → 1935 at the arrest beat · object labels w/ leader lines: `FORGED PAPERS`, `THE BUYER`, `THE TOWER`, `FAKE HUNDREDS` · event chips (gold accents): `SECRET MEETING`, `THE BRIBE`, `HE VANISHES`, `THE PERFECT ALIBI`, `HE DOES IT AGAIN`, `CAUGHT — NOT FOR THE TOWER` · **gold flow arrow** = the money handover (invisible crime made visible) · honesty label bottom-left
- **No watermark, no CTA** (reference rule: no intro/logo/outro)

---

## 4. STORYBOARD (story frames @30 fps — provisional; exact frames re-derived from `phrases.json` after VO)

| # | Frames (≈s) | VO line | Picture / acting | Camera | Light | Text overlay | SFX |
|---|---|---|---|---|---|---|---|
| S1 | 0–153 (0–5.1) | "A man sells the Eiffel Tower. Twice — and nobody calls the police." | **MCU Lustig** (black suit, slick hair, smug smirk) tips an imaginary hat; behind him through the hotel window: **Eiffel Tower** at golden hour. Red `VENDU / SOLD` sticker on the window pane peels at the corner | slow push-in, slight roll −2° | **golden** | Title card (top) + word captions | sting + city ambience |
| S2 | 153–300 (5.1–10) | "Paris, nineteen twenty-five. Con man Victor Lustig forges government papers…" | **White flash** → wide hotel suite: six dealers around the table, Lustig stands at head with a folder (wax-seal blob, no readable text). Dealer faces: interested → greedy grins | crane down from window onto table (continuous) | day | counter pops **1925** `THE SETUP`; chip `SECRET MEETING`; honesty label | paper slap, room tone |
| S3 | 300–387 (10–12.9) | "…and calls six scrap dealers to a secret hotel meeting." (tail) | MS: papers slide across table to each dealer (prop gag: one dealer sniffs them like wine) | lateral track across faces | day | label `FORGED PAPERS` (leader line → folder) | paper slide ticks |
| S4 | 387–564 (12.9–18.8) | "He claims the city can't afford the tower — so it's quietly being sold for scrap." | Insert CU: **newspaper prop** (blank masthead block + tower sketch) → tilt up to Lustig presenting; window tower in frame | tilt + push | day | word captions only | whoosh |
| S5 | 564–777 (18.8–25.9) | "One dealer, Poisson, wants it so badly he pays a bribe on top of the price." | **Money shot**: stack of bills slides dealer→Lustig; Lustig's sly smile CU; Poisson (vest, eager grin) leans in | top-down tilt then push on faces | day | chip `THE BRIBE`; **gold flow arrow** with packet dot = money path; label `THE BUYER` → Poisson | money slide, coin tick |
| S6 | 777–918 (25.9–30.6) | "The deal closes. Lustig vanishes. Poisson never says a word." | Lustig tips hat, exits frame right; door closes; empty chair left in frame; Poisson frozen mid-grin → grin drops | static hold with creep (no freeze), watch the exit | **golden** | chip `HE VANISHES` | footsteps, door, music stops |
| S7 | 918–1131 (30.6–37.7) | "You see, the bribe was Poisson's own crime — reporting the sale would confess it. Shame was the perfect alibi." | **Poisson alone**, head in hands (temple pose, sweat drop); slow orbit around the table; ghost of the money stack fades where it lay | slow orbit + push | **night-blue** (explanation beat) | chip `THE PERFECT ALIBI`; counter still 1925 | drone, clock tick |
| S8 | 1131–1275 (37.7–42.5) | "So Lustig comes back and runs the exact same trick again." | **White flash** → SAME framing as S2 (visual rhyme joke): new dealer colors, identical poses; Lustig same smirk, same folder | whip-pan match to S2 framing | day | chip `HE DOES IT AGAIN`; flash cut | whoosh, paper slap |
| S9 | 1275–1452 (42.5–48.4) | "They catch him in nineteen thirty-five — for fake money, not for landmarks." | 1935 street: two agents (investigator suits) grab Lustig mid-count of bills; cuffs = wrist cross pose; he scowls (stern) | push through agents to CU | day | **counter rolls 1925 → 1935** (`CAUGHT`); chip `NOT FOR THE TOWER`; label `FAKE HUNDREDS` → money | siren whoosh, cuff snap (kick+flash) |
| S10 | 1452–1605 (48.4–53.5) | "The tower still charges admission. Lustig never paid a franc." | Present-day: ticket booth + queue (guide, visitorA, child), **tower full height** behind; tiny `SOLD` sticker flutters off the booth and flies past camera | crane up from booth → tower wide, roll +2° | **golden** (payoff) | chip `STILL STANDING`; final title pop `SOLD TWICE · ADMITTED ONCE` | warm resolve chord, coin ding on last word |

Shot grammar per reference: 10 shots, **3 flash cuts** only (S2/S8 time jumps + cuff impact kick), continuous glides elsewhere, DOF on S1/S4/S5/S9 CUs (cInf 14–16), campus/tower wide sharp. Light story: golden → day → day → golden → **night-blue** → day → day → golden = mood follows the con's rise/fall/rise.

**Visual callbacks:** S8 reuses S2's exact camera path (the joke); S10's sticker answers S1's sticker; money arrow in S5 returns as `FAKE HUNDREDS` label in S9 (same money, now counterfeit — the irony made visible).

---

## 5. Audio plan
- **Music:** curious march (pluck + brass + kick/snare, 108 bpm) f0→918 — **stops exactly at the vanish** (twist), low drone f918→1452, warm resolve chord f1452→end. Mix: music & SFX at exactly −6 dB vs voice (gated RMS), −14 LUFS out.
- **SFX cues (story frames):** 18 hook sting · 165 paper slap · 600 money slide + coin · 780 door · 918 music-stop whoosh · 1131 flash whoosh · 1300 siren+approach · 1452 cuff snap w/ 7f kick · 1600 coin ding (last word).

---

## 6. Production pipeline & specs
1. VO (A: my TTS narrator / B: your ElevenLabs take) → `timing.py` → exact `phrases.json` + `words.json`
2. Rebuild kit engine + **V2 overlay layer** (captions, counter, labels, chips, gold arrow, honesty label — code all in session history, kit survives workspace wipes)
3. World: 1925 hotel suite (window + tower geometry, table, door),1935 street, present-day booth+tower — all original, painted textures (paint.js), no copy of any reference shot
4. Cast: +3 outfits only (`lustig` black suit slick hair, `poisson` vest, keep dealer/agent suits from existing set)
5. Stills contact sheet → **you look** → full render: **~6,420 frames @120 fps** (SUBDIV=4, ≥6k ✓), 1080×1920, segmented x264 (OOM-safe), loudnorm −14.0 LUFS, freeze/black QA + 3 contact sheets
6. Private Drive upload → link
- Gates: **① STORYBOARD APPROVAL (now)** → ② VO ready → ③ stills sheet (quick look) → ④ render → deliver

---

## 7. Alternates (if this topic doesn't appeal)
- **B — "London Bridge Moved to the Desert"** (1968 auction → $2.46M → Lake Havasu, Arizona, opened1971): physical cause (old bridge too weak/narrow for traffic), ships + desert rebuild = big visuals, workers+suits cast ✓, ironic payoff: tourists queue for a "fake-looking" real bridge.
- **C — "The Moth That Didn't Invent Bugs"**: script ALREADY in your `Two_New_Short_Scripts_ElevenLabs_v4.txt` (117 words) — but **no VO exists** (verified this session: the s32 take is pitch-drop's second take, gap-matched to script one within 0.4 s). Edison-1870s + Smithsonian "probably not Hopper's" facts verified again ✓.

---

## 8. Aapko decide karna hai
1. **Topic approve?** (yeh / B / C / koi naya idea)
2. **VO:** main TTS bana doon, ya aap ElevenLabs se? (script ready hai upar)
3. **Text layer** V2 jaisa hi rakhen? (captions + counter + labels — default YES; agar sirf visuals chahiye to bata dena)

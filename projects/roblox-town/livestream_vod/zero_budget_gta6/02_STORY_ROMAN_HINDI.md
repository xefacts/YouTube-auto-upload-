# Original Cinematic Story — Roman Hindi

**Project:** IShowSpeed GTA 6 (VOD: `qSyo5d-dVzA`)
**Language:** Roman Hindi (Hindi, Latin script)
**Status:** Story structure complete. `{{SLOTS}}` transcript se fill honge.
Slots ke bina ye story ship nahi hogi — ye rule hai, option nahi.

---

## Story ka spine (ek nazar mein)

| Act | Kya hota hai | Duration |
|---|---|---|
| **Hook** | Speed GTA 6 early access mein ghus gaya — 133,000 log live | 8 s |
| **Mission 1** | {{MISSION_1_NAME}} — attempts, fail, phir clutch | 25 s |
| **Mission 2** | {{MISSION_2_NAME}} — complication, setback, phir clutch | 25 s |
| **Payoff** | Do missions, ek stream — aur Speed abhi bhi khel raha hai | 7 s |
| **Total** | | **~65 s** |

---

## Narration script (Roman Hindi) — FINAL TEXT

### [HOOK — 0:00–0:08]

> Ye kahani hai Speed ki.
> Jo ghus gaya GTA 6 ke early access mein — seedha, bina soche.
> 133,000 log live dekh rahe hain.
> Aur pehla mission... yahin se shuru hota hai.

### [MISSION 1 — 0:08–0:33]

> Pehla mission: **{{MISSION_1_NAME}}**.
> Speed ne koshish ki — ek baar. Do baar. Teen baar.
> Har baar fail. Har baar wapas, wahi jagah.
> Phir ek pal aaya... **{{MISSION_1_CLUTCH_MOMENT}}**.
> Aur mission... **complete**.

### [MISSION 2 — 0:33–0:58]

> Dusra mission: **{{MISSION_2_NAME}}**.
> Is baar Speed ne **{{MISSION_2_STRATEGY}}** try kiya.
> Lekin **{{MISSION_2_COMPLICATION}}** ne sab bigaad diya.
> Speed ne haar nahi maani.
> **{{MISSION_2_CLUTCH_MOMENT}}** — aur dusra mission bhi **complete**.

### [PAYOFF — 0:58–1:05]

> Do missions. Ek stream. 133,000 log gawah.
> Aur Speed... abhi bhi khel raha hai.

---

## Slot dictionary (har slot kahan se bharega)

| Slot | Source | Example (FORMAT dikhane ke liye — asal naam transcript se aayega) |
|---|---|---|
| `{{MISSION_1_NAME}}` | On-screen mission title (visual check) ya transcript mein Speed ka bola hua naam | "Bank Heist" |
| `{{MISSION_1_CLUTCH_MOMENT}}` | Transcript line jahan Speed ne strategy change ki | "usne gaadi chhod ke paidal rasta liya" |
| `{{MISSION_2_NAME}}` | On-screen title / transcript | "Getaway Chase" |
| `{{MISSION_2_STRATEGY}}` | Transcript: Speed ne kya try kiya | "seedha highway route" |
| `{{MISSION_2_COMPLICATION}}` | Transcript: kya bigda | "police ne road block kar diya" |
| `{{MISSION_2_CLUTCH_MOMENT}}` | Transcript: clutch moment | "usne train track se shortcut liya" |

**Writing rules (strict):**
1. Koi mechanic, naam, ya number tab tak nahi likhna jab tak transcript/visual mein na dikhe.
2. Slot khaali rahe to uska sentence delete kar do — guess mat bharo.
3. Speed ke asli quotes sirf tab use karo jab transcript mein verbatim milen.
4. Koi real chat handle, koi third-party brand naam narration mein nahi.

---

## Filled example (FORMAT samjhane ke liye — ye asal facts NAHI hain)

> Pehla mission: **Bank Heist**.
> Speed ne koshish ki — ek baar. Do baar. Teen baar.
> Har baar fail. Har baar wapas, wahi jagah.
> Phir ek pal aaya... **usne gaadi chhod ke paidal rasta liya**.
> Aur mission... **complete**.

⚠️ Upar wala example sirf format dikhata hai. Asal mission names aur moments transcript
milne ke baad hi likhe jayenge. Abhi ye sab `UNVERIFIED` hai.

---

## Voiceover notes

| Item | Detail |
|---|---|
| TTS tool | edge-tts (free, no API key) — `pip install edge-tts` |
| Voice | `hi-IN` (Hindi) ya `ur-PK` (Urdu) — Roman Hindi text ko Devanagari mein convert karke TTS karo |
| Alternative | Apni awaz record karo (OBS / phone) — sab se natural |
| Speed | ~2.6 words/second, deadpan, no hype words |
| Music | YouTube Audio Library (free) — tense bed, −26 dB |

**Roman Hindi TTS ka sach:** edge-tts Hindi voices Devanagari text padhti hain. Roman Hindi
(Latin script) ko seedha TTS mein daalne se pronunciation galat ho sakta hai. Isliye:
- **TTS ke liye:** story ko Devanagari mein convert karo (main kar dunga)
- **Captions ke liye:** Roman Hindi hi rakho (audience ke liye)
- **Ya:** apni awaz mein Roman Hindi record karo — ye sab se best hai

---

## End card

- Text: `MISSION 3 →` · subline: `agle stream mein`
- Duration: 6 s, freeze frame, `swish.wav`
- Koi footage nahi, koi slot nahi — ye humara apna asset hai

#!/usr/bin/env python3
"""Maintain a copy-ready prompt beside each identity scene sheet."""
from pathlib import Path
from build_package import VARIANTS
ROOT=Path(__file__).resolve().parent
LOCK="""Use the supplied 00_FINCH_REFINED_CHARACTER_SHEET.png as the ONLY character reference: the same adult freckled ginger male detective with tousled strawberry-blond hair, teal eyes and small ginger moustache. Tailored deep petrol-teal mid-thigh detective coat with storm shoulder yoke and bronze buttons, dark cocoa waistcoat, ivory shirt, restrained burnt-copper scarf, charcoal tapered trousers, cognac lace-up boots, brown cross-body evidence satchel. His signature physical optic is a portrait-OVAL clear copper double-rim magnifying glass, small flip-up round secondary loupe at the TOP, a petrol-teal focus wheel and walnut grip. Keep his face, outfit, hair and prop identical across new image-based poses. Original restrained American 2D editorial animation look, matte ink and cel shading, vertical 9:16. Do not rig or reuse one static cutout; create new expressive poses for the action. No previously rejected character or unapproved channel name."""
NEG="""No music, singing, celebrity imitation, reference-video footage/audio, on-screen subtitles, flashing text, glowing sci-fi scan, supernatural evidence reveal, dead body or gore, extra characters, changing coat or moustache, changing the lens into a round compass, flickering features or invented historical claims. Fictional intro motif only. Preserve phone-safe framing and clear narration."""
lines=[]
for v in VARIANTS:
    label=f"INTRO_{v['id']}_{v['name'].replace(' ','_')}"
    body=f"""# Variant {v['id']} — {v['name']}

**Visual sheet:** `{label}_SCENE_SHEET.png` (one image showing all four beats). **Source still:** `art/{v['scene']}`. This is an original **fictional 4.8-second identity-intro proposal**, not a completed animation or a historical incident. The working label FINCH is not an approved character/channel name.

## Sequence

| Time | What happens |
| --- | --- |
| 0.0–1.0s | {v['beats'][0]}. |
| 1.0–2.3s | {v['beats'][1]}. |
| 2.3–3.6s | {v['beats'][2]}. |
| 3.6–4.8s | {v['beats'][3]}; cut into the actual case. |

**Character dialogue (original US-English voice):** “{v['line']}” Speak naturally from approximately 2.5s; time against the actual recording and shorten the cut if needed. No name or channel name is spoken until the user approves both.

## Copy-ready character lock

> {LOCK}

## Copy-ready image-to-video motion prompt

> {v['prompt']}

## Copy-ready supporting-still prompt

> Create one standalone vertical 9:16 fictional evidence scene: {v['setting'].lower()}. {v['evidence']}. Use the character lock and the selected sheet for face, outfit, satchel and oval hinged-loupe lens. Cinematic teal night atmosphere with warm practical light; legible evidence, expressive but restrained male character pose. One scene, no title or collage, no gore or borrowed footage.

## Sound / QC constraints

> {NEG}

Use a truthful episode hook **before** any branded identity beat if this is later placed in a history Short. No extra captions or subtitles are prescribed here. Choose ONE variant, not all three in a single episode. The moving clip and recorded dialogue are **not yet generated**.
"""
    (ROOT/f'{label}_PROMPT.md').write_text(body)
    lines.append(f"- **{v['id']} {v['name']}** — `{label}_SCENE_SHEET.png` + `{label}_PROMPT.md`; line: “{v['line']}”")
readme=f"""# Finch — refined 2D detective and identity-scene concepts

The user chose the **third character from the latest ten (19 FINCH)** for a stylish detective outfit and more elegant lens. These files are selection-stage concepts, not a completed video, song, historical claim, approved channel name or YouTube action.

- `00_FINCH_REFINED_CHARACTER_SHEET.png`: four reference-guided generated front/left/back/right concept angles plus a detailed oval copper + top flip-loupe lens. Small satchel/loupe variations between angles need continuity cleanup before final animation.
- `art/lens_macro.png`: full-size lens finish target.
- Three **single-image 4-beat identity intro storyboards**, each with its concise video prompt printed on the sheet:
{chr(10).join(lines)}
- `art/scene_a_archive.png`, `art/scene_b_street.png`, `art/scene_c_envelope.png`: separately generated fictional 9:16 scene keyframes.
- `art/pose_focus.png` and `art/pose_reveal.png`: alternative image-based expressions/poses for storyboard composition.

The user's earlier no-music preference remains in force; all three variants use rain/paper/metal foley only. No extra on-screen subtitle overlays. Spoken lines are suggestions, not an approved branded name line. A real 4.8s animated intro and audio track have **not** been generated. Approve one scene and the actual channel/character identity before production or publication.
"""
(ROOT/'README.md').write_text(readme)
print('Wrote 3 prompts and README')

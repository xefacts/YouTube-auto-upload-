# Phase 1 — Reference Comparison

Compares the two genuine reference videos (frames extracted earlier this
project: `town_compare/ref1_a/b/c.jpg` = towers/billionaire video,
`town_compare/ref2_a/b/c.jpg` = robot/apocalypse video) against the
upgraded v2 renderer's actual output (`town_compare/character_face_test.jpg`,
`town_compare/city_test4_clipfix.jpg`, `town_render/phase5_shot*.jpg`,
`town_compare/before_after_comparison.jpg`).

Every observation below is from actually looking at those frames. Nothing
here is invented or inferred from genre convention.

| # | Criterion | Reference videos (ref1/ref2) | New v2 sample | Gap / verdict |
|---|---|---|---|---|
| 1 | Character design | ref1: Roblox-style blocky avatar, cylindrical capped head, trim lines on torso. ref2: blocky robot/mech, backpack-pod shoulders, distinctive silhouette. | Original character with a boxy-but-beveled head, two inset eye panels, a mouth panel, 3 selectable hair styles (short/ponytail/spiky), distinct shirt/pants/shoe colors. | v1 had **no face at all** (see before/after image, left column) — a flat-color box stack. v2 closes most of this gap: it has a legible, distinct face/hair, but it is still a single humanoid archetype, not a per-character silhouette language (robot vs. Roblox-avatar) like the references use to differentiate characters. |
| 2 | Character proportions | Both refs use stylized blocky proportions (oversized head relative to body, short torso) consistent with a "Roblox-inspired" look. | `head_s`-relative proportions (legs 0.62, torso 0.50, head 0.24 of total height at scale 1) deliberately mimic the same blocky-but-readable ratio. | Proportions are in the right family; not pixel-matched to either reference (intentionally — this is meant to be an *original* design, not a copy). |
| 3 | Geometry complexity | ref1 buildings: window-grid facades, gold banding rings, rooftop props (palm trees, signage, boom-barrier gate). ref2: brick-pattern facades, striped awnings, spiral-cone trees, ceiling grates. | v2 buildings: real window grid (lit/unlit variation via seeded RNG), trim frames around windows, door inset, roof cap, bevels; 3-tier beveled tree canopies; streetlight posts with lamp heads. | Window grids and trim are now present (v1 had **zero** windows — flat boxes only, see before/after). Still missing: patterned/textured facades (brick, banding rings), decorative rooftop props, signage, barriers — the renderer has no texture-mapping, only flat per-face colors with small per-face jitter. |
| 4 | Environment detail | Street debris, signage boards, awnings, palm trees, boom-barrier gates — environmental *storytelling* props, not just filler geometry. | Buildings + road + sidewalk + curbs + trees + streetlights + a grass ground-fill, laid out with intentional alternating placement and consistent scale (`build_city_block`). | Structurally sound and correctly scaled/occluded, but has no narrative "clutter" props (no debris, signage, or barriers) — environment reads as clean/generic rather than lived-in. |
| 5 | Lighting | ref1: bright even daylight with soft volumetric-looking clouds, emissive rooftop light dots. ref2: dramatic orange dusk rim-light, moody interior red lighting with a hard-edged gobo/grate shadow. | v2 has one directional light + ambient + up to 8 per-pixel-attenuated point lights (used here as warm "streetlight glow" accents) + a sky gradient. | v2 lighting is real (not faked) but single-mood: no gobo/patterned shadows, no color-graded "dusk/interior" presets exercised in this sample (the *code* in `camera_rig.py`/`Scene2` supports changing `sky_top/bottom`, `ambient`, `light_dir`, but only one daytime preset was actually rendered and inspected here). |
| 6 | Shadows | ref1: soft ambient-only shadows. ref2: a real hard-edged directional gobo/shaft-of-light shadow pattern cast through a grate — genuine directional shadow-casting. | v2 casts per-character "blob" ground shadows (soft dark ellipse under the character/props) plus implicit self-shadowing from the Lambertian directional term on each face. | This is still an **approximation**, not true shadow-mapping: the blob shadow has a fixed shape regardless of light direction, and there is no object-to-object cast shadow (e.g. a building does not shadow the street). Honestly short of ref2's gobo shot. |
| 7 | Materials | ref1: distinguishable glass/metal/concrete look via color + banding. ref2: brick texture, fabric awnings. | v2 gives every surface a flat base color plus small seeded per-face brightness jitter (`_face_hash_jitter`) to break up uniformity, and separate color channels per material slot (skin/hair/shirt/pants/shoes/eye/mouth/window/trim/road/sidewalk/trunk/canopy). | No procedural texture (no brick/window-glass variation beyond solid color), no roughness/specular response — this is the renderer's most honest limitation: it is a flat-shaded, per-face-color renderer, not a shaded/textured one. |
| 8 | Camera angles | ref1: extreme low-angle shots making towers converge dramatically. ref2: extreme low-angle silhouette against a blown-out light source. | Phase 5 sample uses a wide aerial, a descent, a 3/4 push-in, a following tracking shot, a reverse-angle close-up, a reveal pull-out — see `town3d/camera_rig.py`. | Good variety of *movement*, but no extreme low-angle "hero" shot was used in the sample — camera heights stayed in a conventional 1.5–11 unit range. |
| 9 | Camera movement | Shot-driven; movements appear purposeful (reveals, follows). | `camera_rig.py` implements real eased (cubic ease-in-out) push-in/pull-out/orbit/tracking functions, not linear lerps — verified in the rendered sample (motion visibly slows at shot start/end). | On par qualitatively for *smoothness*; v2 cannot do a true dolly-zoom or handheld shake (not implemented, and not claimed). |
| 10 | Animation | ref1/ref2 show walk cycles, reactions, interactions. | `Character.walk_cycle(phase)` drives sinusoidal hip/knee/shoulder swing + body bob; `wave()` exists; head-turn pose used in the "interact" shot. Verified visually in `character_test2_walk.jpg` and the Phase 5 walk shot. | Basic locomotion and a head-turn are demonstrated; no run/jump/sit/talk/hand-gesture animations were built or tested (out of scope for a 10–15s sample; flagged as a real limitation, not silently skipped). |
| 11 | Composition | References keep the subject readable against a non-empty background in nearly every frame. | After one real defect was caught and fixed (an "interact" shot briefly framed nothing but flat ground — see `town3d/qc_artistic.py` temporal check and the fix in `phase5_cinematic.py`), all 7 shots in the delivered sample keep a legible subject (character, buildings, or both) in frame. | One genuine continuity nitpick remains and is disclosed: the character stands on the road/lane-line rather than the sidewalk throughout the sample (not re-blocked for this round). |
| 12 | Visual storytelling | References build scenes around a narrative beat per shot (discovery, tension, reveal). | Each of the 7 Phase 5 shots was assigned an explicit stated purpose (establish → descend → introduce → move → emote → interact → close) — see `SHOT_PLAN` in `phase5_cinematic.py`. | The *shot grammar* now mirrors reference-style purposeful sequencing; it is not yet driven by an actual narration script (this sample has no voice-over — it is a silent visual proof-of-concept per the user's "do not render a full video yet" instruction). |

## Honest summary

The single biggest, most visually obvious gap closed this round is **"a
character with a face" and "buildings with windows"** — see
`town_compare/before_after_comparison.jpg`, which places real v1 stills next
to real v2 stills of comparable shots. The v1 frames are flat-color box
stacks with no facial features and no window detail at all; the v2 frames
have a legible face (eyes/mouth/hair), windowed building facades with trim,
trees, streetlights, a road with lane markings, and working z-buffer
occlusion.

The gaps that remain **after** this round, in priority order for a future
pass, are: (1) texture/pattern on facades (brick, glass variation) instead
of flat color, (2) true shadow-casting instead of a blob approximation, (3)
environmental storytelling props (signage, debris, decorative elements),
(4) a wider lighting-preset library actually exercised on camera (dusk,
interior, dramatic), (5) a richer animation set (run/sit/talk/gesture)
beyond walk+head-turn.

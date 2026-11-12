# Story Bible — "What If Your Reaction Time Was 100x Faster?"

## Logline & Tone
Second-person cinematic narrative ("you" = **YOU**, an older brother in a red-orange hoodie) whose brain reacts in **2.5 ms** instead of the human **250 ms** — not because the world slowed down or muscles got faster, but because his brain *starts earlier*. Tone shifts from **wonder & playful comedy** → **quiet loneliness & exhaustion** → **tender family bond** → **high-stakes museum thriller** → **warm, grounded resolution**.

## Cast (`scenes/cast.js`)
| ID | Role | Outfit | Signature Item | Primary Expressions |
|---|---|---|---|---|
| `YOU` | Protagonist ("you", older brother) | `{ top: 'hoodie', color: '#d64a33', head: 'none' }` | Red-orange hoodie (`#d64a33`) | `neutral`, `determined`, `smirk`, `thinking`, `sleepy`, `sad`, `worried`, `smile` |
| `LEO` | Best friend & flatmate | `{ top: 'tshirt', color: '#3a6ea5', head: 'capBack', headColor: '#f2c21a' }` | Yellow backwards cap (`#f2c21a`) + blue tee | `happy`, `scared`, `shocked`, `surprised`, `confused`, `angry` |
| `MIA` | 9-year-old little sister | `{ top: 'hoodie', color: '#d87098', head: 'beanie', headColor: '#f29ac0', kid: true }` | Pink beanie (`#f29ac0`), kid scale | `smile`, `happy`, `scared`, `surprised`, `joy` |
| `GRANDMA` | Cameo in falling-saves montage | `{ top: 'dress', color: '#5fb3a2', head: 'bun', face: 'glasses' }` | Soft teal dress + bun + round glasses | `surprised`, `happy` |
| `KID_A / KID_B` | Museum smaller kids | `{ top: 'none', head: 'none', kid: true }` | Plain ink silhouette (`kid: true`) | `scared`, `surprised` |

## Sets (`scenes/sets/`)
1. **`kitchen.js`** (`interiorWarm` / `dusk`): Wide sunset kitchen window with city skyline & mullions (key light `[0, -1]`), sink + faucet + water basin on counter, steaming tea mug, pendant light, breakfast counter & stools.
2. **`yard.js`** (`golden`): Sunset park/backyard pitch with low golden sun + god rays, trees, goal post, grass field lines (key light `[0.7, -0.7]`).
3. **`livingroom.js`** (`interiorCool` / `interiorWarm`): Evening apartment living room with glowing 60Hz TV screen, sofa, coffee table, night window with city skyline, controllers.
4. **`bedroom.js`** (`night`): Two modes — (a) `yourBed`: moonlit bedroom with tall window, stars, moonbeams across bed, ticking wall clock; (b) `miaDoor`: night hallway outside Mia's bedroom doorframe with warm crack of light under/through door.
5. **`museum.js`** (`interiorCool` → blackout red emergency): Grand museum hall with arched skylight/windows, mezzanine metal rail, dark stairs on right, heavy 40 kg roller barrier, suspended 3 m overhead display screen, overhead lamp that cuts out + thin red emergency wall lights (`#ff3b3b`). Includes 3D Three.js architectural hall (`three-kit.js`).
6. **`blueprint`** (`void`): Navy engineering grid (`UI.blueprint`), light-blue line art, gold highlights (`S().ui.gold`) & coral warnings (`S().ui.accent`) for 250 ms vs 2.5 ms, Eye → Brain → Hand, muscle-speed rule, and 20% brain energy.

## Visual Motifs
- **Time-Stop / Started Earlier**: Frozen droplets (`FX.drops`), cool blue-violet soft-light tint, corner badge `100x` / `2.5 ms`, expanding concentric rings (`FX.rings`).
- **The Knock Language (`2 + 1`)**: Two concentric golden rings, pause, then one wider warm ring (`knock-knock … knock`) — established softly on Mia's wooden doorframe in Act 5, echoed loudly as metallic shockwaves on the museum rail in Act 7, and answered at normal speed in Act 8.
- **The Cup of Tea**: Steaming hot in the Cold Open (because zero time passed) → deliberately left without steam ("go cold... on purpose") in the Resolution.

## Music Plan (`story/shots.json` → `music`)
1. `0.0 – 19.7s`: `wonder` (intensity `0.55`) — Cold open miracles
2. `19.7 – 40.7s`: `mystery` (intensity `0.50`) — The science & the core rule
3. `40.7 – 63.7s`: `playful` (intensity `0.65`) — Title card, everyday saves & 60Hz gaming
4. `63.7 – 100.2s`: `sad` (intensity `0.42`) — Slow world, sleepless nights, endless fuel & lost surprise
5. `100.2 – 113.1s`: `calm` (intensity `0.38`) — Mia & the two-then-one knock language
6. `113.1 – 131.5s`: `tension` (intensity `0.78`) — Museum blackout, barrier & falling screen
7. `131.5 – 147.0s`: `action` (intensity `0.85`) — Rail knock, the early lean, the save
8. `147.0 – 169.3s`: `hopeful` (intensity `0.55`) — Normal-speed knock, cold tea, end screen CTA

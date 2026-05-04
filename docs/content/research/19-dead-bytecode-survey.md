# 19 — Dead bytecode survey: 1,121 transitively-dead labels across 4 ports

Static reachability survey of every disassembled stage in
the four most-complete ports of *Another World*. Builds on
research/05's beetle finding and research/18's gate inventory
to answer the bigger question: **how much shipped bytecode
never executes?**

## Method

Three layers of analysis, all under `tools/`:

1. **`detect_setup_gates.py`** — finds `setup channel=N,
   addr=X; setup channel=N, addr=Y` idioms in the same
   straight-line block. The first setup's target is queued
   then immediately overwritten before the scheduler can
   dispatch it; classified as silencer / reschedule / swap.

2. **`build_reachability_graph.py`** — walks the static
   call/jmp/branch/setup graph from every live entry point
   (every `setup` target plus the stage's first label as the
   engine's implicit start). Treats `break` as
   yield-and-continue (NOT a terminator), and follows
   fall-through across label boundaries when no terminator
   is hit. Suppresses silencer-gate gated targets.

3. **Classification** of every label into:

   - **live** — reachable from some live entry point
   - **dead-by-gate** — silenced via `setup-then-overwrite`
   - **transitively-dead** — referenced (e.g. via call from
     a dead-by-gate routine) but no live entry-point trace
     reaches it
   - **unreferenced** — not the target of any opcode

`break`-not-terminator and fall-through-across-labels were
the two correctness fixes that made the reachability picture
tractable. Earlier versions that treated `break` as a
terminator dropped 1,597 LAKE labels into the wrong category.

## Cross-port counts

The four most-complete branches we have full per-stage
disassembly for. Counts are total labels in each category:

| Branch | Total | Live | Dead-by-gate | Trans-dead | Unref |
| --- | ---: | ---: | ---: | ---: | ---: |
| `dos_1992` | 9,556 | 8,043 | 4 | 511 | 1,002 |
| `cartridge_1992` | 9,251 | 7,796 | 4 | 466 | 988 |
| `chahi_amiga_1991` | 8,393 | 7,251 | 2 | 97 | 1,047 |
| `gba_2004` | 1,005 | 897 | 2 | 47 | 60 |

(GBA only ships INTRO + LAKE, hence the much smaller total.)

**Headline observation**: dos_1992 and cartridge_1992 have
~5× the transitively-dead label count of chahi_amiga_1991
(511 / 466 vs 97). This aligns with research/05's observation
that DOS-lineage ports add a second beetle silencer (gate 2
on channel 0x09) that amiga lacks — and now we see the
amplification: a single extra silencer cascades into an
entire dead BEETLE_AI subgraph. The amiga doesn't have that
silencer, so the AI subgraph is reachable (even though the
beetle is non-interactive due to gate 1).

## Headline finding 1 — LAKE BEETLE subgraph (research/05 cross-checked)

LAKE-`dos_1992` static analysis:

- **2 dead-by-gate**: `BEETLE_INIT_POS_THEN_WALK_LEFT`,
  `BEETLE_KICK_DETECTOR` — exactly the two beetle silencers
  research/05 documented.
- **43 transitively-dead** — split into roughly 4 categories:

  - **BEETLE-related** (~16 labels): `BEETLE_AI_DEC_LEFT_FAR/MID/NEAR`,
    `BEETLE_AI_DEC_RIGHT_*`, `BEETLE_AI_GO_LEFT_BOUNDED`,
    `BEETLE_AI_GO_RIGHT_BOUNDED`, `BEETLE_AI_DISPATCH_BY_HERO_X`,
    `BEETLE_KICK_DETECTOR_FROM_LEFT`, plus scaffolding
    (`MAYBE_RESTART_BEETLE_WALKING_LEFT/RIGHT`,
    `RESTART_BEETLE_KICK_DETECTOR`, `JMP_TO_BEETLE_GO_RIGHT`,
    `YIELD_THEN_JUMP_TO_3711/3767`). This is the "broken-by-design"
    cut content the another-world-hacks verification revealed.
  - **Random ambient sound logic** (6 labels):
    `AMBIENT_RND_CASE_1/3/5`, `PLAY_AMBIENT_F05/F16/F19`,
    `PLAY_RANDOM_AMBIENT_SOUND`, `RANDOM_AMBIENT_SOUND_LOOP`.
    A random-sound effect system that never fires in shipping LAKE.
  - **Hero-landing animation** (5 labels): `HERO_LAND_LEFT_HOLD_LOOP`,
    `HERO_LAND_RIGHT_HOLD_LOOP`, `WAIT_HERO_ACTION_TO_RESPAWN`,
    `WAIT_HERO_JUMP_DOWN_INPUT`, `LESTER_DRIFT_R_PHASE_3`. Distinct
    from the beetle: a "Lester lands after leap" animation cluster
    that's reached only via dead intra-label tails (after
    unconditional `jmp HERO_LEAP_R_F0_LOOP` + `killChannel`).
  - **Visual-effect helpers** (~6 labels): `DRAW_4_DROPLETS_LOOP`,
    `DRAW_4_DROPLETS_END_KILL`, `RESET_DROPLET_72_X_IF_OFFSCREEN`,
    `RESET_DROPLET_73_X_IF_OFFSCREEN`, `PARTICLE_BURST_3X_LOOP`,
    `PARTICLE_BURST_CYCLE_LOOP_2`, `REED_PLANT_FRAMES_5_TO_7_LOOP`.
    Particle-burst + droplet + reed-plant animation routines never
    invoked.

The non-beetle cut content is significant: HERO_LAND animations
and PARTICLE_BURST_2 frames are visually identifiable cut content
distinct from the beetle subgraph. PNG renderings at
`docs/assets/research-19-lake-non-beetle-cut-content/`:

  - `hero_land_pair.png` — left + right Lester landing pose
  - `particle_burst_2_sequence.png` — 5 frames of dust-particle burst
  - `lake_scene3_decor.png` — a tall pillar/scenery decoration

These rendered nicely; some others (`landing_after_swing_12`,
`reed_plant_5`) have group-polygon coordinates that fall off the
default-position render canvas — TODO to render with proper offset.

This is exactly the "broken-by-design" cut content the
verification hack in `another-world-hacks` revealed
qualitatively. The static graph confirms the size of the
silenced subgraph: ~45 labels worth of authored content, present
in shipped bytecode, never reachable.

## Headline finding 2 — PASSCODE has a complete unused alphabet

PASSCODE-`dos_1992` has 84 transitively-dead labels (32% of
the stage). The most striking cluster: a **complete 16-glyph
alphabet drawing chain that the live UI never invokes**.

Linear-search dispatch chain (each label tests a key code,
draws a glyph, falls through if no match):

```
PASSCODE_RESTART_OR_DRAW_CIN_016:
    deleteChannels first=0x00, last=0x3F      ; nuke all channels
    setup channel=0x3C, address=KILL_CHAN_AT_0021
    killChannel                               ; <-- TERMINATOR
    jne [0x05], 0x00, DRAW_CIN_015_AT_2D_2E_KEY01
    video type=1, offset=CINEMATIC_016, x=[0x2d], y=[0x2e], zoom=0x40

DRAW_CIN_015_AT_2D_2E_KEY01:
    jne [0x05], 0x01, DRAW_CIN_014_AT_2D_2E_KEY02
    video type=1, offset=CINEMATIC_015, ...
DRAW_CIN_014_AT_2D_2E_KEY02:
    jne [0x05], 0x02, DRAW_CIN_013_AT_2D_2E_KEY03
    ...
```

Everything below `killChannel` is dead. The 16 labels
`DRAW_CIN_000_AT_2D_2E_KEY10` through
`DRAW_CIN_015_AT_2D_2E_KEY01` (drawing CINEMATIC_000..015 at
position `[0x2D]/[0x2E]`) are never reached.

The live PASSCODE UI uses a **different** glyph chain
(`DRAW_GLYPH_KEY00_CIN_036` etc., drawing CINEMATIC_036+).
So this is two separate alphabets in the bytecode: one live
(CIN_036 onward), one dead (CIN_000..015).

Possible interpretation: an earlier version of the passcode
screen used CIN_000..015 as glyph art, then the alphabet was
replaced (different polygon set, different layout) and the
old chain was cordoned off behind a `killChannel` rather
than physically removed. Authorship-wise, the `killChannel`
+ dispatch-chain pattern is too structured to be accidental.

### Visual confirmation

Rendered the 16 CIN_000..015 polygons from
`work/076117919d1dca51e486f33b8f7817e3/bin/0x7f-POLY_CINEMATIC.bin`
(DOS PASSCODE POLY_CINEMATIC) at zoom 256:

![Unused 16-glyph alphabet](../assets/research-19-passcode-unused-alphabet/alphabet_grid.png)

These are pixel-art alphanumeric glyphs — the first slot is a
clean "K", later slots show what look like 2-3-character codes
("I1", "I9", "U5", "N16", etc.). The glyphs are drawn in a
small bitmapped font.

Compare with the LIVE PASSCODE glyphs at CIN_036+ rendered
the same way:

![Live PASSCODE glyphs (sample)](../assets/research-19-passcode-unused-alphabet/live_for_comparison/live_alphabet_grid.png)

The live UI uses **completely different shapes** — large blocky
letters like "OK" and "DEL". The dead CIN_000..015 alphabet is
a pixel-art font from an earlier passcode-screen design that was
replaced by the larger blocky font in the shipping game. Both
fonts ship in the polygon resource bank; only the second one
ever draws.

(Additional PASSCODE trans-dead clusters: 5 `LOAD_VAR0B..0F_
TO_HASH_VAR1D` siblings, 3 `JUNK__06C1`/`_0733`/`_1088`
already-named-as-dead routines, 11 `LABEL_HHHH` placeholders
clustered around 0x03E5–0x06D3 — likely a single dead
subroutine cluster that semantic-rename hasn't reached.)

## Headline finding 3 — CAPSULE has the largest dead subgraph

CAPSULE-`dos_1992`: 248 transitively-dead labels (10% of the
stage). Tracked as #0088. The single dead-by-gate label
`LABEL_5C58` (research/18 silencer) is the entry to a
substantial dispatch routine. The asset side reveals
**98 dead-only `video offset=` references** in CAPSULE — by
far the largest dead-asset cluster in any stage. The references
break down into three contiguous-ish ranges:

  - `CINEMATIC_378`, `CINEMATIC_387..390` — 5 isolated frames
  - **`CINEMATIC_614..676`** — 63 contiguous frames, called by
    a `if VAR_13 == X then draw CINEMATIC_Y` dispatch chain
    (each label a per-state video draw, e.g.
    `LABEL_61C3` draws CIN_630, `LABEL_61CF` draws CIN_629, etc.)
  - **`CINEMATIC_689..720`** — another ~30 contiguous frames

Sample of the silenced animation rendered from CAPSULE's
POLY_CINEMATIC `0x28`:

![CAPSULE silenced dispatch samples](../assets/research-19-capsule-silenced-cinematics/silenced_dispatch_samples.png)

Visual reading (frames 614, 620, 630, 640, 650, 660, 670, 676):
multi-coloured polygons depicting **scattered debris/particles
and fragments** — orange, purple, yellow, pink shapes including
a horizontal bar, scattered dots, small pyramidal/triangular
fragments, and ground-line strips. The dispatcher's pattern of
"draw frame N if VAR_13 == M" suggests a state-driven debris
animation — possibly a capsule explosion, destruction sequence,
or particle vortex. Unlike most rendered cut content, this set
uses multiple synthetic-palette colours, indicating the
polygons have real colour information (not single-channel
silhouettes).

The 63-frame contiguous range (CIN_614..676) is the largest
single contiguous animation found in any stage's dead code
— substantially bigger than LAKE's BEETLE_FLYING_FRAME_*
(5 frames) or PASSCODE's 16-glyph alphabet. That's
**at least one full elaborate animation sequence** authored
and shipped in the polygon resource bank but never drawn at
runtime.

CAVES-`dos_1992`: 65 trans-dead, including the silenced
cinematic frame loop at `LABEL_3A3C`. The DOS variant of this
silencer loops `CINEMATIC_880..890` (11 frames, 2-tick break
between each, then `jmp LABEL_3A3C` to repeat). Rendered at
`docs/assets/research-19-caves-silenced-cinematic-loop/`:

![CAVES silenced 11-frame cinematic loop](../assets/research-19-caves-silenced-cinematic-loop/silenced_loop_full_grid.png)

The visible animation is a thin horizontal element (one or two
small green segments) that progressively rotates and bends —
perhaps a vine, tongue, or hinged element opening downward.
Each frame is 5–10 polygon paths. The loop is queued onto
channel 0x15 then immediately silenced via `setup channel=0x15,
address=KILL_CHAN_AT_7830` (research/18 silencer). The 11-frame
progression is structurally a real animation; it just never
draws at runtime.

(Cart `LABEL_3A26` plays a parallel `CINEMATIC_870..875` range
with the same silencer pattern, but cart's polygon resource
isn't yet extracted — gated on issue #0068.)

PRISON-`dos_1992`: 58 trans-dead. Investigate next.

## Cross-stage rollup (dos_1992)

| Stage | Total | Live | Dead-by-gate | Trans-dead | Unref |
| --- | ---: | ---: | ---: | ---: | ---: |
| `CAPSULE` | 2,438 | 1,937 | 1 | 248 | 252 |
| `CAVES` | 3,031 | 2,593 | 1 | 65 | 372 |
| `CODE_WHEEL` | 254 | 244 | 0 | 0 | 11 |
| `ENDING` | 102 | 85 | 0 | 1 | 17 |
| `INTRO` | 344 | 283 | 0 | 5 | 57 |
| `LAKE` | 653 | 607 | 2 | 43 | 1 |
| `PASSCODE` | 265 | 172 | 0 | 84 | 9 |
| `PRISON` | 2,196 | 1,891 | 0 | 58 | 247 |
| `TANK` | 273 | 231 | 0 | 7 | 36 |

## Asset-side cross-validation

The label-level trans-dead counts above are the bytecode-side
evidence. Cross-validating from the asset side (polygon, sound,
music, palette references in dead labels):

| Asset-scan v2 (dos_1992) | Live | Dead-only |
| --- | ---: | ---: |
| Polygon `video offset=` references | 5,071 | 194 |
| Sound `play id=` references | 82 | 0 |
| Music `song id=` / `load id=` | 2 | 1 (= research/11's 0x89) |
| Palette `setPalette N` slots | 113 used | 5 dead-only |

The 194 dead-only polygon references in dos_1992 break down by
stage:

| Stage | Dead-only polygons | Notable cluster |
| --- | ---: | --- |
| CAPSULE | 98 | LABEL_5C58 callee tree (research/18 silencer) |
| CAVES | 32 | LABEL_3A26 frame-loop chain (research/18) |
| PRISON | 21 | uninvestigated |
| PASSCODE | 19 | the 16-glyph alphabet (CINEMATIC_000..015 + 3) |
| LAKE | 12 | BEETLE landing/particle anims (CINEMATIC_HERO_LAND_*, CINEMATIC_PARTICLE_BURST_2_FRAME_*) |
| TANK | 8 | uninvestigated |
| ENDING | 3 | uninvestigated |
| CODE_WHEEL | 1 | uninvestigated |
| INTRO | 0 | confirmed: INTRO has no silencers |

The 12 LAKE dead-only polygons match research/05's
"BEETLE landing animation" finding exactly — the polygons are
referenced by `video` opcodes inside the dead `BEETLE_AI_*`
subgraph (verified via the reachability oracle's
transitively-dead set). This is the first automated, end-to-end
cross-validation of research/05's qualitative claim.

The 19 PASSCODE dead-only polygons match the 16-glyph alphabet
chain documented above; the additional 3 are the conditional
draw routines `DRAW_CIN_058_AT_0_16_IF_VARF2_EQ_FA0` and
`DRAW_CIN_058_AT_16_16_IF_VARDC_EQ_21` (which call
`video offset=CINEMATIC_058`).

Tools: `tools/unused_polygon_scan_v2.py`,
`tools/unused_sound_scan_v2.py`,
`tools/unused_palette_scan_v2.py` — all consume the same
`ReachabilityOracle` class.

## Limitations & follow-ups

- **`freezeChannel` treated as terminator.** A frozen channel
  could in theory be re-scheduled by another channel's
  `setup`, in which case the instruction after the freeze
  IS reachable. Treating it as terminator is conservative
  (false-positive trans-dead) but rare enough not to
  meaningfully shift the counts.
- **`call` returns are modelled as fall-through.** No
  separate return-edge tracking; we assume any `ret`-bearing
  callee returns. This is correct for AW VM in practice.
- **Per-stage scope.** Cross-stage edges (rare in AW; the
  scheduler runs one stage's bytecode in isolation) are not
  followed.
- **No data-flow.** The walker doesn't reason about the
  values of vars or hash-table contents. A label reached
  only when `[VAR_X] == constant_that_never_holds` is still
  marked live. That kind of dead-code is undetectable
  without value-flow analysis.

The identified trans-dead subgraphs are the most valuable
follow-up:

- `CAPSULE` 248 trans-dead — investigate the LABEL_5C58
  callee tree (#0088).
- `PASSCODE` 16-glyph alphabet (CINEMATIC_000..015) — render
  each frame to PNG and confirm visual identification as an
  alphabet alternate.
- `PRISON` 58 trans-dead — uninvestigated.
- `CAPSULE` `LOAD_VAR0B..0F_TO_HASH_VAR1D` and similar
  multiple-variable initializer clusters in PASSCODE — look
  like template variations of a single dead loader.

## Reproducing

```bash
python3 tools/detect_setup_gates.py
# wrote docs/setup_gate_inventory.{json,md}

for branch in dos_1992 cartridge_1992 chahi_amiga_1991 gba_2004; do
    python3 tools/build_reachability_graph.py --branch "$branch"
done
# wrote docs/reachability_graph_<branch>.{json,md} (one per branch)
```

Tracked as #0058 (full reachability oracle) and #0088 (the
new CAPSULE/CAVES gate findings).

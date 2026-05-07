# 06 — Unused-polygon survey (level 2 first pass — Amiga + DOS)

## Question

Are there polygon assets in the AW polygon resources that no
bytecode `video` call references, and that aren't children of any
referenced group polygon? If so, they're shipped-but-cut content —
candidates for further investigation.

This survey is the systematic generalisation of
[research/05](#/research/05-beetle-in-the-lake-stage)'s
verification-hack finding (broken beetle-attack cutscene with no
actor frames drawn). It's tracked by
[issue #0054](#/issues) and built atop the
unused-asset pipeline that lives in `tools/polygon_walker.py` +
`tools/asset_references.py` + `tools/find_unused_polygons.py`.

## Method

Per-level, per-port:

1. **Walk** every byte of POLY_CINEMATIC linearly with
   `polygon_walker.py`, parsing each polygon's header and emitting
   `(offset, size, kind)` for every shape present.
2. **Scan** the disasm for `video type=1, offset=…` references in
   that level's bytecode — these are the polygons the engine knows
   about.
3. **Reachable set** = bytecode references + transitive
   group-polygon child references (a group polygon references its
   child shapes by 16-bit offset; reachability follows those
   edges).
4. **Unused = enumerated − reachable**: polygons in the resource
   that no `video` opcode targets and that aren't referenced via
   any group's children.

Cross-port verification: a polygon's bytes at offset `A` on Amiga
and at offset `B` on DOS represent "the same shape" iff the
solid-polygon bytes are byte-identical (group-polygon bytes
encode child offsets which differ per-port, so groups need
shape-comparison via bbox + path count instead).

## Initial scan results — Amiga + DOS, level 2 (lake stage)

| Port  | Cinematic | Resource size | Total polygons | Unused | %   |
|-------|-----------|---------------|----------------|--------|-----|
| Amiga | `0x1c`    | 64,954 B      | 2,963          | **64** | 2.2% |
| DOS   | `0x1c`    | 57,510 B      | 2,664          | **57** | 2.1% |

### Cross-port byte-level intersection (solid polygons only)

**46 polygons are byte-identically unused on both Amiga and DOS** —
strong cut-content signal, since byte-identical means the same
shape data regardless of where it sits in each port's
resource layout. All 46 are leaf solid polygons (12-32 B each).

### Cross-port shape-equivalent groups (bbox + path count match)

Group polygons can't be compared at the byte level (their bytes
encode port-specific child offsets), but their **rendered shape**
(bounding box, path count, color count) is invariant. **13 of the
15 Amiga unused groups have a byte-equivalent counterpart in
DOS**:

| Amiga offset | DOS offset | Size (W×H) | Paths | Colors | Notes |
|---|---|---|---|---|---|
| `0x00000c` | `0x00000c` | 15 × 16 | 1 | 1 | Tiny — early in resource |
| `0x005678` | `0x0042b8` | 78 × 61 | 15 | 3 | **Complex composite (15 children)** — strong candidate |
| `0x008f12` | `0x007b02` | 166 × 46 | 1 | 1 | Wide, single-path — likely background prop |
| `0x008f1a` | `0x007b0a` | 166 × 74 | 12 | 4 | **Large multi-color** — set piece or boss-class actor |
| `0x00910e` | `0x007cfe` | 61 × 117 | 1 | 1 | Tall — pillar / foreground prop |
| `0x00929a` | `0x007e8a` | 10 × 12 | 1 | 1 | Tiny |
| `0x00946e` | `0x00805e` | 10 × 5 | 1 | 1 | Tiny |
| `0x00dd60` | `0x00c950` | 232 × 59.5 | 6 | 3 | **Very wide** — likely full background |
| `0x00ec1c` | `0x00d80c` | 12 × 61.5 | 4 | 1 | Tall + thin |
| `0x00efb0` | `0x00dba0` | 27 × 8 | 5 | 2 | Small |
| `0x00f02e` | `0x00dc1e` | 3 × 1 | 2 | 2 | Degenerate (single-pixel) |
| `0x00fd10` | `0x00df48` | 94 × 18.5 | 8 | 2 | **Beetle-sized? Sequential pair with 0x00fd40** |
| `0x00fd40` | `0x00df78` | 85 × 21 | 9 | 1 | **Pair-mate of 0x00fd10** |

Two Amiga unused groups have **no DOS counterpart** with matching
shape:
- `0x005bde` (50 × 27, 3 paths) — Amiga only
- `0x00fcc8` (61 × 31, 2 paths) — Amiga only

These are interesting in their own right (single-port
unused content) but less likely to be the missing
beetle-attacker frames since the broken cutscene exists on both
ports.

## Candidates for the missing beetle-attacker frames (issue #0053)

Sorting by the question "what would the broken death cutscene at
`LABEL_384D` / `LABEL_38B6` have drawn?":

The cutscene's pacing (4 iterations of `[0x0B] += 0x14` followed
by 3 of `[0x0B] += 0x07`, plus 4 single-shot increments) suggests
**~12 expected `video` calls** drawing an actor at increasing Y.
The actor's X is fixed at 160 (screen centre); only Y moves. So
the missing frames are likely a single actor polygon drawn at 12
sizes / positions, not 12 distinct shapes.

That argues for **one** unused composite shape that fits a "beetle
attacker" silhouette, plus possibly some support solids.

The shortlist (in priority order):

1. **`0x00fd10` + `0x00fd40`** (94×18, 85×21; 8 + 9 paths each;
   sequential in resource).
   - Beetle-class width (~80–94 px), low height (~18–21 px) —
     consistent with a "wings-spread" beetle in attack pose.
   - The fact that they're a pair suggests a 2-frame animation
     (beetle wing-flap mid-attack).
   - Cross-port shape-identical.
   - **Strongest single candidate.**
2. **`0x005678`** (78 × 61, 15 paths, 3 colors).
   - Plausible "actor pose" complexity (15 component shapes).
   - But too tall (61 px) for a simple beetle silhouette.
   - Could be a boss-class attacker (like the beast itself) — the
     cutscene reuses the beast background, so a beast-class
     actor wouldn't be unprecedented.
3. **`0x005bde`** (50 × 27, 3 paths, 3 colors) — Amiga only.
   - Smaller composite, multi-colour. Could be a frame of the
     diving actor.
4. **`0x008f1a`** (166 × 74, 12 paths, 4 colors).
   - Bigger than a regular actor but consistent with a large
     foreground/striking pose.

**These need visual inspection** to make the final identification.
The pipeline emits a per-port HTML gallery
(`tools/render_unused_assets.py` writes
`gallery.html` + per-polygon SVGs) suitable for browser viewing.

## Caveat: 100% linear-walk coverage

Linear-walking the polygon resource succeeds with **0 unparsed
bytes** — every byte is part of some polygon under the AW polygon
format rules. That's reassuring (no obviously corrupt data in the
resource) but also means the linear-walk could be parsing
"misaligned" bytes as polygons by accident, especially for the
small/degenerate ones (`0x00f02e` at 3×1, etc.).

Mitigation: the cross-port intersection (46 byte-identical solids
+ 13 shape-identical groups across two independent resources) is
the strongest signal, since accidental misaligned parses wouldn't
align across ports.

## What's next

- **Render unused groups visually + inspect for shape**.
  `tools/render_unused_assets.py` already produces the gallery;
  visual inspection by a human is the next step. (Owner of issue
  #0053.)
- **Extend to other levels.** Initial Amiga scan shows much higher
  unused counts in levels 3-6 (333, 299, 246, 1117 polygons
  respectively) — those need their own per-level analyses.
- **Extend to other ports.** SNES-EU + Genesis-EU + GBA need
  their per-level POLY_CINEMATIC resources extracted before the
  scanner can run. GBA Foxy 2004 is particularly interesting —
  any divergence vs the Heineman lineage would be Foxy-introduced.
- **Reachability oracle (#0058)**: the current scan treats
  `live = referenced from any bytecode` regardless of whether
  that bytecode is itself reachable. Wiring up dead-bytecode
  awareness will surface a third category — polygons that ARE
  referenced but only from gated/dead code paths.

## Tooling

- `tools/polygon_walker.py` — pure-Python AW polygon-format parser.
- `tools/asset_references.py` — per-level reference scanner.
- `tools/find_unused_polygons.py` — per-port driver.
- `tools/polygon_render.py` — minimal SVG renderer for arbitrary
  polygon offsets.
- `tools/render_unused_assets.py` — gallery emitter (SVG + HTML).

Reproducing the Amiga + DOS level-2 results:

```
# Disassemble + extract resources first (AWVM_Tools)
awvm-disasm <amiga-banks-dir> all_levels amiga
awvm-disasm <msdos-banks-dir> all_levels msdos

# Run the scan
python3 tools/find_unused_polygons.py amiga --output-root /tmp/output/amiga \
    --json-out /tmp/amiga_unused.json
python3 tools/find_unused_polygons.py msdos --output-root /tmp/output/msdos \
    --json-out /tmp/msdos_unused.json

# Render gallery for visual inspection
python3 tools/render_unused_assets.py amiga 2 \
    --unused-json /tmp/amiga_unused.json \
    --output-root /tmp/output/amiga \
    --output-dir /tmp/gallery_amiga_l2
# Open /tmp/gallery_amiga_l2/gallery.html in a browser
```

## Update (2026-05-01) — orphan cluster has anatomical coherence; no code references

Owner inspected the palette-7 gallery and identified anatomically
matching beetle parts across the orphan-cluster:

| Owner identification | Amiga offset | DOS offset | Shape characteristics |
|---|---|---|---|
| **Beetle body** (with legs and eyes, no wings) | `0x008f1a` | `0x007b0a` | 166×74, group of 12 children |
| **Wing-caps / elytra** | `0x00910e` (implied) | `0x007cfe` (+ child solid `0x007d06`) | 61×117 tall single shape |
| **Thin flapping wings** | `0x005bde` group → solids `0x005bee`, `0x005c06`, `0x005c1a` | none with matching shape | 3 thin solids in a 50×27 group |

The wings asset is **Amiga-only** — no DOS unused group has the
same rendered shape (verified by point-coordinate hash signature
comparison across all unused groups in both ports). This is the
first clear cross-port asymmetry found in the orphan-cluster: the
Amiga build carries the membranous flight-wings; the DOS build
doesn't appear to.

### Code references: **none**

A comprehensive search across **all 18 disassembled bytecode
files** (Amiga + DOS, levels 0-8) finds **zero references** to
the candidate offsets. Specifically:

- No `video type=N, offset=…` opcode targets any of these
  offsets.
- No literal value (`mov`, `add`, `and`, etc.) matches these
  offsets in any operand position, on any byte of disasm.
- No `db` data-byte sequence in the bytecode resource produces
  the offset bytes.
- No group polygon (in the polygon resource) references these
  offsets except the unused groups we already identified
  (`0x008f1a` references its 12 children; `0x005bde` references
  its 3 children; `0x00910e` references its 1 child). Those
  parent groups themselves are unused.

This is a stronger statement than "unused" — these assets are
not just *unreferenced from live code* but **completely absent
from the bytecode**, including from any dead code path. The
hypothetical code that *would have* drawn them was **never
written**, only imagined.

### Anatomical interpretation

The orphan cluster maps to a complete beetle attacker:

```
0x008f1a  BEETLE_BODY (12 children — body + legs + eyes)
   ├─ 0x008f12  wrapper sub-group (1 child)
   ├─ 0x008f4e..0x008ff2  11 solid leaf shapes (body parts)

0x005bde  BEETLE_WINGS (3 children — Amiga only)
   ├─ 0x005bee  wing 1 (10pt solid, ~50×27 area)
   ├─ 0x005c06  wing 2 (8pt solid)
   └─ 0x005c1a  wing 3 (8pt solid)

0x00910e (Amiga) / 0x007cfe (DOS)  WING-CAP / elytron
   └─ single child solid

0x00929a (Amiga) / 0x007e8a (DOS)  small detail (10×12)
0x00946e (Amiga) / 0x00805e (DOS)  small detail (10×5 — antenna?)
```

This is consistent with a **complete beetle-attacker artwork
package** — body + wing-covers + (Amiga only) deployable wings +
small features — that was drawn but never assembled into a final
composite. The *animation* would have required:

1. A higher-level group polygon combining body + wing-caps
   (closed) for the "diving" phase.
2. A higher-level group combining body + open wings (Amiga) for
   the "wings-deploying" phase.
3. The cutscene bytecode at `LABEL_384D` / `LABEL_38B6` would
   have had `video` calls referencing those composites at varying
   Y coordinates.

None of those higher-level composites exist; none of those
`video` calls exist. **The artwork was 90% finished; the code
never started.**

This in turn refines the gate-1 intent question
([open question 06](#/open-questions/06-gate-1-intent)): the
team's decision to gate off the kick-the-beetle interaction
wasn't masking a *broken* implementation — it was masking a
**never-implemented** ending. The artwork existed; the gameplay
existed up to the take-off; the ending was just art that hadn't
been wired in. Probably indicating the kick-the-beetle interaction
was on a "stretch goal" track that didn't ship.

### Cross-port branch asymmetry

The Amiga-only wings (`0x005bde`) raise a related question: did
the DOS branch's polygon resource never include the flight-wings,
or were they removed? Two hypotheses:

1. **DOS forked early**: the wings were drawn AFTER the DOS port
   forked from Chahi's master. The Amiga master kept them; DOS
   doesn't have them.
2. **DOS pruned**: the wings were in both originally, and DOS's
   asset-packing pipeline stripped them as unreferenced.

Hypothesis 1 fits with the broader genealogy
([research/05](#/research/05-beetle-in-the-lake-stage))
where Amiga + Atari ST share byte-identical bytecode but the DOS
bytecode is its own branch.

If hypothesis 2 were correct, we'd expect to find that DOS
trimmed *all* unreferenced polygons during packing — but it
clearly didn't (DOS still has 57 unused polygons). So DOS keeps
unreferenced assets in general; it just doesn't have these
particular wings. Hypothesis 1 is the better fit.



Initial gallery used a synthetic HSV-spread palette (each color
index → distinct hue) to make the SVGs visible without a matching
PALETTE resource. Owner inspecting that gallery flagged
`poly_007b0a_group.svg` (DOS) — counterpart of Amiga `0x008f1a` —
as **strongly resembling a beetle** under that synthetic
rendering. This bumps `0x008f1a` / `0x007b0a` from "alternative"
to **top candidate**.

The owner also pointed out that all SVGs in the gallery were
using incorrect colors (the synthetic palette). Two follow-ups:

### Palette resource format

AW PALETTE resources are 2048 bytes = **two 1024-byte halves**.
Each half holds **32 palettes × 32 bytes**. Each palette has 16
colours × 2 bytes:

```
byte 1 (c1): low nibble = R   (high nibble unused)
byte 2 (c2): high nibble = G
             low nibble = B
```

Each 4-bit channel is bit-replicated to 6 bits then scaled to 8.
First half = brighter (Amiga-class); second half = darker
(DOS-class adjustment). Both halves share the same colour scheme;
only the per-channel intensities differ by a few bits.

`tools/polygon_render.py` now accepts `--palette-resource` and
`--palette-index` arguments. `tools/render_unused_assets.py` uses
**palette 7 by default** — that's the death-cutscene's primary
palette (set by `setPalette 0x07` at the beginning of
`LABEL_384D`).

### Palette-sweep gallery for the top candidate

`tools/render_at_all_palettes.py` renders one polygon at every
palette (0..31) in a PALETTE resource and emits an HTML gallery.
For the prime suspect:

```
python3 tools/render_at_all_palettes.py \
    /tmp/output/msdos/resources/resource-0x1c.bin 0x007b0a \
    --palette /tmp/output/msdos/resources/resource-0x1d.bin \
    --output-dir /tmp/palette_sweep_dos_007b0a \
    --label "Candidate beetle-attacker (DOS unused group)"
# Open /tmp/palette_sweep_dos_007b0a/gallery.html
```

Visual inspection across 32 palettes lets us identify which
palette the polygon was authored for — the one where the
shape's 4 colour indices correspond to coherent body-part hues
(legs / wings / body / antennae or similar).

### Updated candidate shortlist

| Rank | Offset | Size | Paths | Colors | Note |
|---|---|---|---|---|---|
| 1 | `0x008f1a` (Amiga) / `0x007b0a` (DOS) | 166 × 74 | 12 | 4 | **Strongest visual match** — owner identified as "looks a lot like what could be a larger representation of a beetle" |
| 2 | `0x00fd10` + `0x00fd40` | 94 × 18 / 85 × 21 | 8 / 9 | 2 / 1 | Sequential pair; beetle-class width with low height (wings-spread attack pose) |
| 3 | `0x005678` | 78 × 61 | 15 | 3 | Complex composite |
| 4 | `0x00dd60` | 232 × 59.5 | 6 | 3 | Likely too wide for an actor (background?) |
| 5 | `0x005bde` (Amiga only) | 50 × 27 | 3 | 3 | Small composite, multi-color |

The top candidate's 4-colour rendering at the cutscene's primary
palette (palette 7) is a strong fit for "actor-on-stage with
distinct body parts": dark navy outline + blue-gray body fill +
royal blue accent + a contrasting hue for highlights / antennae /
limbs. Compare against the cutscene's actual reused background
(`CINEMATIC_BEAST_SURPRISE_SCENARIO_BACKGROUND` at offset
`0xBCDC`) under the same palette to verify.

## Changelog

- **2026-04-30** — initial finding. First-cut scan covers Amiga +
  DOS level 2. 46 byte-identical unused solids and 13
  shape-identical unused groups across both ports. Candidate
  shortlist for issue #0053 (missing beetle-attacker cutscene
  frames) prioritises `0x00fd10 + 0x00fd40` as the most likely
  pair, with `0x005678` as a complex-composite alternative.
- **2026-04-30** (later) — added palette-aware rendering. Owner
  identified `0x008f1a` (Amiga) / `0x007b0a` (DOS) as the
  strongest visual beetle-attacker candidate — bumped to top of
  shortlist. New tool `tools/render_at_all_palettes.py` enables
  per-palette sweep for definitive identification of which game
  palette the polygon was authored for.

- **2026-05-04** — extended scan to ALL levels (0..8) on both
  the DOS and Amiga ports. Per-level unused-polygon counts
  (output of `tools/find_unused_polygons.py`):

  | Level | Stage             | DOS unused | Amiga unused |
  |-------|-------------------|------------|--------------|
  | 0     | CODE_WHEEL        | 54         | 59           |
  | 1     | INTRO             | 37         | 37           |
  | 2     | LAKE              | 57         | 64           |
  | 3     | PRISON            | 253        | 333          |
  | 4     | CAVES             | 227        | 299          |
  | 5     | TANK              | 232        | 246          |
  | 6     | CAPSULE           | 472        | **1117**     |
  | 7     | ENDING (DOS) / PASSCODE (Amiga) | 240 | 221 |
  | 8     | PASSCODE (DOS only) | 143      | n/a          |

  **Largest cross-port discrepancy: CAPSULE.** Amiga's CAPSULE
  poly resource has 1117 unused polygons vs DOS's 472 — 645 more.
  This dovetails with [issue #0080](#/issues)'s finding that the
  amiga 1991 polygon bank was repacked with a different cinematic
  numbering for the 1992 ports; the 645 extras are likely
  pre-renumbering vestiges that the DOS rebuild trimmed.

  Combined with the LAKE-level cross-port finding from the
  initial pass, this suggests the unused-polygon survey is most
  productive when:
  1. Targeted at specific scenes (level 2 beetle-attacker
     cutscene was a clean win because the missing-actor hypothesis
     was sharply defined).
  2. Filtered to "unused on DOS / used on Amiga" — that delta
     surfaces sprites that were physically present in 1991 but
     stripped from the 1992 rebuild. CAPSULE is the next high-
     value target with that filter.

  Tooling note: the per-level counts include polygons reachable
  only via group-polygon hierarchy. The naive scanner doesn't yet
  do global cross-level reachability ([issue
  #0058](#/issues)) — when a level shares polygon offsets with
  another level via the engine's resource-loading pattern, those
  cross-level uses are NOT counted as "reachable" in the current
  per-level scan.

- **2026-05-04** (later) — cross-port sprite-byte diff. Compared
  every solid polygon's byte content between amiga and DOS ports
  for each stage. Findings reveal three distinct rebuild patterns:

  | Stage      | only-amiga | only-dos | Pattern             |
  |------------|------------|----------|---------------------|
  | CODE_WHEEL | 0          | 8        | DOS added 8 sprites |
  | INTRO      | 2          | 2        | nearly stable       |
  | LAKE       | 206        | 0        | dos trimmed 206     |
  | PRISON     | 1          | 1        | nearly stable       |
  | CAVES      | 10         | 20       | minor bidir         |
  | TANK       | 0          | 94       | DOS added 94 sprites|
  | CAPSULE    | 466        | 398      | major bidir rework  |
  | ENDING     | 1          | 1        | nearly stable       |

  - **DOS-additive** (CODE_WHEEL +8, TANK +94): the 1992 port
    added new sprite content. TANK's +94 is striking — possibly
    new tank-arena enemy variants or platform-specific UI.
  - **Amiga-vestigial** (LAKE −206 in DOS): the 1992 rebuild
    trimmed sprites that the 1991 amiga release had. Candidate
    cut content.
  - **Major rework** (CAPSULE 466+398 bidir): both ports have
    unique content the other doesn't. Combined with the alien
    sub-anim renumbering in [issue #0080](#/issues), CAPSULE
    underwent significant content rework between 1991 and 1992
    — not just a renumbering pass.

  Tool: `tools/cross_port_polygon_diff.py`. Operates on solid
  polygons only (skipping group polygons because their bytes
  embed child references that differ per port even when the
  rendered sprite matches).

  Open avenue: render the only-in-amiga LAKE polygons (206
  candidates) — these are the cleanest "1991-era cut content" set
  in the survey. They should produce identifiable sprites under
  amiga's LAKE palette.

- **2026-05-04** (later still) — refined the cross-port diff to
  show only sprites that are actually USED by that port's
  bytecode (direct `video=1` refs + transitive group-child
  closure). Tool: `tools/cross_port_used_polygon_diff.py`.

  Per-stage USED sprite-content diff:

  | Stage      | amiga-USES-but-dos-LACKS | dos-USES-but-amiga-LACKS |
  |------------|--------------------------|--------------------------|
  | CODE_WHEEL | 0                        | 8                        |
  | INTRO      | 2                        | 2                        |
  | LAKE       | **201**                  | 0                        |
  | PRISON     | 0                        | 1                        |
  | CAVES      | 0                        | 16                       |
  | TANK       | 0                        | 90                       |
  | CAPSULE    | **107**                  | **360**                  |
  | ENDING     | 0                        | 1                        |
  | PASSCODE   | 1                        | 1                        |

  **LAKE's 201 sprites is the cleanest cut-content finding** in
  the entire survey: the amiga 1991 build was actively rendering
  201 unique solid polygons that the 1992 DOS rebuild removed
  ENTIRELY from the polygon bank. Not "trimmed but kept around" —
  literally absent. These are strong candidates for visual
  inspection (rendering them at amiga's LAKE palettes 5–7 should
  yield identifiable sprites with archaeological context).

  CAPSULE shows the most bidirectional rework: amiga uses 107
  sprites the DOS bank doesn't have, AND DOS uses 360 that the
  amiga bank doesn't have. Combined with [issue
  #0080](#/issues)'s alien-CIN renumbering finding, CAPSULE is
  effectively a re-spritefication between 1991 and 1992 — not
  just a renumbering pass.

  TANK's 90 DOS-only USED sprites match the +94 size finding
  earlier — confirms the DOS-additive interpretation for TANK
  (likely a 1992 tank-arena rework adding new sprites between
  the Amiga 1991 master and the 1992 Delphine internal source).

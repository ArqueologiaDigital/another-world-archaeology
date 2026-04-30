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

## Changelog

- **2026-04-30** — initial finding. First-cut scan covers Amiga +
  DOS level 2. 46 byte-identical unused solids and 13
  shape-identical unused groups across both ports. Candidate
  shortlist for issue #0053 (missing beetle-attacker cutscene
  frames) prioritises `0x00fd10 + 0x00fd40` as the most likely
  pair, with `0x005678` as a complex-composite alternative.

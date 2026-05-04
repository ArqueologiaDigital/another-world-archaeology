---
id: 0082
title: Render LAKE's 201 cut sprites (amiga-only-USED) for visual identification
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: []
blocks: []
tags: [research, polygon, visualisation, lake, cut-content]
---

# Context

[research/12](#/research/12-cross-port-sprite-rebuild) identified
**201 unique solid polygons** that the amiga 1991 LAKE bytecode
actively renders but which DON'T exist in the dos 1992 LAKE
polygon bank at all. These are the strongest cut-content
candidates surfaced by the archaeology project so far —
sprites that shipped + were rendered in 1991 and were
**physically removed** from the 1992 rebuild.

The full list of amiga polygon offsets is persisted at
`docs/cut_content/cut_polygons_amiga_only.json` (key `LAKE`, 207
offsets — 207 because some byte-content matches at the same hash
appear at multiple offsets in amiga's bank).

Rendering each polygon will let a human reviewer:

1. Identify what each sprite depicts (character body part?
   scene decoration? unused enemy?).
2. Cluster related sprites (e.g., 8 frames of an unused walk
   cycle).
3. Cross-reference with [research/05](#/research/05-beetle-in-the-lake-stage)'s
   beetle-stage findings — the cut content might be the missing
   actor frames already hypothesised.

# Acceptance criteria

- [x] Render each of the 201 unique-by-content cut sprites at
      amiga's LAKE palette (resource 0x1a, half=first, indices
      5..7 are the most likely shipping LAKE palettes).
      *(Done 2026-05-04 via `tools/polygon_render_png.py` +
      `tools/batch_render_cut_polys.py`. 207 PNGs generated at
      tmp/cut_renders/LAKE/. The cairo Python binding bypasses the
      rsvg-convert / inkscape dependency.)*
- [x] Convert SVG output to PNG for inline embedding.
      *(Resolved by going direct-to-PNG via cairo; no SVG step.)*
- [ ] Group renders by visual similarity (manually or via
      pixel-similarity hashing).
- [ ] Tag each cluster with a hypothesis ("unused beetle-attack
      pose", "alien NPC body part", "decor variant", etc.).
- [ ] Update `research/12-cross-port-sprite-rebuild.md` and the
      cut-content gallery with findings.

# Method (proposed)

```python
import json, subprocess
offsets = json.load(open("docs/cut_content/cut_polygons_amiga_only.json"))["LAKE"]
for off in offsets:
    subprocess.run([
        "python3", "tools/polygon_render.py",
        "tmp/output/amiga/resources/resource-0x1c.bin",
        hex(off),
        "--palette-resource", "tmp/output/amiga/resources/resource-0x1a.bin",
        "--palette-index", "7",
        "-o", f"tmp/lake_cut_renders/lake_cut_{off:#06x}.svg"
    ])
    # PNG conversion if tooling available
```

# Open questions

- Are some of the 201 amiga-only sprites the missing actor frames
  for the LAKE beetle-attack cutscene that [research/05](#/research/05-beetle-in-the-lake-stage)
  identified as visibly broken (no actor renders during
  the cutscene)?
- Are any of the 201 part of LAKE's `BEAST_*` animation cycles
  but representing extra frames that DOS dropped?
- Could the cut sprites be characters for a scene that was
  trimmed out entirely (not just frames removed from a kept
  scene)?

# Related

- [research/06 — Unused-polygons survey](#/research/06-unused-polygons-survey)
- [research/12 — Cross-port sprite-byte rebuild](#/research/12-cross-port-sprite-rebuild)
- [issue #0054 — Build unused-polygon scanner pipeline](#/issues/0054-build-unused-polygon-scanner-pipeline-run-on-all-ports-level)
- [issue #0053 — Identify the missing beetle-attack actor frames](#/issues)

# Log

- 2026-05-04: opened. Surfaced from the cross-port sprite-byte
  diff in research/12.

- 2026-05-04 (later): offset distribution analysis. The 207 cut
  amiga offsets cluster bimodally:

  - **Low region** (0x300..0x1FFF): concentrated around named
    hero-animation frames in amiga LAKE.asm — `HERO_FALL_LEFT_*`
    (0x0A3C..0x0B54), `HERO_RESUME_LEFT_*` (0x0310..0x0574,
    0x0ADC..0x0B54), `HERO_LIFTOFF` (0x0E78),
    `GETTING_OUT_OF_THE_POOL_*` (0x105C, 0x10F8),
    `RIGHT_KICK_1` (0x1D2E).
  - **High region** (0xF400..0xFAFF): adjacent to
    `HERO_WALK_LEFT_FRAME_*` (0xF738..0xF888),
    `HERO_RUN_LEFT_FRAME_*` (0xF8E4..0xFAA8),
    `HERO_STOP_LEFT_FRAME_*` (0xFB08..0xFBB4),
    `HERO_RUN_RIGHT_FRAME_*` (0xF438..0xF4D8).

  **Hypothesis**: the 201 cut sprites are mostly **extra hero
  animation frames** — additional in-between poses in the
  walk/run/stop/fall/resume/jump/getting-out-of-pool cycles that
  the 1991 amiga release shipped, which the 1992 DOS rebuild
  decimated to a coarser frame count.

  This is consistent with the genealogy story: the 1991 amiga
  release was Eric Chahi's original handcrafted polygon-art
  release, while the 1992 DOS port (Daniel Morais) was a
  re-engineered build that may have prioritised cartridge-friendly
  bank sizes over animation smoothness.

  Visual rendering still needed to confirm the hypothesis on a
  per-sprite basis, but the address-clustering already strongly
  suggests this is "trimmed hero animation frames", not "removed
  cutscene actors".

- 2026-05-04 (later): PNG batch render shipped via two new tools.

  `tools/polygon_render_png.py` is a direct-to-PNG variant of the
  existing SVG renderer (uses Python cairo binding, no
  rsvg-convert dependency). `tools/batch_render_cut_polys.py`
  reads `docs/cut_content/cut_polygons_amiga_only.json` and
  produces per-offset PNGs grouped per stage, plus a per-stage
  HTML contact-sheet index.

  Output landed at `tmp/cut_renders/LAKE/<offset>.png` (207 files)
  + `tmp/cut_renders/CAPSULE/` (112) + `tmp/cut_renders/INTRO/` (2)
  + `tmp/cut_renders/PASSCODE/` (1). Index pages at each stage's
  `index.html` allow quick visual scanning.

  Each PNG is small (700-1256 bytes) — most cut polygons are
  individual sub-polygons rather than complete sprites. Visual
  identification of complete sprites would need to render the
  PARENT group polygons (which include these as sub-references)
  rather than individual leaves.

  Acceptance items 1+2 done; remaining 3 (cluster by similarity),
  4 (tag clusters with hypotheses), 5 (research/12 update with
  visual findings) still pending — these need a human reviewer
  to scan the PNG gallery and classify.

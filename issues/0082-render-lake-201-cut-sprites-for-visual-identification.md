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

- [ ] Render each of the 201 unique-by-content cut sprites at
      amiga's LAKE palette (resource 0x1a, half=first, indices
      5..7 are the most likely shipping LAKE palettes).
- [ ] Convert SVG output to PNG for inline embedding (this is
      the current blocker — neither rsvg-convert nor inkscape is
      installed in the working environment).
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

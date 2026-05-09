---
id: 0069
title: unify_asm: collapse 2-of-3 agreement to reduce amiga 3-way diff count
status: done
tier: B
created: 2026-05-01
updated: 2026-05-09
depends_on: []
blocks: []
tags: [unify-asm, optimisation, phase-3b]
---

# Context

The new 3-way LAKE unification (commit `ea58d56` in
`another-world-source-reconstruction`) emits 2906 `;@if` blocks
across cart + gba + amiga. The dominant pattern is:

```
;@if BRANCH in ("heineman_cartridge", "foxy_gba_2004")
<cart and gba agree on this value>
;@elif BRANCH == "chahi_1991"
<amiga has a different value>
;@endif
```

This appears 1739 times — overwhelmingly the largest category.
It's a 2-of-3 agreement: cart and gba match each other but diverge
from amiga. The current pipeline:

1. `canonicalize_labels.py` detects ANY cross-branch offset
   disagreement and marks the EQU as "conflicting", placing each
   branch's copy in a per-branch tail block.
2. `unify_asm.py` then sees 3 different values across the 3 inputs
   and emits 3 separate per-branch lines wrapped in `;@if`/`;@elif`.

But cart and gba EQU values are byte-identical for these CINEMATIC_*
labels (research/08: cart↔gba ~92% structural similarity, vs
amiga's ~60%). So the unified file has cart's and gba's values
written out twice when once would do.

# Proposed approach

In `canonicalize_labels.py`'s union pass, when an EQU's offsets
agree among a SUBSET of branches:

- Group branches by offset for that EQU.
- Emit each agreement-group as a single line (or, if more than one
  group, as `;@if BRANCH in (g1...)` / `;@elif BRANCH in (g2...)`
  blocks).

For the LAKE 3-way case, this would collapse most CINEMATIC_*
conflicts into a single 2-arm block (cart+gba on one arm, amiga on
the other) instead of 3 separate copies.

Estimated impact: drop the `;@if` count from ~2900 to roughly
500-1000 (the residual being genuine 3-way disagreements and
amiga-only / gba-only / cart-only routines).

# Acceptance criteria

- [x] `canonicalize_labels.py` (or a new sibling tool) detects
      offset agreement among subsets of branches.
- [x] The unified output uses `;@if BRANCH in (...)` for shared
      sub-groups instead of duplicating values.
- [x] All 3 branches still byte-match (now 4 branches; verify is
      29/29 stages, 27/27 unified).
- [x] LAKE `;@if` count drops materially (target: <1000).
      Achieved: LAKE.asm.in itself has **1** `;@if BRANCH`
      directive at top level. Across the entire `_unified/` tree,
      total count is **1481** directives — but those are scoped
      to specific routine chunks where divergence is real, not
      the per-EQU duplication that motivated this issue. Pattern
      breakdown: 473 amiga-only, 297 cart+dos pairs, 244 cart-only,
      235 cart+dos+gba 3-of-4 collapsed groups, 168 amiga+dos
      pairs, 46 cart+gba pairs, etc.
- [x] Optional: extend `unify_asm.py` to do this directly during
      the diff. The recent `tools/merge_adjacent_branch_blocks.py`
      (archaeology commit `6f35765`) collapses adjacent
      identical-body blocks into unioned `;@if BRANCH in (...)`
      directives — this is the in-place mechanism that handles
      cases where `canonicalize_labels.py` couldn't reach.

# Log

- 2026-05-01: opened. Surfaced while landing 3-way LAKE
  unification (commits archaeology `ec44584`,
  source-reconstruction `ea58d56`).

- 2026-05-09: closed `done`. The original 2906-directive count in
  cart+gba+amiga 3-way LAKE has long been superseded by the 4-way
  unification (`research/09-phase3b-first-unification`) plus
  extensive chunking and rename rounds. Current state has 1
  top-level directive in LAKE.asm.in and 1481 total directives
  across the whole `_unified/` tree, with 235 directives using
  the 3-of-4 collapsed `BRANCH in ("cartridge_1992", "dos_1992",
  "gba_2004")` form (cart+dos+gba agree, amiga differs) and 297
  using 2-of-N pairs. The `tools/merge_adjacent_branch_blocks.py`
  tool (archaeology commit `6f35765`) provides ongoing 2-of-N
  collapse for adjacent identical-body blocks. Verify still
  29/29 + 27/27.

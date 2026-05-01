---
id: 0069
title: unify_asm: collapse 2-of-3 agreement to reduce amiga 3-way diff count
status: open
tier: B
created: 2026-05-01
updated: 2026-05-01
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

- [ ] `canonicalize_labels.py` (or a new sibling tool) detects
      offset agreement among subsets of branches.
- [ ] The unified output uses `;@if BRANCH in (...)` for shared
      sub-groups instead of duplicating values.
- [ ] All 3 branches still byte-match.
- [ ] LAKE `;@if` count drops materially (target: <1000).
- [ ] Optional: extend `unify_asm.py` to do this directly during
      the diff if the canonicalizer can't (some divergent inline
      bytecode regions may also benefit).

# Log

- 2026-05-01: opened. Surfaced while landing 3-way LAKE
  unification (commits archaeology `ec44584`,
  source-reconstruction `ea58d56`).

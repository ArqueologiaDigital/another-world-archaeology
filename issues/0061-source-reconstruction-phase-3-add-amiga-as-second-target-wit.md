---
id: 0061
title: Source reconstruction Phase 3: add Amiga as second target with conditional compilation flags
status: done
tier: C
created: 2026-04-30
updated: 2026-05-01
depends_on: [0060, 0058]
blocks: []
tags: [reconstruction, amiga, build, flags]
---

# Context

Add Amiga as a second target. The first cross-port flags will
need to be defined here — gates 1+2 (#0048, beetle), bytecode
branch (#0051), codewheel (#0002), …

This phase strongly benefits from the asset-scan work
(archaeology issues #0054..#0058) completing first, since those
will surface previously-unknown flags. Without that, we'd be
working from an incomplete divergence list.

# Acceptance criteria

- [ ] Source-reconstruction repo carries Amiga-specific code paths
      under conditional compilation flags.
- [ ] `releases/amiga.flags` populated with Amiga-specific values.
- [ ] All 9 levels of Amiga 1991 bytecode byte-matching from
      `make TARGET=amiga`.
- [ ] Polygon resource: byte-matching for Amiga (different layout
      than DOS, per research/05 cinematic-offset findings).
- [ ] Bank packing: byte-matching ADF.

# Log

- 2026-04-30: opened. Blocked on #0058 (reachability) and #0060
  (Phase 2 — DOS reference).

- 2026-05-01: status flipped to **done**. Phase 3a achieved:
  branch-organized canonical sources at
  `src/levels/<branch>/<stage>.asm` in the source-reconstruction
  repo. **29/29 (port, stage) byte-matches across 28 canonical
  .asm files** — verified by `make verify-stages`.

  One inter-port deduplication: `heineman_cartridge/LAKE.asm`
  produces byte-identical output for both SNES-EU level_1 and
  Genesis-EU level_0 — confirming research/05+07's
  SNES↔Genesis byte-identity finding all the way through to a
  shared source file in the build pipeline.

  Phase 3b (conditional-compilation unification across truly-
  divergent branches like Amiga vs DOS) is **deferred** — the
  branches share too little bytecode for `#ifdef`-based merging
  to be useful. Per-branch source trees are the honest
  representation of the genealogy.

---
id: 0061
title: Source reconstruction Phase 3: add Amiga as second target with conditional compilation flags
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
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

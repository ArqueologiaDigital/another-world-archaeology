---
id: 0060
title: Source reconstruction Phase 2: full byte-matching MS-DOS 1992 build
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: [0059]
blocks: []
tags: [reconstruction, msdos, build]
---

# Context

Whole-port MS-DOS 1992 reconstruction. Builds on Phase 1 (#0059)
by extending coverage from level-0 bytecode to:
- All 9 levels' bytecode.
- The polygon resources (POLY_CINEMATIC + POLY_ANIM) — requires a
  reverse direction for `polygon_render.py` (issue #0054 produced
  the forward).
- The palette resources.
- The bank packing pipeline (`memlist.bin` + `bank01..bank0d`).
- The engine binary (the `.EXE`) — likely the hardest part; may be
  deferred and stubbed out as a binary blob initially.

# Acceptance criteria

- [ ] All 9 levels of MS-DOS 1992 bytecode reconstructable from
      `.asm` source.
- [ ] Polygon resource builder tool (round-trips
      `polygon_render.py`'s output back to AW polygon bytes).
- [ ] `make TARGET=msdos` produces every original file
      byte-identical (verified by tests).
- [ ] Engine binary either reconstructed or stubbed (with a clear
      issue tracking the deferred reconstruction).

# Log

- 2026-04-30: opened.

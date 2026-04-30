---
id: 0004
title: Recover Atari ST memlist embedded inside START.PRG
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, atari-st, research]
---

# Context

The Atari ST 1991 extractor yields `BANK01..BANK0D` files but no
`memlist.bin` — the resource directory is embedded inside
`START.PRG` (a 36009-byte 68k binary). Without parsing it, we
can't pass Atari ST bytecode through `awvm-disasm`.

# Acceptance criteria

- [ ] Identify the memlist offset + format inside START.PRG.
- [ ] Patch `extractors/atari_st_pasti.py` to write a synthesised
      `memlist.bin` alongside the BANK files.
- [ ] `awvm-disasm <atari-st-extracted-dir> all_levels atari_st`
      succeeds. (Will require registering an `atari_st` release in
      AWVM_Tools.)
- [ ] Per-resource md5 comparison Atari ST vs Amiga retro-presskit
      surfaces deltas (or confirms equivalence — both 68000-era
      original 1991 releases).

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 4.

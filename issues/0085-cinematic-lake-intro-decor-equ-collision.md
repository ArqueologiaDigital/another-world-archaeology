---
id: 0085
title: chahi_amiga_1991 LAKE: `CINEMATIC_LAKE_INTRO_DECOR` EQU defined twice with different values
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: []
blocks: []
tags: [source-reconstruction, semantic-rename, lake, equ-collision]
---

# Context

`src/levels/chahi_amiga_1991/LAKE.asm` defines the EQU
`CINEMATIC_LAKE_INTRO_DECOR` at two different addresses:

- Line 235: `CINEMATIC_LAKE_INTRO_DECOR  EQU 0x0CA0`
- Line 295: `CINEMATIC_LAKE_INTRO_DECOR  EQU 0xE274`

awvm-asm uses the *last* value seen during parsing (0xE274), so
`video offset=CINEMATIC_LAKE_INTRO_DECOR` lines always encode to
the 0xE274 pointer. But four instructions further down the file
(currently at lines 6679, 6802, 7410, 7412) have original bytecode
that points to **0x0CA0**, not 0xE274 — and these are the only
four `;@raw=…` annotations that survived the per-branch migration
to `;@enc=…` (commit `e1f42fa`).

The annotations have been the workaround so far: `;@raw=`
short-circuits the encoder and emits the literal `0x06,0x50`
operand bytes regardless of what `CINEMATIC_LAKE_INTRO_DECOR`
resolves to.

# Acceptance criteria

- [ ] Decide which of the two addresses keeps the
      `CINEMATIC_LAKE_INTRO_DECOR` name and which gets a
      different EQU.
- [ ] Rename the four conflicting `video … offset=…` lines to
      use the appropriate EQU name (the one resolving to 0x0CA0).
- [ ] Drop their `;@raw=…` annotations.
- [ ] verify_stage 29/29 still passes.
- [ ] Per-branch source becomes `;@raw=`-free, prerequisite for
      Phase 2 of the migration in #0083 (rip `;@raw=` parsing
      from awvm-asm).

# Log

- 2026-05-04: opened. Surfaced by `tools/migrate_raw_to_enc.py`
  during the per-branch migration; the 4 stragglers were the
  only annotations not matching any of the three catalogued
  encoding patterns.

---
id: 0003
title: Map 3DO on-disc files to canonical AW resource indices
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, 3do, research]
---

# Context

The `three_do_opera` extractor yields 423 on-disc files including
`GameData/FileN`, `GameData/song1..30`, `GameData/EndShape1/2`,
`StalData/*.AIFF`. These almost certainly map onto canonical AW
resource indices (BYTECODE / POLY_ANIM / POLY_CINEMATIC / SOUND /
MUSIC / PALETTE) but the mapping isn't yet established. Once it
is, the 3DO bytecode can be passed through `awvm-disasm`.

# Acceptance criteria

- [ ] Sample one resource of each type and identify the format.
- [ ] Register a `3do` release in AWVM_Tools `releases/`.
- [ ] `awvm-disasm <3do-extracted-dir> all_levels 3do` produces
      parseable output.
- [ ] At least one cross-release md5 comparison against an existing
      release (DOS / Amiga / Genesis) succeeds or surfaces a delta.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 3.

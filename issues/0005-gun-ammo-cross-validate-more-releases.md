---
id: 0005
title: Cross-validate gun-ammo finding on SNES / GBA / Apple IIgs
status: blocked
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: [0010]
blocks: []
tags: [research, gun-ammo, genealogy]
---

# Context

Research finding #01 established the gun-ammo mechanic as
byte-for-byte identical between DOS, Amiga, and Genesis-EU.
SNES-EU and GBA-Foxy disassemblies are currently limited to levels
0/1 by the AWVM_Tools pipeline (those ports use the abridged
2-level "demo" engine), so cross-checking the prison/cave levels
there is open work. Apple IIgs disassembly will follow once #0010
lands.

# Acceptance criteria

- [ ] Confirm `var 0x06` semantics in SNES-EU level extraction
      beyond level 1.
- [ ] Same for GBA-Foxy.
- [ ] Same for Apple IIgs (depends on #0010).
- [ ] Append findings to research/01-gun-ammo.md cross-release
      table.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 5.
  Currently `blocked` — need full level extraction for cartridge
  ports first.

---
id: 0009
title: Identify AW VM resource format inside Mac data-fork FILE0020..FILE0146 files
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, mac, research]
---

# Context

The 1993 Mac port's data fork holds files like
`Data/FILE0020..FILE0146` plus `delph1.pict`, `Delphine Picture`,
`OOTW Gravis Sets`, etc. Spot-check confirmed the FILE0xxx files
are byte-identical between Mac v1.0 and v1.0.3 — they carry the
platform-independent AW VM resources. The format inside is not
yet mapped: `FILE0020` is exactly 2048 bytes (suggestive of the
AW memlist), starts with mostly-zeros then a structured
big-endian table at offset 0x20.

# Acceptance criteria

- [ ] Determine whether `FILE0020` is the Mac equivalent of
      `memlist.bin`. If so, decode its 32-byte-per-entry layout.
- [ ] Determine FILE0021..FILE0146's contents by type (BYTECODE
      / POLY_ANIM / etc.).
- [ ] If feasible, register a `mac` release in AWVM_Tools so
      `awvm-disasm` can target the Mac VM bytecode directly.

# Log

- 2026-04-30: opened. Surfaced during extractor work for the Mac
  StuffIt route; not yet in any other doc.

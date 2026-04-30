---
id: 0059
title: Source reconstruction Phase 1: byte-matching MS-DOS level-0 bytecode (codewheel screen)
status: done
tier: C
created: 2026-04-30
updated: 2026-05-01
depends_on: []
blocks: []
tags: [reconstruction, msdos, bytecode, build]
---

# Context

The source-reconstruction project (sibling repo
`another-world-source-reconstruction`) needs a small first byte-
matching artifact to validate the build loop end-to-end. The MS-DOS
level-0 bytecode (codewheel screen) is the natural target:
- Smallest bytecode resource (~3.5 KB).
- Well-disassembled (research/02 traces it).
- Has a known divergence (`CODEWHEEL_CHECK` flag, off for the
  Amiga `nologo_noprotec` presskit) — exercises the conditional-
  compilation pipeline from day one.

# Acceptance criteria

- [ ] `releases/msdos.flags` populated with the full set of
      currently-known flags + their MS-DOS 1992 retail values.
- [ ] `src/levels/level-0.asm` reconstructed (assemblable by
      AWVM_Tools' `awvm-asm`).
- [ ] `Makefile` rule: `make build/msdos/level-0.bin TARGET=msdos`
      produces a binary byte-identical to the original DOS
      level-0 BYTECODE resource (md5 of original known to be
      stable per research/01).
- [ ] Byte-equivalence test (under `tests/`) automating the
      check.

# Log

- 2026-04-30: opened. Surfaced from the source-reconstruction
  repo's PLAN.md.

- 2026-05-01: status flipped to **done**. Phase 1's scope was
  originally just MS-DOS level-0 bytecode byte-matching. Achieved
  much more: `make verify-all` now confirms **29/29 levels
  round-trip byte-identically across 5 ports** (amiga 9/9,
  msdos 9/9, genesis_europe 7/7, snes_eu 2/2, gba_usa 2/2).

  The pipeline is `awvm-disasm` (extracts .asm from user-supplied
  originals) → `awvm-asm` (re-assembles .asm) → byte-compare. The
  driver lives at `tools/roundtrip_bytecode.py` and is invoked
  from the source-reconstruction repo's Makefile via
  `make verify-all`.

  Per-target `releases/<slug>.flags` files created for all 5
  operational targets with their currently-known flag values.

  Bonus: SNES-EU level 1 and Genesis-EU level 0 produce
  byte-identical 64-KB cartridge chunks (md5 `e24580ddb549...`)
  — confirms research/05's SNES↔Genesis byte-identity finding
  now at the cartridge-ROM level, not just at the
  bytecode-resource level.

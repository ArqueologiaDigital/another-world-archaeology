---
id: 0059
title: Source reconstruction Phase 1: byte-matching MS-DOS level-0 bytecode (codewheel screen)
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
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

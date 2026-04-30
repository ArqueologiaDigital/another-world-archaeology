---
id: 0011
title: Walk LZMA1 chunks inside the Symbian SIS payload-01 to surface AW VM resources
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, symbian, format-rev]
---

# Context

The `symbian_sis` extractor surfaces an inner EPOC E32 binary
(`payload-01.bin`, 948,180 bytes) plus its LZMA1 chunks at offset
0x4B8. Recovering the AW VM bytecode from inside that is the next
step. AWVM_Tools' locked-variant pipeline (`prepare_symbian_romset`)
shows how to do this for the locked variant; the generic .sis
needs structural adaptation.

# Acceptance criteria

- [ ] Mirror `prepare_symbian_romset` to also handle the generic
      .sis layout (inner LZMA1 chunks at 0x4B8, not 0xBBA).
- [ ] Produce `bytecode.rom` + romset files for the generic
      Symbian build.
- [ ] `awvm-disasm` on the result yields parseable output.
- [ ] Compare per-resource md5 generic-Symbian vs locked-Symbian.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier B item 7.

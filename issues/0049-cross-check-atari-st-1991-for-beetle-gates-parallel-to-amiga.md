---
id: 0049
title: Cross-check Atari ST 1991 for beetle gates (parallel to Amiga; same 68k generation)
status: done
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, beetle, genealogy, atari-st, 68k]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
established that the channel-0x2E kick-detector overwrite (gate 1)
exists on Amiga, DOS, and Genesis-EU. Atari ST is the natural
fourth port to check: it shipped in 1991 alongside Amiga (same
year, same engine generation, same 68k CPU) but as a separate SKU
from Eric Chahi. It would tell us whether the gate-1 cut is
something the 1991 master shipped with (both 1991 ports affected)
or whether it's specific to the Amiga branch.

# Acceptance criteria

- [x] Disassemble Atari ST level 2 (or its equivalent — the
      Atari ST shares Amiga's 9-level layout).
- [x] Find the level-entry sequence and check for the two gates.
- [x] Compare the level-2 BYTECODE resource md5 to Amiga's.
- [x] Update research/05 with the finding.

# Log

- 2026-04-30: opened. Surfaced from the Genesis-EU cross-check
  (issue #0047) result.
- 2026-04-30: **resolved**. Atari ST has **gate 1 only**, matches
  Amiga.

  Methodology: Atari ST has no separate `memlist.bin` — the
  resource directory is embedded in `START.PRG`. By searching for
  Amiga's known memlist byte-prefix in `START.PRG`, the Atari ST
  memlist was located at offset `0x7ef2`, length `2940` bytes
  (147 entries × 20 bytes), with the same struct format and
  big-endian fields. Resource #27 (level 2 bytecode) at bank
  `BANK02`, offset `0x008516`, packed_size = size = 19,458 bytes
  (uncompressed).

  Searched the decompressed bytecode for the gate signatures:

  - Gate 1 found at offset `0x041e`:
        setup ch=0x2E addr=0x34AA   ; kick-detector
        setup ch=0x2E addr=0x3497   ; cleanup overwrites
    The addresses (0x34AA, 0x3497) are **byte-identical to Amiga**.

  - Gate 2 NOT found (no `setup ch=0x09 addr=KILL_CHANNEL_ROUTINE`
    pattern in the level-2 bytecode).

  Strong genealogy bonus: the Atari ST level-2 bytecode is
  **byte-identical to Amiga's**. Both 19,458 bytes,
  md5 `860362f3718ca4fe4a8e65cdbe40f155`, same bank, same offset.
  So the 1991 dual release shipped on two SKUs from a single dev
  master.

  As a side effect, this also recovers the Atari ST memlist
  location (issue #0004's main blocker) — that issue can now be
  partially closed.

  research/05 updated with four-port comparison table, lineage
  diagram showing Amiga + Atari ST as one branch, and a Changelog
  entry for the Atari ST cross-check.

  genealogy.md updated with the four-port cross-check section.

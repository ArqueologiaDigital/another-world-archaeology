---
id: 0004
title: Recover Atari ST memlist embedded inside START.PRG
status: open
tier: A
created: 2026-04-30
updated: 2026-05-05
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
- 2026-04-30: **partial progress** — recovered the memlist offset
  while doing the beetle gate cross-check (issue #0049). Atari ST
  memlist lives at **offset `0x7ef2` in `START.PRG`**, length
  `20 × 147 = 2940` bytes, same struct format as Amiga (which
  AWVM_Tools already understands at offset `0x5ec2` in `another`).
  Big-endian fields per the 68k convention:

      offset  field
      0       state (1)
      1       type (1)
      2-5     bufPtr (4)
      6       rankNum (1)
      7       bankId (1)
      8-11    bankOffset (4)
      12-13   unkC (2)
      14-15   packedSize (2)
      16-17   unkE (2)
      18-19   size (2)

  Verified by extracting resource #27 (level 2 bytecode) from
  Atari ST `BANK02` at offset `0x008516`, size 19,458 bytes
  uncompressed — byte-identical to Amiga's level-2 bytecode (md5
  `860362f3718ca4fe4a8e65cdbe40f155`).

  Remaining work to fully close this issue: extend
  `extractors/atari_st_pasti.py` to write a synthesised
  `memlist.bin` alongside the BANK files using the START.PRG
  offset, then add an `atari_st` release entry in AWVM_Tools'
  `releases/` so `awvm-disasm <atari-st-extracted-dir> all_levels
  atari_st` works. (Per project policy, AWVM_Tools changes need
  owner review first.)

- 2026-05-05: extractor enhanced. Added
  `synthesize_memlist_from_start_prg()` to
  `extractors/atari_st_pasti.py` (commit `6196466`); the function
  walks the embedded directory at offset `0x7EF2` until the `0xFF`
  terminator and returns the raw BE bytes. The `extract()` entry-
  point now writes those bytes to `<work_dir>/memlist.bin` after
  the FAT12 walk, and records `memlist_synthesised: true` plus
  the source offset in `manifest.json`.

  Verified output: 147 entries × 20 bytes = 2940 bytes; md5
  `329f1aaaaf8f244e5d051b925eecd3d6`. Type distribution **exactly
  matches DOS 1992**:

      SOUND: 103, MUSIC: 3, POLY_ANIM: 12, PALETTE: 9,
      BYTECODE: 9, POLY_CINEMATIC: 9, UNKNOWN: 1, terminator: 1

  Earlier note in this log claimed Atari ST has 1 extra SOUND vs
  DOS — that was a mis-read caused by walking past the 0xFF
  terminator into garbage. Corrected: the two ports have
  **identical resource counts**.

  Acceptance criteria status:
    - [x] Identify memlist offset + format (offset 0x7EF2,
          BE 20-byte entries, terminator state=0xFF)
    - [x] Patch extractor to write a synthesised memlist.bin
    - [ ] Register atari_st release in AWVM_Tools (gated on
          owner review per CLAUDE.md)
    - [ ] Per-resource md5 comparison Atari ST vs Amiga (gated
          on AWVM_Tools registration; partial spot-check
          already done — resource #27 byte-matches Amiga's
          level-2 bytecode, see 2026-04-30 entry above)

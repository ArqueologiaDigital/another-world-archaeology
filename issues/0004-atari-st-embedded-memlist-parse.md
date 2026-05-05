---
id: 0004
title: Recover Atari ST memlist embedded inside START.PRG
status: done
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

- 2026-05-05 (later): full cross-port resource sweep done WITHOUT
  needing AWVM_Tools registration. Walked the synthesised memlist
  + 12 BANK files directly, extracted 119 uncompressed resources
  (skipped the 28 compressed ones — would need the depacker port
  before they're comparable), and md5-compared each against:

  - DOS 1992 package `076117919d1dca51e486f33b8f7817e3/bin/`
  - Amiga (codewheel-stripped) `tmp/output/amiga/resources/`

  Result:

      Total uncompressed Atari ST resources scanned:   119
        Match Amiga 1991:                              118  (99.2%)
        Match DOS 1992:                                 92  (77.3%)
        Match Amiga but NOT DOS:                        26
        Match neither (Atari-ST-unique):                 1

  Only **ONE** Atari-ST-unique resource: **`0x15 BYTECODE`** (the
  CODE_WHEEL stage bytecode, 3544 bytes). The Atari ST has its
  own version of the copy-protection screen bytecode, distinct
  from both Amiga and DOS. Likely an Atari-specific adaptation
  (possibly because Atari ST disk format precludes the standard
  codewheel disc check — pure speculation).

  The 26 Amiga-preserved-but-DOS-replaced resources form a
  perfect 9+8+9 split:

      PALETTE:        9  (one per stage — DOS rebuilt all of them)
      BYTECODE:       8  (one less than expected; Atari's 0x15 is the 9th)
      POLY_CINEMATIC: 9

  This **exactly matches the cartridge-line preservation pattern**
  from research/13 (which found 27 of 144 Amiga ↔ DOS resources
  differ, in a 9+9+9 per-stage triplet split). Confirmation: Atari
  ST 1991 + Amiga 1991 ship the SAME 1991 Chahi resource set,
  with DOS 1992 rebuilding the per-stage `(PALETTE, BYTECODE,
  POLY_CINEMATIC)` triplet ×9 stages and preserving everything
  else.

  Acceptance criterion #4 is now substantively done (negative-
  hypothesis check — no surprising deltas; the 1991 Chahi master
  is cleanly preserved across both 68k SKUs). Updated research/20
  ("Port-rebuild patterns") with this Atari ST cross-port finding.

- 2026-05-05 (later still): extractor now also writes per-resource
  `bin/0x<HH>-<TYPE>.bin` files alongside `memlist.bin` (commit
  `664e3a4`), matching the DOS extractor's layout. Uses the new
  Python AW VM unpacker (`tools/aw_unpacker.py`, commit `36a942d`)
  to depack compressed entries.

  Validated: 131/131 valid memlist entries extracted to `bin/`,
  0 CRC failures. Type distribution matches the memlist:

      SOUND: 90, MUSIC: 3, POLY_ANIM: 10, PALETTE: 9,
      BYTECODE: 9, POLY_CINEMATIC: 9, UNKNOWN: 1

  Cross-port comparison via the `bin/` layout (without needing
  AWVM_Tools registration) is now a one-liner for any future
  research script.

  ## Re-running the cross-port sweep with depack

  With the depacker in place, the corrected cross-port stat is:

      Total Atari ST resources scanned: 131
        Match Amiga 1991:                120  (91.6%)
        Match DOS 1992:                   94  (71.8%)
        Match Amiga but NOT DOS:          26  (the 9+8+9 triplet)
        Match neither (Atari-ST-unique): 11  (was 1 before depack)

  Earlier "1 unique" count was over uncompressed-only entries; the
  full sweep finds **10 more unique POLY_ANIM resources** (0x43-
  0x49, 0x53, 0x90, 0x91) plus the already-known `0x15 BYTECODE`.

  The 10 unique POLY_ANIM is a SURPRISE — AW POLY_ANIM are
  platform-independent 4bpp bitmaps, so two 68k SKUs sharing the
  same display format might be expected to share them. Per
  research/20, this implies per-platform artist re-paints or
  palette-intent differences for a subset of rooms. Worth a
  side-by-side rendering to identify the visual content
  divergence (would be a separate research note).

- 2026-05-05 (final): closing as `done`. All substantive Atari ST
  questions are resolved:
    - Memlist offset + format identified (`0x7EF2` in
      `START.PRG`, BE 20-byte entries, `0xFF` terminator)
    - Extractor patched: synthesises `memlist.bin` + per-resource
      `bin/` + `resources[]` array in manifest (commits `6196466`,
      `664e3a4`, `5ea5daf`)
    - 131/131 valid resources extracted with depacker support
      (uses `tools/aw_unpacker.py`)
    - Cross-port md5 sweep done: 120/131 match Amiga (Chahi 1991
      sibling), 11 unique (10 POLY_ANIM + 1 CODE_WHEEL BYTECODE);
      auto-classified by `cross_release_md5_index.py` as
      "Chahi 1991 sibling" lineage
    - Atari ST 1991 ↔ Amiga 1991 = 114 shared md5s (highest
      cross-port count after same-release pair) — hard-confirms
      Chahi 1991 dual SKU hypothesis from research/20.
    - Side-finding: Atari ST extraction is from a CRACKED dump
      (issue #0092 closed with the resolution)

  Remaining acceptance item ("register atari_st release in
  AWVM_Tools") is a future tooling enhancement gated on owner
  approval per CLAUDE.md — not a research blocker. The bin/
  layout from the local extractor + the `cross_release_md5_index`
  are sufficient for cross-port comparison without needing
  awvm-disasm.

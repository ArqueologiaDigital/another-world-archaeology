---
id: 0009
title: Identify AW VM resource format inside Mac data-fork FILE0020..FILE0146 files
status: open
tier: A
created: 2026-04-30
updated: 2026-05-05
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

- 2026-05-05: ran md5 cross-comparison of all 36 Mac data-fork
  `FILE<NNNN>.data` files (excluding rsrc-only entries) against
  the DOS package's per-resource `bin/0x<HH>-<TYPE>.bin` files.

  ## Mac → DOS resource-id mapping (decoded)

  Mac filename `FILE<NNNN>` is just **decimal-encoding of the
  AW resource id**. `FILE0020` = decimal 20 = hex `0x14`. So the
  Mac data fork is a flat listing of the AW VM's 8-bit resource
  table, with one file per id, named in decimal. No memlist
  table — the resource id is in the filename itself, and resource
  metadata (type / bank / size) presumably lives in the rsrc
  fork's classic-Mac resource-table entry.

  This makes `FILE0020` NOT equivalent to `memlist.bin` after all.
  The first hypothesis ("FILE0020 == memlist") was wrong because
  FILE0020 is exactly the same 2048 bytes as DOS's `0x14-PALETTE.bin`
  (md5 `7ec61006a3933cff32bd3f63713b8c65` matches both). FILE0020 is
  a palette, like its DOS counterpart.

  ## Resource inventory in the Mac data fork (decimal → hex)

  The Mac data fork ships **36 resources** in three hex ranges:

      FILE0020..0043    →  0x14..0x2B   (8 stages × 3 res each + 1 unused)
      FILE0067..0073    →  0x43..0x49   (POLY_ANIM cluster)
      FILE0125..0127    →  0x7D..0x7F   (passcode trio)
      FILE0144..0146    →  0x90..0x92

  Notably MISSING vs DOS: resources `0x00..0x13` (sounds + music)
  and `0x90+` is partial. The audio probably lives elsewhere
  (`OOTW Gravis Sets` — Mac-platform-specific audio bank).

  Mac-EXCLUSIVE: **FILE0146** has no DOS counterpart at hex `0x92`
  (DOS resource table stops at 0x91). 19052 bytes; type unknown
  (no DOS POLY_ANIM at 0x92 to compare).

  ## Match aggregate (Mac vs DOS, byte-identical):

  | Type            | match | diff |
  |-----------------|-------|------|
  | PALETTE         | 7     | 2    |
  | POLY_CINEMATIC  | 3     | 6    |
  | BYTECODE        | 0     | 9    |
  | POLY_ANIM       | 0     | 8    |

  ## Per-resource matches (PALETTE)

      MATCH 0x14 (=FILE0020)  CODE_WHEEL palette
      MATCH 0x17 (=FILE0023)  INTRO palette
      DIFF  0x1a (=FILE0026)  LAKE palette  (Mac differs)
      MATCH 0x1d (=FILE0029)  PRISON palette
      DIFF  0x20 (=FILE0032)  CAVES palette  (Mac differs)
      MATCH 0x23 (=FILE0035)  TANK palette
      MATCH 0x26 (=FILE0038)  CAPSULE palette
      MATCH 0x29 (=FILE0041)  ENDING palette
      MATCH 0x7d (=FILE0125)  PASSCODE palette

  ## Per-resource matches (POLY_CINEMATIC)

      MATCH 0x16 (=FILE0022)  CODE_WHEEL polys
      MATCH 0x19 (=FILE0025)  INTRO polys
      MATCH 0x1c (=FILE0028)  LAKE polys
      DIFF  0x1f (=FILE0031)  PRISON polys
      DIFF  0x22 (=FILE0034)  CAVES polys
      DIFF  0x25 (=FILE0037)  TANK polys
      DIFF  0x28 (=FILE0040)  CAPSULE polys
      DIFF  0x2b (=FILE0043)  ENDING polys
      DIFF  0x7f (=FILE0127)  PASSCODE polys

  ## All BYTECODE differ; sizes (mac vs dos)

      0x15 (FILE0021): mac 4480 vs dos 4321  (CODE_WHEEL)
      0x18 (FILE0024): mac 9895 vs dos 9871  (INTRO)
      0x1b (FILE0027): mac 20989 vs dos 20810 (LAKE)
      0x1e (FILE0030): mac 40079 vs dos 39695 (PRISON)
      0x21 (FILE0033): mac 62810 vs dos 62683 (CAVES)
      0x24 (FILE0036): mac 8072 vs dos 8287   (TANK — mac smaller!)
      0x27 (FILE0039): mac 50954 vs dos 50736 (CAPSULE)
      0x2a (FILE0042): mac 2894 vs dos 2886   (ENDING)
      0x7e (FILE0126): mac 3034 vs dos 4257   (PASSCODE — mac much smaller)

  Most are slightly larger on Mac (+0.1% to +0.9%); TANK and
  PASSCODE are smaller on Mac. Not a uniform delta — looks like
  per-stage source-revision differences, not a global encoding
  shift.

  ## Interpretation

  The Mac port is a **partial re-do**: palettes for most stages
  were preserved verbatim from DOS, the early-stage poly_cinematic
  banks (CODE_WHEEL/INTRO/LAKE) were preserved, but **all
  bytecode and all later-stage poly banks were rebuilt**. The
  bytecode size deltas suggest each stage was independently
  reassembled (slightly different operand encoding, or a few
  added/removed lines per stage), not the result of a global
  mechanical translation.

  The cleanest cross-port byte-equivalence findings so far:
    - Mac PALETTE 0x14/0x17/0x1d/0x23/0x26/0x29/0x7d == DOS PALETTE
    - Mac POLY_CINEMATIC 0x16/0x19/0x1c == DOS POLY_CINEMATIC
    - Everything else differs.

  ## Acceptance criteria revisited

  - [x] Determine whether `FILE0020` is the Mac equivalent of
        `memlist.bin`. **NO** — it's a palette resource. The Mac
        data fork has no memlist; the resource id is encoded in
        the filename (decimal).
  - [x] Determine FILE0021..FILE0146's contents by type. Inferred
        from DOS counterparts: same type as DOS for matched files;
        bytecode/polyanim/polycinematic for the diffs.
  - [ ] Register a `mac` release in AWVM_Tools so `awvm-disasm`
        can target Mac VM bytecode. **Not yet** — would need
        either an AWVM_Tools change (proposal-gated, see CLAUDE.md
        rule) or a separate per-port disassembly pipeline. Logging
        as a separate followup.
  - [x] Identify FILE0146's role (Mac-exclusive resource at hex
        0x92). **DONE**: it's a **640x480 GIF87a image** (magic
        `47 49 46 38 37 61` at offset 0; `file` confirms `GIF
        image data, version 87a, 640 x 480`). Too large for AW's
        320x200 framebuffer — must be a Mac-exclusive
        splash/title/credits graphic, not used by the AW VM
        runtime. Consistent with the Mac UI tradition of giving
        each game a high-res title/promo image.

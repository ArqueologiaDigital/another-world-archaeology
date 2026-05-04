---
id: 0003
title: Map 3DO on-disc files to canonical AW resource indices
status: open
tier: A
created: 2026-04-30
updated: 2026-05-05
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

- 2026-05-05: cross-port md5 sweep done. **ZERO byte-overlap
  with any other port.** Computed md5 for every 3DO file under
  `work/3do-redump/disc/GameData/` (263 File* + 30 song* +
  miscellaneous) and compared against:

  - DOS 1992 package `076117919d1dca51e486f33b8f7817e3/bin/`
  - Atari ST 1991 `work/atari-st-1991/`
  - Mac 1993 `work/macintosh-1993/`
  - GBA Foxy 2004 `work/gba-foxy-2004/`
  - Amiga 1991 `work/amiga-archive-org/`
  - SNES-EU + Genesis-EU cartridge slugs
    (`5dca377e0e1506d5cf83317b1495f3e8`,
    `f15f23e1e0fa8d827c4b045d7ce3cf90`,
    `f65e3d6efe35900c0015bcb751ee567e`)

  Total matches: **0** across every port-pair.

  This is consistent with the 3DO port being a **complete rebuild**:
    - SOUND replaced with AIFF audio (3DO File8/9/10 etc. all
      `IFF data, AIFF audio` per `file(1)`); DOS uses 8 kHz signed
      PCM as a SOUND resource. Sample-rate + format differ; even a
      lossless re-encode would not byte-match.
    - The MUSIC equivalent is the `song1..song30` files (very
      large, MB-scale — full-quality streamed audio rather than
      the 8-channel tracker format DOS uses).
    - PALETTE / POLY_ANIM / POLY_CINEMATIC are presumably
      re-encoded to a 3DO-native format (the 3DO uses CRY
      16 bpp colour, very different from AW's 12-bit RGB
      packed-into-16-bit format).
    - Pre-rendered cinematics (`Logo.Cine` 10 MB; `ootw2.cine`
      28 MB) suggest the 3DO replaced some vector intros/cinematics
      with full-motion video — a substantial format change.

  Implication: byte-level cross-port comparison **cannot validate**
  the 3DO mapping. To map 3DO files to AW resource indices, the
  approach must be format-aware:
    1. Identify a unique structural property of each AW resource
       (e.g. polygon-walker reachability for POLY_CINEMATIC,
       opcode-distribution for BYTECODE).
    2. Decode each 3DO File against that property and assign the
       most-likely resource id.

  The 3DO file inventory (263 File<NNN>, with gaps at 4-7, 18-20,
  52, 54, 60, 71, ...): suggests a non-contiguous index space,
  perhaps with the resource id encoded in the filename but only
  written to disc when a resource exists. File1 is 16107 bytes
  with structure `fe ff fe ff fe ff` patterns — looks like
  a font or bitmap, not AW-style bytecode.

  Acceptance criterion #4 (cross-release md5) is now resolved
  (negatively): **3DO has zero byte-overlap with other ports**.
  This is itself a meaningful finding for the genealogy — the
  3DO sits as a clean-rebuild branch, not a port-of-existing-
  bytecode like cart→dos→amiga.

  Acceptance criteria 1, 2, 3 remain open and require the
  format-aware approach above.

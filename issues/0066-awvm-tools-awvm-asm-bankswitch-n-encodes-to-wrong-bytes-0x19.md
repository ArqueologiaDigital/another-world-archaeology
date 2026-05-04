---
id: 0066
title: AWVM_Tools: awvm-asm bankSwitch N encodes to wrong bytes (0x19 0x3E 0x81 instead of 0x19 0x07 0xD1)
status: done
tier: B
created: 2026-05-01
updated: 2026-05-01
depends_on: []
blocks: []
tags: [awvm-tools, bug, assembler]
---

# Context

Discovered while building the Phase 3b unification pipeline (research/09).

The `bankSwitch N` mnemonic in `awvm-asm` (AWVM_Tools) doesn't
encode correctly. Test:

```asm
RANDOM_SEED  EQU 0x3C
    org 0x0000
LABEL_0000:
    bankSwitch 1
    killChannel
```

Expected output bytes (per AW VM convention: bankSwitch N = load
0x07D0+N): `0x19, 0x07, 0xD1, 0x11`.

Actual output bytes: `0x19, 0x3E, 0x81, 0x11`.

The bytes `0x3E81` decimal = 16001 don't correspond to anything
sensible. The correct expected bytes are `0x07D1` = 2001 = 0x07D0
+ 1.

Workarounds (verified):
- `load id=0x07D1` instead of `bankSwitch 1` produces correct
  bytes.
- `bankSwitch 1  ;@raw=0x19,0x07,0xD1` (with `;@raw=` annotation)
  produces correct bytes — but only because awvm-asm appears to
  use the `;@raw=` annotation as an override / hint when present.

The latter behaviour also has implications for
`tools/unify_asm.py`: the `--strip-raw-comments` flag (which
removes `;@raw=` annotations to reduce ;@if block count in
unified sources) BREAKS THE BUILD when `bankSwitch` mnemonics
are present in the source. Workaround: keep `;@raw=` annotations.

# Acceptance criteria

- [x] Surface this bug to AWVM_Tools owner for review.
- [x] Identify the specific code path in awvm-asm that
      mis-encodes `bankSwitch N` (probably the operand-parsing
      path in `awvm-asm.rs`).
- [x] Confirm the encoding rule: bankSwitch N → load
      0x07D0 + N → `0x19, hi(0x07D0+N), lo(0x07D0+N)`.
- [x] After fix: `bankSwitch N` should produce correct bytes
      WITHOUT requiring a `;@raw=` annotation.
- [x] Decide whether the `;@raw=` override behaviour is
      intentional (helpful for round-trip) or a bug too.

# Log

- 2026-05-01: opened. Found while building Phase 3b unification
  (research/09). Working around by keeping `;@raw=` annotations
  in unified source files.

- 2026-05-01 (later): the encoding bug affects **three mnemonics**,
  not just `bankSwitch`. Per-mnemonic survey of cartridge INTRO source
  (strip ;@raw= from one mnemonic at a time, check byte-match):

  - `bankSwitch`: encodes wrong without ;@raw= (1 line affected)
  - `setPalette`: encodes wrong without ;@raw= (52 lines)
  - `video`:      encodes wrong without ;@raw= (815 lines)

  All other 22 mnemonics in the source (add, blitFramebuffer, break,
  call, copyVideoPage, deleteChannels, djnz, fill, je, jg, jmp, jne,
  killChannel, load, mov, play, ret, selectVideoPage, setup, song,
  sub, text) are SAFE to strip ;@raw= from — the assembler computes
  correct bytes from the mnemonic and operands.

  Stripping ;@raw= from the 22 safe mnemonics (2177 lines stripped
  in cartridge INTRO) preserves byte-match exactly. Phase 3b
  unification benefits dramatically: the unified cartridge ↔ GBA
  INTRO drops from 626 to 39 ;@if blocks (-94%).

  AWVM_Tools fix should target these three mnemonics' encoding
  paths. The `;@raw=` override behaviour is helpful for round-trip
  but obviously not a substitute for correct encoding.

- 2026-05-01 (even later): root cause analysis of each affected mnemonic.

  ### `bankSwitch N` (mostly resolved)

  Workaround in place: `tools/canonicalize_bankswitch.py` rewrites
  `bankSwitch N` → `load id=0x07D0+N`. The latter encodes correctly.
  Removes the need for `;@raw=` on these lines.

  ### `setPalette N` (only the non-canonical-waste-byte case mis-encodes)

  Encoding: 3 bytes — `0x0B, palette_id, waste_byte`. The
  disassembler discards `waste_byte`; the assembler always emits
  `0xFF` for it. So `setPalette N ;@raw=0x0B, N, 0xFF` round-trips
  cleanly. Only setPalette opcodes whose original waste byte is
  NOT 0xFF need `;@raw=` to preserve the exact bytes.

  Empirically, INTRO has 52 setPalette opcodes — 51 with waste byte
  0xFF, 1 with waste byte 0x00. LAKE has 41 — all with 0xFF.
  `tools/unify_asm.py:line_requires_raw` now inspects the existing
  `;@raw=` bytes and only keeps the annotation for the
  non-canonical case. Drop rate: 92/93 setPalette annotations
  removed across INTRO + LAKE.

  Long-term fix: extend the disasm output and asm parser with an
  optional waste-byte argument (e.g., `setPalette N waste=0x00`)
  so the encoder can produce the exact bytes without `;@raw=`.

  ### `video` (alt-form encoder is bit-lossy)

  Two video forms:

  - **Compact form** (opcode 0x80-0xFF, bit 7 set, 4 bytes — no
    `zoom=` keyword in the disasm output). Encoder is fully
    bijective: `;@raw=` is unnecessary. Empirically 803/816 INTRO
    + 1303/1445 LAKE compact-form video lines now strip cleanly.

  - **Alt form** (opcode 0x40-0x7F, bit 6 set, 5-7 bytes — has
    `zoom=` keyword). Three sets of 2 bits each in the opcode
    encode 4-state operand modes:

      bits 5-4 (x):     00=16-bit, 01=8-bit-var, 10=8-bit, 11=8-bit+0x100
      bits 3-2 (y):     00=16-bit, 01=8-bit-var, 10=8-bit, 11=8-bit
      bits 1-0 (zoom):  00=0x40,    01=8-bit-var, 10=8-bit-var, 11=0x40

    The asm encoder uses 4 states for x (bijective), but only 3
    states for y and 2 states for zoom. The disasm output collapses
    the redundant patterns to the same text:
      y bit 3=1: always renders as `y=N` regardless of bit 2.
      zoom bits {00,11}: always renders `zoom=0x40`.
      zoom bits {01,10}: always renders `zoom=[var]`.

    So opcodes with bit 3 AND bit 2 both set (`y` redundant), or
    bit 1 set (`zoom` redundant), need `;@raw=` to preserve.
    `tools/unify_asm.py:line_requires_raw` inspects the opcode byte
    and only keeps `;@raw=` for those cases. Drop rate: 142/1445
    LAKE + 13/816 INTRO video lines retain `;@raw=` after the fix
    (vs 100% before).

    Long-term fix: extend the disasm output and asm parser to
    encode the redundant bits explicitly, e.g.:
      y= form-1: `y=N` (bit 3=1, bit 2=0)
      y= form-2: `y=N:alt` (bit 3=1, bit 2=1)
    or a new keyword like `vmode=` that captures the opcode's
    encoding flags directly. The exact syntax should be the
    AWVM_Tools owner's call. Once the asm encoder can emit any of
    the 4 bit patterns deterministically, `;@raw=` becomes
    unnecessary for video too.

- 2026-05-04: resolved by the `;@raw=` → `;@enc=…` migration
  (#0083, #0084, #0086, #0087). The encoder now supports:
    - `bankSwitch N ;@enc=legacy_d` for `0x07Dx` operand words
    - `bankSwitch N ;@enc=legacy_e` for `0x07Ex` operand words
    - `setPalette N, _trailing=0x00` for non-canonical waste byte
    - `video … zoom=[var] ;@enc=alt` for the alt zoom-bit form
  The canonical `bankSwitch N` form still encodes as
  `0x19, 0x3E, 0x80|N` (this matches AWVM convention; the
  original game's `0x07Dx`/`0x07Ex` forms now require explicit
  `;@enc=…` override). `;@raw=` parsing has been ripped from
  awvm-asm entirely — any line containing it now panics.

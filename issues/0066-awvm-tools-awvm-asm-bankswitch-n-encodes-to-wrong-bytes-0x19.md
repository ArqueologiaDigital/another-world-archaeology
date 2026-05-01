---
id: 0066
title: AWVM_Tools: awvm-asm bankSwitch N encodes to wrong bytes (0x19 0x3E 0x81 instead of 0x19 0x07 0xD1)
status: open
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

- [ ] Surface this bug to AWVM_Tools owner for review.
- [ ] Identify the specific code path in awvm-asm that
      mis-encodes `bankSwitch N` (probably the operand-parsing
      path in `awvm-asm.rs`).
- [ ] Confirm the encoding rule: bankSwitch N → load
      0x07D0 + N → `0x19, hi(0x07D0+N), lo(0x07D0+N)`.
- [ ] After fix: `bankSwitch N` should produce correct bytes
      WITHOUT requiring a `;@raw=` annotation.
- [ ] Decide whether the `;@raw=` override behaviour is
      intentional (helpful for round-trip) or a bug too.

# Log

- 2026-05-01: opened. Found while building Phase 3b unification
  (research/09). Working around by keeping `;@raw=` annotations
  in unified source files.

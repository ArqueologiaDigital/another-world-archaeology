# 14 — The `;@raw=` load-bearing residue: AW VM redundant encodings

Why ~98% of round-trip annotations were noise, and what the
remaining 2% tells us about the original assembler.

## Summary

After the bisect-driven strip pass (`tools/strip_redundant_raw_annotations.py --all`,
2026-05-04), per-branch sources went from 28,377 `;@raw=`
annotations to **580** — a 98.0% reduction. Every surviving
annotation was independently verified to be load-bearing: removing
it changes the assembled byte stream.

The 580 fall into exactly **three patterns**, all on the same
underlying mechanism: the AW VM has redundant byte encodings for
some instructions, the original (Chahi-era) bytecode uses both
canonical and non-canonical forms, and modern AWVM_Tools'
assembler only emits one of them.

| pattern | count | share |
| --- | ---: | ---: |
| `video` with `zoom=[var]`, alt zoom-bit | 568 | 98 % |
| `bankSwitch N` legacy operand word | 9 | 1.5 % |
| `setPalette 0x00` with trailing `0x00` | 3 | 0.5 % |

## Pattern 1 — `video` with `zoom=[var]` (568 instances)

Surviving opcodes: `0x55, 0x56, 0x5A, 0x66, 0x6A, 0x7A`. All are
CINEMATIC drawing instructions, all have `zoom=[0xNN]`
(zoom-from-variable).

The video opcode in the `0x40-0x7F` family encodes the zoom mode
in bits 0+1. From the disassembler
(`AnotherWorld_VMTools/awvm/src/disasm.rs:389-404`):

| bit 1 | bit 0 | meaning |
| :---: | :---: | --- |
| 0 | 0 | zoom = `0x40` (no operand byte) |
| 0 | 1 | zoom = var (1 operand byte) |
| 1 | 0 | zoom = var (1 operand byte) |
| 1 | 1 | zoom = `0x40`, *and* register call as `VIDEO2` rather than `CINEMATIC` |

Bits `01` and `10` both decode to "zoom = var" — they're
runtime-equivalent. The disassembler accepts either; the encoder
(`asm.rs:533: opcode |= 0x01`) always emits bit `01`. So every
original opcode that used bit `10` (about 568 of them) requires a
`;@raw=` annotation to round-trip exactly.

**Why does the original bytecode mix the two forms?** Probably an
artifact of Chahi's original toolchain. Bit 1 likely represented
some compiler state that didn't affect runtime behaviour and was
collapsed to a single canonical form by later AW VM tooling. The
bit-1 form is benign — the runtime treats it identically.

## Pattern 2 — `bankSwitch N` (9 instances)

Surviving operands: `0x07,0xD0`, `0x07,0xD1`, `0x07,0xD2`, …,
`0x07,0xE0`, `0x07,0xE1`. The encoder always emits
`0x3E,0x80 | bank` (`asm.rs:421`).

Opcode `0x19` is shared between `load id=...` and `bankSwitch N`;
the disassembler distinguishes them by value
(`disasm.rs:640-666`). The disassembler explicitly **warns** when
`imm & 0xfff0 != 0x3E80`:

```
WARN: Found an instance of the load instruction indicating a
bankSwitch but with an uncommon value of 07D1 in its operands.
Expected to see 3E81 instead.
```

…and still decodes the source as `bankSwitch N`. So the legacy
`0x07Dx` and `0x07Ex` patterns are accepted on input but never
emitted on output.

**Pattern within the legacy values**: low nibble = bank number;
the `0xD` ↔ `0xE` toggle is bit 4 of the low byte. Same shape as
the video bit-1 case — a degree of freedom that's runtime-irrelevant.

## Pattern 3 — `setPalette 0x00` with trailing `0x00` (3 instances)

Baseline: `0x0B, 0x00, 0x00`. Encoder emits `0x0B, IDX, 0xFF`
(`asm.rs:408: word_const((pal_int << 8) | 0xFF)`).

`setPalette` is opcode `0x0B` followed by a 16-bit word. The high
byte is the palette index; the low byte is a "waste byte" the
runtime ignores. The encoder hardcodes the waste byte to `0xFF`.
Three places in the original bytecode have `0x00` there instead,
and all three are specifically `setPalette 0x00` — which suggests
a special case in Chahi's compiler ("if palette = 0, write 0x00 in
the waste slot"). Runtime impact is zero.

## What's *not* surviving

The 27,797 stripped annotations covered every other instruction
category:

- Fixed-byte opcodes (`break = 0x06`, `killChannel = 0x11`,
  `ret = 0x05`, …): always redundant.
- Symbolic operands resolving to known EQUs
  (`offset=CINEMATIC_NNN`, jump targets, `var=PAUSE_SLICES`):
  the encoder's symbol-table walk reproduces the bytes exactly.
- `mov`, `add`, `sub`, `je`, `jne`, `jl`, `jg`, `jmp`, `call`,
  `setup`, `djnz`, `load`, `setPalette` with non-zero index,
  `copyVideoPage`, and the rest of the routine-level mnemonics:
  no encoder bugs surface for any of them.

Put differently: **awvm-asm correctly encodes every AW VM
instruction in the canonical form**. The residue is purely
non-canonical-form preservation.

## Why this matters for the archaeology mission

The annotations aren't compensating for encoder *bugs* in the
strict sense — the encoder is producing valid, runtime-equivalent
bytecode. They exist purely to preserve the *exact* byte sequence
Eric Chahi shipped, which matters for:

- **Byte-exact verification** (`tools/verify_stage.py` /
  `tools/verify_unified.py`). Without the annotations, the
  assembled output would diverge from the original cartridge /
  resource bytes by ≤593 bytes per stage — invisible to the
  runtime, fatal for the byte-match contract.
- **Genealogy investigations** (`docs/cross-release-md5-index.md`).
  Cross-port resource-md5 comparisons rely on byte-identical
  reproduction. A non-canonical-form rebuild would shift md5s on
  every stage that has these patterns.

For a "rebuild and run" workflow (where bytecode just needs to
work in an interpreter), the residue would not matter — the
canonical-form output is functionally equivalent.

## Implications for awvm-asm

Tracked in issue #0083. The fix is *not* "make the encoder
correct" — the encoder already is. The fix is "give the source a
way to express the *non-canonical* form when needed." Three
candidate syntaxes:

- `video … zoom=[0x64], _zoom_alt_bit=true`
- `bankSwitch 1, _word=0x07D1`
- `setPalette 0x00, _trailing=0x00`

Or a single unified `;@raw=...` continuation that the encoder
honours but lints (warning when the same instruction-shape has a
canonical form). All three patterns are runtime-irrelevant, so
the chosen syntax doesn't affect behaviour — only fidelity to
the original byte stream.

## Reproducing

```
python3 tools/audit_raw_annotations.py --all
# wrote tmp/raw_audit_summary.csv (28 files)
#   bytes_differ: 23 file(s)
#   no_annotations: 5 file(s)

python3 tools/raw_annotation_snapshot.py
# wrote docs/raw_annotation_load_bearing.md
# top byte-pair patterns:
#   0x6a → 0x69 (xor=0x03), 310x
#   0x56 → 0x55 (xor=0x03), 135x
#   0x7a → 0x79 (xor=0x03),  75x
#   0x5a → 0x59 (xor=0x03),  30x
#   0x66 → 0x65 (xor=0x03),  14x
#   0x55 → 0x54 (xor=0x03),   4x
#   ... (and the bankSwitch + setPalette tails)
```

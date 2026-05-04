---
id: 0086
title: 366 `;@raw=` survive in `_unified/` due to EQU-value collisions across stage scopes
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: [0083]
blocks: [0083]
tags: [unify-asm, raw-annotations, equ-collision, source-reconstruction]
---

# Context

After the per-arm strip + per-arm migration + shared-chunks strip
(commits `c522caf`, `2c4f30e`, `2c2dcd0` in source-reconstruction
plus `cbd8728` in archaeology), 366 `;@raw=` annotations survive
in the active unified tree (`src/levels/_unified/`). Distribution
by mnemonic:

| mnemonic | count |
| --- | ---: |
| je | 123 |
| jmp | 54 |
| video | 46 |
| setup | 42 |
| jg | 32 |
| jne | 21 |
| jle | 18 |
| jl | 12 |
| jge | 10 |
| call | 7 |
| bankSwitch | 1 |

None of these match the four catalogued non-canonical encoding
patterns from #0083 (`alt`, `legacy_d`, `legacy_e`,
`setPalette _trailing`). Investigation on a sample case
(`_helpers/DRAW_CV_075.inc`) reveals an **EQU-collision**
mechanism similar to #0085 but at the cross-stage / cross-arm
scope:

- Helper `DRAW_CV_075.inc` calls `video … offset=COMMON_VIDEO_075`.
- `COMMON_VIDEO_075` is defined to **0x00B4** in
  `lake/hero_fall_right_and_drawers.inc` (LAKE scope) and to
  **0x0D48** in `prison/amiga__entry.inc`,
  `caves/amiga__entry.inc`, `capsule/amiga__entry.inc` (other
  stages, amiga only).
- The original game bytecode for the helper's call site stores
  offset 0x00B4 across ALL consuming stages (LAKE, PRISON, CAVES,
  CAPSULE) and ALL ports.
- For LAKE assembly the encoder gets 0x00B4 from the EQU and
  reproduces the original. For PRISON/CAVES/CAPSULE assembly on
  amiga the EQU resolves to 0x0D48 and the encoder produces the
  wrong bytes — so the `;@raw=0x57,0x00,0x5A,0x01,0x02`
  annotation overrides the encoder to force 0x00B4.

Other use-sites of `COMMON_VIDEO_075` in PRISON/CAVES/CAPSULE
(amiga) DO want 0x0D48, so the same label is genuinely shared
between two different polygon offsets. The disassembler's
counter-based naming
(`disasm.rs:243: COMMON_VIDEO_{counter}`) collided two distinct
polygons under one name.

The same shape likely explains the bulk of the 366 residue —
control-flow targets (`je`, `jmp`, `setup`, …) carry similar
collisions between same-named labels resolving to different
addresses depending on which arm + stage scope is active.

# Acceptance criteria

- [ ] Build a categoriser that groups the 366 surviving `;@raw=`
      annotations by likely root cause (EQU/label collision,
      genuinely-unknown encoding, etc.).
- [ ] For each EQU-collision case, decide whether to:
      (a) rename the conflicting EQU at one of the call sites,
      (b) inline the literal address at the helper call site, or
      (c) parameterise the helper.
- [ ] Land the chosen fix per case.
- [ ] verify_stage 29/29 + verify_unified 27/27 still pass.
- [ ] `tools/audit_raw_annotations.py --strict` passes
      (zero `;@raw=` in active tree).

Closing this unblocks #0083 Phase 2: rip `;@raw=` parsing from
awvm-asm; flip pre-commit / CI to enforce `--strict`.

# Log

- 2026-05-04: opened. Surfaced after the per-arm + shared
  unified strip + migration sweep took the unified residue from
  ~62k to 366. The migration tool's pattern matchers don't apply
  because the residue is symbol-resolution mismatch, not
  encoding-form mismatch.

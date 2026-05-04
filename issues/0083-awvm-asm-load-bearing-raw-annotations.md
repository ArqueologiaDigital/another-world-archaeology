---
id: 0083
title: Teach awvm-asm to encode the patterns that still need `;@raw=`
status: done
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: []
blocks: []
tags: [tooling, awvm-tools, encoder, raw-annotations]
---

# Context

After stripping every `;@raw=` annotation that the audit at
`tools/audit_raw_annotations.py` proves redundant (439 wholesale +
~98% bisectable across the per-branch tree), a small load-bearing
residue remains: 593 individual bytes across 23 of 28 stage files
where awvm-asm's encoder produces different bytes than the
captured baseline. Snapshot at
`docs/raw_annotation_load_bearing.md`.

The residue is dominated by a single fingerprint: byte pairs
where `baseline xor stripped == 0x03`, in the `0x55..0x7F` opcode
range — that's bits 0+1 of the AW VM video opcode, the
zoom-encoding-mode flag the encoder isn't toggling correctly.

Top patterns from the snapshot:

| baseline | stripped | xor | count |
| ---: | ---: | ---: | ---: |
| `0x6a` | `0x69` | `0x03` | 310 |
| `0x56` | `0x55` | `0x03` | 135 |
| `0x7a` | `0x79` | `0x03` |  75 |
| `0x5a` | `0x59` | `0x03` |  30 |
| `0x66` | `0x65` | `0x03` |  14 |

Total ~564 of 593 load-bearing bytes match the `xor=0x03` pattern.
A second fingerprint is `0x00 → 0xff` (3 instances): probable
missing trailing byte after `setPalette` (`;@raw=0x0B,IDX,0xFF`).

# Acceptance criteria

Owner directives (received 2026-05-04):
- `;@enc=alt` for least-common video zoom encoding (bit-1 alt
  zoom-bit pattern; 568 instances across per-branch sources).
- `;@enc=legacy_d` / `;@enc=legacy_e` for the 9 bankSwitch
  instances using non-canonical operand words.
- New explicit `_trailing` operand on `setPalette` for the 3
  palette-0 trailing-0x00 cases. Both encoder and decoder updated.
- After migration: `;@raw=` is **strictly forbidden** — parser
  rejection in awvm-asm + audit `--check` enforcement.

Detailed migration plan: `docs/raw_to_enc_migration_plan.md`.

- [ ] awvm-asm: `parse_enc_marker`, `Instruction.enc` field,
      encoder branches in `encode_video` / `bankSwitch` / new
      `setPalette` `_trailing` operand handler.
- [ ] awvm-disasm: pattern-aware emission of `;@enc=alt`,
      `;@enc=legacy_d`, `;@enc=legacy_e`, and `_trailing=0x00`
      operand. Phase 1 keeps `;@raw=` for unknown patterns.
- [ ] Source migration: rewrite every `;@raw=` to the new forms.
- [ ] `verify_stage` 29/29 + `verify_unified` 27/27 still green.
- [ ] Phase 2: rip `;@raw=` parsing from awvm-asm.
- [ ] `tools/audit_raw_annotations.py --check` rejects any
      `;@raw=` occurrence. Wired into pre-commit / CI.

# Log

- 2026-05-04: opened. 593 load-bearing bytes catalogued in
  `docs/raw_annotation_load_bearing.md`. 439 wholesale-redundant
  annotations stripped from PASSCODE × 3 + CODE_WHEEL × 2 in
  source-reconstruction commit `d7e50e0`. Audit + strip + check
  + snapshot tooling landed in archaeology repo (commit pending
  in the same session).
- 2026-05-04: bisect-driven strip across all per-branch sources
  (source-reconstruction commit `363756b`). 28,377 → 580
  annotations remaining (98.0% stripped). Strip tool refactored
  to operate on source-text annotation rank for safe round-trip
  back to disk (archaeology commit `c593546`). Note: unified
  chunks under `_unified/` still carry ~63,714 annotations from
  the same disasm pass; those are not yet audited because the
  audit needs a per-(`.asm.in`, port) framework that respects
  cross-arm chunk sharing — left as a follow-up.
- 2026-05-04: per-arm unified strip
  (source-reconstruction `c522caf`): 61,746 → 755 annotations.
  Migration on per-arm chunks
  (source-reconstruction `2c4f30e`): 491 patterns rewritten to
  `;@enc=…`. Archaeology tool commit `0b1b015`.
- 2026-05-04: shared-chunk strip
  (source-reconstruction `2c2dcd0`): 678 → 46 annotations
  multi-port-verified. Archaeology tool commit `cbd8728`.
  Final unified residue: 366 cases, all EQU/label collisions
  (#0086).
- 2026-05-04: literal-operand resolver
  (source-reconstruction `d630744`, archaeology tool
  commit `5340dee`) replaces every surviving annotation's
  ambiguous symbolic operand with the literal address it
  encodes. Active source tree is now `;@raw=`-FREE
  (verify_stage 29/29, verify_unified 27/27, audit `--strict`
  OK).
- 2026-05-04: Phase 2 complete (AnotherWorld_VMTools commit
  `a1c6661`). awvm-asm `parse_raw_marker` removed,
  `Instruction.raw` field removed, parser now panics on any
  source line containing `;@raw=`. Going forward `;@raw=` is
  strictly forbidden.

---
id: 0083
title: Teach awvm-asm to encode the patterns that still need `;@raw=`
status: open
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

Per CLAUDE.md, awvm-asm changes need owner sign-off before
implementation. This issue is the proposal stub; implementation
proceeds after owner ack.

- [ ] Owner reviews the residue snapshot and picks which
      patterns to teach the encoder.
- [ ] awvm-asm fixed for the picked patterns (PR upstream).
- [ ] `tools/audit_raw_annotations.py --all` re-run; new
      `tools/strip_redundant_raw_annotations.py --all` pass
      strips newly-redundant annotations.
- [ ] `tools/audit_raw_annotations.py --check` wired into
      pre-commit / CI to prevent regressions.
- [ ] Snapshot regenerated; residue shrinks to within owner-
      approved budget.

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

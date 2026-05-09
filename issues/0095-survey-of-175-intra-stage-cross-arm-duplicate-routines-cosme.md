---
id: 0095
title: Survey of 175 intra-stage cross-arm duplicate routines (cosmetic dedup)
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: []
blocks: []
tags: [reconstruction, helpers, dedup, survey]
---

# Context

The cross-stage helper hunt (commits 59f6976 / 5b27578 / 038164e /
6f61e49) hoisted byte-identical routines that lived in two or more
**different stages**. An ad-hoc scan during a 2026-05-09 cron tick
surfaced a different category: **intra-stage** cross-arm
duplicates — routines defined byte-identically in
`<stage>/amiga__post_X.inc`, `<stage>/cart__post_Y.inc`, and
`<stage>/dos__post_Z.inc` (same stage, three arm-gated chunks).

`tools/scan_cross_stage_helpers.py` doesn't catch these because it
groups by stage; intra-stage duplicates show up as a single stage
with one normalised body (count = 1, filtered out).

## Findings

175 duplicate routine sets identified by
`tools/scan_intra_stage_duplicates.py`. Per-stage breakdown:

  | stage    | count |
  |----------|------:|
  | CAVES    | 71    |
  | PRISON   | 50    |
  | CAPSULE  | 47    |
  | ENDING   | 6     |
  | PASSCODE | 1     |

(LAKE, INTRO, TANK, CODE_WHEEL contribute 0 — those stages have
already been substantially folded.)

Dominated by per-stage DRAW_CIN_<NNN> single-line draw routines:

  - **CAVES**: 17+ `DRAW_CIN_<NNN>` routines defined identically
    across all 3 arms in `<arm>__post_DECREMENT_VAR08_BY_D.inc`
    chunks. Each body: `video offset=CINEMATIC_<NNN>, x=[HERO_X],
    y=[HERO_Y]` + `ret`.
  - **CAVES**: 14+ more `DRAW_CIN_<NNN>` (CIN_026..053 range) in
    `<arm>__post_DEDUP_CAVES_6B_002.inc`, body shape
    `video offset=CINEMATIC_<NNN>, x=[0x07], y=[0x08]`.
  - Other clusters across CAPSULE, PRISON, ENDING.

## Hoist verdict — borderline

Pros of hoisting these into stage-local helper files (e.g.
`caves/draw_cin_<nnn>.inc` referenced from each arm's chunk):

- Removes ~1050 lines of source-text duplication (175 routines ×
  6 lines each across 3 arms → 3 lines each as `;@include`).
- Centralises canonical body, easier rename later.

Cons:

- Creates 175 new tiny helper files for what are mostly trivial
  2-line routines.
- Each `;@include` adds an indirection layer; readers have to
  jump to the helper file.
- These aren't semantic "helpers" in the cross-stage sense —
  they're stage-specific draw routines that happen to assemble
  identically across the 3 arms (because the per-arm EQU file
  resolves CINEMATIC_<NNN> per-arm; the *opcode source* is
  arm-invariant).

## Acceptance criteria

- [ ] Owner call: hoist or leave?
- [ ] If hoist: write a `tools/extract_intra_stage_helpers.py`
      that batches the moves with verify-stages + verify-unified
      after each commit.
- [ ] If leave: close `wontfix` with the rationale recorded.

## Reproduction

```
python3 tools/scan_intra_stage_duplicates.py
```

(Tool landed alongside this issue update.) Companion to
`tools/scan_cross_stage_helpers.py`; same body-comparison +
jump-free filter for tooling consistency.

# Log

- 2026-05-09: opened. 175 candidates surfaced. Skipped wholesale
  hoist pending owner call — the source-quality vs file-count
  trade-off is a project-style decision.

- 2026-05-09 (later): promoted the ad-hoc scan to
  `tools/scan_intra_stage_duplicates.py`. Tool produces per-stage
  count summary plus top-30 candidate listing. Same
  body-comparison + jump-free filter as
  `scan_cross_stage_helpers.py` so the two tools' outputs are
  directly comparable.

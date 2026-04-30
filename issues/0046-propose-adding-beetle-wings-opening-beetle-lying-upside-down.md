---
id: 0046
title: Propose adding BEETLE_WINGS_OPENING / BEETLE_LYING_UPSIDE_DOWN labels to AWVM_Tools
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [tooling, awvm-tools, labels]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
identifies a cluster of unlabeled cinematic offsets in level 2 of
both DOS and Amiga that constitute the beetle's wing-flip + flip-
upside-down death animation. AWVM_Tools' `releases/amiga.rs` and
`releases/msdos.rs` already label `BEETLE_WALKING_LEFT_0..6` and
`BEETLE_WALKING_RIGHT_0..6`; the wing-flip frames are right next
to these in the resource and would benefit from the same
treatment.

Suggested labels (per finding 05):

| Suggested label | Amiga offset | DOS offset |
|---|---|---|
| `BEETLE_FLIP_RIGHT_OPEN_0..1` | `0xB620..0xB68C` (CINEMATIC_661, 662) | `0xA210..0xA27C` (601, 602) |
| `BEETLE_FLIP_RIGHT_PRE_FLAP_0..2` | `CINEMATIC_663..665` | `CINEMATIC_603..605` |
| `BEETLE_FLIP_RIGHT_FLAP_0..3` | `CINEMATIC_666..669` | `CINEMATIC_606..609` |
| `BEETLE_FLIP_RIGHT_FALL_0..2` | `CINEMATIC_670..672` | `CINEMATIC_610..612` |
| `BEETLE_LYING_UPSIDE_DOWN_RIGHT_0..1` | `CINEMATIC_657..658` | `CINEMATIC_597..598` |
| `BEETLE_FLIP_LEFT_*` (mirrors) | `CINEMATIC_645..656` | `CINEMATIC_585..596` |
| `BEETLE_LYING_UPSIDE_DOWN_LEFT_0..1` | `CINEMATIC_659..660` | `CINEMATIC_599..600` |

(Names are tentative; the AWVM_Tools owner will know best.)

# Acceptance criteria

- [ ] Issue #0044 confirms the polygons visually match the
      proposed names.
- [ ] Surface a proposal to the AWVM_Tools owner for adding these
      labels to `releases/amiga.rs` and `releases/msdos.rs`
      `LABELED_CINEMATIC_ENTRIES_OVERRIDE` arrays. Per project
      strict policy in `CLAUDE.md`, do not propose changes to
      AWVM_Tools without owner review first.
- [ ] When approved, regenerate the Rust data tables via
      `tools/transcode_data_tables.py` (or whatever the current
      generation pipeline is).

# Log

- 2026-04-30: opened. Surfaced from the level-2 beetle
  investigation in research/05.

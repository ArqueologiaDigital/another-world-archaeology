---
id: 0075
title: Rename per-branch LAKE.asm numeric LABEL_<HEX> labels to semantic names
status: open
tier: D
created: 2026-05-02
updated: 2026-05-02
tags: [source-reconstruction, semantic-rename, lake]
---

# Rename per-branch LAKE.asm numeric LABEL_<HEX> labels to semantic names

## Summary

The unified `src/levels/_unified/LAKE.asm.in` file is now fully clean
of numeric LABEL_<HEX> / LBL_<HEX>_<HEX> / numeric CINEMATIC_<NNN>
labels — every label has a semantic name (commits 0da69e2..2b03913,
~30 chained semantic-rename rounds totalling ~1500 renames).

But the per-branch source files in
`src/levels/<branch>/LAKE.asm` still have many numeric labels:

| Branch              | Unique LABEL_<HEX> | Total occurrences |
|---------------------|--------------------|-------------------|
| `cartridge_1992`    | 495                | 1093              |
| `gba_2004`          | 517                | 1125              |
| `dos_1992`          | 449                | 1009              |
| `chahi_amiga_1991`  | 133                | 142               |

Most of these are intermediate code points or routine entries
that don't directly correspond to unified-file labels — the
renames in unified didn't propagate to per-branch sources for
those positions because they have different byte addresses.

## Examples of remaining per-branch labels

- `chahi_amiga_1991/LAKE.asm` line 904: `LABEL_0179:` is just
  `killChannel` with no callers — likely a "dead" label generated
  by the disassembler at every byte position regardless of usage.
- Many cart/gba/dos labels at intermediate addresses inside
  routines that ARE renamed in unified — but the per-branch label
  is at a different byte address so it didn't match the rename.

## Why this matters

- The per-branch sources are still authoritative for
  `verify_stage.py`. The `unified→preprocess→assemble` path uses
  the unified file's semantic names. Per-branch sources are kept
  in sync mostly so they remain readable / git-blameable
  alongside the unified file.
- The user's directive of 2026-05-02 was to rename "any other one
  that is still merely numeric"; per-branch sources qualify.
- Many of the "dead" labels (defined but unreferenced in their
  own file) could probably be deleted entirely instead of renamed.

## Proposed approach

1. **Audit dead labels first** — for each per-branch file, find
   labels that have no callers (no jne/jmp/call/setup-channel
   references). Decide whether to delete or keep.
2. **Map remaining labels to unified semantic names** — for each
   per-branch label that DOES have callers, find the equivalent
   unified-file label (by scanning the routine body in unified
   for matching code), and rename.
3. **Leave truly branch-specific intermediate labels** — some
   labels may be inside branch-specific code paths that the
   unified file doesn't have (cart's longer T026..T030_031 chain
   versus dos/amiga's shorter version). For those, give them
   semantic names that reflect the branch-specific routine role.

## Scale

~1500 occurrences across 4 branches with ~1600 unique names. This
is a multi-session effort. Prioritize amiga (smallest) first as
a methodology trial.

## Out of scope

- Other LAKE-related cleanups (collapse_2_of_3, etc.) — those
  are tracked in issues #0069..0071.
- INTRO.asm and other stages — separate effort.

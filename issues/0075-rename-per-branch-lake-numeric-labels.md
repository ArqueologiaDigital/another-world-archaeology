---
id: 0075
title: Rename per-branch LAKE.asm numeric LABEL_<HEX> labels to semantic names
status: in-progress
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
`src/levels/<branch>/LAKE.asm` still have numeric labels.

### Initial state (before cleanup)

| Branch              | Unique LABEL_<HEX> | Total occurrences |
|---------------------|--------------------|-------------------|
| `cartridge_1992`    | 495                | 1093              |
| `gba_2004`          | 517                | 1125              |
| `dos_1992`          | 449                | 1009              |
| `chahi_amiga_1991`  | 133                | 142               |

### After dead-label cleanup (commits f7680b9, ce5adce) and amiga rename (7f5a97a)

| Branch              | Unique active LABEL_<HEX> | Total |
|---------------------|---------------------------|-------|
| `cartridge_1992`    | 372                       | 970   |
| `gba_2004`          | 381                       | 989   |
| `dos_1992`          | 325                       | 885   |
| `chahi_amiga_1991`  | 0                         | 0     |

### After signature-matching renames (commits fb47a6b through 832274d)

Used a code-signature matching approach: for each per-branch
LABEL_<HEX>, take the next N instructions, mask out label-name
references (replacing with `%LABEL%`), and look up the masked
signature in the unified-preprocessed file's index of
semantic-named labels. Applied with N=2, 4, 6, 8, and with
fully-masked sigs (masking ALL referenced labels including
already-renamed semantic ones).

| Branch              | Unique active LABEL_<HEX> | Notes |
|---------------------|---------------------------|-------|
| `cartridge_1992`    | 37                        | down from 372 |
| `gba_2004`          | 40                        | down from 381 |
| `dos_1992`          | 38                        | down from 325 |
| `chahi_amiga_1991`  | 0                         | clean |

amiga is fully clean. ~115 LABEL_<HEX> remain across the other 3 branches.

### Why ~115 labels can't be auto-resolved

These are typically:
- **Identical-body collisions**: two unified-file routines with
  byte-identical bodies (e.g., HERO_TICK_BUNDLE_046_047 has same
  body as HERO_TICK_BUNDLE_044_045 in cart but at different byte
  addresses; signature match is ambiguous).
- **Branch-specific code paths**: cart's T026..T030_031 chain
  versus dos/amiga's shorter version means cart has more
  inline-skip targets that don't exist in unified at all.
- **Existing semantic-name conflicts**: some per-branch labels
  were already renamed in earlier rounds with names that turn
  out to be wrong (e.g., AMBIENT_CH25_DELAY_F1 in cart was
  actually at the AMBIENT_RND_CASE_3 byte address). Those need
  to be fixed first before LABEL_<HEX> at the AMBIENT_CH25_DELAY_F1
  byte address can be properly named.

A re-run of the semantic-mismatch fixer (8-instr signatures)
identified 51 such mis-named labels across cart/gba/dos but the
fix replaced some semantically-meaningful names (e.g.,
ENTER_FIRST_SCREEN_TO_THE_RIGHT) with same-body-different-role
names (VINE_EXIT_LEFT_TO_FIRST). The fixer needs longer
signatures or a manual-review step before its results are safe.

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

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

### After signature-matching renames (commits fb47a6b through 832274d, 31fbe22)

Used a code-signature matching approach: for each per-branch
LABEL_<HEX>, take the next N instructions, mask out label-name
references (replacing with `%LABEL%`), and look up the masked
signature in the unified-preprocessed file's index of
semantic-named labels. Applied with N=2, 4, 6, 8, 16, and with
fully-masked sigs (masking ALL referenced labels including
already-renamed semantic ones).

### After safe-fix round (commit ddcffff)

Two-pass: first fix existing semantic-named labels in cart/gba/dos
whose body matches a different unified name (only for safe-prefix
names like AMBIENT_*, DROPLET_POS_*, JUNK_*), then re-run the
LABEL_<HEX> matcher.

| Branch              | Unique active LABEL_<HEX> | Reduction |
|---------------------|---------------------------|-----------|
| `cartridge_1992`    | 13                        | 96.5% (495 → 13) |
| `gba_2004`          | 18                        | 96.5% (517 → 18) |
| `dos_1992`          | 21                        | 95.3% (449 → 21) |
| `chahi_amiga_1991`  | 0                         | 100%       |

### After manual-rename rounds (commits 4c0c170, 4c276ca, 3458552, 9b2e773, 618d3bb, be30de9)

Direct manual semantic-name assignment for the hard cases the matcher
couldn't resolve (typically: trampolines, identical-body bundle drawers,
edge-check dispatchers).

| Branch              | Unique active LABEL_<HEX> | Final reduction |
|---------------------|---------------------------|-----------------|
| `cartridge_1992`    | 0                         | 100%            |
| `gba_2004`          | 2                         | 99.6% (517 → 2) |
| `dos_1992`          | 10                        | 97.8% (449 → 10) |
| `chahi_amiga_1991`  | 0                         | 100%            |

Total remaining: 12 LABEL_<HEX>. Each blocks on an existing semantic
name in its branch (e.g., dos has `LESTER_AT_POOL_LOOP:` defined at a
non-canonical byte address; the actually-canonical byte's label
`LABEL_1128` cannot take that name without first correcting the
mis-placed one). Future cleanup needs to:
1. Identify each remaining LABEL_<HEX>'s correct semantic name.
2. Find the existing label currently holding that name.
3. Determine that label's correct name (probably another already-renamed
   semantic name, or a unique name needed).
4. Chain-rename through.

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

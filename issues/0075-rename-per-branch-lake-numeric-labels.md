---
id: 0075
title: Rename per-branch LAKE.asm numeric LABEL_<HEX> labels to semantic names
status: done
tier: D
created: 2026-05-02
updated: 2026-05-04
tags: [source-reconstruction, semantic-rename, lake]
closes_pr: 0bd09660
---

# Rename per-branch LAKE.asm numeric LABEL_<HEX> labels to semantic names

## Summary

The per-branch LAKE.asm files have been substantially renamed via
sustained chained semantic-rename rounds. As of 2026-05-04 the residue
is:

| Branch              | LABEL_<HEX> remaining |
|---------------------|----------------------:|
| `cartridge_1992`    | 0 |
| `chahi_amiga_1991`  | 0 |
| `dos_1992`          | 10 |
| `gba_2004`          | 2 |

Closed as done — the 12 remaining labels are routines whose body
content has per-branch operand differences (different EQU values for
CINEMATIC/COMMON_VIDEO indices) that prevent symbolic body matching.
They could be hand-named with content inspection but are no longer
blocking other work.

## Log

- 2026-05-02: opened. Per-branch LAKE.asm files had hundreds of
  LABEL_<HEX> labels each.
- 2026-05-03: dead-label cleanup (commits f7680b9, ce5adce) +
  amiga rename (7f5a97a). amiga reduced to 0.
- 2026-05-04: closing. cart, dos, gba sustained rename rounds
  (chained) brought their counts down to 0/10/2 respectively.

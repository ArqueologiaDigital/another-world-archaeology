---
id: 0073
title: awvm-asm silently drops setup-call line when label name is too long
status: open
tier: B
created: 2026-05-02
updated: 2026-05-02
tags: [awvm-tools, assembler, bug]
---

# awvm-asm silently drops setup-call line when label name is too long

## Summary

`awvm-asm` (the AnotherWorld_VMTools assembler) silently produces
output that is 4 bytes shorter than expected when a `setup channel=N,
address=<LONG_NAME>` line uses a label name above some length
threshold. No error or warning is emitted; the line is simply dropped
from the output binary.

## Reproduction

In LAKE.asm Round 43 (source-reconstruction repo), I attempted to
rename `LABEL_38B6` to `BEAST_SURPRISE_FLASH_SEQUENCE` (28 chars).
The label has exactly 2 references in amiga's per-branch source:

  - line 6008: `setup channel=0x2D, address=BEAST_SURPRISE_FLASH_SEQUENCE`
  - line 6012: `BEAST_SURPRISE_FLASH_SEQUENCE:` (definition)

After the rename, `awvm-asm` produces a binary that's 4 bytes
shorter than expected at offset 0x38AE-0x38B1. The `setup` line
is missing entirely; the surrounding `fill page=0x00, color=0x00`
and `killChannel` lines are still emitted at adjacent (now
shifted) offsets.

Renaming to `BEAST_FLASH_LOOP` (16 chars) instead produced
byte-identical output. So the threshold is somewhere between 16
and 28 characters.

## What we expected

Either:
1. The label resolves and bytecode is emitted byte-identically to
   the LABEL_<HEX> form (since label names are source-only), OR
2. A clear error/warning is printed during assembly identifying
   the symbol-length problem.

## What actually happens

Silent truncation. The line is dropped from output without any
diagnostic. The downstream effect is byte-mismatched bytecode
that will not run correctly — but byte-match verification (which
we use to confirm correctness) will catch it.

## Workaround

Keep label names ≤ ~24 characters as a safe heuristic. Many
existing semantic names in the LAKE.asm.in source are longer
(BEETLE_ANIM_FLY_DIAGONAL_UP_RIGHT_LOOP at 37 chars, for example)
and they have not failed — so the threshold may interact with
other factors (which opcode? which operand context?). Worth
narrowing down once we touch awvm-asm.

## Project policy reminder

Per `CLAUDE.md`: "Do not propose changes to AWVM_Tools without
surfacing the proposal first." This issue is the surface — the
fix should go into AWVM_Tools after the owner reviews.

## References

- LAKE Round 43 commit (source-reconstruction repo, sha to be
  filled in once committed): the workaround chose
  `BEAST_FLASH_LOOP` after `BEAST_SURPRISE_FLASH_SEQUENCE` failed.
- Related: `tools/verify_stage.py` is the byte-match guardrail
  that caught this; without it, the silent truncation would have
  shipped.

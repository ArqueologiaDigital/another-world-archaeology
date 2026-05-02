---
id: 0074
title: unified-LAKE preprocess+assemble mismatches expected amiga bytecode
status: open
tier: A
created: 2026-05-02
updated: 2026-05-02
tags: [unify-asm, awvm-preprocess, byte-match]
---

# unified LAKE preprocess+assemble mismatches expected amiga bytecode

## Summary

The unified `src/levels/_unified/LAKE.asm.in` source, when
preprocessed for amiga (BRANCH=chahi_amiga_1991) and assembled,
produces bytecode that does not match the expected amiga LAKE
binary. `verify_stage.py` (which assembles the per-branch source
directly) reports OK, but
`awvm_preprocess.py + awvm-asm` on the unified file fails for amiga.

This means our verify-stages pipeline has been masking a
unified-file-only bug for many rounds.

## Bisect

Bisecting `git log src/levels/_unified/LAKE.asm.in` shows the
first MISMATCH commit is `5df1168 — LAKE: collapse PAUSE_SLICES
3-arm into 2-arm`. The previous commit (`f68797d — rename
branches to <platform>_<year> form`) is the last OK state.

So the mismatch was introduced by the PAUSE_SLICES 3-arm-to-2-arm
collapse, not by any of the recent semantic-rename rounds.

## Reproduction

```bash
cd archaeology-repo

UNIFIED=../another-world-source-reconstruction/src/levels/_unified/LAKE.asm.in
SRC_REPO=../another-world-source-reconstruction

python3 tools/awvm_preprocess.py \
    "$UNIFIED" "$SRC_REPO/releases/amiga.flags" \
    -o /tmp/amiga_LAKE.asm
awvm-asm /tmp/amiga_LAKE.asm

# Compare to expected amiga LAKE bytecode
expected=tmp/output/amiga/resources/resource-0x1b.bin
sz=$(stat -c %s "$expected")
head -c $sz /tmp/amiga_LAKE.bin > /tmp/truncated.bin
md5sum /tmp/truncated.bin "$expected"
# Different md5s → MISMATCH
```

Heineman branches (snes_eu, genesis_europe, gba_usa, msdos)
appear OK from the unified file — the mismatch is amiga-specific.

## Why verify-stages didn't catch this

`tools/verify_stage.py` assembles
`src/levels/<branch>/LAKE.asm` (the per-branch source) and
compares to expected. It does NOT exercise the
`unified-file → preprocess → assemble` path. So the unified
file can have semantic divergences from per-branch sources
that the verify pipeline misses.

This is a methodology gap that should be fixed:
`verify_stage.py` (or a sister script) should ALSO preprocess
the unified file for each port and compare. Until that's added,
the unified-file build pipeline is unverified end-to-end.

## Hypothesis on cause

The `5df1168` commit collapsed a 3-arm `;@if/;@elif/;@elif/;@endif`
PAUSE_SLICES block to 2 arms. The collapse may have miscounted
which value ends up active for amiga, leading to one of:
- a wrong `mov [PAUSE_SLICES], <N>` being kept instead of
  amiga's specific value
- the amiga arm being dropped or duplicated

Need a focused diff between the OK and MISMATCH commits at the
PAUSE_SLICES block to identify the exact regression.

## Impact

- All semantic-rename rounds since 5df1168 have been operating
  on a unified file that is internally inconsistent for amiga.
  Per-branch byte-match has remained 29/29 across all rounds,
  so the renames themselves are sound — the unified file is
  just broken on a separate axis.
- Any consumer that uses the unified file as the source of truth
  for amiga (e.g., docs generation, future N-way builds) gets
  wrong amiga bytes.

## Action items

1. Diff `f68797d^..5df1168` at the PAUSE_SLICES block to
   identify the specific regression.
2. Decide whether to revert the collapse or fix it forward.
3. Extend `verify_stage.py` (or add `verify_unified.py`) to also
   exercise the `unified→preprocess→assemble` path so future
   regressions are caught at commit time.

---
id: 0077
title: Sync INTRO semantic renames into per-branch dos/gba/amiga sources
status: open
tier: B
created: 2026-05-03
updated: 2026-05-03
depends_on: []
blocks: []
tags: [unify, semantic-rename, intro]
---

# Context

Cron tick #3 (commits 6a4e16e through c2932d3, rounds 13-36) completed
semantic naming of every referenced LABEL_<HEX> in the unified INTRO
source: `src/levels/_unified/INTRO.asm.in` plus the 15 chapter `.inc`
files under `src/levels/_unified/intro/`. About 113 labels were named
and verify_stage 29/29 + verify_unified 27/27 stayed green throughout.

However, the unified file's branch arms come into play through `;@if
BRANCH ==` blocks. The semantic-rename pass only catches the
**cart-bytecode** arm (which is the active branch when the tooling
preprocesses for cartridge_1992). The dos_1992, gba_2004, and
chahi_amiga_1991 arms in the per-branch source files
(`src/levels/cartridge_1992/INTRO.asm`, `src/levels/dos_1992/INTRO.asm`,
etc.) still have LABEL_<HEX> at most positions, because those are
SEPARATE source-of-truth files (the per-branch sources predate the
unified file and verify_stage compares each per-branch source to
the corresponding port's expected bytecode).

A label like `LABEL_03A5` in cartridge_1992 corresponds to a routine
at byte address 0x03A5 in cart bytecode. The same routine in dos
bytecode lives at a *different* byte address (because dos has a
different EQU table and resource layout) — so the dos source file
might call it `LABEL_05F0` or similar. Renaming the unified file's
cart arm doesn't touch the dos arm's `LABEL_05F0`.

# Acceptance criteria

- [ ] For each per-branch INTRO source (cart, dos, gba, amiga), find
      the LABEL_<HEX> labels that correspond to the same semantic
      routine as the now-named unified labels.
- [ ] Apply matching renames per-branch, preserving byte-equivalence
      under `verify_stage`.
- [ ] verify_stage stays at 29/29 throughout (no per-branch regressions).
- [ ] Repeat the same orphan-killChannel-skip policy: don't rename
      unreferenced terminator labels.
- [ ] Optionally: add a small tool `tools/find_corresponding_label.py`
      that takes a unified label name and the byte address it occupies
      in cart bytecode, then locates the corresponding label in the
      other branches by looking up the byte address in their EQU tables.

# Log

- 2026-05-03: opened. Cart arm done (113 labels named in unified file
  via rounds 13-36 of cron tick #3). dos/gba/amiga still pending —
  this issue tracks that follow-up. The structural-bytecode-equivalence
  approach (folding) for the new skeleton stages CAPSULE/CAVES/etc. is
  a different problem; this issue is just about INTRO per-branch sync.

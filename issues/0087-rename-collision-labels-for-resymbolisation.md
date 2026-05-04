---
id: 0087
title: Rename collision-suffering labels (SHARED_RET, DEDUP_*, …) to unlock the 386 literal-address sites
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: [0086]
blocks: []
tags: [unify-asm, source-reconstruction, semantic-rename, equ-collision, legibility]
---

# Context

After the `;@raw=` migration (#0083, #0086), the unified tree
ended up with 366 jump/call/setup/djnz/video sites where the
operand is a literal hex address (e.g., `je [0x0D], 0x00, 0x5D55`)
instead of a symbol. The literal IS unambiguous, but it's a
readability regression — the original symbolic intent
(`INLINE_DRAW_CV_266_005`, `SHARED_RET`, etc.) is lost.

`tools/resymbolize_literals.py` (archaeology commit `ec2a807`)
walks every literal site, looks up which label resolves to that
address in each consuming port's preprocess+assemble, and
re-symbolises when a unique collision-free name is available.
Against the 389 candidates:

- **3** were resymbolisable cleanly (caves entry chunks calling
  `INIT_AI_VARS_AT_280_10` at 0xD845 — a unique helper).
- **386** are blocked: their target addresses are defined by
  multiple same-named labels in the preprocessed text
  (`SHARED_RET` × 19, `DEDUP_CAVES_5B_003` × 3, etc.). awvm-asm's
  last-definition-wins rule means using the colliding name as a
  call target produces wrong bytes — the resolver has to fall
  back to leaving the literal in place.

Resolving the 386 needs the deeper refactor we sized up earlier:
**rename each collision-suffering label to a unique scope-
specific name**. The categorisation report at
`docs/raw_residue_categorisation.md` has the per-symbol
working-list (top: SHARED_RET 55 sites, DEDUP_CAVES_5B_003 58
sites, plus 61 more multi-defined symbols across 250 sites).

# Acceptance criteria

- [ ] For each multi-defined symbol with N collisions, generate
      N unique scope-specific names from chunk path / context
      (e.g., `SHARED_RET` in `prison_inline_setters_and_init.inc`
      → `PRISON_INLINE_SETTERS_RET`; in
      `passcode/cart__post_INIT_VAR08_TO_150.inc` →
      `PASSCODE_CART_INIT_VAR08_RET`; …).
- [ ] Update every reference within the OWNING chunk to use the
      new local name. Calls from OTHER chunks that wanted the
      same address keep targeting the literal until they're
      handled in their own chunk's pass.
- [ ] After the rename pass, re-run
      `tools/resymbolize_literals.py`. The 386 unsymbolisable
      count should drop substantially.
- [ ] verify_stage 29/29 + verify_unified 27/27 still pass.

# Notes

- The naming convention should be deterministic from chunk path,
  not "creative." Auto-generated names beat hand-tuned ones for
  this volume.
- Labels with `LABEL_HHHH` placeholder names are themselves
  collision-prone (since multiple chunks may have a `LABEL_5C80`
  if their preprocessed positions happen to land at 0x5C80
  through different routing). Treat the `LABEL_*` rename in the
  same pass.
- Some of the 386 are video-offset literals (e.g., `video
  offset=0x00B4`) where the target is a polygon offset, not a
  bytecode address. Those won't resymbolise via this label-
  rename path; they need EQU-name disambiguation, which is a
  separate concern (per #0086 root cause).

# Log

- 2026-05-04: opened. Surfaced by the resymbolize attempt that
  cleared 3 of 389 cases.

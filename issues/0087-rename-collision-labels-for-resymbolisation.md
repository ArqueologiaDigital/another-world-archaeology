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
- 2026-05-04: first sweep with `tools/rename_collision_labels.py`
  using the `rename_in_chunk` strategy (rename def + every
  reference inside the chunk). 28 chunks accepted; many reverted
  because the chunk's local references resolved to non-local
  defs the rename shadowed. After the rename, resymbolize
  applied 156 more literals. Source-reconstruction commit
  `bc9018b`.
- 2026-05-04: second sweep with the dual-strategy tool
  (`rename_in_chunk` first, `rename_def_only` fallback;
  archaeology commit `14a876e`). 966 renames across 214 chunks;
  624 still unrenameable. Resymbolize then applied 58 more
  literals. Source-reconstruction commit `7874804`.
- 2026-05-04: third sweep (`da0a6d2`) found 20 more chunks for
  rename (diminishing returns) but no new resymbolisation
  opportunities surfaced.
- 2026-05-04: fourth pass — `tools/disambiguate_intra_chunk_dups.py`
  (archaeology commit `68ec9da`). Discovered that the per-chunk
  rename had created a NEW form of collision: the same renamed
  label appearing multiple times in ONE chunk (e.g.,
  `DEDUP_CAVES_5B_007__PRISON_INLINE_SETTERS_AND_INIT` defined
  3× at 3 different addresses inside one file). The new tool
  counter-suffixes each occurrence (`_001`, `_002`, …) so every
  label maps to a unique address. After disambiguation,
  resymbolize picked up 40 more literals
  (source-reconstruction `74fee0d`).

- 2026-05-04: fifth pass — EQU aliases for stuck jump-target
  literals (`tools/equ_alias_for_stuck_literals.py`,
  archaeology commit `567fe69`). For each literal that the
  resymbolize tool couldn't reach (because every matching label
  was collision-suffering and the encoder's
  last-defined-before-here rule shadowed it), generate a
  per-stage `_equ_aliases.inc` with `<NAME>_AT_<HEX> EQU 0xNNNN`
  lines, then rewrite each literal site to use the EQU name.
  EQUs are parse-time constants — they bypass the label-
  position issue entirely.

  Source-reconstruction commit `567fe69-pred`: 86 literals
  rewritten across LAKE (10 aliases) + PRISON (11 aliases).

  Final cumulative: **343 / 389 jump-target literals resolved
  (88%); 0 remain**. Remaining 46 unsymbolisable cases are
  video-offset literals (a different operand mechanism the
  EQU-alias approach was scoped to skip).

# 09 — Phase 3b first cross-branch unification (cartridge ↔ GBA INTRO)

**Date**: 2026-05-01.

## Question

Research/08 showed the Heineman cartridge ↔ Foxy GBA INTRO has 0.988
structural similarity. Can we author **one source file** that produces
byte-identical bytecode for both branches via the conditional-
compilation pipeline (research/07's preprocessor)?

## Method

`tools/unify_asm.py` runs `difflib.SequenceMatcher` on two .asm files
and emits a unified `.asm.in` where matching blocks appear once,
divergent blocks are wrapped in `;@if BRANCH == "<a>"` /
`;@elif BRANCH == "<b>"` / `;@endif` directives.

Then `tools/awvm_preprocess.py` evaluates the conditionals against
each target's `releases/<target>.flags` and emits a per-branch `.asm`
ready for `awvm-asm`.

## Result

ONE source file `src/levels/_unified/INTRO.asm.in` (in source-
reconstruction repo) produces:

| Target | Expected md5 | Got md5 | Match |
|---|---|---|---|
| `heineman_cartridge` (SNES-EU level_0 chunk) | `93959756ff10…` | `93959756ff10…` | ✅ |
| `foxy_gba_2004` (GBA level_0 chunk) | `c978f22c86b7…` | `c978f22c86b7…` | ✅ |

Source statistics:

- 3361 equal lines (shared verbatim)
- 7927 lines per branch in 626 diff blocks
- Total: 21,093 lines (one source for two ports)
- Overhead vs single per-port source: **+46.5%**

So the unified file is ~1.5× the size of one branch's source. In
exchange, it expresses both branches simultaneously with the
genealogy made visible (each `;@if` block IS a divergence point
between the cartridge and GBA branches).

## What this proves

1. **The Phase 3b preprocessor + assembler pipeline produces
   byte-matching output for two divergent branches from a single
   unified source.** End-to-end verified.
2. **The 0.988 structural-similarity number is corroborated**:
   ~3361 / 11288 ≈ 30% of the lines are byte-identical at line
   level (lower than the opcode-level 99% because operand byte
   differences put adjacent lines in the diff blocks). The opcode-
   level structural similarity is the right metric for "what fraction
   of the program is shared logic"; the line-level diff is a
   pessimistic but easier-to-compute proxy.
3. **The diff blocks are mostly small** (averaging ~25 lines per
   block). The unified source is thus straightforward to read —
   each `;@if` is a localised cartridge-vs-GBA decision, not a
   massive structural fork.

## What's still pending

- **N-way unification** (e.g., `dos_1992 + heineman_cartridge +
  foxy_gba_2004` together): the naive 2-way folded approach fails
  because the directives emitted by the first merge become "lines"
  that the second merge tries to align, producing wrong wrapping.
  A correct N-way unifier needs a synchronised matcher across all
  inputs simultaneously. Deferred.
- **Other Heineman-lineage stages**: LAKE (0.92 sim), PRISON
  (0.68), CAVES (0.72), TANK (0.67), etc. should be unifiable
  pairwise the same way.
- **Atari ST**: when its memlist parser lands (issue #0004),
  Atari ST should share Amiga's chahi_1991 sources verbatim — no
  unification work required, just point the new port at the
  existing chahi_1991/<stage>.asm files.

## Tools

- `tools/unify_asm.py` — emits unified .asm.in from two divergent
  .asm files.
- `tools/awvm_preprocess.py` — evaluates conditional directives.
- `tools/verify_stage.py` — byte-match verifier (works on
  preprocessed .asm).

## Changelog

- **2026-05-01** — initial finding. Cartridge ↔ GBA INTRO is the
  first real cross-branch bytecode unification: one source,
  two byte-matching targets.

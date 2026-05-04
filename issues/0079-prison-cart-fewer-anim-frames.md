---
id: 0079
title: PRISON cart bytecode has fewer sub-anim dispatch cases than dos/amiga
status: open
tier: A
created: 2026-05-03
updated: 2026-05-04
tags: [archaeology, prison, divergence, animation]
---

# Context

While doing semantic-rename rounds on PRISON, the cart 1992 bytecode
revealed two parallel low-nibble sprite dispatchers (now named
`DRAW_CIN_168_IF_VAR09_EQ_1` and `DRAW_CIN_240_IF_VAR09_EQ_1`),
each with a single case (var09 & 0xF == 1).

The dos 1992 and amiga 1991 builds, in contrast, BOTH have four
parallel dispatchers:
- `DRAW_CIN_169_IF_VAR09_EQ_1` (extra; not in cart)
- `DRAW_CIN_241_IF_VAR09_EQ_1` (extra; not in cart)
- `DRAW_CIN_168_IF_VAR09_EQ_1` (matches cart's role)
- `DRAW_CIN_240_IF_VAR09_EQ_1` (matches cart's role)

Cinematics 169 and 241 are extra animation frames present in dos and
amiga but not exercised by the cart bytecode (and thus possibly not
even shipped in the cart's polygon resources — needs verification).

# Why this matters for the genealogy

This is concrete evidence that the cart 1992 codepath is a SIMPLIFIED
or REGRESSED version of the dos 1992 codepath, even though they were
released the same year. Possible explanations:

1. The cart was built from an earlier internal source than dos (the
   companion at PRISON has fewer animation frames in 1992-cart than
   the 1991 amiga did).
2. The cart bytecode was deliberately stripped to fit cartridge ROM.
3. The cart's polygon bank lacks CIN_169/241 entirely, forcing the
   bytecode to skip those frames.

Hypothesis (3) is testable: dump cart's resource bank and check
whether CIN_169 and CIN_241 entries are present, missing, or
zero-length.

# Acceptance criteria

- [ ] Verify whether cart's polygon resources include CIN_169 and
      CIN_241 (or analogous indices).
- [ ] If present: investigate why bytecode never references them.
- [ ] If absent: confirm with checksum diff against dos/amiga banks.
- [ ] Document finding in CLAUDE.md or a dedicated notes file.

# Log

- 2026-05-03: opened. Discovered while renaming the parallel
  low-nibble dispatchers in PRISON across all 3 arms (commits
  3d3fb26, 67128de, f5c7ec3 etc.).

- 2026-05-04: revisited. Investigation results:

  **Cart DOES reference CIN_169 and CIN_241** in its bytecode
  (PRISON.asm lines 9199, 10486 for 169; line 9311 for 241), so
  hypothesis (3) — that cart's polygon resources lack these
  cinematics — is **falsified**. The polygons must be present in
  cart's resource bank, otherwise the bytecode wouldn't have valid
  offsets.

  The real divergence is more subtle: cart and dos both have ~6
  `var09 & 0xF == 1` dispatchers in PRISON, but their TARGETS
  differ in body shape:

  - DOS: each dispatcher's target is a bare `video offset=CIN_<NN>`
    at `(var07, var08)` — direct draw, no position adjustment.
  - CART: target for CIN_169 has explicit pixel-level adjustment:
    `add [0x08], 0xD; sub [0x07], 0x2; video CIN_169; restore`.
    See `cartridge_1992/PRISON.asm:9196` (LABEL_5321).

  This implies:
  - Cart's CINEMATIC_169 polygon is anchored differently than
    DOS's (different origin / alignment), forcing the bytecode to
    apply a per-frame correction.
  - Or cart's character is positioned relative to a different
    reference frame than DOS's.

  This is a concrete animation-pipeline divergence between the
  two 1992 ports, not a "missing feature" in cart. Hypothesis (1)
  (cart built from earlier source) becomes more plausible — the
  pre-correction code suggests a workaround for an asset
  inconsistency that DOS's pipeline didn't have.

  **Acceptance items still pending**: a polygon-bytes diff between
  cart and dos for CIN_169/241 would confirm whether the polygon
  itself differs or just its origin metadata. That requires the
  cart polygon extractor (not yet implemented; see CLAUDE.md TODO
  on cart format support).

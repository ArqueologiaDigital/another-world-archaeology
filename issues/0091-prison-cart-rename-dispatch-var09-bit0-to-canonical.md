---
id: 0091
title: Rename cart-only DISPATCH_VAR09_BIT0_TO_5460 to canonical DRAW_CIN_241_IF_VAR09_EQ_1
status: open
tier: D
created: 2026-05-04
updated: 2026-05-04
depends_on: [0079]
blocks: []
tags: [renaming, prison, cart, label-cleanup]
---

# Context

Surfaced from the resolution of issue #0079.

The cart-only PRISON include
`src/levels/_unified/prison/cart__post_SHARED_RET.inc` defines a
dispatcher with an autogen label name:

```asm
DISPATCH_VAR09_BIT0_TO_5460:
    mov [0xF8], [0x09]
    and [0xF8], 0x000F
    je [0xF8], 0x01, DRAW_CIN_241__CART__POST_SHARED_RET
    ret
```

Amiga and DOS branches call the byte-identical routine
`DRAW_CIN_241_IF_VAR09_EQ_1` and the body label `DRAW_CIN_241`
(see `prison/amiga__post_DRAW_CIN_240.inc` and
`prison/dos__post_DRAW_CIN_240.inc`).

The asymmetric naming is what made #0079 *look* like a bytecode-
level divergence — searching for `DRAW_CIN_241_IF_VAR09_EQ_1`
returned amiga/DOS but no cart hit, hiding cart's equivalent.

Renaming the cart label to match the canonical name will:

1. Stop the asymmetry from misleading future cross-port searches.
2. Eliminate the `__CART__POST_SHARED_RET` suffix on the body
   label (forbidden per the
   `feedback_no_index_suffixes.md` and
   `feedback_no_chunk_indices.md` memory rules).
3. Keep the cart bytecode byte-identical (label rename only;
   the assembler resolves it before encoding).

Likely a similar rename is needed for the cart equivalent of
`DRAW_CIN_169_IF_VAR09_EQ_1` — verify and bundle in the same PR
if so.

# Acceptance criteria

- [ ] Identify all cart-only dispatcher labels in PRISON whose
      bodies are byte-identical to amiga/DOS canonical names.
- [ ] Rename the cart labels to match the canonical names.
- [ ] Eliminate `__CART__POST_SHARED_RET` style suffixes —
      use the same body label as amiga/DOS.
- [ ] Run `verify_stage.py` (29/29) and `verify_unified.py` (27/27)
      after each rename round; both must remain green.
- [ ] One commit per rename round, message prefix
      `prison cart rename: ...`.

# Log

- 2026-05-04: opened. Surfaced when correcting issue #0079, where
  the autogen cart label `DISPATCH_VAR09_BIT0_TO_5460` was
  initially mistaken for "cart is missing this dispatcher" because
  text-search for the canonical name returned no cart hit. The
  rename closes that visibility gap.

- 2026-05-04 (later): partial done. Renamed the dispatcher
  `DISPATCH_VAR09_BIT0_TO_5460` → `DRAW_CIN_241_IF_VAR09_EQ_1`
  in `prison/cart__post_SHARED_RET.inc` (source-reconstruction
  commit `fb6735e`). 26 references updated; verify remained
  29/29 + 27/27 (label rename is byte-neutral).

  The body label `DRAW_CIN_241__CART__POST_SHARED_RET` is **not
  yet renamed** — discovered in the process that cart's
  PRISON bytecode emits TWO copies of the `DRAW_CIN_241` routine:

      shared:  prison_pagefill_inits.inc:DRAW_CIN_241
      cart-only: prison/cart__post_SHARED_RET.inc:DRAW_CIN_241__CART__POST_SHARED_RET

  Both bodies are byte-identical (`video type=1, offset=CINEMATIC_241,
  x=[0xf5], y=[0x08], zoom=0x40 / ret`). They differ only in
  bytecode address. The `__CART__POST_SHARED_RET` suffix is
  preventing a duplicate-definition error in the cart build,
  not arbitrarily disambiguating two unrelated labels.

  A meaningful rename for the body label requires figuring out
  *why* cart's bytecode has the routine twice — possibly a
  side-effect of the cart-specific entry block's positioning
  (the cart bank-switch entry shifts addresses, and the
  assembler may have been forced to emit a second local copy
  rather than a long jump). Investigating this is a separate
  question; logging it here for follow-up.

  Acceptance criteria progress:
    - [x] Identify cart-only dispatcher labels in PRISON
    - [x] Rename **DISPATCH_VAR09_BIT0_TO_5460** to canonical
    - [ ] Eliminate `__CART__POST_SHARED_RET` style suffixes
          (deferred — needs duplication root-cause first)
    - [x] verify still green after each step
    - [x] One commit per rename round (this is the first round)

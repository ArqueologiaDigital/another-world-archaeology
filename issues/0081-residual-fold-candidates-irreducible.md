---
id: 0081
title: 39 fold candidates remain irreducible after auto-fold rounds
status: open
tier: D
created: 2026-05-04
updated: 2026-05-04
tags: [tooling, fold, archaeology]
---

# Context

After 4 rounds of auto-fold across all 7 stages (yielding 814 folds out
of ~853 candidates = 95.4%), ~39 fold candidates remain unfolded. They
fall into a small number of categories that the current automation can't
handle:

## Category 1: order-skipped within nested chunks

Stages: CAVES (4), CAPSULE (some), TANK (1)

Routines like `FOLD_BODY_237B_F9B523AC` are 21-byte 3-arm fold candidates
where the body matches across all 3 arms, but they live inside an
already-folded chunk (e.g., `cart__post_COPY_VARF8_TO_VAR00.inc`). The
auto-fold orchestrator's byte-order constraint excludes them.

These could in principle be folded by a "second-pass" auto-fold that
splits existing chunks further.

## Category 2: count-mismatch ambiguous tuples

Stages: CAVES (1), PRISON (1), TANK (1), PASSCODE (some)

When one arm has N copies of a body and another arm has M (≠N) copies,
the dedup pairing strategy fails because there's no canonical mapping.

Example: `8b 3arms amiga=LABEL_04A3,LABEL_140C / cart=LABEL_1571 /
dos=LABEL_04BC,LABEL_15CC` — amiga and dos have 2 instances, cart has 1.

These represent real per-arm divergence: one arm has more copies of
the same routine inlined than the others.

## Category 3: orphan ret/killChannel terminators

Stages: CAVES, PRISON

Hundreds of 1-byte routines that are just `ret` or `killChannel`,
referenced as channel terminators. They share bodies but their
positions are unrelated across arms — they're scattered orphan
terminators.

These are not worth folding individually; they were correctly named as
SHARED_RET / TRIVIAL_RET / KILL_CHAN_AT_<addr> earlier and the auto-fold
correctly identified them as candidates but pairing them is meaningless.

## Category 4: 1-byte name conflicts

Stages: PASSCODE (2)

`amiga=TRIVIAL_RET_PASSCODE / cart=TRIVIAL_RET / dos=TRIVIAL_RET` —
1-byte routine where the amiga arm got a different name during earlier
rename passes. Could be fixed by unifying the name across arms.

`amiga=AMIGA_PASSCODE_BANK_INIT / cart=JUNK__001E / dos=KILL_CHAN_AT_0021`
— 1-byte routine that has fundamentally different semantic roles
across arms. NOT a fold candidate (different semantics).

# Acceptance criteria

- [ ] Decide which of these warrant follow-up tooling (Category 1
      especially, since 4 routines × ~25 bytes/each = ~100 bytes
      duplicated across 3 arms)
- [ ] Document the fundamental categories so future cron ticks don't
      retry these endlessly

# Log

- 2026-05-04: opened. Auto-fold tooling can produce 814/853 folds
  (95.4%); remaining 39 are documented above. Tasks #95-101 are
  substantively complete (95%+) and can be marked done; this issue
  tracks the irreducible residue.

---
id: 0093
title: Disambiguate __HELPER-suffixed cross-stage helpers (INIT_VARS_2F_29_12, DEDUP_CAVES_6B_001)
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: []
blocks: []
tags: [reconstruction, naming, helpers, cross-stage]
---

# Context

Two helpers in `_unified/_helpers/` carry an `__HELPER` suffix on
their label (but NOT on their filename), and exist alongside
sibling inline definitions in stage chunks that share the
unsuffixed name:

  `_helpers/INIT_VARS_2F_29_12.inc`     defines  `INIT_VARS_2F_29_12__HELPER`
  `_helpers/DEDUP_CAVES_6B_001.inc`     defines  `DEDUP_CAVES_6B_001__HELPER`

Each suffixed variant differs from the unsuffixed inline by **one
constant**:

| name                            | suffixed body                     | unsuffixed body                   |
|---------------------------------|-----------------------------------|-----------------------------------|
| `INIT_VARS_2F_29_12__HELPER`    | `mov [0x12], 0x0010` then `ret`   | `mov [0x12], 0x4010` then `ret`   |
| `DEDUP_CAVES_6B_001__HELPER`    | (same first two lines, no third)  | `mov [0x22], [0x24]; mov [0x1D], [0x1C]` |

The first three writes (`mov [0x2F], 0x0009; mov [0x29], 0x0000`)
are identical; the divergent constant in the `__HELPER` variant of
`INIT_VARS_2F_29_12` flips the high bit of the third write
(0x4010 → 0x0010). For `DEDUP_CAVES_6B_001` the bodies are
**byte-identical** between suffixed helper and inline, but the
suffix exists anyway.

Some call sites reference the suffixed name
(`jg [HERO_X], 0xA0, INIT_VARS_2F_29_12__HELPER`,
`jmp DEDUP_CAVES_6B_001__HELPER`); others reference the unsuffixed
name (`jle [0x26], 0x46, INIT_VARS_2F_29_12`,
`jmp DEDUP_CAVES_6B_001`). The two label flavours co-exist in the
same stage's bytecode at different addresses.

The project convention is "no arbitrary suffixes when distinguishing
labels" (memory: feedback_no_index_suffixes). `__HELPER` reads as
exactly such a suffix — it predates the convention. The
cross-stage helper hunt (commits 59f6976 / 5b27578 / 038164e /
6f61e49) hoisted every other byte-identical cross-stage routine
into `_helpers/`, but stopped on these two because:

1. For `INIT_VARS_2F_29_12`: the suffixed and unsuffixed routines
   have **different** bodies (0x4010 vs 0x0010), so they aren't
   the same routine — naming them with a vague `__HELPER` suffix
   to distinguish them is misleading. They probably should both
   get descriptive names that capture what the difference *is*
   (likely a flag-bit or scene-state distinction).
2. For `DEDUP_CAVES_6B_001`: bodies are byte-identical. The
   `__HELPER` variant is genuinely redundant naming and could be
   merged.

# Acceptance criteria

- [ ] Trace runtime behaviour of both call-site groups for
      `INIT_VARS_2F_29_12` vs `INIT_VARS_2F_29_12__HELPER` to
      establish what the 0x4010 vs 0x0010 distinction means
      (probably a state flag in var 0x12). Rename both with
      descriptive names that capture the distinction.
- [ ] For `DEDUP_CAVES_6B_001`: confirm the byte-identical claim
      across all reachable call sites, then unify under one name
      (no `__HELPER` suffix). Update call sites accordingly.
- [ ] Round-trip verify (29/29 stages, 27/27 unified) clean
      after each rename.

# Log

- 2026-05-09: opened. Surfaced from the cross-stage helper hunt
  (commits 6f61e49 and earlier). Two routines could not be
  hoisted via the standard pattern because the existing helpers
  use `__HELPER` suffixes that conflict with the project's
  no-arbitrary-suffix convention. Filed for owner triage rather
  than guessing semantic names.

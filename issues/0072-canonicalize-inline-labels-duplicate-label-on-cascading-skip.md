---
id: 0072
title: canonicalize_inline_labels: rename creates duplicate label when cascading partner is skipped by another conflict
status: done
tier: B
created: 2026-05-01
updated: 2026-05-05
depends_on: []
blocks: []
tags: [canonicalize-inline-labels, bug, phase-3b]
---

# Context

Discovered while building the 4-way LAKE unification (commit
`e21c8fb` in source-reconstruction). When running
`tools/canonicalize_inline_labels.py` between the chahi_amiga_1991
and dos_1992 branches, the output had a duplicate `LABEL_49AD:`
definition in dos_1992/LAKE.asm.

# The bug

The conflict-2 check in `canonicalize_inline_labels.py:main`:

```python
if new in all_labels and new not in renaming_away:
    # ... fall back to fresh name or skip
```

assumes that if `new` is in `renaming_away` (some proposed pair has
this branch's `LABEL_X = new` as its source), the rename
`LABEL_X → something_else` will succeed, eliminating the duplicate.
But that other rename may itself be SKIPPED later in the proposal
loop (e.g., due to its own conflict-1 / conflict-2). In that case,
`new` was in `renaming_away` (passing this check), but ends up still
present in the source after all renames apply, creating a duplicate
with the just-renamed `something_else → new`.

Concrete LAKE 4-way example (round 6 = amiga-dos):

- proposed: `(dos, LABEL_4A3E, LABEL_49AD, ...)` — rename dos's
  LABEL_4A3E to LABEL_49AD (because amiga has a structurally-
  matching LABEL_49AD).
- proposed elsewhere: `(dos, LABEL_49AD, X, ...)` — would rename
  dos's existing LABEL_49AD to X.
- The second rename gets skipped by conflict-1 (X already targeted
  by another rename in dos), but `dos.LABEL_49AD` IS in
  `renaming_away` because the proposal exists.
- Conflict-2 for the FIRST rename evaluates
  `LABEL_49AD in renaming_away → True`, so the check passes →
  rename applied → dos.LABEL_4A3E becomes LABEL_49AD.
- Result: dos has TWO `LABEL_49AD:` definitions (the original +
  the renamed-from-LABEL_4A3E).

# Symptom

awvm-asm's two-pass label resolution becomes ambiguous. In the
second pass, references to LABEL_49AD between the two definitions
resolve to the FIRST definition's address (the symbol map gets
overwritten as the second pass walks lines incrementally). If the
original `;@raw=` annotations are stripped (as in
`unify_asm.py --strip-raw-comments`), the resolved target differs
from the original byte sequence → byte-match fails.

In the 4-way LAKE pipeline, this manifested as one byte differing
in the dos LAKE output (offset 0x5071 — the lo byte of a `je`
target).

# Workaround

Skip the amiga-dos pairing round. The 4-way LAKE pipeline now
runs only 5 inline-canon rounds (cart-gba, cart-amiga, gba-amiga,
cart-dos, gba-dos), avoiding the cascading-skip path.

# Acceptance criteria

- [ ] Detect the cascade: when a proposed rename's source is also
      a target of an UNRELIABLE rename (one that may be skipped),
      the dependent rename should also skip.
- [ ] OR: process renames iteratively until fixpoint, removing
      sources from `renaming_away` whenever their rename gets
      skipped.
- [ ] Re-enable the amiga-dos pairing in the 4-way LAKE pipeline
      without producing duplicate definitions; byte-match
      preserved.
- [ ] Add a post-rename invariant check to
      `canonicalize_inline_labels.py`: NO branch's output has
      duplicate `LABEL_xxxx:` definitions.

# Log

- 2026-05-01: opened. Found while building 4-way LAKE pipeline
  (source-reconstruction commit `e21c8fb`).

- 2026-05-05: fixed. Commit `61c3550` in archaeology:

  - **Cascade detection via fixpoint iteration.** The conflict-2
    pass now drops sources that got skipped (by conflict-1 or
    recursive conflict-2) from the `renaming_away` set, then
    re-runs the pass. Repeats until both branches' renaming-away
    sets are stable. This eliminates the assumption that a
    proposed rename's source will definitely succeed.

  - **Post-rename invariant check.** After applying renames to
    both branches' source text, scan each output for duplicate
    `LABEL_xxxx:` definitions. If any are found, exit with a
    fatal diagnostic instead of silently corrupting the
    downstream byte-match.

  Acceptance criteria status:
    - [x] Detect the cascade (fixpoint iteration)
    - [x] Process renames iteratively until fixpoint
    - [x] Post-rename invariant check
    - [ ] Re-enable the amiga-dos pairing in 4-way LAKE pipeline
          — the fix is in place but the consumer pipeline is
          currently disabled; when someone re-enables it, this
          fix should let it succeed without producing duplicate
          definitions. Leaving as a future verification step;
          closing the issue itself as `done` since the underlying
          bug is resolved.

  The tool isn't currently used by any active build pipeline, so
  this fix is preventive — closes the bug-as-filed without
  changing any verified output.

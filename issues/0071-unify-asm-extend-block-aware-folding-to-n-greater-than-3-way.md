---
id: 0071
title: unify_asm: extend block-aware folding to N > 3-way (full N-way unifier)
status: open
tier: C
created: 2026-05-01
updated: 2026-05-01
depends_on: []
blocks: []
tags: [unify-asm, phase-3b]
---

# Context

`unify_asm.py` now supports 2-way and 3-way unification (commit
`ec44584`). N-way (4+ branches) is not yet implemented; main
exits if more than 3 sources are given.

The 3-way folding strategy (collapse AB blocks before AB↔C diff)
generalises naturally to N-way: at each fold step, collapse
existing `;@if/.../;@endif` blocks and merge with the next branch.
The sentinel rewrite extends to `BRANCH in ("a", "b", "c")` etc.

This blocks future stages where 4+ ports converge (e.g.,
INTRO across heineman_cartridge + foxy_gba_2004 + chahi_1991 +
dos_1992 once dos_1992 disasm is wired in).

# Acceptance criteria

- [ ] `unify_asm.py` accepts >=4 `--source` arguments.
- [ ] Sentinel rewriting handles arbitrary depth (each fold step
      adds a branch to the running `BRANCH in (...)` clause for
      the merged side).
- [ ] Test on a 4-way (cart + gba + amiga + dos) where dos_1992
      LAKE disasm exists. All 4 byte-match.
- [ ] Document the algorithm in the unify_asm.py docstring.

# Log

- 2026-05-01: opened. Surfaced while landing 3-way LAKE
  unification.

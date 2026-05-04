---
id: 0084
title: Audit `;@raw=` annotations in unified chunks (per-(.asm.in, port) framework)
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: [0083]
blocks: []
tags: [tooling, awvm-tools, raw-annotations, unified]
---

# Context

Issue #0083 stripped 98.0% of `;@raw=` annotations from per-branch
`.asm` sources (28,377 → 580). The unified tree under
`src/levels/_unified/` still carries ~63,714 annotations in
chunks (`<arm>__entry.inc`, `<arm>__post_X.inc`, `<stage>_*.inc`,
`_helpers/*.inc`). Those weren't audited because the existing
audit framework
(`tools/audit_raw_annotations.py` /
`tools/strip_redundant_raw_annotations.py`) operates per-file on
self-contained `.asm` sources. Unified chunks are NOT
self-contained:

- Per-arm chunks (e.g., `dos__post_X.inc`) are only included
  when `BRANCH == "dos_1992"`. Their annotations only affect
  one port's assembly.
- Shared chunks (chapter chunks like
  `caves_inline_setters_and_init.inc`, helpers in `_helpers/`)
  are included by multiple `.asm.in` files across multiple
  ports. An annotation in a shared chunk is "redundant" only if
  EVERY consuming port's assembly still matches its baseline
  after the strip.

# Acceptance criteria

- [ ] Extend the audit/strip tools to operate at the
      `(.asm.in, port)` granularity. For each unified `.asm.in`
      and each port that consumes it, compute a baseline +
      stripped pair using the `verify_unified.py`
      preprocess+assemble pipeline.
- [ ] Bisect on chunk annotation rank, but verify the post-strip
      bytes against EVERY consuming port (not just one).
- [ ] Run the sweep across the unified tree.
- [ ] Update `docs/raw_annotation_load_bearing.md` with both
      per-branch and unified-chunk residue.
- [ ] Surviving load-bearing annotations should match (or
      strictly subset) the per-branch residue catalogued in
      issue #0083.

# Log

- 2026-05-04: opened. Follow-up to #0083 mass-strip.

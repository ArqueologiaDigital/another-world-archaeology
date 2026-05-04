---
id: 0084
title: Audit `;@raw=` annotations in unified chunks (per-(.asm.in, port) framework)
status: done
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

- [x] Extend the audit/strip tools to operate at the
      `(.asm.in, port)` granularity. For each unified `.asm.in`
      and each port that consumes it, compute a baseline +
      stripped pair using the `verify_unified.py`
      preprocess+assemble pipeline.
- [x] Bisect on chunk annotation rank, but verify the post-strip
      bytes against EVERY consuming port (not just one).
- [x] Run the sweep across the unified tree.
- [x] Update `docs/raw_annotation_load_bearing.md` with both
      per-branch and unified-chunk residue.
- [x] Surviving load-bearing annotations should match (or
      strictly subset) the per-branch residue catalogued in
      issue #0083.

# Log

- 2026-05-04: opened. Follow-up to #0083 mass-strip.
- 2026-05-04: done — covered by the per-arm strip
  (`tools/strip_redundant_raw_unified_chunks.py`,
  source-reconstruction commit `c522caf`) and the multi-port
  shared-chunk strip
  (`tools/strip_redundant_raw_unified_shared.py`,
  source-reconstruction commit `2c2dcd0`). Combined: 60,991 +
  632 = 61,623 redundant annotations stripped from unified
  chunks. Subsequent migration + literal-replacement +
  collision-rename sweeps brought the active source tree to 0
  `;@raw=` annotations (per #0083 closure).

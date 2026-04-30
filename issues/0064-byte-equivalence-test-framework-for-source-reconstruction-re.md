---
id: 0064
title: Byte-equivalence test framework for source-reconstruction repo (CI gate)
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [reconstruction, testing, build]
---

# Context

Cross-cutting infrastructure for the source-reconstruction repo.
Each `make TARGET=<slug>` build needs to verify byte-equivalence
against the reference dump in `another-world-archive/`.

The test framework should:

- Compare every produced artifact to its reference (md5 + diff).
- Run as a CI gate after every build.
- Report which artifacts match, which don't, and the byte-level
  diff for non-matches (with addresses if possible).
- NOT carry reference binaries in the source-reconstruction repo
  itself — they live in `another-world-archive/`.

# Acceptance criteria

- [ ] `tests/byte_equivalence.py` (or similar) that, given a
      target slug, verifies all produced files match the
      archive's reference.
- [ ] Hooked into the Makefile (`make test TARGET=<slug>`).
- [ ] First instance: passes for Phase 1 (DOS level-0 bytecode
      byte-matching).

# Log

- 2026-04-30: opened.

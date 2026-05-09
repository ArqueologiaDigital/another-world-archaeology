---
id: 0064
title: Byte-equivalence test framework for source-reconstruction repo (CI gate)
status: open
tier: C
created: 2026-04-30
updated: 2026-05-07
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

- [x] Hooked into the Makefile (aggregate `make test` rule landed
      in source-recon `c5346bd`; wraps `verify-stages` +
      `verify-unified` + `verify-all` + `lint`).
- [x] First instance: passes for Phase 1 (DOS level-0 bytecode
      byte-matching). Round-trip is now 29/29 stages + 27/27
      unified.
- [ ] Standalone `tests/byte_equivalence.py` driver that produces
      cleaner per-artifact PASS/FAIL output with byte-level diff
      on FAIL. The existing per-stage / per-port verifiers in
      `tools/` already cover the byte comparisons, so this is a
      thin aggregator + reporter.

# Log

- 2026-04-30: opened.

- 2026-05-05: partial. Added `make test` aggregate gate to the
  source-reconstruction Makefile (commit `c5346bd`). The new rule
  wraps the existing checks the project considers blocking:

      verify-stages   per-port .asm round-trip      (29/29)
      verify-unified  unified .asm.in round-trip    (27/27)
      verify-all      bytecode + raw resources × 5 ports
      lint            lint-raw + others

  Pre-commit / CI hooks can now invoke `make test` instead of
  knowing the full chain. Also added a `verify-unified` rule
  (the underlying script existed in archaeology but wasn't
  wired into the source-recon Makefile).

  Acceptance criteria status:
    - [x] Aggregate `make test` rule (✓ — invoked by CI)
    - [ ] `tests/byte_equivalence.py` standalone driver — not
          implemented yet; the existing per-stage / per-port
          verifiers in archaeology/tools/ already cover the
          byte-comparison work, so this would be a thin
          aggregator + reporter.
    - [x] Passes for Phase 1 — confirmed (verify-stages 29/29,
          verify-unified 27/27 already green).

  Remaining: write `tests/byte_equivalence.py` that produces
  cleaner per-artifact PASS/FAIL output with byte-level diff
  on FAIL.

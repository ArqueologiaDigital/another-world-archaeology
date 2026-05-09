---
id: 0064
title: Byte-equivalence test framework for source-reconstruction repo (CI gate)
status: done
tier: C
created: 2026-04-30
updated: 2026-05-09
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
- [x] Standalone `tests/byte_equivalence.py` driver that produces
      cleaner per-artifact PASS/FAIL output with byte-level diff
      on FAIL. *(Done — landed in source-reconstruction. Wraps
      verify-stages / verify-unified / verify-all / lint as
      subprocess calls, parses each tool's `TOTAL: ...` line, and
      aggregates into a single PASS/FAIL table. On FAIL, surfaces
      the underlying tool's diagnostic lines (FAIL markers,
      expected/got addresses, tracebacks). `--quick` flag skips
      the resource-heavy verify-all step, `--no-lint` skips lint.
      Verified: 3/4 checks pass on the current tree; verify-all
      surfaced a real pre-existing bug now tracked as #0094.)*

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

- 2026-05-09: closed `done`. `tests/byte_equivalence.py` shipped
  in source-reconstruction. Aggregator over verify-stages /
  verify-unified / verify-all / lint with structured PASS/FAIL
  + on-FAIL diagnostic surfacing. Side effect: surfaced a
  pre-existing infrastructure bug in `make verify-all` (stale
  `;@raw=` annotations in legacy tmp/output/<port>/disasm/ tree)
  now tracked as #0094 — that's a follow-up on the verifier
  inputs, not this issue.

---
id: 0094
title: make verify-all fails: tmp/output/<port>/disasm/ has stale ;@raw= annotations
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: []
blocks: []
tags: [reconstruction, testing, verify, raw-to-enc]
---

# Context

`make verify-all` (in source-reconstruction) invokes
`tools/roundtrip_bytecode.py` (in archaeology) which reads per-port
disasm files at
`tmp/output/<port>/disasm/level_N/<port>_level-N.asm` and
re-assembles them via `awvm-asm` to confirm byte-equivalence.

These tmp-output files predate the `;@raw=` → `;@enc=` migration
(see `docs/raw_to_enc_migration_plan.md`). `awvm-asm` was updated
in AWVM_Tools to reject `;@raw=` annotations:

```
asm.rs: `;@raw=` is no longer supported
(line: "\tcall LABEL_0DC6\t;@raw=0x04,0x0D,0xC6").
Use `;@enc=…` for named non-canonical encodings or a literal
operand value. See archaeology/docs/raw_to_enc_migration_plan.md.
```

Source-reconstruction's per-stage `.asm` files
(`src/levels/<branch>/<stage>.asm`) ARE migrated — `make verify-stages`
runs cleanly (29/29) and `make verify-unified` runs cleanly (27/27).
Only the legacy per-resource extraction tree under
`tmp/output/<port>/disasm/level_N/` is stale.

So `make test` aggregate gate fails on the `verify-all` step on
any checkout that hasn't re-run the per-port extraction since the
migration. Structural failure, not transient.

Reproduces from the new `tests/byte_equivalence.py` driver
(source-reconstruction):

```
$ python3 tests/byte_equivalence.py
verify-stages   per-port .asm round-trip            PASS
verify-unified  unified .asm.in round-trip          PASS
verify-all      bytecode + raw resources × 5 ports  FAIL
lint            source lint                         PASS

Failure detail:
=== verify-all ===
  Traceback (most recent call last):
  subprocess.CalledProcessError: Command [..., 'amiga_level-0.asm']
  returned non-zero exit status 101.

AGGREGATE: 3/4 checks passed.
```

# Acceptance criteria

- [ ] Decide canonical action: regenerate the legacy
      `tmp/output/<port>/disasm/` tree through the new
      `;@enc=`-emitting disassembler, OR retire `verify-all` /
      `roundtrip_bytecode.py` and fold its byte-equivalence
      checks into `verify-stages` / `verify-unified` (which
      already work on the migrated source).
- [ ] `make test` (and `python3 tests/byte_equivalence.py`)
      pass clean on a vanilla source-reconstruction checkout.

# Log

- 2026-05-09: opened. Surfaced while writing the
  `tests/byte_equivalence.py` driver for #0064 — the new
  driver correctly reports the failure, but it's a real
  infrastructure issue that predates this work.

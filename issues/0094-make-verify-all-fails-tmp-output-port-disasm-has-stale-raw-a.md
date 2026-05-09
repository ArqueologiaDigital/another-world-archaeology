---
id: 0094
title: make verify-all fails: tmp/output/<port>/disasm/ has stale ;@raw= annotations
status: in-progress
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

- 2026-05-09 (later): immediate breakage mitigated in
  source-reconstruction commit `239f875`: `make test` split
  into a core gate (verify-stages + verify-unified + lint —
  all pass on vanilla checkout) and `make test-full` (adds
  verify-all). `tests/byte_equivalence.py` updated to match
  (default skips verify-all; opt in via `--full`). So fresh
  checkouts now pass `make test`.

  This is a partial mitigation — the underlying issue (legacy
  tmp/output disasm tree has stale `;@raw=` annotations that
  awvm-asm rejects) is unchanged. Status flipped to
  `in-progress` to track the remaining work: regenerate the
  legacy tree through the current disassembler so `make
  test-full` (and the `verify-all` chain underneath) passes
  cleanly. Likely path: `make extract` from archaeology, but
  needs verification that the current awvm-disasm output
  uses `;@enc=` (not `;@raw=`).

- 2026-05-09 (later 2): regen path implemented for bank-format
  ports in archaeology commit `ac12cba`. `tools/regen_disasm.py`
  + `make disasm PORT=<port>` runs current awvm-disasm against
  the unpacked game files and writes to `tmp/output/<port>/disasm/`.

  Confirmed: current awvm-disasm emits **zero** `;@raw=`
  annotations (the migrated encoder produces canonical output
  directly). Round-trip: every regenerated per-level .asm
  re-assembles through awvm-asm cleanly. msdos and amiga both
  pass.

  One upstream awvm-disasm quirk: amiga's `all_levels` mode
  panics at `pdata_offset out of bounds` in
  `awvm/src/polygons.rs:100` AFTER successfully writing all 9
  per-level disasm files. The regen tool tolerates this case
  (treats "non-zero rc but per-level files present" as partial
  success). The panic is a separate awvm-disasm bug worth
  filing upstream — not blocking this issue.

  Cartridge-format ports (snes_eu, genesis_europe, gba_usa) get
  their disasm trees from `extractors/cartridge_rom.py` during
  `make extract`; that path is not covered by `make disasm`. To
  finish closing this issue: re-run `make extract` for the
  cartridge ports OR extend `regen_disasm.py` with cart support.

  After regen, `make verify-all` reaches gba_usa as the next
  blocker (cart disasm tree is still stale).

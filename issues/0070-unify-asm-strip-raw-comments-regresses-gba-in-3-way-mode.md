---
id: 0070
title: unify_asm: --strip-raw-comments regresses GBA in 3-way mode (2 bytes diff at offset 0x14)
status: open
tier: C
created: 2026-05-01
updated: 2026-05-01
depends_on: []
blocks: []
tags: [unify-asm, bug, phase-3b]
---

# Context

The 3-way LAKE unification (commit `ec44584` in archaeology)
byte-matches all 3 branches when run WITHOUT
`--strip-raw-comments`. With the flag enabled, GBA regresses by 2
bytes:

```
expected at 0x0014: 0x07
got at 0x0014:      0x3E
```

Cart and amiga still byte-match in stripped mode. Only GBA loses
2 bytes (probably a `bankSwitch` / `setPalette` / `video` line
where the encoder mis-handles the canonical case but the
`line_requires_raw` heuristic stripped the override.

Diff count drops from 2906 (non-stripped) to 2443 (stripped) — a
~16% reduction — but the byte regression makes stripped mode
unusable until the underlying mnemonic encoding is fixed (related
to issue #0066's awvm-asm encoding bugs).

# Reproduction

```bash
cd /home/fsanches/compartilhado/another-world-archaeology
LAKE_DIR=/tmp/lake_3way
python3 tools/unify_asm.py \
    --source heineman_cartridge=$LAKE_DIR/cart_canon.asm \
    --source foxy_gba_2004=$LAKE_DIR/gba_canon.asm \
    --source chahi_1991=$LAKE_DIR/amiga_canon.asm \
    --strip-raw-comments \
    -o $LAKE_DIR/CART_GBA_AMIGA_LAKE_stripped.asm.in
# Then preprocess + assemble for gba_usa flags.
```

# Acceptance criteria

- [ ] Identify the specific instruction at offset 0x14 (gba LAKE).
- [ ] Determine whether it's an awvm-asm encoding bug (extend #0066)
      or a bug in `unify_asm.py:line_requires_raw`.
- [ ] Fix the root cause OR add the offending mnemonic/case to
      `RAW_REQUIRED_MNEMONICS` until the encoder is fixed.
- [ ] `--strip-raw-comments` 3-way mode passes byte-match for all 3
      branches.

# Log

- 2026-05-01: opened. Found while validating 3-way LAKE
  unification.

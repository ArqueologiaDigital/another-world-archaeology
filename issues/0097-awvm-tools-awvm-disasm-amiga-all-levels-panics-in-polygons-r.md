---
id: 0097
title: AWVM_Tools awvm-disasm: amiga all_levels panics in polygons.rs:100 (pdata_offset out of bounds)
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: []
blocks: []
tags: [awvm-tools, bug, amiga, disasm]
---

# Context

Surfaced from the #0094 disasm-tree regen work. Filing in
archaeology rather than proposing directly to AWVM_Tools (per
CLAUDE.md: surface AWVM_Tools changes before implementation).

`awvm-disasm <input> all_levels amiga` against the amiga bank
files panics AFTER successfully writing all 9 per-level disasm
files:

```
$ awvm-disasm work/5dca377e0e1506d5cf83317b1495f3e8/bin all_levels amiga

=== amiga ===
Num. levels = 9
disassembling level 0...
        53 cinematic entries.
disassembling level 1...
        569 cinematic entries.
...
disassembling level 8...
        57 cinematic entries.

thread 'main' (43266) panicked at awvm/src/polygons.rs:100:14:
pdata_offset out of bounds
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
```

The crash happens AFTER level 8 is disassembled but during a
downstream step (likely common_video aggregation, which msdos
also runs but doesn't crash on). Per-level outputs are correct
and round-trip cleanly through `awvm-asm`, so the practical
impact is just the non-zero exit code.

`tools/regen_disasm.py` works around the issue by detecting
"non-zero rc but per-level files present" and treating it as
partial success.

# Reproduction

```bash
cd /tmp
mkdir test_amiga && cd test_amiga
~/compartilhado/AnotherWorld_VMTools/target/release/awvm-disasm \
  ~/compartilhado/another-world-archaeology/work/5dca377e0e1506d5cf83317b1495f3e8/bin \
  all_levels \
  amiga
echo $?  # 101
ls output/amiga/disasm/  # all 9 levels present
```

# Acceptance criteria

- [ ] AWVM_Tools owner triages: is this a real out-of-bounds bug
      in polygon-array indexing for amiga, or a known limitation
      (e.g. amiga doesn't have a common_video bank in the same
      shape as msdos)?
- [ ] If a real bug, fix `awvm/src/polygons.rs:100` so the bound
      check holds for amiga input.
- [ ] If a known limitation, make `all_levels` mode skip the
      offending step gracefully on amiga (or document the expected
      panic so wrappers like `regen_disasm.py` don't have to guess).

# Notes

The fact that all 9 per-level outputs round-trip cleanly through
`awvm-asm` strongly suggests the panic is in a non-essential
post-processing step — the disasm decoder itself is doing the
right thing for amiga. So this is probably a 1-2 line bound
check fix in polygons.rs.

# Log

- 2026-05-09: opened. Surfaced while writing
  `tools/regen_disasm.py` for #0094 (commit ac12cba). The regen
  tool tolerates the panic but the underlying bug should still
  be fixed upstream.

---
id: 0068
title: AWVM_Tools cartridge ports — extract cinematic.rom (currently inlined into bytecode.rom)
status: open
tier: A
created: 2026-05-01
updated: 2026-05-01
tags: [awvm-tools, proposal, extractor, cartridge, cinematic, gba, snes]
---

# Context

For all cartridge-style ports (`gba_usa`, `snes`, `genesis_europe`,
`symbian_demo`), `awvm-disasm` produces only a `bytecode.rom`
(plus the hardcoded `str_data.rom` / `str_index.rom` /
`anotherworld_chargen.rom`). It does **not** produce a
`cinematic.rom`, even though every cartridge ROM contains the
cinematic polygon data needed to render the game's video opcodes.

This was discovered while investigating GBA's INTRO byte-match
unification: 55 KB of "trailing data" inside GBA's `level_0`
chunk turned out to be 99 % of the level_0 cinematic-polygon
slab. The 100 % match (570/570 INTRO `CINEMATIC_xxx` addresses
land on valid polygon-entry bytes) confirms it.

The AWVM_Tools `CartridgeSpec` for `gba_usa` over-extracts:

```rust
"gba_usa" => prepare_cartridge_romset(
    ...
    bytecode_chunks: &[(0x6ea74, 0x10000), (0x813f8, 0x10000)],
    ...
),
```

It declares each level's bytecode is a full 64 KB. In practice
the actual bytecode is much shorter (`level_0` = ~9.9 KB,
`level_1` = ~21 KB), and the rest of each 64 KB region is the
adjacent cinematic data bleeding in. The current extractor
silently includes that cinematic data as "bytecode", which the
disassembler then either tries to decode (producing nonsense
instructions) or emits as `db <bytes>`.

## Findings

GBA ROM layout (verified, 100 % match):

```
0x6EA74  level_0 bytecode start    (~9.9 KB of real bytecode)
0x71126  level_0 last bytecode byte (killChannel at level-relative 0x26B2)
0x71127  1 byte separator/marker (0x0F)
0x71128  level_0 cinematic.rom slab start (64 KB)
0x81128  level_0 cinematic.rom slab end
0x81128  720 bytes — palette data?
0x813F8  level_1 bytecode start    (~21 KB of real bytecode)
0x86620  level_1 cinematic.rom slab start (64 KB; 100 % match too)
...
```

(Full GBA ROM is 2 MB; only `level_0` and `level_1` are spec'd in
AWVM_Tools, but the layout pattern repeats. There should be 8
levels of bytecode + cinematic.)

SNES ROM (`Another World (Europe).sfc`, 1 MB) has its level_0
cinematic data at offset `0x486E0` (95.1 % match — high enough to
confirm but suggests minor encoding quirks worth investigating).

# Acceptance criteria

- [ ] AWVM_Tools' `gba_usa` `CartridgeSpec` updated:
  - [ ] Trim `bytecode_chunks` to actual bytecode lengths
        (`level_0`: ~0x26B3, `level_1`: ~0x5228, etc.).
  - [ ] Add `cinematic_chunks: &[(0x71128, 0x10000), (0x86620, 0x10000), ...]`
        producing `cinematic.rom`.
  - [ ] Map all 8 levels (currently only 2 are spec'd).
- [ ] Same for `snes`, `genesis_europe`, `symbian_demo` — figure
      out per-port cinematic offsets.
- [ ] Verify by:
  - [ ] Decoding cinematic.rom with `awvm-tools` polygon decoder.
  - [ ] Comparing rendered SVGs against MSDOS / Amiga reference
        renders (semantic equivalence, not byte-identical).
- [ ] Update `cinematic.rom` MD5 placeholders in each release's
      `releases/<port>/<port>.rs` (currently `"?"` or `BAD_DUMP`).

# Why this matters (research ROI: tier A)

Cinematic polygon data is one of the four asset classes (alongside
bytecode, palettes, and string tables) that has to byte-match
across the cross-branch unification work in
`another-world-source-reconstruction`. Without separate
`cinematic.rom` files, each cartridge port's polygons are stuck
inside `bytecode.rom` (mis-classified as bytecode), and the
research/06 unused-polygon survey couldn't be re-run on these
ports.

It also unblocks visual rendering of cartridge-only animations
to compare them against Chahi-original Amiga / DOS art.

Discovery thread is in research/09 (Phase 3b unification). Owner
should review and decide whether this work happens in
AWVM_Tools or as a temporary archaeology-side extractor.

# Log

- 2026-05-01: opened — finding came out of GBA INTRO LABEL_26A6
  trailing-data investigation.

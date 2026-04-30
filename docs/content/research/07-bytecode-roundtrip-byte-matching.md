# 07 — Bytecode round-trip is byte-identical for 5 ports (29 levels)

**Date**: 2026-05-01.

## Question

Can we reconstruct the original AW VM bytecode resources from
their disassembled `.asm` form, byte-for-byte, for every cataloged
release we have disasm for?

A "yes" answer is the foundation for the
[source reconstruction project](https://github.com/felipesanches/another-world-source-reconstruction)
— it proves that the disassembler/assembler round-trip is
information-preserving, which means a unified `.asm` source tree
can produce byte-matching output for every port.

## Method

For each port × level:

1. Take the disassembled `<port>_level-N.asm` file (output of
   AWVM_Tools' `awvm-disasm`).
2. Run AWVM_Tools' `awvm-asm` on it.
3. The assembler always produces a 64-KB output (the AW VM's
   maximum bytecode segment size), padded with zeros after the
   meaningful end.
4. Compare:
   - For **resource-bin** format ports (DOS, Amiga, Atari ST):
     truncate the assembler output to the original resource's
     size; compare byte-by-byte.
   - For **cartridge** format ports (SNES, Genesis, GBA):
     compare the full 64-KB assembler output to the corresponding
     64-KB chunk of the cartridge's `bytecode.rom`.

The driver is at `tools/roundtrip_bytecode.py`; the
source-reconstruction repo invokes it via `make verify-all`.

## Result

**29/29 levels round-trip byte-identically across 5 ports.**

| Port | Levels | Format | Notes |
|---|---|---|---|
| **amiga**          | 9/9 | resource-bin | 1991 Chahi master |
| **msdos**          | 9/9 | resource-bin | 1992 Heineman |
| **genesis_europe** | 7/7 | cartridge (7×64KB chunks) | 1993 Heineman / Interplay |
| **snes_eu**        | 2/2 | cartridge (2 levels disasm only) | 1992 Heineman |
| **gba_usa**        | 2/2 | cartridge (2 levels disasm only) | 2004 Foxy fan port |

Per-level md5 of the 18 resource-bin levels (Amiga + DOS) and the
11 cartridge chunks (Genesis-EU + SNES-EU + GBA Foxy) all match
expected values exactly.

## Bonus finding: SNES-EU and Genesis-EU share cartridge ROM bytes

While running the round-trip for the cartridge ports, an
unexpected exact match surfaced:

```
SNES-EU level_1 chunk md5:    e24580ddb549b2a0f27502fb913b7339
Genesis-EU level_0 chunk md5: e24580ddb549b2a0f27502fb913b7339
```

These two **64-KB cartridge ROM chunks** are byte-identical —
the SNES-EU level-1 lake-stage chunk is, byte-for-byte, the
same data as the Genesis-EU level-0 lake-stage chunk. This
confirms [research finding 05](#/research/05-beetle-in-the-lake-stage)'s
SNES↔Genesis byte-identity finding at the strongest possible
level: not just the AW VM bytecode resource (which we already
knew matched), but the entire 64 KB of cartridge ROM that holds
that resource — including any padding.

This means Heineman's tooling for the Genesis-EU port produced
the cartridge chunks **bit-for-bit** from the same source data
he'd used for SNES-EU. Even though SNES = 65816 CPU and Genesis
= 68000 CPU (no shared instruction set), the AW VM bytecode is
CPU-independent, so the cartridge chunks are identical.

## Implications for source reconstruction

This is the **foundation for Phase 1** of the
[source-reconstruction project](https://github.com/felipesanches/another-world-source-reconstruction).
The reconstruction loop is now demonstrably:

1. User supplies original game files.
2. `awvm-disasm` extracts `.asm` files.
3. `awvm-asm` re-assembles `.asm` to byte-matching binaries.

What's still pending for **full** byte-matching builds (Phase 2):

- **Polygon resource builder** — the inverse of
  `tools/polygon_render.py`. Given an SVG / structured rep,
  emit AW polygon bytes.
- **Palette resource builder** — trivial; copy bytes verbatim.
- **Sound + music resources** — trivial; copy bytes verbatim.
- **Bank packing** — the DOS/Amiga banks (`memlist.bin` +
  `bank01..bank0d`) need a packer that produces byte-matching
  output.
- **Cartridge ROM packing** — for SNES/Genesis/GBA: assemble the
  cartridge ROM from its constituent .rom files (bytecode.rom,
  palettes.rom, etc.) at the right offsets with the right
  metadata.
- **Engine binary** — likely deferred, with the original engine
  binary copied as-is until the engine itself can be
  reconstructed from C source.

Phase 3 (unified source with conditional compilation flags)
becomes meaningful once Phase 2 reference builds exist for all
ports — only then can we identify divergences systematically and
flag them.

## What's not covered yet

- **Atari ST 1991** — gated on issue #0004 (memlist parser).
  Per [research/05](#/research/05-beetle-in-the-lake-stage),
  Atari ST shares Amiga's bytecode byte-identically, so once
  Atari ST .asm files are available, Phase 1 will trivially
  extend to it.
- **Apple IIgs 1993** — gated on WOZ extractor (issue #0014).
- **3DO**, **Mac**, **Mega-CD**, **Symbian**, **NDS**, **Apple II
  demake** — each has its own structural hurdles tracked in
  separate issues.

## Files referenced

- `tools/roundtrip_bytecode.py` — the round-trip driver.
- `another-world-source-reconstruction/Makefile` — `make verify`,
  `make verify-all` rules.
- `another-world-source-reconstruction/releases/<slug>.flags` —
  per-target flag values for the 5 operational ports.

## Changelog

- **2026-05-01** — initial finding. Phase 1 of the
  source-reconstruction project achieved for the 5 ports we have
  disasm for.

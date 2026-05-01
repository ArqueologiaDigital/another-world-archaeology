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
| **msdos**          | 9/9 | resource-bin | 1992 Delphine/Morais |
| **genesis_europe** | 7/7 | cartridge (7×64KB chunks) | 1993 Heineman / Interplay |
| **snes_eu**        | 2/2 | cartridge (2 levels disasm only) | 1992 Delphine/Morais |
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

This is the **foundation for the source-reconstruction project**.
The reconstruction loop is:

1. User supplies original game files.
2. `awvm-disasm` extracts `.asm` files + raw asset bins.
3. `awvm-asm` re-assembles `.asm` to byte-matching binaries.
4. Raw assets pass through verbatim, verified by md5.

### Companion: raw-asset md5 verification

`tools/verify_resources.py` does the analogous check for
**non-bytecode** resources. For each port, every extracted
`resource-0xNN.bin` (Amiga/DOS-style) or `<name>.rom`
(cartridge-style) is hashed and compared against a committed
manifest at `another-world-source-reconstruction/releases/<port>.resources.json`.

First run results:

| Port | Raw asset files |
|---|---|
| amiga | 151 |
| msdos | 153 |
| gba_usa | 4 (cartridge .rom files) |
| genesis_europe | 4 |
| snes_eu | 4 |

**316 raw asset files across 5 ports**, all md5-matched against
their reference manifests.

### Scope: packaging is OUT

Per the source-reconstruction project's 2026-05-01 scope
reduction, packaging is **out of scope**:

- No bank-packer (memlist.bin + bank01..bank0d).
- No ADF / cartridge ROM repacker.
- No engine binary reconstruction.

The project produces byte-matching SETS OF RESOURCES (bytecode +
raw assets), not byte-matching distribution packages. If you need
a runnable game, copy the produced resources back into your
original ADF/ROM/zip with an external tool of your choice.

### What's next: Phase 3 — unified source via conditional compilation

Now that bytecode + raw assets are byte-matched per-port, the
remaining research goal is to merge the per-port `.asm` files
into a unified source tree with conditional compilation flags.

Initial bytecode-equivalence map (md5 of `;@raw=` byte stream
per port × stage):

| Stage | Chahi 1991 | Delphine DOS | Heineman cartridge | Foxy GBA |
|---|---|---|---|---|
| CODE_WHEEL | `7b3b8d33…` | `5067870d…` | `d1490888…` (snes_eu only) | `94538fe7…` |
| INTRO       | `61f84573…` | `916bbdb9…` | (not present)             | (not present) |
| **LAKE**    | `e3bcc765…` | `8cf974ae…` | **`4a03b136…`** (snes + genesis BOTH) | `1649d466…` |
| PRISON      | `3e2583d1…` | `cc7922a4…` | `231d7999…` | (not present) |
| CAVES       | `73cbf0c2…` | `e6bd3630…` | `fae3b3ba…` | (not present) |
| TANK        | `dcfb2ff0…` | `4a16938f…` | `1cbb16da…` | (not present) |
| CAPSULE     | `9a9e8ae9…` | `41387ef9…` | `3c7d7e52…` | (not present) |
| ENDING      | `8d03b818…` | `520ae52f…` | `056606c6…` | (not present) |
| PASSCODE    | `db6ef401…` | `163e61de…` | `77071e34…` | (not present) |

**Only one byte-equality across the four branches**: SNES-EU LAKE
+ Genesis-EU LAKE share md5 `4a03b136…`. All other (branch, stage)
combinations have distinct bytecode.

### Phase 3a — Branch-organized canonical sources (✅ achieved 2026-05-01)

The source-reconstruction project's
[`src/levels/<branch>/<stage>.asm`](https://github.com/felipesanches/another-world-source-reconstruction/tree/main/src/levels)
tree organizes the .asm files **by genealogical branch and stage
name**, not by port slot.

`make verify-stages` reports
**29/29 (port, stage) byte-matches across 28 canonical .asm
files**:

| Branch | Source files | Targets |
|---|---|---|
| `chahi_1991` | 9 stages | amiga (atari_st when extractor lands) |
| `dos_1992` | 9 stages | msdos |
| `heineman_cartridge` | **8 stages** | snes_eu + genesis_europe (LAKE shared) |
| `foxy_gba_2004` | 2 stages | gba_usa |
| **Total** | **28 .asm** | **29 targets** |

The single inter-port unification surfaces concretely:
`heineman_cartridge/LAKE.asm` produces byte-identical output for
both SNES-EU level_1 and Genesis-EU level_0 — confirming
[research/05](#/research/05-beetle-in-the-lake-stage)'s
SNES↔Genesis byte-identity finding all the way through to a
shared source file in the build pipeline.

### ~~Phase 3b — Cross-branch conditional-compilation~~ (deferred)

The original Phase 3 plan was to merge *divergent* branches via
`#ifdef BYTECODE_BRANCH` in unified .asm files. After diffing the
per-port .asm files we find:

- Different number of labels (Amiga: 208 in level 0; DOS: 254)
- Different instruction counts and sequences
- Different polygon-resource layouts → different EQU offsets

A unified .asm would be 60-80% `#ifdef`'d code blocks — *harder*
to read than the branch-organized tree. **Phase 3b is deferred**
unless a concrete research need surfaces. Per-branch sources are
the honest representation of the genealogy.

Tracked as issue #0061 (closed as done with this scope).

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

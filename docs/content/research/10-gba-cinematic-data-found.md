# 10 — GBA `LABEL_26A6` mystery: 55 KB of "trailing data" is the level_0 cinematic.rom

**Date**: 2026-05-01.

## Question

The cartridge ↔ GBA INTRO unification (research/09) ended with 4
remaining `;@if` blocks. The largest by far was at `LABEL_26A6`:

```
LABEL_26A6:
    killChannel
;@if BRANCH == "cartridge_1992"
    FILL(55641, 0xFF)
;@elif BRANCH == "gba_2004"
    db 0x0F, 0xC6, 0x12, ...   ; 55,629 bytes of unknown data
    db ...
;@endif
```

Cartridge ports left their `level_0` chunk's trailing 55 KB as
`0xFF` padding (the 64 KB-chunk size minus the actual ~9.9 KB of
bytecode). GBA filled the same region with **non-padding bytes**.

The byte distribution looked polygon-like (low values dominant,
0xC0-range bytes scattered, 0x00 and 0x80 over-represented), but
without a confirmed mapping, "the bytes look like polygon data"
was speculation.

This investigation pinned it down.

## Method

The GBA disassembled INTRO source defines 570 `CINEMATIC_<NNN>`
labels with addresses in the cinematic-bank address space:

```
CINEMATIC_000   EQU 0xEB1C
CINEMATIC_001   EQU 0xEB34
CINEMATIC_002   EQU 0xEB4C
...
CINEMATIC_006   EQU 0x0404
...
```

These addresses are arguments to the `video` opcode and represent
byte offsets into `cinematic.rom` (one of the AW VM's standard
resource banks — same role across all ports).

The polygon decoder in
[`AnotherWorld_VMTools/awvm/src/polygons.rs`](https://github.com/felipesanches/AnotherWorld_VMTools/blob/master/awvm/src/polygons.rs)
spells out the polygon-entry format: the byte at each cinematic
address must be **either**

- `>= 0xC0` (a fill-polygon header, with the colour in the low 6
  bits), **or**
- have low 6 bits == `0x02` (a hierarchy-polygon header).

Random data has ~26 % chance of matching this constraint. So a
brute-force scan of the GBA ROM, looking for an offset where
**all 570** `CINEMATIC_xxx` addresses land on a valid polygon-entry
byte, is a clean signal/noise test.

Result: a single offset gives **570 / 570 = 100 %** match —
ROM offset `0x71128`, exactly **one byte after** the end of GBA's
`level_0` bytecode (which ends at offset `0x71126` with the
`killChannel` byte at `LABEL_26A6`).

## Layout

The GBA ROM (2 MB, `Another_world.gba`) has its INTRO data
organised as:

```
0x6EA74    level_0 bytecode start    (~9.9 KB of real bytecode)
0x71126    level_0 last byte of bytecode (killChannel at offset 0x26B2)
0x71127    1 byte separator/marker (0x0F)
0x71128    level_0 cinematic.rom slab start (64 KB)
0x81128    level_0 cinematic.rom slab end
0x81128    720 bytes (palette data candidate — looks like 16-colour
           tables of 2 bytes each, with a lot of 0x00 padding)
0x813F8    level_1 bytecode start    (~21 KB)
0x86620    level_1 cinematic.rom slab start (also 100 % match,
           660 / 660 cinematic addresses valid)
...
```

The pattern repeats per level. The full GBA ROM contains **all 8
stages' bytecode, cinematics, and palettes** in a fixed sequence
of `(bytecode | separator | cinematic | palette)` records.

So the 55 KB after `LABEL_26A6` is the **first 55 KB of GBA's
`level_0` cinematic-polygon slab**. The remaining 9.9 KB of the
slab spills past the `level_0` chunk boundary and lives in the
gap between the two `bytecode_chunks` regions that AWVM_Tools
declares for GBA.

## Validation

Manual hierarchical decoding of `CINEMATIC_006` (at
cinematic-rom offset `0x0404`):

```
header byte: 0x02         — HIERARCHY
center:      cx=128, cy=128
children:    2

  child[0]:  off=0x0014  ×2 → 0x0028, x=+209, y=+143
             byte at 0x0028: 0xC0 (FILL)  ✓
  child[1]:  off=0x000A  ×2 → 0x0014, x=+69,  y=+138
             byte at 0x0014: 0xC0 (FILL)  ✓
```

A small Python decoder ported from `polygons.rs` renders 7 sample
cinematics into SVGs without error:

| Address | Cinematic | Type | Output |
|---|---|---|---|
| `0x0404` | CINEMATIC_006 | hierarchy → 2 fills | [SVG](assets/research-10/CINEMATIC_006.svg) |
| `0x041C` | CINEMATIC_010 | hierarchy → 2 fills | [SVG](assets/research-10/CINEMATIC_010.svg) |
| `0x0460` | CINEMATIC_017 | hierarchy → 3 fills | [SVG](assets/research-10/CINEMATIC_017.svg) |
| `0x05B8` | CINEMATIC_032 | hierarchy → 17 fills | [SVG](assets/research-10/CINEMATIC_032.svg) |
| `0xEC10` | CINEMATIC_339 | hierarchy → 3 fills | [SVG](assets/research-10/CINEMATIC_339.svg) |
| `0xEC64` | CINEMATIC_340 | hierarchy → 1 fill | [SVG](assets/research-10/CINEMATIC_340.svg) |
| `0xED2C` | CINEMATIC_345 | hierarchy → 1 fill | [SVG](assets/research-10/CINEMATIC_345.svg) |

(Renderings use a synthetic rainbow palette since the real GBA
palette extraction isn't done yet — the shapes are real, the
colours are placeholder.)

## Why AWVM_Tools didn't catch this

The cartridge-port pipeline in
`awvm-tools/src/bin/awvm-disasm.rs`:

```rust
"gba_usa" => prepare_cartridge_romset(
    ...
    bytecode_chunks: &[(0x6ea74, 0x10000), (0x813f8, 0x10000)],
    ...
),
```

declares each level's `bytecode_chunks` entry as the **full 64 KB
slab**. For `snes` / `genesis_europe`, the entries are scoped
tighter (`(0x74A4C, 0x26A7)` etc.) so SNES's `bytecode.rom` ends
up correctly with just bytecode + 0xFF padding to 64 KB.

But the GBA spec captures the full 64 KB region — bytecode +
cinematic data — and labels all of it as bytecode. The
disassembler then either tries to decode the cinematic bytes as
instructions (producing nonsense `text id=0xVVVV` and similar
where `VVVV` is way out of range) or falls back to `db <bytes>`,
which is what we saw.

There's also no `cinematic.rom` produced for **any** cartridge
port — the cinematic resource id list is empty:

```rust
resource_ids: ResourceIds { bytecode: &[], cinematic: &[], palette: &[], video2: &[] },
```

so `awvm-tools` doesn't render polygons for these ports.

## SNES check

Same brute-force scan against the SNES `Another World (Europe).sfc`
ROM (1 MB) finds `level_0` cinematic data at ROM offset
`0x486E0`, with a **95.1 % match rate** (542 / 570 INTRO
cinematics resolve to valid polygon-entry bytes). The remaining
4.9 % are likely a quirk of the SNES encoding (different
multiplier, different per-level layout, or a few addresses that
genuinely don't point to standalone polygon entries) — worth a
deeper pass.

## Implications

1. **The unified-INTRO trailing `;@if` block ISN'T a bytecode
   divergence.** It's a *resource-class boundary*: cart's level_0
   bytecode chunk has 0xFF padding; GBA's same chunk happens to
   sit alongside cinematic data in the ROM, and the extractor
   pulled both into one file. After fixing the GBA extraction to
   produce a separate `cinematic.rom`, the `;@if FILL` block
   should disappear (both branches end their `bytecode.rom` with
   `killChannel + 0xFF padding` to 64 KB).

2. **GBA polygon assets are now in scope for unused-polygons
   research** (research/06). The same gallery + `n`-way
   reachability survey we ran on Amiga / MSDOS can be applied to
   GBA once `cinematic.rom` is extracted.

3. **Same recipe likely works for SNES / Genesis / Symbian.**
   Brute-force scan + format-validation gives a confident base
   offset; the per-port quirks are minor (95 %+ match rates).

## Next steps

Tracked as [issue #0068](#/issues): fix `awvm-tools`
cartridge-port extraction to produce a proper `cinematic.rom`
(and likely a `palettes.rom`) for GBA, SNES, Genesis, and
Symbian. Owner-review gate, since AWVM_Tools is upstream.

In the meantime, the archaeology-side `tools/redisasm_db.py`
keeps the `db` representation for these bytes — they'll
byte-match either way, and once the upstream extraction is
fixed, the trailing-padding `;@if` resolves automatically.

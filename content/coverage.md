# Format coverage

Status of extractors for each release format. An extractor takes a
release's package file (zip / ADF / ROM / PAK / .stx / .bin / .sis) and
produces a per-release `manifest.json` plus a tree of binary resources
and (where the format yields VM bytecode) diff-friendly disassembly.

## Status table

| Format | Status | Used by | Notes |
|---|---|---|---|
| `dos-bank` | ✅ implemented | `dos` | `memlist.bin` + `bank<NN>` files. `extractors/dos_bank.py`. Reference implementation. |
| `winxp-pak` | ✅ implemented | `winxp-1.1c` | Valve PAK format ("PACK" magic, 64-byte dir entries). Contents are DirectX shaders / BMPs / OGGs — *not* AW VM bytecode; the 1.1c remake is a different engine. Useful artifact, not a genealogy data point. |
| `amiga-adf` | ✅ implemented | `amiga-retro-presskit`, `amiga-archive-org` | OFS Amiga floppies; delegates to AWVM_Tools' `adf-extract` Rust binary. Handles the double-zipped retro-presskit layout. |
| `atari-st-pasti` | ✅ implemented | `atari-st-1991` | Pasti `.stx` → flat 720 KiB `.st` → FAT12 walk. Pure-Python in `extractors/atari_st_pasti.py`. |
| `snes-rom` | ✅ implemented | `snes-eu` (`snes-usa` blocked on fixture) | Cartridge ROM with hardcoded byte-chunk offsets. EU and USA share the same memory layout (alias dispatch). Shared `cartridge_rom.py` with region-aware target picker. |
| `genesis-rom` | ✅ implemented | `genesis-eu` | Cartridge ROM. Shared `cartridge_rom.py`. Text strings extracted from cartridge range `[0x382B, 0x46FE]`. |
| `gba-rom` | ✅ implemented | `gba-foxy-2004` | Cartridge ROM. Shared `cartridge_rom.py`. 2-level abridged engine (vs the 9-level full engine). |
| `3do-cue-bin` | ✅ implemented | `3do-1993` | CD-ROM Mode 1 + 3DO Opera filesystem. AWVM_Tools' `opera-list` Rust binary walks volume header + directory blocks (linked-list chaining via logical-block index relative to avatar start) recursively. Yields 423 on-disc files; mapping back to canonical AW resource indices is open research. |
| `nds-rom` | ✅ implemented | `nintendo-ds-alekmaul-2011` | Generic zip-unpack via `zip_unpack.py`. The .nds binary doesn't carry canonical AW resources — it loads user-supplied DOS files at runtime. |
| `apple-ii-demake` | ✅ implemented | `apple-ii-demake-weaver-2019` | Generic zip-unpack. Yields 3 DOS 3.3 .dsk floppy sides (the v3.1 release has 3 sides, not 2 as the upstream README suggests). Distinct engine from canonical AW. |
| `symbian-sis` | ⚠️ best-effort | `symbian-anotherworld-generic` | Best-effort zlib payload scan (`extractors/symbian_sis.py`). Yields a 3 KB metadata blob + a 948 KB EPOC E32 binary with LZMA1 chunks inside at offset `0x4B8`. Recovering AW VM resources from inside the E32 is future work. AWVM_Tools' locked-variant extractor (in `prepare_symbian_romset`) targets a different .sis layout. |
| `apple-iigs-2mg` | ⏵ stub | `apple-iigs-1992` | Two .woz disks archived. Needs **WOZ2 container parser + 3.5" GCR decoder (Apple IWM 8-and-3 GCR) + ProDOS volume walker**. WOZ2 disk metadata already confirmed: 3.5" / 2-sided / cleaned / Applesauce v1.46.1. See `extractors/apple_iigs_woz.py`. |
| `mac-classic` | ⏵ stub | `macintosh-1993` | One `.sit` archived. Needs **StuffIt .sit decompressor + MacBinary parser + 68k Mac resource-fork reader**. The AW VM resources live in the resource fork (inverse of every other AW format). See `extractors/mac_classic.py`. |
| `jaguar-rom` | n/a | `atari-jaguar-removers-2014` | No public dump exists. Acquiring this fixture will require a donor cartridge dump. |

## Extractor architecture

Every per-format extractor module lives in
[`extractors/<format>.py`](#) and exposes one function:

```python
def extract(release_meta: dict, archive_dir: Path, work_dir: Path) -> dict
```

- `release_meta` is the matching record from `metadata.json`.
- `archive_dir` is `original_files/<key>/` — a **read-only symlink**
  into the sibling archive repo. Extractors **never write into** it.
- `work_dir` is `work/<key>/` (gitignored, regenerable).

The dispatch table in `extractors/__init__.py` maps each format
string in `metadata.json` to the right extractor module.

The `cartridge_rom`, `amiga_adf`, `three_do_opera`, and `winxp_pak`
modules shell out to Rust binaries built from
[`AnotherWorld_VMTools`](https://github.com/felipesanches/AnotherWorld_VMTools).
Each binary handles its container format and (for cartridge ports +
DOS / Amiga bank format) the AWVM disassembler stage. The Python
glue copes with archive layout (zip-of-ADFs vs bare ADFs, Pasti
`.stx` decode, etc.).

## What "implemented" means

A format is considered **implemented** when:

1. `python3 extract.py --slug <slug>` produces resource binaries
   under `work/<key>/`.
2. A `manifest.json` is written listing every extracted file.
3. Re-running extraction yields byte-identical output (deterministic).
4. Where applicable, **`BYTECODE` resources can be passed to
   `awvm-disasm` and produce a parseable disassembly**.

The `dos-bank`, `amiga-adf`, `snes-rom`, `genesis-rom`, `gba-rom`
formats meet all four. `atari-st-pasti`, `3do-cue-bin`, `nds-rom`,
`apple-ii-demake`, `winxp-pak` meet 1–3 but not 4 (their formats
either don't carry AW VM bytecode or the bytecode-locating step is
open research).

## Stubs vs not-implemented

Two registered formats currently raise `NotImplementedError` with a
documented protocol breakdown rather than failing with "unknown
format":

- `apple-iigs-2mg` — see `extractors/apple_iigs_woz.py`
- `mac-classic`    — see `extractors/mac_classic.py`

A third format, `symbian-sis`, falls between best-effort and
implemented: it produces useful intermediate output (zlib payloads
extracted) but doesn't yet recover the AW VM resources nested
inside.

## Side findings worth turning into extractor work

Each row of the side-findings list in [Release catalog](#/catalog)
implies an extractor or a parallel slug. Notably:

- A clean **SNES USA** dump would let us validate SNES EU/USA chunk
  offsets are truly identical (only one half currently confirmed).
- A **Mac StuffIt** decoder would unlock the resource fork of the
  1993 Mac binary — the closest 68k-Mac sibling to the Anniversary
  engine codebase, and a high-value genealogy data point.
- A **WOZ + 3.5" GCR + ProDOS** chain would unlock the **Apple IIgs**
  port — Rebecca Heineman's only direct SNES-source transposition
  (same 65C816 CPU). Cross-validation against the SNES bytecode
  there would be a notable result.

## Cross-release resource sharing

When two releases produce a `BYTECODE` resource with the same md5,
the second extraction can skip disassembly and record a "shares
with `<other slug>`" pointer instead. Already observed in the wild:

- `amiga-retro-presskit` ↔ `amiga-archive-org` share **143 of 144
  resources byte-for-byte**; only `level-0 BYTECODE` differs in 13
  bytes (the codewheel-protection patch). See
  [Research finding 02](#/research/02-amiga-codewheel-protection).
- `atari-st-1991` BANK06 and BANK09 are byte-identical between the
  two floppies of the same release.

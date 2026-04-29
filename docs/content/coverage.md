# Format coverage

Status of extractors for each release format. An extractor takes a
release's package file (zip / ADF / ROM / PAK) and produces:
individual binary resources, a per-release `manifest.json` with each
resource's md5, and (where applicable) a tree of disassembled,
diff-friendly text.

| Format | Status | Used by | Notes |
|---|---|---|---|
| `dos-bank` | implemented | `dos` | `memlist.bin` + `bank<NN>` files; LZ-style decoder for compressed entries. Reference: `init.py` (will move to `extractors/dos_bank.py`). |
| `winxp-pak` | not implemented | `winxp-1.1c` | Resources inside `Data/Pak01.pak`. Format unverified — may be Valve-style or a custom bundle. |
| `amiga-adf` | not implemented | `amiga-retro-presskit` | Floppy disk images (`AnotherWorld_DiskA_nologo_noprotec.adf`, `…DiskB…`). Standard OFS/FFS, but the in-disk layout of the game's banks needs investigation. |
| `snes-rom` | not implemented | `snes-eu` | Bare cartridge ROM. No standard layout — needs reverse engineering. |
| `genesis-rom` | not implemented | `genesis-eu` | Bare cartridge ROM. Different memory map from SNES. |

## What "implemented" means

A format is considered implemented when:

1. `make extract SLUG=<slug>` produces resource binaries under the
   release's working directory.
2. A `manifest.json` is written with the md5 of every extracted
   resource.
3. Re-running extraction from the cached original yields
   byte-identical outputs (deterministic).
4. `BYTECODE` resources can be passed to `awvm-disasm` and produce a
   parseable disassembly.

## Cross-release resource sharing

When two releases produce a `BYTECODE` resource with the same md5,
the second extraction skips disassembly and records a "shares with
&lt;other slug&gt;" pointer instead. This both saves work and surfaces
genealogy signal automatically.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

This is a **research/archaeology project**, not a piece of software with users. The goal is to catalog every release/port of Eric Chahi's *Another World* (a.k.a. *Out of This World*), extract their assets, and use comparative analysis to reconstruct a "genealogy" of the codebase — which port introduced which feature or bug.

Methodology is modeled on MAME's approach to ROM preservation: original game files are identified and tracked by checksum.

## Important repository conventions

- **Never commit original game files in this repo.** The archaeology repo only stores metadata (filename, checksum, asset type, provenance URL/date) and the code that extracts assets from the various release formats.
- **`original_files/` is a symlink to a separate sibling repo.** The actual archive lives at `../another-world-archive/` — its own git repository, dedicated to storing release fixtures so they survive any deletion of this repo's working tree. The symlink at `original_files/` makes the existing `original_files/<slug>/...` paths work transparently. New fixtures are committed in the *archive* repo, not here. Do not replace the symlink with a directory.
- **Permanent archive — deletion is absolutely forbidden.** Once a file lands in `another-world-archive/`, it stays. `make clean` and other workflow targets must never touch the archive. Old fixtures are preserved even after better dumps are obtained — they serve as evidence of provenance and as comparison material for genealogy investigations.
- **Provenance is part of the data.** Every entry in `metadata.json` should include the download URL, download date, and ideally a Wayback Machine archive URL for that source. If you add a release, preserve this discipline.
- **Two-level checksumming.** md5 is used at both the package level (the release file as distributed, e.g. the zip) and the individual extracted resource level. The per-release working directory is named after the package md5.
- **External tool dependency: AnotherWorld_VMTools** (https://github.com/felipesanches/AnotherWorld_VMTools). The owner's `ExecTrace` fork in that repo is the bytecode disassembler. It is *not* vendored here; cloning it is part of setup. **Do not propose changes to AWVM_Tools without surfacing the proposal first** — the owner wants to review modifications to that tool before implementation.
- **The `issues/` directory is the canonical issue tracker.** One file per issue, frontmatter-typed, validated by `tools/issues.py validate`. **Strict policy:** every loose end identified during a session must become an issue before the conversation moves on; no "I'll remember this later" — TaskList is session-local, memory is for behavioural guidance, only commits are durable. Closing an issue means flipping its `status:` to `done` and adding a Log entry referencing the resolving commit. Issues are never deleted; wrong-direction work is closed `wontfix` with a reason. Run `python3 tools/issues.py index` whenever issue files change so the auto-generated `issues/README.md` stays in sync. See `issues/SCHEMA.md` for the full schema and policies.

## Architecture

### Per-release layout

Every cataloged release gets a working directory named by its package md5sum (e.g. `076117919d1dca51e486f33b8f7817e3/`) with three subdirectories:

- `original/` — the unpacked source release (zip extracted, ADF mounted, etc.)
- `bin/` — individual resources extracted from the release's bank/pak/ROM, named `0x<index>-<TYPE>.bin`
- `disasm/` — disassembled bytecode (target output; not yet wired up in `init.py`)

The intent is that each release ends up with a parallel tree of regenerated, source-like artifacts (disassembled bytecode, polygon data, palettes, etc.) so trees can be diffed across releases.

### `init.py` — the only extractor today

`init.py` currently handles only the **DOS-style bank format** (`memlist.bin` + `bank01..bankNN`). Other release formats listed in `metadata.json` (Windows `.pak`, Amiga `.adf`, SNES/Genesis cartridge ROMs, Atari ST, Apple IIgs, etc.) **are not yet implemented** — `metadata.json` lists them with `note` fields describing what still needs to be reverse-engineered.

Key pieces in `init.py`:

- `ResourceType` enum: `SOUND`, `MUSIC`, `POLY_ANIM`, `PALETTE`, `BYTECODE`, `POLY_CINEMATIC`, `UNKNOWN` — these come from the original engine and are stable across DOS-format releases.
- `read_mem_entries(path)` parses `memlist.bin` into a list of resource descriptors (bankId, bankOffset, packedSize, size, type).
- `Bank.read(entry)` reads a resource from `bank<bankId>`. If `packedSize == size` it's stored raw; otherwise `Bank.unpack()` decompresses it. The unpack routine is a port of the well-known fbBeRoFiel-style LZ-ish decoder used by the original engine — bit stream is consumed *backwards* from the end of the buffer (`_iBuf` decrements; `_oBuf` decrements). If you touch this, preserve the backwards semantics.
- The script's `try/except: print("FAILED")` at the bottom swallows extraction errors per release — this is intentional during cataloging (a new format failing shouldn't abort the whole run), but means a silent "FAILED" is the only signal. When debugging extraction, comment out the `try`/`except` to see the real traceback.

### What's missing / TODOs called out in the source

- `init.py:get_files` has TODOs for downloading missing files from `metadata.json["download"]`, verifying md5, and warning on mismatch. Not implemented.
- `init.py:171-194` has TODOs for actually creating the per-release directory tree, copying originals into it, and invoking the bytecode disassembler. The script currently assumes the directories and `original/` contents already exist.
- The `initial_research_plan.txt` calls for a centralized **Makefile** that fetches → extracts → disassembles for all releases. **Not yet written.** When asked to "run extraction," check whether a Makefile now exists; if not, the only working entry point is `python3 init.py` (DOS-format only).
- `metadata.json` has a JSON syntax error at the SNES entry (missing comma after the `download` line, line 31). Anyone parsing it programmatically will need to fix that first.

## Running things

There is no build system, no tests, no lint config. The whole codebase is currently `init.py` plus `metadata.json`.

```bash
python3 init.py        # extracts DOS-format releases whose package is already in original_files/<md5>/
```

For new format support, add an extractor module and wire it into the dispatch in `init.py`. Don't try to shoehorn non-DOS formats through the existing `Bank` class — they need their own readers (ADF parsing, PAK parsing, ROM bank decoding, etc.).

## Working with the owner

- The repo owner (Felipe Sanches) treats this as an open-ended research collaboration. Research questions will arrive as natural-language asks (see `initial_research_plan.txt` for the first one: how the gun's ammo/shot counter works in the bytecode). Expect comparative-analysis questions across releases.
- When a research question arrives, the answer usually requires extracting the relevant release, locating the right `BYTECODE` resource, disassembling it via AWVM_Tools, and reading the disassembly. Cite specific resource indices and bytecode offsets when reporting findings.
- Surface methodology gaps when you find them — the owner explicitly invited this.

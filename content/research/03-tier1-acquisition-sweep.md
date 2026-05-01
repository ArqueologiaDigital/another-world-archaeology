# 03 — Tier 1 acquisition sweep results (2026-04-30)

## Context

When the catalog hit 29 documented release variants, only 8 were
locally archived. This was the first systematic push to fetch the
remaining 21, prioritised by the
[acquisition plan](#/acquisition_plan): tier 1 = publicly
redistributable downloads (classic-platform romdumps + fan ports);
tier 2 = commercial digital we'd own and extract; tier 3 = physical-
only.

## Results

**Coverage went from 8/29 → 14/29 archived.** 12 of the 14 archived
fixtures now extract end-to-end via `python3 extract.py --slug X`;
2 are registered as informative stubs awaiting protocol work.

### Fetched (6 new fixtures)

| Slug | Source | md5 | Notes |
|---|---|---|---|
| `apple-iigs-1992` | archive.org / `wozaday_Out_of_this_World_IIgs` (4am) | per-disk md5 + sha1 verified | Two `.woz` flux-level disks, ~1.27 MB each. WOZ2 / 3.5" / 2-sided / cleaned. |
| `macintosh-1993` | macintoshgarden.org → old.mac.gdn | `411cfe55f7c43c7d846fcb2f24adeddb` | 3,739,614-byte StuffIt; bundles v1.0 + v1.2 + v1.3 with updaters. |
| `nintendo-ds-alekmaul-2011` | Wayback 2023-05-15 of filetrip.net | `a819d702799090b198a887e458703517` | Original mirror is dead in 2026; Wayback is now the canonical source. |
| `gba-foxy-2004` | github.com/OpenEmu/OpenEmu-Update | `9cef2ca9fba8a4532629f8c7e7c9ddf8` | 2,010,358 bytes. Author's own hosts (foxysofts.com, playerAdvance.org) are defunct. |
| `apple-ii-demake-weaver-2019` | author's own deater.net | `e78aeb4a0401998eac9f34c0b01132a3` | v3.1 (2021-05-01). Has **3 disk sides**, not 2 as upstream README implies. |
| `symbian-anotherworld-generic` | mobiles24.co (uploaded 2008-11-19) | `a0012563536c4baaa6487031e00d7b0f` | 753,982 bytes. **Confirmed distinct** from the locked variant (md5 `fe4742b67415eb16ef340548573538b8`). |

### Confirmed gaps (2)

- **`snes-usa`** — survey of archive.org turned up only a Fast-ROM+SRAM
  hack and a 687 MB bundled `snes100.zip` with no separable per-file
  checksums. Recommendation: source the No-Intro DAT-listed pristine
  cart from elsewhere and verify by md5 before archiving.
- **`atari-jaguar-removers-2014`** — confirmed *no public ROM dump
  exists*. Sole legitimate source is The Removers' commercial
  pre-order page; Atarimania lists Dump status as MISSING. Acquiring
  will require a donor cartridge.

### Side findings (candidate parallel slugs)

The acquisition push surfaced 9 additional release variants that
should have their own metadata entries when fetched:

- **European Apple IIgs** — `e2gs_Out_of_this_World_Disk_1` /
  `_Disk_2` on archive.org (smaller `.po` images, no per-file
  checksums recorded by uploader)
- **Mac v1.0-only** — `Out_of_this_World_1.0.mar` (Disk Copy 4.2
  image of just version 1.0, on the same Macintosh Garden page)
- **Mac demo** — `OutofthisWorldDemo.sit` (same page)
- **Hidden Palace SNES prototype** — Sep 1992 build, separate from
  the released cart
- **mobiles24 Symbian sibling listing 110775** — 752,492 bytes,
  distinct from the 753,982-byte one we already have
- **Telcogames v1.25** — SyMPDA-cracked Symbian SIS, bundled inside
  `Nokia_Games_Ultimate_SIS_Pack.zip` on archive.org
- **Symbian v1.36** — inside `club-60-part-1-1-300` RAR collections
  on archive.org
- **Symbian UIQ2** — Sony Ericsson P800/P900 port, distinct platform
  from S60
- **Older Apple II demake versions** — pre-v3.1 in the upstream git
  history

All recorded in `metadata.json` notes for follow-up acquisition.

## Methodology notes

This was the first session to make heavy use of parallel research
agents — three subagents ran concurrently (one for classic ROMs,
one for homebrew ports, one for the Symbian SIS hunt). The agents
returned structured candidate URLs which were then verified by HEAD
request and compared against the strict-archive policies before
fetching.

A subagent's claim is not a fact. Two minor agent corrections during
verification:

- One agent attributed the Apple II demake to "Roger Weaver / 4am" —
  actually **Vince Weaver (deater)**, which the existing metadata
  already had right.
- Atari Jaguar release year was reported as 2013 with sources varying
  to 2015; we kept the existing slug `-2014` for stability and noted
  the discrepancy in the metadata note.

29 source URLs from this push were appended to
[`references/sources.csv`](#) for the next batch Wayback Save Page
Now run.

## Three more extractors landed in the same session

Stitching the new fixtures into the dispatch:

- **`cartridge_rom`** — unified extractor for SNES / Genesis / GBA.
  Region-aware (EU vs USA). Replaces the snes_rom + genesis_rom
  stubs.
- **`zip_unpack`** — generic zip-unpack for releases whose payload
  doesn't fit a richer format yet. Wired up for `nds-rom` and
  `apple-ii-demake`.
- **`symbian_sis`** — best-effort zlib payload scan. Yields the
  inner EPOC E32 binary which itself contains LZMA1 chunks (matching
  the locked-variant nested format).
- **`amiga_adf`** — was a stub, now real (`adf-extract` Rust binary
  delegate).

## Forward implications

- The remaining 15 unfetched slugs are **mostly tier 2** (Anniversary
  editions, owner-purchase-then-extract). The PC ones (GOG, Steam)
  are the cheap entry; console editions need per-platform CFW dumping
  rigs.
- The Mac StuffIt route is the **highest-value remaining tier 1
  protocol-work item** — the 1993 Mac port's resource fork is the
  closest 68k-Mac sibling to the Anniversary engine codebase.
- The Apple IIgs WOZ route is the **highest-value cross-CPU
  comparison opportunity**: Rebecca Heineman's only direct
  SNES-source transposition (same 65C816), so cross-validation
  against the already-extracted SNES bytecode would be a strong
  genealogy result.

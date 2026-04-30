# Forward plan (2026-04-30)

The state of the project at the end of the current session is the
baseline this plan starts from. The acquisition + extractor work has
gone roughly an order of magnitude beyond the original
`initial_research_plan.txt` scope — coverage is now broad enough that
the next round of work can shift from *infrastructure* to *research
and analysis*.

## Where we are

- **Catalog:** 29 release variants documented in `metadata.json`.
- **Archive:** **14 of 29 fixtures** in `another-world-archive/`
  (~410 MB).
- **Extractors:** **13 of 14 archived fixtures extract end-to-end**;
  1 stub (Apple IIgs WOZ).
- **Round-trip parity:** confirmed byte-identical disasm + reassembly
  for `dos`, `amiga` (both retro-presskit and archive-org), `snes-eu`,
  `genesis-eu`, `gba-foxy-2004`. SNES USA aliased.
- **Comparative findings landed:** Amiga codewheel-protection patch
  (research finding 02), Tier 1 acquisition sweep summary (finding 03).
- **Open research questions:** gun ammo (#01) — investigation in
  flight in a parallel agent at the time of writing.

## Forward work, ranked

### Tier A — Highest research ROI (do next)

These build on what we already have and would unlock concrete
genealogy results.

1. **Mac resource-fork walker.** The `mac-stuffit-extract` binary
   yields three .rsrc blobs (v1.0 / v1.0.2 / v1.0.3) totaling ~1.6 MB
   of 68k Mac code + AW VM resources. Adding a `MacBinary`-using
   resource-fork walker would surface individual TYPE+ID-keyed Mac
   resources (likely `BANK`, `POLY`, plus engine code in `CODE` /
   `DATA` / `SIZE` etc.). The `macbinary` crate is already in the
   AWVM_Tools workspace deps. Output: per-resource binaries indexed
   by `(TYPE, ID)`, plus a 68k-binary version of the engine code
   that becomes the closest 68k-Mac sibling to the Anniversary
   editions for genealogy.

2. **Mac v1.0 vs v1.0.2 vs v1.0.3 binary diff.** Once (1) is done,
   diff the three Mac builds — three close versions of the same
   port give a high-density signal about what the patches actually
   changed (bug fixes? feature additions? localisation?). Per the
   strict "compare ALL assets" policy, do this at the per-resource
   md5 level, not just on the engine binary.

3. **3DO file ↔ canonical AW resource index mapping.** The
   `three_do_opera` extractor yields 423 on-disc files including
   `GameData/FileN`, `GameData/song1..30`, `GameData/EndShape1/2`.
   These almost certainly map onto canonical AW resource indices
   (BYTECODE / POLY_ANIM / POLY_CINEMATIC / SOUND / MUSIC / PALETTE)
   but the mapping isn't yet established. Pull a sample resource of
   each type and identify the format → register a 3do release in
   AWVM_Tools' `releases/` so disasm works on the on-disc bytecode.

4. **Atari ST embedded memlist parse.** The Atari ST 1991 extractor
   yields `BANK01..BANK0D` files but no `memlist.bin` — the directory
   is embedded inside `START.PRG`. Parse `START.PRG` to recover the
   memlist, then run the bank-format pipeline against the Atari ST
   banks. Compare result to the Amiga banks; the two share the
   68000 engine generation, so non-trivial differences are
   first-order genealogy signal.

5. **Resolve the gun-ammo question.** The agent currently running
   should produce a finding (research/01-gun-ammo.md). Once it lands,
   cross-validate the finding across all releases that already
   disassemble (DOS / Amiga / Genesis / GBA / SNES) — variation
   across versions is genealogy gold.

### Tier B — Format work that unlocks more comparisons

These need substantial protocol implementation but each unlocks a
significant cross-platform comparison.

6. **Apple IIgs WOZ → ProDOS.** The two .woz disks are flux-level
   preserved by 4am. Implementing WOZ2 + 3.5" GCR (Apple IWM
   8-and-3) + ProDOS would unlock the IIgs port — Rebecca
   Heineman's only direct SNES-source transposition (same 65C816
   CPU). Cross-validating the IIgs bytecode against the SNES port
   would be a strong genealogy result. ~500–800 lines of code.

7. **Symbian SIS → AW VM resources.** The `symbian-anotherworld-generic`
   extractor surfaces the inner EPOC E32 binary plus its LZMA1 chunks,
   but the AW VM bytecode itself is still nested inside that. Walk
   the LZMA1 chunks, mirror `prepare_symbian_romset` from AWVM_Tools'
   locked-variant pipeline, and produce extracted bytecode +
   diff-friendly disasm.

8. **Sega CD: `mega-cd-heart-of-alien-1994`.** Acquire the redump-grade
   `.bin` + `.cue` (multiple mirrors documented), implement the CD-ROM
   filesystem + bank extractor for the Sega CD layout. Tie it to the
   already-archived `genesis-eu` for an OOTW-vs-OOTW comparison and
   surface the *sequel* (Heart of the Alien) as a separate VM
   investigation — ostensibly using the same engine but with new
   stages.

### Tier C — Acquisition sweep round 2

The remaining slugs in `metadata.json` we haven't archived yet.

9. **Tier 2 acquisitions** (Anniversary editions): the project owner
   gates these on storefront accounts.
   - **PC**: GOG (DRM-free, highest analyzability) and Steam are the
     cheap entry; Android APK via APKMirror or `adb backup`.
   - **Console**: each requires console-specific CFW dumping (3DS:
     GodMode9; Wii U: NUSspli; Switch: Atmosphere+nxdumptool; PS3:
     IRISMAN; Vita: VitaShell; PS4: GoldHEN). Defer until a user
     has hardware ready.

10. **Tier 1 follow-ups confirmed at 2026-04-30 but not yet
    fetched.** Convert the side findings into actual fetches:
    - European Apple IIgs (`e2gs_Out_of_this_World_Disk_1` /
      `_Disk_2` on archive.org)
    - Mac v1.0-only (`Out_of_this_World_1.0.mar` on Macintosh Garden)
    - Mac demo (`OutofthisWorldDemo.sit`)
    - Hidden Palace SNES prototype (Sep 1992 build)
    - mobiles24 Symbian sibling (listing 110775)
    - Telcogames v1.25 SyMPDA-cracked SIS (extract from
      `Nokia_Games_Ultimate_SIS_Pack.zip`)
    - Symbian v1.36 (in `club-60-part-1-1-300` RAR)
    - Symbian UIQ2 (Sony Ericsson P800/P900) port
    - Older Apple II demake versions (`dos33fsprogs` git history)

11. **Confirmed-gap acquisitions.** Two known fixtures that
    require external action:
    - `snes-usa` — needs a No-Intro DAT-listed pristine cart
      (probably acquired from a NDS/cart dumper or No-Intro torrent)
    - `atari-jaguar-removers-2014` — needs a donor cartridge dump,
      since no public ROM exists

### Tier D — Site & infrastructure

12. **Wayback batch.** 144 URLs in `references/sources.csv`; ~half
    don't yet have Wayback snapshots. Run a Save Page Now batch via
    the Google Sheet importer; populate the `wayback` column.

13. **Per-release page generation.** The static doc site currently
    has one big catalog page. Generate one page per release from
    `metadata.json` so each can carry its own running findings log.

14. **Cross-resource md5 index.** Build a `manifest.json`-aggregating
    tool that, across every extracted release, identifies BYTECODE
    resources sharing an md5. The Amiga codewheel-protection finding
    (research 02) was found this way by hand; automation makes this
    available for every comparison pair.

## What's not on this list

- **Engine source-code repo.** This project is a research artefact,
  not a re-engineered engine. We catalog and compare; we do not
  rewrite. (See the explicit non-goal in `CLAUDE.md`.)
- **Distribution of fixtures.** The local archive is local. We never
  distribute original game files, only metadata + the code that
  works on them.

## Update cadence for this page

This document is meant to evolve with the project. After any major
session that completes one of the items above (or surfaces a new
priority), update this file in-place and add a `## Changelog` entry
at the bottom.

## Changelog

- **2026-04-30** — initial draft, written at the end of the Tier 1
  acquisition + extractor sweep session. 14/29 archived, 13/14
  extracting. Gun-ammo agent in flight.

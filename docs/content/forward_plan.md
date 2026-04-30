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
- **Comparative findings landed:** gun ammo (research finding 01),
  Amiga codewheel-protection patch (02), Tier 1 acquisition sweep
  summary (03), Mac patch chain v1.0 → v1.0.2 → v1.0.3 (04).
- **Open research questions:** none currently active in the
  open-questions queue.

## Forward work, ranked

### Tier A — Highest research ROI (do next)

These build on what we already have and would unlock concrete
genealogy results.

1. ~~**Mac resource-fork walker.**~~ ✅ Done 2026-04-30 —
   `mac-rsrc-walk` binary in AWVM_Tools, wired into
   `extractors/mac_classic.py`. End-to-end yields 1697 per-resource
   blobs across 50 forks.

2. ~~**Mac v1.0 vs v1.0.2 vs v1.0.3 binary diff.**~~ ✅ Done
   2026-04-30 — see [research finding 04](#/research/04-mac-port-patch-chain).

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

5. **Cross-validate gun-ammo finding (#01) on more releases.** The
   2026-04-30 finding established that DOS / Amiga / Genesis-EU
   share the gun mechanic byte-for-byte. SNES-EU and GBA-Foxy
   disassemblies are currently limited to levels 0/1 by the
   AWVM_Tools pipeline (those ports use the abridged 2-level "demo"
   engine), so cross-checking the prison/cave levels there is open
   work. Apple IIgs disassembly will follow once tier B item 6
   lands.

6. **Map second recharge-zone scene flag to game location.** The
   gun-ammo finding (#01) shows two recharge zones in level 4
   sharing one handler `LABEL_3473`, parameterised by `HACK_VAR_67`:
   the default scene fires on `X ≤ 103` (any Y), the alternate scene
   `HACK_VAR_67 == 0x4F` requires `X ≤ 110 && Y ≤ 100`. The
   default-scene one matches the walkthrough's "strange looking
   room". The alternate-scene one's in-game location needs to be
   identified — it's somewhere later in level 4. (Spotted by the
   project owner during review of finding 01; resolution pending
   their answer.)

7. **Investigate `Estr` 192-entry resource type in the Mac port.**
   The 1993 Mac port's resource fork has exactly 192 `Estr`
   resources totalling 6,114 bytes, byte-stable across all three
   build versions. 192 doesn't match the canonical 144 AW resource
   indices, but is suspicious. Could be event/error strings, or a
   different indexing scheme. A trivial cross-version diff would
   confirm whether any string changed across the patch chain.

8. **68k disassembler for Mac CODE segments.** The Mac patch-chain
   finding (research/04) identified WHICH segments changed across
   v1.0 / 1.0.2 / 1.0.3 by md5 alone, but doesn't tell us *what*
   changed. A 68k disassembler against the v1.0 vs v1.0.2 CODE 2 /
   3 / 5 deltas would surface the actual bug-fix pattern. Confirms
   or refutes the hypothesis that v1.0.3's `MacTraps2_ANSI`
   replacement segment is a Symantec C runtime upgrade.

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
- **2026-04-30** (later that day) — gun-ammo finding (#01) landed +
  corrected; Mac resource-fork walker (tier A 1+2) landed; finding
  #04 published. Reranked tier A: items 1+2 marked done; new items
  6 (locate alternate recharge-zone scene), 7 (`Estr` 192-entry
  investigation), 8 (68k disassembler for Mac CODE deltas) added
  to the active list.

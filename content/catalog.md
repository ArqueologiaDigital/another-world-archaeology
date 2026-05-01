# Release catalog

The full list of *Another World* / *Out of This World* release variants
the project has identified, ordered roughly by historical release.
Each entry mirrors a record in [`metadata.json`](#) (the authoritative
source) plus narrative context this page can hold and the JSON can't.

**Locally archived** = a copy of the original release file is stored
in the sibling [`another-world-archive`](#) repo (accessed transparently
via the `original_files/` symlink in this repo). The archive is
**permanent** — files are never deleted, even after a better dump
supersedes them, since they serve as evidence of provenance and as
genealogy comparison material.

**Documented** = present in `metadata.json` with provenance metadata,
even if the archive is empty so far.

**Extractor** = whether `python3 extract.py --slug <slug>` produces
useful output today. ✓ = end-to-end working; ⏵ = registered but raises
NotImplementedError with a documented protocol-work TODO; — = no
fixture archived yet so extraction is not attempted.

## Status table — 14 archived, 12 extracting, 15 pending

| Slug | Platform | Year | URL | Archived | Extractor |
|---|---|---|---|---|---|
| `dos` | MS-DOS | 1992 | yes | yes | ✓ `dos-bank` |
| `winxp-1.1c` | Windows XP | (later) | yes | yes | ✓ `winxp-pak` |
| `amiga-retro-presskit` | Amiga (OCS) | 1991 | yes | yes | ✓ `amiga-adf` |
| `amiga-archive-org` | Amiga (OCS) | 1991 | yes | yes | ✓ `amiga-adf` |
| `atari-st-1991` | Atari ST/STE | 1991 | yes | yes | ✓ `atari-st-pasti` |
| `snes-eu` | SNES (Europe) | 1992 | yes | yes | ✓ `snes-rom` |
| `snes-usa` | SNES (USA) | 1992 | gap | no | n/a (no fixture) |
| `genesis-eu` | Mega Drive (EU) | 1993 | yes | yes | ✓ `genesis-rom` |
| `mega-cd-heart-of-alien-1994` | Sega CD | 1994 | partial | no | n/a |
| `3do-1993` | 3DO | 1993 | yes | yes | ✓ `3do-cue-bin` |
| `apple-iigs-1992` | Apple IIgs | 1992 | yes | yes | ⏵ `apple-iigs-2mg` |
| `macintosh-1993` | Macintosh classic | 1993 | yes | yes | ⏵ `mac-classic` |
| `atari-jaguar-removers-2014` | Atari Jaguar | 2013–14 | landing only | no | — |
| `gba-foxy-2004` | Game Boy Advance | 2004 (v2.1: 2005) | yes | yes | ✓ `gba-rom` |
| `nintendo-ds-alekmaul-2011` | Nintendo DS | 2011 | yes | yes | ✓ `nds-rom` |
| `symbian-locked-anotherworld` | Symbian S60 | 2003 | no | no | — |
| `symbian-anotherworld-generic` | Symbian S60 | 2003 (this dump 2008) | yes | yes | ✓ `symbian-sis` |
| `apple-ii-demake-weaver-2019` | Apple II 8-bit | 2019 (v3.1: 2021) | yes | yes | ✓ `apple-ii-demake` |
| `anniversary-ios-2011` | iOS | 2011 | App Store | no | n/a (commercial) |
| `anniversary-android-2012` | Android | 2012 | Play Store | no | n/a |
| `anniversary-steam-2013` | PC | 2013 | Steam | no | n/a |
| `anniversary-gog-2013` | PC | 2013 | GOG | no | n/a |
| `anniversary-3ds-2014` | 3DS eShop | 2014 | partial | no | n/a |
| `anniversary-wiiu-2014` | Wii U | 2014 | — | no | n/a |
| `anniversary-ps3-2014` | PS3 | 2014 | — | no | n/a |
| `anniversary-psv-2014` | PS Vita | 2014 | — | no | n/a |
| `anniversary-ps4-2014` | PS4 | 2014 | — | no | n/a |
| `anniversary-xbone-2014` | Xbox One | 2014 | — | no | n/a |
| `anniversary-switch-2018` | Switch | 2018 | — | no | n/a |

## Notes on individual releases

### `dos` — MS-DOS (1992)

The reference release for the project. Eric Chahi authored Another
World on Amiga / Atari ST in 1991; the MS-DOS port followed in 1992.
The archive holds `Aworld_1994.zip` from classicgames.me — a later
abandonware repackaging, but the bytecode is the original 1992 build.

Resources are stored as `memlist.bin` + `bank01..bank0d`. AWVM_Tools'
Rust `prepare_bank_romset(uppercase=false, MemlistSource::File("memlist.bin"))`
handles this directly. Round-trip disasm + asm preserves the original
bytes exactly.

### `winxp-1.1c` — Windows XP hi-res 1.1c remake

A 2002-era hi-res remake distributed by Eric Chahi from
anotherworld.fr. Resources are inside `Data/Pak01.pak`.

**Investigation result:** the .pak is Valve PAK format ("PACK" magic,
LE u32 dir offset, 64-byte dir entries) — extracted via the new
`valve-pak-extract` Rust binary in AWVM_Tools. Contents are DirectX
shaders, BMPs, OGGs — **not VM bytecode.** The 1.1c remake is a
different engine entirely; the original AW VM does not run inside it.
Valuable as a historical port artifact, not as a VM-genealogy data
point.

### `amiga-retro-presskit` — original 1991 Amiga (presskit redistribution)

The 2014 retro presskit ships two ADF floppy images
(`AnotherWorld_DiskA_nologo_noprotec.adf`,
`…DiskB…`) wrapped in two layers of zip.

The Rust `adf-extract` binary unpacks the OFS-formatted ADFs,
yielding `BANK01..BANK0D` (uppercase, 13 banks, no BANK05) plus
`another` (the Amiga binary with the embedded memlist) plus
`readme.txt` + `Trashcan.info`. **All 9 levels' .asm output is
byte-identical to the Python reference.**

### `amiga-archive-org` — independent 2020 Amiga dump

`Disk1.adf` + `Disk2.adf` uploaded to Internet Archive by
`JasonBreen` on 2020-01-31 under CC0 1.0 public-domain dedication.
**Not the same rip as the presskit.**

Comparative finding ([Genealogy](#/genealogy) and
[Research finding 02](#/research/02-amiga-codewheel-protection)):
the two Amiga dumps share **143 of 144 resources byte-for-byte**;
**level-0 BYTECODE differs in 13 bytes** — the codewheel-protection
patch that the presskit's `_nologo_noprotec` filename announces.

### `atari-st-1991` — Atari ST 1991

Same year as the original Amiga release; the Atari ST and Amiga
were the two original platforms, both 1991. Distributed as Pasti
`.stx` disk images preserving the codewheel copy-protection sectors.

**Extractor implemented** (`extractors/atari_st_pasti.py`): Pasti
`.stx` → flat 720 KiB `.st` → FAT12. Yields 16 files: `BANK01..BANK0D`
(12 unique across the two disks; `BANK06` and `BANK09` are
byte-identical between disks) plus `START.PRG` and `AUTO/START.PRG`.
There is no `memlist.bin` on the floppies — **the resource directory
is embedded inside `START.PRG`**, mirroring the Amiga layout. Mapping
banks back to canonical AW resource indices is open research.

### `snes-eu` and `snes-usa` — Super Nintendo (Europe / USA)

Both are SNES cartridge dumps from Interplay's 1992 port by
Rebecca "Burger" Heineman. The European ROM is archived; the USA
ROM is not.

**SNES EU/USA share the same memory layout** (chunk offsets are
identical), so the Rust `snes-eu` data tables alias `snes` with a
different cartridge filename. The shared `cartridge_rom` extractor
handles both via region-aware dispatch.

A 2026-04 survey for a clean USA fixture turned up only (a) a
Fast-ROM+SRAM hack and (b) a 687 MB bundled `snes100.zip` with no
separable per-file checksums. Recommendation: source the No-Intro
DAT-listed pristine cart elsewhere and verify by md5 before
archiving. Hidden Palace's Sep 1992 SNES prototype is flagged as a
candidate parallel slug.

### `genesis-eu` — SEGA Mega Drive (Europe, 1993)

European Mega Drive cartridge dump. Round-trips byte-identical
end-to-end. The text strings are extracted from the cartridge itself
(range `[0x382B, 0x46FE]` per `genesis2romset.py`).

### `mega-cd-heart-of-alien-1994` — SEGA CD bundle

USA-exclusive Sega CD release that bundles *Out of This World*
together with its only sequel, *Heart of the Alien*. The original-
game half is reportedly identical to the Mega Drive version with
music + sound-effect differences. Not yet archived.

### `3do-1993` — 3DO (USA, 1993)

Interplay 3DO port, also by Rebecca Heineman. Redump-grade `.bin` +
`.cue` (~386 MiB) on archive.org by user `bikerspade` (2021-12-23).

**Extractor implemented** (`extractors/three_do_opera.py` via the new
`opera-list` Rust binary): walks the proprietary 3DO Opera filesystem
end-to-end, yielding **423 on-disc files** including `GameData/FileN`,
`GameData/song1..30`, `GameData/EndShape1/2`, `StalData/*.AIFF`, plus
the ARM-binary `ootw` at the disc root. Mapping these on-disc files
back to canonical AW resource indices is future work.

### `apple-iigs-1992` — Apple IIgs (1992)

Direct port of the SNES build to Apple IIgs by Rebecca Heineman —
*the only Another World port directly transposed from the SNES
source*, made possible because the IIgs and the SNES share the
65C816 CPU. Flux-level WOZ disk images preserved by `4am`
(canonical Apple II preservation curator) in archive.org's
`woz-a-day` collection.

**Two .woz disks archived**, md5 + sha1 verified. **Extraction
stub** — actually pulling files out needs WOZ2 container parser +
3.5" GCR decoder (Apple IWM 8-and-3 GCR, distinct from the 5.25"
6-and-2 used by Apple ][ floppies) + ProDOS volume walker. See
`extractors/apple_iigs_woz.py` for the protocol breakdown.

A separate **European IIgs** item exists on archive.org as smaller
`.po` (ProDOS-order) images without per-file checksums — flagged
as a candidate parallel slug.

### `macintosh-1993` — Macintosh classic (1993)

MacPlay's Mac OS port. **Macintosh Garden** is the canonical source;
publishes per-file SHA-1s. Architecture: Motorola 68k.

**One file archived** — `out_of_this_world.sit`, md5
`411cfe55f7c43c7d846fcb2f24adeddb`, 3,739,614 bytes. Bundles v1.0 +
v1.2 + v1.3 with updaters. **Extraction stub** — needs StuffIt .sit
decompressor + MacBinary parser + 68k Mac resource-fork reader.
The AW VM resources live in the resource fork (not the data fork)
— inverse of every other AW release format we've seen, so the
resource format inside is unmapped.

Two side artifacts on the same Macintosh Garden page would warrant
parallel slugs once parsed: `Out_of_this_World_1.0.mar` (Disk Copy
4.2 image of v1.0 only) and `OutofthisWorldDemo.sit`. Two later
community ports also live on the same page (`Another_World_SDL_Intel.dmg`
PowerPC, `anotherworldx_v0.2b.dmg`) — these are NOT the original 1993
release.

### `atari-jaguar-removers-2014` — Atari Jaguar (community port)

Atari Jaguar **never received a commercial Another World release**.
The Removers (a Jagware collective) and Retro Gaming Connexion
released an authorised community port (year of primary release per
Atarimania is 2013; sources vary 2013–2015). Two graphical variants
ship: original 16-color and "Deluxe" 256-color (15th-anniversary
redo). Eric Chahi authorised the port.

**Status: no public ROM dump exists.** Sole legitimate source is
the Removers' commercial pre-order page at
[mleguludec.free.fr](http://mleguludec.free.fr/product/AnotherWorld_Jaguar/);
Atarimania lists Dump status as MISSING. Acquiring this fixture
will require a donor cartridge.

### `gba-foxy-2004` — Game Boy Advance (Foxy fan port)

Filename in AWVM_Tools is `Another World (Prototype) # GBA.GBA`,
which is **misleading**: this is NOT a leaked Nintendo prototype.
It's the Cyril Cogordan ("Foxy") fan port; Eric Chahi co-developed,
remastered the music, and authorised distribution. Development from
2004; public v2.1 release 2005-04-28. Both author hosts
(foxysofts.com, playerAdvance.org) are now defunct.

**Fixture archived** from the OpenEmu-Update GitHub mirror; an
identical-size copy exists at retrobrews/gba-games. **Extractor
implemented** via shared `cartridge_rom` dispatch:
`prepare_cartridge_romset` extracts hardcoded byte chunks into
`bytecode.rom`, then disassembles 2 levels (the GBA port is based on
the abridged 2-level "demo" build of the engine, like SNES/Genesis).

### `nintendo-ds-alekmaul-2011` — Nintendo DS (homebrew)

Homebrew DS port by Alekmaul (GBATemp 2011 Homebrew Bounty winner),
based on the New RAW engine. Not Nintendo IP. Original mirror
(filetrip.net) is dead in 2026; only the **Wayback snapshot** at
2023-05-15 still serves the zip.

**Extractor implemented** via `zip_unpack`: yields
`anotherworld.nds` + 20 codewheel JPEGs in `wheel/` + 3 docs. The
.nds binary itself does not contain the canonical AW resources —
**at runtime it loads user-supplied DOS `bank01..bankNN` +
`memlist.bin`** (English version) — so the genealogy value here is
in the engine binary itself, not the assets it would play.

### `symbian-locked-anotherworld` and `symbian-anotherworld-generic`

The Symbian Series 60 build was distributed circa 2003 for early
Nokia smartphones (3230, 3250, 3600, …, N72). Two flavours appear
in the wild:

- The **generic `anotherworld.sis`**, widely listed on mobile-game
  catalogue sites (mobiles24.co, vatikag.com).
- A **`locked_anotherworld.sis`** variant — the cracked /
  DRM-stripped form that AWVM_Tools' `symbian_demo` extractor was
  reverse-engineered against. md5 published in `symbian2romset.py`:
  `fe4742b67415eb16ef340548573538b8`.

The generic .sis we archived (`a0012563536c4baaa6487031e00d7b0f`,
753,982 bytes) is **confirmed distinct** from the locked one: 1.6×
larger, possibly a different (later or repacked) build.

**Extractor implemented** — best-effort zlib payload scan
(`extractors/symbian_sis.py`). On the generic .sis it yields a 3 KB
metadata blob plus a 948 KB EPOC E32 binary (UID1=`0x10000079`)
containing **LZMA1 chunks** at offset `0x4B8` — the same nested
format AWVM_Tools' locked-variant extractor consumes. Recovering the
AW VM resources from inside the E32 is a future research task.

Other documented Symbian variant leads (recorded in `metadata.json`
notes but not yet fetched): the mobiles24 sibling listing 110775
(distinct file size), the Telcogames v1.25 SyMPDA-cracked SIS
bundled inside `Nokia_Games_Ultimate_SIS_Pack.zip` on archive.org,
the v1.36 SIS in the `club-60-part-1-1-300` RAR collections, and
the Symbian UIQ2 (Sony Ericsson P800/P900) port — a distinct
platform, would warrant its own slug.

### `apple-ii-demake-weaver-2019` — Apple II 8-bit demake

Vince Weaver's homebrew adaptation of *Out of This World* to the
Apple II's far more constrained graphics. Distinct work from the
Apple IIgs port — same plot, different engine. v3.1 released
2021-05-01; original 2019 release in the upstream source repo's
git history.

**Fixture archived** from the author's deater.net page.
**Extractor implemented** via `zip_unpack`: yields three DOS 3.3
`.dsk` floppy images (140 K each — note the v3.1 release has **3
disk sides, not 2** as the README implies).

### `anniversary-*` — 20th Anniversary Edition (2011 onwards)

Eric Chahi + DotEmu (initially) + Digital Lounge (consoles)
released the 20th Anniversary Edition starting 2011 on iOS, then
spreading across:

- **Mobile**: iOS (2011-09-22), Android (2012-03)
- **PC**: Steam (2013-04-04, app `233550`), GOG (2013-04-22)
- **Nintendo**: 3DS eShop (2014-06), Wii U eShop (2014), Switch
  eShop (2018)
- **PlayStation**: PS3, PS Vita, PS4 (all 2014, with cross-buy)
- **Xbox**: Xbox One (2014), Xbox Series S/X (later, same build)
- **Linux** + **macOS** Anniversary builds also ship via Steam and GOG.

These are commercial digital purchases — provenance is the storefront
receipt, not a ROM dump. The **GOG release** is the DRM-free, most
analysable variant for research purposes.

## Side findings flagged for parallel slugs

These came out of the Tier 1 acquisition push (2026-04-30) and are
candidate parallel-slug entries in `metadata.json`:

- **European Apple IIgs** — `e2gs_Out_of_this_World_Disk_1` /
  `_Disk_2` on archive.org (smaller `.po` images, no per-file
  checksums)
- **Mac v1.0-only** — `Out_of_this_World_1.0.mar` (Disk Copy 4.2)
- **Mac demo** — `OutofthisWorldDemo.sit`
- **Hidden Palace SNES prototype** — Sep 1992 build, separate from
  the released cart
- **mobiles24 Symbian sibling** — listing 110775 (distinct file size)
- **Telcogames v1.25** — SyMPDA-cracked SIS in Nokia ultimate pack
- **Symbian v1.36** — in club-60 archive
- **Symbian UIQ2** — Sony Ericsson P800/P900 port (distinct platform)
- **Older Apple II demake** — pre-v3.1 releases in git history

## Releases we haven't found yet

Mentioned in passing in various sources but no concrete fixture or
download URL has been pinned down. Listed for future research:

- **PSP** — implied by some "Anniversary edition platforms" lists
  but uncertain if it actually shipped on PSP specifically.
- **Localised editions** — French, German, Spanish copies of the
  original 1991 / 1992 Delphine release. archive.org has a Spanish
  manual scan (`instrucciones-another-world-esp_202403`) but no
  associated binary.
- **Original 1992 PC release variants** — the existing `dos`
  fixture is a later distribution; an original Delphine 1992 disk
  set (3.5" floppies) would be a primary source.
- **Atari 2600 / Dreamcast / other 8-bit homebrew demakes** — Vince
  Weaver's Apple II demake is one example; community demakes for
  other retro platforms may exist.

When new candidates surface, add them to `metadata.json` with whatever
provenance is known and append a row to `references/sources.csv`. The
catalog is never "done" — only ever growing.

## See also

- [Format coverage](#/coverage) — extractor implementation status
- [Genealogy](#/genealogy) — research findings on cross-release
  relationships
- [`metadata.json`](#) — the JSON authoritative source
- [`references/sources.csv`](#) — every URL cited as a source

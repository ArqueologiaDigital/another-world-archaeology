# Release catalog

The full list of *Another World* / *Out of This World* release variants
the project has identified, ordered roughly by historical release.
Each entry mirrors a record in [`metadata.json`](#) (the authoritative
source) plus narrative context this page can hold and the JSON can't.

**Locally archived** = a copy of the original release file is stored
in `original_files/<key>/` (the project's permanent local archive —
never deleted; the upstream URL may go offline at any time, and the
local copy is the safety net).

**Documented** = present in `metadata.json` with provenance metadata,
even if the local archive is empty so far.

## Quick status

| Slug | Platform | Year | Source URL known | Locally archived | Disasm parity |
|---|---|---|---|---|---|
| `dos` | MS-DOS | 1992 | yes | yes | ✅ byte-identical |
| `winxp-1.1c` | Windows XP | — | yes | yes | not implemented (winxp-pak format) |
| `amiga-retro-presskit` | Amiga (OCS) | 1991 | yes | yes | ✅ byte-identical |
| `amiga-archive-org` | Amiga (OCS) | 1991 | yes | yes | (same format as presskit; not run yet) |
| `atari-st-1991` | Atari ST/STE | 1991 | yes | yes | not implemented (Pasti format) |
| `snes-eu` | SNES (Europe) | 1992 | yes | yes | not implemented (EU offsets ≠ USA) |
| `snes-usa` | SNES (USA) | 1992 | partial | no | parity blocked on missing fixture |
| `genesis-eu` | SEGA Mega Drive (Europe) | 1993 | yes | yes | ✅ byte-identical |
| `mega-cd-heart-of-alien-1994` | SEGA CD | 1994 | yes (multiple) | no | not implemented |
| `3do-1993` | 3DO | 1993 | yes | yes | not implemented |
| `apple-iigs-1992` | Apple IIgs | 1992 | partial | no | not implemented |
| `macintosh-1993` | Macintosh classic | 1993 | yes (SHA1s) | no | not implemented |
| `atari-jaguar-removers-2014` | Atari Jaguar | 2014 | landing page | no | not implemented |
| `gba-foxy-2004` | Game Boy Advance | 2004 | landing page | no | format misnamed `gba_usa` upstream |
| `nintendo-ds-alekmaul-2011` | Nintendo DS | 2011 | yes | no | homebrew, not yet wired |
| `symbian-locked-anotherworld` | Symbian S60 | 2003 | no | no | parity blocked on missing fixture |
| `symbian-anotherworld-generic` | Symbian S60 | 2003 | yes | no | may or may not match the locked-variant offsets |
| `anniversary-ios-2011` | iOS | 2011 | yes (App Store) | no | n/a (commercial release) |
| `anniversary-android-2012` | Android | 2012 | yes (Play Store) | no | n/a |
| `anniversary-steam-2013` | PC | 2013 | yes (Steam) | no | n/a (DRM build) |
| `anniversary-gog-2013` | PC | 2013 | yes (GOG) | no | n/a (DRM-free, the most analysable) |
| `anniversary-3ds-2014` | 3DS eShop | 2014 | partial | no | n/a |
| `anniversary-wiiu-2014` | Wii U eShop | 2014 | — | no | n/a |
| `anniversary-ps3-2014` | PS3 PSN | 2014 | — | no | n/a |
| `anniversary-psv-2014` | PS Vita | 2014 | — | no | n/a |
| `anniversary-ps4-2014` | PS4 | 2014 | — | no | n/a |
| `anniversary-xbone-2014` | Xbox One | 2014 | — | no | n/a |
| `anniversary-switch-2018` | Nintendo Switch | 2018 | — | no | n/a |
| `apple-ii-demake-weaver-2019` | Apple II 8-bit | 2019 | yes (archive.org) | no | n/a (separate engine — demake) |

## Notes on individual releases

### `dos` — MS-DOS (1992)

The reference release for the project. Eric Chahi authored Another
World on Amiga/Atari ST in 1991; the MS-DOS port followed in 1992.
The local archive holds the `Aworld_1994.zip` distribution from
classicgames.me — a later abandonware repackaging. The actual
bytecode is the original 1992 build.

Resources are stored as `memlist.bin` + `bank01..bank0d` files; the
Python `releases/common_data/banks2resources.py` and the Rust
`prepare_bank_romset(uppercase=false, MemlistSource::File("memlist.bin"))`
both handle this directly.

### `winxp-1.1c` — Windows XP hires demo (anotherworld.fr)

A later demo build distributed by Eric Chahi himself from
anotherworld.fr. Resources are inside `Data/Pak01.pak`. **Pak01
extractor not implemented** — the format may be Valve-style or a
custom bundle; investigation pending.

### `amiga-retro-presskit` — original 1991 Amiga (presskit redistribution)

The 2014 retro presskit ships two ADF floppy images
(`AnotherWorld_DiskA_nologo_noprotec.adf`,
`AnotherWorld_DiskB_nologo_noprotec.adf`) wrapped in two layers of
zip. Disks contain `another` (Amiga binary with embedded memlist)
plus uppercase `BANK01..BANK0D` files.

The AWVM_Tools `adf-extract` Rust binary unpacks the OFS-formatted
ADFs; `awvm-disasm <dir> all_levels amiga` then runs the standard
bank-format pipeline with `uppercase=true` and a memlist sourced
from offset 0x5ec2 inside `another`. **All 9 levels' .asm output
is byte-identical to the Python reference.**

### `amiga-archive-org` — independent 2020 Amiga dump

`Disk1.adf` + `Disk2.adf` uploaded to Internet Archive by
JasonBreen on 2020-01-31 under a CC0 1.0 public-domain dedication.
**Different rip from the presskit** — the actual disk byte content
might or might not match. Worth a comparative pass at the
resource-md5 level once the alt-amiga is run through the pipeline.

### `atari-st-1991` — Atari ST 1991

Same year as the original Amiga release; the Atari ST and Amiga
were the two original platforms, both 1991. Distributed as Pasti
`.stx` disk images (preserves the codewheel copy-protection
sectors). The atarimania record lists multiple imprints (Delphine,
US Gold, Kixx XL re-release, ST Action rolling demo) — only the
US Gold "protected" dump is currently archived.

**Format support not yet implemented** — needs a Pasti reader
plus an Atari ST bank-format extractor. The Atari ST and Amiga
share the same engine, so the bank format is likely close to
identical (both use `bank<NN>` files); the wrapper differs (Pasti
vs ADF).

### `snes-eu` and `snes-usa` — Super Nintendo (Europe / USA)

Both are SNES cartridge dumps from Interplay's 1992 port by
Rebecca "Burger" Heineman. The European ROM is locally archived;
the USA ROM is not. The **AWVM_Tools `snes` extractor's chunk
offsets (`0x74A4C, 0x81CB0`) target the USA ROM specifically** —
parity validation against Python is blocked on the USA fixture.

### `genesis-eu` — SEGA Mega Drive (Europe, 1993)

European Mega Drive cartridge dump. Locally archived, parity
**byte-identical** end-to-end through the Rust pipeline. The text
strings are extracted from the cartridge itself (range
`[0x382B, 0x46FE]` per `genesis2romset.py:generate_text_string_roms`).

### `mega-cd-heart-of-alien-1994` — SEGA CD bundle

USA-exclusive Sega CD release that **bundles Out of This World
together with its only sequel, Heart of the Alien**. The
original-game half is reportedly identical to the Mega Drive
version with music + sound-effect differences. Multiple mirrors
(myabandonware, emuparadise, romhustler, cdromance, edgeemu); a
sample track-1 CRC32 published as `c524515e` (cdromance — needs
cross-verification against Redump). Not yet archived.

### `3do-1993` — 3DO (USA, 1993)

Interplay 3DO port (also by Rebecca Heineman). Redump-grade .bin
+ .cue pair on archive.org, locally archived. CD-ROM extraction
pipeline not yet implemented.

### `apple-iigs-1992` — Apple IIgs (1992)

Direct port of the SNES build to Apple IIgs by Rebecca Heineman
— *the only Another World port directly transposed from the SNES
source*, made possible because the IIgs and the SNES share the
65C816 CPU. Distributed as a `.2mg` disk image. Source URLs
known (oldgames.sk landing page; macintoshrepository alongside
Mac builds), but neither yields a clean direct download —
investigation pending.

### `macintosh-1993` — Macintosh classic (1993)

MacPlay's Mac OS port. **Macintosh Repository publishes per-file
SHA1s**, the highest-quality canonical source we have:

| File | Size | SHA1 |
|---|---|---|
| `out_of_this_world.sit` | 3.57 MiB | `a4a15978d5257f1eeb88ac23c0a25b738005a292` |
| `Out_of_this_World_1.0.mar` | 1.73 MiB | `f41cb05789155375c745cf3ffdbb2d07f1afb339` |
| `OutofthisWorldDemo.sit` | 768 KiB | `0c0fc143da4d97928cb33d135793270ca5b4f1c6` |

The `.sit` archive contains v1.0 + v1.2 + v1.3 with updaters; the
`.mar` is a Disk Copy 4.2 image of v1.0. Mac architecture is
Motorola 68k. Not yet archived locally — MacRepo's ad-and-redirect
download flow needs navigating.

### `atari-jaguar-removers-2014` — Atari Jaguar (community port)

Atari Jaguar **never received a commercial Another World release**.
The Removers (a Jagware collective) and Retro Gaming Connexion
released an authorised community port in 2014 as a physical
cartridge with box and manual; the engine was rewritten for the
Jaguar. Two graphical variants ship: original 16-color and
"Deluxe" 256-color (15th-anniversary redo). Eric Chahi authorised
the port. The AWVM_Tools `jaguar` release glue probably targets
this same dump.

### `gba-foxy-2004` — Game Boy Advance (Foxy fan port)

Filename in AWVM_Tools is `Another World (Prototype) # GBA.GBA`,
which is **misleading**: this is NOT a leaked Nintendo prototype.
It's the Cyril Cogordan ("Foxy") fan port released in 2004,
reverse-engineered from the Atari ST version. Originally
distributed without authorisation; **Eric Chahi authorised
distribution in 2005**. v2.1 is on gbadev.org. Hidden Palace's
unreleased-prototypes index does *not* list it, consistent with
its non-prototype status.

The slug `gba_usa` and the "Prototype" filename are both
misnomers and could be cleaned up post-port.

### `nintendo-ds-alekmaul-2011` — Nintendo DS (homebrew)

Homebrew DS port by Alekmaul (GBATemp 2011 Homebrew Bounty
winner), based on the New RAW engine. Not Nintendo IP. Distributed
openly on GBATemp.

### `symbian-locked-anotherworld` and `symbian-anotherworld-generic`

The Symbian Series 60 build was distributed circa 2003 for early
Nokia smartphones (3230, 3250, 3600, …, N72). Two flavours appear
in the wild:

- The **generic `anotherworld.sis`** (~ 450 KB), widely listed on
  mobile-game catalogue sites (mobiles24.co, vatikag.com).
- A **`locked_anotherworld.sis`** variant — the cracked /
  DRM-stripped form that the AWVM_Tools `symbian_demo` extractor
  was reverse-engineered against. Its specific MD5 is published
  in `symbian2romset.py` comments:
  `fe4742b67415eb16ef340548573538b8`.

The extractor's offsets (zlib payload at `0xBBA + 749540` bytes
containing LZMA1 chunks) are tuned for the locked variant; a
generic .sis may have different offsets. Both are documented;
neither is locally archived yet.

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
- **Linux** and **macOS** Anniversary builds also ship via Steam
  and GOG.

These are commercial digital purchases — provenance is the
storefront receipt, not a ROM dump. The **GOG release** is the
DRM-free, most analysable variant for research purposes (the
binary can be inspected, resources extracted, etc.). Steam and
console builds are DRM-managed and harder to study.

### `apple-ii-demake-weaver-2019` — Apple II 8-bit demake

Vince Weaver's homebrew adaptation of *Out of This World* to the
Apple II's far more constrained graphics. Distinct work from the
Apple IIgs port — same plot, different engine. Hosted on
archive.org.

## Releases we haven't found yet

These are mentioned in passing in various sources but no concrete
fixture or download URL has been pinned down. Listed for future
research:

- **PSP** — implied by some "Anniversary edition platforms" lists
  but uncertain if it actually shipped on PSP specifically.
- **Atari 2600 / Dreamcast / other 8-bit homebrew demakes** — Vince
  Weaver's Apple II demake is one example; community demakes for
  other retro platforms may exist.
- **Localised editions** — French, German, Spanish copies of the
  original 1991 / 1992 Delphine release would be different binaries
  with different string tables. archive.org has a Spanish manual
  scan (`instrucciones-another-world-esp_202403`) but no associated
  binary.
- **Original 1992 PC release variants** — the existing `dos`
  fixture is a later distribution; an original Delphine 1992 disk
  set (3.5" floppies) would be a primary source.

When new candidates surface, add them to `metadata.json` with
whatever provenance is known and append a row to
`references/sources.csv`. The catalog is never "done" — only ever
growing.

## See also

- [`metadata.json`](#) — the JSON authoritative source
- [`references/sources.csv`](#) — every URL cited as a source
- [Format coverage](#/coverage) — extractor implementation status
- [Genealogy](#/genealogy) — research findings on cross-release
  relationships

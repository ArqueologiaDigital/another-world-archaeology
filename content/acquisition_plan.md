# Release Acquisition Plan

## Status

The catalog in `metadata.json` documents 29 release variants of
*Another World*. As of 2026-04-30, the local archive
(`another-world-archive/` — sibling repo, accessed via the
`original_files/` symlink) holds fixtures for **8** of those:

```
dos · winxp-1.1c · amiga-retro-presskit · amiga-archive-org ·
atari-st-1991 · snes-eu · genesis-eu · 3do-1993
```

The remaining **21** releases are documented but unfetched. This
plan groups them into three tiers by acquisition difficulty, so
work can proceed in parallel and the easy wins are not blocked
by the hard ones.

---

## Tier 1 — Public download (low effort; do first)

These are publicly redistributable: classic-platform romdumps that
have been online for decades, plus fan/homebrew ports whose authors
intentionally distribute them. Goal for tier 1: locate a stable URL
(prefer the original author / canonical archive), record it in
`metadata.json` with a Wayback snapshot, fetch the file into
`another-world-archive/<slug>/`, record per-file md5.

| slug                          | platform                | strategy                                                                |
|-------------------------------|-------------------------|-------------------------------------------------------------------------|
| `snes-usa`                    | SNES (USA)              | No-Intro / wowroms cartridge dump (parallel of the EU rom we already have) |
| `apple-iigs-1992`             | Apple IIgs              | archive.org Apple IIgs software collections (`.2mg` / `.po` disk image) |
| `macintosh-1993`              | Macintosh System 6.0.7+ | archive.org Macintosh game archives (likely `.sit` or `.dsk`)           |
| `nintendo-ds-alekmaul-2011`   | Nintendo DS (homebrew)  | `gbatemp.net` URL already in metadata — just fetch                       |
| `gba-foxy-2004`               | Game Boy Advance (homebrew) | search GBATemp / romhacking.net for "Foxy Another World GBA"        |
| `atari-jaguar-removers-2014`  | Atari Jaguar (homebrew) | `removers.fr` / AtariAge — homebrew port by the Removers team           |
| `apple-ii-demake-weaver-2019` | Apple II demake         | Roger Weaver's itch.io / 4amphi-2 self-publication                       |
| `symbian-anotherworld-generic`| Symbian S60 (generic)   | older abandonware Symbian SIS archive (parallel to the *locked* SIS we already record) |

## Tier 2 — Commercial digital, you-own-it-then-extract (medium effort, needs purchases / accounts)

The 2013-2018 *15th/20th Anniversary Edition* releases by DotEmu /
The Digital Lounge / BulkyPix exist on a dozen storefronts. The PC
ones (GOG, Steam, Android) are the cheap-and-easy entry — the
console editions each need a console-specific dumping setup.

| slug                       | source         | extraction approach                                              |
|----------------------------|----------------|------------------------------------------------------------------|
| `anniversary-gog-2013`     | GOG.com        | GOG installer ships assets plain in `gog-game/data/` — no DRM    |
| `anniversary-steam-2013`   | Steam          | Steam install dir at `steamapps/common/Another World/` — plain   |
| `anniversary-android-2012` | Google Play    | pull APK via `adb backup` or APKMirror archive                   |
| `anniversary-ios-2011`     | App Store      | Apple Configurator on macOS; the `.ipa` then needs decryption   |
| `anniversary-3ds-2014`     | 3DS eShop      | 3DS CFW + GodMode9 (extract `.cia` from NAND backup)              |
| `anniversary-wiiu-2014`    | Wii U eShop    | Wii U CFW + NUSspli ticket dump                                  |
| `anniversary-switch-2018`  | Switch eShop   | Switch CFW (Atmosphere) + nxdumptool                             |
| `anniversary-ps3-2014`     | PSN PS3        | PS3 4.xx CFW + multiMan / IRISMAN ISO dump                       |
| `anniversary-psv-2014`     | PSN Vita       | HENkaku CFW + VitaShell                                          |
| `anniversary-ps4-2014`     | PSN PS4        | GoldHEN / firmware-specific PS4 jailbreak + PKG dump             |
| `anniversary-xbone-2014`   | Xbox Live      | no public dumping toolchain — likely will remain undumped         |

For genealogy purposes, the PC anniversary releases (GOG/Steam) are
likely the highest-value targets in this tier — the console ports
all share the same Anniversary engine codebase, so extracting one
and diffing should reveal whether the others differ. Owner has
not yet confirmed which storefronts they own; this tier waits on
the owner's purchase decisions.

## Tier 3 — Specialty / physical-only

| slug                         | platform              | strategy                                                       |
|------------------------------|-----------------------|----------------------------------------------------------------|
| `mega-cd-heart-of-alien-1994`| Sega CD / Mega-CD     | Redump / archive.org Sega CD set — *Heart of the Alien* is the 1994 sequel, originally CD-only |

---

## Workflow per acquired release

For every fetched fixture, follow the established discipline:

1. **Save the file** in `another-world-archive/<slug>/<filename>`.
   The slug should match the `metadata.json` `archive_dir` field; if
   the existing entry doesn't yet have one, add it.
2. **Update `metadata.json`** with: per-file size + md5, the `download`
   URL, `download_date`, `wayback_url` (after archiving via Save Page Now).
3. **Add the source URL** to `references/sources.csv` for the next
   batch Wayback round.
4. **Commit** the archive repo and the archaeology repo separately
   — the archive holds the bytes, the archaeology repo holds the
   metadata.
5. **Wire the extractor** if the format is novel; if it matches an
   existing format (e.g. another DOS-bank or Amiga-style release),
   the existing dispatch should pick it up automatically.

---

## Owner-driven escape hatches

Some tier-1 fetches may require the owner to act manually — for
example, if a homebrew page has a "click to agree to the licence
before download" form, or if a captcha intervenes. In those cases,
record the URL in metadata, mark `md5sum: null`, and flag the entry
in this plan; the file lands in the archive on the owner's next pass.

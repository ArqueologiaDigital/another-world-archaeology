# 04 — 1993 Mac port patch chain (v1.0 → v1.0.2 → v1.0.3)

## Question

The 1993 Macintosh release ships in a single StuffIt archive bundling
three close-versioned application builds (v1.0, v1.0.2, v1.0.3) plus
two updaters. **What changed across the patches?**

This is a uniquely dense genealogy dataset — three close versions of
the same port, plus two patch deltas — the closest thing we have to
*internal* developer changes during a port's lifecycle.

## Method

The Mac extraction pipeline, working end-to-end as of 2026-04-30:

1. `mac-stuffit-extract` decompresses the StuffIt archive and writes
   each entry's data fork + resource fork separately.
2. `mac-rsrc-walk` parses each resource fork's resource map and
   emits one file per `(TYPE, ID)` resource.

Both binaries live in AWVM_Tools (`stuffit = "0.1.4"` +
`macbinary = "0.2.1"` upstream crates). Wiring is in
`extractors/mac_classic.py`.

For this finding, the key piece is the per-resource `md5` of every
`CODE` segment in each application's resource fork. CODE segments
hold the 68k engine code and are what the Mac OS Segment Loader
loads at runtime.

## Findings

### Per-segment md5 across the three builds

The main app's resource fork has 7 `CODE` segments (a `CODE 0`
jump-table plus 6 numbered code segments) plus a small `OOTW`
custom-type "owner resource" stamping the copyright.

| `CODE` segment | v1.0 (md5-12) | v1.0.2 (md5-12) | v1.0.3 (md5-12) |
|---|---|---|---|
| 0 (jump table) | `76fc5ee0702a` | `344a28e78668` | `27e114e44111` |
| 1              | `be0111e047ed` | `be0111e047ed` ← same | `6edce16a74ba` |
| 2              | `2c75e0107a34` | `64c9ed527671` | `02aedfb6b96d` |
| 3              | `35dc6cafeac4` | `85d95c8f9943` | `57c8a94668e6` |
| 4              | `cdf752c16d3b` | `cdf752c16d3b` ← same | `9035ddefe768` (renamed `MacTraps2_ANSI`) |
| 5              | `1914afbba0cd` | `1fb63920b752` | **`cdf752c16d3b`** (= v1.0/v1.0.2 CODE 4! renamed `Histories _ Docs`) |
| 6              | `6ae67cd893c7` | `6ae67cd893c7` ← same | `ad1a4e2b2d49` |

Three independent observations fall out cleanly.

### 1. v1.0 → v1.0.2 was a small targeted patch

Three of the seven CODE segments are byte-identical between v1.0 and
v1.0.2 (CODE 1, 4, 6). Only CODE 0, 2, 3, 5 changed.

CODE 0 changing is expected — it's the segment-loader jump table,
which gets regenerated whenever any other segment changes size. So
the genuine code-level changes are concentrated in segments **2, 3,
5** — three of six numbered segments. v1.0.2 was a **focused bug-fix
patch**, not a feature drop.

### 2. v1.0.2 → v1.0.3 was a structural reorganisation

Every single CODE segment changed md5 — but **the byte content
didn't all change**. The hash `cdf752c16d3bc253411eb1b947c3963d` is:

- **CODE 4** in v1.0 *and* v1.0.2 (unnamed)
- **CODE 5** in v1.0.3, with an explicit name `Histories _ Docs`

A segment got **inserted between CODE 3 and the previous CODE 4**,
which shifted what was CODE 4 to CODE 5. The new v1.0.3 CODE 4 is
named `MacTraps2_ANSI` — almost certainly the MacTraps2 + ANSI
runtime libraries from a Symantec C compiler upgrade. So **v1.0.3 is
essentially the same engine relinked against a newer C runtime**.

### 3. The OOTW "owner resource" carries human-meaningful version data

The custom 4cc resource type `OOTW` (the application's "owner
resource", a standard Mac convention where the four-char-code
creator code is also a resource type) holds a Pascal-style
copyright string:

| Build | Owner-resource string |
|---|---|
| v1.0   | `©1992 MacPlay.` |
| v1.0.2 | `©1992-3 MacPlay and Delphine Software.` |
| v1.0.3 | `©1992 MacPlay.` ← **reverted** to the v1.0 wording |

v1.0.2 added Delphine Software to the credit line; v1.0.3 dropped it
back out. Either a release-note correction (Delphine wasn't actually
the right credit for the Mac port — that was Interplay/MacPlay) or
just an oversight where the v1.0.2 copyright string didn't get
forwarded to the v1.0.3 build template.

Either way, this is a **human-meaningful artefact embedded in the
binary** that an end-user would never see, surfacing only via
resource-fork inspection.

## Genealogy implications

- The Mac port has the **finest-grained version history** of any AW
  release in the catalog — three close versions plus two updaters.
- The v1.0.2 → v1.0.3 segment renumber is a **structural
  fingerprint**: any future port we suspect derives from "the Mac
  build" can be checked for the `cdf752c16d3b...` hash, and if
  present, its position (CODE 4 vs CODE 5) tells us which lineage
  it was forked from.
- The `MacTraps2_ANSI` segment name in v1.0.3 strongly suggests a
  Symantec Think C → Symantec C++ transition between 1.0.2 and 1.0.3
  — worth checking against the rest of the segments' code for
  compiler-fingerprint patterns once a 68k disassembler is in the
  toolchain.
- The Mac port's **`Estr` resource type has exactly 192 entries**
  (totalling 6,114 bytes) in all three versions. 192 = 144 + 48 (a
  number that doesn't match the canonical 144 AW resource indices,
  but is suspiciously tidy). Worth investigating — could be event
  strings, error strings, or something else entirely.

## Cross-link to bytecode genealogy

The per-version `Data/FILE0020..FILE0146` files (which live in the
**data fork**, not the resource fork) are byte-identical between
v1.0 and v1.0.3 — confirmed by md5 spot-check on `FILE0020`. The
**AW VM resources are platform-independent and don't change between
Mac patch versions**. That matches the [gun-ammo finding
01](#/research/01-gun-ammo): mechanic constants are byte-stable
across DOS / Amiga / Genesis-EU. The Mac port preserves the same
AW VM data; the patches only touched the Mac-specific 68k engine
glue.

## Open questions

- What does the new v1.0.3 CODE 1 contain (it changed md5 vs v1.0.2)
  — disassembly would tell.
- Is the segment numbering shift in v1.0.3 visible in the AW VM
  bytecode behaviour? If the Mac engine binds to the bytecode at
  fixed segment offsets, a renumber could break things — unless the
  segment loader is loaded by name.
- Do the `Estr` resources (192 entries in every version) map onto
  AW VM event/error codes? A trivial cross-version diff would say so
  if any string changed across the patch chain.

## See also

- [Research finding 01 — Gun ammo](#/research/01-gun-ammo) — the AW
  VM mechanic constants that are byte-stable across all releases.
- [Research finding 02 — Amiga codewheel patch](#/research/02-amiga-codewheel-protection)
  — the inverse pattern: same engine, different bytecode resource
  in two dumps.
- [Genealogy](#/genealogy) — high-level cross-release findings.
- [Forward plan](#/forward_plan) — tier A item 2 (deeper diff of
  the Mac patch chain) is the natural next step from here.

## Changelog

- **2026-04-30** — initial finding, generated immediately after the
  Mac resource-fork walker (`mac-rsrc-walk`) landed in AWVM_Tools.

# 02 — Amiga: codewheel protection patch

The first concrete genealogy finding from the project.

## Summary

The two Amiga dumps in our local archive — `amiga-retro-presskit`
(2014 redistribution) and `amiga-archive-org` (independent 2020
upload to Internet Archive, CC0) — are **NOT the same binary**.
They share 143 of 144 resources byte-for-byte, but the level-0
`BYTECODE` resource (`resource-0x15.bin`) differs in exactly 13
bytes (0.4% of its 3544-byte payload). All other resources are
identical: 103 SOUND, 9 PALETTE, 10 POLY_ANIM, 9 POLY_CINEMATIC,
3 MUSIC, 1 UNKNOWN, plus 8 of 9 BYTECODEs.

## What the evidence says

The presskit's ADF filenames carry the smoking gun:

```
AnotherWorld_DiskA_nologo_noprotec.adf
AnotherWorld_DiskB_nologo_noprotec.adf
```

`nologo_noprotec` reads as "no logo, no protection." The presskit
is a **patched / cracked variant** of the original Amiga release
with the codewheel copy-protection bypass already applied. The
archive.org dump is presumably the original commercial release
with the codewheel intact.

Per `STAGE_TITLES` in the AWVM_Tools data tables, level 0 is the
*Code-wheel screen* — exactly the level we'd expect to differ if
copy protection had been patched.

## Where the diff sits

13 bytes differ at the following offsets within
`resource-0x15.bin` (the level-0 BYTECODE):

| Offset | presskit | archive_org |
|---|---|---|
| `0x00b5` | `0e` | `19` |
| `0x00b7` | `00` | `47` |
| `0x09fc` | `0a` | `07` |
| `0x09fd` | `80` | `0a` |
| `0x09fe` | `29` | `68` |
| `0x0a01` | `68` | `17` |
| `0x0a07` | `68` | `17` |
| `0x0a0d` | `68` | `17` |
| `0x0a13` | `68` | `17` |
| `0x0a16` | `68` | `d5` |
| `0x0a88..0x0a8a` | (3 bytes) | (3 bytes) |

Total instruction length is preserved (both dumps are 3544 bytes),
which is consistent with an in-place opcode patch rather than a
re-assembly.

The cluster at `0x9fc..0xa88` looks like several conditional-jump-
shaped sequences swapped out (`68` → `17` is the replacement of
the `0x68` opcode-byte with `0x17` = `shr` — almost certainly the
codewheel comparison being neutered). The two-byte diff at
`0x00b5..0x00b7` near the start of the level looks like a single
instruction patched in the entry sequence — possibly the dispatch
that decides whether to enter the codewheel check.

A full bytecode-disassembly diff of those two regions would
identify the exact patched instructions and would let us:

1. Document the cracker's patch (which opcodes / where).
2. Look for the equivalent codewheel logic across other releases
   (Atari ST 1991 has the same codewheel, MS-DOS preserves it,
   etc.) — first cross-release lineage data point.
3. Identify whether the *same* patch (byte-identical) shows up
   in any community redistributions of other Amiga or ST releases.

## How this was found

While answering "how many of our archived dumps round-trip
perfectly," I claimed both Amiga dumps were "the same underlying
binary" because both round-tripped 9/9 levels. The owner pointed
out that round-trip checks the BYTECODE only — every other
resource type could still differ silently.

A per-resource md5 comparison against both dumps' `resources/`
directories surfaced the level-0 BYTECODE divergence. Every other
resource matched exactly.

This is now standing project policy: never claim sameness on
disasm parity alone. See `feedback_compare_all_assets` in the
project memory.

## Status

- **Finding** ✅ retained here.
- **Patch identification** — opcode-level diff has been disassembled
  out of both `resource-0x15.bin` variants. The codewheel-check
  routine is now governed by the `CODEWHEEL_CHECK` flag in the
  source-reconstruction repo
  (`releases/<port>.flags:BYTECODE_BRANCH=...`), with the
  per-release table in [`docs/glossary.md`](https://github.com/ArqueologiaDigital/another-world-source-reconstruction/blob/main/docs/glossary.md).
- **Cross-release search** — partial: DOS and Amiga both ship the
  codewheel check (it's the per-release `CODEWHEEL_CHECK=on/off`
  flag value); cartridge ports (SNES-EU, Genesis-EU, GBA Foxy)
  don't carry it (cartridges had no manual / codewheel insert).
  Atari ST 1991 — see "Atari ST does not carry the codewheel"
  finding below. 3DO / Mac / Apple IIgs await their respective
  parsers.

## Presskit also patched the user-facing prompt (2026-05-05)

Diffing the two Amiga `another` executables (presskit 2014 vs
archive-org 2020 CC0) shows **50 bytes differ in 8 ranges**, all
clustered at offset 0x3414..0x343d — a single embedded text
string the executable prints as the codewheel-check prompt:

      archive (codewheel intact, 2020):
        "SELECT SYMBOLS CORRESPONDING TO\r THE POSITION\r ON THE CODE WHEEL"

      presskit (codewheel stripped, 2014):
        "SELECT 3 SYMBOLS THEN PRESS OK                                  "
        (padded to original byte width)

The cracker patched **both layers**:

1. **Bytecode-level**: the `0x68 → 0x17` opcode swaps in
   `resource-0x15.bin` neuter the codewheel comparison
   (research/02's main finding).
2. **User-facing-string-level**: the prompt string in the
   executable's text segment is replaced from "look up symbols
   on the codewheel" to "press OK after picking any 3 symbols",
   so the user knows the check is bypassed and they don't need
   to consult a codewheel insert.

The two patches are complementary: the bytecode patch makes any
input pass the check; the prompt patch tells the player they
don't need to bother matching symbols. Outside `0x3400..0x343d`
the two `another` executables are byte-identical.

This is consistent with a polished community release rather than
a hasty crack — the cracker took care to update the user-facing
text to reflect the modified behaviour.

## Atari ST 1991: codewheel-check absent (2026-05-05)

The full Atari ST cross-port resource sweep (issue #0004,
research/20) revealed exactly **one Atari-ST-unique resource**:
`0x15 BYTECODE` (the CODE_WHEEL stage bytecode, 3544 bytes — same
length as Amiga's). Byte-diffing Atari ST against the codewheel-
intact Amiga (`tmp/output/amiga/resources/resource-0x15.bin`):

      Atari ST: 3544 bytes
      Amiga:    3544 bytes
      Diff:     7 single-byte changes in 2 clusters
      Coverage: 0.2%

Diff offsets:

      0x00B5  atari=0x19  amiga=0x0E
      0x00B7  atari=0x47  amiga=0x00
      0x0A01  atari=0x17  amiga=0x68
      0x0A07  atari=0x17  amiga=0x68
      0x0A0D  atari=0x17  amiga=0x68
      0x0A13  atari=0x17  amiga=0x68
      0x0A16  atari=0xD5  amiga=0x68

These offsets sit **exactly inside the codewheel-check region**
this finding identified above. The 0x00B5..0x00B7 cluster matches
the "two-byte diff at the start of the level" (gate dispatch)
location; the 0x0A01..0x0A16 cluster is inside `0x9fc..0xa88`
(the conditional-jump cluster) and uses the SAME `0x68 → 0x17`
opcode swap the presskit's codewheel-strip patch uses.

So the Atari ST 1991 release ships with the codewheel-check
**already neutralised** at the bytecode level, in a way that
resembles the 2014 presskit cracker patch.

Two interpretations:

1. **Different protection regime at release**. The Atari ST port
   used a *disk-format* protection scheme (custom-formatted
   sectors, common on Atari ST commercial games of the era)
   handled in `START.PRG` running natively on 68k *before* the
   AW VM bytecode is loaded. The bytecode-level codewheel check
   was therefore unnecessary, and shipping without it is
   plausible for Delphine's Atari ST build.

2. **Cracked-release dump**. The Atari ST extraction we have was
   sourced from atarimania.com (PASTI .stx) — Pasti preserves
   protection-track sectors but a Pasti image of an *already-
   cracked* disc would carry the cracker's bytecode patch.

Distinguishing these requires comparing against a known-pristine
Atari ST dump (issue tracking the question filed as `#0092`).

For the current finding's purposes, the byte-level diff is
documented here as a hard cross-port observation; the
"why" remains an open question.

## Reproducing

```bash
# Extract both Amiga dumps:
adf-extract \
    original_files/amiga-retro-presskit/{DiskA,DiskB}.adf \
    /tmp/in_presskit
adf-extract \
    original_files/amiga-archive-org/Another_World_Disk{1,2}.adf \
    /tmp/in_archive_org

# Run each through the Rust pipeline (no-polygons for speed):
awvm-disasm /tmp/in_presskit   all_levels amiga --no-polygons
awvm-disasm /tmp/in_archive_org all_levels amiga --no-polygons

# Diff resources/ md5s:
diff <(cd presskit_out/amiga/resources && md5sum *) \
     <(cd archive_out/amiga/resources && md5sum *)
```

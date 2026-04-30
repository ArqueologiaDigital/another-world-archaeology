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
- **Patch identification** TODO — disassemble both `resource-0x15.bin`
  variants in the affected offset ranges and document the exact
  opcode-level differences.
- **Cross-release search** TODO — look for the same codewheel
  logic in `dos`, `atari-st-1991` once we have an Atari ST
  extractor, and the SNES / Genesis / 3DO / Macintosh / Apple IIgs
  ports as those land.

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

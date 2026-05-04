# 13 — Cross-release md5 index of extracted resources

The first systematic resource-byte audit between the Amiga 1991
and DOS 1992 ports.

## Summary

Aggregating per-resource md5s across releases (`tools/cross_release_md5_index.py`)
shows that the Amiga 1991 → DOS 1992 port reused most assets verbatim
and rebuilt a small, structured slice of them. Of the 144 resource
slots Amiga ships:

- **117 are byte-identical** with their DOS counterpart at the same
  index (mostly SOUND, MUSIC, POLY_ANIM, plus a handful of BYTECODEs
  that survived intact from the dispatcher / cross-stage helpers).
- **27 differ** at the same index — and they cluster in a perfect
  9 + 9 + 9 split:
  - 9 PALETTE resources
  - 9 BYTECODE resources
  - 9 POLY_CINEMATIC resources
- **0 are Amiga-only.**
- **2 are DOS-only**: indices `0x12` and `0x13`, both POLY_ANIM
  type. Amiga's resource set skips these slots entirely.

The differing-27 indices are not scattered: they form 9 consecutive
triplets `(PALETTE, BYTECODE, POLY_CINEMATIC)` at indices
`(0x14,0x15,0x16)`, `(0x17,0x18,0x19)`, `(0x1A,0x1B,0x1C)`,
`(0x1D,0x1E,0x1F)`, `(0x20,0x21,0x22)`, … one triplet per stage.
Every stage gets a fresh palette + recompiled bytecode + repacked
cinematic-polygon bank on DOS; nothing else changes.

## What the evidence says

The structure of the diff is the genealogy. Not random per-asset
churn — a deliberate rebuild boundary drawn around exactly one
asset class per stage.

- **Per-stage triplets all rewritten**: BYTECODE re-encoding is
  expected (CINEMATIC offsets shift when the polygon bank is
  repacked; even the same logical bytecode produces different
  bytes). POLY_CINEMATIC repack is also expected (per-port
  polygon ordering / packing). PALETTE divergence is the
  surprising one — same logical 32-color palette, different
  bytes. Spot-check on stage 0's PALETTE_0x14 shows 79/2048 bytes
  differ (3.9%) starting at offset 0x460, with bit patterns that
  look like high-nibble flags toggled per-color (Amiga writes
  `0x0NNN`, DOS writes `0xFNNN`-class values for the same color
  slots). Plausibly a port-specific palette annotation byte
  (cycling flag, plane mask, or transparency hint) that's
  always-zero on Amiga and stage-tunable on DOS.

- **Everything else literally copied**: the 103 SOUND, 7 MUSIC,
  10 POLY_ANIM (out of 12 on DOS — see below), and ~7 small
  BYTECODE / cross-stage helper resources are reused as raw
  bytes. The DOS port did not re-encode SFX or music.

- **DOS adds 2 POLY_ANIM resources** at indices `0x12` and `0x13`.
  These slots simply don't exist on Amiga. Likely candidates:
  the additional code-wheel scene art that DOS introduced (the
  Amiga release used physical codewheel verification; DOS's
  version is the on-screen code-wheel sprite set). Subject to
  verification by following references from BYTECODE_0x15
  onward.

- **`dos` ↔ `msdos` is a no-op match**: the `dos` slug is the
  `init.py` extraction of `Aworld_1994.zip` into
  `work/076117919d1dca51e486f33b8f7817e3/bin/`; `msdos` is the
  AWVM_Tools extraction of the same package into
  `tmp/output/msdos/resources/`. Same 146 indices, same md5s
  byte-for-byte — confirms the two extractors agree on every
  resource.

## Why this matters

Compiling the diff by md5 is a cheap, total scan. It collapses the
"which assets did the DOS port really inherit" question from "diff
two whole releases" to "look at this 27-row table." The shape of
the table tells the story: Amiga's PALETTE+BYTECODE+POLY_CINEMATIC
per-stage triplet was the only thing that crossed the port
boundary as bytes-changing — the rest is verbatim.

This is the byte-level analogue of the source-reconstruction sweep
(research 09 onward) that walks the Amiga vs. DOS bytecode
disasms. The bytecode-source diff is large and noisy because
operand bytes shift with polygon bank reflows; the resource-md5
diff is small and clean. Both views are needed: the bytecode
diff tells you which logic moved; the md5 diff tells you which
assets the port actually rebuilt versus reshipped.

## Reproducing

```
python3 tools/cross_release_md5_index.py
# wrote docs/cross-release-md5-index.md
#   3 releases, 436 resources, 162 distinct md5s
```

The aggregator reads from two sources today:

1. `work/<slug>/manifest.json` `resources[]` arrays (DOS only,
   for now).
2. `tmp/output/<port>/resources/resource-0x<index>.bin` files
   (computes md5s on demand; covers Amiga and msdos).

Adding extractors for SNES, Genesis, GBA, etc. fills out the
matrix. Once those land, the same report becomes the genealogy
backbone for every port.

## Limitations

- The Amiga release indexed here is the `nologo_noprotec` ADF
  pair (codewheel-stripped — see research 02). The 13-byte
  BYTECODE_0x15 patch documented there is not visible in the
  matrix because the matrix counts md5 mismatches per-port pair,
  not per-Amiga-variant. A future expansion: add the
  `amiga-archive-org` (codewheel-intact) variant as a separate
  release row.
- POLY_ANIM count on DOS reads as 12 not 10 — the matrix table
  groups by type-tag, not by per-resource-type role. The "DOS
  has 2 extra POLY_ANIM" finding is read off the per-pair B-only
  column, not the type-count.
- `tmp/output/` is a parallel scratch tree from AWVM_Tools, not
  part of the canonical work/ archive. The aggregator reads it
  opportunistically; if a future cleanup wipes `tmp/output/`,
  the report will lose its non-DOS rows until the canonical
  extractors catch up.

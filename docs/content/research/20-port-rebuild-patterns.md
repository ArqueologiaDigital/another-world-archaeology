# 20 — Port-rebuild patterns: who reused DOS resources, who rebuilt

How much of the AW VM resource set survives byte-for-byte across each
port? This finding documents three distinct **port-rebuild patterns**
visible in the byte-level cross-port md5 sweep, and what each implies
about the port's relationship to the original DOS / Amiga lineage.

## Question

When a new port of *Another World* shipped, how much of its on-disc
data was copied verbatim from an existing release vs reauthored from
scratch?

The Amiga 1991 → DOS 1992 → SNES/Genesis 1992 → GBA 2004 line is
already known to share most resources verbatim (see research/13:
117/144 byte-identical Amiga ↔ DOS). What about the other ports —
Mac 1993, Atari ST 1991, 3DO?

## Answer (summary)

Three distinct rebuild patterns:

1. **Cartridge-line preservation** (Amiga, DOS, SNES-EU, Genesis-EU,
   GBA). 117 of 144 resources byte-identical Amiga ↔ DOS. Per-stage
   triplet (PALETTE, BYTECODE, POLY_CINEMATIC) rebuilt; everything
   else preserved. See research/13 for the matrix.

2. **Mac 1993 — selective preservation**. The Mac data fork preserves
   PALETTE and early-stage POLY_CINEMATIC verbatim but rebuilds all
   BYTECODE and most poly banks. Carries one Mac-exclusive resource
   (a 640×480 GIF87a splash image, hex id `0x92`).

3. **3DO — full rebuild**. **Zero byte-overlap** with any other port.
   SOUND replaced with AIFF audio; some cinematics replaced with
   pre-rendered streamed video; everything else re-encoded for the
   3DO's CRY 16 bpp colour space.

The matrix:

| Port               | match vs DOS | rebuild fraction          |
|--------------------|--------------|---------------------------|
| Amiga 1991         | 117/144      | per-stage triplet         |
| Atari ST 1991      | 92/119*      | per-stage triplet (=Amiga)|
| Genesis-EU 1992    | ≈117/144     | per-stage triplet         |
| SNES-EU 1992       | ≈117/144     | per-stage triplet         |
| GBA Foxy 2004      | ≈117/144     | per-stage triplet         |
| Mac 1993           | 10/35        | most stages rebuilt       |
| 3DO ~1994          | 0/...        | total rebuild             |

(*Atari ST count is over the 119 uncompressed resources only;
the 28 compressed resources weren't compared in this sweep. The
118/119 match-vs-Amiga rate is the more telling number — Atari
ST is essentially the Amiga release with a single CODE_WHEEL
bytecode swap.)

(Atari ST is a special case: same memlist *layout* and per-stage
resource counts as DOS — 103 SOUND, 3 MUSIC, 12 POLY_ANIM, 9 PALETTE,
9 BYTECODE, 9 POLY_CINEMATIC, 1 UNKNOWN — but the memlist is
big-endian and BE/LE fields shift every numeric value. Spot-check
of resource #27 from `BANK02` confirms byte-identity with Amiga's
level-2 bytecode after the format shift; full audit pending an
AWVM_Tools `atari_st` release registration. See archaeology issue
`#0004`.)

## Why this matters

The three patterns each suggest a different development arrangement:

- **Cartridge-line preservation** is the cheapest port path:
  reuse the platform-independent assets and re-encode only the parts
  that depend on the target platform's CPU (BYTECODE) and rendering
  (PALETTE + POLY_CINEMATIC). Per-stage rebuild matches what a single
  developer-with-an-asset-pipeline would produce in a few months.

- **Mac selective preservation** suggests Delphine handed the Mac
  developer a partial source tree with the early-stage assets
  reusable but the bytecode requiring re-derivation (perhaps the
  Mac VM had different opcode encoding details, or the stage-load
  logic was reauthored against the Mac OS). The 640×480 splash
  image is a clear Mac-platform-only addition.

- **3DO total rebuild** suggests a full re-implementation by a
  separate team using their own asset pipeline and the 3DO's
  hardware-rendered video / streamed-audio capabilities. The 3DO
  port is the most "remote" branch in the genealogy: it inherits
  the *game design* but shares zero bytes with any earlier release.

## Detailed analysis

### Mac data fork (issue #0009)

Mac 1993's data fork ships 36 distinct AW resources at decimal-encoded
filenames `FILE<NNNN>.data` (where `NNNN` decodes directly to the
hex resource id: `FILE0020` = decimal 20 = hex `0x14`).

Hex-resource layout in the Mac data fork:

    FILE0020..0043   →  0x14..0x2B   (8 stages × 3 res + 1 unused)
    FILE0067..0073   →  0x43..0x49   (POLY_ANIM cluster)
    FILE0125..0127   →  0x7D..0x7F   (passcode trio)
    FILE0144..0146   →  0x90..0x92   (last range; 0x92 is Mac-exclusive)

Match aggregate vs DOS:

| Type            | match | diff | total |
|-----------------|-------|------|-------|
| PALETTE         | 7     | 2    | 9     |
| POLY_CINEMATIC  | 3     | 6    | 9     |
| BYTECODE        | 0     | 9    | 9     |
| POLY_ANIM       | 0     | 8    | 8     |

The 3 matching POLY_CINEMATIC are the *first three stages*
(CODE_WHEEL, INTRO, LAKE) — i.e. the ones with the simplest
polygons (logo / lab interior / underwater pool). The two diverging
PALETTEs are LAKE and CAVES (`0x1A` and `0x20`) — Eric Chahi
presumably touched up the underwater + caves colour mood for the
Mac display gamut.

`FILE0146` (=hex `0x92`) is **Mac-exclusive**: a 640×480 GIF87a image
(magic `47 49 46 38 37 61` at offset 0). Far too large for AW's
320×200 framebuffer; almost certainly the splash/title/credits art,
not used by the AW VM runtime.

#### Mac is downstream of DOS, not Amiga (2026-05-05)

Cross-checking each of the 10 Mac↔DOS shared md5s against Amiga
and Atari ST 1991 confirms the lineage direction:

      idx 0x14  PALETTE        shared with: DOS-only-rebuild
      idx 0x16  POLY_CINEMATIC shared with: DOS-only-rebuild
      idx 0x17  PALETTE        shared with: DOS-only-rebuild
      idx 0x19  POLY_CINEMATIC shared with: DOS-only-rebuild
      idx 0x1c  POLY_CINEMATIC shared with: DOS-only-rebuild
      idx 0x1d  PALETTE        shared with: DOS-only-rebuild
      idx 0x23  PALETTE        shared with: DOS-only-rebuild
      idx 0x26  PALETTE        shared with: DOS-only-rebuild
      idx 0x29  PALETTE        shared with: DOS-only-rebuild
      idx 0x7d  PALETTE        shared with: DOS-only-rebuild

**Every** Mac↔DOS verbatim-shared resource is one DOS rebuilt in
the 1991→1992 port (i.e., none of them match the original
Chahi 1991 versions). This means the Mac team sourced their
data fork from **DOS 1992**, not from the original 1991 Amiga
master. Even when Mac preserves resources verbatim, it's
preserving DOS's 1992 rebuilds.

The lineage arrow pointing to Mac is thus DOS → Mac, not
Amiga → Mac:

```
Chahi 1991 master (Amiga + Atari ST)
   │ per-stage triplet rebuild
   ▼
Delphine 1992 internal source (lost — only inferred)
   ├── DOS 1992 (Morais @ Delphine)
   │     │ data-fork hand-off
   │     ▼
   │   Mac 1993 (MacPlay)
   │     - 7 PALETTE + 3 POLY_CINEMATIC verbatim from DOS
   │     - all BYTECODE + later POLY_CINEMATIC + all POLY_ANIM rebuilt
   │
   └── SNES-EU 1992 (Heineman @ Interplay)
         ├── Genesis-EU 1993 (verbatim cartridge bytecode reuse)
         └── Foxy/Magic Pockets → GBA 2004
```

### 3DO (issue #0003)

3DO ships 263 `File<NNN>` data blobs + 30 `song<NN>` audio files
+ a couple of pre-rendered cinematic .Cine files (Logo.Cine 10 MB,
ootw2.cine 28 MB).

Cross-port md5 sweep:

    DOS 1992        : 0 matches
    Atari ST 1991   : 0 matches
    Mac 1993        : 0 matches
    GBA Foxy 2004   : 0 matches
    Amiga 1991      : 0 matches
    SNES-EU 1992    : 0 matches
    Genesis-EU 1992 : 0 matches (×2 slugs checked)

**Zero matches across every port-pair.** The 3DO port has no
byte-equivalent file in any other release.

The 3DO File numbering has gaps (4-7, 18-20, 52, 54, 60, 71, ...);
this is consistent with a sparse-write resource-id scheme rather
than a contiguous index.

### Atari ST (issue #0004)

The Atari ST 1991 release is *almost* indistinguishable from Amiga
at the resource level — same struct layout, same resource counts,
same content. The two differences are operational rather than
content:

1. The memlist lives **inside** `START.PRG` (offset `0x7EF2`,
   2940 bytes, 147 entries) rather than as a standalone
   `memlist.bin` file. The Atari ST extractor now synthesises
   `memlist.bin` from this offset — see commit `6196466`.
2. Field byte order is **big-endian** (68000-native), matching
   Amiga; DOS uses little-endian for the same struct.

**Full cross-port resource sweep (2026-05-05)** — walked the
synthesised memlist + 12 BANK files directly. Initially compared
only the 119 uncompressed resources, then **extended to all 131
resources after porting the AW VM unpacker to Python**
(`tools/aw_unpacker.py`, validated against DOS PALETTE 0x14 +
DOS POLY_ANIM 0x43 — byte-identical to AWVM_Tools' Rust
`awvm::unpacker::unpack` output).

    Total Atari ST resources scanned (uncompressed + depacked): 131
      Match Amiga 1991:                                          120  (91.6%)
      Match DOS 1992:                                             94  (71.8%)
      Match Amiga but NOT DOS:                                    26
      Match DOS but NOT Amiga:                                     0
      Match neither (Atari-ST-unique):                            11

The 26 Amiga-preserved-but-DOS-replaced resources form a perfect
9+8+9 split (PALETTE / BYTECODE / POLY_CINEMATIC), which is
exactly the same per-stage triplet pattern research/13 found for
the Amiga ↔ DOS comparison. **Atari ST + Amiga ship the same
core 1991 Chahi resource set; DOS 1992 rebuilt the per-stage
triplet ×9 stages and preserved everything else.**

**The 11 Atari-ST-unique resources** break down as:

  - **10 POLY_ANIM** (background bitmaps): 0x43, 0x44, 0x45, 0x46,
    0x47, 0x48, 0x49, 0x53, 0x90, 0x91. All 32000 bytes
    uncompressed (320×200 4bpp). Atari ST ships **different
    background art** for those rooms — not just re-encoded; the
    pixel-index bitmaps themselves differ from both Amiga 1991
    and DOS 1992.
  - **1 BYTECODE**: 0x15 (the CODE_WHEEL stage, 3544 bytes).
    Differs from Amiga in only 7 bytes, all at the codewheel-
    check sites — see research/02 + issue #0092 for the open
    question on whether this is a deliberate Atari-specific
    authoring choice or a cracked-release artefact.

The 10 unique POLY_ANIM is a surprise. AW's POLY_ANIM resources
are platform-independent 4bpp bitmaps; one might expect them to
be byte-identical between two 68k SKUs that share the same
display word-size. The divergence implies one of:

  - **Per-platform artist re-paints** for a subset of room
    backgrounds (different visual mood for Atari vs Amiga).
  - **Different palette intent** that required pre-quantising
    the bitmap differently per port.
  - **Compression-asymmetric originals** that were re-encoded
    with slight artist tweaks during port-out.

Without a side-by-side rendering to compare visual content
(gated on a POLY_ANIM viewer), the precise nature of the
divergence is currently unknown — but the byte-level fact is
solid. 10 of 12 Atari ST POLY_ANIM resources differ from both
Amiga and DOS, so this is **not** a uniform "DOS rebuilt
everything" pattern; it's an Atari-vs-Amiga 1991 divergence.

Acceptance criterion #4 of issue #0004 (cross-port md5
comparison) is now fully covered.

## Genealogy implications

The byte-level evidence places each port on a 3-tier proximity scale
to the original Eric Chahi 1991 amiga release:

```
                     1991 amiga  ─────────────  Atari ST 1991
                                               (~identical content)
                          │
                          │  per-stage triplet rebuild
                          ▼
                     1992 dos  ───────────────  cartridge_1992
                                                (Amiga + 1992 DOS triplets
                                                 propagated via the same
                                                 toolchain)
                                              │
                                              │  pure inheritance
                                              ▼
                                          GBA 2004
                                                (Foxy port reuses
                                                 cartridge bytecode)

  Mac 1993:    keeps PALETTE + early POLY_CINEMATIC; rebuilds rest
  3DO ~1994:   keeps NOTHING; full rebuild
```

The Mac and 3DO ports are clean "outgroup" branches: their resource
sets cannot be derived from the cartridge lineage by any patching
workflow. Mac is partial (some assets survived); 3DO is total
(everything was reauthored).

## Reproducing

The cross-port md5 sweep used:

```bash
# Build md5 of every file in package N
find <package_root> -type f | xargs md5sum

# Find shared md5s across two packages
md5sum -c <(...)  # or simple set-intersection in Python
```

A reusable scanner lives in
`tools/cross_release_md5_index.py` (the one research/13 cites for
DOS↔Amiga).

## See also

- [Research 13 — Cross-release md5 index](#/research/13-cross-release-md5-index)
  — the original Amiga ↔ DOS matrix this finding extends.
- [Issue #0003 — 3DO resource mapping](#/issues/0003-3do-aw-resource-mapping)
- [Issue #0004 — Atari ST embedded memlist](#/issues/0004-atari-st-embedded-memlist-parse)
- [Issue #0009 — Mac data fork resource format](#/issues/0009-mac-data-fork-aw-resources)

## Changelog

- 2026-05-05: opened. Synthesises findings from issues #0003,
  #0004, #0009 plus the 0-match cross-port sweep done this session.

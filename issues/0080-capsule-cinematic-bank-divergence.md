---
id: 0080
title: CAPSULE alien sprite uses different CIN ranges in cart, dos, and amiga
status: open
tier: A
created: 2026-05-03
updated: 2026-05-04
tags: [archaeology, capsule, divergence, animation, cinematic-bank]
---

# Context

Three parallel low-nibble sub-anim dispatchers in CAPSULE for the
alien character draw cinematic frames at different indices in each
arm:

| Routine role               | cart       | dos        | amiga       |
|----------------------------|------------|------------|-------------|
| 2-case alien sub-anim      | CIN_112-113| CIN_111-112| CIN_183-184 |
| 3-case alien sub-anim      | CIN_109-111| CIN_108-110| CIN_180-182 |
| 2-case alien sub-anim (B)  | (no peer)  | (no peer)  | CIN_204-205 |
| 3-case alien sub-anim (B)  | (no peer)  | (no peer)  | CIN_201-203 |

For the hero character, the same dispatchers use:

| Routine role               | cart       | dos        | amiga      |
|----------------------------|------------|------------|------------|
| 2-case hero sub-anim       | CIN_033-034| CIN_033-034| (?)        |
| 3-case hero sub-anim       | CIN_030-032| CIN_030-032| (?)        |

Hero's CIN range is identical between cart and dos (033/030 base);
amiga uses entirely different cinematic indices (164 / 195 base for
the high-nibble dispatchers we already named).

# What this tells us

- The CIN bank index space is NOT stable across releases.
- Cart 1992 and dos 1992 are nearly aligned for hero anim, but the
  alien anim base is off-by-one between them — strong hint they were
  built from different source revisions.
- Amiga 1991 (Eric Chahi himself) used a substantially different
  cinematic numbering, suggesting the 1992 ports renumbered indices
  rather than preserving the original 1991 layout.

# Acceptance criteria

- [ ] Build a per-release CIN-index → poly-content mapping.
- [ ] For each cart/dos/amiga CIN that maps to "alien-pose-N":
      identify the index in the other two arms.
- [ ] Determine whether the underlying poly bytes are identical
      (same sprite, different index) or whether the sprite content
      itself was updated.
- [ ] If sprite content is identical: this is purely a renumbering.
      If sprite content differs: it's a meaningful re-spritefication.

# Related

- Issue 0079 — PRISON cart has fewer dispatch cases than dos/amiga.

# Log

- 2026-05-03: opened. Surfaced during CAPSULE rename rounds —
  see commit b494b46 for the dos+amiga round that documented the
  divergent CIN ranges per arm.

- 2026-05-04: byte-level comparison of CAPSULE poly_cinematic
  banks (`tmp/output/msdos/resources/resource-0x28.bin` vs
  `tmp/output/amiga/resources/resource-0x28.bin`) at the EQU
  offsets for the mapped CIN pairs:

  | Pair | DOS CIN | Amiga CIN | First-4-byte (type+bbox) match | Full-32-byte match |
  |---|---|---|---|---|
  | 2-case A | 111 (0x493E) | 183 (0x506E) | YES | NO |
  | 2-case B | 112 (0x655E) | 184 (0x9658) | YES | NO |
  | 3-case A | 108 (0x4906) | 180 (0x5036) | YES | NO |
  | 3-case B | 109 (0x494E) | 181 (0x507E) | YES | NO |
  | 3-case C | 110 (0x6526) | 182 (0x9620) | YES | NO |

  All five mapped pairs have **identical poly type + bounding box**
  (first 4 bytes), confirming each pair refers to the same logical
  sprite (same dimensions, same root polygon).

  The trailing bytes diverge only at SUB-POLYGON OFFSETS
  (the 16-bit pointers to chained sub-polys within the bank). The
  vector data tail itself (e.g. `ce 09 01 04 09 00 09 01 00 01 00 00`
  on the 3-case C pair) is **byte-identical** in both arms.

  **Conclusion**: the CAPSULE alien CIN renumbering between
  amiga 1991 and dos 1992 is a **bank repack + index renumbering**,
  not a content rewrite. The sprite OUTLINES are the same; only the
  polygon-bank packing layout (and therefore the EQU offsets and
  index positions) differs.

  Cart 1992 is presumably the same logical content (the
  dispatchers' role-mapping says cart CIN_109-111 ≡ dos CIN_108-110
  ≡ amiga CIN_180-182), but cart's polygon bank isn't yet
  extracted — the cartridge_rom extractor doesn't decode polygons
  yet. Confirming cart's bytes would close this issue.

  **Acceptance items resolved**:
    - ✅ Built per-release CIN-index → poly-content mapping
      (for dos and amiga; cart pending extractor).
    - ✅ For each dos/amiga CIN pair: confirmed underlying poly
      bytes have identical headers (semantically the same sprite)
      but differ only in sub-poly offsets (bank repack).
    - ✅ Verdict: this IS purely a renumbering, not a
      re-spritefication. The 1992 ports both renumbered indices
      from amiga's 1991 layout, presumably to suit their target
      platform's bank-loading conventions.

  **Still pending**:
    - [ ] Cart polygon extraction (gated on cartridge_rom
      extractor implementing polygon decode).

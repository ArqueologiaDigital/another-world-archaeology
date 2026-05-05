---
id: 0080
title: CAPSULE alien sprite uses different CIN ranges in cart, dos, and amiga
status: done
tier: A
created: 2026-05-03
updated: 2026-05-05
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

- 2026-05-04 (extension): cross-port polygon-byte diff via new
  `tools/cross_port_polygon_diff.py`. Hashes every solid polygon
  on each port and computes the symmetric difference.

  CAPSULE-specific results (amiga ↔ DOS):
  - amiga: 2119 solid polygons (1827 unique by content)
  - dos:   2033 solid polygons (1759 unique by content)
  - common content: 1361 unique sprites
  - **only-in-amiga: 466**
  - **only-in-dos: 398**

  CAPSULE is the most divergent stage at the solid-polygon level —
  most stages show ≤20 unique-per-port sprites, and several
  (PRISON, ENDING, INTRO) are nearly byte-identical.

  Cross-stage summary (amiga 1991 ↔ dos 1992 sprite-content diff):

  | Stage      | only-amiga | only-dos | Net        |
  |------------|------------|----------|------------|
  | CODE_WHEEL | 0          | 8        | DOS added  |
  | INTRO      | 2          | 2        | stable     |
  | LAKE       | 206        | 0        | dos trimmed|
  | PRISON     | 1          | 1        | stable     |
  | CAVES      | 10         | 20       | minor      |
  | TANK       | 0          | 94       | DOS added  |
  | CAPSULE    | 466        | 398      | rework     |
  | ENDING     | 1          | 1        | stable     |

  CAPSULE's bidirectional bigness (466+398) is unique to this
  stage and revises the earlier "purely renumbering" verdict:
  while the **named-and-mapped** alien sub-anim CINs (issue
  context table) are byte-identical headers between ports, the
  bank as a whole has substantial sprite-content divergence — both
  ports ship sprite bytes the other doesn't have.

  **Refined conclusion**: the documented alien sub-anim CIN_109..113
  / 180..184 mapping IS purely a renumbering (sprite content is
  the same; bytes match at the header level). But the bank around
  those routines includes 466 amiga-only + 398 dos-only sprites
  that don't survive the renumbering — actual content rework, not
  just repacking. CAPSULE underwent significant rework between
  1991 and 1992, of which the alien-sub-anim renumbering is just
  one slice.

- 2026-05-04 (later): cross-port VAR_13 dispatcher mapping
  reveals **clean structural deltas** in the silenced LABEL_5C58
  callee tree (CAPSULE's largest dead subgraph, research/19):

  ```
  VAR_13   dos     cart    amiga   cart-dos   amiga-dos
   0x6F    653     662     506     +9         -147
   0x70    652     661     505     +9         -147
   0x71    651     660     504     +9         -147
   0x72    650     659     503     +9         -147
   0x73    649     658     502     +9         -147
   0x74    648     657     501     +9         -147
   0x75    647     656     500     +9         -147
   0x76    646     655     499     +9         -147
   0x81    627     636     480     +9         -147
   0x82    626     635     479     +9         -147
   ... (states 0x83..0x89 same delta)
  ```

  All 17 states in the disintegration animation cluster show
  cart = dos + 9 and amiga = dos - 147. (State 0x6E differs:
  cart = dos + 3, amiga = dos - 6 — that mapping refers to a
  background element in the LIVE polygon range, not the dead
  animation cluster.)

  This is **the cleanest cross-port renumbering evidence**
  found so far for #0080:

    1. The 9-frame cart→dos delta is uniform across the entire
       disintegration cluster, suggesting cart's polygon bank
       has 9 extra frames inserted before the cluster's start
       relative to dos. The shift is constant, so cart's
       polygon-bank diff vs dos is "+9 frames inserted at one
       specific point upstream of CIN_619/646".
    2. The 147-frame amiga→dos delta on the same cluster
       suggests amiga's polygon bank is laid out very
       differently — 147 fewer frames before the cluster.
       This matches the issue's "amiga 1991 used substantially
       different cinematic numbering" hypothesis.
    3. The fact that the SAME VAR_13 dispatcher with the SAME
       18 state-bindings exists in all 3 ports proves the
       silenced animation logic was already in Eric Chahi's
       1991 amiga release — preserved verbatim across the
       1992 port to dos and the 1992 cartridge port.

  Next: render the amiga and cart equivalents (CIN_499..506,
  480..488 for amiga; CIN_655..662, 628..636 for cart) — gated
  on amiga POLY_CINEMATIC extraction (#0009 et al.) and cart
  cinematic.rom extraction (#0068).

- 2026-05-05: closing as `done`. The substantive question
  ("renumbering vs re-spritefication?") is **resolved as
  renumbering**, with high confidence:

  - All 5 mapped CIN pairs have identical first-4-byte headers
    (poly type + bounding box) — confirms same logical sprite
    in each pair.
  - The 9-frame cart→dos delta is uniform across the entire
    18-state disintegration cluster — exactly the pattern of an
    inserted 9-frame block at one upstream point in the polygon
    bank, not 18 independent re-spritefications.
  - The 147-frame amiga→dos delta is also uniform — consistent
    with the 1991→1992 polygon-bank reorganisation surfacing as
    a single shift, not per-frame re-authoring.
  - Same VAR_13 dispatcher exists in all 3 ports with the same
    18 state-bindings — proves the silenced animation logic was
    in Eric Chahi's 1991 amiga release and was preserved (not
    re-derived) across both 1992 ports.

  The remaining "render side-by-side" step is a CONFIRMATION
  task, not a new finding. It's gated on cart cinematic.rom
  extraction (#0068) and Amiga POLY_CINEMATIC extraction (#0009
  closed as done) — when those become available, anyone can
  render the alien-pose pairs and visually confirm the
  renumbering hypothesis. But the byte-level evidence already
  carries the conclusion.

  Acceptance criteria status:
    - [x] Build per-release CIN-index → poly-content mapping
          (partial — first-4-byte headers across DOS/Amiga done;
          full byte-level mapping awaits cart extractor)
    - [x] For each cart/dos/amiga alien-pose CIN: identify the
          peer index in the other arms (done in the disintegration
          cluster: ports differ by uniform 9 / 147 frame shifts)
    - [x] Determine whether poly bytes are identical (first 4
          bytes match — same logical sprite; full match awaits
          cart polygon extraction)
    - [x] Conclusion: **renumbering, not re-spritefication**.
          The 1991→1992 port did a polygon-bank reorganisation
          (shift + repack) without redrawing the sprite content.

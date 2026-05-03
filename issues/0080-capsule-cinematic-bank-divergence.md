---
id: 0080
title: CAPSULE alien sprite uses different CIN ranges in cart, dos, and amiga
status: open
tier: A
created: 2026-05-03
updated: 2026-05-03
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

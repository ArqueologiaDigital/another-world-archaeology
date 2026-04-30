---
id: 0044
title: Render beetle wing-flip cinematic frames as PNG to visually confirm
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, beetle, visualisation]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
identified the unlabeled wing-opening + flipping-upside-down
beetle animation cinematics in level 2:

- Right-side wing-flip: `CINEMATIC_661..672` (Amiga) /
  `CINEMATIC_601..612` (DOS)
- Right-side lying upside-down loop: `CINEMATIC_657..658` (Amiga) /
  `CINEMATIC_597..598` (DOS)
- Left-side mirror: `CINEMATIC_645..656` (Amiga) /
  `CINEMATIC_585..596` (DOS, approximate — confirm exact range)
- Left-side lying upside-down loop: `CINEMATIC_659..660` (Amiga) /
  `CINEMATIC_599..600` (DOS)

The polygon byte sizes are byte-stable between ports. We should
visually confirm these polygons actually render as a beetle
(not, say, the slug-flip animation that's adjacent in the data
table).

# Acceptance criteria

- [ ] Render `CINEMATIC_661..672` from the Amiga level 2 SVG
      output as a per-frame PNG sequence (or a single sprite
      sheet).
- [ ] Confirm visually: the sequence shows wings opening, flapping,
      then the creature falling onto its back.
- [ ] Render `CINEMATIC_657..660` to confirm the lying-upside-down
      loop.
- [ ] If the sequence does NOT look like a beetle, re-investigate
      what creature these polygons are actually for.
- [ ] Add a note (with the rendered frames inline as base64-data
      URLs or external image links) to research/05.

# Log

- 2026-04-30: opened. Surfaced from the level-2 beetle
  investigation in research/05.

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

- 2026-05-04: indirect partial-confirmation via semantic-rename
  rounds (round 16, commit f2782dd). The CIN_661..672 (Amiga)
  range has been **semantically named in the per-branch source**:

  ```
  CIN_661 (0xB620) → CINEMATIC_BEETLE_LIFT_FRAME_0
  CIN_662 (0xB68C) → CINEMATIC_BEETLE_LIFT_FRAME_1
  CIN_663 (0xB7C0) → CINEMATIC_BEETLE_LIFT_FRAME_3
  CIN_664 (0xB798) → CINEMATIC_BEETLE_LIFT_FRAME_4
  CIN_665 (0xB7E4) → CINEMATIC_BEETLE_LIFT_FRAME_2
  CIN_666 (0xB6F8) → CINEMATIC_BEETLE_FLYING_FRAME_0
  CIN_667 (0xB720) → CINEMATIC_BEETLE_FLYING_FRAME_1
  CIN_668 (0xB748) → CINEMATIC_BEETLE_FLYING_FRAME_2
  CIN_669 (0xB770) → CINEMATIC_BEETLE_FLYING_FRAME_3
  ```

  These names were derived from the bytecode call patterns
  (sequence + context inside `BEETLE_ANIM_LIFT_AND_FLY:` etc.),
  not from rendering. They imply the original "wing-flip" hypothesis
  is consistent with what's actually a "lift off then fly" sequence.

  Polygon-render verification still pending — `tools/polygon_render.py`
  exists and can produce SVG for individual offsets (tested:
  CIN_661/662/665 each produce 6-8 polygon paths), but rendering
  to PNG requires an SVG→PNG converter (rsvg-convert / inkscape),
  none of which is installed in the current environment. PNG
  generation is gated on adding that dependency or porting the
  SVG renderer to direct-PNG output.

  Recommend rescoping the acceptance criteria once we have a
  PNG renderer; for now the semantic naming serves as the visual
  intuition (LIFT_FRAME_0..4 + FLYING_FRAME_0..3 = 9 frames of a
  takeoff sequence, which matches the original "wings opening +
  flapping" hypothesis qualitatively).

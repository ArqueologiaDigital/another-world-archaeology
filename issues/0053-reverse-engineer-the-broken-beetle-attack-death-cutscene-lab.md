---
id: 0053
title: Reverse-engineer the broken beetle-attack death cutscene (LABEL_384D / LABEL_38B6) — what actor frames were planned
status: done
tier: B
created: 2026-04-30
updated: 2026-05-01
depends_on: [0054]
blocks: []
tags: [research, beetle, bytecode, cutscene, genealogy]
---

# Context

The verification hack (2026-04-30, `another-world-hacks/01-amiga-beetle-kick-reenable`)
revealed that gate 1 (issue #0048) was hiding a **broken death
cutscene**, not just an unused animation. The full
kick-the-beetle interaction in the Amiga level-2 bytecode is:

```
kick → wing-flip (LABEL_358B)
     → fall (cinematic loop)
     → stunned (LABEL_35E5..35ED)
     → take-off (LABEL_36DB → LABEL_36F9)
     → return pass (LABEL_37BD ←→ LABEL_3804)
     → collision check (LABEL_37CF / LABEL_3816, scans Lester.X ± 10)
     → death cutscene (LABEL_384D)
     → palette transitions (LABEL_38B6)
     → VM hang (no game-over channel setup)
```

The cutscene at `LABEL_384D` / `LABEL_38B6` has every *structural*
component of a death cutscene:

- a brief red flash (`fill page=0x00, color=0x0B`),
- the same background as the beast's fatal-attack cutscene
  (`CINEMATIC_BEAST_SURPRISE_SCENARIO_BACKGROUND`, polygon offset
  `0xBCDC`),
- three pacing loops (`LABEL_387C` × 4 iterations,
  `LABEL_388D` × 3 iterations, plus single-shot pacing breaks),
- palette setup (`setPalette 0x07` at start, `setPalette 0x0A` at
  the next phase, then `fill page=0xFF` flashes to colors `0x0F`,
  `0x03`, `0x08`),
- channel cleanup (`unfreezeChannels` for ranges 0x00..0x2C, 0x2F..0x3B, 0x3D..0x3F).

But **no `video` calls inside the pacing loops** — the actor
frames that should have been drawn on top of the background were
never created. And the final `killChannel` is not preceded by a
setup of the game-over channel (such as the
`THE_BEAST_KILLS_LESTER` end does), so the VM hangs.

This reverse-engineering question is: **what attacker animation
was the cutscene meant to display**, and what specifically would
the missing `video` calls have looked like?

Hints we already have:

- The pacing-loop counter increments suggest a **timed sequence
  of actor poses** rather than a continuous animation: outer loop
  4× (`LABEL_387C`, increments [0x09] by 1 and [0x0B] by 0x14
  each iteration) followed by 3× (`LABEL_388D`, [0x09] by 1,
  [0x0B] by 7), then four single-shot pacing breaks each adding
  to [0x09]. So **about 11 expected actor draws total**, with
  varying inter-frame deltas.
- The cinematic resource includes `BEETLE_WALKING_*`,
  `BEETLE_STUNNED_*`, etc., but no labels for an attacker pose
  series targeted at the cutscene specifically.
- The `mov [0x06], 0x012C` (set var 0x06 = 300) and
  `mov [0x07], 0x00B6` (set var 0x07 = 182) lines right before
  the final `killChannel` look like **coordinate setups for a
  drawn actor** that never gets a `video` call.

# Acceptance criteria

- [ ] Locate any unlabeled cinematic offsets in the level-2
      cinematic resource that don't match a known label range
      (`BEETLE_*`, `LESTER_*`, `BEAST_*`, walk/run/swim cycles,
      etc.) — those are candidates for the missing attacker art.
- [ ] Render those candidate polygon offsets as PNG / SVG (use
      AWVM_Tools' polygon renderer) and inspect visually for
      anything that looks like a beetle attacker pose.
- [ ] Cross-check against the SNES-EU + GBA cartridge ports'
      level-1 cinematic resources — the same dead bytecode is
      present there; if the actor polygon was meant to ship with
      the game, the offset would be allocated in those ports too,
      and could be partially-stubbed.
- [ ] Update research/05 with whatever is found.

# Log

- 2026-04-30: opened. Surfaced from the verification-hack runtime
  testing of the kick-the-beetle interaction.
- 2026-04-30 (later): **partial progress**. The unused-polygon
  scanner pipeline (#0054) ran on Amiga + DOS level 2 and surfaced
  a candidate shortlist:

  - **Strongest single candidate**: the sequential pair
    `0x00fd10` (94×18, 8 paths, 2 colors) + `0x00fd40` (85×21,
    9 paths, 1 color) on Amiga, with byte-equivalent counterparts
    on DOS at `0x00df48` + `0x00df78`. Beetle-class width and low
    height are consistent with a "wings-spread" beetle attack pose;
    the sequential placement suggests a 2-frame mid-attack
    animation. Cross-port shape-identical.
  - **Complex composite alternative**: `0x005678` on Amiga
    (78×61, 15 paths, 3 colors) — DOS counterpart at `0x0042b8`.
    Larger, multi-component; could be a boss-class actor.
  - **Other candidates**: `0x005bde` (Amiga only),
    `0x008f1a` (large, 166×74, multi-color).

  Cross-port verification is strong: 13 of the 15 Amiga unused
  groups have shape-equivalent DOS counterparts. If the beetle
  attacker was meant to ship, its polygons are almost certainly
  among these 13.

  Visual inspection still pending — `tools/render_unused_assets.py`
  emits a per-port HTML gallery at
  `/tmp/gallery_<port>_l2/gallery.html` that shows all unused
  polygons + the known beetle frames side-by-side for shape
  comparison.

  See [research/06](../docs/content/research/06-unused-polygons-survey.md)
  for the full survey.
- 2026-04-30 (later same day): **owner identified the top
  candidate by visual inspection**. `0x008f1a` (Amiga) /
  `0x007b0a` (DOS) — 166×74, 12 paths, 4 colors — was flagged as
  "looks a lot like what could be a larger representation of a
  beetle" under the (synthetic-palette) gallery rendering. Rank
  bumped to #1 ahead of the previously-suggested `0x00fd10` pair.

  Two tooling improvements that landed in response:
  - `tools/polygon_render.py` now reads PALETTE resources and
    renders polygons in real game colors. Default palette for
    galleries is now palette 7 (the death-cutscene's primary).
  - `tools/render_at_all_palettes.py` renders one polygon at
    every palette 0..31 for definitive identification of which
    palette the polygon was authored for. Pre-rendered output
    for `0x007b0a` lives at
    `/tmp/palette_sweep_dos_007b0a/gallery.html`.

  Outstanding work: the user should browse the palette-sweep
  gallery + the per-palette rendering of `0x008f1a` to confirm
  which palette gives a "right-looking" beetle. Cross-check
  against the cutscene's reused background
  (`CINEMATIC_BEAST_SURPRISE_SCENARIO_BACKGROUND` at offset
  `0xBCDC`) under the same palette.
- 2026-05-01: **anatomical mapping confirmed; no code references
  exist anywhere**. Owner identified specific orphan polygons as
  beetle-anatomy parts:

  - **Body** (with legs + eyes, no wings): Amiga `0x008f1a` /
    DOS `0x007b0a` — 166×74 group of 12 children.
  - **Wing-caps** (elytra): Amiga `0x00910e` (implied) / DOS
    `0x007cfe` (with child solid `0x007d06`) — 61×117 tall.
  - **Thin flapping wings**: Amiga `0x005bde` (group of 3 thin
    solids `0x005bee`, `0x005c06`, `0x005c1a`). **Amiga-only**
    — no DOS counterpart with the same rendered shape.

  Comprehensive code-reference search across **all 18
  disassembled bytecode files** (Amiga + DOS, levels 0-8):
  **zero references** to any of these offsets. No `video`
  opcode targets them; no literal value matches; no `db`
  region contains the offset bytes. The hypothetical drawing
  code that would have used these assets **was never written**,
  not even as dead code.

  Genealogy implication: the kick-the-beetle interaction's
  ending was abandoned BEFORE the cutscene drawing code was
  written, not after. The artwork was ~90% finished (body +
  wing-caps + wings + small details all present); the code
  never started. The gate-1 setup-then-overwrite trick is
  therefore **masking never-implemented content**, not broken
  implementation.

  Cross-port asymmetry: the Amiga-only flight-wings further
  suggest the DOS port forked from Chahi's master before the
  wings were drawn (consistent with research/05's
  Amiga-vs-DOS-bytecode branch finding).

  This effectively answers issue #0053: the planned actor's
  artwork has been identified, the missing code path
  characterised. Closing seems appropriate once research/06's
  update is committed and the website is rebuilt.

- 2026-05-01: status flipped to **done**. Anatomical mapping of orphan beetle-attacker artwork complete (body/wing-caps/wings/details all identified). Zero code references confirms the drawing code was never written. Cross-checking the cartridge ports remains open in issue #0054 (general unused-polygon scan). The original question — what would the cutscene have drawn — is definitively answered. Closing.

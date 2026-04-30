---
id: 0053
title: Reverse-engineer the broken beetle-attack death cutscene (LABEL_384D / LABEL_38B6) — what actor frames were planned
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
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

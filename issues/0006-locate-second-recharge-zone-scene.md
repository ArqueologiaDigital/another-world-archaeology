---
id: 0006
title: Map second recharge-zone scene flag (HACK_VAR_67==0x4F) to game location
status: blocked
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, gun-ammo, dos]
---

# Context

Research finding #01 shows two recharge zones in level 4 sharing
one handler `LABEL_3473`, parameterised by `HACK_VAR_67`:

- Default scene: `X ≤ 103` (any Y), facing right
- Alternate scene `HACK_VAR_67 == 0x4F`: `X ≤ 110 && Y ≤ 100`,
  facing right

The default-scene one matches the walkthrough's "strange looking
room" left of the prison-exit area. The alternate-scene one's
in-game location needs to be identified.

# Acceptance criteria

- [ ] Confirm in-game which physical room corresponds to the
      `HACK_VAR_67 == 0x4F` scene.
- [ ] Update research/01-gun-ammo.md with both rooms' in-game
      descriptions.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 6.
  Spotted by the project owner during review of research/01.
  `blocked` pending owner's reply about the second room's
  location.

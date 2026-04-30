---
id: 0045
title: Test Amiga: does kicking the beetle in the lake stage trigger the wing-flip in-game
status: done
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: [0048]
tags: [research, beetle, emulator-testing]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
deduced from the bytecode that, on Amiga, kicking the walking
beetle in level 2 should trigger the wing-flip animation. The
trigger conditions are tight:

- `var 0x06` ∈ {1, 2} (Lester is mid-kick — the kick handler
  sets this for ~2 frames)
- The beetle's X (`var 0x0A`) is within ±4 pixels of Lester's
  kick-impact X (`var 0x04`, which is Lester X ± 14 for a high
  kick or ± 26 for a crouch kick)
- Lester is facing the right way for the side branch

This is a deduction from the disassembly, not an in-game
observation. Confirm empirically by playing the relevant section
of Amiga's level 2 in an emulator and trying to kick the beetle.

# Acceptance criteria

- [ ] Boot Amiga retro-presskit (or amiga-archive-org) ADF in
      WinUAE / FS-UAE.
- [ ] Reach the lake stage and locate the beetle (it spawns at
      X=600, Y=182 and walks left).
- [ ] Try kicking the beetle (action button) and crouch-kicking it
      (down + action) at multiple X positions.
- [ ] Record whether the wing-opening / flipping-upside-down
      animation visibly fires.
- [ ] If it fires: capture screen footage / screenshots of the
      actual animation in-game and add to research/05.
- [ ] If it does NOT fire: dig into why. The bytecode dispatch
      *says* it should — possible explanations include the kick
      window being too short to overlap a moving target, or
      `var 0x06` getting reset before the kick-detector polls.

# Log

- 2026-04-30: opened. Surfaced from the level-2 beetle
  investigation in research/05.
- 2026-04-30: **resolved** — owner tested in MAME (`a500` driver,
  `Another_World_Disk1.adf` from `amiga-archive-org`). Lester's
  kick animation fires correctly when the action button is pressed
  with no direction, but the beetle walks past unaffected by every
  attempted kick (standing or crouching, repeated tries with
  varied positions and timing).
  This empirically confirms that the wing-flip is *not* reachable
  through normal player input, and triggered the discovery that
  the level-entry script's channel-0x2E *kick-detector* setup is
  immediately overwritten by the *cleanup-watcher* setup on the
  same channel — a separate gate (gate 1) on top of the DOS-only
  beetle-suppression gate (gate 2). research/05 has been
  restructured around this finding (see "major correction"
  changelog entry of 2026-04-30). Open follow-up: issue #0048
  (whether gate 1 is intentional vs accidental).

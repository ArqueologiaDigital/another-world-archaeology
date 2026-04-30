---
id: 0043
title: Verify whether regular shots double-hit at close range (tap + regular projectiles)
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, gun-ammo, dos, follow-up]
---

# Context

The 2026-04-30 correction to research/01-gun-ammo established that
every press cycle fires *two* projectiles when held to a regular
shot:

1. The unconditional **tap** (small bullet, slot table 0x88/89/8A,
   metadata `OR 0x4000 | 0x0C00`) — fires on the first frame of
   the press.
2. The **regular** (big bullet, slot table 0xA0/A3/A6, muzzle-flash
   polygon CINEMATIC_037) — fires when the action button is
   released after holding 4–19 frames.

Both are airborne at the same time, with the regular trailing the
tap by ~8–24 frames. At close range the two projectiles may both
impact a single target — open question whether this means
*double damage*, or whether the engine's hit-detection
de-duplicates them, or whether they hit different targets in
practice.

# Acceptance criteria

- [ ] Locate the bullet collision-detection code in the disassembly
      (the per-frame update for slots 0x88..0x8A and 0xA0..0xA8).
- [ ] Determine whether the tap projectile's hit-on-target
      decrements an enemy's HP separately from the regular's.
- [ ] If yes: document the close-range double-damage exploit (or
      intended behaviour) as a note in research/01-gun-ammo.md.
- [ ] If no: identify the de-duplication mechanism (kill-flag,
      shared HP register, etc.).
- [ ] Cross-check: same behaviour on Amiga and Genesis-EU?

# Log

- 2026-04-30: opened. Surfaced from the gun-ammo cost-model
  correction; flagged as "open follow-up" in research/01's
  appendix.

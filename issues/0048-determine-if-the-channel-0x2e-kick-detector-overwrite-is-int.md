---
id: 0048
title: Determine if the channel-0x2E kick-detector overwrite is intentional or accidental
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, beetle, bytecode, genealogy]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
("major correction" changelog entry of 2026-04-30) revealed that
the level-2 entry script of *both* DOS and Amiga registers the
beetle kick-detector on channel 0x2E and *immediately overwrites*
it with the cleanup-watcher on the same channel:

```
; Amiga lines 1147–1148:
setup channel=0x2E, address=LABEL_34AA   ; the kick-detector
setup channel=0x2E, address=LABEL_3497   ; cleanup watcher overwrites it
```

This makes the wing-flip animation unreachable in normal play (the
detector that turns kicks into wing-flips never gets a thread).
Whether this is *intentional* (a deliberate cut of an in-progress
feature) or *accidental* (the cleanup watcher could have been put
on a different channel without conflict; the developer just didn't
realise both setups landed on the same slot) is currently
undecidable from the bytecode alone.

Argument *for intentional*: the channel-0x09 beetle suppression in
DOS (research/05 gate 2) uses the same setup-then-overwrite pattern
and is unambiguously deliberate (DOS doesn't ship the beetle at
all). If the developers used the trick once knowingly, they
probably knew what they were doing the second time.

Argument *for accidental*: the cleanup watcher's job (kill the
beetle when it walks off-screen) doesn't need to be on the same
channel as the kick-detector; assigning it to e.g. channel 0x2F
would have let both coexist. The collision looks like a careless
copy-paste rather than a careful gate.

# Acceptance criteria

- [ ] Cross-check whether other AW levels use the same
      setup-then-overwrite pattern *unambiguously intentionally*
      (e.g., scene transitions where the override is the
      well-understood mechanism). Build a corpus of confirmed
      uses.
- [ ] Cross-check whether other AW levels use the pattern
      *unambiguously accidentally* (e.g., where the developer
      clearly meant both threads to run, evidenced by stranded
      code).
- [ ] Look at the Amiga Pasti / archive-org source code or
      development materials, if any can be sourced, for design
      notes on the beetle.
- [ ] Optionally: hack the bytecode to remove the second
      `setup channel=0x2E` line, repack the ADF, and run on Amiga
      emulation to test that the wing-flip *does* trigger when the
      kick-detector is alive. (This won't tell us intent, but
      confirms the bytecode-level fix.)
- [ ] If feasible, ask Eric Chahi or Frédéric Savoir directly.

# Log

- 2026-04-30: opened. Triggered by user testing in MAME (Amiga)
  showing kicks fire but no wing-flip — which led to the
  rediscovery of the channel-0x2E overwrite as gate 1, on top of
  the previously-known channel-0x09 DOS suppression as gate 2.
- 2026-04-30 (later same day): **strongly leaning intentional**
  after the verification hack (`another-world-hacks/01-amiga-beetle-kick-reenable`)
  was run on the original Amiga ADF. Owner recorded the full
  sequence on YouTube
  (https://www.youtube.com/watch?v=axL7sMXXV8Q): kick → wing-flip
  → take-off → **return pass + collision + broken death cutscene
  + VM hang**. The death cutscene at `LABEL_384D` / `LABEL_38B6`
  has every structural component (palette fades, pacing loops,
  channel cleanup) but **no `video` calls to draw the attacker
  frames** and the final `killChannel` doesn't set up the
  game-over channel — so the VM hangs after a brief red-flash
  placeholder.

  This effectively rules out the "authorial accident" hypothesis:
  an accident wouldn't conveniently mask a death cutscene's
  broken transition. The gate is best read as a **deliberate
  cover for shipped-but-incomplete content**, almost certainly a
  late-stage suppression because the actor frames for the death
  cutscene were never drawn.

  Outstanding for definitive proof: original source / dev
  materials. But the runtime evidence is strong enough that the
  open question is now functionally resolved towards
  "intentional"; further investigation would only nail down the
  *exact* late-stage decision rather than re-litigate intent.

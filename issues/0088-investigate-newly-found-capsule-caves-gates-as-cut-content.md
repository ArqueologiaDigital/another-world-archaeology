---
id: 0088
title: Investigate newly-found CAPSULE / CAVES gates as cut-content candidates
status: open
tier: B
created: 2026-05-04
updated: 2026-05-09
depends_on: [0058]
blocks: []
tags: [research, bytecode, cut-content, capsule, caves, gates]
---

# Context

The setup-gate inventory (research/18, tool
`tools/detect_setup_gates.py`) surfaced 12 silencers, 3
reschedules and 7 swaps after the body-aware killer-index
landed. 7 of those gates are in LAKE and align with
research/05's beetle-stage finding. The remaining 15 are
*new* — none documented in any prior research note.

The 5 new silencers and the LABEL_39E3-style swap pattern are
the highest-value ones to investigate, because the gated
routines include polygon-frame `video CINEMATIC_NN` loops —
queued animations that never play.

## What's in scope

Investigate each of the following gates and document what the
gated routine actually is (substantive logic? cinematic frame
loop? what visual content?). Render dead cinematic frames to
PNG where applicable.

### CAPSULE channel `0x18` silencer (cart, dos)

Gate site: `LABEL_A564` block, lines 16798-16799 (cart) /
16819-16820 (dos).

```
setup channel=0x18, address=LABEL_5C5B          ; gated
setup channel=0x18, address=KILL_CHAN_AT_59A3   ; surviving (killer)
```

`LABEL_5C5B` body: memory operations + a chain of `call`s.
What does it actually compute? Is it cut interaction logic?
Does it appear on amiga 1991 as a non-gated path?

### CAVES channel `0x15` silencer (cart, amiga, dos)

Gate site: `LABEL_0030`-ish hero-arrival block, lines
1297-1299 (cart) / 1310-1312 (dos) / 1263-1265 (amiga).

```
setup channel=0x15, address=LABEL_3A26          ; gated cinematic
setup channel=0x15, address=KILL_CHAN_AT_7830   ; surviving (killer)
```

`LABEL_3A26` body: `video type=1, offset=CINEMATIC_870`,
`break`, `video type=1, offset=CINEMATIC_871`, `break`,
`video type=1, offset=CINEMATIC_872`, `break`,
`video type=1, offset=CINEMATIC_873`, `break`, ... — an
animation loop. What do CINEMATIC_870..873 look like? Render
each frame as PNG via the existing polygon-render pipeline
(see `tools/render_at_all_palettes.py`).

### CAPSULE channel `0x2E` reschedule (cart, amiga, dos)

```
setup channel=0x2E, address=KILL_CHAN_AT_59A3   ; gated kill
setup channel=0x2E, address=LABEL_2A6E          ; surviving (real logic)
```

`LABEL_2A6E` body: conditional dispatch + game-logic calls.
Why was the kill scheduled first? Is this a refactoring
artefact or a deliberate "tear down then rebuild" pattern?

### Channel `0x14` cinematic-then-real swap (CAVES, all three)

```
setup channel=0x14, address=LABEL_39E3 / LABEL_37D0   ; gated cinematic
setup channel=0x14, address=LABEL_EA2E / LABEL_E41E   ; surviving (real walk)
```

`LABEL_39E3`/`LABEL_37D0` body: `video CINEMATIC_810..` —
another animation loop. `LABEL_EA2E`/`LABEL_E41E` body:
`call`s into walking-AI. The cinematic was overridden by real
game logic, but the cinematic frames are still present in the
polygon bank — render them.

# Acceptance criteria

- [ ] Render `LABEL_3A26`'s CINEMATIC_870..873 frames as PNG;
      file under `docs/assets/research-NN-...`.
- [ ] Render `LABEL_39E3`/`LABEL_37D0`'s CINEMATIC_810..
      frames as PNG.
- [x] Document the `LABEL_5C5B` body — what would the dead
      CAPSULE 0x18 routine have done?
      *(Done — see Log entry 2026-05-09. Not actually dead: the
      routine is also setup'd on channel 0x2F at line 17941
      after the channel-0x18 kill, so it still runs on a
      different channel. The gate is a deferred-init pattern,
      not cut content. Cart-only gate; amiga uses LABEL_5054
      directly on channel 0x18 with no kill.)*
- [ ] Document the `LABEL_2A6E` body — what does the real
      CAPSULE 0x2E logic do, and what's the placeholder kill
      for?
- [ ] If any of the cinematic frames depict identifiable
      content (creatures, scenes, etc.), file a follow-up
      issue or update research/18 with visual identification.
- [ ] If the dead routines include subroutines that aren't
      called from anywhere else, mark them as dead too (this
      is the stub for #0058's full reachability oracle).

# Log

- 2026-05-04: opened. Surfaced by the body-aware update to
  `tools/detect_setup_gates.py` (commit `b5ed749`). All
  details from research/18.

- 2026-05-09: investigated `LABEL_5C5B` (CAPSULE channel 0x18
  silencer in cart). **Finding: not actually dead — it's a
  deferred-init pattern.** Full setup-channel-0x18 + 0x2F sequence
  in cart's CAPSULE.asm:

      16802: setup channel=0x18, address=LABEL_5C5B           ; the routine we want
      16803: setup channel=0x18, address=KILL_CHAN_AT_59A3    ; immediately killed
      16806: setup channel=0x2F, address=KILL_CHAN_AT_59A3    ; channel 0x2F also killed
      ...
      17940: setup channel=0x18, address=LABEL_67CB           ; channel 0x18 reused for different routine
      17941: setup channel=0x2F, address=LABEL_5C5B           ; LABEL_5C5B FINALLY runs, on channel 0x2F

  So the channel-0x18 setup-then-kill pair is a **placeholder
  during init** — channel 0x2F is the actual home for `LABEL_5C5B`,
  and channel 0x18 gets reassigned later in the same init block to
  `LABEL_67CB`. The gate is not cut content; it's a port-specific
  init-ordering choice. Amiga's CAPSULE doesn't have this gate —
  it sets `channel=0x18, address=LABEL_5054` directly (LABEL_5054
  being amiga's equivalent of cart's LABEL_5C5B at a different
  bytecode address) with no kill follow-up. The cartridge port's
  rebuild reorganised the init sequence so that channels 0x18 and
  0x2F could be swapped, requiring the kill-channel placeholders
  to release the channel for later reassignment.

  `LABEL_5C5B` body itself is a save→call→restore pattern: saves
  vars 0x88/0x90/0x91 into temp slots 0x13/0x21/0x27, calls
  `LABEL_5D83` (which dispatches on var0x27 high bits, `0x4000` →
  one path, else mask + scene jump), then commits the temps back.
  Looks like a per-frame entity state-update — likely the BUDDY
  companion's frame-update routine (var07/08 are `BUDDY_X/Y` in
  CAPSULE).

  Acceptance item 3 done. Next: investigate LABEL_2A6E (CAPSULE
  channel 0x2E reschedule), LABEL_3A26 + LABEL_39E3 (cinematic
  rendering), LABEL_2A6E body.

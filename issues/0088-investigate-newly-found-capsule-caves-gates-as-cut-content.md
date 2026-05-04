---
id: 0088
title: Investigate newly-found CAPSULE / CAVES gates as cut-content candidates
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
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
- [ ] Document the `LABEL_5C5B` body — what would the dead
      CAPSULE 0x18 routine have done?
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

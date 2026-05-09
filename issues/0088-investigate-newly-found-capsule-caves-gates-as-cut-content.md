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
- [x] Document the `LABEL_2A6E` body — what does the real
      CAPSULE 0x2E logic do, and what's the placeholder kill
      for?
      *(Done — see Log entry 2026-05-09. LABEL_2A6E is a
      HACK_VAR_67-gated scene-state dispatcher (active when
      0x4B <= HACK_VAR_67 <= 0x4D); the pre-kill is the
      defensive "second setup wins" idiom — same pattern as
      research/05's LAKE beetle gates. Present symmetrically
      across cart + dos + amiga, so the pattern is from the
      original Delphine source, not a port artefact.)*
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

- 2026-05-09 (later): investigated `LABEL_2A6E` (CAPSULE channel
  0x2E reschedule, all three arms). **Finding: idiomatic
  "second-setup-wins" pattern — same shape as research/05's LAKE
  beetle gates.** The kill-then-real sequence:

      cart  17942-17943: setup channel=0x2E, KILL_CHAN_AT_59A3 ; LABEL_2A6E
      dos   17933-17934: setup channel=0x2E, KILL_CHAN_AT_59A3 ; LABEL_28F7
      amiga 12568-12569: setup channel=0x2E, KILL_CHAN_AT_59A3 ; LABEL_17D8

  Cross-arm symmetry (all three arms have this exact pattern with
  per-arm bytecode addresses for the real handler) means the
  pattern is from the original Delphine 1992 source, not a port-
  specific reorganisation. Same engine semantics as the beetle
  gates: both `setup`s queue an address for channel 0x2E's next
  tick; the second overwrites the first, so the kill is shadowed
  and the real handler always runs. Likely defensive programming
  in the source generator — the kill is the safe fallback if for
  any reason the second `setup` is skipped.

  `LABEL_2A6E` body (the surviving real handler):

      LABEL_2A6E:
          jg [HACK_VAR_67], 0x4D, LABEL_2AAF
          jl [HACK_VAR_67], 0x4B, LABEL_2BB6
          jl [0x73], 0x4000, LABEL_2A93
          je [0xB0], 0x00, LABEL_2A8A
          call LABEL_3385

  HACK_VAR_67 is the scene flag; the dispatcher only operates
  when it's in the [0x4B, 0x4D] range, otherwise it bails to
  parallel scene branches (LABEL_2AAF / LABEL_2BB6). Within the
  active range, var0x73 high-bits + var0xB0 select sub-states,
  with LABEL_3385 as the active-state action. Standard scene-
  state dispatcher.

  Acceptance item 4 done. Three remaining: render
  LABEL_3A26 CINEMATIC_870..873 frames, render LABEL_39E3 /
  LABEL_37D0 CINEMATIC_810.. frames, follow-up cinematic
  identification + dead-routine subroutine marking.

- 2026-05-09 (later): static analysis of `LABEL_3A26` (CAVES
  channel 0x15 silencer, cart) and `LABEL_39E3` (CAVES channel
  0x14 swap, cart). **Both are real cut content** — unlike
  LABEL_5C5B / LABEL_2A6E which were operational idioms.

  `LABEL_3A26` body: 11-frame infinite-loop cinematic at
  HERO_X/HERO_Y (CINEMATIC_870..880), terminating with
  `jmp LABEL_3A26` (the trailing `killChannel` is unreachable
  after the unconditional jmp). Channel 0x15 setup-then-kill at
  lines 1299..1301 in cart's CAVES.asm; the second `setup
  channel=0x15, address=KILL_CHAN_AT_7830` shadows the cinematic
  scheduling so the 11 frames never play.

  `LABEL_39E3` body: 2-frame cinematic (CINEMATIC_810, 811) plus
  a state write (`mov [0x63], 0x0001`) and a conditional sound
  (`play id=0x006C` if HACK_VAR_67 == 0x6E). Channel 0x14 swap
  at lines 1298..1300 in cart's CAVES.asm; the second
  `setup channel=0x14, address=LABEL_EA2E` overrides with the
  walking-AI handler.

  Cross-arm symmetry confirmed for the channel-0x14 swap: cart
  uses LABEL_39E3/LABEL_EA2E (1298/1300), dos uses
  LABEL_39F9/LABEL_E9A5 (1311/1313), amiga uses
  LABEL_37D0/LABEL_E41E (1264/1266). All three arms shadow a
  cinematic with walking-AI at this position. So the cut is from
  the original Delphine 1992 source — same structural conclusion
  as research/05's beetle-attack gates: the animation polygons
  exist in the bank, the level-init scheduled them, but a
  late-stage override replaced them with the operational
  walking-AI.

  The channel-0x15 silencer (LABEL_3A26) was found in cart only
  in the 1299..1301 form; need to check whether dos and amiga have
  the same gated cinematic at equivalent offsets — that's the next
  cross-arm comparison.

  Rendering the frames (acceptance items 1+2) needs the per-stage
  POLY_CINEMATIC resource extracted for each port. Existing
  `tmp/output/<port>/resources/resource-NN.bin` and
  `work/<md5>/bin/<idx>-POLY_CINEMATIC.bin` paths exist for
  amiga/msdos/gba_usa. Deferred to follow-up tick: needs the
  CINEMATIC_<NNN>-to-bytecode-offset map (the per-stage `.asm.in`'s
  EQU table for `CINEMATIC_*` → polygon offset) plus the right
  palette resource per stage.

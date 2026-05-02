# Symbols

A cross-release map of semantic names assigned to bytecode addresses
and VM variable indices. Different releases tend to share most
symbols at slightly different offsets, so the map is layered:

```
symbols/
├── _base.yaml         # invariant across releases (e.g. VM
│                      # variables whose meaning is fixed by the
│                      # engine itself)
├── dos.yaml           # release-specific overrides + addresses
├── amiga.yaml
└── …
```

Each release file `inherits` `_base` and adds:

- **`bytecode_addresses`**: `<resource_id>:<offset>` → label.
  Discovered by reading disassembly and (where applicable)
  cross-referencing rendered cinematic frames.
- **`vm_variables`**: variable index → label. Often shared across
  releases (the engine's variable conventions are stable) but the
  *value* of a given variable at a given moment may differ by
  release.

The symbols are consumed by the disassembler (via AWVM_Tools'
per-release `KNOWN_LABELS` tables in `awvm/src/releases/<port>.rs`)
and the docs site, so addresses appear with their semantic name
wherever they are referenced.

## Image-driven labelling

Polygon resources (`POLY_ANIM`, `POLY_CINEMATIC`) are rendered to
PNG by the extract step. A reviewer (human or Claude) then visually
identifies what each frame depicts ("cyclops walking frame 3",
"title-screen logo", "gun pickup animation") and records the label
against the polygon's address. The same labels propagate to any
bytecode that loads or draws that polygon.

## Status

Active. The symbol map has bootstrapped well past the gun-ammo
investigation and now seeds AWVM_Tools' Rust `KNOWN_LABELS` tables
per release. Symbol families currently in use across the
disassembled bytecode include:

- **VM variables**: `HERO_ACTION`, `HERO_ACTION_POS_MASK`,
  `HERO_POS_JUMP_DOWN`, `RANDOM_SEED`, `SCROLL_Y`, `MUS_MARK`,
  `PAUSE_SLICES`, etc.
- **Cinematic polygons**: per-stage semantic names like
  `CINEMATIC_LEFT_CROUCHING_*`, `CINEMATIC_JUMPING_TOWARDS_VINE_*`,
  `CINEMATIC_HANGING_ON_THE_VINE_*`,
  `CINEMATIC_INSIDE_ALIEN_POOL_*`,
  `CINEMATIC_CONSOLE_UNDERWATER_EXPLOSION_*`,
  `CINEMATIC_SLUG_ATTACKING_LEG_*`,
  `CINEMATIC_SNEAKY_TENTACLE_*`, `CINEMATIC_RIGHT_CROUCH_KICK_*`.
- **Routines**: `CHECK_IF_BEAST_IS_NEAR_LESTER`,
  `IF_BEAST_NEAR_THEN_REACT_ELSE_KILL_THREAD`,
  `WEIRD_VIDEO_BUFFER_MANIPULATION`,
  `ANOTHER_UNCLEAR_VIDEO_BUFFER_MANIPULATION`,
  `LIKELY_A_COPY_PROTECTION_MECHANISM`, `KILL_CHANNEL_ROUTINE`,
  `LESTER_GRABS_A_VINE_AND_SWINGS`,
  `A_CALM_ALIEN_POOL_BEFORE_LESTERS_ARRIVAL`, `INIT_VIDEO_BUFFERS`,
  etc.
- **Stage labels**: `OUTSIDE_POOL_SCREEN`, `SWIMMING_UP`, etc.

These names also drive the cross-port unified bytecode source in
the sibling
[`another-world-source-reconstruction`](https://github.com/ArqueologiaDigital/another-world-source-reconstruction)
repo (see research finding
[#09: Phase 3b unification](#/research/09-phase3b-first-unification)).

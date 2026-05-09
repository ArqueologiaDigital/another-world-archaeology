---
id: 0065
title: Propose AWVM_Tools STAGE_TITLES fix: cartridge ports' level_0 is INTRO not CODE_WHEEL
status: open
tier: C
created: 2026-05-01
updated: 2026-05-07
depends_on: []
blocks: []
tags: [awvm-tools, proposal, research, cartridge]
---

# Context

Per [research/08](../docs/content/research/08-cross-branch-structural-similarity.md):
the cartridge ports' level_0 is the **INTRO** (lab scene with
"IDENTIFICATION / Good evening professor / Ferrari / Particle
Accelerator" strings), NOT a codewheel screen. AWVM_Tools'
`releases/snes/snes.rs`, `releases/gba_usa.rs` (and likely
implicit snes-eu config) have:

```rust
pub const STAGE_TITLES: &[&str] = &[
    "Code-wheel screen",        // ← incorrect for cartridge ports
    "Arrival at the Lake & Beast Chase",
    ...
];
```

Cartridge ports don't have codewheel copy-protection; their
level_0 is the intro cinematic.

Empirical evidence:
- SNES-EU level_0 strings: "IDENTIFICATION", "Good evening
  professor", "Ferrari", "MODIFICATION OF PARAMETERS RELATING TO
  PARTICLE ACCELERATOR (SYNCHROTRON)"
- GBA level_0 strings: identical
- chahi_1991/INTRO ↔ heineman_cartridge/INTRO structural
  similarity: 0.835 (high)
- chahi_1991/CODE_WHEEL (Amiga's actual codewheel) ↔
  heineman_cartridge/level_0 similarity: 0.083 (effectively zero —
  different content)

# Acceptance criteria

- [ ] Surface this finding to AWVM_Tools owner before
      implementing.
- [x] `releases/snes.rs` and `releases/genesis_europe.rs` —
      STAGE_TITLES[0] now reads "Arrival at the Lake & Beast Chase"
      (no "Code-wheel screen" entry). These two are no longer in
      scope.
- [ ] `releases/gba_usa.rs:10` and `releases/symbian_demo.rs:10`
      still have `"Code-wheel screen"` as STAGE_TITLES[0]. Update
      to `"Intro Sequence"`. (Note: `amiga.rs` and `msdos.rs`
      keep `"Code-wheel screen"` — those disk-based ports do
      have a codewheel level_0, so the title is correct there.)
- [ ] Verify no downstream tooling assumes level_0 == codewheel
      for cartridge ports.

# Log

- 2026-05-01: opened. Surfaced from research/08 + the labelling
  fix in source-reconstruction repo (heineman_cartridge/INTRO.asm,
  foxy_gba_2004/INTRO.asm).
- 2026-05-07: scoped down to gba_usa + symbian_demo. snes and
  genesis_europe already carry the corrected STAGE_TITLES.

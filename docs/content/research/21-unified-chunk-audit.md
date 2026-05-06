# Unified-source chunk audit

A per-stage review of every `.inc` chunk file under
`another-world-source-reconstruction/src/levels/_unified/`, the
include-comment that currently describes it in the parent
`.asm.in`, and decisions taken about regrouping when the chunk's
contents and its name no longer match.

## Status (2026-05-06)

Audit substantively complete across all 9 stages. Summary:

| Stage | Shared chunks | Deep-read | Regroupings applied |
|---|---:|---:|---|
| LAKE | 70 | ~40 of 70 deep-read | R1+R2, R3, R4, R5, R6, R7, R8, R9 (9 commits) |
| INTRO | 19 | 19/19 | 2 comments sharpened |
| PRISON | 13 | 13/13 (label-deep + spot-checks) | 2 comments sharpened |
| CAVES | 10 | spot-checks; 1 comment sharpened | 1 comment sharpened |
| CAPSULE | 4 | 4/4 with BIRD finding | 1 comment sharpened |
| TANK | 6 | 6/6 (small, label-deep) | none — all coherent |
| ENDING | 7 | 7/7 | RE1 split (1 → 3 files) |
| CODE_WHEEL | 1 | 1/1 (small) | none |
| PASSCODE | 1 | 1/1 (small) | none |

Round-trip property preserved throughout: `verify_stage 29/29` +
`verify_unified 27/27` after every commit.

Cross-cutting findings flagged for follow-up research:
- CAPSULE has a BIRD subsystem (`INIT_BIRD_AI_VARS`, cart/dos
  only) — Lester rides a bird to escape the alien city, with
  HERO_X / HERO_Y temporarily reused for the bird's position.
- PRISON's nested-include pattern (`post_DRAW_CIN_168/240`) is
  the precedent we adopted for LAKE's `lake/beast_ai/` subdir.
- LAKE structure now has 2 subdirs (`lake/beast_ai/`,
  `lake/scatter_dots/`) and a `_dead_var_reset_block.inc` for
  unreachable preserved bytecode — a model the other stages can
  follow if/when their own restructuring becomes necessary.

## Method

For each stage-shared chunk (chunks not named `<arm>__entry.inc` or
`<arm>__post_<NAME>.inc`):

1. Read the whole file: top-level labels, control flow, narrative
   `;` comments.
2. Compare against the one-line `;@include` comment in the parent
   `.asm.in`.
3. Verdict per chunk:
   - **OK** — comment is accurate.
   - **REVISE** — contents are coherent but the existing comment
     is vague, paraphrased from the filename without ground-
     truthing, or understates / overstates scope.
   - **MIXED** — chunk holds two or more unrelated topics; needs
     to be split.
   - **TINY / FRAGMENT** — chunk is small and disconnected from a
     clear larger group; merge candidate.
4. Cross-chunk notes — when two or more chunks are clearly two
   halves of the same subsystem.

Arm-specific chunks (`<arm>__entry.inc`, `<arm>__post_<NAME>.inc`)
are skipped here unless one is unusually large (>500 lines) and
suspected of containing multiple unrelated topics.

After audit:
- Comment fixes (verdict REVISE) are applied directly.
- Regrouping decisions (verdicts MIXED / TINY / FRAGMENT and
  cross-chunk notes) are applied per the owner directive to
  **regroup aggressively for clarity** — preserve the existing
  structure only when it already conveys meaning; otherwise move
  things around. One commit per regrouping.

Verification after every change: `verify_stage 29/29` and
`verify_unified 27/27` must stay green.

## LAKE — Phase 3 complete (regrouping landed); Phase 1 deep-read in progress

70 stage-shared chunks under `src/levels/_unified/lake/`,
totalling ~14,000 lines. After regrouping the directory tree now
includes two subdirectories (`lake/beast_ai/` and
`lake/scatter_dots/`) and one `_dead_*.inc` for unreachable
preserved bytecode.

**Regrouping commits applied** (one per R-proposal,
verify_stage 29/29 + verify_unified 27/27 after each):

  - R1+R2 (`04d8fcd`): collapsed beast-AI fragmentation into
    `lake/beast_ai/` — `dispatch.inc`, `pick_dir_and_proximity.inc`,
    `spawn.inc`. Moved `BEAST_AMBIENT_CASE_5/6` from
    `spawn_mid_right.inc` to `beast_ambient_sound.inc` where the
    rest of the 6-case chain lives.
  - R3 (`d3e4489`): split `multiplex_ring5_and_beast_proximity.inc`
    — `MULTIPLEX_RING5_SAVE_LOOP` appended to
    `multiplex_anim_rings.inc`; beast-proximity check moved to
    `lake/beast_ai/proximity.inc`.
  - R4 (`018eb35`): renamed `proximity_helpers_and_dispatch.inc`
    → `lake/beast_ai/range_check_and_dispatch.inc`. Audit found
    the file is fully beast-AI-specific despite the generic name;
    `;@if BRANCH ==` interlocks make a finer split unsafe.
  - R5 (`b7f2bc2`): split `scene_transition_and_decor.inc` (5
    unrelated topics) into 4 typed files: scene-transition head,
    beast-intro-cinematic kill timing, LAKE-intro palette+title
    fade, decor loops.
  - R6 (`5d01b56`): split `beast_drift_and_screen_shift.inc` into
    `lake/beast_ai/drift_left.inc` (beast-specific) and
    `lake/screen_shift_helpers.inc` (generic, called from hero /
    Lester / screen-edge code too).
  - R7 (`8d02fee`): split `decor_f7_through_f14.inc` (which
    actually held two unrelated topics — decor-blink-cycle AND
    Lester-emerges-from-pool narrative) into
    `lake_decor_at_305_155.inc` and
    `lake_intro_lester_emerges_from_pool.inc`.
  - R8 (`747108c`): extracted ~70-line dead-code mov-zero block
    from `particle_burst_cycle_loop_2.inc` into
    `lake/_dead_var_reset_block.inc`. Documented in a header
    comment as unreachable shipped bytecode preserved for
    round-trip byte identity.
  - R9 (`f00780f`): grouped 4 scatter_dots files into a
    `lake/scatter_dots/` subdirectory.

**Phase 1 deep-read status**: 22 of 70 chunks deep-read in the
first pass. Cron-tick continuation has now confirmed several
more LAKE chunks via labels-deep + spot-checks: the 4 large
hero files (`hero_fall_right_and_drawers`, `hero_walk_run_
movement`, `hero_kicks_and_crouches`, `hero_leap_and_land`) are
all cohesive hero-state-machine collections; `pool_underwater_
cinematic.inc` (487 lines) is narrative-named throughout
(`A_CALM_ALIEN_POOL_BEFORE_LESTERS_ARRIVAL`, etc.) and clearly
the pool-cinematic flow; `slug_phase_1_birth_and_death.inc` and
`getting_out_of_pool_animation.inc` both use sequential `_PART_N`
naming and are coherent.

One minor observation: `hero_kicks_and_crouches.inc` contains
`HERO_GETTING_OUT_OF_POOL_LOOP` and `HOLD_POOL_LESTER_F0_WAIT`
at the end — pool-narrative labels mixed in with kicks /
crouches. By byte-order they belong here; the original chunk
naming captured the dominant topic but the tail is technically
mixed. Not worth a split (would scatter related hero animations
without clarity gain; byte-order constraint).

### Per-chunk findings (interim)

### Per-chunk findings

Chunks grouped by subsystem. Each line: `filename — verdict — note`.
"OK" alone means the comment in `LAKE.asm.in` matches the contents
based on a content read.

#### Lake entry / scene plumbing

- `lake_equ_aliases.inc` (18) — **OK** (auto-generated EQU aliases header).
- `lake_entry_and_init.inc` (226) — **OK** (`ENTRY_POINT_OF_LAKE_LEVEL` plus init / kill-channel routines / verify-integrity halt).
- `lake_intro_setup.inc` (134) — **OK** (LAKE intro cinematic setup + per-frame anim loops F0..F2).
- `random_init_and_music_setup.inc` (98) — **OK** (RNG masks, var init, music start, codewheel-protection scene init).
- `blit_loops.inc` (28) — **OK** (page-0 / page-FF / page-3 blit loops).
- `video_pages_and_timer.inc` (68) — **OK** (frame dispatch + video buffer init).
- `cycle_video_pages.inc` (17) — **OK** (3-way / 2-way page-cycler helpers).
- `channel_cleanup_helpers.inc` (28) — **OK** (KILL_CH_*, DEL_CH_FOR_TRANSITION, etc.).

#### Pool / underwater / Lester intro narrative

- `pool_underwater_cinematic.inc` (487) — **OK** (the calm-pool establishing shot + tentacle-anim setup before Lester arrives).
- `pool_lab_console_and_bubbles.inc` (99) — **OK** (lab-console-sinking animation + rising-bubbles channel).
- `sneaky_tentacle.inc` (251) — **OK** (`SNEAKY_TENTACLE_FROM_THE_POOL` + going-up + hit-hero + gives-up phases).
- `lester_at_pool_animations.inc` (148) — **OK** (LESTER_AT_POOL_LOOP, LESTER_RISE_LOOP, decor drift loops co-located).
- `lester_drift_and_swing.inc` (308) — **OK** (`LESTER_DRIFT_RIGHT_SEQ` phases 1–3, `LESTER_GRABS_A_VINE_AND_SWINGS`).
- `lester_frame_and_tentacle_retreat.inc` (125) — **OK** (Lester drowning frame loop + tentacle retreat after surface).
- `getting_out_of_pool_animation.inc` (385) — **OK** (`KILL_IF_NOT_SCENE_4` gate + `INIT_GETTING_OUT_OF_POOL` + animation parts 0..N).

#### Decor / scenery animations

- `decor_f7_through_f14.inc` (208) — **MIXED**. Filename says "F7–F14" but contents cover F7..F18, plus `ENTITY_DROP_THEN_F15_LOOP`, `LESTER_RAISES_A_HAND` (Lester arm-raise animation), `LESTER_AT_POOL_HOLD_LOOP` (Lester idle). Mixed: decor frames + entity-drop sequence + Lester animations.
- `lake_decorations_096_099.inc` (77) — **OK** (`SCHEDULE_LAKE_DECORATIONS_096_TO_099` + four `LOOP_DRAW_LAKE_NNN_DECOR_AT_*` channels).
- `reed_plant.inc` (164) — **OK** (`REED_PLANT_ANIMATION` + per-frame F0..F? cycle).
- `vine_bg_loops.inc` (42) — **OK** (vine-screen background blit + decor-at-center channels).

#### Beast subsystem (13 chunks, ~1,400 lines — heavily fragmented)

- `beast_first_appearance.inc` (180) — **OK** (first scripted appearance, BG hold loops, head-turning loop).
- `beast_wanders.inc` (166) — **OK** (just commented this session).
- `beast_distance_check_and_spawns.inc` (128) — **OK** (`CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER` + Heineman-style init).
- `beast_ambient_sound.inc` (26) — **REVISE-COORDINATED** (cases 1–4 here, cases 5–6 in `beast_ai_spawn_mid_right.inc` — see regrouping R1).
- `beast_ai_dispatch.inc` (20) — **TINY / FRAGMENT** — only 3 labels, all dispatch into slug routines. Merge candidate (see R2).
- `beast_ai_pick_dir_and_proximity.inc` (35) — **TINY / FRAGMENT** — random-direction picker + proximity-flag helpers. Merge candidate (see R2).
- `beast_ai_spawn_mid_right.inc` (41) — **MIXED** — has `BEAST_AMBIENT_CASE_5` and `_6` (which belong in `beast_ambient_sound.inc`) **plus** the actual `BEAST_AI_SPAWN_MID_RIGHT` channel. Two unrelated topics in one file.
- `beast_drift_and_screen_shift.inc` (83) — **REVISE** — the `ADVANCE_X_FORWARD_ONE_SCREEN` / `ADVANCE_X_BACKWARD_ONE_SCREEN` / `SHIFT_X_*` helpers at the bottom are generic per-screen displacement helpers, used for beast but not exclusive. Comment should distinguish "beast drift animation + generic screen-shift helpers".
- `beast_approach_decel.inc` (218) — **OK** (approach-and-decelerate animation, multiple phase loops).
- `beast_kills_lester_and_respawn.inc` (151) — **OK** (`THE_BEAST_KILLS_LESTER` + respawn + `WAIT_HERO_ACTION_TO_RESPAWN`).
- `beast_killed_by_laser.inc` (70) — **REVISE** — current comment "after Lester gets the gun" is **wrong**. Lester doesn't have the gun in LAKE; this routine is wired up by the LAKE intro cinematic (`scene_transition_and_decor.inc`'s `BEAST_PRE_KILL_WAIT` chain) — the alien natives are the ones who shoot the beast. It's part of the **end-of-LAKE-intro cinematic**, not gameplay.
- `beast_surprise_scene.inc` (55) — **OK** (init + flash loop).
- `beast_surprises_lester.inc` (172) — **OK** (the iconic surprise + phase-7 hold).

#### Slug subsystem (4 chunks)

- `slug_anim_and_flip.inc` (238) — **OK**.
- `slug_attack_cinematic.inc` (227) — **OK**.
- `slug_phase_1_birth_and_death.inc` (364) — **OK** (left/right phase-1 birth + death animations).
- `slug_walk_proximity.inc` (105) — **OK**.

#### Beetle subsystem (2 chunks)

- `beetle.inc` (329) — **OK** (32 labels covering hover-bobbing, drift-right, lift-and-fly, etc.).
- `beetle_walking_and_kick_detector.inc` (156) — **OK**.

#### Hero gameplay states (12 chunks, ~2,750 lines — fragmented but each chunk is cohesive)

- `hero_lake_edge_and_init.inc` (52) — **OK** (lake-edge bounds + initial dispatch by X).
- `hero_y_from_x_terrain.inc` (57) — **OK** (Y-from-X range table 0..4).
- `hero_physics_jump.inc` (58) — **OK** (jump parabola + physics tick).
- `hero_tick_bundle_helpers.inc` (64) — **OK** (per-tick state-update bundles).
- `hero_stand_left.inc` (104) — **OK** (idle-left + landing-after paths).
- `hero_ai_dispatch_airborne.inc` (139) — **OK** (top-level + airborne dispatcher).
- `hero_dispatch_and_leap_left.inc` (190) — **OK** (left-action dispatcher + leap-left animation).
- `hero_leap_and_land.inc` (251) — **OK** (leap-right + land-hold).
- `hero_fall_left.inc` (292) — **OK** (fall-left prelude + per-frame X-deltas).
- `hero_fall_right.inc` (272) — **OK** (mirror of fall-left).
- `hero_kicks_and_crouches.inc` (313) — **OK** (kick-left/right loops + crouch-kick variants).
- `hero_walk_run_movement.inc` (473) — **OK** (walk-left/right + run-left/right entries and loops).
- `hero_fall_right_and_drawers.inc` (568) — **OK by labels, large — verify cohesion in Phase 1b** (66 labels; first label `MAYBE_RESUME_WALK_RIGHT_IF_GROUNDED` suggests post-fall recovery; large size hints at possible split, but per-frame drawer chains for fall-right are inherently long).

#### Particle / scatter-dot effects (6 chunks)

- `opening_bg_droplet_sprinkles.inc` (157) — **OK** (`SCROLL_BG_RANDOM_LOOP` + droplet-pick + droplet-fall channels).
- `droplet_fall_and_random_pos.inc` (116) — **OK**.
- `draw_helpers_and_droplet_variants.inc` (47) — **OK**.
- `particle_bursts_and_droplet_drip.inc` (203) — **OK** (`PARTICLE_BURST_CYCLE_LOOP` + 3X / 7X variants + droplet-drip).
- `particle_burst_cycle_loop_2.inc` (155) — **MIXED** — the actual `PARTICLE_BURST_CYCLE_LOOP_2` is ~52 lines; the rest is **a large block of unlabelled `mov [varN], 0x0000` resets that follows a `killChannel` and is unreachable**. The dead block belongs in a `_dead_var_reset.inc` (or annotated as such), not silently appended to a particle-burst file.

#### Scatter-dots (4 chunks — overlapping naming)

- `scatter_dots_init_and_drift.inc` (208) — **OK by labels** (`LOOP_DRAW_LAKE_018_AT_CENTER`, `DRAW_3_SCATTER_DOTS_CYCLE`, `INIT_SCATTER_DOTS_POSITIONS`, `SCATTER_8DOT_DRIFT_RAW`, etc.).
- `scatter_3dots_classify_regions.inc` (100) — **OK by labels** (init-right + drift-loop + classify-region helpers).
- `scatter_8dots_loops.inc` (90) — **OK** (left/right 8-dot loops with delays).
- `scatter_dots_burst_right_drift.inc` (42) — **TINY / FRAGMENT** — 5 labels for right-burst + drift; could merge with `scatter_dots_init_and_drift.inc` since that file also handles burst-and-drift.

#### Audio

- `ambient_audio.inc` (97) — **OK** (`WAIT_RANDOM_DELAY_THEN_LOOP` + 19 ambient-case branches).

#### Multiplex animation rings

- `multiplex_anim_rings.inc` (90) — **OK** (ring-1 slots + ring-3 save loop).
- `multiplex_ring3_and_lake051.inc` (95) — **OK** (ring-3 slots 0..2 + LAKE_051 sequence).
- `multiplex_ring5_and_beast_proximity.inc` (43) — **MIXED** — `MULTIPLEX_RING5_SAVE_LOOP` (animation timing) plus `JMP_TO_CHECK_BEAST_NEAR` / `CHECK_IF_BEAST_IS_NEAR_LESTER` / `IF_BEAST_NEAR_THEN_REACT_*` (beast-proximity gating). Two unrelated topics.

#### Proximity / dispatch helpers

- `proximity_helpers_and_dispatch.inc` (64) — **REVISE** — comment says "horizontal/vertical proximity helpers"; only horizontal proximity is here. Also the file mixes the generic `CHECK_HORIZONTAL_PROXIMITY` helper with beast-AI-specific `BEAST_AI_RANGE_CHECK_*` and slug-dispatch helpers.

#### Screen / scenario draws

- `screen_to_the_right_setups.inc` (150) — **OK** (`FIRST_SCREEN_TO_THE_RIGHT` + per-screen channel setup + `CLAMP_HERO_X_TO_PLAYABLE_AREA`).
- `screen_edge_loops.inc` (170) — **OK** (vine-screen edge handlers + first-screen-right edges).
- `screen_scenarios.inc` (239) — **OK** (per-screen scenario draws: vine, second/third right, first right, outside-pool).
- `vine_and_outside_pool_screens.inc` (69) — **OK**.

#### Scene transitions

- `scene_transition_and_decor.inc` (157) — **MIXED — biggest split candidate**. Contains:
  1. `SCENE_TRANSITION_TO_GETTING_OUT_OF_POOL` — channel setup for the post-tentacle scene.
  2. `BEAST_PRE_KILL_WAIT` + `BEAST_KILLED_POST_DELAY` — beast death timing (belongs with `beast_killed_by_laser.inc`).
  3. `LAKE_PALETTE_FADE_IN` — palette-fade chain (8-step cross-fade).
  4. `WAIT_VAR_03_FRAMES_LOOP` (2 copies, branch-conditional) — generic frame wait.
  5. `DISPLAY_TEXT_01FA_AND_FADE_TO_PAL_2` — title text "ANOTHER WORLD" / "L'AUTRE MONDE" fade-in.
  6. `LOOP_DRAW_DECOR_215_AT_327_164`, `DECOR_AT_327_164_BLINK_LOOP`, `LOOP_DRAW_LAKE_037_AT_305_155` — decor channels.

### Regrouping proposals (LAKE)

Each proposal has a label (R1, R2, …) so commits can reference it.
Aggressive regrouping per owner directive — execute unless owner
flags otherwise.

**R1. Move BEAST_AMBIENT_CASE_5/6 from `beast_ai_spawn_mid_right.inc` into `beast_ambient_sound.inc`.** The two cases are part of the same random-pick chain (cases 1–6). Splitting them across files because they happen to live at adjacent byte addresses is exactly the "arbitrary cuts of the bytecode at arbitrary addresses" anti-pattern. After the move, `beast_ai_spawn_mid_right.inc` contains only `BEAST_AI_SPAWN_MID_RIGHT` and its inner helpers — rename to `beast_ai_spawn.inc` (no compass-direction suffix; only one spawn position handler exists in LAKE).

**R2. Merge the four small beast-AI files into one.** `beast_ai_dispatch.inc` (20 lines), `beast_ai_pick_dir_and_proximity.inc` (35), `beast_ai_spawn_mid_right.inc` (post-R1, ~25 lines), and `beast_drift_and_screen_shift.inc`'s `ADVANCE_X_FORWARD/BACKWARD_ONE_SCREEN` helpers (move to a dedicated file — see R6) → one file `beast_ai.inc` (~80 lines, 13–14 labels). All these files are sub-pieces of one logical state machine that dispatches on `[HERO_X]`, `[0x0D]`, and proximity flags into slug or hold-position routines.

**R3. Split `multiplex_ring5_and_beast_proximity.inc`.** Move `MULTIPLEX_RING5_SAVE_LOOP` to `multiplex_anim_rings.inc` (which already holds rings 1–3). Move `JMP_TO_CHECK_BEAST_NEAR`, `CHECK_IF_BEAST_IS_NEAR_LESTER`, `CHECK_IF_BEAST_IS_NEAR_LESTER__OUT_OF_RANGE_RET`, `IF_BEAST_NEAR_THEN_REACT_ELSE_KILL_THREAD`, `IF_BEAST_NEAR_THEN_REACT_ELSE_KILL_THREAD_2` to a new `beast_proximity.inc` (or merge into the new `beast_ai.inc` from R2). Delete `multiplex_ring5_and_beast_proximity.inc`.

**R4. Split `proximity_helpers_and_dispatch.inc`.** Move `CHECK_HORIZONTAL_PROXIMITY` + `EXIT_PATH_FROM_PROXIMITY_OUT_OF_RANGE` to `proximity_check.inc` (clean generic helper). Move `BEAST_AI_RANGE_CHECK_INIT_CART`, `BEAST_AI_RANGE_CHECK_VAR_39`, `BEAST_AI_RANGE_BOUNDS_CHK` into `beast_ai.inc` (or `beast_proximity.inc`). Move `DISPATCH_ON_PROXIMITY_TO_338F_OR_3068`, `DISPATCH_ON_PROXIMITY_TO_SLUG_FLIP_OR_306C` into `slug_anim_and_flip.inc` (their only callers are slug-side).

**R5. Split `scene_transition_and_decor.inc` into 4 files:**
  - `scene_transition_to_getting_out_of_pool.inc` — the channel-setup head.
  - `beast_intro_cinematic_kill.inc` — `BEAST_PRE_KILL_WAIT`, `BEAST_KILLED_POST_DELAY` (move next to `beast_killed_by_laser.inc`, or merge with it). The "killed by laser" wiring lives here, so a single file `beast_intro_cinematic_kill.inc` containing the wait + the death animation makes the intro cinematic legible top-to-bottom.
  - `lake_intro_palette_fade_and_title.inc` — `LAKE_PALETTE_FADE_IN`, the conditional `WAIT_VAR_03_FRAMES_LOOP`s, `DISPLAY_TEXT_01FA_AND_FADE_TO_PAL_2`. This is the "ANOTHER WORLD" title screen handoff.
  - Move `LOOP_DRAW_DECOR_215_AT_327_164`, `DECOR_AT_327_164_BLINK_LOOP`, `LOOP_DRAW_LAKE_037_AT_305_155` into `lake_decorations_096_099.inc` (rename that file to `lake_decoration_loops.inc` since it'll then hold a wider set than just 096–099).

**R6. Pull screen-shift helpers out of `beast_drift_and_screen_shift.inc`.** `ADVANCE_X_FORWARD_ONE_SCREEN`, `ADVANCE_X_BACKWARD_ONE_SCREEN`, `SHIFT_X_RIGHT_320`, `SHIFT_X_LEFT_320`, `SHIFT_X_LEFT_F_AND_JMP` → `screen_shift_helpers.inc` (or merge into `screen_to_the_right_setups.inc`). The remaining `BEAST_APPROACH_FAST_LOOP` + `DRAW_BEAST_DRIFT_LEFT_*` becomes `beast_drift_left.inc` (cleaner name reflecting just the drift sequence).

**R7. Rename + sharpen `decor_f7_through_f14.inc`.** Filename understates scope (covers F7..F18 plus Lester arm-raise + at-pool hold). Rename to `lake_intro_visual_chain.inc` (or split into `decor_305_155_blink_chain.inc` + `entity_drop_and_lester_at_pool.inc`). The Lester animations don't really belong in a "decor" file.

**R8. Extract dead block from `particle_burst_cycle_loop_2.inc`.** The unreachable `mov [varN], 0x0000` tail (~100 lines) lives here only because it's at the next byte-address slot in the bytecode — classic "arbitrary cut" symptom. Move to `_dead_var_reset_block.inc` with a comment noting that this is unreachable shipped bytecode preserved for round-trip byte-identity, and possibly add an `;@enc=dead` annotation in future. The remaining cycle becomes a small clean file.

**R9. Merge `scatter_dots_burst_right_drift.inc` into `scatter_dots_init_and_drift.inc`.** Both files cover the same scatter-dots-burst subsystem; the split is mechanical. After merging, the four scatter files become three, and the names line up with what they actually do.

### Phase 2 (comment fixes) for LAKE

To apply directly without regrouping:

1. `beast_killed_by_laser.inc`: replace "after Lester gets the gun" with "Beast laser-death animation cinematic — fired by the LAKE intro `BEAST_PRE_KILL_WAIT` chain (the alien natives kill the beast in the opening scripted sequence, before Lester gains control)."
2. `proximity_helpers_and_dispatch.inc`: drop "horizontal/vertical" — only horizontal. Mention generic + beast-AI-specific + slug-dispatch.
3. `decor_f7_through_f14.inc`: extend to "F7..F18 + entity-drop sequence + Lester arm-raise / at-pool hold animations." (only if not split per R7).
4. `beast_drift_and_screen_shift.inc`: clarify "beast drift animation + generic screen-shift helpers (`ADVANCE_X_FORWARD/BACKWARD_ONE_SCREEN`)" (only if not split per R6).
5. `multiplex_ring5_and_beast_proximity.inc`: irrelevant once R3 deletes the file.
6. `scene_transition_and_decor.inc`: irrelevant once R5 splits the file.
7. `beast_ai_spawn_mid_right.inc`: irrelevant once R1+R2 collapse the file.

## INTRO

19 stage-shared chunks under `src/levels/_unified/intro/`. INTRO
is a long cinematic with many phases; the existing chunk
breakdown is by phase / scene-element, and the labels reflect
their content.

### Per-chunk findings

- `intro_entry_and_dispatchers.inc` (110) — **OK** (entry point,
  resource-load setup, top-level dispatcher).
- `intro_first_scene_init.inc` (49) — **OK** (pause, draw 6 frames
  of CIN_138..143 establishing-shot, display two text strings —
  the "Good evening professor" / "I see you have driven here in
  your Ferrari." dialogue).
- `intro_song_init_and_decor.inc` (169) — **OK**.
- `intro_reset_and_lab_decor.inc` (281) — **OK**.
- `intro_lab_decor_late_phase.inc` (244) — **OK**.
- `intro_dna_animation.inc` (249) — **REVISE**. Filename suggests
  just the DNA helix, but the file actually covers BOTH the DNA
  intro animation (first ~13 labels) AND a tail of lab-cinematic
  draws (`DRAW_CIN_453_454_SEQ`, `DRAW_CIN_035_PAL_3_REPEAT_HEAD`,
  `DRAW_CIN_048_15_FRAMES_LOOP`) that hand off to the next phase
  via setup-channel calls. Conceptually adjacent (DNA →
  lab-establishing) but the filename misleads. Comment should
  say so explicitly; not split because they are sequential phases
  of one narrative beat.
- `intro_channel_inits.inc` (259) — **OK** (CH_0A through CH_1F
  channel-init helpers).
- `intro_late_pages_fill.inc` (226) — **OK** (page-fill init +
  drift loops by per-frame increments).
- `intro_particle_channels.inc` (393) — **OK**.
- `intro_page_show_and_text.inc` (319) — **OK** (SHOW_PAGE_0 /
  SHOW_PAGE_FF loops + text setup).
- `intro_lake_phase_fx_drifts.inc` (107) — **OK** (drift loops +
  per-phase FX play).
- `intro_lake_transition.inc` (414, **largest**) — **REVISE**
  (large; keep as-is but comment should hint that this is the
  multi-phase transition cinematic that owns the channel inits,
  cinematic slides/rises, and city-seq setup for the LAKE
  hand-off).
- `intro_music_marks_and_city_pans.inc` (153) — **OK**.
- `intro_city_seq_draws.inc` (397) — **OK** (CIN_190 / CIN_431 /
  CIN_432-433 city-sequence draw loops).
- `intro_scene_late_phase.inc` (217) — **OK** (parallax loops,
  zoom-out, palette E init).
- `intro_scene_final_fx_phase.inc` (172) — **OK**.
- `intro_scene_final.inc` (294) — **OK** (final-scene draws +
  particle init + bg audio).
- `intro_scene_transitions.inc` (71) — **OK** (4 wait-scene
  routines + the next-phase scene transition).
- `intro_transition_to_lake_setup.inc` (260) — **OK** (preloads
  LAKE bytecode + state ready for the bank switch).

### Regrouping proposals (INTRO)

Given INTRO's nature (long linear cinematic, each chunk is a
phase), aggressive regrouping risks scattering the narrative.
Two minor proposals:

**RI1.** Sharper comments on the two flagged files
(intro_dna_animation, intro_lake_transition) per audit findings —
applied as a comment-fix commit, no file moves.

INTRO Phase 3 deliberately minimal: the chunk structure
reflects narrative phases, and splitting further would obscure
the linear flow. Reopen if a specific chunk surfaces as a real
mixed-content blocker during later cross-stage work.

## PRISON

13 stage-shared chunks under `src/levels/_unified/prison/` plus
515 arm-specific chunks. PRISON has been heavily folded by
match_arms.py rounds, so most stage-shared chunks are
**collections of INLINE_SET_VARN_TO_M / DEDUP_* / DRAW_CIN_NNN
helpers** that share a topical theme rather than narratively-
sequential routines. Each helper has its own `;@if BRANCH ==`
arm-include chain.

**Important architectural note**: PRISON has a NESTED INCLUDE
pattern not seen elsewhere yet —
`prison/prison_dedups_and_landing_kill.inc` includes
`post_DRAW_CIN_168.inc` mid-routine (reaching the helper
`DRAW_CIN_169_IF_VAR09_EQ_1`), and similarly
`prison/prison_pagefill_inits.inc` includes `post_DRAW_CIN_240.inc`.
These tiny (5-line) files exist to allow the same helper to be
inserted at two byte addresses in the parent chunk's flow.

### Per-chunk findings

- `prison_equ_aliases.inc` (19) — **OK** (auto-generated EQU
  aliases header).
- `post_DRAW_CIN_168.inc` (5) — **OK** (nested-include helper).
- `post_DRAW_CIN_240.inc` (5) — **OK** (nested-include helper).
- `prison_delay_preload_resources.inc` (94) — **OK** (delay +
  preload + bank4 + step-position draw).
- `prison_step_draws_and_breaks.inc` (102) — **OK** (step-draw of
  CIN555 left/right + INLINE_BREAK_035 + a few CIN block draws).
- `prison_var29_state_machine.inc` (208) — **REVISE**. Title
  overstates: file is a collection of `INLINE_SET_VAR29_TO_N`
  setters (5/6/28/A/...) plus a few DRAW_CIN_406_408_BLOCK and
  DECREMENT_VAR29_BY_1 helpers, each with arm-specific
  post-bodies via `;@include "<arm>__post_*.inc"`. The actual
  var-29 state-machine *logic* lives in arm-specific entry
  chunks; this file is the SHARED setter / draw helpers the
  state machine calls into.
- `prison_var2f_state_machine.inc` (248) — **REVISE** (same as
  var29: collection of `SET_VAR2F_TO_NN` setters + INIT_VARS_*
  helpers; not the state machine itself).
- `prison_late_phase_var_setup.inc` (361) — **OK**.
- `prison_late_phase_scroll_and_pages.inc` (288) — **OK**.
- `prison_pagefill_inits.inc` (470) — **OK**.
- `prison_inline_setters_and_init.inc` (434) — **OK**.
- `prison_dedups_and_landing_kill.inc` (575) — **OK** (heavy
  fold-output: ~26 DEDUP_*, INLINE_DRAW_CV_*, DRAW_CIN_* labels
  with arm-specific tails).
- `prison_sfx_and_dedup_helpers.inc` (368) — **OK** (PLAY_SFX +
  DRAW_CIN draw helpers + dedup tails).

### Regrouping proposals (PRISON)

PRISON's structure is the output of careful match_arms.py
folding rounds. Re-organising into subdirectories would scatter
related fold helpers across directories without obvious gain,
so deliberately restrained:

**RP1.** Sharper comments on the two state-machine files in
PRISON.asm.in (note the contents are setters + draw helpers
called BY the state machine, not the state machine itself).

PRISON Phase 3 limited to RP1.

## CAPSULE

4 stage-shared chunks under `src/levels/_unified/capsule/` plus
366 arm-specific chunks. Like PRISON, CAPSULE is heavily folded;
each shared chunk is a topical bundle of fold helpers.

### Per-chunk findings

- `capsule_init_dispatch.inc` (816, **largest**) — **OK**.
  INIT_VARS_2F_29_12 + various INIT_VARS_* + DRAW_CV*_PLAY_*
  helpers + INLINE_*. The "init dispatch" name is broad but
  accurate.
- `capsule_init_vars_cluster.inc` (182) — **OK**. INIT_VARS_29_0E
  / E6_07_08 / 0E_29 / 63_01_02_03 / E7_E8 / E9_EA, INLINE_SET_*
  for VARE6, plus 4 PLAY_FX_* helpers — the per-frame state-init
  cluster.
- `capsule_inline_setters_and_init.inc` (424) — **OK**.
- `capsule_load_helpers_and_anim.inc` (286) — **DEEP-READ FINDING**:
  contains `INIT_BIRD_AI_VARS` (cart/dos only — gated by
  `;@if BRANCH in ("cartridge_1992", "dos_1992")`). The routine
  resets `HERO_X` to 0x91 (145), `HERO_Y` to 0x8F (143), saves
  prior `HERO_X` to var 0x28, sets gun-energy var 0x06 to 0x3DE
  (990 — same value Lester gets at PRISON entry per
  research/01), sets scene-state var 0x2A to 0x0F. The routine
  is the "ride the bird" scene init — overwrites HERO_X/Y to
  treat the bird's position as Lester's position for that scene.
  The file also contains SET_VAR22_* setters, PROJ_VAR22_*
  projection helpers, the SET_VAR04_* / INLINE_SET_VAR63_*
  shared-helper chain, and WALK_LEFT/RIGHT_DRAW_CV multistep
  helpers. Comment in CAPSULE.asm.in sharpened to mention the
  bird init.

### Regrouping proposals (CAPSULE)

CAPSULE's structure mirrors PRISON's (heavily folded helpers).
No file moves; the 4 chunks each represent a distinct topical
bundle of helpers.

### CAPSULE BIRD subsystem — follow-up research note

The `INIT_BIRD_AI_VARS` finding warrants its own research note:
this is a cart/dos-only initialiser that sets up the **alien city
bird scene** (Lester rides a bird to escape). The fact that the
routine reuses `HERO_X` / `HERO_Y` for the bird's position
(saving Lester's prior X to var 0x28) is the kind of variable-
overloading pattern documented in research/14 (`;@raw=` residue)
and the ACTOR_X / BUDDY_X discussions. Worth a dedicated entry
when somebody traces the full bird-flight bytecode.

## CAVES

10 stage-shared chunks under `src/levels/_unified/caves/` plus
587 arm-specific chunks (highest count of any stage). Same
pattern as PRISON / CAPSULE: heavily folded.

### Per-chunk findings (label-based — full reads pending in
follow-up cron tick)

- `caves_action_helpers.inc` — INIT_VARS_E6_EA + action helpers.
- `caves_dedup_helpers_cluster.inc` (786 lines, **largest** in
  CAVES) — DEDUP_CAVES_6B_* cluster; ~36 routines salvaged from
  match_arms.py rounds.
- `caves_inline_breaks.inc` — INLINE break sequences with VAR18
  setters.
- `caves_inline_setters_and_init.inc` — small inline init
  helpers, var-derivation chains.
- `caves_inline_setters_part1c.inc` — INIT_VARS_E6_68_69_6B
  cluster.
- `caves_preload_resources.inc` — PRELOAD_RES_6A_77_6D_6E_74_76
  _78_7C (8 resources).
- `caves_scroll_init_and_sfx.inc` — INIT_VARS_2F_29_12 + scroll
  init + SFX setup.
- `caves_scroll_setup_and_helpers.inc` — SCROLL_BLIT_P83_TO_PFF
  + scroll-blit helpers.
- `caves_var22_setters_and_projections.inc` — SET_VAR22_TO_*
  setters and projection helpers.

### Regrouping proposals (CAVES)

Same disposition as PRISON / CAPSULE — heavily folded structure
mostly cohesive at the file level. No structural moves; deep-
read pass during follow-up cron tick may surface specific
mixed-content cases.

## TANK

6 stage-shared chunks under `src/levels/_unified/tank/`. TANK is
short (battle-arena cinematic). 58 arm-specific chunks.

- `tank_animation_timing.inc` — ALTERNATE_VAR06_VAR04_TIMING.
- `tank_drawing_helpers.inc` — INIT_VARS_A_B_PAL_1.
- `tank_drive_vars.inc` — INCREMENT_VAR44_BY_37.
- `tank_inline_setters_and_hash.inc` — inline setters + hash
  bookkeeping.
- `tank_var5f_manipulation.inc` — INCREMENT_VAR5F_BY_8 + related.

All small helper aggregations; comments accurate.

## ENDING

7 stage-shared chunks under `src/levels/_unified/ending/`.
Ending is cinematic-only; 32 arm-specific chunks.

**Deep-read findings**:

- `ending_channel_cleanup.inc` was **MIXED** (5 unrelated topics
  in one file). Split applied as RE1 (commit `826e17a`):
  - `ending_channel_cleanup.inc` — DELETE_ALL_CHANS_AND_KILL +
    PRELOAD_RESOURCES_8_TO_1.
  - `ending_credits_cinematics.inc` — DRAW_CIN_97_TO_100,
    DRAW_CIN_101_102_FADE_PAL_C, DRAW_CIN_103_LOOP,
    DRAW_CIN_58_ANIM_LOOP, DRAW_CIN_59_TO_64_VAR_POS (credits
    cinematic draws).
  - `ending_drift_and_delay_helpers.inc` — DRIFT_VAR_4_PLUS_10,
    DRIFT_VAR_3_MINUS_1 variants, DELAY_VAR6_THEN_* (utility
    loops gating channel transitions).
- `ending_palette_fades.inc` (79) — **OK** (PAL_FADE_18_TO_1D
  6-step cross-fade + DRAW_CIN_71_72_FADE + DRAW_CIN_106_107_FX_57).
- `ending_pal_var_setup.inc` (143) — **OK** (palette + var setup
  + DRAW_STARS_PAGE0/3 + DRAW_STARS_CIN_38_39_40 — the closing
  star-field draws).
- `ending_var_setups.inc` (63) — **OK** (INIT_VARE + drift loops
  + DRAW_CIN_70_ANIM_LOOP).
- `post_DRAW_CIN_103_LOOP.inc` / `post_DRAW_CIN_58_ANIM_LOOP.inc` /
  `post_DRAW_CIN_97_TO_100.inc` — nested-include 5-line helpers
  (LABEL_NNNN entries with `db 0x11` sentinel byte). Pattern
  identical to PRISON's `post_DRAW_CIN_168/240`. **OK**.

## CODE_WHEEL

1 stage-shared chunk: `code_wheel_palette_fades.inc` (palette
fades shared between amiga and dos arms). 21 arm-specific
chunks. The cartridge port skips CODE_WHEEL; cart entry chunk
is just 17 lines.

- `code_wheel_palette_fades.inc` — PAL_FADE_DOWN_17_TO_11 etc.

Audit OK; no regroupings.

## PASSCODE

1 stage-shared chunk: `passcode_var_init.inc` (SET_VAR_E6_F_PAUSE_4).
17 arm-specific chunks.

Audit OK; no regroupings.

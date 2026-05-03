# Autonomous Work Brief — chapter-split methodology

This file is the entry-point for any cron-resumed session. Read this
plus `CLAUDE.md` plus the memory dir at
`.claude/projects/-home-fsanches-compartilhado-another-world-archaeology/memory/`
before doing anything.

## Goal

Apply the LAKE chapter-split methodology to every other stage of
the game. Methodology: rename → fold → chapter-split.

## State as of 2026-05-04 (FOLD MILESTONE for all 7 stages)

**705 cross-arm fold operations landed across all 7 new stages.**

Per-stage fold tally:

| Stage      | Folds | Arm-instances | Comment |
|------------|------:|--------------:|---------|
| CAPSULE    |   179 |           438 | 3-arm hash/init helpers + many SET_VAR + body-hash routines |
| CAVES      |   218 |           579 | Most complex stage |
| CODE_WHEEL |    14 |            28 | 2-arm only (amiga + dos; no cart for this stage) |
| ENDING     |    28 |            63 | Hero-fade and channel teardown helpers |
| PASSCODE   |     5 |            12 | Modest — passcode validation diverges per port |
| PRISON     |   238 |           552 | Most folds (round 2 added +33) |
| TANK       |    23 |            59 | Tank-drive init + WAIT helpers |
| **TOTAL**  | **705** |       **1731** |         |

This is a 7× increase from the 100-fold milestone of 2026-05-03.

The leap was driven by the auto_fold_rename + auto_fold tools that
automatically rename LABEL_<HEX> tuples to body-shape-derived names
(or FOLD_BODY_<sha>-style hash names as fallback) before folding.

This is built on top of:
- Massive rename rounds: ~3000+ named routines across all stages
- Cross-arm matcher fix (issue #0078): no longer over-abstracts
  CINEMATIC operands
- Batch rename patterns: DELAY_LOOP_VAR<X> (334 instances), single-frame
  draws (778), hang-draws (135), trampolines (107), various single-instr
  patterns (~200)

## Verify state

After every fold: `verify_stage 29/29 + verify_unified 27/27` maintained.

## Tasks #95-101: still in_progress

These remain in_progress because there are MORE fold candidates beyond
the named routines folded so far — specifically, LABEL_<HEX> routines
whose bodies are byte-equivalent across arms but whose addresses (and
thus default labels) differ per arm. Folding those requires renaming
each pair/triple to a shared name first.

## State as of 2026-05-04 (LAKE methodology applied — rename rounds, all stages)

User directive (received 2026-05-04): apply the LAKE methodology
fully — semantic-rename LABEL_<HEX> labels first across all stages,
THEN chapter-split (later), THEN folds (later still).

**Rename progress per stage / arm (after multiple rounds):**

Each stage typically has ~50-300 named routines per arm, ~100-2700
LABEL_<HEX> routines remaining (mostly inner case-targets of dispatch
chains, low-ref jump targets).

PASSCODE is most-complete: cart 5 LABEL, dos 5 LABEL, amiga 5 LABEL.

## Tools built

- `tools/match_arms.py` — symbolic cart→arm label matcher.
  Fixed in #0078 to only abstract LABEL_<HEX> identifiers.
- `tools/find_singletons.py` — finds most-referenced single-instruction
  labels per arm.
- `tools/find_foldable_routines.py` — surfaces cross-arm routine
  bodies that are byte- AND symbolic-identical (the safe fold criterion).
- `tools/multi_fold.py` — batch fold helper. Fixed (this session) to
  handle stages with fewer than 3 arms (CODE_WHEEL has only dos+amiga).
- `tools/reconstruct_arms.py` — inverse of multi_fold; rebuilds flat
  per-arm files from chunks + unified file. Used to revert/refold.
- `tools/split_asm_chapter.py` — generic chapter splitter (used for
  INTRO and LAKE).

## Cross-stage shared helpers (recurring across multiple stages)

- `SHARED_RET` (most-referenced ret-only label per stage)
- `KILL_CHANNEL_LANDING`, `TRIVIAL_RET`, `TRIVIAL_RET_2`
- `COPY_HASH_VAR_37_TO_RANGE`, `DERIVE_VAR12_11_10_FROM_VAR9`,
  `INIT_RANGE_48_TO_4D_TO_MAX`, `ACCUMULATE_HASH_INTO_VAR37_38`,
  `DERIVE_HASH_BUCKETS_FROM_VAR38`
- `STATE_VAR12_BIG_DISPATCH`, `DISPATCH_VAR2F_STATE`
- `COMPUTE_OFFSET_VAR21_22`, `COMPUTE_OFFSET_PLUS21_MINUS22`
- `DECREMENT_VAR22`, `INCREMENT_VAR31`, `ZERO_VAR0F_AND_KILL`
- `MAIN_GAME_LOOP_HERO_128`, `GAME_LOOP_HERO_DISPATCH_FIRST`,
  `GAME_LOOP_HERO_DISPATCH_LAST`, `GAME_LOOP_CV_304_305`
- `GUARDED_HERO_ANIM_CV_128`, `GUARDED_DRAW_CV_159`,
  `GUARDED_DRAW_CV_126`, `DRAW_CV_304_THEN_305`
- `HERO_WALK_LEFT_LOOP`, `HERO_WALK_RIGHT_LOOP`
- `ADVANCE_VAR0D_RESTORE_STATE`

## Issues filed

- #0078 (closed): match_arms.py over-abstracted CINEMATIC operands
- #0079 (open): PRISON cart has fewer dispatch cases than dos/amiga —
  evidence cart was either built from earlier source or had its
  polygon bank stripped.
- #0080 (open): CAPSULE alien sprite uses different CIN ranges per
  arm (cart=112, dos=111, amiga=183) — CIN index space was renumbered
  across the 1991→1992 ports.

## Next steps

1. **More fold rounds:** the 100 folds so far are just the tip — all
   stages have many more LABEL_<HEX> routines that are byte-identical
   across arms but need same-name renames before they can be folded.
   Run `find_foldable_routines.py STAGE` to see remaining candidates.

2. **Chapter-split** (per LAKE methodology): once a unified file has
   real content from folds, the next step is to split it into
   per-feature chapters using `tools/split_asm_chapter.py`.

3. **More cross-arm matching:** the matcher finds peer routines
   automatically when the FROM arm has a name. Run more rename rounds
   then re-run match_arms.py to surface new matches.

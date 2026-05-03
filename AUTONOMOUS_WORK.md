# Autonomous Work Brief — chapter-split methodology

This file is the entry-point for any cron-resumed session. Read this
plus `CLAUDE.md` plus the memory dir at
`.claude/projects/-home-fsanches-compartilhado-another-world-archaeology/memory/`
before doing anything.

## Goal

Apply the LAKE chapter-split methodology to every other stage of
the game. Methodology: rename → fold → chapter-split.

## State as of 2026-05-04 (post-fold polish)

After fold completion, polished the codebase:

- **156 FOLD_BODY/DEDUP routines renamed** to semantic names by
  body-pattern recognition (DELAY_<N>_QUANTUMS, INLINE_SET_VAR<X>_TO_Y,
  DRIFT_DOWN_VAR<X>_<N>X, INIT_VARS_<...>, etc.)
- **65 cross-stage names unified** — when the same byte-identical body
  appeared in 2+ stages with different names, picked the highest-
  quality name and propagated it.
- **263 chunk filenames aligned** with their preceding routine's
  current label (so /post_FOLD_BODY_xxx.inc files reflect what they
  follow).

Final naming quality across all 7 stages:

| Stage      | Folds | Semantic | % |
|------------|------:|---------:|--:|
| CAPSULE    |   179 |      117 | 65% |
| CAVES      |   264 |      166 | 62% |
| CODE_WHEEL |    14 |       14 | 100% |
| ENDING     |    28 |       28 | 100% |
| PASSCODE   |     6 |        6 | 100% |
| PRISON     |   299 |      216 | 72% |
| TANK       |    24 |       24 | 100% |
| **TOTAL**  | **814** | **571** | **70%** |

243 routines remain with FOLD_BODY_<sha> or DEDUP_<seq> generic names —
these are the long-tail of unique-shape bodies that don't fit auto-
namable patterns. They could be renamed manually with semantic insight.

New tools landed:
-  — body-shape renamer for FOLD_BODY
-  — body-shape renamer for DEDUP
- Cross-stage helper candidates: 142

  117b  CAPSULE,CAVES,PRISON: COPY_HASH_VAR_37_TO_RANGE
   69b  CAPSULE,CAVES,PRISON: DERIVE_VAR12_11_10_FROM_VAR9
   61b  CAPSULE,CAVES,PRISON: INIT_RANGE_48_TO_4D_TO_MAX
   27b  CAPSULE,CAVES,PRISON: FOLD_BODY_358B_6F629262
   27b  CAPSULE,PRISON: FOLD_BODY_358B_DF9AE0DF
   23b  CAPSULE,CAVES,PRISON: SPLIT_VAR09_BITS_INTO_VAR0D
   21b  CAPSULE,CAVES: INIT_VARS_AA_AD_5B_5E_PLUS1
   16b  CAPSULE,CAVES,PRISON: CLEAR_PAGES_1_2_AND_BLIT_CHAIN_X8
   16b  CAPSULE,CAVES: FOLD_BODY_189B_29E88AAE
   15b  CODE_WHEEL,ENDING,TANK: CLEAR_PAGES_1_2_AND_BLIT
   14b  CAPSULE,CAVES: FOLD_BODY_206B_44F9C1BD
   14b  CAPSULE,CAVES: FOLD_BODY_206B_F444FCB9
   13b  CAPSULE,CAVES,PRISON: ACCUMULATE_HASH_INTO_VAR37_38
   13b  CAPSULE,CAVES: INIT_VARS_2F_29_12
   13b  CAPSULE,CAVES: INIT_VARS_2F_29_12
   13b  CAPSULE,CAVES,PRISON: FOLD_BODY_189B_794E4590
   13b  CAPSULE,CAVES: INIT_VARS_A1_A4_A7
   12b  CAPSULE,CAVES: FOLD_BODY_200B_1AFE2B0B
   12b  CAPSULE,CAVES: FOLD_BODY_200B_5D805D1F
   12b  CAPSULE,CAVES: FOLD_BODY_200B_37F93421 — surfaces cross-stage helper bodies
- Unifying 0 cross-stage names — unifies names across stages
-  — aligns chunk filenames with current
  labels (BUG: don't run after cross-stage unification — can produce
  duplicate filenames that break verify)

## State as of 2026-05-04 (FOLD MILESTONE — tasks #95-101 completed)

**814 cross-arm fold operations landed across all 7 new stages.**
Tasks #95-101 marked completed; 39 residual candidates tracked in
issue #0081.

Per-stage final fold tally:

| Stage      | Folds | Coverage | Comment |
|------------|------:|---------:|---------|
| CAPSULE    |   179 |     ~88% | v4 used; v5+dedup regressed for this stage |
| CAVES      |   264 |     ~97% | 8 residual (4 single-routine in nested chunks, 4 ambiguous) |
| CODE_WHEEL |    14 |     100% | All 2-arm candidates folded |
| ENDING     |    28 |     100% | All 3-arm candidates folded |
| PASSCODE   |     6 |      75% | 2 residual (1-byte name conflicts) |
| PRISON     |   299 |     ~99% | 2 residual (count-mismatch tuples) |
| TANK       |    24 |     ~96% | 1 residual (count-mismatch tuple) |
| **TOTAL**  | **814** | **~95%** |         |

Residual ~39 candidates documented in issue #0081 (4 categories:
order-skipped within nested chunks, count-mismatch tuples, orphan
ret/killChannel terminators, 1-byte name conflicts).

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

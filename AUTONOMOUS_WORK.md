# Autonomous Work Brief — chapter-split methodology

This file is the entry-point for any cron-resumed session. Read this
plus `CLAUDE.md` plus the memory dir at
`.claude/projects/-home-fsanches-compartilhado-another-world-archaeology/memory/`
before doing anything.

## Goal

Apply the LAKE chapter-split methodology to every other stage of
the game. Methodology: rename → fold → chapter-split.

## State as of 2026-05-04 (cleanup pass: @raw + FILL + empty chunks)

After all the rename/fold/sync work, the source tree had accumulated
significant clutter that didn't carry information. Three cleanup passes
landed:

### 1. Strip redundant ;@raw= comments

awvm-asm uses ;@raw= as authoritative when present, but for most
opcodes recomputes identical bytes from the symbolic form. Three
opcode families need ;@raw= (bankSwitch, video, setPalette);
chunks additionally need it for cross-chunk branch targets
(call/je/jne/jl/jg/jle/jge/jmp/djnz/setup/song/load).

Stripped:
  per-branch sources:        136884 lines
  unified .asm.in files:       2110
  unified per-arm chunks:     65774
  TOTAL:                     204768 redundant @raw comments removed

Tools: strip_redundant_raw.py, strip_redundant_raw_unified.py,
strip_redundant_raw_chunks.py.

### 2. Compress repeated db <byte> runs into FILL macros

End-of-bytecode-bank padding produced thousands of repeated
'db 0xFF, 0xFF, ...' lines. Replaced with FILL(n, 0xFF) macros
(already supported by tools/awvm_preprocess.py).

Per branch:
  cartridge_1992:    27303 lines removed
  dos_1992:          42686
  gba_2004:           6952
  chahi_amiga_1991:  44865

Per stage chunks:  108690 lines removed
TOTAL: 230496 lines of FILL padding compressed.

Tool: compress_fill_padding.py.

### 3. Remove empty per-arm chunk files

When two folded routines are adjacent with nothing between them in
an arm, multi_fold creates an empty chunk file. 309 such empty chunks
removed (CAPSULE 78, CODE_WHEEL 10, PASSCODE 0, PRISON 191, TANK 2).

CAVES (109 empties) and ENDING (28 empties) skipped — the cleanup
heuristic broke verify_unified for those stages; needs a deeper fix.

Tool: remove_empty_chunks.py.

### Net effect

Combined across all three passes: ~435K source lines removed without
losing any information (verify_stage 29/29 + verify_unified 27/27
maintained throughout). Files now read MUCH closer to '70s-style
compact assembly rather than disassembler-output-with-everything.

## State as of 2026-05-04 evening (per-branch source sync)

After the fold polish round, propagated semantic names from unified
files into per-branch sources:

**INTRO sync** (issue #0077):
- 13 cart, 59 dos, 60 gba, 34 amiga renames in round 1
- 3+5+5+2 in round 2
- Total: 181 renames across 4 per-branch INTRO sources

**LAKE sync** (issue #0075 — closed):
- Per-branch LAKE was already substantially renamed (cart 0, amiga 0,
  dos 10, gba 2 LABEL_<HEX> remaining). Closed the issue.

**Stage sync** (new — applies to CAPSULE/CAVES/CODE_WHEEL/ENDING/
PASSCODE/PRISON/TANK):
- Round 1: 754 renames across 21 per-branch sources
- Round 2: 78 more renames
- Total: 832 per-branch renames

These renames sync the unified  chunk
labels (which were renamed during the fold work) into the per-branch
 source-of-truth files (which
verify_stage uses).

**Tools added:**
-  — unified intro → cart per-branch
-  — cart per-branch → dos/gba/amiga
-  — same approach for LAKE
-  — for the 7 new stages

All sync tools use abstracted-body matching (LABEL_<HEX>/JUNK__<HEX>
tokens replaced with placeholder).

verify 29/29 + 27/27 maintained throughout.

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

## State as of 2026-05-03 (semantics + readability + organization pass)

8-phase plan executed autonomously (verify_stage 29/29 +
verify_unified 27/27 maintained throughout):

- **Phase 1a** — strip unused EQUs per file: 5532 lines removed
  (2980 per-branch + 2552 unified-chunk).
- **Phase 1b** — consolidate 15 var-alias EQUs into shared
  `src/levels/_common_vars.inc`. `verify_stage.py` extended to
  expand `;@include` directives so per-branch sources can use it.
- **Phase 2** — stage-narrative doc headers added to all 9 unified
  `.asm.in` files and all 28 per-branch sources (drawn from
  `references/walkthroughs/2026-04-29-gamefaqs-aw-78570.txt` and
  archaeology context). Tool: `tools/add_stage_doc_headers.py`.
- **Phase 4 / rounds 5-8** — 98 FOLD_BODY routines renamed from
  body shape (down from 134 distinct → 29 remaining). Tools:
  `tools/fold_body_rename_round_5.py` through `_round_8.py`.
- **EQU localization** (per user request) — 1371 single-use EQUs
  moved out of INTRO/LAKE `.asm.in` into the chunk that
  references them. Per-branch values preserved via
  `;@if BRANCH ==` blocks at chunk top. Tool:
  `tools/localize_single_use_equs.py`.
- **Phase 7** — `docs/SOURCE_TREE.md` (in source-reconstruction
  repo) documenting the three-layer src/levels/ organization,
  multi-fold technique, verification regime, and per-tool reference.

Still pending: Phase 6 (cross-stage helper extraction).

## State as of 2026-05-03 evening (continued)

- **EQU localization** (per user request, post-restart):
  CINEMATIC_SLUG_FLIP_WALKING_0 and 1370 other single-use EQUs
  moved out of INTRO/LAKE `.asm.in` into the chunks that reference
  them. Per-branch values preserved via `;@if BRANCH ==` blocks at
  chunk top. Tool: `tools/localize_single_use_equs.py`.
- **FOLD_BODY rounds 5–8**: 98 routines renamed (134 → 29
  remaining distinct). Tools: `fold_body_rename_round_{5,6,7,8}.py`.
- **Phase 3** (dispatcher case-target naming): 33 + 142 LABEL_<HEX>
  case-targets renamed across per-branch sources and unified per-arm
  scopes. Tool: `tools/rename_dispatcher_cases.py`. Per-FILE scope
  enforced — `LABEL_<HEX>` names are address-derived and the same
  hex can refer to unrelated routines across files.
- **Phase 5** (empty-chunk removal redo): 137 empty chunks removed
  from CAVES + ENDING (109 + 28). Previous attempt broke verify
  because it tried to also collapse the surrounding `;@if`
  structure; new tool just drops the include line and leaves the
  conditional structure intact. Tool:
  `tools/remove_empty_chunks_safe.py`.
- **Phase 7** (architecture README): `docs/SOURCE_TREE.md` in
  source-reconstruction repo.

**Phase 6** (cross-stage helper extraction) — DONE.
136 routines hoisted to `src/levels/_unified/_helpers/<NAME>.inc`
with each stage's local definition replaced by
`;@include "_helpers/<NAME>.inc"`. Constraint: jump/call-free
bodies only (the assembler emits stage-specific operand bytes for
flow-control instructions, so identical source would compile to
different bytecode per stage). Tool:
`tools/extract_cross_stage_helpers.py` + scanner
`tools/scan_cross_stage_helpers.py`. 364 replacements across the
9 unified `.asm.in` files. verify_stage 29/29 + verify_unified
27/27 stay green.

ALL 8 PHASES COMPLETE.

## State as of 2026-05-04 (post-plan continuation)

After the 8-phase plan landed, autonomous cron ticks pursued
follow-up work focused on per-branch sync and archaeology:

- **FOLD_BODY rename round 9** — 24 more routines named
  (24 → 5 distinct remaining; the 5 are edge cases with ambiguous
  bodies). Tool: `fold_body_rename_round_9.py`.
- **EQU localization extension** — `localize_single_use_equs.py`
  extended to handle the multi-chunk-but-not-asm.in case (62 more
  EQUs moved out of INTRO/LAKE `.asm.in`). `_UNUSED_` named EQUs
  pinned at top-level as research flags.
- **`docs/SOURCE_TREE.md` updates** — documented `_helpers/`,
  multi-chunk localization, and `_UNUSED_` convention.
- **Per-branch sync expansion** — new
  `tools/sync_all_chunks_to_per_branch.py` reads ALL chunks (not
  just arm-prefixed), with optional `--aggressive` operand
  abstraction. Across multiple iterations: ~1,476 LABEL_<HEX>
  routines renamed in per-branch sources (24272 → 22796). The
  iteration converges to a fixed point when no body abstraction
  finds new matches.
- **Archaeology investigations**:
  - **Issue #0079** (PRISON cart fewer dispatch cases) — falsified
    the "missing polygons" hypothesis. Cart DOES reference CIN_169
    and CIN_241; the real divergence is a per-frame position
    adjustment (cart adjusts (var07, var08) by (-2, +13) before
    drawing CIN_169, dos draws directly). Implies a polygon-anchor
    or coordinate-frame difference between the two 1992 ports.
  - **Issue #0080** (CAPSULE alien CIN renumbering) — confirmed
    the renumbering between amiga 1991 and dos 1992 is a **bank
    repack + index renumbering**, not a sprite rewrite. All 5
    mapped CIN pairs have identical first-4-byte headers (poly
    type + bbox) and the vector-data tail is byte-identical; only
    the sub-polygon offsets within the bank differ.
  - **Issue #0077** (INTRO sync per-branch) closed — all
    acceptance criteria met.

## State as of 2026-05-04 (archaeology investigations cont'd)

- **Issue #0007** (Mac Estr resource type) closed — `Estr` is
  classic Mac OS error-string table, not AW data. Decoded ~15
  Pascal strings + confirmed byte-stable across v1.0.2 + v1.0.3.
- **Issue #0076** action 2 done — LAKE dead-code preload of music
  0x89 is byte-identical in all 4 ports (1991 amiga + 1992 dos +
  1992 cart + 2004 gba). Music 0x89 is genuine 1991-era cut content
  preserved across every subsequent port.
- **Issue #0044** partial — semantic-rename rounds confirm the
  beetle wing-flip range CIN_661..669 in Amiga LAKE = LIFT_FRAME_*
  + FLYING_FRAME_* (lift off + fly), qualitatively matching the
  original wings-opening hypothesis. PNG rendering still gated on
  rsvg-convert/inkscape (not installed locally).
- **Issue #0055** progress — `tools/unused_sound_scan.py` shipped.
  DOS has 4 SOUND resources never play'd OR loaded (0x2E, 0x37,
  0x38, 0x42), candidate cut-content sounds.
- **Issue #0057** progress — `tools/unused_palette_scan.py`
  shipped. DOS has 113 unused palette slot-indices summed across
  all levels; PASSCODE uses only 2 of 32, ENDING skips the entire
  low half (0-9).
- **Issue #0054** progress — `find_unused_polygons.py` re-run for
  DOS + Amiga. Cross-port comparison shows amiga CAPSULE has 1117
  unused polygons vs DOS's 472 (645 more) — consistent with the
  CAPSULE alien-CIN renumbering finding (#0080), suggesting amiga
  retained pre-renumbering polygon vestiges that DOS trimmed.

## State as of 2026-05-04 (cross-port sprite-byte archaeology)

New `tools/cross_port_polygon_diff.py` (raw byte set difference)
and `tools/cross_port_used_polygon_diff.py` (intersected with
"used by that port's bytecode") surface the cleanest cut-content
finding in the entire archaeology project so far:

  | Stage      | amiga-USES-but-dos-LACKS | dos-USES-but-amiga-LACKS |
  |------------|--------------------------|--------------------------|
  | LAKE       | **201 sprites**          | 0                        |
  | CAPSULE    | 107                      | 360                      |
  | TANK       | 0                        | 90                       |
  | CODE_WHEEL | 0                        | 8                        |
  | CAVES      | 0                        | 16                       |
  | INTRO/PRISON/ENDING/PASSCODE | ≤2     | ≤2                       |

LAKE's 201 amiga-only-USED sprites is the cleanest "1991-era cut
content" set in the project: amiga bytecode actively renders 201
unique solid polygons that DOS removed entirely from the bank.

Persisted offsets:
  - `docs/cut_content/cut_polygons_amiga_only.json`
  - `docs/cut_content/dos_added_polygons.json`

Three rebuild patterns documented in research/06:
  - **DOS-additive** (CODE_WHEEL +8, TANK +93, CAVES +16): the
    1992 port added new sprite content.
  - **Amiga-vestigial** (LAKE 201 cut): DOS rebuild excised
    sprites the 1991 amiga release shipped + actively rendered.
  - **Major rework** (CAPSULE 107+360): both ports have unique
    USED content — full re-spritefication, not just renumbering.

Issues updated this round: #0054, #0080, research/06.

## State as of 2026-05-04 (parent-group attribution)

The 207 LAKE cut sub-polys were attributed to **86 named amiga
hero/Lester animation parent groups** via a new
`tools/find_parent_polygons.py` (inverts polygon-walker's child
→ parent traversal). Composite breakdown:

  HERO_RESUME_LEFT: 10 frames cut    HERO_LEAP_LEFT/RIGHT: 10 each
  HERO_RESUME_RIGHT: 7 frames        POOL_LESTER: 7 frames
  HERO_RUN_LEFT/RIGHT: 6 each        HERO_FALL_LEFT: 4 frames
  HERO_WALK_LEFT/RIGHT: 4 each       HERO_STOP_LEFT/RIGHT: 3 each
  HERO_OUT_POOL, LESTER_WAIT, etc.: 1-3 each

HERO_RESUME_LEFT is the cleanest pure-cut case: amiga has 10
group polygons at the named offsets (0x0310..0x0574 + 0x0ADC..0x0B54),
DOS's polygon bank has PARSE-FAIL or unrelated content at all 10,
and DOS LAKE.asm has no matching CINEMATIC_HERO_RESUME_LEFT_F* EQU
declarations. The 10-frame stop→walk-left smoothing animation was
removed from the 1992 rebuild.

HERO_LEAP_RIGHT was rebuilt rather than cut — DOS has its own
HERO_LEAP_RIGHT_LOOP routine but uses DRAW_HERO_STOP_R_BUNDLE_NN_MM
helpers (composite/bundled sprites) instead of the 10 individual
amiga frames.

New tool: `tools/attribute_cut_polygons.py` walks the same
attribution across all stages and writes
`docs/cut_content/cut_attribution.json`. CAPSULE/TANK/CAVES
attribution is shallower because their CINEMATIC_<NNN> EQUs aren't
semantically renamed yet — the breakdown surfaces "CINEMATIC_NNN"
labels rather than "HERO_*" labels.

## State as of 2026-05-04 (sprite-pipeline rebuild verdict)

Refined the cross-port sprite-byte finding by walking the actual
DOS bytecode at hero-animation states. DOS DOES preserve hero
animations like HERO_RESUME_LEFT and HERO_LEAP_LEFT — but uses
COMPOSITE helpers (`DRAW_VIDEO_NNN_AND_CIN_002`,
`DRAW_HERO_SHADOW_BUNDLE_NN_MM`) that draw shared `COMMON_VIDEO`
sprites instead of amiga's per-stage `CINEMATIC_HERO_*` detail
frames. Verified the same composite-helper architecture in
`cartridge_1992/LAKE.asm` and `gba_2004/LAKE.asm` — the pipeline
shift propagated to ALL post-1991 ports.

**Final archaeology verdict**: the 1991→1992 port wasn't a content
cut, it was a **sprite pipeline rebuild**. The 1991 amiga release
gave each stage its own dedicated detail sprites for hero
animations; the 1992 DOS rebuild unified these by using the
shared `COMMON_VIDEO` bank + per-stage cinematic overlays
composited via helper routines. amiga's per-stage richness was
traded for DOS's bank-friendly shared-sprite approach. Every
port from 1992 onward inherits this architecture; only the
original 1991 amiga release uses the per-stage detail-sprite
pipeline.

This is the inflection point of the entire AW port lineage —
explains why no two post-1991 ports byte-match amiga (the
pipeline differs at the polygon-bank level even when the
bytecode-level animation logic is preserved).

## State as of 2026-05-04 (chapter-split sweep)

Applied `tools/split_asm_chapter.py` (with two bug fixes — `<stage>/`
and `_helpers/` include-path rewriting) across 5 stages. Every
`.asm.in` is now ≤433 lines (down from up to 3808).

| Stage      | Before | After | Reduction | Chapters |
|------------|--------|-------|-----------|----------|
| INTRO      | 591    | 43    | -93%      | (already split — 14 chapters) |
| LAKE       | 1836   | 339   | -82%      | (already split — 65 chapters) |
| CODE_WHEEL | 272    | 272   | (no depth-0 labels — all `;@if`-wrapped) |
| PASSCODE   | 115    | 69    | -40%      | 1 |
| TANK       | 504    | 124   | -76%      | 5 |
| ENDING     | 561    | 66    | -88%      | 4 |
| CAPSULE    | 2296   | 398   | -83%      | 3 |
| CAVES      | 3644   | 362   | -90%      | 3 |
| PRISON     | 3808   | 433   | -89%      | 2 |

Total `.asm.in` size: 2106 lines (down from ~14000+).

Every stage except CODE_WHEEL has chapter-style chunks alongside
its per-arm fold chunks. CODE_WHEEL is the only stage where
chapter-splitting via the depth-0-label mechanism doesn't apply
(every routine is wrapped in a `;@if BRANCH ==` block, so there
are no depth-0 cut points). It's small enough (272 lines) that
this is OK.

All chapter-splits verified at each step; verify_stage 29/29 +
verify_unified 27/27 maintained throughout the sweep.

# Autonomous Work Brief — chapter-split methodology

This file is the entry-point for any cron-resumed session. Read this
plus `CLAUDE.md` plus the memory dir at
`.claude/projects/-home-fsanches-compartilhado-another-world-archaeology/memory/`
before doing anything.

## Goal

Apply the LAKE chapter-split methodology to every other stage of
the game, then split each unified file into per-feature `.inc`
chapter files for readability. The user is away; do not stop to
ask questions; commit at every passing-verify step.

## State as of 2026-05-03 ~14:30 (end of cron tick #3)

**INTRO chapter-split DONE** (#87): 15 chapters under src/levels/_unified/intro/.
Main INTRO.asm.in went from 4384 → 605 lines. Drive-by fix in same tick:
verify_unified.py now walks ;@include transitively (commit f52c717).

**INTRO semantic-rename DONE** (#102): all referenced LABEL_<HEX>
labels in INTRO have been given semantic names. 113+ labels named
across rounds 13-36 this session. The 56 remaining LABEL_<HEX>
entries are all **orphan killChannel terminators** — unreferenced
filler bytes between routines, intentionally left as LABEL_<HEX>.

Issue #0077 filed: per-branch INTRO sync (cart→dos/gba/amiga).
That's the natural follow-up but is NOT in the task list yet.

## State as of 2026-05-03 ~16:30 (end of cron tick #4)

**Cross-arm fold candidates: surfaced and renamed across all 7
new-stages.** Built tools/find_foldable_routines.py to identify
routines whose **symbolic source bodies** match across per-arm
.inc files (the safe fold criterion — same source assembles to
matching bytes regardless of EQU table differences). Used it to
rename 91 cross-arm pairs/triples across all 7 stages:

| Stage      | Renamed cross-arm pairs | Foldable bytes |
|------------|------------------------:|---------------:|
| CODE_WHEEL |                      16 |          327 |
| ENDING     |                      19 |        1,485 |
| PASSCODE   |                       9 |          188 |
| TANK       |                      15 |        1,062 |
| PRISON     |                      14 |        5,893 |
| CAVES      |                      11 |        6,089 |
| CAPSULE    |                       7 |        2,987 |
| **Total**  |                     **91** |   **18,031** |

Cross-stage shared helpers identified:
- `CLEAR_PAGES_1_2_AND_BLIT` — appears in CODE_WHEEL, ENDING, TANK, PASSCODE
- `COPY_HASH_VAR_37_TO_RANGE` — appears in PRISON, CAVES, CAPSULE
- `DERIVE_VAR12_11_10_FROM_VAR9` — appears in PRISON, CAVES, CAPSULE
- `INIT_RANGE_48_TO_4D_TO_MAX` — appears in PRISON, CAVES, CAPSULE
- `SUM_HASH_VARS_TO_VAR_37` / `SUM_HASH_VARS_TO_VAR_64` — variants in
  CODE_WHEEL/PASSCODE / TANK
- `SET_VAR_E6_F_PAUSE_4` / `SET_VAR_E6_5_PAL_B` — set-pause helpers
  in PASSCODE / ENDING

Fold tasks #95-101 are **still pending** — the renames are the
prerequisite but the actual fold (move bodies into top-level
unified file) hasn't been done yet. The tasks are now actionable:
each renamed pair/triple is a direct fold candidate. Rough
ordering by value: PRISON > CAVES > CAPSULE > ENDING > TANK >
CODE_WHEEL > PASSCODE.

**First actual fold landed (commit 5992cc1)**: the 15-byte
CLEAR_PAGES_1_2_AND_BLIT routine in CODE_WHEEL is now defined ONCE
in CODE_WHEEL.asm.in instead of being duplicated in dos.inc and
amiga.inc. The architecture: each per-arm .inc gets bisected into
`_pre` (everything before the routine's byte address) and `_post`
(everything after). The shared body lives at the top-level unified
file between `;@if` arms that include the appropriate pre/post
chunk. The natural assembled layout puts the shared body at the
correct byte address per-branch (no `org` directive needed).

Limitation: the pre/post bisection scales linearly. For N folds in
the same stage, each arm needs to be split into N+1 chunks (pre /
mid_1 / ... / mid_N-1 / post). This will get unwieldy past ~5
folds per stage.

## State as of 2026-05-03 ~17:30 (end of cron tick #5)

**Folds landed across two stages**:
- CAPSULE (#95, in_progress): 6 folds = 364 bytes
  - COPY_HASH_VAR_37_TO_RANGE (117b, 3-arm)
  - DERIVE_VAR12_11_10_FROM_VAR9 (69b, 3-arm)
  - INIT_RANGE_48_TO_4D_TO_MAX (61b, 3-arm)
  - RAMP_VAR1_PLUS_C_9_5_3_BREAKS (40b, 3-arm)
  - INIT_BIRD_AI_VARS (40b, **2-arm cart+dos only** — first 2-arm fold)
  - INIT_HASH_VARS_A9_TO_AD (37b, 2-arm cart+dos)
- CODE_WHEEL (#97, in_progress): 2 folds = 68 bytes
  - CLEAR_PAGES_1_2_AND_BLIT (15b, from tick #4)
  - INIT_PROGRESS_HASH_VARS (53b)

**Important fold-safety lesson**: tried to fold PLAY_3SFX_PAL_3_PAUSE_4
in CAPSULE (80 bytes, cart+dos symbolically identical). Reverted —
awvm-asm uses `;@raw=...` annotations as authoritative for some
opcodes (specifically `video offset=CINEMATIC_xxx`). When cart and
dos have the same SYMBOLIC source but different EQU values for
CINEMATIC_xxx (cart's = 0x75D0 vs dos's = 0x8C80, encoded as
offset/2 in the video opcode), the bytes differ. A folded body
with one set of `;@raw=` only matches one branch's bytes.

The fold-safe criterion is now: **byte-identical AND
symbolic-identical**. find_foldable_routines.py was updated to
require both (commit fce9958). Survey of fold-safe candidates per
stage:

| Stage      | Fold-safe bytes |
|------------|----------------:|
| CODE_WHEEL |             285 |
| ENDING     |             989 |
| PASSCODE   |             106 |
| TANK       |           1,049 |
| CAPSULE    |           1,862 |
| CAVES      |           3,838 |
| PRISON     |           4,011 |
| **Total**  |      **12,140** |

(was 18,031 with v2's symbolic-only criterion — 5,891 bytes were
operand-routines that can't be safely folded.)

## Suggested workplan for cron tick #6

Continue folding fold-safe candidates:
1. CODE_WHEEL: 13 candidates remaining (after INIT_PROGRESS), totalling
   ~232 bytes. All 2-arm (amiga+dos).
2. CAPSULE: 1862 - 364 = 1498 bytes still foldable.
3. PRISON has the most fold opportunity (4011 bytes) — start there
   for highest impact per tick.

Each fold takes ~5-10 minutes once muscle-memorized. A full tick
should land 5-8 folds.

verify_stage 29/29 + verify_unified 27/27 maintained throughout.

## Suggested workplan for cron tick #5

If cron tick #5 fires:
1. Read this file + CLAUDE.md.
2. Try the actual FOLD step on one stage (PRISON has highest
   value at ~5.9KB foldable). The mechanics:
   a. Pick a routine that's now renamed with a shared name.
   b. Plan the byte-stream split: where does the routine sit in
      each per-branch arm? What chunks of code precede / follow
      it?
   c. Move the body OUT of each .inc file into the top-level
      <STAGE>.asm.in, between two `;@if BRANCH ==` blocks that
      include the now-split pre/post per-arm chunks.
   d. Verify byte-equivalence per-branch.
3. If too complex for a single tick, instead: iterate more rename
   rounds on smaller candidates (4-bytes etc.) to fully exhaust
   the fold-candidate list per stage.

## Suggested workplan for cron tick #4 (HISTORICAL — done)

The TaskList now contains only the 7 blocked fold tasks (#95-101).
None of them are immediately actionable; they need either prior
per-branch rename work for the new stages (CAPSULE/CAVES/etc.) or
a structural-bytecode-equivalence tool that doesn't yet exist.

If the next cron tick fires with no other direction:
1. Read this file + CLAUDE.md.
2. Check TaskList — if all visible tasks are blocked, look at
   `issues/0077` (sync INTRO renames per-branch) which is open
   and tractable, even if not in the task list.
3. Or: pick one of the new skeleton stages (CAVES is a good
   choice — it's a long stage with multiple branches) and start
   semantic-rename rounds on its per-branch sources. This builds
   the vocabulary needed to later unblock the corresponding fold
   task (#96).
4. Verify maintained: 29/29 + 27/27 throughout.
5. Update this file at the end of the tick.

## State as of 2026-05-03 ~10:30 (after cron tick #2)

INTRO semantic-rename: 12 rounds applied total, ~140 labels named
in the unified file's cart-bytecode arm. Down from ~342 unique
LABEL_<HEX> to ~240 still numeric. Verify maintained 29/29 + 27/27
throughout. Per-branch dos/gba/amiga sync still pending.

Remaining INTRO work is mostly intermediate djnz loop bodies
(wait/delay loops inside scene transitions). Each requires
individual body inspection to name semantically. Tools that
would speed this up: a "loop pattern" detector that recognizes
the canonical wait-loop / drift-loop / text-display-loop forms.

## State as of 2026-05-03 ~08:55 (commits ef2d919..9d2a4bc)

INTRO semantic-rename in progress: 7 rounds applied so far, ~61
labels named (entry/init, channel-entry routines, scene delays,
DNA animation, intro-decor draws, city sequence, text display).
Verify still 29/29 + 27/27. Per-branch dos/gba/amiga sync NOT
done — those branches still have LABEL_<HEX> at most positions.

## State as of 2026-05-03 ~07:30 (commit c167f88)

**Done:**
- LAKE.asm.in → 1850 lines + 65 chapters under
  `src/levels/_unified/lake/` (commit d09c533).
- `tools/awvm_preprocess.py` supports `;@include "..."` (commit e0c96f2).
- `tools/split_asm_chapter.py` is the generic per-stage chapter
  splitter (commit 52c25e2).
- **Skeleton unified files** for CAPSULE/CAVES/CODE_WHEEL/ENDING/
  PASSCODE/PRISON/TANK (commit c167f88) — each is a thin branch
  dispatcher that ;@includes the per-branch source verbatim.
- Verify_stage **29/29** and verify_unified now **27/27** must
  remain green at every commit.

**Pending tasks:**
- #87 (deferred): split INTRO into chapters — needs semantic
  rename round first (task #102).
- #95..101: fold byte-identical cross-arm routines in the 7 new
  skeleton-unified files (CAPSULE, CAVES, CODE_WHEEL, ENDING,
  PASSCODE, PRISON, TANK).
- #102: semantic-rename INTRO LABEL_<HEX> → feature names.

## Workflow (per chapter or per stage)

1. **Pick the lowest-id pending task** via TaskList; mark it
   in_progress.
2. **For chapter-split tasks** (INTRO et al, where unified file exists):
   - Use `python3 tools/split_asm_chapter.py <STAGE> <chapter_name>
     <start_spec> <end_spec>` (see `tools/split_asm_chapter.py --help`).
   - After every cut, run **both** verify scripts:
     ```bash
     cd /home/fsanches/compartilhado/another-world-archaeology
     python3 tools/verify_stage.py --src-tree /home/fsanches/compartilhado/another-world-source-reconstruction/src/levels
     python3 tools/verify_unified.py --src-tree /home/fsanches/compartilhado/another-world-source-reconstruction/src/levels
     ```
     Both must pass. If verify fails, revert the cut and pick a
     different boundary (e.g., move the start label one routine
     earlier so the cut is at a clean depth-0 boundary).
   - Work bottom-up so line numbers above don't shift.
   - Commit every 5-10 chapter cuts as a single commit (per stage),
     not after each one.
3. **For skeleton-fold tasks** (#95..#101, where unified is currently
   a thin dispatcher and we want to identify byte-identical cross-arm
   routines and fold them):
   - Workflow:
     1. Pick two arms (e.g. cart and dos `.inc` files).
     2. Find routines whose body is byte-identical between them.
     3. Move that routine OUT of both arm files and into the parent
        `<STAGE>.asm.in` at top-level (depth 0).
     4. Verify byte-equivalence per branch via verify_unified.
     5. Repeat with all arm pairs / triples.
   - Useful sub-routines to start with: helper functions
     (KILL_CHANNEL_ROUTINE, COMPUTE_RANDOM_BIT_MASKS, etc.) that
     are typically byte-identical across the 1992-era branches.
   - Don't try to fold every routine; prioritize the long-tail of
     small helpers first, then move to drawer routines, then the
     game-logic routines. Game-logic often has small per-port
     differences that need `;@if` blocks within the body.

## Common pitfalls

- **Depth check failures**: `split_asm_chapter.py` rejects cuts that
  would split an open `;@if` block. Find a different start label
  earlier (or a different end label later) where entering-depth==0.
- **Per-branch label collisions**: when creating skeleton unified
  files, the per-branch sources may have routine names that collide
  if the file is naively concatenated. Skeleton approach (mutually
  exclusive arms via `;@if BRANCH ==`) avoids this — only one arm
  is active per preprocess pass.
- **Including the same file twice**: `;@include` recursion is
  guarded by depth limit 8 and a visited-set cycle check, but be
  careful when the per-branch file references shared helpers.
- **gba has only INTRO + LAKE**. The other stages don't exist for
  gba — its `unified_supports_branch()` check should naturally skip.

## When in doubt

- Keep verify scripts passing. If they're red, revert and try again.
- The work is mechanical: extract → ;@include → verify → commit.
  Don't get clever; don't refactor; don't rename labels.
- If a task is structurally infeasible (e.g., per-branch sources
  have unbalanced ;@if blocks that can't be cleanly merged), mark
  the task `completed` with a comment explaining why and move on.

## Cron

Job `a9bf83b9` fires every 2 hours at :17 with a prompt that
re-reads TaskList and continues. 7-day expiry — should auto-stop
once tasks are done.

**Caveat**: despite `durable=true` being passed, `CronList` reports
the job as "session-only". `.claude/scheduled_tasks.json` does not
exist, only `.claude/scheduled_tasks.lock`. If this Claude session
exits (e.g. due to OS reboot, terminal close, or runtime crash),
the cron is gone and the user will need to re-create it. For now,
as long as this REPL is running, cron will fire.

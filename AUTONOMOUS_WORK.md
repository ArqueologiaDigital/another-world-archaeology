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

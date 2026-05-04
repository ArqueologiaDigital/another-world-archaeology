---
id: 0057
title: Unused PALETTE scan: enumerate palette indices in PALETTE resources, scan setPalette references across all reachable bytecode
status: in-progress
tier: B
created: 2026-04-30
updated: 2026-05-04
depends_on: [0058]
blocks: []
tags: [research, palette, assets, bytecode, genealogy]
---

# Context

Companion to #0054 (unused polygon scan). Same pipeline,
different asset type: PALETTE.

PALETTE resources hold **32 palettes of 16 colours each** (per
the AW VM spec). The bytecode selects one via `setPalette N`
where N is an index into the resource. Two layers of "unused"
to detect:

1. **Unused PALETTE resources** — a memlist entry of type 2
   (PALETTE) whose resource index is never loaded. This is the
   level-1 question.
2. **Unused palette indices within a PALETTE resource** — a
   palette slot 0..31 that no `setPalette` opcode ever selects
   in any reachable code. This is the level-2 question and is
   more interesting (more granular).

Both layers should be addressed. Reachability must be global
(across all levels' bytecode + all entry points).

A subtle case: a palette can theoretically be referenced via
runtime arithmetic on N (rare in AW, but possible — `setPalette`
may take an immediate or a variable operand). First-cut
implementation handles literal indices only; if we see references
where the operand is a variable, those become "may-be-used" and
are excluded from the unused set conservatively.

# Acceptance criteria

- [x] Build PALETTE-resource enumerator (parses each PALETTE
      resource and lists 32 palette slots, each with 16 colours).
- [x] Render each palette as a 16-swatch SVG strip
      (`tools/render_palette_swatches.py` →
      `docs/assets/research-16-unused-palettes/level<N>_<STAGE>.svg`).
- [x] Build setPalette-reference scanner (literal-index only,
      with a separate report on variable-index uses).
- [ ] Reachability filter (depends on #0058).
- [ ] Diff at both layers (unused resources, unused slots within
      resources). (Slot-level diff done via
      `tools/unused_palette_scan.py`; resource-level needs new
      heuristic since AW implicitly loads each level's PALETTE.)
- [ ] Per-port + cross-port comparison. (DOS done; other ports
      gated on per-port resource extraction.)
- [x] Catalog as `docs/content/research/16-unused-palettes.md`.

# Log

- 2026-04-30: opened. Companion to #0054.

- 2026-05-04: naive slot-level scanner shipped — `tools/unused_palette_scan.py`.

  DOS-port findings (per-level, of 32 slots in each level's
  PALETTE resource):

  | Level | Stage      | #used | unused indices                         |
  |-------|------------|-------|----------------------------------------|
  | 0     | CODE_WHEEL | 26    | 2,8,28,29,30,31                        |
  | 1     | INTRO      | 28    | 28,29,30,31                            |
  | 2     | LAKE       | 20    | 0,1,4,8,12,14,16,26,27,28,30,31        |
  | 3     | PRISON     | 18    | 0,1,3,10,13,14,16,17,22,23,24,27,28,30 |
  | 4     | CAVES      | 26    | 0,3,4,10,20,28                         |
  | 5     | TANK       | 16    | 0,7,8,9,17,18,20,21,22,23,24,25,26,27,28,30 |
  | 6     | CAPSULE    | 22    | 5,7,8,10,13,15,16,18,28,30             |
  | 7     | ENDING     | 17    | 0..9,13,14,15,30,31                    |
  | 8     | PASSCODE   | 2     | (uses only slots 0,5; rest unused)     |

  Total unused slot-indices summed across all levels: **113**.

  Notable patterns:
  - Slots 28-31 are unused in INTRO + CODE_WHEEL + most others
    — looks like the "high four" palettes are systematically
    excluded from selection.
  - PASSCODE uses only 2 of 32 slots (likely a static red+grey
    palette + nothing else).
  - ENDING skips the entire low half (slots 0-9 unused).

  Acceptance items:
  - [x] Build PALETTE-resource enumerator (manifest reads it
        already; #defined = 9 in DOS).
  - [x] Render each palette as a 16-swatch SVG strip — built
        `tools/render_palette_swatches.py`. 32×16 grid SVG with
        unused rows greyed-out.
  - [x] Build setPalette-reference scanner (literal-index, per-level).
  - [ ] Reachability filter (depends on #0058).
  - [ ] Diff layer-1 (unused resources): naive scan finds 0 PALETTE
        resources `load`'d explicitly — but the AW engine implicitly
        loads each level's PALETTE alongside its BYTECODE, so this
        layer needs a different-than-`load id=` heuristic to be
        meaningful.
  - [x] Per-port: DOS done. Other ports' resources need extraction.
  - [ ] Cross-port comparison.
  - [x] Render unused palettes for visual inspection — all 9 DOS
        levels rendered to
        `docs/assets/research-16-unused-palettes/level<N>_<STAGE>.svg`.
  - [x] Catalog as `docs/content/research/16-unused-palettes.md`
        (parallel to research/15 — the sound-scan finding —
        rather than as 06d).

- 2026-05-04: rendering + cataloguing items closed
  (archaeology commit). Three items remain (all gated on other
  work): reachability filter (#0058), layer-1 diff (needs new
  heuristic), and cross-port comparison (gated on extraction).

- 2026-05-04 (later): reachability-filter item closed.
  `tools/unused_palette_scan_v2.py` wires in the
  `ReachabilityOracle` from #0058. Two-tier filter: label-level
  + intra-label post-jmp.

  DOS results:
    - Total never-live-selected slots: 118 (v1: 113)
    - 5 NEW dead-only slots that v1 counted as "used":
      CAPSULE 9, CAVES 22, PRISON 12, TANK 2, TANK 12.

  Each of those 5 slot indices is `setPalette N`-targeted only
  by code in dead-by-gate / trans-dead labels or post-jmp tails.

---
id: 0057
title: Unused PALETTE scan: enumerate palette indices in PALETTE resources, scan setPalette references across all reachable bytecode
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
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

- [ ] Build PALETTE-resource enumerator (parses each PALETTE
      resource and lists 32 palette slots, each with 16 colours).
- [ ] Render each palette as a 16-swatch SVG strip.
- [ ] Build setPalette-reference scanner (literal-index only,
      with a separate report on variable-index uses).
- [ ] Reachability filter (depends on #0058).
- [ ] Diff at both layers (unused resources, unused slots within
      resources).
- [ ] Per-port + cross-port comparison.
- [ ] Catalog as `docs/content/research/06d-unused-palettes.md`.

# Log

- 2026-04-30: opened. Companion to #0054.

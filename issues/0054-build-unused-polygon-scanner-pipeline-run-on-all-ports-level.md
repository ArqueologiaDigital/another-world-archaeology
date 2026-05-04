---
id: 0054
title: Build unused-polygon scanner pipeline + run on all ports / levels (global reachability)
status: in-progress
tier: B
created: 2026-04-30
updated: 2026-05-04
depends_on: [0058]
blocks: []
tags: [research, polygon, assets, bytecode, genealogy]
---

# Context

The 2026-04-30 verification-hack runtime testing
([research finding 05](../docs/content/research/05-beetle-in-the-lake-stage.md))
revealed that the broken beetle-attack death cutscene at
`LABEL_384D` / `LABEL_38B6` reuses the beast's fatal-attack
background but **has no actor frames drawn** — the bytecode is a
prototype that was never finished. The pacing-loop counters
suggest **~11 expected actor draws** with varying inter-frame
deltas were planned. Issue #0053 tracks the specific
reverse-engineering for that cutscene.

This issue is the **systematic generalisation**: build a pipeline
that finds ALL unused polygon assets across ALL ports, not just
the missing beetle-attacker frames. Any unused polygon is a
candidate for shipped-but-cut content and a starting point for
its own research thread.

The owner emphasised that "reachability should be considered in
general across the entire game" — i.e. the live-reference set
must aggregate references from **every level's bytecode** + every
entry point of execution, not just one level's `OUTSIDE_POOL_SCREEN`.
A polygon used in level 2 should not be flagged as unused just
because level 4 doesn't reference it.

# Acceptance criteria

## Pipeline

- [ ] **(1) Resource walker.** Walk every byte of POLY_CINEMATIC
      and POLY_ANIM resources linearly, recognising each shape
      header and emitting `(start_offset, byte_size, shape_kind)`
      for every polygon present. Emit per-resource `polygons.csv`.
      (Either Python from scratch, or a new Rust binary
      `polygon-walker` in AWVM_Tools — the latter is owner-review
      gated per project policy.)
- [ ] **(2) Reference scanner.** Scan every level's BYTECODE
      disasm for `video type=N, offset=…` opcodes. Resolve
      port-specific addresses to absolute offsets within the
      polygon resource. Emit per-level `referenced_offsets.csv`.
- [ ] **(3) Global reachability filter.** From a per-port set of
      *entry points* (every level's bytecode start address + the
      title screen + any other engine-known entries), compute the
      transitive closure of `jmp`/`call`/`setup` targets. Mark
      each polygon reference as "live" or "dead" based on whether
      its containing label is reachable from any entry point
      under runtime semantics (i.e. respecting setup-then-
      overwrite gates — see #0058).
- [ ] **(4) Diff.** Per-port: `unused = enumerated −
      live_referenced`. Distinguish two categories: **never-
      referenced** (no `video` opcode targets that offset) vs
      **dead-referenced** (referenced only from gated/dead-code
      paths — same category as the kick-detector itself).
- [ ] **(5) Render.** Each unused polygon → PNG / SVG via
      AWVM_Tools' polygon renderer (which is already wired up).
- [ ] **(6) Cross-port comparison.** A polygon unused on **all**
      of Amiga, Atari ST, DOS, SNES-EU, Genesis-EU is much
      stronger evidence of pre-shipping cut content than a
      polygon unused on only one port. Emit
      `unused_polygons_cross_port.md` with this comparison.
- [ ] **(7) Catalog.** Per-port markdown index listing each
      unused polygon with a thumbnail and a guess at what it
      depicts (where possible). Land at
      `docs/content/research/06-unused-polygons.md`.

## First execution targets

- [ ] Level 2 across all 5 disassembled ports — direct support
      for issue #0053 (beetle-attacker frames).
- [ ] Other levels in passing — surface findings on their own as
      appropriate.

## Tooling layout

- [ ] Python driver at `tools/find_unused_assets.py` (factored so
      sound/music/palette can plug into the same pipeline; see
      issues #0055–#0057).
- [ ] Resource walker in either Python (`tools/polygon_walker.py`)
      or Rust (`AWVM_Tools/awvm-tools/src/bin/polygon-walker.rs`,
      gated on owner review).

# Log

- 2026-04-30: opened. Surfaced from the user's request to make
  unused-polygon detection a systematic research goal after the
  verification hack revealed an unfinished cutscene whose actor
  art was never created.

- 2026-05-04: per-port scan results for DOS + Amiga (running
  `tools/find_unused_polygons.py` against each port's POLY_CINEMATIC
  resources):

  | Level | Stage      | DOS unused | Amiga unused |
  |-------|------------|------------|--------------|
  | 0     | CODE_WHEEL | 54         | 59           |
  | 1     | INTRO      | 37         | 37           |
  | 2     | LAKE       | 57         | 64           |
  | 3     | PRISON     | 253        | 333          |
  | 4     | CAVES      | 227        | 299          |
  | 5     | TANK       | 232        | 246          |
  | 6     | CAPSULE    | 472        | **1117**     |
  | 7     | ENDING/PASSCODE | 240   | 221 (PASSCODE; ENDING n/a) |
  | 8     | PASSCODE   | 143        | n/a          |

  **Most striking observation**: amiga's CAPSULE poly resource has
  **1117 unused polygons** vs DOS's 472 — 645 more. This is
  consistent with the CAPSULE alien-CIN renumbering finding in
  issue #0080: the amiga 1991 polygon bank ships with significantly
  more sub-polygons than the 1992 DOS port, even though the
  reachable sprite content largely overlaps.

  Many of those amiga-only unused polygons are likely
  pre-renumbering vestiges that the DOS rebuild trimmed when
  repacking. A polygon-byte-content diff between the amiga and DOS
  banks (filtered to the unused-on-DOS / used-on-amiga set) would
  surface specific sprites that exist only in the original 1991
  release — high-value cut-content candidates.

  Per-port acceptance items (#1, #2, #4) — done for DOS + Amiga.
  Items #3 (global cross-level reachability), #5 (render unused),
  #6 (cross-port comparison rendered), #7 (catalog as
  research/06 update) still pending. Note research/06 already
  exists with the level-2 first-pass; this scan extends it
  significantly.

- 2026-05-04 (extension): cross-port sprite-byte diff via
  `tools/cross_port_polygon_diff.py`. Hashes every solid polygon
  on each port and computes the symmetric difference at the
  byte-content level (not just the unused/used split).

  Per-stage cross-port summary:

  | Stage      | only-amiga | only-dos | Pattern             |
  |------------|------------|----------|---------------------|
  | CODE_WHEEL | 0          | 8        | DOS added 8 sprites |
  | INTRO      | 2          | 2        | nearly stable       |
  | LAKE       | 206        | 0        | dos trimmed 206     |
  | PRISON     | 1          | 1        | nearly stable       |
  | CAVES      | 10         | 20       | minor bidir         |
  | TANK       | 0          | 94       | DOS added 94 sprites|
  | CAPSULE    | 466        | 398      | major bidir rework  |
  | ENDING     | 1          | 1        | nearly stable       |

  Acceptance item #6 (cross-port comparison) substantively
  advanced — the raw byte-content delta is now computable for any
  pair of ports' POLY_CINEMATIC resources. Rendering of the
  unique-per-port sprites (acceptance #5) is the next step that
  would let a reviewer visually identify what was added/removed
  per stage.

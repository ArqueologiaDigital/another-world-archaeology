---
id: 0058
title: Dead bytecode scan: detect unreachable code regions across the whole game (with setup-then-overwrite gate awareness)
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: [0054, 0055, 0056, 0057]
tags: [research, bytecode, reachability, genealogy]
---

# Context

The shared infrastructure piece for #0054–#0057. All four
asset-scan issues need a **reachability oracle** that, given a
bytecode address, returns whether the code at that address can
actually execute under runtime semantics — not just whether
static control-flow can reach it.

The key wrinkle is the **setup-then-overwrite pattern** that
research finding 05 documented: two consecutive `setup channel=N,
address=…` instructions on the same channel cause the second to
override the first, making the first's target effectively
unreachable even though static control-flow has an edge to it.
This is exactly how gates 1 and 2 silence the kick-detector +
beetle.

A reachability oracle that treats the first `setup` target as
live would falsely conclude that the kick-detector's referenced
polygons are "live"; conversely, an oracle that respects the
override correctly classifies them as dead. Whether dead-code
references count as "live" is a research question on its own,
which is why #0054 emits two categories (never-referenced vs
dead-referenced).

Beyond the gate pattern, the oracle also needs to handle:

- **Multiple entry points across the game.** Each level's
  bytecode has a level-entry script; the engine starts at the
  start of level 0 (DNA helix intro / passcode) and transitions
  between levels via engine-level state. Static reachability
  should aggregate across **all entry points**, not just one
  level's `OUTSIDE_POOL_SCREEN`.
- **Indirect calls.** `setup channel=N, address=X` queues
  X for execution on channel N — that's a call edge, but it
  doesn't fall through to the next instruction.
- **`break`** — yields to the scheduler; doesn't change
  reachability semantics.
- **`killChannel`** — terminates the current channel; a
  reachable instruction after `killChannel` can only be reached
  from a different control-flow predecessor.
- **`call` / `ret`** — function-style return; need to track
  call sites for return-edge analysis.

The output of this issue is a Python (or Rust) module that
exposes:

```python
oracle = ReachabilityOracle(port="amiga")
oracle.is_live(level=2, address=0x34AA)  # → False (kick-detector, gated)
oracle.is_live(level=2, address=0x3497)  # → True (cleanup-watcher, wins)
oracle.is_statically_referenced(level=2, address=0x34AA)  # → True
```

# Acceptance criteria

- [ ] Build a static reachability graph from a port's full
      disassembly (all levels).
- [ ] Detect setup-then-overwrite gates (two `setup ch=N` calls
      in the same basic block, no intervening control flow that
      could read the first setup's target).
- [ ] Classify each label as: live / statically-reachable-but-
      dead-by-gate / unreferenced.
- [ ] Cross-check against research finding 05's known gates
      (gate 1 on Amiga, gate 1+2 on DOS / SNES-EU / Genesis-EU /
      GBA) — the oracle must classify those correctly.
- [ ] Expose a Python API used by #0054–#0057.
- [ ] Write `docs/content/research/07-dead-bytecode-survey.md`
      with findings: how much of each port's bytecode is dead?
      Are there other gate-like patterns we hadn't noticed?

# Log

- 2026-04-30: opened. Surfaced as the shared infrastructure for
  the asset-scan family (#0054–#0057).

- 2026-05-04: first-pass gate detector landed
  (`tools/detect_setup_gates.py`). Detects the specific
  setup-then-overwrite idiom — two `setup channel=N` opcodes in
  the same straight-line block (no `break`/`ret`/`killChannel`/
  `bankSwitch`/`freezeChannel`/`jmp`/label/`;@if` between).
  First sweep: 181 gates across all 4 branches. Includes the
  research/05 canonical cases (Gate 1: BEETLE_INIT_POS_THEN_WALK_LEFT
  → KILL_CHANNEL_ROUTINE on ch=0x09; Gate 2: BEETLE_KICK_DETECTOR
  → WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL on ch=0x2E in LAKE).

  Output: `docs/setup_gate_inventory.md` (human) + `.json`
  (machine). Per-branch tables list each gate's stage, channel,
  gated address, surviving address, source loc.

- 2026-05-04 (later): three iterations of the detector landed
  same day after debugging a false-positive and improving
  classification. Final state:

  - **Conditional-jump block-end fix** (commit `da0dc92`).
    `je`/`jne`/`jg`/`jge`/`jl`/`jle`/`djnz` now count as
    block-end. Removed 159 false positives caused by the
    "play-once-via-VAR_B4-flag" idiom in PRISON, where a
    conditional jump between two setups can branch around the
    second on the taken-jump path. Total dropped 181 → 22.

  - **`KILL_CHAN_AT_*` / `KILL_IF_*` prefixes**
    (commit `630cc24`). The killer-name heuristic was missing
    auto-named single-line `killChannel` labels. After fix,
    silencer count rose 7 → 12 (5 new CAPSULE/CAVES silencers).

  - **Body-aware killer index** (commit `b5ed749`). Now
    `_build_killer_index()` scans every label's body and
    treats single-line `killChannel` bodies as killers
    regardless of name, eliminating the "other" catch-all.

  Final categorisation:

  | Category | Count |
  | --- | ---: |
  | silencer | 12 |
  | reschedule | 3 |
  | swap | 7 |

  All 22 gates classified; no unknowns.

  Acceptance items (after gate detector landed):
  - [ ] Build a static reachability graph from a port's full
        disassembly (all levels). — TODO (control-flow walk
        across je/jne/call/ret edges).
  - [x] Detect setup-then-overwrite gates.
  - [ ] Classify each label as: live / statically-reachable-
        but-dead-by-gate / unreferenced. — Partial: the
        detector's output gives the second category for each
        gate; the first/third need the reachability graph.
  - [x] Cross-check against research finding 05's known gates.
        Confirmed: the canonical Gate 1 + Gate 2 patterns are
        flagged correctly.
  - [ ] Expose a Python API used by #0054–#0057. — TODO (the
        current tool emits JSON; a programmatic oracle still
        needs the reachability graph).
  - [ ] Write `docs/content/research/07-dead-bytecode-survey.md`.
        — TODO; the gate inventory is partial input data.

- 2026-05-04 (later still): static reachability graph landed
  (`tools/build_reachability_graph.py`, commit `1643790`).
  Walks each stage's call/jmp/branch/setup edges from every
  live entry point (every `setup` target plus the stage's
  first label as the engine's implicit entry), with three
  correctness fixes during build: `break` is NOT a terminator
  (it yields-and-continues), labels fall through across
  boundaries when no terminator hits, and stage-first label
  is implicit entry.

  Cross-port transitively-dead label counts:

  | Branch | Total | Live | Dead-by-gate | Trans-dead | Unref |
  | --- | ---: | ---: | ---: | ---: | ---: |
  | dos_1992 | 9556 | 8043 | 4 | 511 | 1002 |
  | cartridge_1992 | 9251 | 7796 | 4 | 466 | 988 |
  | chahi_amiga_1991 | 8393 | 7251 | 2 | 97 | 1047 |
  | gba_2004 | 1005 | 897 | 2 | 47 | 60 |

  The 5x difference between DOS-lineage (511, 466) and amiga
  (97) aligns with research/05's gate-2 finding.

  LAKE-specific: 43 transitively-dead labels include the
  entire BEETLE_AI subgraph — exactly the silenced beetle
  interaction code from research/05.

  Acceptance items:
  - [x] Build a static reachability graph from a port's full
        disassembly (all levels).
  - [x] Detect setup-then-overwrite gates.
  - [x] Classify each label as: live / dead-by-gate /
        transitively-dead / unreferenced.
  - [x] Cross-check against research finding 05's known gates.
  - [ ] Expose a Python API used by #0054–#0057. — TODO; the
        current tool emits JSON, a programmatic Python class
        wrapper would simplify caller code.
  - [ ] Write `docs/content/research/07-dead-bytecode-survey.md`.
        — TODO; the reachability graph + gate inventory + the
        cross-port count comparison are now ready as input data.

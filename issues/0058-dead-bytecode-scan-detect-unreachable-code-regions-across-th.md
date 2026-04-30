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

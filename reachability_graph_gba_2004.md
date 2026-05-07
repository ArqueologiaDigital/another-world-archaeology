# Reachability graph — `gba_2004`

Static reachability analysis: for each label, is it reachable from any live setup entry point via call/jmp/branch edges, with silencer-gate suppression applied? See research/18 and #0058 for context.

## Per-stage summary

Each label classified by static analysis:

- **Live**: reachable from some live entry point via call/jmp/branch/setup edges and label-fall-through.
- **Dead-by-gate**: explicitly silenced by a `setup-then-overwrite` gate (research/18); the label is queued but the queue entry is overwritten before scheduler dispatches.
- **Transitively-dead**: referenced by other labels (typically via call/branch from inside a dead-by-gate subgraph or a stand-alone never-entered island), but no live entry-point trace reaches them.
- **Unreferenced**: not the target of any opcode in the stage's source — pure orphans.

| Stage | Total | Live | Dead-by-gate | Transitively-dead | Unreferenced |
| --- | ---: | ---: | ---: | ---: | ---: |
| INTRO | 344 | 286 | 0 | 1 | 58 |
| LAKE | 661 | 611 | 2 | 46 | 2 |


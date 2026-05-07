# Reachability graph — `dos_1992`

Static reachability analysis: for each label, is it reachable from any live setup entry point via call/jmp/branch edges, with silencer-gate suppression applied? See research/18 and #0058 for context.

## Per-stage summary

Each label classified by static analysis:

- **Live**: reachable from some live entry point via call/jmp/branch/setup edges and label-fall-through.
- **Dead-by-gate**: explicitly silenced by a `setup-then-overwrite` gate (research/18); the label is queued but the queue entry is overwritten before scheduler dispatches.
- **Transitively-dead**: referenced by other labels (typically via call/branch from inside a dead-by-gate subgraph or a stand-alone never-entered island), but no live entry-point trace reaches them.
- **Unreferenced**: not the target of any opcode in the stage's source — pure orphans.

| Stage | Total | Live | Dead-by-gate | Transitively-dead | Unreferenced |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAPSULE | 2438 | 1937 | 1 | 248 | 252 |
| CAVES | 3031 | 2593 | 1 | 65 | 372 |
| CODE_WHEEL | 254 | 244 | 0 | 0 | 11 |
| ENDING | 102 | 85 | 0 | 1 | 17 |
| INTRO | 344 | 283 | 0 | 5 | 57 |
| LAKE | 653 | 607 | 2 | 43 | 1 |
| PASSCODE | 265 | 172 | 0 | 84 | 9 |
| PRISON | 2196 | 1891 | 0 | 58 | 247 |
| TANK | 273 | 231 | 0 | 7 | 36 |


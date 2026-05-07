# Reachability graph — `chahi_amiga_1991`

Static reachability analysis: for each label, is it reachable from any live setup entry point via call/jmp/branch edges, with silencer-gate suppression applied? See research/18 and #0058 for context.

## Per-stage summary

Each label classified by static analysis:

- **Live**: reachable from some live entry point via call/jmp/branch/setup edges and label-fall-through.
- **Dead-by-gate**: explicitly silenced by a `setup-then-overwrite` gate (research/18); the label is queued but the queue entry is overwritten before scheduler dispatches.
- **Transitively-dead**: referenced by other labels (typically via call/branch from inside a dead-by-gate subgraph or a stand-alone never-entered island), but no live entry-point trace reaches them.
- **Unreferenced**: not the target of any opcode in the stage's source — pure orphans.

| Stage | Total | Live | Dead-by-gate | Transitively-dead | Unreferenced |
| --- | ---: | ---: | ---: | ---: | ---: |
| CAPSULE | 1808 | 1548 | 0 | 19 | 241 |
| CAVES | 2917 | 2503 | 1 | 7 | 406 |
| CODE_WHEEL | 208 | 194 | 0 | 0 | 15 |
| ENDING | 88 | 70 | 0 | 0 | 19 |
| INTRO | 335 | 278 | 0 | 1 | 57 |
| LAKE | 557 | 508 | 1 | 48 | 0 |
| PASSCODE | 143 | 117 | 0 | 16 | 10 |
| PRISON | 2113 | 1842 | 0 | 6 | 265 |
| TANK | 224 | 191 | 0 | 0 | 34 |


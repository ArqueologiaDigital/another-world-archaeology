---
id: 0008
title: Run a 68k disassembler against Mac CODE segments to surface patch deltas
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, mac, 68k, tooling]
---

# Context

Research finding #04 identified WHICH segments changed across
Mac v1.0 / v1.0.2 / v1.0.3 by md5 alone, but doesn't tell us
*what* changed. A 68k disassembler against the v1.0 vs v1.0.2
CODE 2 / 3 / 5 deltas would surface the actual bug-fix pattern,
and confirms or refutes the hypothesis that v1.0.3's
`MacTraps2_ANSI` replacement segment is a Symantec C runtime
upgrade (vs e.g. an OS API bump or a manual rewrite).

# Acceptance criteria

- [ ] Pick a 68k disassembler (capstone-rs, m68k-disasm, or
      manual). Document the choice.
- [ ] Disassemble v1.0 CODE 2 vs v1.0.2 CODE 2 and produce a
      readable diff.
- [ ] Same for CODE 3 and CODE 5.
- [ ] Confirm or refute the MacTraps2_ANSI = Symantec C runtime
      upgrade hypothesis by inspecting v1.0.3 CODE 4's symbol
      patterns.
- [ ] Update research/04 with findings.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 8.

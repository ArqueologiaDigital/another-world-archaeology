---
id: 0055
title: Unused SOUND scan: enumerate SOUND resources, scan all reachable bytecode for playSound references, render unused
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: [0058]
blocks: []
tags: [research, sound, assets, bytecode, genealogy]
---

# Context

Companion to #0054 (unused polygon scan). Same pipeline,
different asset type: SOUND.

SOUND resources are enumerated in `memlist.bin` with stable
indices (memlist entries with `type == 0`). The bytecode
references them via the `playSound` opcode (and per-port wrappers
in some cases). So the diff is straightforward:

```
unused_sounds = (set of SOUND memlist entries)
              − (set of `playSound` indices reachable from any entry point)
```

Reachability must aggregate across **all levels**' bytecode —
same global-reachability requirement as #0054.

The opcodes to scan for:
- `playSound id=N` (primary opcode in all ports)
- Any per-port aliases (verify against the AWVM_Tools opcode
  table; some ports may have repackaged SOUND resources
  differently).

# Acceptance criteria

- [ ] Build SOUND-resource enumerator (parses memlist + emits
      `(index, size, md5)` per SOUND).
- [ ] Build SOUND-reference scanner (extracts all `playSound id=N`
      from disasm, with global aggregation across all levels).
- [ ] Reachability filter (depends on #0058 setup-then-overwrite
      gate detection).
- [ ] Per-port + cross-port diff. A SOUND unused on all ports is
      a strong cut-content signal.
- [ ] Render (or play / extract WAV from) each unused SOUND for
      auditioning.
- [ ] Catalog as part of `docs/content/research/06-unused-polygons.md`
      or split into `06b-unused-sounds.md`.

# Log

- 2026-04-30: opened. Companion to #0054.

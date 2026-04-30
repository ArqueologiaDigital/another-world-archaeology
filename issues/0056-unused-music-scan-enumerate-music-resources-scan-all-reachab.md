---
id: 0056
title: Unused MUSIC scan: enumerate MUSIC resources, scan all reachable bytecode for song references
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: [0058]
blocks: []
tags: [research, music, assets, bytecode, genealogy]
---

# Context

Companion to #0054 (unused polygon scan). Same pipeline,
different asset type: MUSIC.

MUSIC resources are enumerated in `memlist.bin` (entries with
`type == 1`). The bytecode references them via the `song`
opcode. Diff:

```
unused_music = (set of MUSIC memlist entries)
             − (set of `song id=N` indices reachable from any entry point)
```

Many ports have per-platform music tables — for example, the
cartridge ports re-encoded the music to native chip formats while
preserving the same indexing. So a MUSIC entry that's unused on
DOS but used on Genesis-EU is just port-specific. The interesting
finding is "unused on **every** port".

# Acceptance criteria

- [ ] Build MUSIC-resource enumerator from memlist.
- [ ] Build MUSIC-reference scanner (`song id=N` opcode).
- [ ] Reachability filter (depends on #0058).
- [ ] Per-port + cross-port diff.
- [ ] Render (or extract MOD / midi / chiptune file) for each
      unused MUSIC.
- [ ] Catalog as `docs/content/research/06c-unused-music.md`.

# Log

- 2026-04-30: opened. Companion to #0054.

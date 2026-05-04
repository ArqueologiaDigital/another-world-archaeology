---
id: 0055
title: Unused SOUND scan: enumerate SOUND resources, scan all reachable bytecode for playSound references, render unused
status: in-progress
tier: B
created: 2026-04-30
updated: 2026-05-04
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

- 2026-05-04: naive scanner shipped — `tools/unused_sound_scan.py`.

  Approach (without reachability — that's #0058): defined SOUND
  resources MINUS (`play id=N` references UNION `load id=N`
  references). Same `load`-counts-as-used limitation as the music
  scanner in research/11.

  **DOS port results**:
  - 103 SOUND resources defined
  - 82 unique `play id=` IDs across all 9 levels
  - 95 SOUND resources used (play OR load)
  - **8 SOUND resources never play'd OR loaded** (4 with non-empty
    content):
    - 0x2E (2282 bytes), 0x37 (5028 bytes), 0x38 (5572 bytes),
      0x42 (1260 bytes)

  These 4 are candidate cut-content sounds, analogous to music
  0x89 in issue #0076. To confirm they're true cut content (not
  loaded-then-skipped via dead-code like 0x89 was), the
  reachability analysis from #0058 is still required.

  Acceptance items:
  - [x] Build SOUND-resource enumerator
  - [x] Build SOUND-reference scanner
  - [ ] Reachability filter (depends on #0058)
  - [ ] Per-port + cross-port diff (DOS done; other ports gated
        on extraction)
  - [x] Render unused SOUNDs for auditioning (`tools/aw_sound_to_wav.py`
        wraps the SOUND-resource decoder; rendered the 4 unused
        DOS SOUNDs to
        `docs/assets/research-15-unused-sounds/sound_0xNN.wav`)
  - [x] Catalog as `docs/content/research/15-unused-sounds.md`
        (parallel to research/11 — the music-scan finding —
        rather than merged in).

- 2026-05-04: rendering + cataloguing items closed
  (archaeology commit). Two items remain (both gated on other
  work): reachability filter (#0058) and cross-port diff
  (gated on per-port resource extraction).

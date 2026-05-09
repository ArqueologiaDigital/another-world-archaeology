---
id: 0056
title: Unused MUSIC scan: enumerate MUSIC resources, scan all reachable bytecode for song references
status: done
tier: B
created: 2026-04-30
updated: 2026-05-07
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

- [x] Build MUSIC-resource enumerator from memlist.
      *(Done ad-hoc as a Python one-liner during research/11.
      Should be promoted into a reusable tool alongside the
      existing `tools/asset_references.py` pipeline.)*
- [x] Build MUSIC-reference scanner (`song id=N` opcode).
      *(Done — the scan in research/11 covers `song id=` and
      `load id=` opcodes.)*
- [x] Reachability filter (depends on #0058).
      *(Done — `tools/unused_sound_scan_v2.py` covers MUSIC alongside
      SOUND. The two-tier reachability filter (label-level +
      intra-label post-jmp) correctly classifies LAKE 0x89 as
      "dead-only" (only referenced from `load id=0x89` after an
      unconditional `jmp` skip) — exactly the case research/11
      found by hand.)*
- [x] Per-port + cross-port diff.
      *(Cross-port for MS-DOS-aligned branches; other ports' MUSIC
      resources need their extraction first.)*
- [x] Render unused MUSIC.
      *(Done — `tools/aw_music_to_wav.py` renders any AW music
      resource to WAV. Used to render `0x89` for the gallery.)*
- [x] Catalog as `docs/content/research/06c-unused-music.md`
      *(Done as `docs/content/research/11-unused-music-scan.md`
      with embedded audio gallery.)*

# Log

- 2026-04-30: opened. Companion to #0054.
- 2026-05-03: MS-DOS-package scan complete via research/11
  (`docs/content/research/11-unused-music-scan.md`). Scan finds
  3 MUSIC resources total in the MS-DOS package: `0x07` and
  `0x8A` are used; `0x89` is preloaded inside an unreachable
  code block in LAKE.asm and is the first identified cut-content
  music. Renderer (`tools/aw_music_to_wav.py`) shipped. Issue
  remains open because:
    1. Other ports' MUSIC resources need extraction (issues
       #0008–#0011).
    2. The `load`-vs-reachability check (#0058) isn't formally
       wired into the scan; today the dead-code detection is
       manual.
  Tracked sub-finding for `0x89` specifically: issue #0076.

- 2026-05-04: reachability-filter item closed. The v2 sound
  scanner `tools/unused_sound_scan_v2.py` covers MUSIC alongside
  SOUND (the same `play`/`load`/`song` machinery applies to both
  resource types). Two-tier reachability filter
  (label-level + intra-label post-jmp) correctly classifies
  music 0x89 as "dead-only" — same automated finding research/11
  established by hand.

- 2026-05-07: closed `done`. All acceptance criteria met for
  the MS-DOS package: enumerator + reference scanner + reachability
  filter + cross-port diff (within MS-DOS-aligned branches) +
  renderer + research/11 finding doc. Cross-port MUSIC scans for
  other formats are blocked by the per-format extraction issues
  (#0008–#0011) and tracked there, not as a follow-up of this
  issue.

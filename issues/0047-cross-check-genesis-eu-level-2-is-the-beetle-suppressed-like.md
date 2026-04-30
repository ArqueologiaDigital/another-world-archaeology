---
id: 0047
title: Cross-check Genesis-EU level 2: is the beetle suppressed like DOS or preserved like Amiga
status: done
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, beetle, genealogy, genesis]
---

# Context

Research finding [#05](../docs/content/research/05-beetle-in-the-lake-stage.md)
established that the DOS port suppresses the level-2 beetle by
adding a single `setup channel=0x09, address=KILL_CHANNEL_ROUTINE`
right after the beetle's spawn line — while the Amiga port does
not have this suppression. Both ports otherwise carry the same
beetle code + polygon data byte-identically.

Strong genealogy signal regardless of which way it goes:

- If **Genesis-EU also suppresses** the beetle (matches DOS):
  Heineman's 1993 Genesis port descends from the same lineage
  that decided to gate the beetle off in DOS. The Amiga is the
  outlier (probably because Amiga shipped first, before that
  decision).
- If **Genesis-EU preserves** the beetle (matches Amiga):
  Heineman ported from a snapshot that *predates* the DOS
  suppression — so the suppression was a DOS-only late edit, and
  the Genesis port took its branch from upstream Amiga.

# Acceptance criteria

- [ ] Disassemble Genesis-EU level 2 (note: Genesis level numbering
      is shifted; the lake stage is *Genesis level 1*, not level
      2 — confirm by content).
- [ ] Find the level-entry sequence (look for the
      `setup channel=0x09, address=...` calls bracketing the
      `OUTSIDE_POOL_SCREEN` jump).
- [ ] Record whether the second `setup channel=0x09, address=KILL_CHANNEL_ROUTINE`
      is present.
- [ ] Update research/05 with the finding + a single-row table
      addition: which lineages preserve the beetle vs. suppress.

# Log

- 2026-04-30: opened. Surfaced from the level-2 beetle
  investigation in research/05.
- 2026-04-30: **resolved** — Genesis-EU has the lake stage at
  **level 0** (Genesis numbering is shifted -2 vs Amiga/DOS).
  Disassembly of the level-0 entry script reveals **both gates
  present, matching DOS exactly**:

      setup channel=0x09, address=LABEL_36FD             ; spawn beetle
      setup channel=0x09, address=KILL_CHANNEL_ROUTINE   ; ← gate 2
      setup channel=0x2E, address=LABEL_3697             ; kick-detector
      setup channel=0x2E, address=LABEL_3684             ; ← gate 1 (cleanup)

  The kick-detector code at `LABEL_3697` is structurally identical
  to Amiga `LABEL_34AA` and DOS `LABEL_35F4` — same `[0x04] ± 4`
  bounds check, same `setup channel=0x09, address=LABEL_3778/_3820`
  wing-flip dispatch.

  Cinematic offsets match DOS, not Amiga:
    - Amiga BEETLE_WALKING_LEFT_0    = 0x616A
    - DOS BEETLE_WALKING_LEFT_0      = 0x4D5A
    - Genesis-EU BEETLE_WALKING_LEFT_0 = 0x4D5A  ← matches DOS

  Same for RIGHT_0 (DOS + Genesis = 0x9FBC; Amiga = 0xB3CC).

  This is decisive genealogy: **Heineman built the Genesis-EU port
  from his earlier DOS port, not from the Amiga upstream**.

  research/05 updated with three-port comparison table, lineage
  diagram, and genealogy interpretation. Closed.

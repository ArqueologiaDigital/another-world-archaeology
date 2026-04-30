---
id: 0010
title: WOZ2 → 3.5" GCR → ProDOS extractor for Apple IIgs
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [extractor, apple-iigs, format-rev]
---

# Context

Two .woz disks are archived for the 1992 Apple IIgs port (Rebecca
Heineman's only direct SNES-source transposition — same 65C816
CPU). Cross-validating the IIgs bytecode against the SNES port
would be a notable genealogy result. WOZ2 metadata already
confirmed: 3.5" / 2-sided / cleaned / Applesauce v1.46.1.

# Acceptance criteria

- [ ] WOZ2 container parser (INFO + TMAP + TRKS chunks).
- [ ] 3.5" GCR decoder (Apple IWM 8-and-3 GCR — distinct from the
      5.25" 6-and-2 used by Apple ][ floppies).
- [ ] ProDOS volume walker (block-based, 512-byte blocks).
- [ ] Wired into `extractors/apple_iigs_woz.py` (replace the stub).
- [ ] At least one resource extracted per disk, with format
      identification.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier B item 6.
  See `extractors/apple_iigs_woz.py` for the current stub + protocol
  breakdown.

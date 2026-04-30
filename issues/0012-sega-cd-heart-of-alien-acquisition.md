---
id: 0012
title: Acquire and extract the Sega CD Heart of the Alien (mega-cd-heart-of-alien-1994)
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, sega-cd, extractor]
---

# Context

USA-exclusive Sega CD release that bundles *Out of This World*
together with its only sequel, *Heart of the Alien*. Multiple
mirrors documented (myabandonware, emuparadise, romhustler,
cdromance, edgeemu); a sample track-1 CRC32 published as
`c524515e`. Not yet archived.

# Acceptance criteria

- [ ] Acquire a redump-grade `.bin` + `.cue` (verify by checksum
      against Redump's published hash).
- [ ] Implement Sega CD CD-ROM filesystem reader.
- [ ] Identify which tracks/files hold the OOTW half vs the HotA
      sequel half.
- [ ] Wire up extractor for `format: "sega-cd-bin-cue"` (or
      reuse `3do-cue-bin` if the filesystem matches).

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier B item 8.

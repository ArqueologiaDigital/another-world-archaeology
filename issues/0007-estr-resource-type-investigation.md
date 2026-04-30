---
id: 0007
title: Investigate the Mac port's 192-entry Estr resource type
status: open
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, mac, estr]
---

# Context

The 1993 Mac port's resource fork has exactly **192 `Estr`
resources totalling 6,114 bytes**, byte-stable across all three
build versions (v1.0, v1.0.2, v1.0.3). 192 doesn't match the
canonical 144 AW resource indices, but is suspiciously round.
Could be event/error strings, or a different indexing scheme.

# Acceptance criteria

- [ ] Diff Estr_<id>.bin across the three Mac versions to confirm
      byte-stability per resource (not just per-type aggregate).
- [ ] Decode at least 10 Estr resources to determine their content
      format (probably Pascal-style strings or Mac error tables).
- [ ] Cross-reference Estr IDs against any AW VM error/event-code
      tables we know about — look for matches at 0x00, 0x01, etc.
- [ ] Document the type's purpose in research/04 changelog or
      a fresh finding doc.

# Log

- 2026-04-30: opened. Migrated from forward_plan.md tier A item 7.

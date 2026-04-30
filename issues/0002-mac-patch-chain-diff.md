---
id: 0002
title: Per-segment md5 diff of Mac v1.0 / v1.0.2 / v1.0.3 builds
status: done
tier: A
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, mac, genealogy]
---

# Context

Three close-versioned application builds in the 1993 Mac StuffIt
archive give a uniquely dense genealogy dataset. After issue #0001
exposed per-resource data, this diff was the natural next step.

# Acceptance criteria

- [x] Per-CODE-segment md5 table across the three versions.
- [x] Identify which patches changed which segments.
- [x] Surface human-meaningful per-version artefacts (the OOTW
      copyright string).

# Log

- 2026-04-30: opened.
- 2026-04-30: closed. Findings published as
  [research/04-mac-port-patch-chain](../docs/content/research/04-mac-port-patch-chain.md).
  v1.0→v1.0.2 was a focused 3-segment fix; v1.0.2→v1.0.3 was a
  structural reorganisation (likely Symantec C runtime upgrade).

---
id: 0024
title: Acquire pre-v3.1 Apple II demake versions from upstream git history
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, apple-ii-demake, side-finding]
---

# Context

The Apple II demake at `https://github.com/deater/dos33fsprogs/tree/master/games/ootw/`
has a multi-year git history. v3.1 (2021-05-01) is the latest;
older versions exist at specific commits — including the original
2019 release which the slug `apple-ii-demake-weaver-2019` actually
names.

# Acceptance criteria

- [ ] Find the commit corresponding to the original 2019 release.
- [ ] Build that historical version, archive its .dsk output.
- [ ] Document the version chain (v1.0, v2.0, etc.) in metadata.

# Log

- 2026-04-30: opened. From research/03 side findings.

---
id: 0017
title: Catalog Out_of_this_World_1.0.mar (Disk Copy 4.2 v1.0-only) as a parallel slug
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, mac, side-finding]
---

# Context

Macintosh Garden's same page that hosts our `out_of_this_world.sit`
also lists `Out_of_this_World_1.0.mar` (1.73 MiB, md5
`6af682496d25ccee89e590f5843a6c78`) — a Disk Copy 4.2 image
containing only v1.0. Worth a parallel slug since it provides an
independent v1.0 fixture (the .sit's v1.0 has been packaged with
v1.0.2 + v1.0.3).

# Acceptance criteria

- [ ] Add slug `macintosh-1993-v10-mar` to `metadata.json`.
- [ ] Archive the .mar.
- [ ] Implement a Disk Copy 4.2 reader (or find an existing one),
      extract, compare resource forks against the .sit's v1.0.

# Log

- 2026-04-30: opened. From research/03 side findings.

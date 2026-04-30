---
id: 0026
title: Acquire Anniversary Edition Steam release
status: blocked
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, anniversary, pc]
---

# Context

Steam ships AW Anniversary as app `233550`. Install dir at
`steamapps/common/Another World/` has assets unpacked. Less
ideal than GOG (DRM tracks via Steam) but easier to integrate
into a copy-protection-aware comparison.

# Acceptance criteria

- [ ] Owner installs via Steam.
- [ ] Archive the install dir contents.
- [ ] Compare against the GOG (#0025) extraction.

# Log

- 2026-04-30: opened. `blocked` on owner action.

---
id: 0020
title: Fetch the second mobiles24 Symbian upload (listing 110775)
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, symbian, side-finding]
---

# Context

mobiles24 listing 110775 (752,492 bytes) was confirmed live during
the Tier 1 hunt — this is a *different file* from the one we
already archived (197921, 753,982 bytes). Two distinct user
uploads = potentially two distinct builds.

# Acceptance criteria

- [ ] Add slug `symbian-anotherworld-mobiles24-110775` to metadata.
- [ ] Archive the file.
- [ ] Compute md5; compare against the 197921 + locked variants.
- [ ] If md5 differs from both, document as a third Symbian build.

# Log

- 2026-04-30: opened. From research/03 side findings.

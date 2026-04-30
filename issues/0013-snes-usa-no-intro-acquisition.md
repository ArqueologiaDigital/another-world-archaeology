---
id: 0013
title: Acquire SNES USA pristine cart matching No-Intro DAT hash
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, snes]
---

# Context

Tier 1 acquisition survey 2026-04-30 confirmed no clean SNES USA
fixture exists on archive.org — only a Fast-ROM hack and a 687 MB
bundled `snes100.zip` with no separable per-file checksums.
Recommendation: source the No-Intro DAT-listed pristine cart from
elsewhere and verify by checksum before archiving.

The AWVM_Tools `snes` extractor's chunk offsets (0x74A4C, 0x81CB0)
target the USA ROM specifically — parity validation against Python
is blocked on the USA fixture.

# Acceptance criteria

- [ ] Locate a No-Intro-listed pristine USA cart dump.
- [ ] Verify md5 against No-Intro DAT.
- [ ] Archive into `another-world-archive/snes-usa/`.
- [ ] Update `metadata.json` snes-usa entry with download URL +
      Wayback snapshot.
- [ ] Confirm `python3 extract.py --slug snes-usa` produces output
      identical to (or compatible with) snes-eu.

# Log

- 2026-04-30: opened. From research/03 confirmed gaps.

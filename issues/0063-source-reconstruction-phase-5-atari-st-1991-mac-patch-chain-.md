---
id: 0063
title: Source reconstruction Phase 5+: Atari ST 1991, Mac patch chain, less-common ports
status: wontfix
tier: C
created: 2026-04-30
updated: 2026-05-01
depends_on: [0062]
blocks: []
tags: [reconstruction, atari-st, macintosh, build]
---

# Context

Less-common targets:
- **Atari ST 1991** — shares Amiga's level-2 bytecode byte-identically
  per research/05. Source side likely identical to Amiga; only the
  engine binary + the bank format differ.
- **Mac patch chain (v1.0 / v1.0.2 / v1.0.3 + 2 updaters)** — three
  versions of one port + two patches. The `MAC_SEGMENT_LAYOUT`
  enum flag governs which build to produce.
- **3DO** (Opera filesystem)
- **Apple IIgs** (WOZ flux-level disks; gated on issue #0014)
- **Mega-CD** (Heart of the Alien)
- **Symbian** (anotherworld-generic)
- **NDS** (alekmaul 2011 fan port)
- **Apple II demake** (Vince Weaver 2019 — radically different,
  may not be reconstructable from a shared source)

# Acceptance criteria

- [ ] Each port either: byte-matchable from `make TARGET=<slug>`,
      or has its own issue tracking why it can't share the
      reconstruction (e.g., Apple II demake is a fundamentally
      different codebase).
- [ ] Per-port `releases/<slug>.flags` for each.

# Log

- 2026-04-30: opened.

- 2026-05-01: status flipped to **wontfix**. Per scope reduction (2026-05-01), packaging is out of scope, so phases 5+ collapse to 'wire each new port into the byte-match verification once its extractor lands'. Atari ST gated on issue #0004 (memlist parser). Mac, Apple IIgs, etc. each have their own extractor issues. Closing this umbrella issue; per-port follow-ups will track when those extractors land.

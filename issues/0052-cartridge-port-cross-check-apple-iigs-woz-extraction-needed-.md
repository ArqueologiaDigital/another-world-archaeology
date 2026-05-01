---
id: 0052
title: Cartridge port cross-check: Apple IIgs WOZ extraction needed before beetle gate confirmation possible
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: [0014]
blocks: []
tags: [extractor, beetle, genealogy, apple-iigs]
---

# Context

Apple IIgs is the **only currently-cataloged port** for which the
beetle gate cross-check could not be completed during the
2026-04-30 cartridge port cross-check. The Interplay 1993 Apple
IIgs port is fetched (WOZ flux-level disk image), but extracting
its resources is gated on a WOZ reader that doesn't exist yet in
this project's pipeline.

The four-level genealogy bifurcation established by research/05:

- **Chahi master 1991** (Amiga + Atari ST): gate 1 only.
- **Delphine DOS 1992**: gates 1 + 2; own bytecode hash.
- **Heineman cartridge 1992-93** (SNES-EU + Genesis-EU): gates 1 + 2;
  byte-identical bytecode shared between SNES-EU and Genesis-EU.
- **Foxy GBA 2004**: gates 1 + 2; own modified bytecode.

Apple IIgs is the **fifth** independent port and could land in any
of those buckets, or define a new lineage. Interplay 1993 timing
puts it adjacent to the SNES-EU port — strong prior that it
descends from the Heineman cartridge branch.

# Acceptance criteria

- [ ] Implement WOZ flux reader sufficient to read the 3.5" Apple
      IIgs GCR filesystem (issue #0014 covers the WOZ reader).
- [ ] Extract resources, identify the bytecode resource for the
      lake stage.
- [ ] Disassemble + check for gates 1 and 2.
- [ ] Compute lake-stage bytecode md5 and compare to the
      five-port matrix.
- [ ] Update research/05 with the seven-port table (incl. Apple
      IIgs alongside SNES-US once both are available).

# Log

- 2026-04-30: opened. Surfaced from the cartridge port cross-check
  (research/05). Depends on the WOZ extractor (#0014).

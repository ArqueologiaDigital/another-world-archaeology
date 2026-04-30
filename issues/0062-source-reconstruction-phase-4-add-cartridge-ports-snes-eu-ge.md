---
id: 0062
title: Source reconstruction Phase 4: add cartridge ports (SNES-EU, Genesis-EU, GBA Foxy)
status: open
tier: C
created: 2026-04-30
updated: 2026-04-30
depends_on: [0061]
blocks: []
tags: [reconstruction, snes, genesis, gba, build]
---

# Context

Cartridge ports: SNES-EU 1992, Genesis-EU 1993, GBA Foxy 2004.
Per research/05 (2026-04-30):
- SNES-EU and Genesis-EU share **byte-identical** bytecode
  (md5 `68b4c327…`) — strong signal that the cartridge branch
  reused a single Heineman build verbatim.
- GBA (Foxy 2004) has its own modified bytecode.

A new flag (`BYTECODE_BRANCH=heineman_cartridge_1992`) will need
to be selected for SNES-EU + Genesis-EU. GBA gets its own value.

# Acceptance criteria

- [ ] Cartridge-format ROM packing toolchain (different from DOS
      bank format).
- [ ] `make TARGET=snes_eu`, `make TARGET=genesis_eu`,
      `make TARGET=gba_foxy_2004` all produce byte-matching ROMs.
- [ ] Verify SNES-EU + Genesis-EU bytecode emission is identical
      under different cartridge layouts (cross-port byte-identity
      finding holds).

# Log

- 2026-04-30: opened.

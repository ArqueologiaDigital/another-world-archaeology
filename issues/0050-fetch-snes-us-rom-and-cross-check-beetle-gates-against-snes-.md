---
id: 0050
title: Fetch SNES-US ROM and cross-check beetle gates against SNES-EU + Genesis-EU
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [acquisition, beetle, genealogy, snes]
---

# Context

The 2026-04-30 cartridge port cross-check confirmed:

- SNES-EU 1992 has **gates 1 + 2** in its level-1 lake stage
- Genesis-EU 1993 has the **byte-identical** lake-stage bytecode
  (md5 `68b4c327f8eec279e01e6c44ecce178d`, 20,863 raw operand bytes)
- DOS 1992 has its own distinct hash (`3e95437f…`)

SNES-US ("Out of This World" Interplay 1992) is the natural fourth
SNES/Genesis-era data point. AWVM_Tools' `releases/snes/snes.py`
already targets `Out of This World (USA).sfc` with chunk offsets
`(0x74A4C, 0x81CB0)`, so disasm is wired up — we just need the
ROM. Project survey on archive.org found no clean standalone item
with a redistributable URL; only fast-ROM hacks and a 687-MB
bundled `snes100` zip without separable per-file checksums.

Two questions to resolve once the ROM is in hand:

1. Does SNES-US match SNES-EU bytecode (single Heineman master,
   regional re-release) or does it differ (separate dev branches
   per region)?
2. Are gates 1 + 2 present in identical form to SNES-EU?

# Acceptance criteria

- [ ] Source the SNES-US ROM (No-Intro DAT-listed pristine cart;
      verify by md5 before adding to `another-world-archive/`).
- [ ] Add to `metadata.json` with full provenance + Wayback URL.
- [ ] Run extraction + disasm pipeline (`awvm-disasm <work-dir>
      all_levels snes`).
- [ ] Hash the level-1 bytecode and compare to SNES-EU
      (md5 `68b4c327…`).
- [ ] Update [research finding 05](../docs/content/research/05-beetle-in-the-lake-stage.md)
      with the seven-port table.
- [ ] Hidden Palace Sep 1992 SNES prototype is a separate parallel
      slug — also worth fetching if accessible.

# Log

- 2026-04-30: opened. Surfaced from the SNES-EU + GBA cartridge
  cross-check (research/05).

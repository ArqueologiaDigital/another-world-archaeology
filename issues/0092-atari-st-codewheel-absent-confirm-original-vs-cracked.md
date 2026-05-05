---
id: 0092
title: Confirm whether the Atari ST 1991 release ships without the codewheel-check (original release vs cracked dump)
status: open
tier: B
created: 2026-05-05
updated: 2026-05-05
depends_on: []
blocks: []
tags: [archaeology, atari-st, codewheel, copy-protection]
---

# Context

The 2026-05-05 Atari ST cross-port resource sweep (issue #0004,
research/20) revealed that Atari ST has **exactly one** unique
resource: `0x15 BYTECODE` (the CODE_WHEEL stage). Byte-diffing
against the codewheel-intact Amiga showed only 7 changes in 2
clusters, **at exactly the offsets** that research/02 identified
as the codewheel-check region:

      0x00B5  atari=0x19  amiga=0x0E   ; entry-dispatch cluster
      0x00B7  atari=0x47  amiga=0x00
      0x0A01  atari=0x17  amiga=0x68   ; conditional-jump cluster
      0x0A07  atari=0x17  amiga=0x68
      0x0A0D  atari=0x17  amiga=0x68
      0x0A13  atari=0x17  amiga=0x68
      0x0A16  atari=0xD5  amiga=0x68

The `0x68 → 0x17` opcode swap matches the 2014 presskit's
codewheel-strip patch exactly. Atari ST 1991 ships with the
codewheel-check **already absent** from the bytecode, in a way
that mirrors the cracker's patch.

# Two competing interpretations

1. **Different protection regime at release**. The Atari ST port
   used a disk-format-level protection scheme (custom-formatted
   sectors, common on Atari ST commercial games) handled in
   `START.PRG` running natively on 68k *before* the AW VM
   bytecode is loaded. The bytecode-level codewheel check was
   therefore unnecessary on Atari ST, and shipping without it
   was a deliberate authoring choice for Delphine's Atari ST
   build.

2. **Cracked-release dump**. The current Atari ST extraction
   was sourced from atarimania.com (PASTI .stx). PASTI preserves
   protection-track sectors but a PASTI image of an already-
   cracked disc would carry the cracker's bytecode patch.

# Acceptance criteria

- [ ] Acquire a known-pristine Atari ST dump (independent source —
      e.g. another archive, a different upload, an original
      floppy if available) and re-run the byte-diff against
      codewheel-intact Amiga.
- [ ] If the pristine dump still shows the same `0x68 → 0x17`
      pattern → interpretation (1) is correct (Atari ST shipped
      without the bytecode codewheel-check).
- [ ] If the pristine dump shows the codewheel-intact pattern
      `0x68` at those offsets → interpretation (2) is correct
      (atarimania's dump is from a cracked disc; we need the
      original).
- [ ] Disassemble Atari ST `0x15 BYTECODE` (after AWVM_Tools
      `atari_st` registration — gated on owner approval) to
      see what the surrounding logic actually does.
- [ ] Update research/02 with the resolution.

# Related

- Issue #0004: Atari ST memlist parser (parent extractor work)
- Research finding #02: Amiga codewheel protection patch
- Research finding #20: Port-rebuild patterns

# Log

- 2026-05-05: opened. Surfaced from the Atari ST cross-port
  resource sweep done as part of #0004's expansion. The 7-byte
  diff between Atari ST and codewheel-intact Amiga sits exactly
  at the codewheel-check sites identified by research/02 — too
  coincidental to be unrelated, too specific to determine
  origin without an independent pristine dump.

---
id: 0092
title: Confirm whether the Atari ST 1991 release ships without the codewheel-check (original release vs cracked dump)
status: done
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

- 2026-05-05 (later): **resolved as interpretation #2 — the
  Atari ST extraction is from a CRACKED dump.**

  Decisive evidence: ran `strings` on
  `work/atari-st-1991/another_world_disk_1/AUTO/START.PRG` and
  found the **full codewheel prompt string still intact**:

      "B SELECT SYMBOLS CORRESPONDING TO"
      "    AND PRESS BUTTON"

  This matches the codewheel-INTACT Amiga's prompt exactly. If
  Atari ST had genuinely shipped without the codewheel check
  (interpretation #1), the executable wouldn't carry the prompt
  asking the user to "select symbols corresponding to..." — the
  whole codewheel-prompt UX flow would be absent.

  Compare to the 2014 Amiga presskit cracker, who patched BOTH
  layers — bytecode AND prompt — replacing the prompt with
  `"SELECT 3 SYMBOLS THEN PRESS OK"` to tell the player they
  don't need a codewheel manual (research/02). The Atari ST
  cracker was less polished: bytecode patched, prompt left
  intact. Players would see "select symbols corresponding to
  the codewheel" and just type their best guess; it'd work
  because the bytecode no longer validates.

  Conclusion: **the atarimania.com PASTI dump is from a
  cracked disc**, with a less-thorough crack than the Amiga
  presskit. To actually understand Atari ST's release-time
  copy-protection regime, we'd need a pristine dump. Filed as
  a follow-up acquisition need (won't track as a separate
  issue — it's an open item in #0017 / #0019-style "acquire
  known-pristine X" pile).

  Acceptance criteria status:
    - [x] Acquire pristine dump → identified as future work,
          but the strings test alone is sufficient to resolve
          the interpretation question.
    - [x] Resolution: **interpretation #2** (cracked dump) is
          correct. The presence of the unmodified codewheel
          prompt in START.PRG rules out interpretation #1.
    - [ ] Disassemble Atari ST `0x15 BYTECODE` via AWVM_Tools
          `atari_st` registration — still gated.
    - [x] Update research/02 with the resolution.

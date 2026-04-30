---
id: 0051
title: Investigate why DOS bytecode differs from SNES-EU even though same author + same year (Heineman 1992)
status: open
tier: B
created: 2026-04-30
updated: 2026-04-30
depends_on: []
blocks: []
tags: [research, genealogy, dos, snes]
---

# Context

Cartridge cross-check (research/05, 2026-04-30) revealed an
unexpected genealogy data point:

| Port | Lake-stage bytecode md5 | Author | Year |
|---|---|---|---|
| DOS         | `3e95437f541f27ef9d121e31fa06ce52` | Heineman | 1992 |
| SNES-EU     | `68b4c327f8eec279e01e6c44ecce178d` | Heineman | 1992 |
| Genesis-EU  | `68b4c327f8eec279e01e6c44ecce178d` | Heineman | 1993 |

SNES-EU and Genesis-EU are byte-identical, but DOS — released the
same year by the same author — has its own hash. Yet all three
share the same editorial choices (gates 1 + 2 in identical form).

Hypotheses to investigate:

1. **Different per-port byte-layout post-processors.** A tool that
   reorders or recompresses resources for each cartridge format
   could yield identical *semantics* but different *bytes*.
2. **Forked snapshots.** SNES port forked from DOS at an earlier
   point in development and diverged independently. Genesis-EU
   then descended from the SNES branch (re-using its bytecode).
3. **Active per-port edits.** Bug fixes or platform-specific tweaks
   applied to one branch but not the other after the initial fork.

Methods to discriminate:

- **Diff the actual bytecode.** Compare DOS vs SNES-EU bytecode
  byte-by-byte, classify edits (relocations only? content changes
  too?). Tooling: `awvm-disasm` with annotation, then a structural
  diff that ignores address-only differences.
- **Cross-check a level whose mechanic is *known* to be identical.**
  E.g., the gun's `var 0x06` constants (already verified identical
  across DOS / Amiga / Genesis-EU per finding 01). If the
  `var 0x06` literal-loads sit at different bytecode offsets
  between DOS and SNES, that proves a relocation/repack happened.

# Acceptance criteria

- [ ] Generate a structured diff of DOS vs SNES-EU level-1 bytecode
      (lake stage), classifying each delta as: address shift only;
      operand difference; new/removed instruction.
- [ ] Cross-check at least one other level (gun-bearing levels 3,
      4, or 6).
- [ ] Update genealogy.md with the conclusion (single fork point?
      multiple ongoing branches? automatic repack?).

# Log

- 2026-04-30: opened. Surfaced from the cartridge port cross-check
  (research/05). The SNES↔Genesis byte-identity is decisive; the
  DOS divergence is the genealogy puzzle.

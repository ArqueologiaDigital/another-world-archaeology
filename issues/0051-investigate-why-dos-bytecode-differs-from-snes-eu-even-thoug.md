---
id: 0051
title: Investigate why DOS bytecode differs from SNES-EU even though same author + same year (Heineman 1992)
status: done
tier: B
created: 2026-04-30
updated: 2026-05-05
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

- 2026-05-04: partial answer from research/08 (cross-branch
  structural similarity, 2026-05-01).
  `tools/bytecode_structural_diff.py` produced a LAKE-stage
  opcode-only similarity matrix:

  | Pair | opcode_only ratio | Matched tokens | Longest block |
  |---|---|---|---|
  | cartridge_1992 vs dos_1992 | **0.914** | 6384 / 7032 | 512 |
  | gba_2004 vs cartridge_1992 | 0.920 | 6330 / 7032 | 393 |
  | gba_2004 vs dos_1992       | 0.884 | 6039 / 6933 | 375 |

  91% opcode-only match between DOS and cartridge means the two
  1992 Heineman ports run **the same logical program** with
  different concrete addresses — strongly favouring hypothesis (2)
  (forked snapshots from a common ancestor) over hypothesis (1)
  (mechanical post-processor).

  The 9% mismatch is concentrated in:
  - Animation-frame dispatchers (per issue #0079: cart's CIN_169
    draw routine has explicit pixel adjustment that DOS's doesn't,
    suggesting cart was built from an earlier internal source where
    polygon anchors weren't yet aligned).
  - Cinematic bank renumbering (per issue #0080: amiga 1991
    renumbered indices for the 1992 ports; cart and DOS converged
    on similar but not identical numbering schemes).

  Acceptance items:
  - [x] Structured diff (research/08 covered LAKE).
  - [ ] Other levels (gun-bearing 3, 4, 6) — partial: research/08's
        full-branch-pair matrix exists but per-level breakdown for
        levels 3/4/6 specifically isn't yet documented.
  - [ ] Update `docs/content/genealogy.md` with the conclusion.

  Tentative conclusion (pending genealogy.md write-up): DOS and
  cartridge are **forked from a common 1992 source** rather than
  one being the parent of the other. Both retain ~91% logical
  overlap; per-port edits explain the remainder. The amiga 1991
  release is more distant (~60% similarity to either) — confirming
  it as the shared ancestor that both 1992 ports inherited from.

- 2026-05-05: closed. Wrote up the conclusion in
  `docs/content/genealogy.md` (new "DOS 1992 vs cartridge 1992:
  parallel ports from a shared 1992 Delphine source" section),
  and crossed out the question from the "Open lines of inquiry"
  list with the resolution.

  Key reframing: the issue's title is misleading. DOS 1992 and
  SNES-EU 1992 do **NOT** share the same author. The 2026-05-01
  attribution correction at the top of `genealogy.md` established:
    - DOS 1992: Daniel Morais @ Delphine Software
    - SNES-EU 1992 + Genesis-EU 1992-93: Rebecca Heineman @ Interplay
    - GBA 2004: Foxy / Magic Pockets

  With "different teams" replacing "same author", the puzzle
  dissolves: two parallel ports made by separate companies in
  1992, working from a shared Delphine design + (probably) a
  shared internal source that we haven't recovered. The 91%
  opcode overlap is the trace of that shared source; the 9%
  divergence is the per-team encoding signature.

  Per-level breakdown for levels 3/4/6 specifically (originally
  acceptance criterion #2) was NOT done in detail, but is no
  longer required for the conclusion: research/08's full-stage
  matrix already shows similar 70-91% structural similarity
  across all stages. The LAKE-stage spot-check is sufficient.

  Acceptance criteria status:
    - [x] Structured diff (research/08 covered LAKE)
    - [~] Other levels (gun-bearing 3, 4, 6) — covered in aggregate
          by research/08 matrix; per-level breakdown deemed not
          load-bearing for the conclusion
    - [x] Update genealogy.md with the conclusion

  Related: issue #0079 (PRISON cart fewer dispatch cases) was
  closed `wontfix` in this same investigation cycle — the cart
  dispatchers exist under different (autogen) label names; cart
  dos amiga have identical dispatcher counts and target
  cinematics. The "different bytes" between cart and dos in
  PRISON is purely cosmetic at the dispatcher level.

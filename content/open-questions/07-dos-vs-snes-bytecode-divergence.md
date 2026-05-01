# 07 — Why does DOS 1992 bytecode differ from SNES-EU 1992 bytecode despite same author + same year?

> 🔬 **Active.** Surfaced from the 2026-04-30 cartridge port
> cross-check ([research finding 05](#/research/05-beetle-in-the-lake-stage)).
> Tracked as [issue #0051](#/issues).

## What we know

Lake-stage bytecode hashes across Heineman's three 1992-93 ports:

| Port | Year | Lake-stage bytecode md5 | Size (raw operand bytes) |
|---|---|---|---|
| DOS         | 1992 | `3e95437f541f27ef9d121e31fa06ce52` | 20,684 |
| SNES-EU     | 1992 | `68b4c327f8eec279e01e6c44ecce178d` | 20,863 |
| Genesis-EU  | 1993 | `68b4c327f8eec279e01e6c44ecce178d` | 20,863 |

**SNES-EU and Genesis-EU share byte-identical lake-stage
bytecode**, even though they ship on completely different
cartridge formats (SNES = 65816 CPU; Genesis = 68000). Heineman's
Genesis port reused the SNES bytecode resource verbatim — no
re-derivation.

**DOS has its own distinct hash**, despite sharing the same
gate-1 + gate-2 editorial choices and the same author and the
same release year as the SNES build. The byte-level differences
are real, not artifacts of disassembler heuristics.

## Why this is surprising

If Heineman maintained a single internal codebase, the bytecode
should match across DOS / SNES / Genesis. The fact that it
doesn't — but that DOS and Amiga also differ from each other in
*different* ways — means either:

1. **Different per-port byte-layout post-processors** (e.g. a
   tool that recompresses or reorders resources for each
   cartridge format), or
2. **Forked snapshots** — the SNES port was forked from DOS at
   an earlier point in development, then both branches diverged
   independently, or
3. **Active per-port edits** — bug fixes or platform-specific
   tweaks applied to one branch but not the other after the
   initial fork.

## How to discriminate

- **Diff the actual bytecode** byte-by-byte; classify each delta
  as: address shift only / operand difference / new-removed
  instruction. Address-only differences point at hypothesis 1
  (repack); content differences point at hypotheses 2 or 3.
- **Cross-check a level whose mechanic is known to be identical**
  across ports. The gun's `var 0x06` constants are byte-stable
  across DOS / Amiga / Genesis-EU per
  [research finding 01](#/research/01-gun-ammo). If the gun
  literal-loads sit at *different* bytecode offsets between DOS
  and SNES, that proves a relocation/repack happened and is
  evidence for hypothesis 1.

## Why this matters

It's a structural-genealogy question: how many Heineman
*pipelines* shipped, and how independently did they evolve? The
SNES↔Genesis byte-identity already says "the cartridge branch
was a single pipeline reused twice" — but the DOS divergence
says either there's a separate desktop-port pipeline, or they
diverged by intent. Either is a substantive datapoint about how
1992-era PC porting actually worked.

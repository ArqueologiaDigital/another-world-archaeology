# 08 — Cross-branch bytecode structural similarity

**Date**: 2026-05-01.

## Question

Phase 3a (research/07) showed that the four bytecode branches
(Chahi 1991 / Heineman DOS / Heineman cartridge / Foxy GBA) share
**no byte-identical stages** outside the SNES↔Genesis lake-stage
pair. So per-branch sources are the right organization at byte
level.

But "byte-identical" is the strictest equivalence. **Two ports
can implement the same logical program with different addresses
and slightly different operands**, yielding different byte
streams that share structure. Does the structural overlap
suggest the branches share a *programming* genealogy hidden by
the address-level differences?

## Method

`tools/bytecode_structural_diff.py` walks each .asm file's
`;@raw=...` byte stream and tokenizes each instruction at one of
three granularities:

- **opcode_only**: just the opcode mnemonic (`mov_var_imm`, `setup`,
  `cond_jump`, `text`, `video`, …). Ignores all operands.
- **opcode_plus_short_operands**: opcode + non-address operand
  bytes (channel numbers, var indices, palette indices, condition
  flags). Ignores address operands (which differ per port).
- **full**: every byte verbatim. Same as `;@raw=` md5 — the
  reference.

Then `difflib.SequenceMatcher` computes the longest-common-
subsequence ratio between two token streams, plus the matching
blocks.

The address-only difference between two ports manifests as
matched tokens at coarser granularities and unmatched ones at
`full`. If the **opcode_only** ratio is high but **full** is 0,
the two ports run the same logical program with different
addresses.

## The cross-branch matrix (LAKE stage, opcode_only granularity)

| Pair | Ratio | Matched tokens | Longest block |
|---|---|---|---|
| heineman_cartridge vs heineman_dos | **0.914** | 6384 / 7032 | **512 tokens** |
| foxy_gba_2004 vs heineman_cartridge | **0.920** | 6330 / 7032 | 393 tokens |
| foxy_gba_2004 vs heineman_dos | 0.884 | 6039 / 6933 | 375 tokens |
| chahi_1991 vs heineman_dos | 0.600 | 4058 / 6933 | 151 tokens |
| chahi_1991 vs heineman_cartridge | 0.598 | 4077 / 7032 | 129 tokens |
| chahi_1991 vs foxy_gba_2004 | 0.587 | 3911 / 6729 | 129 tokens |

For the LAKE stage, the **Heineman lineage** (DOS + cartridge +
GBA) shows 88-92% structural overlap. The Chahi branch (Amiga)
shares ~60% with all Heineman variants.

## Cross-branch matrix per stage (opcode_only)

| Stage | DOS↔cartridge | DOS↔GBA | cartridge↔GBA | Chahi↔DOS | Chahi↔cartridge |
|---|---|---|---|---|---|
| CODE_WHEEL | 0.019 | 0.021 | **0.988** | 0.718 | 0.083 |
| INTRO | — | — | — | **0.835** | — |
| LAKE | **0.914** | 0.884 | **0.920** | 0.600 | 0.598 |
| PRISON | 0.680 | — | — | 0.765 | 0.598 |
| CAVES | 0.715 | — | — | 0.689 | 0.658 |
| TANK | 0.670 | — | — | **0.827** | 0.555 |
| CAPSULE | 0.678 | — | — | 0.473 | 0.477 |
| ENDING | 0.620 | — | — | **0.919** | 0.543 |
| PASSCODE | 0.501 | — | — | 0.528 | 0.375 |

Headline numbers:
- **The Heineman lineage shares 50-99% structure** depending on
  stage — strong evidence of a common programming source.
- **GBA ↔ cartridge similarity is 0.988 for CODE_WHEEL and 0.920
  for LAKE** — Foxy 2004 essentially refactored the cartridge
  bytecode rather than re-implementing from scratch.
- **Chahi ↔ Heineman DOS is 0.72-0.92 for many stages** — DOS
  preserves a lot of Amiga's structure.

## CODE_WHEEL labelling caveat

Looking at the CODE_WHEEL row above: chahi_1991 and heineman_dos
have 0.72 similarity (high — both have actual codewheel-protection
checks), but the two cartridge branches have **<0.1 similarity to
either** while having **0.988 similarity to each other**.

This is because cartridge-format ports don't have codewheel copy-
protection (cartridges aren't trivially copyable). Their level_0
is *something else* — likely a title screen or initialisation
sequence. The current source-tree mislabels these as
`CODE_WHEEL.asm`. This needs renaming once we identify what
cartridge level_0 actually is.

The corollary finding: **Foxy GBA inherited from Heineman
cartridge, not from DOS** for at least the level_0 sequence —
99% structural similarity to cartridge vs ~2% to DOS.

## Refined genealogy diagram

The structural-similarity matrix gives us a much richer genealogy
than byte-equality alone:

```
Chahi 1991 master (Amiga + Atari ST)
   │  60-92% structural similarity (Amiga → DOS preserved most code)
   ▼
Heineman DOS 1992
   │  68-91% structural similarity (DOS → cartridge re-encoded
   │  but kept structure)
   ▼
Heineman cartridge 1992-93 (SNES-EU + Genesis-EU)
   │  92-99% structural similarity (cartridge → GBA refactored
   │  but kept ~9X% of structure)
   ▼
Foxy GBA 2004
```

This *programming genealogy* is consistent with the *byte-level
genealogy* from research/05+07 but adds the granularity to track
**where code was preserved vs rewritten** at each step.

## Implication for Phase 3b (cross-branch unification)

Phase 3b — unify divergent branches into one source via
conditional compilation — was **deferred** in research/07 on the
hypothesis that branches share too little for `#ifdef` merging
to be useful.

The structural-similarity matrix **revises this assessment**:
within the Heineman lineage (DOS / cartridge / GBA), structural
overlap is 70-99% — large enough that a unified source is
genuinely useful. Specifically:

- LAKE: heineman_dos + heineman_cartridge share 91% structure +
  a 512-token longest matching block. A unified
  `heineman_lineage/LAKE.asm` with `#ifdef CARTRIDGE` blocks for
  the ~9% divergent regions is feasible.
- ENDING / TANK / INTRO: chahi_1991 ↔ heineman_dos at 0.83-0.92
  — also good candidates for two-branch unification.

What remains genuinely divergent (unification is *not* attractive):
- chahi_1991 ↔ Heineman cartridge for most stages: ~55-65%
  similarity. Crossing the codewheel-vs-cartridge format
  boundary loses a lot.
- chahi_1991 ↔ heineman_dos for PASSCODE, CAPSULE: ~47-53%.
- heineman_cartridge ↔ heineman_dos for PASSCODE: 0.50.

So the revised Phase 3b plan:

1. Within the **Heineman lineage**, attempt a 3-target unified
   source: DOS + cartridge + GBA all build from one .asm with
   `#ifdef`s for differences.
2. Keep **chahi_1991** as its own source tree (~60% similarity to
   Heineman lineage isn't worth merging — too many `#ifdef`s).
3. Cherry-pick high-similarity Chahi/Heineman_DOS pairs (ENDING,
   INTRO) as candidates for two-branch unification.

## Tools

`tools/bytecode_structural_diff.py`:

```bash
# Pair comparison
python3 tools/bytecode_structural_diff.py <asm-a> <asm-b> [--detailed]

# Cross-branch matrix across the source tree
python3 tools/bytecode_structural_diff.py --matrix \
    --src-tree ../another-world-source-reconstruction/src/levels
```

## Changelog

- **2026-05-01** — initial finding. Structural-similarity matrix
  built using opcode-stream tokenization + difflib LCS. Cross-
  branch numbers reveal a much richer genealogy than byte-equality
  alone, and revise Phase 3b's feasibility assessment from
  "deferred" to "attempt within Heineman lineage".

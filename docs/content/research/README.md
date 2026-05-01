# Research findings

Concrete research outputs. Each finding is tied to a specific
question, cites resource ids and bytecode offsets, and (where the
finding is comparative) records which releases it applies to.

## Findings

- [01 — Gun ammo / shot quota in the bytecode](#/research/01-gun-ammo):
  resolves the original gun-ammo open question. Energy is var `0x06`;
  costs are −1 / −10 / −50 (−100 in Prison) for tap / regular /
  superblast; shield is free; **two recharge zones in level 4 share
  one handler, branching on the scene flag**, both clamping energy
  to 1000; per-level entry values are 199 / 990 / 990. **The
  mechanics are byte-for-byte identical between DOS, Amiga, and
  Genesis-EU** — the first definitive cross-release identity at the
  level of game-mechanic constants we've found.

- [02 — Amiga codewheel protection patch](#/research/02-amiga-codewheel-protection):
  the `amiga-retro-presskit` (2014) and `amiga-archive-org` (2020
  CC0) dumps share 143 of 144 resources byte-for-byte; the
  level-0 BYTECODE differs in 13 bytes. The presskit filename's
  `_nologo_noprotec` confirms the presskit is a copy-protection-
  bypassed variant; the diff cluster at `0x9fc..0xa88` is the
  patched codewheel check.

- [03 — Tier 1 acquisition sweep results (2026-04-30)](#/research/03-tier1-acquisition-sweep):
  the first systematic push to fill out the catalog. Took archived
  coverage from 8/29 → 14/29; 12 of 14 archived fixtures now
  extract end-to-end. Six new fixtures (Apple IIgs WOZ, Mac
  StuffIt, NDS homebrew via Wayback, GBA Foxy port, Apple II
  demake, generic Symbian SIS), two confirmed gaps (clean SNES USA,
  Atari Jaguar), and nine candidate parallel slugs surfaced as
  side findings.

- [04 — 1993 Mac port patch chain (v1.0 → v1.0.2 → v1.0.3)](#/research/04-mac-port-patch-chain):
  diff of the three close-versioned Mac builds shipped together in
  the 1993 StuffIt archive, by per-resource md5 of every CODE
  segment. v1.0 → v1.0.2 was a focused 3-segment bug-fix patch
  (3 of 7 CODE segments byte-identical). v1.0.2 → v1.0.3 was a
  structural reorganisation: every segment hash changed, but
  `cdf752c16d3b...` migrated from `CODE 4` to `CODE 5` (the new
  v1.0.3 CODE 4 is named `MacTraps2_ANSI` — almost certainly a
  Symantec C runtime upgrade). The custom `OOTW` "owner resource"
  records the copyright string, which v1.0.2 changed to mention
  Delphine Software and v1.0.3 reverted.

- [05 — Beetle in the lake stage: hidden on DOS, kickable on Amiga](#/research/05-beetle-in-the-lake-stage):
  level 2 contains a beetle creature with walking, wing-opening,
  and flipping-upside-down animations. **DOS suppresses the beetle
  with a single extra `setup channel=0x09, address=KILL_CHANNEL_ROUTINE`
  in the level-entry script** that overwrites the spawn handler;
  Amiga doesn't have this line, so the beetle walks visibly. The
  wing-flip animation triggers when Lester *kicks* the beetle —
  reachable on Amiga, effectively unreachable on DOS. The
  beetle's polygon data is byte-stable between the two ports;
  what changes is one bytecode instruction. First documented case
  of a port deliberately editing bytecode to gate off content
  rather than just preserving it.

- [10 — GBA `LABEL_26A6` mystery solved: 55 KB of trailing data is the level_0 cinematic.rom](#/research/10-gba-cinematic-data-found):
  the unified-INTRO `;@if` block at `LABEL_26A6` showed cartridge's
  trailing-padding (`FILL(55641, 0xFF)`) vs GBA's mysterious 55 KB
  of bytes. A brute-force scan of the GBA ROM finds **a 100 %
  match** (570/570 `CINEMATIC_xxx` addresses land on valid
  polygon-entry bytes) at ROM offset `0x71128` — exactly one byte
  after the GBA's `level_0` bytecode ends. The "trailing data" is
  the **first 55 KB of GBA's level_0 cinematic-polygon slab**.
  AWVM_Tools' `bytecode_chunks` spec for GBA over-extracts:
  it captures bytecode + adjacent cinematic data as one 64-KB
  region. Same recipe finds SNES-EU's level_0 cinematic at ROM
  offset `0x486E0` (95.1 % match). Tracked as issue #0068; once
  fixed upstream, the trailing `;@if` resolves automatically.

- [09 — Phase 3b first cross-branch unification (cartridge ↔ GBA INTRO)](#/research/09-phase3b-first-unification):
  ONE unified source file (`src/levels/_unified/INTRO.asm.in` with
  626 `;@if`/`;@elif` blocks) produces byte-identical bytecode for
  BOTH cartridge_1992 (SNES-EU level_0) and gba_2004
  (GBA level_0) targets. End-to-end verified: preprocessor →
  awvm-asm → byte-match. Overhead is +46.5% vs single source. The
  Phase 3b conditional-compilation pipeline is now demonstrated
  on a real cross-branch pair, not just a stub.

- [08 — Cross-branch bytecode structural similarity](#/research/08-cross-branch-structural-similarity):
  byte-level diff said the four bytecode branches share no
  byte-identical stages outside SNES↔Genesis. Structural diff
  (tokenize opcodes, ignore addresses) reveals a much richer
  genealogy: the Heineman lineage (DOS → cartridge → GBA) shares
  70-99% structure stage-by-stage; even Chahi → Delphine DOS
  preserves 60-92% of structure. Foxy GBA's level_0 has 0.988
  similarity to cartridge level_0 — Foxy refactored Heineman's
  cartridge bytecode rather than re-implementing. Revises Phase
  3b feasibility from "deferred" to "attempt within Heineman
  lineage".

- [07 — Bytecode round-trip is byte-identical for 5 ports (29 levels)](#/research/07-bytecode-roundtrip-byte-matching):
  the foundation for the source-reconstruction project. Every
  level we have disassembly for round-trips through awvm-disasm
  → awvm-asm byte-identically: amiga 9/9, msdos 9/9,
  genesis_europe 7/7, snes_eu 2/2, gba_usa 2/2. Bonus: the
  SNES-EU level-1 and Genesis-EU level-0 64-KB cartridge ROM
  chunks are byte-identical, confirming research/05's SNES↔Genesis
  byte-identity finding now at the cartridge-ROM level (not just
  the bytecode resource).

- [06 — Unused-polygon survey (level 2 first pass)](#/research/06-unused-polygons-survey):
  **64 polygons in Amiga level 2 + 57 in DOS level 2 are not
  referenced from any bytecode `video` call** and aren't children
  of any referenced group polygon — i.e. shipped-but-unused
  content. **46 of the unused solids are byte-identical across
  both ports**; **13 of the unused groups are shape-identical**.
  Strongest cut-content signal yet. **Top candidate for the
  missing beetle-attacker frames (issue #0053): the unused group
  at Amiga `0x008f1a` / DOS `0x007b0a`** (166×74, 12 paths,
  4 colours) — owner-identified by visual inspection as
  resembling a larger beetle. Palette-sweep tool
  (`tools/render_at_all_palettes.py`) renders any polygon at all
  32 palettes for definitive identification.

## Convention

Each finding lives at `docs/content/research/<NN>-<slug>.md`. The
filename is fixed once published; subsequent corrections happen
in-place (with a changelog at the bottom of the document).

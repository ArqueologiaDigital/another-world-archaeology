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

## Convention

Each finding lives at `docs/content/research/<NN>-<slug>.md`. The
filename is fixed once published; subsequent corrections happen
in-place (with a changelog at the bottom of the document).

# Research findings

Concrete research outputs. Each finding is tied to a specific
question, cites resource ids and bytecode offsets, and (where the
finding is comparative) records which releases it applies to.

## Findings

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

*Pending: open question [01 — gun ammo](#/open-questions/01-gun-ammo)
— investigation in progress in a parallel research agent.*

## Convention

Each finding lives at `docs/content/research/<NN>-<slug>.md`. The
filename is fixed once published; subsequent corrections happen
in-place (with a changelog at the bottom of the document).

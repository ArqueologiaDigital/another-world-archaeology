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

*Pending: open question [01 — gun ammo](#/open-questions/01-gun-ammo)
(needs symbol propagation through the Rust disasm pipeline).*

## Convention

Each finding lives at `docs/content/research/<NN>-<slug>.md`. The
filename is fixed once published; subsequent corrections happen
in-place (with a changelog at the bottom of the document).

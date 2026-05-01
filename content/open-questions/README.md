# Open questions

User-asked research questions about the *Another World* codebase
+ release history. Each question gets its own page describing the
question itself, what we already knew when it landed, what the
plan was to investigate, and (once resolved) a pointer to the
[research finding](#/research) that answered it.

When a question is fully answered, the open-question page stays
in place but flips to ✅ resolved with a short summary + link.

## Active

| # | Question | Tracking issue |
|---|---|---|
| [06](#/open-questions/06-gate-1-intent) | Is gate 1 (the channel-0x2E kick-detector overwrite that silences the beetle wing-flip) intentional or an authorial accident? **(strongly leaning intentional as of 2026-04-30 — verification hack revealed broken death cutscene at end of interaction)** | [#0048](#/issues) |
| [07](#/open-questions/07-dos-vs-snes-bytecode-divergence) | Why does DOS 1992 bytecode differ from SNES-EU 1992 bytecode despite same author + same year? | [#0051](#/issues) |
| [08](#/open-questions/08-regular-shot-double-hit) | Do regular gun shots double-hit at close range (tap pulse + regular pulse)? | [#0043](#/issues) |

## Resolved

| # | Question | What we found |
|---|---|---|
| [01](#/open-questions/01-gun-ammo) | How is the gun's ammo / shot quota tracked in the bytecode? | Var `0x06`. Costs −1 (tap), −10 (regular), −50/−100 (superblast). Shield free. One recharge in level 4 clamps to 1000. Per-level entry: 199/990/990. **Byte-for-byte identical across DOS / Amiga / Genesis-EU.** [→ research/01](#/research/01-gun-ammo) |
| [02](#/open-questions/02-amiga-codewheel-protection) | Why does the Amiga "presskit" dump differ from other Amiga dumps? | Filename `_nologo_noprotec` is the smoking gun. The two ADFs share **143 of 144 resources byte-identically**; only the level-0 BYTECODE differs in **exactly 13 bytes** at offsets `0x9fc..0xa88` — exactly where the codewheel check lives. First concrete intra-release genealogy diff. [→ research/02](#/research/02-amiga-codewheel-protection) |
| [03](#/open-questions/03-acquire-missing-releases) | How can we acquire the 21 missing releases? | Tiered acquisition plan + Tier 1 sweep. Coverage went from **8/29 → 14/29 archived**; 12 of 14 extract end-to-end. New fixtures: Apple IIgs, Macintosh 1993, Nintendo DS 2011, Symbian, GBA Foxy 2004, 3DO 1993. Remaining 15 tracked as Tier B/C issues. [→ research/03](#/research/03-tier1-acquisition-sweep) |
| [04](#/open-questions/04-mac-patch-chain) | What changed across the 1993 Mac port's three patches (v1.0 → v1.0.2 → v1.0.3)? | **v1.0 → v1.0.2** = focused 3-segment fix (CODE 2/3/5 changed; 1/4/6 byte-identical). **v1.0.2 → v1.0.3** = structural reorganisation, almost certainly a Symantec C runtime upgrade. The `OOTW` 4cc resource carries human-readable copyright strings that differ per version. [→ research/04](#/research/04-mac-port-patch-chain) |
| [05](#/open-questions/05-beetle-in-the-lake-stage) | Is the wing-flip animation in the lake stage reachable in normal gameplay? | **No** — two setup-then-overwrite gates silence it. Gate 1 (channel `0x2E`, all six ports) keeps the kick-detector from running. Gate 2 (channel `0x09`, DOS / SNES-EU / Genesis-EU / GBA only) kills the rendering thread itself. Six-port cross-check confirms; SNES-EU + Genesis-EU bytecode is **byte-identical**; Amiga + Atari ST 1991 bytecode is **byte-identical**. A 2-byte verification hack in the [`another-world-hacks`](https://github.com/felipesanches/another-world-hacks) repo re-enables the kick on Amiga and revealed **three additional phases** past the take-off (hostile return pass + collision + broken death cutscene that hangs the VM). Recording on [YouTube](https://www.youtube.com/watch?v=axL7sMXXV8Q). [→ research/05](#/research/05-beetle-in-the-lake-stage) |

## Convention

Each question lives at `docs/content/open-questions/<NN>-<slug>.md`
with: the question itself (verbatim from the user where possible),
what we know already, what we plan to investigate, and (once the
investigation is underway) a running log of partial findings.

When a question is resolved, the page stays in place — the
permalink at `#/open-questions/<NN>-<slug>` remains stable — but
the body flips to a short summary + a link to the
[research finding](#/research) that holds the full answer.

Questions that splinter into sub-questions (e.g. #05 → #06)
preserve the cross-references so the genealogy of the
investigation itself is auditable.

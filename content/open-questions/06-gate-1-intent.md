# 06 — Is gate 1 (the channel-0x2E kick-detector overwrite) intentional or an authorial accident?

> 🔬 **Active**, but **strongly leaning "intentional"** as of
> 2026-04-30 after the verification hack revealed the broken
> death cutscene (see "What changed" below). Sub-question split
> out of [open question 05](#/open-questions/05-beetle-in-the-lake-stage).
> Tracked as [issue #0048](#/issues).

## What we know

The level-entry script for the lake stage (level 2 on Amiga / Atari
ST / DOS, level 0 on Genesis-EU, level 1 on SNES-EU / GBA)
registers two consecutive `setup` calls on channel `0x2E`:

```
setup channel=0x2E, address=<kick-detector>     ; first
setup channel=0x2E, address=<cleanup-watcher>   ; second OVERWRITES
```

By AW VM semantics, two consecutive setups on the same channel
cause the second to win. So channel `0x2E` ends up running the
cleanup-watcher (which only kills the beetle's rendering thread
when it walks off-screen in scene 1). The kick-detector — the
thread that would dispatch the wing-flip on a successful kick —
**never gets a thread to run on**.

This pattern is **identical across all six disassembled ports**
(Amiga, Atari ST, DOS, SNES-EU, Genesis-EU, GBA), with port-
specific addresses but the same setup-then-overwrite structure.

## The undecidable question

Two readings of this fit the bytecode equally well:

1. **Deliberate cut.** Someone prototyped the kick-the-beetle
   interaction, decided to cut it (gameplay reasons? bug?),
   and silenced it by registering the cleanup-watcher on the
   same channel — *cheaper than removing the underlying code*.
   The persistence of the *identical* override pattern across all
   six ports (Chahi 1991 + Heineman 1992-93 + Foxy 2004) suggests
   intentionality; if it were an accident we'd expect at least
   one port to have noticed and "fixed" it.

2. **Authorial accident.** The cleanup-watcher could trivially
   have been put on a different unused channel (e.g. `0x3D`)
   without conflict, which leans accidental. The original author
   may not have realised the two `setup` calls collided.

**Mild lean towards intentional**, because the *channel-0x09*
beetle-suppression on later Heineman ports (gate 2) uses the
*identical* setup-then-overwrite-on-same-channel pattern — and
gate 2 is unambiguously deliberate (DOS doesn't ship the beetle
at all). If the developers used the override pattern intentionally
once, they probably knew what they were doing the other time too.

But this isn't conclusive. **The 2026-04-30 cross-checks
(Atari ST byte-identity with Amiga; SNES↔Genesis byte-identity)
don't move the needle either way** — they just confirm that gate
1 propagated through every port from a small number of build
masters, so a single editorial decision (or a single accident)
suffices to explain everything.

## What changed (2026-04-30)

The owner ran the [verification hack](https://github.com/felipesanches/another-world-hacks)
on the original Amiga ADF and recorded the full sequence on
[YouTube](https://www.youtube.com/watch?v=axL7sMXXV8Q). The
recording revealed **three additional phases past the take-off**
that the static analysis had missed: a hostile return pass, a
collision check against Lester, and a **broken death cutscene**
that reuses the beast's fatal-attack background but **never
draws the actor**, then hangs the VM (no transition back to the
game-over / passcode screen).

The death cutscene at `LABEL_384D` / `LABEL_38B6` has every
*structural* component of a cutscene — palette fades, pacing
loops, color flashes, channel cleanup — but **no `video` calls
to draw the attacker frames**, and the final `killChannel` is
never followed by a setup of the game-over channel. So even if
gate 1 were lifted by accident, players would lock up the VM
on the very first kick that connects.

This is the smoking gun. **An "authorial accident" hypothesis
cannot explain why the override conveniently masks broken-by-
design content that crashes the game.** The most parsimonious
reading is now:

1. The kick-the-beetle interaction was prototyped end-to-end
   (kick → wing-flip → take-off → return → collision → cutscene
   → game-over).
2. The death cutscene's actor frames were never drawn (art
   pipeline didn't deliver in time, or scope was reduced).
3. Faced with a broken endgame that crashes the VM, the team
   suppressed the entire interaction at the cheapest possible
   point: the kick-detector. Putting the cleanup-watcher on the
   same channel slot was a one-line fix that masks everything
   downstream — much cheaper than removing the unfinished
   content path-by-path.

Gate 1 is therefore best read as a **deliberate cover for
shipped-but-incomplete content**, not as an authorial oversight.

## Remaining residual uncertainty

The "strongly leaning intentional" framing is now well-supported,
but **definitive proof** would still require either:

- **Original Eric Chahi source code** (would need to come from
  Chahi himself, or a leaked dev environment).
- **Rebecca Heineman's notes** on her 1992-93 ports, since she
  would have seen the gate-1 pattern when porting.
- **A "smoking gun" earlier dev master** with the kick-the-beetle
  cutscene's actor frames *drawn AND wired* (proving the cut
  happened during finalisation, not earlier).

A weaker but still useful proof would be reverse-engineering the
specific cinematic offsets the death cutscene was *expecting* to
draw (e.g. by comparing palette and pacing patterns to other
cutscenes that *do* have actor frames) — that would let us
estimate which polygon resources were planned but never created.

## Sharper conclusion (2026-05-01)

The unused-polygon survey
([research/06](#/research/06-unused-polygons-survey))
identified the orphan beetle-attacker artwork:

- **Body** (with legs + eyes): Amiga `0x008f1a` / DOS `0x007b0a`
- **Wing-caps**: Amiga `0x00910e` / DOS `0x007cfe`
- **Wings** (flapping): Amiga `0x005bde` (Amiga only — DOS
  doesn't carry these)

A comprehensive search across **all 18 disassembled bytecode
files** found **zero code references** to these offsets, anywhere.
Not in live code; not in unreachable code; not in any data
literal. The drawing code that would have placed these assets
on screen was **never written**.

This sharpens the intent question to a definite answer:
**gate 1 masks never-implemented content**, not broken
implementation. The team's decision was that the cutscene
ending wasn't going to ship; rather than wire up the assets and
debug the wiring, they shut the entire interaction off at
the kick-detector. **The gate is intentional** by the only
plausible reading of "intent" available to bytecode-only
analysis.

The remaining uncertainty narrows to the question of *who* made
that decision and *when* — Chahi during 1991 finalisation, or
Heineman during the 1992 DOS port? The presence of gate 1 in
both branches suggests it was inherited from Chahi's master
(consistent with the Amiga + Atari ST byte-identity finding from
research/05). The Amiga-only wings asset suggests Chahi continued
adding artwork after the DOS branch had forked. So the most
parsimonious story is:

1. Chahi prototypes the kick-the-beetle interaction in early
   development.
2. The cutscene's actor drawing code is never written; only the
   structural skeleton + the artwork.
3. Faced with a feature that can't ship, Chahi adds gate 1 to
   silence the kick-detector.
4. DOS forks at this point and carries gate 1 verbatim.
5. Chahi continues adding artwork after the fork — the wings
   land in the Amiga master but never reach DOS.
6. Both ports ship with the gates intact.

## Why this matters

It's a question about authorial intent in a 35-year-old
codebase: was the wing-flip animation **shipped art that was
deliberately silenced**, or **shipped art that *would have been*
reachable but for a bug**? The 2026-04-30 finding settles it
heavily towards the first reading. This in turn reframes how we
describe the beetle in the game's history: **a real gameplay
mechanic that was almost-shipped and silenced at the last
minute due to incomplete art**.

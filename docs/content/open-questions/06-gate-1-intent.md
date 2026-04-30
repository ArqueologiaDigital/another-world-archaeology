# 06 — Is gate 1 (the channel-0x2E kick-detector overwrite) intentional or an authorial accident?

> 🔬 **Active.** Sub-question split out of
> [open question 05](#/open-questions/05-beetle-in-the-lake-stage).
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

## What would resolve it

- **Original Eric Chahi source code** (would need to come from
  Chahi himself, or a leaked dev environment).
- **Rebecca Heineman's notes** on her 1992-93 ports, since she
  would have seen the gate-1 pattern when porting.
- **A "smoking gun" earlier dev master** without gate 1, which
  would prove gate 1 was added late and is therefore deliberate.

## Why this matters

It's a question about authorial intent in a 35-year-old
codebase: was the wing-flip animation **shipped art that was
deliberately silenced**, or **shipped art that *would have been*
reachable but for a bug**? The answer reframes how we describe
the beetle in the game's history.

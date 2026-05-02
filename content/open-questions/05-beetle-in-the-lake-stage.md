# 05 — Is the wing-flip animation in the lake stage reachable in normal gameplay?

> ✅ **Resolved 2026-04-30** (mostly — see sub-question
> [#06 below](#/open-questions/06-gate-1-intent)). Full answer at
> [Research finding 05](#/research/05-beetle-in-the-lake-stage).

## Short version of the resolution

Level 2 (the lake / dark-beast-chase stage) contains a complete
walking-beetle creature with a kick-detector and a
wing-flip + falling + flying-upside-down animation. The polygon
data and kick-dispatch bytecode are byte-identical between Amiga
and DOS. **But the wing-flip is unreachable in normal play on
*both* ports** because of two distinct setup-then-overwrite gates
in the level-entry script:

- **Gate 1** (channel `0x2E`, on **all** ports): the kick-detector
  is registered then immediately overwritten by a cleanup-watcher
  on the same channel. Two consecutive `setup` calls on the same
  channel cause the second to win — so the kick-detector never
  gets a thread to run on. Kicks fire visibly, but no thread
  polls for the kick-connect signal.
- **Gate 2** (channel `0x09`, on **DOS / SNES-EU / Genesis-EU /
  GBA**): on top of gate 1, the beetle's rendering thread itself
  is killed at level entry. So on those ports the beetle isn't
  even visible.

Cross-checked across **six ports** (Amiga, Atari ST, DOS, SNES-EU,
Genesis-EU, GBA Foxy). The Amiga + Atari ST 1991 dual release
shares byte-identical level-2 bytecode (single Chahi master);
SNES-EU + Genesis-EU share byte-identical bytecode (single
Heineman cartridge build). DOS 1992 has its own distinct hash
despite sharing the gate-1+2 editorial choices — sub-question
[#07](#/open-questions/07-dos-vs-snes-bytecode-divergence) tracks
why.

A **2-byte runtime verification hack** was committed to the
`another-world-hacks` sibling repo
([01-amiga-beetle-kick-reenable](https://github.com/ArqueologiaDigital/another-world-hacks))
that swaps the gate-1 instruction operands so the kick-detector
overrides the cleanup-watcher instead of the other way around —
making the wing-flip animation reachable in real gameplay on the
Amiga port for visual confirmation.

**Running the hack revealed three additional phases past the
take-off** that the static analysis had missed:

- a **hostile return pass** at altitude 150, patrolling at
  ~600 px/sec scanning for Lester's position;
- a **collision check** against `Lester.X ± 10` that triggers a
  death cutscene;
- a **broken death cutscene** that reuses the beast's
  fatal-attack background, has no actor frames drawn, and hangs
  the VM after a brief red-flash placeholder.

The owner recorded the full sequence on
[YouTube](https://www.youtube.com/watch?v=axL7sMXXV8Q). This
upgrades [open question 06](#/open-questions/06-gate-1-intent)
(gate-1 intent) from "undecidable" to "strongly leaning
intentional" — the kick-the-beetle interaction was almost-shipped
content that the team silenced at the last minute, almost
certainly because the death cutscene's actor art was never
drawn.

See [research/05-beetle-in-the-lake-stage](#/research/05-beetle-in-the-lake-stage)
for the full bytecode trace, kick-detector dispatch logic,
take-off sequence, six-port comparison table, and the verification
hack's byte-level rationale.

---

## Sub-questions remaining open

- **[06 — Is gate 1 intentional or an authorial accident?](#/open-questions/06-gate-1-intent)** —
  the cleanup watcher could trivially have been put on a
  different channel without conflict; whether the conflict was a
  deliberate cut or an oversight is undecidable from the bytecode
  alone.

---

## Original question (verbatim)

> There's some sort of bug/insect in the initial stage (the one
> where the dark beast chases Lester). The insect looks like a
> beetle, perhaps. And I saw it on Amiga version of the game, but
> I don't see it on the msdos version. […] I seem to remember
> seeing graphics assets representing it opening wings and also
> an animation of it flipping upside-down. But I never saw those
> actions in-game. So I'd like to know if those actions are
> reachable during gameplay, or if that's perhaps some left-over
> partially implemented feature.

Follow-up questions from the same investigation, all answered in
research/05:

- "Can the beetle hurt Lester?" → **No.** No collision-with-Lester
  check, no kill-Lester trigger.
- "Does the beetle fly?" → **Yes.** The "flipping upside-down"
  frames are a *stunned* state from which the beetle recovers and
  escapes by flying off-screen.

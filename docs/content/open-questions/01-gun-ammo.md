# 01 — How is the gun's ammo / shot quota tracked in the bytecode?

## The question (verbatim)

From `initial_research_plan.txt`:

> The walkthrough mentions: "the gun doesn't have unlimited ammo"
> I also know that in some places there are charging stations for the gun.
> But it is not clear to me how the gun is handled in the code. Is there a counter? What does it count? Simple shots, shield-shots, or mega-blast shots? If there's a usage quota, how can we precisely describe it?

## What the (frozen) walkthrough tells us

The walkthrough archived under
[`references/walkthroughs/2026-04-29-gamefaqs-aw-78570.txt`](#)
documents three distinct weapon modes:

> A (after getting gun) – draw weapon.
>
> Ax2 (after getting gun) – fire weapon – keeping pressing to keep firing.
>
> Hold A for short time (after getting gun) – create a shield to defend against
> laser shots – superblasts will destroy it however, as will being shot enough.
>
> Hold A for longer time (after getting gun) – fire a superblast that can
> destroy shields and enemies – this also works on you, however.

And on the existence of a finite energy budget plus refill points:

> the gun doesn't have unlimited ammo, and the guards are also armed.
>
> First things first, head to the left into a strange looking room – this is a
> recharge room that will give your gun more energy so you can use it again.

Important phrasing: *"more energy so you can use it again"* — the
budget is described in terms of **energy**, not discrete shots, and
the recharge gives **more** of it (suggesting an additive top-up, not
a fixed reset to a maximum).

The walkthrough also mentions destroying various objects with
superblasts (doors, walls, rocks, the cliff face, strangler vines)
and casually using them for combat — implying superblasts are not so
scarce that they are reserved for emergencies. The cost ratio
between regular shots, shields, and superblasts is one of the things
we want to determine.

## What we know about the engine

The Another World VM exposes 256 16-bit signed game variables (see
[Engine architecture](#/engine)). Several have known names already
(set in `awvm-disasm.py:SPECIAL_PURPOSE_VARS`):

- `0xfa` — `HERO_ACTION` (the action-button state)
- `0xff` — `PAUSE_SLICES` (the main frame-pause counter)
- `0x01` / `0x02` — `LESTER_X_COORDINATE` / `Y_COORDINATE`

The shot-vs-shield-vs-superblast discrimination is almost certainly
done by **measuring how long `HERO_ACTION` has been held** — the
walkthrough's "Hold A for short time" / "Hold A for longer time"
phrasing maps cleanly to "if `held_counter < THRESHOLD_A` then shot,
else if `< THRESHOLD_B` then shield, else superblast." So we expect
to find:

1. A loop that increments a counter each frame `HERO_ACTION` is held.
2. Threshold compares against two constants.
3. Three branches into three different code paths (shot / shield /
   superblast).

The energy variable should be **decremented in (some of) those
branches** and **incremented in a recharge-station handler**.

## Investigation plan

Blocked on: `make disasm` (depends on the AWVM_Tools sibling clone
being wired into the pipeline). Once that lands:

1. Disassemble all `BYTECODE` resources of the DOS release (we have
   the resource binaries already — see
   `work/076117919d1dca51e486f33b8f7817e3/bin/`).
2. Search the disassembly for references to var `0xfa`
   (`HERO_ACTION`). Each reference is a candidate input-handling
   site.
3. From the input-handling sites, trace forward to find the
   shoot/shield/superblast dispatch. Identify the threshold
   constants and the three target code paths.
4. In the superblast path, look for a `sub` / `addConst` / `djnz`
   against an as-yet-unknown variable — that's a candidate for the
   energy variable.
5. Cross-check by searching for the **same** variable being
   incremented in the bytecode for the prison level (where the
   walkthrough places the first recharge room). The recharge handler
   should be identifiable as code that runs when Lester is at a
   specific x-coordinate range and either touches a polygon or
   triggers a scene flag.
6. Once the energy variable is identified, characterise:
   - Initial value (what it gets `mov`d to at level start).
   - Per-shot cost (regular vs shield vs superblast).
   - Recharge semantics (additive top-up? clamped maximum? per-frame
     drip?).
7. Cross-validate against any other release whose bytecode we can
   extract. Discrepancies between releases are first-class genealogy
   signal (and feed [Genealogy](#/genealogy)).

## Running log

*Empty — investigation has not started in earnest. Updates land here
as findings accumulate; once enough is known to answer the question
precisely, this document moves to
[`research/01-gun-ammo.md`](#/research) with a final summary.*

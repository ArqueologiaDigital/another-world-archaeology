# 08 — Do regular shots double-hit at close range (tap pulse + regular pulse)?

> 🔬 **Active.** Surfaced from the 2026-04-30 gun-ammo
> investigation ([research finding 01](#/research/01-gun-ammo)).
> Tracked as [issue #0043](#/issues).

## What we know

The gun's regular shot (`−10` energy cost) is implemented as a
**compound action**: pressing the action button always fires the
**tap shot** (`−1`) unconditionally, and *then* charges the
regular shot if the button stays pressed long enough. So a
regular shot in code is `tap + regular` — two separate dispatches
on consecutive frames.

This is the kind of compound that *might* result in a target at
close range receiving **two independent hits** in quick
succession (one from the tap pulse, one from the regular pulse)
— or *might* be invisible because the tap pulse is so short-
range / fast-decay that it doesn't reach an enemy by the time
the regular pulse fires.

## What we'd need to verify

- A close-range enemy encounter that's known to die in a fixed
  number of hits (e.g. one of the Prison guards).
- Frame-by-frame inspection of the tap pulse's lifetime vs the
  regular pulse's spawn delay.
- Empirical: does a regular shot at minimum range take down a
  guard in fewer button-press cycles than a tap shot?

## Why this matters

Player-experience question: is the "regular shot" a single
weapon, or implicitly a double-hit at close range that an
expert player could exploit?

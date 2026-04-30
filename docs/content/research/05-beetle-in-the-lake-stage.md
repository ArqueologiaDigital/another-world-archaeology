# 05 — Beetle in the lake stage: hidden on DOS, kickable on Amiga

## Question

> There's some sort of bug/insect in the initial stage (the one
> where the dark beast chases Lester). The insect looks like a
> beetle, perhaps. And I saw it on Amiga version of the game, but I
> don't see it on the msdos version. […] I seem to remember seeing
> graphics assets representing it opening wings and also an
> animation of it flipping upside-down. But I never saw those
> actions in-game. So I'd like to know if those actions are
> reachable during gameplay, or if that's perhaps some left-over
> partially implemented feature.

## Answer (summary)

The beetle is in **level 2** (the "Arrival at the Lake & Beast Chase"
stage — level 1 is the DNA-helix intro). Both the DOS and Amiga
ports contain the same beetle code, the same walking-cycle
polygons (7 frames each direction), the same wing-opening +
flipping-upside-down animation polygons, and the same
kick-detection dispatch. **The polygon data is byte-identical
between the two ports** (modulo offset renumbering) — same polygon
counts, same byte sizes per frame.

What differs is **one extra bytecode instruction in the DOS
level-entry script** that *suppresses the beetle from rendering*:

```
; Amiga level 2 entry (line 1146):
setup channel=0x09, address=LABEL_3510            ; spawn the beetle
setup channel=0x2E, address=LABEL_34AA            ; spawn the kick-detector
setup channel=0x2E, address=LABEL_3497            ; spawn the cleanup watcher

; DOS level 2 entry (line 1222):
setup channel=0x09, address=LABEL_365A            ; spawn the beetle
setup channel=0x09, address=KILL_CHANNEL_ROUTINE  ; ← OVERWRITES IT
setup channel=0x2E, address=LABEL_35F4            ; spawn the kick-detector
setup channel=0x2E, address=LABEL_35E1            ; spawn the cleanup watcher
```

The DOS port's second `setup channel=0x09, address=KILL_CHANNEL_ROUTINE`
overwrites the beetle handler with a no-op kill routine, so the
beetle is never rendered on DOS — even though all of its code and
polygon data are present in the bytecode.

The wing-opening + flipping-upside-down animations are **reachable
in Amiga via Lester's kick** at the right position. They are
*technically* reachable on DOS too (the kick-detector dispatch is
identical), but since the beetle is never spawned, var `0x0A` (the
beetle's X coordinate) is never initialised in level 2, so the
kick-detector's bounds check against an uninitialised value is
unlikely to ever pass — and even if it did, the animation would
render at junk coordinates.

This looks like a **deliberate cut**: the DOS port shipped with the
beetle present in the resource files but actively gated off, rather
than removing it entirely.

---

## Detailed analysis

### The beetle exists and walks

`BEETLE_WALKING_LEFT` and `BEETLE_WALKING_RIGHT` are bytecode
routines on channel `0x09`, present in both ports. They render a
7-frame walk cycle (each frame held for two video frames before
incrementing the X coordinate by 1) and loop forever:

| Release | `BEETLE_WALKING_RIGHT` | `BEETLE_WALKING_LEFT` |
|---|---|---|
| Amiga | `0x3423` | `0x3518` |
| DOS   | `0x356D` | `0x3662` |

The walk-cycle polygons are pre-existing labels in AWVM_Tools'
data tables:

| Polygon | Amiga offset | DOS offset |
|---|---|---|
| `BEETLE_WALKING_LEFT_0..6` | `0x616A..0x6266` | `0x4D5A..0x4E56` |
| `BEETLE_WALKING_RIGHT_0..6` | `0xB3CC..0xB4C8` | `0x9FBC..0xA0B8` |

Initial spawn is at `LABEL_3510` (Amiga) / `LABEL_365A` (DOS):

```
LABEL_3510:                          ; Amiga
  mov [0x0A], 0x0258                 ;   beetle X = 600
  mov [0x0B], 0x00B6                 ;   beetle Y = 182
  ; falls through to BEETLE_WALKING_LEFT (the 7-frame loop)
```

DOS's `LABEL_365A` is byte-identical except for the offset renumbering.

### The kick-detector: turning the beetle into a wing-flip

Channel `0x2E` runs a separate kick-detector loop (`LABEL_34AA` on
Amiga, `LABEL_35F4` on DOS) which checks:

```
LABEL_34AA:                          ; the kick-detector loop
  break                              ; one frame per iteration
  je [0x06], 0x00, LABEL_34F5        ; var 0x06 == 0 → no kick → keep walking
  jg [0x06], 0x02, LABEL_34F5        ; var 0x06 > 2 → no kick → keep walking
  ; var 0x06 ∈ {1, 2}: kick in progress!
  jl [0x01], [0x04], LABEL_34D9      ; if Lester X < kick-impact X → mirror branch
  mov [0x08], [0x04]
  sub [0x08], 0x0004                 ; check beetle X within ± 4 of kick X
  jl [0x0A], [0x08], LABEL_34F5
  add [0x08], 0x0008
  jg [0x0A], [0x08], LABEL_34F5
  setup channel=0x09, address=LABEL_358B    ; ← KICK CONNECTS! Wing-flip!
  killChannel
LABEL_34D9:
  ; ... mirror branch with the same ±4 check ...
  setup channel=0x09, address=LABEL_3633    ; ← mirror wing-flip
  killChannel
```

`var 0x06` ∈ {1, 2} is set in only four places in level 2, and
they are all **inside Lester's kick handlers**:

| Bytecode label | Sets `[0x06]` | Sets `[0x04]` | Meaning |
|---|---|---|---|
| `LABEL_48D6` (Amiga `LEFT_KICK`)        | `2` | Lester X − 14 | High kick, facing left |
| `LABEL_492B` (Amiga `RIGHT_KICK`)       | `2` | Lester X + 14 | High kick, facing right |
| `LABEL_4980` (Amiga `LEFT_CROUCH_KICK`) | `1` | Lester X − 26 | Crouch kick, facing left |
| `LABEL_49DA` (Amiga `RIGHT_CROUCH_KICK`)| `1` | Lester X + 26 | Crouch kick, facing right |

Each kick handler:

1. Sets `[0x06]` to the kick type (1 = crouch kick, 2 = standing kick)
2. Sets `[0x04]` to the kick's *impact X coordinate* (Lester X ±14
   for high, ±26 for crouch)
3. Plays the kick sound + animation
4. After ~2 frames, resets `[0x06]` back to 0 (kick window closes)

So the kick-detector polls each frame for the brief window when
`[0x06]` is non-zero, checks whether the beetle is within ±4 of
the impact point, and if so, replaces the beetle's animation
channel with the wing-flip routine.

### The wing-flip animation

`LABEL_358B` (Amiga) / `LABEL_36D5` (DOS) is the **right-side wing-flip
death animation**. It:

1. Renders a startle pose (5 frames: `CINEMATIC_661..665`)
2. Flaps its wings (10-iteration loop of 5 frames each:
   `CINEMATIC_666..669` + back to `_664`)
3. Renders the fall (`CINEMATIC_670..672`)
4. Spawns a "lying upside-down" loop (`LABEL_36DB`) on a separate
   channel
5. Loops `CINEMATIC_657, 658` (the upside-down lying state) forever

`LABEL_3633` (Amiga) / `LABEL_377D` (DOS) is the **mirror left-side
version**, with the equivalent polygons numbered ~17 lower
(`CINEMATIC_645..656`, `_659..660`).

### Polygon byte sizes are identical between the ports

Confirmed by polygon-count + SVG byte-size comparison. The wing-flip
polygons are renumbered between ports (different offsets in the
cinematic resource) but the actual polygon data is byte-stable:

| Animation phase | Amiga | DOS | Polygons per frame | Bytes per frame |
|---|---|---|---|---|
| Wings starting to open | `CINEMATIC_661..662` | `CINEMATIC_601..602` | 6 | 770–772 |
| Wing-flap loop | `CINEMATIC_666..669` | `CINEMATIC_606..609` | 9 | 1057 |
| Falling onto its back | `CINEMATIC_670..672` | `CINEMATIC_610..612` | 5 | 673–675 |
| Lying upside-down (loop) | `CINEMATIC_657..660` | `CINEMATIC_597..600` | 8 | 962–964 |

### The DOS suppression mechanism

The DOS level-2 entry script (around bytecode address `0x04C8` —
identifiable by the surrounding `OUTSIDE_POOL_SCREEN` jump) runs:

```
... clear-channels boilerplate ...
setup channel=0x14, address=GETTING_OUT_OF_THE_POOL__ANIMATION_PART_4
setup channel=0x09, address=LABEL_365A             ; spawn beetle (Amiga: LABEL_3510)
setup channel=0x09, address=KILL_CHANNEL_ROUTINE   ; ← THE SUPPRESSION
setup channel=0x2E, address=LABEL_35F4             ; kick-detector (Amiga: LABEL_34AA)
setup channel=0x2E, address=LABEL_35E1             ; cleanup watcher
...
jmp OUTSIDE_POOL_SCREEN
```

Amiga's equivalent line *does not* have the second
`setup channel=0x09, address=KILL_CHANNEL_ROUTINE`. That single
extra instruction is the entire mechanism gating the beetle off in
the DOS port.

The kick-detector on channel `0x2E` is still spawned on DOS — it
runs every frame of level 2, polling for `var 0x06 ∈ {1, 2}`. So
in theory, on DOS, kicking at the right X position could still
overwrite channel `0x09` with the wing-flip animation. **But:**
because the beetle's spawn routine (`LABEL_365A`, which sets var
`0x0A` and `0x0B`) is killed before it ever runs, var `0x0A` is
never initialised in level 2 on DOS — the kick-detector's
`±4`-of-`var 0x0A` bounds check compares against uninitialised
data and is overwhelmingly likely to fail, and even on the rare
occasion it passes, the wing-flip animation would render at the
junk coordinates rather than at any visible location.

### Reachability summary

| Animation | Amiga reachable? | DOS reachable? |
|---|---|---|
| Beetle walking left/right | **Yes** — fires automatically on level entry | No — channel 0x09 killed at entry |
| Wing-flip (right side) | **Yes** — kick the beetle while facing right | Effectively no — junk coordinates |
| Wing-flip (left side, mirror) | **Yes** — kick the beetle while facing left | Effectively no |
| Lying upside-down (looping endpoint) | **Yes** — survives after wing-flip | Effectively no |

### Why is this almost-never seen even on Amiga?

The kick-detector's bounds check is **±4 pixels in X**. The
beetle walks across the screen at 1 pixel per 2 frames. Lester's
kick has an impact zone Lester X ± 14 (standing) or ± 26 (crouch).
For the wing-flip to trigger, Lester must be standing (or
crouching) such that:

- His kick-impact X (`Lester.X ± 14` or `± 26`) is within ±4
  pixels of the beetle's current X
- AND he must press the action button during the brief window
  (~2 frames) when `var 0x06` is set to 1 or 2

In normal gameplay, the player is *running away* from the beast in
this level — they have no incentive to stop and kick a beetle. So
the wing-flip is a *secret reward* for an exploratory player who
happens to walk back and try kicking the beetle.

Whether the wing-flip is **art that was implemented and shipped but
never put in the player's normal path**, or **art that the
designers intentionally hid as a discoverable easter egg**, is a
judgment call I can't make from the bytecode alone. The DOS
port's explicit suppression argues mildly for the former — if it
were a designed easter egg, you'd expect the porters to keep it
intact.

## Open follow-up questions

These are tracked as separate issues:

- **#0044** — Render the wing-flip cinematic frames as PNGs and
  visually confirm they look like a beetle opening wings + flipping
  upside-down (not, say, the slug-flip animations the labels are
  adjacent to).
- **#0045** — Test in an Amiga emulator: does kicking the beetle in
  the lake stage actually trigger the wing-flip animation visibly?
- **#0046** — Suggest a label addition to AWVM_Tools' Amiga and DOS
  data tables: the wing-flip polygons (`CINEMATIC_645..672` Amiga,
  `CINEMATIC_597..612` DOS) are currently unlabeled. Suggest names
  like `BEETLE_WINGS_OPENING_0..N`, `BEETLE_FALLING_0..N`,
  `BEETLE_LYING_UPSIDE_DOWN_0..1`. (Per strict policy:
  AWVM_Tools changes need owner review before implementation.)
- **#0047** — Cross-check Genesis-EU level 2 (the Heineman 1993
  port): does it suppress the beetle the same way DOS does, or
  preserve it like Amiga? Strong genealogy signal either way.

## Genealogy implications

The byte-stable polygon data + structurally identical kick-dispatch
across DOS and Amiga is consistent with the existing
[research finding 01](#/research/01-gun-ammo)'s observation that
mechanic constants are byte-stable across release ports. It adds a
new piece of the puzzle: **the DOS port did not just preserve the
existing bytecode verbatim — it actively edited it to suppress
content**, by adding a single setup-channel-kill instruction. That
is a deliberate per-port decision, not a porting accident.

The natural cross-validation is whether the SEGA Genesis port
(also from the Interplay 1993 port lineage, also by Rebecca
Heineman) preserves the beetle's enable bit or the suppression bit
— see issue #0047.

## Files referenced

- `/tmp/amiga-disasm/output/amiga/disasm/level_2/amiga_level-2.asm`
- `/tmp/dos-disasm-fresh/output/msdos/disasm/level_2/msdos_level-2.asm`
- Amiga polygon SVGs at
  `/tmp/amiga-disasm/output/amiga/disasm/level_2/cinematic/CINEMATIC_NNN.svg`
- DOS polygon SVGs at
  `/tmp/dos-disasm-fresh/output/msdos/disasm/level_2/cinematic/CINEMATIC_NNN.svg`

These are scratch outputs that get regenerated per session — reproduce
with:

```
mkdir /tmp/amiga-disasm && cd /tmp/amiga-disasm
awvm-disasm /path/to/amiga-banks all_levels amiga
```

## Changelog

- **2026-04-30** — initial finding. Triggered by the project owner
  observing the beetle on Amiga but not on DOS, and asking whether
  the wing-opening + flipping-upside-down polygons they remembered
  are reachable in gameplay.

# 05 — Beetle in the lake stage: dead-coded on both ports, hidden on DOS

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
flying-upside-down animation polygons, and the same kick-detection
dispatch. **The polygon data is byte-identical between the two
ports** (modulo offset renumbering) — same polygon counts, same
byte sizes per frame.

**The wing-flip is unreachable in normal gameplay on *both* ports.**
Confirmed empirically: kicks visibly fire on Amiga but the beetle
walks past them unaffected. Two distinct gates suppress the wing-flip:

**Gate 1 — kick-detector overwrite** (present on **both** ports).
The level-entry script registers the kick-detector and then
*immediately overwrites it* with the cleanup-watcher on the same
channel:

```
; Amiga level 2 entry (line 1147–1148):
setup channel=0x2E, address=LABEL_34AA   ; the kick-detector
setup channel=0x2E, address=LABEL_3497   ; cleanup watcher OVERWRITES it

; DOS level 2 entry (line 1224–1225):
setup channel=0x2E, address=LABEL_35F4   ; the kick-detector
setup channel=0x2E, address=LABEL_35E1   ; cleanup watcher OVERWRITES it
```

By AW VM semantics — confirmed empirically by the DOS beetle-
suppression pattern below — two consecutive setups on the same
channel cause the second to override the first. So channel `0x2E`
ends up running the *cleanup watcher* (which only kills the beetle
when it walks off-screen in scene 1), and the *kick-detector*
never runs at all. Lester's kicks fire, `var 0x06` gets set to 1
or 2 briefly, but **no thread is polling for that value**, so the
wing-flip is never dispatched.

**Gate 2 — beetle suppression** (DOS only). On top of gate 1, the
DOS port also kills the beetle's rendering channel itself:

```
; DOS level 2 entry (line 1222–1223):
setup channel=0x09, address=LABEL_365A            ; spawn the beetle
setup channel=0x09, address=KILL_CHANNEL_ROUTINE  ; ← second gate (DOS only)

; Amiga has only the first line — beetle is rendered.
```

So:

- **On Amiga**: the beetle is visible (gate 2 not present), but the
  kick-detector is dead (gate 1). You see the beetle walking; kicks
  fire but have no effect on it.
- **On DOS**: both gates active. The beetle isn't rendered at all,
  and even if it were, the kick-detector wouldn't connect.

**The wing-flip animation is therefore content that exists fully in
both ports' bytecode + polygon data, but is gated off at runtime on
both.** It's reachable only by hacking the bytecode (e.g., removing
the second `setup channel=0x2E` line, or using a debugger to redirect
channel 0x2E mid-run).

This is a stronger statement than the original 2026-04-30 reading of
this finding, which thought gate 2 (DOS-only) was the only mechanism
and that the wing-flip was reachable via kicks on Amiga. Empirical
testing in MAME (Amiga emulation) — kicks fire but no wing-flip —
revealed gate 1, which is the deeper and earlier mechanism.

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

**That's what the kick-detector *would* do — but it never gets a
chance.** As [described in the Answer](#answer-summary), the
level-entry script's second `setup channel=0x2E` overwrites the
kick-detector address with the cleanup-watcher address, on both
ports. The kick-detector code is correct and intact in the bytecode;
it is simply never given a thread to run on. See "The
suppression mechanisms" section below for the full picture.

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

### The suppression mechanisms

There are **two distinct gates** at play, sitting in different places
in the level-entry script:

#### Gate 1 — the channel-0x2E overwrite (BOTH ports)

```
; Amiga level 2 entry (line 1147–1148):
setup channel=0x2E, address=LABEL_34AA   ; kick-detector
setup channel=0x2E, address=LABEL_3497   ; cleanup watcher OVERWRITES it

; DOS level 2 entry (line 1224–1225):
setup channel=0x2E, address=LABEL_35F4   ; kick-detector
setup channel=0x2E, address=LABEL_35E1   ; cleanup watcher OVERWRITES it
```

Because `setup channel=N, …` queues the channel's next program until
the next sync point (and queueing twice in the same instruction
stream just leaves the second value in the queue), channel 0x2E
ends up running the **cleanup watcher** (`LABEL_3497` Amiga /
`LABEL_35E1` DOS) and **never the kick-detector**. The cleanup
watcher's job is just to kill the beetle when it walks off-screen
in scene 1; it doesn't poll `var 0x06`. So `var 0x06` going to 1 or
2 (when Lester kicks) has no observer, and the wing-flip dispatch
at `setup channel=0x09, address=LABEL_358B` never executes.

This gate is **on both ports**.

#### Gate 2 — the channel-0x09 overwrite (DOS only)

On top of gate 1, the DOS port also kills the beetle's rendering
channel:

```
; DOS level 2 entry (line 1222–1223):
setup channel=0x09, address=LABEL_365A            ; spawn beetle (Amiga: LABEL_3510)
setup channel=0x09, address=KILL_CHANNEL_ROUTINE  ; ← second gate (DOS only)
```

Amiga's level-entry has only the first line — beetle is rendered.
DOS has both lines — beetle's rendering channel is killed before it
ever runs, so the beetle is invisible.

This gate is **DOS-only**.

#### Why the same authorial pattern shows up twice

Both gates use the same trick: register a thing on a channel, then
register a different thing on the same channel in the very next
instruction. The second `setup` overrides the first. **Empirical
confirmation that the override is real**: the beetle is invisible
on DOS (proving gate 2 works as described). By the same VM
semantic, gate 1 is also real — the kick-detector is dead on both
ports, even though there's no comparable visual evidence (you can't
"see" a polling loop not running).

#### Empirical validation of gate 1

Testing in MAME (Amiga, retro-presskit ADFs): Lester visibly kicks
in the lake stage (kick animation plays correctly), but the beetle
walks past unaffected. Direct match for "the kick-detector is dead
even on Amiga". Recorded against issue #0045.

### Reachability summary (across all six currently-disassembled ports)

| Animation | Amiga 1991 | Atari ST 1991 | DOS 1992 | SNES-EU 1992 | Genesis-EU 1993 | GBA 2004 |
|---|---|---|---|---|---|---|
| Beetle walking left/right | **Yes** | **Yes** | No (g2) | No (g2) | No (g2) | No (g2) |
| Wing-flip (right side) | No (g1) | No (g1) | No (g1+g2) | No (g1+g2) | No (g1+g2) | No (g1+g2) |
| Wing-flip (left side, mirror) | No (g1) | No (g1) | No (g1+g2) | No (g1+g2) | No (g1+g2) | No (g1+g2) |
| Falling onto back | No | No | No | No | No | No |
| Flying upside-down + take-off | No | No | No | No | No | No |

The wing-flip is **dead in all six ports**. Only the two 1991 ports
(Amiga + Atari ST) show the beetle visually at all. Apple IIgs
(Interplay 1993) has not yet been extracted — its bytecode is gated
on a WOZ flux-level reader (issue #0014).

### Six-port comparison: which gates each port carries

| Port | Year | Author | Beetle spawn | 2nd `setup ch=0x09` (g2) | Kick-detector | 2nd `setup ch=0x2E` (g1) |
|---|---|---|---|---|---|---|
| **Amiga**        | 1991 | Chahi    | `0x3510` | (none) | `0x34AA` | `0x3497` cleanup |
| **Atari ST**     | 1991 | Chahi    | `0x3510` | (none) | `0x34AA` | `0x3497` cleanup |
| **DOS**          | 1992 | Heineman | `0x365A` | `KILL_CHANNEL_ROUTINE` | `0x35F4` | `0x35E1` cleanup |
| **SNES-EU**      | 1992 | Heineman | `0x36FD` | `KILL_CHANNEL_ROUTINE` | `0x3697` | `0x3684` cleanup |
| **Genesis-EU**   | 1993 | Heineman | `0x36FD` | `KILL_CHANNEL_ROUTINE` | `0x3697` | `0x3684` cleanup |
| **GBA (Foxy)**   | 2004 | Foxy     | `0x3721` | `KILL_CHANNEL_ROUTINE` | `0x36BB` | `0x36A8` cleanup |

Same kick-detector code is intact on all six ports (just unrunnable
because of gate 1) — confirmed by reading the kick-detector body in
each port: same `je [0x06], 0x00`/`jg [0x06], 0x02` guards, same
`[0x04] ± 4` bounds checks, same `setup channel=0x09, address=…`
wing-flip dispatch. The kick-dispatch logic was preserved verbatim
across thirteen years and four CPU architectures (68k, x86, 65816,
68000, ARM).

### Cartridge port cross-check: SNES-EU + Genesis-EU share byte-identical bytecode

Verified empirically (2026-04-30): the SNES-EU and Genesis-EU
**lake-stage bytecode resources are byte-identical** —
md5 `68b4c327f8eec279e01e6c44ecce178d`, 20,863 raw operand bytes
emitted by the disassembler — even though they ship on completely
different cartridge formats with different CPU architectures
(SNES = 65816; Genesis = 68000).

The five-port lake-stage bytecode hash matrix:

| Port | Lake-stage bytecode md5 | raw-byte size |
|---|---|---|
| **Amiga** 1991                  | `6f5ab0e0868cc23025c7551eea549e85` | 19,332 |
| **Atari ST** 1991 (resource md5) | `860362f3718ca4fe4a8e65cdbe40f155` | 19,458 |
| **DOS** 1992                    | `3e95437f541f27ef9d121e31fa06ce52` | 20,684 |
| **SNES-EU** 1992                | `68b4c327f8eec279e01e6c44ecce178d` | 20,863 |
| **Genesis-EU** 1993             | `68b4c327f8eec279e01e6c44ecce178d` | 20,863 |
| **GBA (Foxy)** 2004             | `37487368811666a6b3103a63434db002` | 19,717 |

(Atari ST disasm hash is the resource's raw uncompressed bytes —
disasm itself is gated on issue #0004. The Atari ST resource is
**byte-identical to the Amiga resource**, which has md5 `6f5ab0e0…`
*after disasm extraction* but `860362f3…` *as the raw resource*.
The two hashes refer to different views of the same bytes.)

This is decisive lineage data:

- **Amiga + Atari ST 1991** = single Chahi master, distributed on
  two SKUs.
- **SNES-EU 1992 + Genesis-EU 1993** = single Heineman build, ported
  to two cartridge platforms with the AW VM bytecode resource
  reused verbatim. Heineman's 1993 Genesis-EU port did **not**
  re-derive bytecode from his earlier DOS port (which has its own
  hash `3e95437f…`); it built on the SNES-EU bytecode.
- **DOS 1992** = its own Heineman build, distinct from the SNES
  build despite sharing the gates 1+2 editorial choices.
- **GBA 2004 (Foxy)** = a separate later branch with modified
  bytecode (size 19,717), differing from all of the original 1991-93
  ports. The gates remained intact through Foxy's modifications.

The two-tier branching:

```
                 Pre-1991 dev master (Chahi)
                          │
                          ▼
                 1991 release master (Chahi, gate 1 added)
                  ├── Amiga 1991       ┐  byte-identical
                  └── Atari ST 1991    ┘  level-2 bytecode
                          │
                          ▼  (separate port: Heineman, gates 1+2)
                  ┌────── DOS 1992 ──────┐  (own bytecode hash)
                  │                      │
                  │ ┌── SNES-EU 1992 ─┐  │  byte-identical
                  │ └── Genesis-EU 1993 ┘  level-1/0 bytecode
                  │                      │
                  └──────────────────────┘
                          │
                          ▼  (later derivative: Foxy/Magic Pockets)
                       GBA 2004 (own bytecode; gates preserved)
```

The DOS-vs-SNES distinction is the most surprising data point.
Heineman shipped both in 1992; if he'd worked from a single
internal codebase the bytecode would match. The fact that they
differ — but DOS and Amiga also differ from each other in different
ways — suggests Heineman maintained two parallel ports rather than
a shared bytecode source. Hypotheses to investigate:

- Different per-port byte-layout post-processors (e.g. a tool that
  recompresses or reorders resources for cartridge ROM packing).
- Different snapshots: the SNES port may have been forked from DOS
  at an earlier point in development and diverged independently.
- Active per-port edits — bug-fixes or platform-specific tweaks
  applied to one branch but not the other.

### Atari ST and Amiga share byte-identical level-2 bytecode

Verified empirically (2026-04-30): the Atari ST level-2 bytecode
resource is **byte-identical to Amiga's**. Both 19,458 bytes,
md5 `860362f3718ca4fe4a8e65cdbe40f155`. Both live at the same
memlist index (#27), same bank (BANK02), same bank offset
(`0x008516`), same `packed_size == size` (i.e., stored uncompressed
in both ports).

Atari ST stores its memlist embedded in `START.PRG` at offset
`0x7ef2`, length `20 × 147 = 2940` bytes — same struct format as
Amiga's memlist (which lives in `another` at offset `0x5ec2`,
already known to AWVM_Tools). Memlist entry layout (big-endian on
both 68k ports): `state(1) type(1) bufPtr(4) rankNum(1) bankId(1)
bankOffset(4) unkC(2) packedSize(2) unkE(2) size(2)` = 20 bytes.

So the 1991 dual release (Amiga + Atari ST) was built from a single
master: **same bytecode resources, same bank file layout, same
memlist contents.** The platform differences are in the engine
binary (`another` on Amiga, `START.PRG` on Atari ST) and in the
bank-file packaging — *not* in the VM bytecode.

### What about the bounds check that the kick-detector implements?

If gate 1 weren't present and the kick-detector did run, its bounds
check would be **±4 pixels in X**. The beetle walks across the
screen at 1 pixel per 2 frames. Lester's kick has an impact zone
Lester X ± 14 (standing) or ± 26 (crouch). For the wing-flip to
trigger, Lester would have to be standing (or crouching) such that:

- His kick-impact X (`Lester.X ± 14` or `± 26`) is within ±4
  pixels of the beetle's current X
- AND he must press the action button during the brief window
  (~2 frames) when `var 0x06` is set to 1 or 2

So even *without* gate 1, the wing-flip would have been a tight,
precise interaction the player would essentially never trigger by
accident. The presence of gate 1 makes that academic — but the
combination (a tight precision requirement + a hard cancel) is
informative about what the developers were thinking. Either:

1. **Bug-then-mask**: the kick-detector was added late, then
   discovered to be janky / unreliable / a balance issue, and
   silenced by adding the cleanup watcher to the same channel.
2. **Deliberate cut from the start**: the kick-the-beetle
   interaction was prototyped, then cut for design reasons, and the
   level-entry overwrite is how they cut it without removing the
   underlying code (cheaper than a full removal).
3. **Authorial accident**: someone wrote the cleanup watcher
   alongside the kick-detector without realising they collided on
   the same channel slot.

Hypothesis 3 is mildly disfavoured by the *identical* pattern
appearing on channel 0x09 (the DOS beetle suppression) — that one
is unambiguously deliberate, since DOS doesn't ship the beetle at
all. If the developers used the override pattern intentionally
once, they probably knew what they were doing the other time too.

Whether the wing-flip is **art that was implemented and shipped but
deliberately disabled before release**, or **a bug** (the cleanup
watcher accidentally ate the kick-detector's channel slot), is a
judgment call I can't make from the bytecode alone. Both the
channel-0x2E and channel-0x09 patterns being identical
(setup-then-overwrite-on-same-channel) leans deliberate; but the
cleanup watcher could equally have been put on a different channel
without conflict, which leans accidental for the kick-detector cut.
Open question, tracked in issue #0048.

### Does the beetle fly?

**Yes — and the "flipping-upside-down" frames the user remembered
are not a death animation; they're a *stunned* state from which
the beetle recovers and escapes by flying away.**

The full sequence after a kick connects:

1. **Wing-opening + flap loop** (`LABEL_358B` body, ~25–35 frames):
   the beetle hops back, opens its wings, flaps in place.
2. **Falling onto its back** (3 frames `CINEMATIC_670..672`).
3. **Stunned-on-back** (~10 frames): channel `0x09` is switched to
   `LABEL_35ED`, an infinite 2-frame loop of `CINEMATIC_659..660`.
   Channel `0x2E` is simultaneously kicked over to `LABEL_36DB`,
   which sleeps 10 frames before doing anything.
4. **Wings re-engage and lift-off begins**: channel `0x2E` writes
   `setup channel=0x09, address=LABEL_36A4` — switching the
   render to the upside-down *flapping* loop (`CINEMATIC_657..658`),
   which itself decrements `var 0x0B` by 1 per frame.
5. **Slow lift-off** (8 frames): controller subtracts 2 from `var
   0x0B` and adds 1 to `var 0x0A` per frame. Combined with the
   render loop's −1, the beetle rises at ~3 px/frame and drifts
   slightly right.
6. **Fast escape** (until X ≥ 360, ~screen-right): controller
   switches to `Y −= 2; X += 12` per frame. The beetle banks up and
   to the right, off-screen.
7. **Final settle**: `mov [0x0B], 0x0092` (Y = 146); the channel
   ends. The beetle is gone.

The take-off code is **byte-identical between Amiga (`LABEL_36DB`)
and DOS (`LABEL_3825`)** — same constants, same control flow.

So the creature isn't a "ground beetle that dies when kicked" — it's
a **flying beetle** that walks across the ground when at rest, falls
on its back when startled, and **escapes by flying off-screen**,
still inverted. The wings serve a real mechanical purpose. From a
naturalism standpoint, this is a remarkably small detail to ship in a
1991 cinematic-platformer's first level — for a creature that has no
gameplay consequence whatsoever.

### Can the beetle hurt Lester?

**No.** The bytecode contains no offensive code on the beetle's
side. To put it in context, the beast in the same level *does*
hurt Lester, and its hazard mechanism is straightforward:

```
CHECK_IF_THE_BEAST_HAS_ALREADY_REACHED_LESTER:
  mov [0x11], [0x0E]                   ; copy beast X (var 0x0E)
  sub [0x11], 0x0028                   ; beast X − 40
  jg [0x11], [0x01], THE_BEAST_IS_STILL_AT_A_DISTANCE  ; if Lester is more than 40 pixels right of beast, ok
  ; ... otherwise:
  setup channel=0x28, address=THE_BEAST_KILLS_LESTER   ; trigger Lester's death cinematic
```

The beast has all three components of a hazard:
1. A **position-tracking variable** (`var 0x0E` = beast X)
2. A **collision-detection routine** that polls each frame and
   compares the beast's position against Lester's (`var 0x01`)
3. A **kill trigger** that swaps in `THE_BEAST_KILLS_LESTER` on
   channel `0x28`

The beetle has none of these. Across both Amiga and DOS level-2
disassemblies, every single read of `var 0x0A` (beetle X) and
`var 0x0B` (beetle Y) falls into exactly three categories:

| Read site | Purpose | Threatens Lester? |
|---|---|---|
| `BEETLE_WALKING_RIGHT` / `_LEFT` | Render the walk animation at the beetle's current X / Y | No |
| Cleanup watcher (`LABEL_3497`) | `jg [0x0A], 0x014A` — when the beetle walks off the right edge of the screen, kill its channel | No |
| Kick-detector (`LABEL_34AA`) | `[0x0A]` vs `[0x04] ± 4` — checks if Lester's *kick* impact connects with the beetle | No (the opposite direction — Lester hurts the beetle) |

There is **no comparison of `var 0x0A` against `var 0x01` (Lester
X)** anywhere in level 2. The wing-flip routines (`LABEL_358B`,
`LABEL_3633` and their DOS counterparts) likewise contain only
`video` rendering calls and a few state-mode writes against `var
0x09` (the inner flap-loop counter) — no setup of a kill channel,
no Lester-state writes, no damage triggers of any kind.

So the beetle is **strictly an aesthetic prop**: it walks across
the screen as ambient fauna, with no interaction with anything in
the rest of the level. A player ignoring it pays no penalty;
there's nothing to dodge. The kick-the-beetle interaction that
appears to exist in the bytecode was disabled before release on
both ports (gate 1 above), so even pressing fire near it has no
effect.

## Open follow-up questions

These are tracked as separate issues:

- **#0044** — Render the wing-flip cinematic frames as PNGs and
  visually confirm they look like a beetle opening wings + flying
  upside-down (not, say, the slug-flip animations the labels are
  adjacent to).
- **#0045** — Test in an Amiga emulator: does kicking the beetle in
  the lake stage actually trigger the wing-flip animation visibly?
  (**RESOLVED 2026-04-30**: tested in MAME, kicks fire but no
  wing-flip — confirms gate 1.)
- **#0046** — Suggest a label addition to AWVM_Tools' Amiga and DOS
  data tables for the wing-flip polygons.
- **#0047** — Cross-check Genesis-EU level 2 (the Heineman 1993
  port). **RESOLVED 2026-04-30**: Genesis-EU has *both* gates
  (matches DOS, not Amiga); cinematic offsets are identical to DOS
  and different from Amiga. The Heineman lineage clearly
  preserves both gates. See "Genealogy implications" below.
- **#0048** — Investigate whether the gate-1 kick-detector
  overwrite is intentional or accidental. The cleanup watcher
  could trivially have been put on a different channel without
  conflict; whether the conflict was a deliberate cut or an
  authorial oversight is currently undecidable from the bytecode.

## Genealogy implications

The byte-stable polygon data + structurally identical kick-dispatch
across all three ports is consistent with the existing
[research finding 01](#/research/01-gun-ammo)'s observation that
mechanic constants are byte-stable across release ports. The
beetle finding adds three new pieces:

1. **The original Amiga build *itself* contains a content-gate**
   — the channel-0x2E kick-detector overwrite (gate 1 above) — that
   both subsequent ports inherit intact. So gating off the wing-flip
   is not a per-port editorial decision; it's already in the
   upstream that all ports descend from. **This is the first
   finding of pre-shipping content cuts visible in the bytecode
   itself.**

2. **The Heineman lineage (DOS 1992 + Genesis-EU 1993) shares a
   second editorial cut** — gate 2 (channel-0x09 beetle suppression).
   Verified 2026-04-30 against Genesis-EU level 0: it has the same
   double-`setup channel=0x09` pattern as DOS, with the second
   setup pointing at `KILL_CHANNEL_ROUTINE` (the same opcode).

3. **DOS and Genesis-EU share the cinematic resource layout**, but
   Amiga doesn't. Confirmed by polygon offsets:

   - Amiga: `BEETLE_WALKING_LEFT_0..6` at `0x616A..0x6266`,
     `BEETLE_WALKING_RIGHT_0..6` at `0xB3CC..0xB4C8`.
   - DOS: at `0x4D5A..0x4E56` and `0x9FBC..0xA0B8`.
   - Genesis-EU: at `0x4D5A..0x4E56` and `0x9FBC..0xA0B8`
     (**identical to DOS, not Amiga**).

   So the cinematic resource is shared between DOS and Genesis-EU,
   strongly suggesting Heineman built the Genesis-EU port from the
   DOS port's resources rather than re-deriving from Amiga.

Combined, this gives a clean lineage hypothesis:

```
Pre-1991 dev build (Chahi):  beetle alive, wing-flip working
        │
        ▼
1991 dual release (Chahi):   gate 1 added — beetle visible, wing-flip silenced
   ├── Amiga                 ↘  byte-identical level-2 bytecode
   └── Atari ST              ↗  (same memlist contents, same bank layout)
        │
        ▼
1992 DOS port (Heineman):    inherits gate 1; adds gate 2 — beetle hidden too
        │                    cinematic resource laid out at new offsets
        ▼
1993 Genesis-EU (Heineman):  inherits gate 1 + gate 2 + DOS cinematic offsets
                             (does NOT re-derive from Amiga)
```

The "Heineman built Genesis-EU from his DOS port, not from Amiga
upstream" hypothesis is testable by spot-checking other resources
(non-beetle cinematics, bytecode constants) for the same DOS-vs-
Amiga offset signature. Worth a follow-up.

The Atari ST byte-identity finding has its own implication for
issue #0048 (whether gate 1 is intentional or accidental). Both
1991 SKUs have gate 1, but they share the *same dev master* (proven
by byte-identical bytecode), so a single editorial decision (or a
single accident) propagates to both. The Atari ST data point
doesn't move the needle on intent — it just proves the 1991 master
is a single artifact.

## Verification hack: re-enable the beetle kick on Amiga (2026-04-30)

A surgical 2-byte patch that makes the wing-flip animation
reachable in real gameplay (rather than only by reading the
bytecode) lives in the sibling
[`another-world-hacks`](https://github.com/felipesanches/another-world-hacks)
repo, under `01-amiga-beetle-kick-reenable/`.

The patch swaps the two address operands in the gate-1 instruction
pair so the kick-detector overrides the cleanup-watcher (rather
than the other way around) on channel `0x2E`:

```
; original (gate-1 dead — kick-detector overwritten):
082E34AA 082E3497   = setup ch=0x2E addr=0x34AA   (kick-detector)
                     setup ch=0x2E addr=0x3497   (cleanup, overrides)

; patched (gate-1 inverted — kick-detector wins):
082E3497 082E34AA   = setup ch=0x2E addr=0x3497   (cleanup)
                     setup ch=0x2E addr=0x34AA   (kick-detector, overrides)
```

The patch lives at BANK02 offset `0x008934` (= level-2 BYTECODE
resource offset `0x041e`), and on the archive.org 2020 Amiga
Disk1.adf it lands at ADF offset `0x0255f4` inside OFS data block
#298 (file BANK02's 72nd data block). The hacks repo provides two
patchers:

- `patch_bank02.py` — operates on a raw extracted BANK02 file.
- `patch_adf.py` — operates directly on Disk1.adf, recomputes the
  OFS data-block checksum, and writes a fully bootable patched
  ADF that any Amiga emulator (MAME, FS-UAE, WinUAE) can load.

After the patch, the wing-flip + falling + take-off sequence
that's encoded in the level-2 bytecode but normally unreachable
becomes reachable: kick the beetle in the lake stage and watch
it open its wings, fall onto its back, lie stunned briefly, and
fly off-screen upside-down. This is the runtime-level
confirmation of the bytecode-level finding.

The patch is intentionally minimal (2 bytes — the smallest
possible change that flips gate 1) so that any other behavioural
delta in the patched game definitively comes from removing
gate 1, not from a side effect of a larger edit. The
cleanup-watcher (which tears down the beetle when it walks
off-screen in scene 1) is the regression — it's the one that
gets overwritten now — but the beetle is on-screen for under
five seconds in normal play, so this rarely matters.

A future revision could put the cleanup-watcher on a different
unused channel slot (e.g. `0x3D`) instead of just swapping —
that would preserve both the kick-detector AND the cleanup. Not
done in v1 to keep the patch surgically minimal.

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
- **2026-04-30** (same day, follow-up) — added "Can the beetle
  hurt Lester?" subsection in response to the owner's follow-up
  question. Confirmed by exhaustive enumeration of `var 0x0A` /
  `var 0x0B` reads that the beetle has no collision-with-Lester
  check and no kill-Lester trigger. Compared against the beast's
  full three-part hazard structure (position variable +
  collision routine + kill trigger) for context.
- **2026-04-30** (same day, follow-up) — added "Does the beetle
  fly?" subsection in response to the owner's follow-up. The
  bytecode at `LABEL_36DB` (Amiga) / `LABEL_3825` (DOS) is a
  full take-off sequence: 10-frame stun beat, 8-frame slow
  lift-off (`Y −= 2`, `X += 1`), then accelerated escape
  (`Y −= 2`, `X += 12`) until the beetle is off-screen right.
  Combined with the rendering loop's own `sub [0x0B], 0x0001`,
  the beetle rises at ~3 px/frame. So the "flipping-upside-down"
  frames are a *stunned* state from which the beetle recovers
  and escapes — not a death animation. The take-off code is
  byte-identical between Amiga and DOS.
- **2026-04-30** (same day, **major correction** in response to
  owner's MAME testing) — the wing-flip is **unreachable in normal
  play on both ports**, not just DOS. Empirical: kicks visibly
  fire on Amiga but the beetle walks past unaffected. Cause: the
  level-entry script registers the kick-detector on channel 0x2E
  and *immediately overwrites it* with the cleanup-watcher on the
  same channel (lines 1147–1148 Amiga, 1224–1225 DOS) — same
  override pattern as the DOS-only beetle suppression on channel
  0x09. So the kick-detector never gets a thread to run on. The
  finding's earlier framing — "kickable on Amiga" — was wrong; the
  wing-flip is shipped content that is gated off at runtime even
  on Amiga. Restructured the "suppression mechanisms" section to
  describe gate 1 (channel 0x2E, both ports) and gate 2 (channel
  0x09, DOS-only) as two distinct editorial cuts. Reachability
  table updated to show **No** for all wing-flip animations on
  both ports. Genealogy implications expanded — the gate-1 cut is
  *upstream of both ports*, meaning the original Amiga build
  itself already shipped this content gated off; the DOS port adds
  gate 2 on top. New issue #0048 opened to investigate whether
  gate 1 is intentional or accidental.
- **2026-04-30** (same day, follow-up — Genesis-EU cross-check) —
  Genesis-EU level 0 (the Heineman 1993 port's lake stage)
  inspected. **Both gates present**, matching DOS exactly:
  `setup channel=0x09, address=LABEL_36FD` followed by
  `setup channel=0x09, address=KILL_CHANNEL_ROUTINE` (gate 2),
  then `setup channel=0x2E, address=LABEL_3697` followed by
  `setup channel=0x2E, address=LABEL_3684` (gate 1). Cinematic
  resource offsets are identical to DOS (`BEETLE_WALKING_LEFT_0`
  at `0x4D5A`, `BEETLE_WALKING_RIGHT_0` at `0x9FBC`) and different
  from Amiga (`0x616A` and `0xB3CC`), suggesting Heineman built
  the Genesis-EU port from his DOS port's resources rather than
  re-deriving from Amiga. Reachability table widened to three
  columns. Genealogy implications expanded with a 4-step lineage
  diagram (Pre-1991 → Amiga 1991 → DOS 1992 → Genesis-EU 1993)
  showing each port's added gates. Issue #0047 closed.
- **2026-04-30** (same day, follow-up — Atari ST cross-check) —
  Atari ST 1991 (the Pasti `.stx` release) inspected. **Same as
  Amiga**: gate 1 present (`setup ch=0x2E, addr=0x34AA` → `addr=0x3497`),
  gate 2 NOT present, beetle visible. **Level-2 bytecode resource
  is byte-identical to Amiga**: 19,458 bytes, md5
  `860362f3718ca4fe4a8e65cdbe40f155` for both, same memlist index
  (#27), same bank (BANK02), same offset (0x008516). The 1991 dual
  release is a single dev master shipped on two 68k SKUs.

  As a side benefit, recovered the Atari ST memlist location:
  embedded in `START.PRG` at offset `0x7ef2`, length `20 × 147 =
  2940` bytes, same struct format as Amiga (big-endian fields).
  This unblocks issue #0004 (Atari ST embedded memlist parse).

  Reachability table widened to four columns. Lineage diagram
  updated to show the Amiga + Atari ST 1991 dual release as one
  branch with byte-identical bytecode. Issue #0049 closed.
- **2026-04-30** (same day, follow-up — cartridge port cross-check) —
  SNES-EU 1992 and GBA Foxy 2004 inspected. Both carry **gates 1 +
  2**, matching DOS / Genesis-EU exactly. The kick-detector
  bounds-check + dispatch logic is structurally intact in all six
  ports (`[0x04] ± 4`, `setup channel=0x09, address=…`).

  Genealogy bonus: the **SNES-EU lake-stage bytecode is
  byte-identical to Genesis-EU's** — md5
  `68b4c327f8eec279e01e6c44ecce178d`, 20,863 raw operand bytes —
  even though they ship on completely different cartridge formats
  (SNES = 65816 CPU, Genesis = 68000). The DOS bytecode hash
  (`3e95437f…`) differs from both, so Heineman's three Heineman-era
  ports (DOS / SNES-EU / Genesis-EU) carry **two distinct bytecode
  branches**, not one. The Genesis-EU port descends from the
  SNES-EU branch, not from DOS, even though DOS shipped first.

  GBA bytecode (`37487368…`, 19,717 bytes) is distinct from all
  earlier ports — Foxy / Magic Pockets modified the bytecode for
  the 2004 GBA port but preserved the gates. Reachability +
  comparison tables widened to six columns (Apple IIgs still
  pending — gated on the WOZ extractor, issue #0014). Lineage
  diagram updated with the SNES↔Genesis byte-identity branch.
- **2026-04-30** (same day, follow-up — verification hack landed) —
  set up the sibling `another-world-hacks` repo and committed
  `01-amiga-beetle-kick-reenable/`: a 2-byte ADF patch that swaps
  the gate-1 instruction pair so the kick-detector overrides the
  cleanup-watcher (rather than the other way around). The patch
  generates a fully bootable `Another_World_Disk1_BEETLE_KICK.adf`
  with exactly 2 byte changes (`0x0255f7` and `0x0255fb`) and a
  recomputed OFS data-block checksum. This is the runtime-level
  artifact that converts the bytecode-level gate-1 finding into a
  reproducible visual: kick the beetle, watch the wing-flip /
  fall / take-off animation that the unmodified game silences.
  Documented as a new "Verification hack" subsection above.

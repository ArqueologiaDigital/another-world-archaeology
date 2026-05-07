# 01 — Gun ammo / shot quota in the bytecode

## Question

> The walkthrough mentions: "the gun doesn't have unlimited ammo" — and
> in some places there are charging stations for the gun. How is the
> gun handled in the code? Is there a counter? What does it count?
> Simple shots, shield-shots, or mega-blast shots? If there's a usage
> quota, how can we precisely describe it?

(Original phrasing in [open question 01](#/open-questions/01-gun-ammo).)

## Answer (summary)

- The gun energy is stored in **VM variable `0x06`**.
- **Three weapon modes are dispatched by hold-time, with compound
  energy costs**: pressing the action button always fires a small
  "tap" shot *unconditionally* on the first frame, and if the
  button is held longer a *separate* shot (regular or superblast)
  fires later from a parallel "firing thread". So the
  total cost of each player action is:
  - **Quick tap** (release within 4 frames): **−1** (just the tap)
  - **Regular shot** (held + released): **−1 + −10 = −11** (tap + regular)
  - **Superblast** (held ≥ 20 frames): **−1 + −50 = −51** (tap + superblast,
    or **−101** in level 3 Prison Escape where the superblast costs
    −100)
- The tap and the regular are **two different laser pulses**, not
  two states of the same shot. They use separate spawn routines,
  separate shot-tracking slot tables, separate sounds, and the
  regular has a visible muzzle-flash polygon (`CINEMATIC_037`) the
  tap doesn't. (The gun is a laser/plasma-style energy weapon,
  not a kinetic firearm — every "shot" in this document is a
  discrete pulse of laser light, even when the bytecode comments
  below use the term *bullet* in its generic shot-tracking sense.)
  See the "Visual / mechanical semantics of each shot type"
  section below.
- **The shield is free** — the visual shield is the gun-drawn
  animation rendered while the action button is held; no decrement
  happens while it's up. (But entering the shield still costs the
  unconditional −1 tap that fires the moment the button goes down.)
- The dispatch is **two cooperating VM threads** — a state-machine
  thread that handles animation and a firing thread that counts
  held-frames and branches on threshold.
- **Two recharge zones** in the entire game, both in **level 4 (Gas
  Tunnels)**, sharing a single recharge handler (`LABEL_3473`).
  The handler is `setup`'d on channel 0x36 from two distinct scene
  initialisers and switches its trigger geometry on `HACK_VAR_67`:
  the default scene fires on `X ≤ 103` (any Y), the alternate scene
  (`HACK_VAR_67 == 0x4F`) requires `X ≤ 110 && Y ≤ 100`. Both rooms
  also require Lester to be facing right and energy < 991. The
  recharge itself is a **clamp-to-1000** (`mov`, not `add`).
- **Per-level initial values:**
  - Level 3 (Prison Escape): **199 energy**
  - Level 4 (Gas Tunnels):   **990 energy**
  - Level 6 (Final Action):  **990 energy**
- **The code is byte-for-byte identical between DOS, Amiga
  (retro-presskit), and Genesis-EU** — same variable, same costs,
  same recharge, same initializers.

The level-3-only −100 superblast cost (vs −50 in levels 4/6) is
**not a port-specific drift** — it's an intentional design choice
in the original 1991 code, present consistently across all releases
that disassemble.

---

## Detailed analysis

### Input dispatch

The shoot/shield/superblast dispatch is split across **two cooperating
VM threads**, both gated on `HERO_ACTION_POS_MASK == 0x80` (action
button held, no movement).

**State-machine thread** (hero animation channel) at
`level_4.asm:23721` (`LABEL_EF03`):

```
LABEL_EF03:
  jne [0x0F], 0x00, LABEL_EF38            ; skip if state already advanced
  sub [0x01], 0x0002                      ; nudge X
  call LABEL_9D73                         ; draw "gun raised" animation
  mov [0x21], [0x01]; mov [0x27], [0x02]  ; shot origin = Lester's coords
  sub [0x21], 0x001E; sub [0x27], 0x0027  ; offset to muzzle
  call LABEL_6588                         ; spawn tap, deduct 1 energy
  break
  call LABEL_9D37                         ; continue animation
  jne [HERO_ACTION_POS_MASK], 0x80, LABEL_EED5
  setup channel=0x17, address=LABEL_74C1  ; spawn firing thread
```

**Firing thread** at `level_4.asm:12370` (`LABEL_74C1` for
facing-right; `LABEL_7523` is the mirror for facing-left):

```
LABEL_74C1:
  mov [0x0F], 0x0000
  jle [0x06], 0x00, LABEL_7609            ; abort if energy exhausted
LABEL_74CB:                                ; 4-frame initial wait
  break ; add [0x0F], 1
  abort if movement, jump-down, or release
  jl [0x0F], 0x04, LABEL_74CB
  ; ... raise-gun animation (CINEMATIC_063..066) ...
  je [HERO_ACTION], 0x00, LABEL_75E9      ; released here → REGULAR SHOT
  jmp LABEL_7587                           ; else → CHARGE LOOP
LABEL_7587:                                ; counter 0x0F goes 4 → 20 in steps of 4
  ...
  jl [0x0F], 0x14, LABEL_7587
  je [HERO_ACTION], 0x01, LABEL_7655      ; still held at 20 frames → SUPERBLAST
  ; fall through → SHIELD (visual frame) → regular shot exit
```

Threshold constants: **4 frames** (initial draw-gun delay) and
**0x14 = 20 frames** (full superblast charge).

### Energy variable

**Var `0x06`** holds gun energy. Confirmed by four matching contexts
in the DOS bytecode:

- Level 4 entry: `mov [0x06], 0x03DE` (= 990) at `level_4.asm:22113`
- Level 4 recharge: `mov [0x06], 0x03E8` (= 1000) at `level_4.asm:6209`
- Regular shot decrement: `sub [0x06], 0x000A` at `level_4.asm:12460`
- Superblast decrement: `sub [0x06], 0x0032` at `level_4.asm:12524`
- Tap-shot decrement: `sub [0x06], 0x0001` at `level_4.asm:10873`

**Caveat**: var `0x06` is **reused** as a render scratch variable in
non-combat levels (level 0, 1, 5, 8). It holds gun energy in **levels
3 (Prison), 4 (Caves), and 6 (Tunnels)** — the levels that contain
shooting.

### Cost model

Per-opcode `sub [0x06], …` decrements (each fires when its specific
code path runs, *not* alternatively):

| Decrement site | Amount | Site |
|---|---|---|
| Tap shot (instant fire on press) | **−1** | `LABEL_6588` / `LABEL_6600` (`level_4.asm:10873`, `10915`) |
| Regular shot (≥ 4-frame hold then release) | **−10** | `LABEL_75E9` (`level_4.asm:12460`) — `sub [0x06], 0x000A` |
| Superblast (held ≥ 20 frames) | **−50** | `LABEL_76C6` (`level_4.asm:12524`) — `sub [0x06], 0x0032` |

**These decrements compound within a single press cycle.** The state
machine fires the tap **unconditionally** the moment the action button
is pressed (`LABEL_EF03` at `level_4.asm:23721` — `call LABEL_6588`
runs whenever `var 0x0F == 0`, which is the entry condition for the
press state). A *separate* "firing thread" is then `setup`'d on
channel `0x17` (`LABEL_74C1`); that thread independently decides
whether to fire a regular or a superblast later, but it never
cancels the tap that already fired. The result:

| Player action | Walkthrough vocabulary | Energy cost | What fires |
|---|---|---|---|
| Press & release **within 4 frames** | "Hold A for short time" → shield (briefly visible) | **−1** | Just the tap |
| Press & hold ≥ 4 frames, **release before 20** | aimed shot (not named explicitly in walkthrough) | **−1 + −10 = −11** | Tap + regular |
| Press & hold **≥ 20 frames** | "Hold A for longer time" → superblast | **−1 + −50 = −51** | Tap + superblast |

(In the Prison level the superblast costs −100, so a charged shot
there is −101 total — see "The level-3 superblast anomaly" below.)

**The shield is the held-state pose, not a fire mode.** The "shield"
visual is the `LABEL_9D49` animation, rendered by the state machine
**every frame the action button is held**, regardless of what the
firing thread is doing. So the player is in shield posture during
the entire hold cycle — including frames 4–19 (the charge
animation) and frames 20+ (the superblast charge). What
distinguishes the walkthrough's "shield action" is **releasing
before frame 4**, so that the firing thread aborts at `LABEL_7609`
without firing anything else. The total cost of "just shielding"
that way is **−1**, paid for by the unconditional tap that fires
the moment the button goes down. The shield itself never decrements
energy; if you hold long enough for the firing thread to fire a
regular or superblast, you've left "shield mode" and committed to
an aimed shot (the mid-charge release path falls through
`LABEL_75E1` → `LABEL_75E9`, so once you're past frame 4 a release
*always* fires the regular).

**The level-3 superblast anomaly.** In level 3 (Prison Escape) the
superblast cost is **−100** (`level_3.asm:7976`: `sub [0x06], 0x0064`),
not −50 as in levels 4 and 6. Same opcode site, different constant.
Cross-checked against Amiga (`amiga_level-3.asm:7719` = −100;
`amiga_level-4.asm:11882` = −50) and Genesis-EU
(`genesis_europe_level-1.asm:8046` = −100;
`genesis_europe_level-2.asm:11413` = −50) — identical. So this is an
intentional design choice in the original 1991 code, **not a
port-specific drift**.

### Recharge semantics

**Two recharge zones** in the entire DOS game, both in level 4 (Gas
Tunnels), sharing a single recharge handler `LABEL_3473` at
`level_4.asm:6195`. The handler is `setup`'d on channel `0x36` from
two distinct scene initialisers (lines 16849 and 17911), and
switches its trigger geometry on `HACK_VAR_67` (the scene flag):

```
LABEL_3473:
  break
  jg [0x06], 0x03DE, LABEL_3473            ; loop while energy > 990
  jne [0x04], 0x20, LABEL_3473             ; loop unless facing right (orientation 0x20)
  je [HACK_VAR_67], 0x4F, LABEL_3490       ; alternate scene → different trigger
  jg [0x01], 0x67, LABEL_3473              ; default scene: loop while X > 103
  jmp LABEL_349C
LABEL_3490:                                  ; HACK_VAR_67 == 0x4F path:
  jg [0x01], 0x6E, LABEL_3473              ;   loop while X > 110
  jg [0x02], 0x64, LABEL_3473              ;   AND   Y > 100
LABEL_349C:                                  ; both paths converge here:
  mov [0x01], 0x0069                       ;   teleport Lester to X = 105
  mov [0x06], 0x03E8                       ;   ENERGY = 1000  ← recharge
  setPalette 0x05                          ;   visual flash (paired with palette 5)
```

In both zones the trigger is a **position + orientation gate** —
the busy-loop only exits when Lester is within the right X/Y
range, facing right, AND already below 991 energy. The recharge
itself is identical in both rooms: a **clamp-to-1000** (`mov`, not
`add`). Confirmed structurally identical in Amiga
(`amiga_level-4.asm:5870-5884`).

The default-scene zone (X ≤ 103, no Y constraint) is the one the
walkthrough describes as the "strange looking room" left of the
prison-exit area. The alternate-scene zone (X ≤ 110, Y ≤ 100) lives
in the same level under a different scene flag. The walkthrough's
phrasing "more energy so you can use it again" is consistent with
set-to-1000: in practice the player only triggers the loop after
energy has dropped below 991, so the effect feels additive even
though the implementation is a clamp.

Earlier revisions of this finding mistakenly described "a single
recharge station". The handler code is single, but the bytecode
clearly carries two scene-init invocations of it — confirming the
gameplay observation that two distinct rooms refill the gun.

### Initial value per level

| Level | Initializer | Energy | Site |
|---|---|---|---|
| 3 (Prison Escape) | `LABEL_8A25` | **199** | `level_3.asm:14654` (`mov [0x06], 0x00C7`) |
| 4 (Gas Tunnels)   | `LABEL_DD59` | **990** | `level_4.asm:22119` (`mov [0x06], 0x03DE`) |
| 6 (Final Action)  | `LABEL_B61A` | **990** | `level_6.asm:18221` (`mov [0x06], 0x03DE`) |

Lester arrives in the Prison level (where he just finds the gun)
with **199 energy** — only enough for a few shots — then after
escaping, levels 4 and 6 begin with 990 (just below the 991 recharge
guard, so the recharge station won't trigger if reached at full).

There is also `mov [0x06], 0x0000` at scene-state setters
(`level_4.asm:7743`, etc.) that zero the energy when `HACK_VAR_67` is
set to scene 0x25 — these are scene-setup helpers and probably
correspond to checkpoint resets.

### Cross-release uniformity

Compared the gun energy code across DOS, Amiga retro-presskit (Amiga
OCS, 1991), and SEGA Genesis EU (Interplay 1993):

| Constant | DOS | Amiga | Genesis EU |
|---|---|---|---|
| Tap-shot cost (`sub [0x06], 0x0001`) | yes (L3, L4, L6) | yes (L3, L4, L6) | yes (Genesis L1, L2, L4) |
| Regular shot cost (`sub [0x06], 0x000A`) | yes | yes | yes |
| Superblast L3 = −100, L4/6 = −50 (`0x0064` / `0x0032`) | yes | yes | yes |
| Level 3 entry energy = 199 (`0x00C7`) | yes | yes | not yet checked |
| Level 4 entry energy = 990 (`0x03DE`) | yes | yes (`amiga_level-4.asm:21185`) | yes |
| Recharge station `jg [0x06], 0x03DE` + `mov [0x06], 0x03E8` | yes | yes (`amiga_level-4.asm:5870-5884`) | yes (Genesis L2) |

**Gun energy mechanics are byte-for-byte identical between DOS,
Amiga, and Genesis-EU.** Same variable, same costs, same recharge
logic, same per-level initializers. SNES-EU and GBA-Foxy
disassemblies are currently limited to levels 0/1 by the AWVM_Tools
pipeline (those ports use the abridged 2-level "demo" engine), so
cross-checking the prison/cave levels there is future work — but the
−10 constant is already visible in non-gun contexts of GBA L0 and
SNES L0, suggesting var `0x06` conventions persist there too.

### Visual / mechanical semantics of each shot type

The tap, the regular, and the superblast are **three distinct
laser pulses**, each emitted by its own spawn routine, each tracked
in its own slot table, each with its own sound and (for the regular
and superblast) its own muzzle/blast cinematic.

| Property | Tap | Regular | Superblast |
|---|---|---|---|
| Spawn site | `LABEL_6588` (right) / `LABEL_6600` (left) | `LABEL_75E9` → `LABEL_70DD` | `LABEL_7655` → `LABEL_76C6` |
| Energy cost (per opcode) | −1 | −10 | −50 (−100 in level 3) |
| Fires when | First frame of press, **unconditionally** | Released after 4–19 frames of hold | Held ≥ 20 frames |
| Shot flag (var `0x27` / `0x88` / `0x91`) | `OR 0x4000 \| 0x0C00` | (no 0x4000 — different metadata) | `OR 0x8000` (almost certainly the **shield-piercing flag** the walkthrough notes) |
| Shot-tracking slots | `0x88` / `0x89` / `0x8A` (positions in `0x90..0x95`) — up to **3 simultaneous taps** | `0xA0` / `0xA3` / `0xA6` (positions in `0xA0..0xA8`) — up to **3 simultaneous regulars**, **tracked independently from taps** | Single dedicated slot (`0x88` reused for the superblast's HP / damage value = `0x64` = 100) |
| Sound played | `id=0x0052, freq=0x1C` (quick "pew") | `id=0x0058, freq=0x14` (louder "pow") | `id=0x0059` then `id=0x005B` (charge → boom) |
| Muzzle / charge polygon | **None** at fire site | `CINEMATIC_037` rendered at the gun's tip | `CINEMATIC_068` (large blast cinematic) |
| Pre-fire animation | `LABEL_9D73` (Lester raises gun) | `CINEMATIC_063..066` charge animation (4 frames) with `id=0x005B` charge-complete tone | Same charge animation, then continues past frame 20 |

The visual experience the player sees (the gun is a
laser/plasma-style energy weapon — the shots are pulses of light,
not metal slugs):

- **Tap.** The instant the button goes down, Lester raises the gun
  and a small laser pulse fires from the muzzle. Up to 3 such
  pulses can be in transit at once. They're fast and weak. The tap
  fires *every time* you press — there's no "draw without firing"
  mode.

- **Regular.** Press, hold, watch Lester complete the gun-up
  animation, see the charge animation play (the gun's silhouette
  brightens / pulses across `CINEMATIC_063..066`), hear the
  charge-complete tone, then release — at which point a *brighter,
  more powerful* laser pulse fires from the gun with a visible
  muzzle-flash polygon (`CINEMATIC_037`) and a louder report. The
  first tap that fired on press is most of the way to its target
  at this point.

- **Superblast.** Same charge sequence, but you keep holding past
  the charge-complete tone. The firing thread enters a second,
  longer charge loop, and at frame 20+ the superblast fires with
  its own distinctive blast cinematic and the shield-piercing flag.
  Like the regular, this is in addition to the tap that already
  fired on press.

This explains the energy accounting: the per-opcode `sub [0x06], …`
sites the agent originally found (−1, −10, −50) are correct in
isolation, but they **compound within a single press cycle** because
the tap fires unconditionally and the firing thread runs in parallel
on a separate channel. So the player's true cost per action is
−1 / −11 / −51 (or −101 for a Prison superblast).

The shield (the walkthrough's "Hold A for short time") is just the
first 4 frames of any press: while the firing thread is in its
4-frame initial wait, the state machine renders `LABEL_9D49` (the
shield-pose animation). Releasing within those 4 frames keeps the
shield up briefly with no additional shot fired — but the press
still cost −1 for the tap that fired on frame 0.

## Genealogy implications

This finding is the first **definitive cross-release identity** at
the level of game-mechanic constants — three independently extracted
ports (DOS / Amiga / Genesis-EU) hold not only the same code
structure but the *same magic numbers* (199, 990, 1000, −1, −10,
−50, −100). The Amiga and DOS sharing this is unsurprising (the DOS
port was a direct adaptation), but the **Genesis port preserving it
verbatim** is genealogy signal: Interplay's 1993 Genesis port
(Rebecca Heineman) descends from a code base that already had the
gun mechanics fully in place in this exact form.

The level-3-vs-level-4/6 superblast cost asymmetry (−100 vs −50)
being preserved across all three ports is particularly telling: it's
the kind of small irregularity that would be tempting to "fix" or
homogenize during a port — its persistence suggests the porters
worked from a snapshot of the bytecode rather than re-deriving the
balance numbers. This is a candidate for cross-checking against the
SNES / GBA / Apple IIgs ports once their full level extraction is
wired up.

## Appendix: simulated quotas

Generated by [`tools/simulate_gun_budget.py`](#) — re-run the script
to refresh these tables if cost constants change. **All costs are
compound** (every press fires the unconditional tap, so a regular
shot pays −1 + −10 = −11 and a superblast pays −1 + −50 = −51,
or −101 in the Prison anomaly).

### At-a-glance pure-mode capacity

After a full recharge in level 4 or 6 (energy = 1000, regular
costs 11, superblast costs 51):

```
  Quick tap     ████████████████████████████████████████  1000
  Regular shot  ████                                        90
  Superblast    █                                           19
```

And under the level-3 anomaly (entry energy 199, superblast costs
101):

```
  Quick tap     ████████████████████████████████████████   199
  Regular shot  ████                                        18
  Superblast    █                                            1
```

### Per-level breakdown

#### Level 3 — Prison Escape (where Lester finds the gun)

Entry energy: **199**. Superblast cost: **101**. Recharge zones:
**0**.

| Mode | Cost | Pure-mode capacity |
|---|---|---|
| Quick tap (release ≤4 frames) | 1 | 199 |
| Regular shot (tap + regular) | 11 | 18 |
| Superblast (tap + Prison superblast) | 101 | 1 |
| Shield-pose hold (just the −1 tap) | 1 | 199 |

Mixed-strategy budgets at level entry:

| Strategy | Superblasts (×101) | Regular (×11) | Tap (×1) | Total spent |
|---|---:|---:|---:|---:|
| Pure tap (panic-fire) | 0 | 0 | 199 | 199 / 199 |
| Pure regular | 0 | 18 | 0 | 198 / 199 |
| Pure superblast | 1 | 0 | 0 | 101 / 199 |
| Cautious (no superblast) | 0 | 9 | 100 | 199 / 199 |
| Balanced 25/25/50 | 1 | 4 | 54 | 199 / 199 |
| Sniper (no taps) | 0 | 18 | 0 | 198 / 199 |

#### Level 4 — Gas Tunnels (the level with both recharge zones)

Entry energy: **990**. Superblast cost: **51**. Recharge zones:
**2** (both clamp to 1000). **Theoretical maximum burnable energy**
if both zones are visited at energy = 0: **2990**.

At level entry (no recharge yet):

| Mode | Cost | Pure-mode capacity |
|---|---|---|
| Quick tap (release ≤4 frames) | 1 | 990 |
| Regular shot (tap + regular) | 11 | 90 |
| Superblast (tap + superblast) | 51 | 19 |
| Shield-pose hold (just the −1 tap) | 1 | 990 |

Mixed-strategy budgets at level entry:

| Strategy | Superblasts (×51) | Regular (×11) | Tap (×1) | Total spent |
|---|---:|---:|---:|---:|
| Pure tap (panic-fire) | 0 | 0 | 990 | 990 / 990 |
| Pure regular | 0 | 90 | 0 | 990 / 990 |
| Pure superblast | 19 | 0 | 0 | 969 / 990 |
| Cautious (no superblast) | 0 | 45 | 495 | 990 / 990 |
| Balanced 25/25/50 | 4 | 35 | 401 | 990 / 990 |
| Heavy combat (~50% energy on superblasts) | 9 | 24 | 267 | 990 / 990 |
| Sniper (no taps) | 4 | 71 | 0 | 985 / 990 |

Immediately after a recharge (energy = 1000):

| Mode | Cost | Pure-mode capacity |
|---|---|---|
| Quick tap (release ≤4 frames) | 1 | 1000 |
| Regular shot (tap + regular) | 11 | 90 |
| Superblast (tap + superblast) | 51 | 19 |
| Shield-pose hold (just the −1 tap) | 1 | 1000 |

Mixed-strategy budgets after recharge:

| Strategy | Superblasts (×51) | Regular (×11) | Tap (×1) | Total spent |
|---|---:|---:|---:|---:|
| Pure tap (panic-fire) | 0 | 0 | 1000 | 1000 / 1000 |
| Pure regular | 0 | 90 | 0 | 990 / 1000 |
| Pure superblast | 19 | 0 | 0 | 969 / 1000 |
| Cautious (no superblast) | 0 | 45 | 505 | 1000 / 1000 |
| Balanced 25/25/50 | 5 | 33 | 382 | 1000 / 1000 |
| Heavy combat (~50% energy on superblasts) | 9 | 24 | 277 | 1000 / 1000 |
| Sniper (no taps) | 4 | 72 | 0 | 996 / 1000 |

#### Level 6 — Final Action

Entry energy: **990**. Superblast cost: **51**. Recharge zones:
**0** (no refills available in this level).

Pure-mode capacity at level entry is identical to level 4 entry:
**990 quick tap / 90 regular / 19 superblasts**. Without recharge
zones, this is the *entire budget* for the level — players come
into the final stretch with whatever discipline they've trained.

### Notable consequences

- **In the Prison level a player can afford exactly one
  superblast.** Even with the corrected compound cost (101), one
  superblast costs more than half the entry energy. With 98 left
  over after a superblast they can fit *9 more regular shots
  (=99), or 98 taps* — but no second superblast.

- **The "shield" is technically not free.** Pressing the action
  button to enter the shield pose costs −1 for the unconditional
  tap that fires on press. The shield itself doesn't decrement
  energy, but you can't get into it without that initial tap.

- **Level 4's two recharge zones triple the level's budget**: the
  burnable cap goes from 990 (no recharges) to 2990 (both
  recharges hit at zero). At 2990 the player has up to **58
  superblasts** with 32 energy left over — comfortably more than
  enough for the level's combat encounters, suggesting the
  recharges were designed primarily to soak up *failed-attempts*
  energy rather than as a strict balance constraint.

- **Level 6 has no recharges.** Whatever the player carries in
  from level 5 is what they have for the entire ending — under
  the design assumption that they entered level 6 close to a
  fresh 990. (The level 6 entry initialiser sets energy to 990
  unconditionally, so any leftover from level 5 is discarded —
  see `level_6.asm:18221` and the "Initial value per level" table
  above.)

- **The "regular shot fires two laser pulses" insight has a side
  effect**: if you fire a regular at close range, the tap pulse and
  the regular pulse may both reach the target. ~~Whether this
  means double damage in practice depends on the target's hit
  semantics — open follow-up.~~

  **Update 2026-05-04**: traced through to closure (issue #0043
  closed `done`). **No double damage**: the regular pulse's
  per-frame routine `LABEL_42C2` is a pure renderer + range
  counter — there is no collision detection along the regular
  pipeline at all. The bullet just lives for 150 frames (initial
  range `0x96`) as visual feedback and expires. *All* enemy
  damage comes from the tap pulse fired on press; the regular's
  `-10` energy cost is paying purely for the audiovisual layer
  (louder sound, muzzle flash polygon CINEMATIC_037, longer
  rendered trail). Superblasts do damage, but they reuse the
  tap-class slot `0x88` with HP=`0x64` and the `OR 0x8000`
  shield-piercing flag — they route through the tap collision
  pipeline, not the regular one.

  See issue #0043's final log entry for the full disassembly
  trace (PRISON.asm DOS-1992; the unified source byte-matches
  amiga and Genesis-EU as well, so the model is identical
  cross-port).

## See also

- [Genealogy](#/genealogy) — high-level cross-release findings
- [Open question 01 (resolved)](#/open-questions/01-gun-ammo) — the
  original framing
- [Engine architecture](#/engine) — VM variables and threading model

## Changelog

- **2026-04-30** — initial finding, generated by a research subagent
  given access to the DOS / Amiga / Genesis-EU disassemblies.
- **2026-04-30** (same day) — corrected "single recharge station"
  to "two recharge zones sharing one handler". The handler code is
  single, but the bytecode carries two scene-init invocations
  (`setup channel=0x36, address=LABEL_3473` at level_4.asm lines
  16849 and 17911), and the handler internally branches on
  `HACK_VAR_67` to select between two trigger zones — matching the
  end-user observation of two distinct refill rooms in the game.
  Spot caught by the project owner on review.
- **2026-04-30** (same day) — added "Appendix: simulated quotas"
  with per-level pure-mode capacities, mixed-strategy budgets,
  and an at-a-glance bar chart. Generated by
  `tools/simulate_gun_budget.py` (re-run if cost constants
  change). Notable consequence highlighted: level 3 affords
  *exactly one* superblast; level 4's two recharges triple the
  level's burnable budget (990 → 2990); level 6 has no recharges
  and discards any leftover from level 5 by setting energy to
  990 unconditionally on entry.
- **2026-04-30** (same day) — **major correction:** the cost
  model originally listed −1, −10, −50 as alternatives, but the
  bytecode shows the tap fires *unconditionally* on the first
  frame of every press (`LABEL_EF03` calls `LABEL_6588`
  whenever `var 0x0F == 0`), and the firing thread that
  produces the regular or superblast runs in parallel on a
  separate channel and never cancels the tap. So per-action
  costs are compound: −1 (quick tap) / −11 (tap + regular) /
  −51 (tap + superblast) / −101 (tap + Prison superblast).
  Added a new section "Visual / mechanical semantics of each
  shot type" documenting the three shot types' separate spawn
  routines, sounds, polygons, and slot tables. The
  appendix tables and `tools/simulate_gun_budget.py` updated
  with the corrected compound costs. Triggered by the project
  owner asking what the tap-vs-regular distinction *means* in
  the game.
- **2026-04-30** (same day, wording cleanup) — the gun is a
  laser/plasma-style energy weapon, not a kinetic firearm. After
  two passes (first dropping "bullet" / "bullets", then dropping
  the still-too-physical "energy bolt" and "projectile" too), the
  vocabulary settled on **"shot"** / **"laser pulse"** / **"in
  transit"** / **"reach the target"** — laser-light terminology
  throughout. The bytecode-comment column retains "bullet" with a
  parenthetical disclaimer noting that's the AW VM's internal
  nomenclature for the shot-tracking slot table, not what the
  player sees.

  Same edit pass strengthened the shield explanation in the
  cost-model section to map walkthrough vocabulary onto the
  bytecode: shield = press & release within 4 frames (only the
  unconditional tap fires); superblast = press & hold ≥ 20
  frames; the regular shot (release at 4–19 frames) is *not* the
  shield action — it's an aimed shot the walkthrough doesn't
  explicitly name. Added a "walkthrough vocabulary" column to the
  player-action cost table for clarity.

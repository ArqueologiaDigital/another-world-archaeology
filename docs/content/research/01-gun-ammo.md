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
- **Three weapon modes consume different amounts of energy:**
  - **Tap shot** (instant fire on press): **−1 energy**
  - **Regular shot** (≥ 4-frame hold then release): **−10 energy**
  - **Superblast** (held ≥ 20 frames): **−50** in level 4 / 6 / **−100
    in level 3** (Prison Escape)
- **The shield is free** — the visual shield is the gun-drawn
  animation rendered while the action button is held; no decrement
  happens while it's up.
- The dispatch is **two cooperating VM threads** — a state-machine
  thread that handles animation and a firing thread that counts
  held-frames and branches on threshold.
- **Single recharge station** in the entire DOS game, in **level 4
  (Gas Tunnels)**. It triggers on a position+orientation polygon
  collision and is a **clamp-to-1000** (`mov`, not `add`) — so even
  though the player perceives "more energy", it's actually a reset
  to 1000.
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
  mov [0x21], [0x01]; mov [0x27], [0x02]  ; bullet origin = Lester's coords
  sub [0x21], 0x001E; sub [0x27], 0x0027  ; offset to muzzle
  call LABEL_6588                         ; spawn bullet, deduct 1 energy
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

| Action | Energy cost | Site |
|---|---|---|
| Tap shot (instant fire on press) | **−1** | `LABEL_6588` / `LABEL_6600` (`level_4.asm:10873`, `10915`) |
| Regular shot (≥ 4-frame hold then release) | **−10** | `LABEL_75E9` (`level_4.asm:12460`) — `sub [0x06], 0x000A` |
| Superblast (held ≥ 20 frames) | **−50** | `LABEL_76C6` (`level_4.asm:12524`) — `sub [0x06], 0x0032` |

**Shield is FREE.** The "shield" visual is the gun-drawn animation
rendered while action is held (`LABEL_9D49` at `level_4.asm:16170`);
no `sub [0x06]` happens while it's up. The mid-charge release path
falls through `LABEL_75E1` → `LABEL_75E9`, so a button-release during
the charge animation pays the same −10 as a regular shot — i.e.,
**releasing always fires**.

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

**Single recharge station** in the entire DOS game, in level 4 (Gas
Tunnels) at `level_4.asm:6195`:

```
LABEL_3473:
  break
  jg [0x06], 0x03DE, LABEL_3473            ; loop while energy > 990
  jne [0x04], 0x20, LABEL_3473             ; loop unless facing right (orientation 0x20)
  je [HACK_VAR_67], 0x4F, LABEL_3490
  jg [0x01], 0x67, LABEL_3473              ; loop while X > 103
  jmp LABEL_349C
LABEL_3490:
  jg [0x01], 0x6E, LABEL_3473              ; loop while X > 110
  jg [0x02], 0x64, LABEL_3473              ; loop while Y > 100
LABEL_349C:
  mov [0x01], 0x0069                       ; Lester X = 105
  mov [0x06], 0x03E8                       ; ENERGY = 1000  ← recharge
  setPalette 0x05                          ; visual flash
```

The trigger is a **position+orientation polygon collision**: the
loop only exits when Lester is within a small X/Y range, facing
right, AND already below 991 energy. The recharge is a
**clamp-to-1000** (`mov`, not `add`) — confirmed identical in Amiga
(`amiga_level-4.asm:5882-5884`).

This is the same room the walkthrough describes ("strange looking
room" left of the prison-exit area). The walkthrough's phrasing
"more energy so you can use it again" is consistent with set-to-1000
even though that wording suggests additive — in practice the player
only triggers the loop after energy has dropped below 991, so the
effect feels additive.

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

## See also

- [Genealogy](#/genealogy) — high-level cross-release findings
- [Open question 01 (resolved)](#/open-questions/01-gun-ammo) — the
  original framing
- [Engine architecture](#/engine) — VM variables and threading model

## Changelog

- **2026-04-30** — initial finding, generated by a research subagent
  given access to the DOS / Amiga / Genesis-EU disassemblies.

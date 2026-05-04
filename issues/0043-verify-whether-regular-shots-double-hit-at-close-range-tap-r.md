---
id: 0043
title: Verify whether regular shots double-hit at close range (tap pulse + regular pulse)
status: done
tier: A
created: 2026-04-30
updated: 2026-05-04
depends_on: []
blocks: []
tags: [research, gun-ammo, dos, follow-up]
---

# Context

The 2026-04-30 correction to research/01-gun-ammo established that
every press cycle fires *two* laser pulses when held long enough
for a regular shot:

1. The unconditional **tap pulse** (small shot, tracked in slots
   0x88/89/8A with positions in 0x90..0x95, metadata
   `OR 0x4000 | 0x0C00`) — fires on the first frame of the press.
2. The **regular pulse** (larger shot, tracked in slots 0xA0/A3/A6
   with positions in 0xA0..0xA8, muzzle-flash polygon
   CINEMATIC_037) — fires when the action button is released after
   holding 4–19 frames.

Both are in transit at the same time, with the regular trailing
the tap by ~8–24 frames. At close range the two pulses may both
reach a single target — open question whether this means *double
damage*, or whether the engine's hit-detection de-duplicates them,
or whether they hit different targets in practice.

# Acceptance criteria

- [ ] Locate the shot collision-detection code in the disassembly
      (the per-frame update for slots 0x88..0x8A and 0xA0..0xA8).
- [ ] Determine whether the tap pulse's hit-on-target decrements
      an enemy's HP separately from the regular pulse's.
- [ ] If yes: document the close-range double-damage exploit (or
      intended behaviour) as a note in research/01-gun-ammo.md.
- [ ] If no: identify the de-duplication mechanism (kill-flag,
      shared HP register, etc.).
- [ ] Cross-check: same behaviour on Amiga and Genesis-EU?

# Log

- 2026-04-30: opened. Surfaced from the gun-ammo cost-model
  correction; flagged as "open follow-up" in research/01's
  appendix.

- 2026-05-04: partial trace of `PRISON.asm` (DOS 1992). Located the
  shot pipeline; key labels:

  - **Lester's tap-pulse spawn** at `LABEL_3801` — `-1` energy, sound
    `0x0052 ch=0`, writes pos/metadata into first free of slots
    `0x88/0x89/0x8A`.
  - **Guards' tap-pulse spawn** at `LABEL_37A6` — `0x0052 ch=1`,
    slots `0x8B/0x8C/0x8D`. (Newly identified — the collision
    dispatcher's "second loop" is *guard fire*, not a second
    Lester-shot type as could have been guessed from the 0x29 flag.)
  - **Lester's regular-pulse spawn** at `LABEL_45CB` — `-10` energy,
    sound `0x0058 ch=0`, calls `LABEL_4185` to write into first free
    of slots `0xA0/0xA3/0xA6` (not 0xA9/0xAC).
  - **Guards' regular-pulse spawn** at `LABEL_4137` — same sound
    `0x0058 ch=1`, slots `0xA9/0xAC`. Owner-id from `[0x10]`.
  - **Superblast spawn** at `LABEL_4662` — `-100` energy, **reuses**
    slot `0x88` with HP value `0x64` (=100) and `OR 0x8000` flag.
    Confirms research/01's claim that superblast piggybacks on the
    tap-class slot.

- The per-frame **tap-pulse update + collision** lives at
  `LABEL_3869` (Lester, `[0x29]:=0`) and `LABEL_38CA` (guards,
  `[0x29]:=1`). Both call `LABEL_3991` per slot. `LABEL_3991`
  advances the bullet (`[0x21] += 0x28` first frame, `+= [0x11]+0x3C`
  thereafter) and calls `LABEL_468E` for collision. If `[0x1D]≠0`
  after the collision call, the shot is fizzled via `LABEL_3BB3`.

- The per-frame **regular-pulse update** lives at `LABEL_4245`,
  iterating slots `0xA0/A3/A6/A9/AC` and calling `LABEL_42C2`.
  **Crucially, `LABEL_42C2` does NOT call `LABEL_468E` or any
  collision routine** — it only renders the bullet trail
  (CINEMATIC_201 / 522..533) and decrements range. This means
  regular pulses do *not* run their own per-frame hit-detection
  through the same collision path as taps.

- The collision routine at `LABEL_468E` calls `LABEL_4717` (broad
  phase: scans all 5 regular-shot slots `0xA0..0xAC`, tags hits
  on Lester-owned slots with tags `0x14..0x18` — these are
  *bullet-vs-bullet collisions*, where a tap intercepts a regular
  in flight, not a tap-on-actor hit) and then dispatches by
  `[0x29]`:
  - `[0x29]==0` (Lester's tap path) → `LABEL_477E` tests slots B/C
    (`0x70/72`, `0x78/7A`) for guard hits, tagging `0x29`/`0x2A`.
  - `[0x29]==1` (guards' tap path) → `LABEL_46E8` tests slot A
    (`0x68/6A` = Lester) for actor hit, tagging `0x28`.

- Tag dispatch in `LABEL_3A0D`:
  - `0x14..0x18` → `LABEL_3A4A` plays sound `0x005C` (deflection)
  - `0x1E` → `LABEL_3A68` (hit Lester via separate path)
  - `0x28` → `LABEL_3AAD` ch=`0x23` (Lester death)
  - `0x29` → `LABEL_3AAD` ch=`0x25` (slot-B guard death)
  - `0x2A` → `LABEL_3AAD` ch=`0x27` (slot-C guard death)

- **Open**: where exactly does Lester's *regular pulse* damage
  guards? `LABEL_42C2` only renders. Hypothesis still being
  validated: either (a) the regular pulse setup also writes a
  twin tap-class slot (no evidence yet), or (b) the broad-phase
  in `LABEL_4717` is bidirectional — when the slot's bullet
  trajectory crosses a guard's hitbox, it tags the *guard*'s
  slot for damage rather than the bullet's slot. The tag
  semantics in `LABEL_47AB` need a more careful trace
  (the `jne [HACK_VAR_67], [0x26]` gate at `LABEL_47BE` reads
  like "skip unless this slot is Lester-owned" — surprising and
  worth re-verifying).

- **Cross-port comparison still TODO** (Amiga, Genesis-EU). Until
  the DOS path itself is fully understood the comparison is
  premature.

- Remaining acceptance criteria not yet satisfied; closing
  blocked on the open hypothesis above.

- 2026-05-04 (final): traced the rest of the pipeline. **The
  regular pulse does not run collision detection at all** — the
  per-frame regular routine `LABEL_42C2` is purely a renderer
  + range-counter:

      LABEL_42C2:
          mov [0x26], [0x40]        ; depth selector
          jge [0x27], 0x00, LABEL_42D2
          sub [0x27], 0x8000
          mov [0x26], [0x44]
      LABEL_42D2:
          jne [0x27], [HACK_VAR_67], LABEL_431B  ; non-Lester → just decrement
          ...renders CINEMATIC_201/520..533 based on range bucket...
      LABEL_431B:
          sub [0x22], 0x0001         ; range -= 1
          ret

  Range starts at 0x96 (150 frames) per `LABEL_4185`'s spawn:
  `mov [0x22], 0x0096`. After 150 frames the slot's range field
  goes negative and the outer iterator `LABEL_4245` skips it. So
  Lester's regular pulse simply lives for 150 frames as visual
  feedback and then expires.

  **Where does the actor-damage actually happen, then?** Only the
  tap-pulse loop (`LABEL_3869`/`LABEL_38CA` → `LABEL_3991` →
  `LABEL_468E`) runs collision. The press-fire sequence at
  `PRISON.asm:15646` proves this:

      sub [0x21], 0x001E
      sub [0x27], 0x0027
      call LABEL_3795             ; <-- tap fires on press (left dir)
      break
      add [0x01], 0x0001
      video offset=CINEMATIC_558  ; gun-up animation
      add [0x01], 0x0001
      jne [HERO_ACTION_POS_MASK], 0x80, LABEL_944F
      setup channel=0x17, address=LABEL_44AF   ; <-- if held, schedule regular
                                               ; on side channel 0x17

  The TAP fires immediately on press via `LABEL_3795` (left) /
  `LABEL_3801` (right). Channel 0x17 is then conditionally given
  `LABEL_44AF` which waits 4 frames, plays the charge animation,
  and on action-release calls `LABEL_45CB` → `LABEL_4185`
  (regular spawn). No additional tap is fired by the regular
  path; no collision routine is wired up for the regular slots.

  ## Answer to the issue

  **There is no double-damage**. The regular pulse never makes
  contact with enemies. Per press cycle, only the tap pulse is
  responsible for damaging enemies (in PRISON: tag 0x29/0x2A via
  `LABEL_477E` → `LABEL_4810` → `LABEL_3AAD` death-channel
  setup). The regular pulse is **purely audiovisual**: louder
  sound (`0x0058`), muzzle flash (CINEMATIC_037), longer
  rendered trail. Its `-10` energy cost is paying for that
  visual indulgence, not extra damage.

  This also corrects research/01's appendix wording. The line
  beginning "if you fire a regular at close range, the tap pulse
  and the regular pulse may both reach the target" is wrong —
  only the tap reaches anything. (Updating research/01 to match
  in a follow-up commit.)

  ## What about the superblast?

  The superblast (held ≥ 20 frames) does damage, but it does so
  by **reusing slot 0x88** (a tap-class slot) with HP encoded as
  `0x64` (=100) plus the `OR 0x8000` shield-piercing flag — see
  `LABEL_4662` in PRISON.asm. So the superblast also routes
  through the tap collision pipeline; only its in-flight HP
  value differs.

  ## Cross-port

  PRISON.asm.in (the unified source) byte-matches simultaneously
  for chahi_amiga_1991, dos_1992, and cartridge_1992 (msdos +
  amiga + genesis_europe verifies all OK), so the same model
  applies on amiga and Genesis-EU.

  Closing as `done` with the corrected mental model. Following
  up with a research/01 wording fix in a separate commit.

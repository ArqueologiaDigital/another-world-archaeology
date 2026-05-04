# 18 — Setup-then-overwrite gate inventory (4 ports × 9 stages)

Static survey of the AW VM's setup-overwrite gate idiom across
every port and stage. Generalises research/05's beetle-stage
finding to the whole game.

## Method

Two consecutive `setup channel=N, address=X` opcodes in the
**same straight-line block** (no `break`/`ret`/`killChannel`/
`bankSwitch`/`freezeChannel`/`jmp`/label/`;@if` between) cause
the second to override the first. The engine's per-tick
channel-queue retains only the most-recent setup before
processing — so the FIRST setup's target is unreachable under
runtime semantics, even though static control-flow has an edge
to it.

`tools/detect_setup_gates.py` scans every per-branch `.asm`
file, splits at block boundaries, and reports each consecutive
`setup ch=N` pair where the addresses differ. Output:
`docs/setup_gate_inventory.{json,md}`.

## Cross-port counts (per stage)

| Stage | cart 1992 | amiga 1991 | dos 1992 | gba 2004 |
| --- | ---: | ---: | ---: | ---: |
| LAKE | 2 | **1** | 2 | 2 |
| CAPSULE | 4 | 1 | 4 | — |
| CAVES | 2 | 2 | 2 | — |

Em-dashes mean the port doesn't ship that stage (or the stage
has zero gates after the conditional-`je` fix). The cart 1992
column covers both SNES-EU and Genesis-EU (they share
byte-identical bytecode per research/07).

**Total: 22 gates surfaced** across the four-port × three-stage
matrix. After the conditional-`je` block-end fix, most stages
have zero gates and LAKE drops to 1 (amiga) / 2 (others).
**All 7 silencers are in LAKE.**

## Headline findings

### Category breakdown

`tools/detect_setup_gates.py` classifies each gate by what it
gates against:

| Category | Count | Description |
| --- | ---: | --- |
| **silencer** | 7 | substantive routine → killer (the gated routine never runs — deliberate cut-content per research/05) |
| reschedule | 0 | killer → substantive (none found — the game uses kill as a tear-down, not as a placeholder) |
| swap | 0 | substantive → substantive (changed mind; both are real game logic, only the second runs) |
| other | 15 | at least one side is a `LABEL_HHHH` placeholder; can't classify without semantic-rename |

All 7 silencers are LAKE beetle gates (the canonical
research/05 pattern, detailed below).

### Note on the conditional-`je` pattern (false-positive avoided)

An earlier version of the detector treated only `break`,
`ret`, `killChannel`, `bankSwitch`, `freezeChannel`, and `jmp`
as block-end. That mis-classified PRISON's
"play-once-via-VAR_B4-flag" pattern as 9 cut-content
silencers:

```
setup channel=0x01, address=INIT_VARS_E7_E8           ; start E7/E8 anim
je [0xB4], 0x00, LABEL_8592                            ; if first visit, skip silence
setup channel=0x01, address=KILL_CHANNEL_LANDING      ; otherwise silence
LABEL_8592:
    ...
```

Because `je`/`jne`/`jg`/`jge`/`jl`/`jle`/`djnz` are
conditional, the second setup is reachable only on the
fall-through path; the taken-jump path skips it. The first
setup CAN run on the taken-jump path. Treating the conditional
as block-end means the detector no longer flags this idiom as
a gate. Updated detector (commit landing this update): 22
total gates, 7 silencers, all in LAKE.

The PRISON `[0xE7]/[0xE8]/[0xE9]` routines turned out to be a
"play this animation only on first visit" feature: VAR_B4 is
initialised to 0, the animation loop sets it to 1 when it
finishes, and subsequent visits silence the loop start. Real
shipped feature, not cut content. Useful reminder that gate
detection without control-flow analysis can over-report.

### Amiga 1991 LAKE has ONE FEWER gate than later ports

Amiga LAKE: 5 gates. Cart/DOS/GBA LAKE: 7. The missing two are
the canonical research/05 cases:

| Gated → Surviving | amiga | cart | dos | gba |
| --- | :---: | :---: | :---: | :---: |
| `BEETLE_INIT_POS_THEN_WALK_LEFT` → `KILL_CHANNEL_ROUTINE` | ❌ | ✅ | ✅ | ✅ |
| `BEETLE_KICK_DETECTOR` → `WAIT_FOR_BEETLE_OFFSCREEN_THEN_KILL` | ✅ | ✅ | ✅ | ✅ |

(Plus a second occurrence of each in the same block, hence
the 2× difference.)

So:

- **amiga 1991**: kick-detector silenced, but the beetle ITSELF
  still runs (walks across the screen). This matches the
  prior-finding observation that amiga's beetle is visible but
  harmless — it crosses the scene, never kicks Lester.
- **cart / dos / gba**: BOTH the beetle and the kick-detector
  are silenced. The beetle never appears at all on these ports.

This is exactly the cut-content shape research/05 documented
qualitatively. The static gate inventory now confirms it
quantitatively across the full bytecode.

### Other stages have many gates, mostly equal across ports

CAVES, PRISON, CAPSULE all have 11-22 gates per port, with cart
and dos tracking each other within ±2. Most are routine
"reschedule channel mid-routine" patterns rather than
deliberate cut-content silencers. Distinguishing the two
requires looking at WHAT'S being gated:

- If the gated address is `KILL_CHANNEL_ROUTINE`, that's a
  rescheduling (the routine kills self after running, then the
  channel gets a new routine). 
- If the gated address is a substantive routine (DRAW_*,
  HERO_*, BEAST_*, etc.) and the surviving address is
  `KILL_CHANNEL_ROUTINE`, that's a *silencer* — the
  substantive routine never runs.
- If both are substantive routines, it's a "we changed our
  mind" pattern — both look like real game logic, but only the
  second runs.

A complete reachability oracle (#0058) would walk the
control-flow graph from every entry point, marking each gate's
*gated_address* unreachable iff no other control-flow path
reaches it. This first-pass detector flags every gate
candidate; classification into the three categories above is
follow-up.

### GBA's only gates are in LAKE

GBA-2004 only ships INTRO and LAKE. The 7 LAKE gates match
cart/dos. INTRO has 0 gates on every port — the opening scene
is purely linear scheduling.

## Reproducing

```bash
python3 tools/detect_setup_gates.py
# wrote docs/setup_gate_inventory.json (machine)
# wrote docs/setup_gate_inventory.md   (per-branch tables)
#   181 gates across 4 branches
```

## Implications for the asset-scan family (#0054–#0057)

The unused-asset scanners currently classify a polygon, sound,
music, or palette as "used" if any reachable bytecode references
it. With the gate inventory in hand:

- A reference inside a *gated* routine (one that the
  setup-then-overwrite idiom blocks from running) should NOT
  count as "used" — that reference is dead.
- The gate inventory's gated-address list is the input to a
  reachability filter that the asset scanners can apply.

#0058 tracks the full reachability oracle that wires this up
end-to-end. This research note + the gate inventory are the
foundation.

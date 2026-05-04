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
| LAKE | 7 | **5** | 7 | 7 |
| PRISON | 12 | 15 | 15 | — |
| CAVES | 22 | 21 | 22 | — |
| CAPSULE | 16 | 11 | 17 | — |
| TANK | 1 | — | 1 | — |
| CODE_WHEEL | — | 1 | 1 | — |

Em-dashes mean the port doesn't ship that stage. The cart 1992
column covers both SNES-EU and Genesis-EU (they share
byte-identical bytecode per research/07).

**Total: 181 gates surfaced across the four-port × seven-stage
matrix.**

## Headline findings

### Category breakdown

`tools/detect_setup_gates.py` classifies each gate by what it
gates against:

| Category | Count | Description |
| --- | ---: | --- |
| **silencer** | 16 | substantive routine → killer (the surviving routine kills the channel, possibly after a delay; the gated routine never runs — likely deliberate cut-content) |
| reschedule | 0 | killer → substantive (none found — the game uses kill as a tear-down, not as a placeholder) |
| swap | 24 | substantive → substantive (changed mind; both are real game logic, only the second runs) |
| other | 141 | at least one side is a `LABEL_HHHH` placeholder; can't classify without semantic-rename |

The **silencers are the highest-interest cases**. Of the 16:

  - 7 are LAKE beetle gates (the canonical research/05 pattern,
    detailed below).
  - **9 are PRISON variable-init silencers** that no prior
    research note has called out:

| Channel | Gated routine | Surviving | Cart | Amiga | DOS |
| :---: | --- | --- | :---: | :---: | :---: |
| `0x01` | `INIT_VARS_E7_E8` | `KILL_CHANNEL_LANDING` | ✅ | ✅ | ✅ |
| `0x02` | `INLINE_SET_VARE9_TO_8` | `KILL_CHANNEL_LANDING` | ✅ | ✅ | ✅ |
| `0x05` | `INLINE_SET_VARE7_TO_5` | `KILL_CHANNEL_LANDING` | ✅ | ✅ | ✅ |

These three silencers gate variable-initialisation routines for
vars `[0xE7]`, `[0xE8]`, `[0xE9]` — high state vars that look
like they were tracking some PRISON-specific feature
(possibly a lock count, sub-screen state, or a meta-state for
the prison-cart sequence). Three different channels (0x01,
0x02, 0x05) all set up this same way. **Same gates present on
all three pre-anniversary ports** — meaning whatever was being
silenced was cut BEFORE the port-split (i.e., during the
original 1991 amiga authoring) and persisted through the 1992
DOS / cart rebuilds. A NEW cut-content signal worth following
up.

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

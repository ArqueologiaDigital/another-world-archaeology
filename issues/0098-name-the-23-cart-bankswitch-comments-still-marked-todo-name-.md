---
id: 0098
title: Name the 23 cart bankSwitch comments still marked 'TODO - Name this stage'
status: open
tier: C
created: 2026-05-09
updated: 2026-05-09
depends_on: [0065]
blocks: []
tags: [reconstruction, cleanup, naming, bankswitch, awvm-tools]
---

# Context

`grep -rE 'TODO - Name this stage' src/levels/_unified/` in
source-reconstruction returns **23 occurrences** in cart-arm
chunks. Each is on a `bankSwitch N` line where the disassembler
emitted a placeholder comment instead of a stage name (e.g.
`bankSwitch 4;  TODO - Name this stage (bank number #4)`).

Per-bank distribution:

| bank | TODO count |
|------|-----------:|
| #4   | 17 |
| #5   | 3  |
| #3   | 2  |
| #2   | 1  |

Already-named cart bankSwitches (from the same grep, filtered to
non-TODO comments):

  - bank 0: "Arrival at the Lake & Beast Chase" (LAKE)
  - bank 1: "Prison"
  - bank 6: "Secret Code Entry Screen" (PASSCODE)

So banks 2, 3, 4, 5 are unnamed in cart. To close this issue:

1. Determine what stage cart's `bankSwitch 2/3/4/5` switches to.
   The AWVM_Tools `releases/snes.rs` / `releases/genesis_europe.rs`
   `STAGE_TITLES` arrays carry the canonical cart stage list — but
   they're indexed by stage slot, not bank number. Need to map
   stage-slot → bank-number (likely via the per-arm `<stage>.asm.in`
   or the disassembler's bank dispatch).

2. Replace each TODO comment with the resolved stage name. Pattern:

       bankSwitch 4;  TODO - Name this stage (bank number #4)
                          ↓
       bankSwitch 4;  <Stage name from STAGE_TITLES>

3. After the rename, all 23 TODOs vanish; verify-stages 29/29 +
   verify-unified 27/27 must stay green (only changes are inside
   `;` comments — no semantic effect).

# Acceptance criteria

- [ ] Map cart bank numbers 2..5 to AW stage slots (probably via
      AWVM_Tools' STAGE_TITLES + bank dispatch table).
- [ ] Replace all 23 `TODO - Name this stage (bank number #N)`
      comments with the resolved stage names.
- [ ] Round-trip verify still 29/29 + 27/27 (comments-only change
      should be neutral).

# Log

- 2026-05-09: opened. Found during a TODO-marker sweep over
  src/levels/_unified/ in source-reconstruction. Initially
  thought of as pure source-side cleanup.

- 2026-05-09 (later): traced the TODOs upstream. The placeholder
  comments in source-recon are **faithful copies** of the
  AWVM_Tools `STAGE_TITLES` array in
  `AnotherWorld_VMTools/awvm/src/releases/gba_usa.rs`:

      pub const STAGE_TITLES: &[&str] = &[
          "Code-wheel screen",
          "Arrival at the Lake & Beast Chase",
          "Prison",
          "TODO - Name this stage (bank number #3)",
          "TODO - Name this stage (bank number #4)",
          "TODO - Name this stage (bank number #5)",
          "TODO - Name this stage (bank number #6)",
          "Secret Code Entry Screen",
      ];

  The disassembler copies these comment strings into the source
  output verbatim. So the 23 TODOs are an UPSTREAM AWVM_Tools
  problem — the gba_usa STAGE_TITLES table needs banks 3-6 named.

  Already partially tracked under #0065 (which focused on bank-0
  "Code-wheel screen" → "Intro Sequence" for cart). This issue
  is the broader scope: also fill in banks 3-6.

  **Per CLAUDE.md ("never propose changes to AWVM_Tools without
  surfacing first"), this needs owner triage**. Fixing requires
  identifying which AW canonical stages map to gba_usa banks 3-6
  and updating the STAGE_TITLES array. The snes.rs +
  genesis_europe.rs only have stages 0-1 (LAKE + Prison) so the
  mapping for the other banks comes from the canonical 8-stage
  list (CAVES, TANK, CAPSULE, ENDING, plus PASSCODE which is
  already at bank 7).

  Re-tier this from D → C (it's a small upstream fix that
  removes 23 TODO markers from the source tree once landed; not
  D-priority infrastructure).

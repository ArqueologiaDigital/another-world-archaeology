# 16 — Unused PALETTE slots (DOS port)

Companion finding to research/15 (unused SOUND), research/11
(unused MUSIC), and research/06 (unused polygons).

## Summary

Each AW VM PALETTE resource defines 32 palettes × 16 colours.
The bytecode selects a palette via `setPalette N` where N is an
index in [0, 32). Counting per-level **literal-index** uses
across DOS bytecode (per `tools/unused_palette_scan.py`, #0057),
**113 palette slots are never selected** by any reachable
bytecode.

Per-level breakdown (DOS):

| Level | Stage      | Resource | #used | unused indices |
| :---: | --- | :---: | ---: | --- |
| 0 | CODE_WHEEL | 0x14 | 26 | 2, 8, 28, 29, 30, 31 |
| 1 | INTRO      | 0x17 | 28 | 28, 29, 30, 31 |
| 2 | LAKE       | 0x1A | 20 | 0, 1, 4, 8, 12, 14, 16, 26, 27, 28, 30, 31 |
| 3 | PRISON     | 0x1D | 18 | 0, 1, 3, 10, 13, 14, 16, 17, 22, 23, 24, 27, 28, 30 |
| 4 | CAVES      | 0x20 | 26 | 0, 3, 4, 10, 20, 28 |
| 5 | TANK       | 0x23 | 16 | 0, 7, 8, 9, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 30 |
| 6 | CAPSULE    | 0x26 | 22 | 5, 7, 8, 10, 13, 15, 16, 18, 28, 30 |
| 7 | ENDING     | 0x29 | 17 | 0..9, 13, 14, 15, 30, 31 |
| 8 | PASSCODE   | 0x7D | 2 | 1..4, 6..31 (uses only slots 0 and 5) |

**Total unused slots: 113.**

## Visual catalogue

`tools/render_palette_swatches.py` renders each PALETTE resource
as a 32×16 grid of colour swatches; rows the bytecode never
selects are greyed out and labelled `(unused)`. Outputs at
`docs/assets/research-16-unused-palettes/level<N>_<STAGE>.svg`.

## Notable patterns

- **Slot 28 is never used in any level.** Across all 9 levels,
  slot 28 of every PALETTE resource is dead. Possibly reserved
  for a feature that didn't ship.
- **Slots 30, 31** are unused in 6 of 9 levels. The "high four"
  palettes (28-31) appear to be systematically excluded — the
  bytecode never touches them.
- **PASSCODE uses only 2 slots** (0 and 5). Likely a static
  red-and-grey colour scheme for the code-entry screen. The
  other 30 palettes in PASSCODE's resource are dead weight in
  this stage's runtime.
- **ENDING skips the entire low half** (slots 0..9 unused). The
  closing cinematic only paints with palettes ≥ 10. Implies the
  ENDING-specific palette resource was authored top-down with
  the expressive colours in the upper half.

## Caveats

- **`setPalette` may take a variable operand** in some places
  (rare in AW). Variable-index uses are excluded conservatively
  from the "used" set, so the unused list might be a slight
  overestimate. The naive scanner reports literal-index uses
  only.
- **Reachability** (#0058) is not yet applied. A `setPalette N`
  inside a setup-then-overwritten dispatch case — like the
  patterns surfaced in #0076 — would still mark N as "used"
  even though the runtime never reaches it. Until reachability
  lands, treat the unused list as a lower bound on actual cuts.
- **Per-port comparison pending**: only DOS scanned today. An
  unused-on-DOS slot that IS selected on the cartridge ports
  would tell us the DOS port re-encoded `setPalette` opcodes
  during the per-stage triplet rebuild documented in
  research/13.

## Reproducing

```bash
# Run the scanner:
python3 tools/unused_palette_scan.py work/076117919d1dca51e486f33b8f7817e3

# Render any level's palette as SVG:
python3 tools/render_palette_swatches.py \
    tmp/output/msdos/resources/resource-0x1a.bin \
    docs/assets/research-16-unused-palettes/level2_LAKE.svg \
    --unused "0,1,4,8,12,14,16,26,27,28,30,31" \
    --title "Level 2: LAKE (palette resource 0x1A)"
```

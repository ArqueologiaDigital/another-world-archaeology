# `video type=1` default-omission migration

## Goal

Make the AWVM_Tools `video` instruction's `type=1` keyword
optional and default. Strip the now-redundant prefix from every
source file in `another-world-source-reconstruction/src/`.

## Background

Across the 5 currently disassembled ports, of 56,779 `video`
instructions:

| `type=` value | Meaning | Count | % |
|---|---|---:|---:|
| `1` | CINEMATIC (per-stage polygon bank) | 47,867 | 84% |
| `0` | VIDEO2 (shared common-video bank)  |  8,912 | 16% |

`type=1` being the dominant case, spelling it out at every call
site adds visual noise without distinguishing one call from
another.

## AWVM_Tools change (commit `207a072` in
`AnotherWorld_VMTools`)

### Encoder (`awvm/src/asm.rs`)

`encode_video` reads the `type=` keyword if present, otherwise
defaults to `CINEMATIC` (1):

```rust
let video_type = match ops.get("type") {
    Some(t) => asm.resolve_or_zero(&t.value),
    None => CINEMATIC,
};
```

Backwards-compatible: source with explicit `type=1` keeps
assembling to byte-identical output.

### Decoder (`awvm/src/disasm.rs`)

| Bytecode | Old emit | New emit |
|---|---|---|
| Compact form, opcode `0x80..0xFF` | `video type=1, offset=…, x=…, y=…` | `video offset=…, x=…, y=…` |
| Full form CINEMATIC, `opcode & 3 != 3` | `video type=1, offset=…, x=…, y=…, zoom=…` | `video offset=…, x=…, y=…, zoom=…` |
| Full form VIDEO2, `opcode & 3 == 3` | `video type=0, offset=…, x=…, y=…, zoom=…` | unchanged |

### Tests

4 new unit tests in `asm.rs`:

- `video_compact_form_type1_default_matches_explicit`
- `video_full_form_default_zoom_type1_default_matches_explicit`
- `video_full_form_var_zoom_type1_default_matches_explicit`
- `video_type0_video2_still_requires_explicit_type`

Each round-trips a small `.asm` snippet through `assemble()` and
asserts byte-equivalence between the old and new syntactic forms.

## Source-tree migration (commit `375a141` in
`another-world-source-reconstruction`)

Run via:

```
python3 tools/migrate_video_type1_default.py \
    --src-tree /path/to/another-world-source-reconstruction/src
```

The tool walks `<src-tree>` for `.asm`, `.inc`, `.asm.in` files
and replaces `video type=1, ` with `video ` (single regex,
idempotent — re-running on already-migrated files is a no-op).

Result: 47,867 lines edited across 701 files; total source-tree
diff `47,980 +/-` lines.

`verify_stage 29/29` and `verify_unified 27/27` both stay green
after the migration — the round-trip property holds because the
encoder defaults the omitted `type` value back to 1.

## Disambiguation: why the full-form CINEMATIC default-zoom case
keeps `zoom=0x40` explicit

There are two distinct bytecode forms for CINEMATIC video calls:

- **Compact form** (opcode `0x80..0xFF`, 3 bytes total): always
  CINEMATIC, no zoom byte (implicit 0x40 zoom).
- **Full form CINEMATIC default zoom** (opcode `0x40..0x7F` with
  `opcode & 3 == 0` and no var-zoom bits, 5+ bytes total):
  CINEMATIC with explicit 0x40 zoom byte in the bytecode.

If both forms were rendered as `video offset=…, x=…, y=…` the
disassembler output would lose information — same source,
different bytecode. So the full-form case keeps `zoom=0x40` in
the source text. Compact-form lines have no zoom field at all.

## Why `type=0` (VIDEO2) stays explicit

VIDEO2 is a minority (16%). Defaulting it would remove the
disambiguation handle for compact-form CINEMATIC (which is
also `type=1`). Spelling out `type=0` in 8,912 lines is the
cheaper choice than introducing a new mnemonic or a different
disambiguation marker.

## Counter-examples we considered and rejected

- **`videoFull` / `videoCinema` mnemonics**: would let us also
  drop `zoom=0x40` from full-form CINEMATIC default zoom. Rejected
  per project preference for fewer mnemonics.
- **`type=0` shorthand** (e.g., a `videoCommon` mnemonic):
  rejected; same reason.
- **Defaulting `song delay=0x0000` and `pos=0x00`**: surveyed
  (91%, 93% of song instructions respectively, ~200 lines each)
  but the user opted to limit this round to `video` only.

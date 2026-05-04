# `;@raw=` → `;@enc=…` migration plan

## Goal

Eliminate `;@raw=` from the source tree and from awvm-asm parsing.
Replace the three load-bearing patterns it currently masks with
explicit, named `;@enc=…` flags that the encoder honours and the
disassembler emits.

After migration, `;@raw=` is **strictly forbidden**: any occurrence
in source is a hard parse error, the audit's `--check` mode rejects
any commit that introduces one.

## The three patterns

Per `docs/content/research/14-raw-annotation-residue.md`:

| Pattern | Count | New marker |
| --- | ---: | --- |
| `video … zoom=[var]` with bit-1 zoom-encoding (opcodes 0x55/0x56/0x5A/0x66/0x6A/0x7A) | 568 | `;@enc=alt` |
| `bankSwitch N` with operand word `0x07Dx` | 6 | `;@enc=legacy_d` |
| `bankSwitch N` with operand word `0x07Ex` | 3 | `;@enc=legacy_e` |
| `setPalette 0x00` with trailing `0x00` (instead of `0xFF`) | 3 | new operand: `setPalette 0x00, _trailing=0x00` |

Counts above are from per-branch sources only; the unified-chunk
strip (in flight as of 2026-05-04) will add more bit-1 video
instances. The bankSwitch and setPalette tail counts are likely
final since those patterns appear only in specific stages.

## awvm-asm changes (`AnotherWorld_VMTools/awvm/src/asm.rs`)

### 1. Parser

Add an `enc: Option<String>` field to `Instruction` (parallel to
`raw: Option<Vec<u8>>`). Add a `parse_enc_marker(line: &str) ->
Option<String>` mirroring `parse_raw_marker`. In `parse_lines`,
populate `instr.enc` for each line.

Recognized values: `alt`, `legacy_d`, `legacy_e`. Unknown values are
a hard error (rejecting typos).

### 2. Video encoder (`encode_video`)

When `instr.enc == Some("alt")` and `zoom.is_var`:

```rust
opcode |= 0x02;     // not 0x01
```

Otherwise continue using `opcode |= 0x01` as today.

`;@enc=alt` is only valid on `video` lines with `zoom=[var]`. Any
other use is a parse error.

### 3. bankSwitch encoder

When `instr.enc == Some("legacy_d")`:

```rust
asm.byte_const(0x19);
asm.word_const(0x07D0 | (bank_int & 0xF));
```

When `instr.enc == Some("legacy_e")`:

```rust
asm.byte_const(0x19);
asm.word_const(0x07E0 | (bank_int & 0xF));
```

Otherwise the canonical `0x3E80 | bank` path.

### 4. setPalette trailing-byte operand

Add a new keyword operand `_trailing` to `setPalette`. When present
and equal to `0x00`:

```rust
asm.byte_const(0x0B);
asm.word_const((pal_int << 8) | 0x00);
```

Otherwise the canonical `(pal_int << 8) | 0xFF` path.

### 5. `;@raw=` deprecation

Phase 1 (transitional): keep `parse_raw_marker` working so the
migration can land in stages without breaking byte-match.

Phase 2 (post-migration): rip `parse_raw_marker` and the `raw`
field on `Instruction` out entirely. Any line containing `;@raw=`
becomes a parse error with a pointer to this migration doc.

## awvm-disasm changes (`AnotherWorld_VMTools/awvm/src/disasm.rs`)

### 1. Per-pattern emission

Replace the unconditional `;@raw=` suffix in `disasm_instruction`
with pattern-aware emission:

- For video opcodes `0x55, 0x56, 0x5A, 0x66, 0x6A, 0x7A` (the bit-1
  zoom-as-var opcodes): emit `;@enc=alt`.
- For other video opcodes in the bit-0 zoom-as-var family: emit
  nothing (canonical form).
- For `0x19` decoded as `bankSwitch N` with `imm & 0xfff0 == 0x07D0`:
  emit `;@enc=legacy_d`.
- For `0x19` decoded as `bankSwitch N` with `imm & 0xfff0 == 0x07E0`:
  emit `;@enc=legacy_e`.
- For `setPalette 0x00` with trailing waste byte `0x00`: emit
  `_trailing=0x00` as an extra operand on the `setPalette` line.
- For everything else: emit nothing (canonical form is
  byte-exact).

### 2. Phase 1: parallel emission

In Phase 1 of the migration, emit BOTH `;@enc=…` for known patterns
AND retain the `;@raw=` suffix for everything else. Once the source
is fully migrated, switch to emitting only `;@enc=…` (or nothing).

## Source migration

After the awvm-asm + awvm-disasm changes land:

1. Run a sed-style script to rewrite each surviving `;@raw=` line:
   - `video … zoom=[var] ;@raw=0x6A,…` → `video … zoom=[var] ;@enc=alt`
   - `video … zoom=[var] ;@raw=0x56,…` → `video … zoom=[var] ;@enc=alt`
   - (and the other 4 alt opcodes)
   - `bankSwitch N ;@raw=0x19,0x07,0xDx` → `bankSwitch N ;@enc=legacy_d`
   - `bankSwitch N ;@raw=0x19,0x07,0xEx` → `bankSwitch N ;@enc=legacy_e`
   - `setPalette 0x00 ;@raw=0x0B,0x00,0x00` → `setPalette 0x00, _trailing=0x00`
2. Run `verify_stage` + `verify_unified`. Both must pass with the
   new awvm-asm.
3. If anything fails, the migration script left a residue —
   investigate the specific failing instruction (possibly a fourth
   pattern not covered above).

## Removing `;@raw=` (Phase 2)

1. Delete `parse_raw_marker` from awvm-asm.
2. Remove the `raw` field from `Instruction`.
3. Remove the `if let Some(raw) = &instr.raw { … return; }`
   short-circuit at the top of `encode`.
4. Have the parser reject any line containing `;@raw=` with a clear
   error message: `;@raw= is no longer supported; use ;@enc= instead
   (see docs/raw_to_enc_migration_plan.md)`.
5. Update `tools/audit_raw_annotations.py --check`: any `;@raw=`
   occurrence is a hard fail.
6. Wire `--check` into pre-commit / CI so future commits can't
   introduce new `;@raw=` annotations.

## Acceptance

- [x] awvm-asm + awvm-disasm support `;@enc=alt`, `;@enc=legacy_d`,
      `;@enc=legacy_e`, and `setPalette` with `_trailing` operand.
      (AnotherWorld_VMTools commit `ad99497`.)
- [x] Source migration rewrites every surviving `;@raw=` to the new
      forms. (per-branch: source-reconstruction commit `e1f42fa`;
      per-arm + shared chunks: `2c4f30e`, `2c2dcd0`, `d630744`.)
- [x] `verify_stage` 29/29 + `verify_unified` 27/27 still green
      after migration.
- [x] `;@raw=` parser removed from awvm-asm.
      (AnotherWorld_VMTools commit `a1c6661` — parser now panics
      on `;@raw=`. Disasm fallback also dropped: `de940c8`.)
- [x] `tools/audit_raw_annotations.py --strict` rejects any
      `;@raw=` presence. Wired into source-reconstruction
      `Makefile` as `make lint` (commit `f8d3530`).
- [x] No `;@raw=` anywhere in active `src/levels/`.

**Migration complete: 2026-05-04.**

For follow-up, see #0086 log: per-chunk re-symbolisation of the
literal addresses (e.g., `0x533A` → `<UNIQUE_NAME>_RET`) is a
readability cleanup if/when needed.

---
id: 0067
title: AWVM_Tools: add 'dw LABEL' directive to awvm-asm (label-as-2-byte-address)
status: open
tier: C
created: 2026-05-01
updated: 2026-05-01
depends_on: []
blocks: []
tags: [awvm-tools, proposal, assembler]
---

# Context

awvm-asm currently supports `db <byte>...` for emitting raw byte
literals, but has no directive for emitting a 2-byte LABEL address
in big-endian. Without one, the Phase 3b unification pipeline
(research/09) can't canonicalize address bytes that live INSIDE
`db` blocks (where awvm-disasm couldn't decode an instruction
properly).

Concrete example from cartridge ↔ GBA INTRO unification:

```
;@if BRANCH == "heineman_cartridge"
    db 0x0A, 0x78, 0x04, 0x06, 0x07, 0x15, 0x40, 0x12
;@elif BRANCH == "foxy_gba_2004"
    db 0x0A, 0x78, 0x04, 0x06, 0x07, 0x15, 0x4C, 0x12
;@endif
```

Bytes 6-7 form a 16-bit big-endian address: 0x4012 (cart) vs
0x4C12 (gba). With a `dw LABEL_X` directive that resolves to the
label's 2-byte address, the line could be:

```
    db 0x0A, 0x78, 0x04, 0x06, 0x07, 0x15
    dw COND_JUMP_TARGET
```

If `COND_JUMP_TARGET` is the same label name in both branches (via
the inline-label canonicalizer, research/09), the `;@if` block
disappears.

I tested several syntaxes:
- `dw LABEL` — silently produces 0 bytes (unknown directive)
- `db LABEL` — emits 1 byte (the label's low-byte? or junk?)
- `.word LABEL` — silently produces 0 bytes
- `addr LABEL` — assembler panic

So none currently work.

# Acceptance criteria

- [ ] Surface this proposal to AWVM_Tools owner before
      implementing.
- [ ] Add `dw <label-or-imm>` directive that emits 2 bytes
      (big-endian, same encoding as the assembler's address
      operands in `jmp`/`call`/`setup` etc.).
- [ ] Verify Phase 3b unification pipeline can use it to
      canonicalize the 4 remaining `db`-block diffs in the
      cartridge ↔ GBA INTRO unified source.

# Log

- 2026-05-01: opened. Surfaced from Phase 3b (research/09) as the
  blocker for canonicalizing 4 of the 8 remaining ;@if blocks in
  the cartridge ↔ GBA INTRO unified source.

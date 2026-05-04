---
id: 0090
title: Proposal — add in-memory assemble_bytes() to awvm-asm for WASM consumers
status: open
tier: D
created: 2026-05-04
updated: 2026-05-04
depends_on: [0089]
blocks: []
tags: [awvm-tools, proposal, wasm, suite, source-editor]
---

# Context

Issue #0089 (Suite source-editor) Phase 2 needs to call awvm-asm
from inside the Suite's `engine/` crate, which compiles to a wasm
target. The crate currently exposes only:

```rust
pub fn assemble(input_path: &Path, output_path: &Path) -> io::Result<()>;
```

— which is unusable on wasm32-unknown-unknown because it touches
`std::fs`. The browser context has no filesystem.

The internal building blocks are already there (`parse_lines`,
`Asm`, `encode`, `encode_video`), but they are private. That is
fine — we don't want to expose internals — but we do need a thin
in-memory wrapper.

Per `CLAUDE.md`, modifications to `AnotherWorld_VMTools` need
project-owner approval before implementation. This issue is the
proposal.

# Proposed API

Add a single `pub` function next to `assemble()` in `awvm/src/asm.rs`:

```rust
/// Assemble AW VM source text in memory. Returns the bytecode
/// and the address-of-each-label pairs (in source-definition
/// order; same data the `<output>.symbols.txt` sidecar carries).
///
/// Pure-rust, no I/O; safe for wasm32 / no_std-style consumers
/// (modulo `alloc`).
pub fn assemble_bytes(src: &str) -> (Vec<u8>, Vec<(String, i64)>) {
    let (initial_symbols, instructions) = parse_lines(src);
    let mut asm = Asm::new();
    asm.symbols = initial_symbols;

    // First pass — labels resolve to current address as we go.
    asm.address = 0;
    for (label, instruction) in &instructions {
        if let Some(l) = label {
            asm.symbols.insert(l.clone(), asm.address as i64);
        }
        encode(&mut asm, instruction);
    }

    // Second pass — symbols are now complete.
    asm.second_pass = true;
    asm.rom.clear();
    asm.address = 0;
    let mut all_defs: Vec<(String, i64)> = Vec::new();
    for (label, instruction) in &instructions {
        if let Some(l) = label {
            asm.symbols.insert(l.clone(), asm.address as i64);
            all_defs.push((l.clone(), asm.address as i64));
        }
        encode(&mut asm, instruction);
    }

    (asm.rom, all_defs)
}
```

Then refactor the existing `assemble()` to delegate:

```rust
pub fn assemble(input_path: &Path, output_path: &Path) -> io::Result<()> {
    let src = fs::read_to_string(input_path)?;
    let (rom, all_defs) = assemble_bytes(&src);
    fs::write(output_path, &rom)?;

    let symbols_path = output_path.with_extension("symbols.txt");
    let mut sym_out = String::new();
    for (name, addr) in &all_defs {
        sym_out.push_str(&format!("0x{:04X}\t{}\n", addr, name));
    }
    fs::write(&symbols_path, sym_out)?;
    Ok(())
}
```

This change is a pure refactor — `assemble()`'s observable
behaviour (the file output) is byte-identical.

# Why minimal

- Single new public function. No new types exposed; no new traits.
- Does not change the parser, the instruction representation, or
  the encoder — those stay private.
- Returns *owned* `Vec<u8>` and `Vec<(String, i64)>` so the caller
  doesn't need to depend on `awvm`'s internal `Asm` struct.
- Failure mode is "panic on bad input" today (same as the existing
  file path) — error propagation could be added later as a
  separate change.

# Acceptance criteria

- [ ] Owner reviews the proposal and either approves, requests
      changes, or rejects.
- [ ] If approved: implement the refactor in `AnotherWorld_VMTools`
      on a feature branch, run the existing tests, byte-match
      the file-based path against the new in-memory path on a
      sample program.
- [ ] Tag a release of awvm so the Suite can pin a known version.
- [ ] Wire the Suite's `assemble_source()` to call
      `awvm::asm::assemble_bytes()` (Phase 2 of #0089).

# Log

- 2026-05-04: opened. Surfaced as part of the Phase 2 plan for the
  Suite source-editor (#0089). Proposal posted instead of an
  unapproved direct change to AWVM_Tools.

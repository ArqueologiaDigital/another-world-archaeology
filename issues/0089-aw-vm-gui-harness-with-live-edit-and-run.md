---
id: 0089
title: AW VM GUI harness with live build-and-run + var/thread inspection
status: open
tier: B
created: 2026-05-04
updated: 2026-05-04
depends_on: []
blocks: [0090]
tags: [tooling, vm, gui, interactive, dev-experience]
---

# Context

Owner request (2026-05-04): a VM implementation that can build
bytecode from source files (the per-branch `.asm` we maintain
or new test bytecodes) and run them in real time, with a GUI
that supports:

  - Text editor for source.
  - Play / pause / reboot controls.
  - Live VM-variable inspection AND editing.
  - Per-channel (thread) controls: enable / disable / freeze /
    unfreeze.

This is a developer-experience tool that would close the loop
between writing/modifying AW VM source and seeing the resulting
behaviour without round-tripping through external tools.

# Existing infrastructure

  - **awvm-asm** (in sibling `AnotherWorld_VMTools/awvm/`):
    Rust assembler that turns `.asm` source into AW VM
    bytecode. Already wired into `tools/verify_stage.py` and
    `tools/verify_unified.py`.
  - **awvm-disasm** (same repo): the inverse, for
    cross-checking byte-identity.
  - **Reference VM implementations available externally**:
    - `rawgl` (C++) — Fabien Sanglard's port.
    - `fbBeRoFiel`'s original — Eric Chahi's reference impl
      that ships with the 1991 amiga.
    - Various forks of rawgl in `another-world-hacks` etc.
  - **No Python VM in this repo yet** — `tools/aw_music_to_wav.py`
    is a partial port of the music decoder; no full VM runtime.

# Scope decision

Three reasonable tech stacks:

  1. **Python + Tkinter** — single-file portable GUI. Pros:
     no new dependencies, cross-platform. Cons: render
     performance for 320×200 polygons may be tight; needs
     a Python VM port (substantial effort).
  2. **Wrap rawgl with a thin GUI** — use rawgl's existing C++
     VM as the backend, expose its state via a tiny IPC layer,
     drive a Python/Tk GUI on top. Pros: reuses battle-tested
     VM, fast. Cons: more moving parts, IPC complexity.
  3. **Web-based** — port the VM to JS (or use an existing JS
     port like `another-world-js`), wrap in a browser UI. Pros:
     easy to share. Cons: out-of-scope for a CLI-driven repo.

Recommendation: option 2 (rawgl wrapper). The VM port is the
biggest cost item; reusing rawgl avoids it. The thin GUI
wrapper is then a few hundred lines of Python.

# Phased implementation

**Phase 1: VM backend** — fork rawgl with a debug/inspection
shim. Add an IPC channel (stdin/stdout JSON, or a TCP socket)
that exposes:

  - Load bytecode from a path.
  - Step / play / pause / reset.
  - Read all VM variables (`vmVariables[256]`).
  - Write a single VM variable.
  - Read per-channel state (instruction pointer, run/freeze flag).
  - Write per-channel state (enable/disable/freeze/unfreeze).

**Phase 2: Build pipeline** — integrate awvm-asm. The GUI's
"play" button:

  1. Save current source buffer to a temp file.
  2. Invoke awvm-asm temp.asm → temp.bin.
  3. Push the bytecode to the VM backend.
  4. Resume the VM.

**Phase 3: GUI** — Python + Tkinter (or PyQt for richer
widgets):

  - Text editor pane (with simple syntax highlighting for AW
    opcodes).
  - Toolbar: play / pause / reboot.
  - Variable inspector grid (256 cells, double-click to edit).
  - Thread inspector list (64 channels with state badges and
    enable/disable/freeze buttons).
  - Render canvas (320×200, scaled 2-3×).

**Phase 4: Polishes** — breakpoints, watchpoints, step-over /
step-into, source-line correlation (via a `-d` debug map from
awvm-asm).

# Acceptance criteria

- [ ] Phase 1 (VM backend with IPC) builds and accepts the
      core commands.
- [ ] Phase 2 (build pipeline) wired so editing source +
      clicking play assembles+runs in <1s for typical .asm
      sizes.
- [ ] Phase 3 (GUI) shows editor + canvas + var grid +
      thread list, with all four interactive controls
      (var edit, channel enable/disable/freeze/unfreeze)
      functional.
- [ ] Bonus: load existing per-port stage source files
      (`src/levels/dos_1992/LAKE.asm`) and replay them.

# Notes / risks

  - Cross-platform: rawgl uses SDL; bundling for Linux/macOS
    is straightforward; Windows requires care.
  - awvm-asm modifications: changes to the assembler need
    owner approval per CLAUDE.md (`do not propose changes to
    AWVM_Tools without surfacing the proposal first`). For
    Phase 2, ideally awvm-asm gets a `--debug-map` flag
    output so the GUI can correlate runtime PC ↔ source line.
    Coordinate that as a separate AWVM_Tools issue before
    starting Phase 4.
  - Owner currently away — log this as a tracking issue and
    start with a scoping/MVP doc rather than committing to a
    specific tech stack until owner can chime in.

# Log

- 2026-05-04: opened. Owner request via cron-tick chat. No
  implementation started yet — substantial scope. Will start
  by sketching the IPC protocol for Phase 1 in a separate
  doc and wait for owner review of the tech-stack choice
  before committing to a specific path.

- 2026-05-04 (later): pivoted away from a from-scratch port.
  Owner pointed out that
  https://github.com/malandrin/another-world-suite already
  ships a working browser-based AW VM (Rust+WASM engine + Vue
  frontend with disassembler / threads / registers panels).
  Stack choice now: extend the Suite with a source-editor
  window. Working in a sibling clone at
  `../another-world-suite` on a feature branch
  `source-editor` — not pushed anywhere upstream, treated as
  a local fork.

  - **Phase 1 (UI shell)** — DONE. Suite commit "add
    SourceEditor window + engine assemble_source stub
    (Phase 1)" 4a2ea55. Adds a `<Window>`-shell editor pane
    pre-populated with the bouncing-ball demo from
    forum.fiozera.com.br/t/127, two action buttons ("assemble"
    / "assemble + load"), engine stubs `assemble_source(&str)`
    and `replace_active_part_bytecode(&[u8])`.
  - **Phase 3 (engine: replace bytecode + reset VM)** — DONE.
    Suite commit "implement replace_active_part_bytecode +
    bump wasm-bindgen (Phase 3)" d6db7a2. Implements the
    bytecode swap + thread reset, bumps wasm-bindgen 0.2.62 →
    0.2.93 to build on current Rust, wires the frontend's
    onSourceLoaded() to refresh the views. Both native and
    `wasm32-unknown-unknown` builds verified.
  - **Phase 2 (engine: actually call awvm-asm)** — BLOCKED on
    issue #0090 (awvm-asm in-memory `assemble_bytes()` API
    proposal awaiting owner review).
  - **Phase 4 (audio backend, breakpoints, debug map)** —
    deferred until 1+2+3 are settled.

  Phases 1 and 3 are independently shippable: they let the
  user open the editor window, write source, see the planned
  flow, and the bytecode-replacement path is exercised the
  moment Phase 2 lands.

# Symbols

A cross-release map of semantic names assigned to bytecode addresses
and VM variable indices. Different releases tend to share most
symbols at slightly different offsets, so the map is layered:

```
symbols/
├── _base.yaml         # invariant across releases (e.g. VM
│                      # variables whose meaning is fixed by the
│                      # engine itself)
├── dos.yaml           # release-specific overrides + addresses
├── amiga.yaml
└── …
```

Each release file `inherits` `_base` and adds:

- **`bytecode_addresses`**: `<resource_id>:<offset>` → label.
  Discovered by reading disassembly and (where applicable)
  cross-referencing rendered cinematic frames.
- **`vm_variables`**: variable index → label. Often shared across
  releases (the engine's variable conventions are stable) but the
  *value* of a given variable at a given moment may differ by
  release.

The symbols are consumed by the disassembler (via AWVM_Tools) and
the docs site so addresses appear with their semantic name wherever
they are referenced.

## Image-driven labelling

Polygon resources (`POLY_ANIM`, `POLY_CINEMATIC`) are rendered to
PNG by the extract step. A reviewer (human or Claude) then visually
identifies what each frame depicts ("cyclops walking frame 3",
"title-screen logo", "gun pickup animation") and records the label
against the polygon's address. The same labels propagate to any
bytecode that loads or draws that polygon.

## Status

*No symbols recorded yet. Bootstrapping starts as soon as the DOS
disassembly lands and we identify the first concrete addresses
(see open question [01: gun ammo](#/open-questions/01-gun-ammo)).*

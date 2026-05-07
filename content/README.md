# Another World Archaeology

A research project tracking the development history of every released
port of Eric Chahi's *Another World* (a.k.a. *Out of This World*).

The methodology is modelled on MAME's approach to ROM preservation:
each original release file is identified by checksum, never committed
to the repo, and instead used as input to a pipeline that extracts and
disassembles its assets into diff-friendly text so releases can be
compared.

## What this site is

A static documentation portal for the project. It is rendered entirely
client-side from data baked into `docs/data/all.js` by the build step
(`tools/gen_docs_data.py`). It is designed to be readable both via
`file://` locally and via GitHub Pages.

The site has three kinds of content:

- **Pages** (engine architecture, release catalog, format coverage,
  genealogy findings, cross-release symbol map) — hand-authored
  reference material, evolves as the research progresses.
- **Research** (findings + open questions) — the actual investigation
  outputs; what we have learned and what we are still trying to
  answer.

## The pipeline at a glance

```
metadata.json  (catalog)
   │
   ▼
fetch  ──→  original_files/<key>/<file>              [local archive]
   │
   ▼
extract  ──→  per-format extractor produces resources, manifest
   │
   ▼
disasm   ──→  AWVM_Tools converts BYTECODE resources to source-like
   │           text (round-trips byte-identical via awvm-asm)
   ▼
compare  ──→  cross-release diffs feed into research findings &
              the genealogy view
```

Most cataloged formats have extractors today: DOS bank, Amiga ADF,
Atari ST Pasti, SNES / Genesis / GBA cartridge ROMs, 3DO Mode 1,
Nintendo DS, Apple II demake, and WinXP PAK. Two formats remain as
stubs awaiting decoder work (Apple IIgs WOZ, Mac classic StuffIt /
resource-fork), one is best-effort (Symbian `.sis`), and one is
blocked on a fixture (Jaguar — no public dump exists yet). The
[Format coverage](#/coverage) page tracks the full status table.

## Standing policies

- **Original game assets are never committed.** They live only in the
  local `original_files/` permanent archive — never a cache, never
  deleted; once a file is fetched, it stays for the life of the
  project.
- **External tool dependencies are pinned**, not vendored. See
  `tools/AWVM_Tools.lock`.
- **Frozen reference material** (e.g. archived walkthroughs) is
  protected by a sha256 manifest checked by `make verify-references`.

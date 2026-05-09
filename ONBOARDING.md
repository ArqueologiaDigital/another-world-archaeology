# Onboarding: extract, disassemble, and round-trip Another World bytecode

You are working on a new port of the *Another World* VM — in this case
to MSX. To do that you need original game bytecode (and the associated
sound / music / polygon / palette resources) in a form you can load
into your engine, plus a reproducible way to verify the bytecode you
shipped is byte-identical to the bytecode the original release shipped.

This repo's toolchain gives you exactly that. The full pipeline is:

    original release archive
        │
        ▼
    extract.py (this repo)        — unpacks bank/ADF/ROM → resource files
        │
        ▼
    awvm-disasm (AWVM_Tools)      — bytecode resource → human-readable .asm
        │
        ▼
    awvm-asm (AWVM_Tools)         — .asm → byte-identical bytecode
        │
        ▼
    round-trip verify             — byte-for-byte match with the original

Once that round-trip is green, you have a trusted reference: the .asm
sources are equivalent to the shipped bytecode, and your MSX port can
load either.

## Prerequisites

  - **Rust toolchain** (rustc + cargo, stable channel). Used to build
    `awvm-disasm` and `awvm-asm` from `AWVM_Tools/`.
  - **Python 3.11+**. Used by the `extract.py` orchestrator and the
    verification scripts under `tools/`.
  - **GNU Make**. The convenience targets are in `Makefile`s in each
    repo.
  - An **original game release** (e.g. the DOS bank-format release).
    See `metadata.json` for the per-release `download` URLs and md5
    checksums; original game files are NEVER committed to these
    repos.

## Three repos, sibling layout

The toolchain spans three repos that expect to live as siblings under
the same parent directory:

    ~/another-world/                 # or wherever you prefer
    ├── AnotherWorld_VMTools/        # the Rust binaries: awvm-disasm + awvm-asm
    ├── another-world-archaeology/   # this repo: extractors + orchestrator
    └── another-world-source-reconstruction/   # the .asm source tree

Clone all three:

    mkdir -p ~/another-world && cd ~/another-world
    git clone https://github.com/felipesanches/AnotherWorld_VMTools.git
    git clone https://github.com/ArqueologiaDigital/another-world-archaeology.git
    git clone https://github.com/ArqueologiaDigital/another-world-source-reconstruction.git

A few tools in `another-world-archaeology` resolve sibling-repo paths
via `tools/_paths.py` — they look for `AnotherWorld_VMTools` and
`another-world-source-reconstruction` exactly one directory above
themselves. The sibling layout matters; symlinking works too.

## Step 1 — build the disassembler / assembler

    cd ~/another-world/AnotherWorld_VMTools
    cargo build --release

This produces `target/release/awvm-disasm` and `target/release/awvm-asm`.
Everything else shells out to these binaries.

## Step 2 — fetch + extract a release

The archaeology repo orchestrates extraction. To extract every
release listed in `metadata.json`:

    cd ~/another-world/another-world-archaeology
    make extract

To extract a single release by slug (faster):

    python3 extract.py --slug dos                # MSDOS bank format
    python3 extract.py --slug amiga-retro-presskit
    python3 extract.py --slug gba-foxy-2004      # cartridge format

For the bank-format ports (DOS, Amiga), each release's archive is
unpacked into `original_files/<key>/` and resource files written to
`work/<package_md5>/`. For cartridge-format ports
(snes-eu, genesis-eu, gba-foxy-2004) the extractor invokes
`awvm-disasm` with `all_levels` and writes per-level disasm + a
`romset/` directory.

Note: original game files are expected to live under
`original_files/<key>/`. If you don't have them, see `metadata.json`
for the download URLs and checksums per release.

## Step 3 — disassemble (bank-format ports)

For DOS / Amiga, the extract step doesn't run the disassembler — there's
a separate Make target:

    make disasm                  # all bank-format ports (msdos, amiga)
    make disasm PORT=msdos       # one specific port

Output lands at `tmp/output/<port>/disasm/level_<N>/<port>_level-<N>.asm`.

Cartridge-format ports already have their disasm trees written by
`make extract` (via `extractors/cartridge_rom.py`), so no separate
disasm step is needed for them.

## Step 4 — verify the round-trip in source-reconstruction

Now switch to the source-reconstruction repo. It has a hand-curated
`.asm` source tree that is **kept byte-identical** with the shipped
bytecode through a CI-style round-trip gate. Each commit must keep
the gate green.

    cd ~/another-world/another-world-source-reconstruction
    make test

`make test` is the default core gate. It runs:

    verify-stages    # per-port .asm round-trip (29/29 stages match)
    verify-unified   # unified .asm.in preprocesses + assembles per arm
                     # (27/27 (unified, port) pairs match)
    lint             # source-tree linters (no `;@raw=` annotations etc.)

A green run means: every `.asm` source file in `src/levels/<port>/`
assembles back to the byte-identical bytecode that shipped in the
original release. So the source tree is a trusted reference.

For the full check including the per-resource md5 audit and the
disasm-level round-trip across all 5 ports' tmp/output trees:

    make test-full

## Step 5 — what to feed your MSX port

Once `make test` is green, you have several artefacts your MSX VM
can consume:

  - `tmp/output/<port>/resources/resource-0xNN.bin` — individual
    resources, one file per memlist entry. The most important types
    for a runtime VM are:
      - `BYTECODE` — the per-level VM bytecode.
      - `POLY_CINEMATIC` / `POLY_ANIM` — polygon shape banks.
      - `PALETTE` — 32 palettes × 16 colours each.
      - `SOUND` / `MUSIC` — Player3 / 8SVX-format audio.
  - `tmp/output/<port>/romset/` — for cartridge ports, a
    `bytecode.rom` + `cinematic.rom` + small auxiliary ROMs.
  - `another-world-source-reconstruction/src/levels/<port>/` — the
    `.asm` source tree, suitable as the primary reference for an
    independent VM implementation. Each opcode is documented in
    `docs/content/engine.md` of the archaeology repo.

A typical MSX-port consumption path:

  1. Use `extract.py` to produce per-resource binaries for the
     release(s) you want to ship.
  2. For each level's `BYTECODE` resource, you can either ship the
     raw bytes (and rely on byte equivalence to play correctly) or
     re-assemble from the `.asm` source if you want to apply patches.
  3. Re-run `make test` after any patch — the round-trip gate is
     your safety net against accidentally producing bytecode the
     real engine can't run.

## How to validate that your VM port runs the original bytecode correctly

The round-trip verify in `make test` only proves that the `.asm`
sources match the shipped bytes. It does NOT prove that your VM
correctly executes them. For runtime verification you'd need to:

  1. Load a bank-format release (e.g. DOS) into your MSX VM.
  2. Compare frame-buffer output against a reference VM (rawgl,
     fbBeRoFiel, or one of the Rust crates in `AWVM_Tools/`).
  3. Compare audio output similarly.

The archaeology repo has tools for some pieces of this (e.g.
`tools/aw_music_to_wav.py` decodes MUSIC resources to WAV via a
Python port of the music decoder), but full runtime parity is out
of scope here — that's the work your port is doing.

## Tooling reference

A few tools you'll probably reach for:

| Tool | Purpose |
|---|---|
| `python3 tools/regen_disasm.py <port>` | Regenerate a port's `tmp/output/<port>/disasm/` tree |
| `python3 tools/issues.py list --status open` | See active research/engineering issues |
| `python3 tools/scan_cross_stage_helpers.py` | Find routines duplicated across stage source files |
| `python3 tools/verify_stage.py` | Per-port `.asm` round-trip (also wrapped by `make verify-stages`) |
| `python3 tools/verify_unified.py` | Unified `.asm.in` round-trip |
| `python3 tests/byte_equivalence.py` (in source-reconstruction) | Standalone test driver — same checks as `make test` with cleaner CI output |

## Where to ask questions

  - Issue tracker: `issues/` directory in the archaeology repo (one file per issue, frontmatter-typed; `python3 tools/issues.py validate` checks integrity).
  - Open-question docs: `docs/content/open-questions/` — research questions that don't yet have answers.
  - The website at `arqueologiadigital.org/another-world-archaeology` renders the archaeology repo's docs/issues as a static site and may be the easiest entry point for cross-port findings (genealogy, cut content, structural-similarity matrix, etc.).

## Strict policies (so you don't get surprises)

  - **Original game files are never committed.** They live only in your local `original_files/<key>/` (or in the sibling `another-world-archive/` private repo if you set that up). Both extract and verify pipelines treat the archive as read-only.
  - **The round-trip gate is mandatory.** Every commit to source-reconstruction must keep `make test` green. If you patch a `.asm`, the assembler emits different bytes, and the gate flags it. Either revert the change or land it together with an updated reference.
  - **AWVM_Tools changes need owner review.** If you find a bug or want to add a feature to `awvm-disasm` / `awvm-asm`, file an issue in the archaeology tracker first describing what you want — the AWVM_Tools owner reviews proposals before any upstream change.

That's it — happy porting.

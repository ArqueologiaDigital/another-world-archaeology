# Research findings

Concrete research outputs. Each finding is tied to a specific
question, cites resource ids and bytecode offsets, and (where the
finding is comparative) records which releases it applies to.

## Findings

- [01 — Gun ammo / shot quota in the bytecode](#/research/01-gun-ammo):
  resolves the original gun-ammo open question. Energy is var `0x06`;
  costs are −1 / −10 / −50 (−100 in Prison) for tap / regular /
  superblast; shield is free; **two recharge zones in level 4 share
  one handler, branching on the scene flag**, both clamping energy
  to 1000; per-level entry values are 199 / 990 / 990. **The
  mechanics are byte-for-byte identical between DOS, Amiga, and
  Genesis-EU** — the first definitive cross-release identity at the
  level of game-mechanic constants we've found.

- [02 — Amiga codewheel protection patch](#/research/02-amiga-codewheel-protection):
  the `amiga-retro-presskit` (2014) and `amiga-archive-org` (2020
  CC0) dumps share 143 of 144 resources byte-for-byte; the
  level-0 BYTECODE differs in 13 bytes. The presskit filename's
  `_nologo_noprotec` confirms the presskit is a copy-protection-
  bypassed variant; the diff cluster at `0x9fc..0xa88` is the
  patched codewheel check.

- [03 — Tier 1 acquisition sweep results (2026-04-30)](#/research/03-tier1-acquisition-sweep):
  the first systematic push to fill out the catalog. Took archived
  coverage from 8/29 → 14/29; 12 of 14 archived fixtures now
  extract end-to-end. Six new fixtures (Apple IIgs WOZ, Mac
  StuffIt, NDS homebrew via Wayback, GBA Foxy port, Apple II
  demake, generic Symbian SIS), two confirmed gaps (clean SNES USA,
  Atari Jaguar), and nine candidate parallel slugs surfaced as
  side findings.

- [04 — 1993 Mac port patch chain (v1.0 → v1.0.2 → v1.0.3)](#/research/04-mac-port-patch-chain):
  diff of the three close-versioned Mac builds shipped together in
  the 1993 StuffIt archive, by per-resource md5 of every CODE
  segment. v1.0 → v1.0.2 was a focused 3-segment bug-fix patch
  (3 of 7 CODE segments byte-identical). v1.0.2 → v1.0.3 was a
  structural reorganisation: every segment hash changed, but
  `cdf752c16d3b...` migrated from `CODE 4` to `CODE 5` (the new
  v1.0.3 CODE 4 is named `MacTraps2_ANSI` — almost certainly a
  Symantec C runtime upgrade). The custom `OOTW` "owner resource"
  records the copyright string, which v1.0.2 changed to mention
  Delphine Software and v1.0.3 reverted.

- [05 — Beetle in the lake stage: dead-coded on every port, hidden on DOS-lineage](#/research/05-beetle-in-the-lake-stage):
  level 2 contains a beetle creature with walking, wing-opening,
  and flipping-upside-down animations plus a kick-detector
  channel — but **two stacked gates make the full interaction
  unreachable in the official releases of every port**.
  **Gate 1** (channel `0x2E`, present on **all** ports) registers
  the kick-detector and then immediately overwrites it with a
  cleanup watcher, so Lester's kicks never connect to the beetle.
  **Gate 2** (channel `0x09`, DOS / SNES-EU / Genesis-EU / GBA
  only) additionally kills the rendering thread, so the beetle
  isn't even visible on those ports. Amiga (and Atari ST) lack
  gate 2, so the beetle *walks visibly* across the scene — but
  kicks still don't connect (gate 1 applies there too). A 2-byte
  verification hack in the
  [`another-world-hacks`](https://github.com/ArqueologiaDigital/another-world-hacks)
  repo patches gate 1 on Amiga, revealing what the kick interaction
  *was supposed to do*: hostile return pass, collision, and a
  death cutscene that hangs the VM (the actor draws were never
  wired in). Strongest signal yet that gate 1 is **intentional**
  cover for broken-by-design content, not an authorial accident.
  The beetle's polygon data is byte-stable across ports.

- [11 — Unused-music scan & rendered cut-content gallery](#/research/11-unused-music-scan):
  systematic counterpart of research/06 for the audio side. The
  shipping AW soundtrack has only 2 music tracks (intro `0x07`,
  ending `0x8A`); the rest of the game is scored by sound-effect
  stingers over silence. A third track, **`0x89`**, is preloaded
  inside an unreachable code block in LAKE.asm and never plays —
  cut content. Rendered to WAV via the new
  `tools/aw_music_to_wav.py` (a Python port of rawgl's
  `sfxplayer.cpp`); listening confirms it as a tense ambient loop
  that fits LAKE's actual narrative (Lester drowning + tentacle
  threat) perfectly. The 12-byte dead-code preload pattern is
  byte-identical across all 5 ports, so the cut goes back to
  Chahi's original 1991 AMIGA release.

- [10 — GBA `LABEL_26A6` mystery solved: 55 KB of trailing data is the level_0 cinematic.rom](#/research/10-gba-cinematic-data-found):
  the unified-INTRO `;@if` block at `LABEL_26A6` showed cartridge's
  trailing-padding (`FILL(55641, 0xFF)`) vs GBA's mysterious 55 KB
  of bytes. A brute-force scan of the GBA ROM finds **a 100 %
  match** (570/570 `CINEMATIC_xxx` addresses land on valid
  polygon-entry bytes) at ROM offset `0x71128` — exactly one byte
  after the GBA's `level_0` bytecode ends. The "trailing data" is
  the **first 55 KB of GBA's level_0 cinematic-polygon slab**.
  AWVM_Tools' `bytecode_chunks` spec for GBA over-extracts:
  it captures bytecode + adjacent cinematic data as one 64-KB
  region. Same recipe finds SNES-EU's level_0 cinematic at ROM
  offset `0x486E0` (95.1 % match). Tracked as issue #0068; once
  fixed upstream, the trailing `;@if` resolves automatically.

- [09 — Phase 3b first cross-branch unification (cartridge ↔ GBA INTRO, then 4-way LAKE)](#/research/09-phase3b-first-unification):
  Started with ONE unified source file
  (`src/levels/_unified/INTRO.asm.in`) producing byte-identical
  bytecode for cartridge_1992 (SNES-EU level_0) and gba_2004
  (GBA level_0). End-to-end verified: preprocessor → awvm-asm →
  byte-match. The pipeline then generalised to N-way folding
  (block-aware), with LAKE now unified across all four branches
  (cartridge_1992 + gba_2004 + chahi_amiga_1991 + dos_1992) at
  362 `;@if` directives — overwhelmingly real semantic
  divergences, not noise.

- [08 — Cross-branch bytecode structural similarity](#/research/08-cross-branch-structural-similarity):
  byte-level diff said the four bytecode branches share no
  byte-identical stages outside SNES↔Genesis. Structural diff
  (tokenize opcodes, ignore addresses) reveals a much richer
  genealogy: the Heineman lineage (DOS → cartridge → GBA) shares
  70-99% structure stage-by-stage; even Chahi → Delphine DOS
  preserves 60-92% of structure. Foxy GBA's level_0 has 0.988
  similarity to cartridge level_0 — Foxy refactored Heineman's
  cartridge bytecode rather than re-implementing. This finding
  motivated the Phase 3b plan that delivered the 4-way LAKE
  unification in finding #09.

- [07 — Bytecode round-trip is byte-identical for 5 ports (29 levels)](#/research/07-bytecode-roundtrip-byte-matching):
  the foundation for the source-reconstruction project. Every
  level we have disassembly for round-trips through awvm-disasm
  → awvm-asm byte-identically: amiga 9/9, msdos 9/9,
  genesis_europe 7/7, snes_eu 2/2, gba_usa 2/2. Bonus: the
  SNES-EU level-1 and Genesis-EU level-0 64-KB cartridge ROM
  chunks are byte-identical, confirming research/05's SNES↔Genesis
  byte-identity finding now at the cartridge-ROM level (not just
  the bytecode resource).

- [19 — Dead bytecode survey: 1,121 transitively-dead labels across 4 ports](#/research/19-dead-bytecode-survey):
  Static reachability survey of every disassembled stage
  across the 4 most-complete ports (`dos_1992`,
  `cartridge_1992`, `chahi_amiga_1991`, `gba_2004`). Builds on
  research/05 (beetle gates) and research/18 (gate inventory)
  by tracing live entry points through call/jmp/branch/setup
  and label-fall-through edges. Surfaces **511** trans-dead
  labels in dos_1992 alone. Headline findings: PASSCODE has
  a complete unused 16-glyph alphabet (CINEMATIC_000..015) —
  the live UI uses a different glyph set (CIN_036+); LAKE's
  43 trans-dead labels are exactly the silenced BEETLE_AI
  subgraph; CAPSULE's 248 trans-dead are likely the entire
  callee tree of the silenced LABEL_5C58 dispatcher.

- [18 — Setup-then-overwrite gate inventory (4 ports × 9 stages)](#/research/18-setup-gate-inventory):
  static survey of the `setup channel=N, address=X; setup
  channel=N, address=Y` idiom across the whole game. **22 gates
  surfaced** total: 12 silencers (7 LAKE beetle gates per
  research/05, plus 5 newly-found CAPSULE/CAVES silencers
  including a queued `CINEMATIC_870..873` frame loop that never
  draws), 3 reschedules, 7 unclassified. Confirms research/05
  quantitatively across all four ports and surfaces additional
  shipped-but-unreachable code paths beyond the beetle stage.
  Foundational input for the reachability oracle (#0058) that
  the asset-scan family (#0054–#0057) needs.

- [17 — VM thread-channel map (per stage)](#/research/17-vm-channel-map):
  static scan of every `setup channel=NN, address=ROUTINE` opcode
  in the unified source (4,082 total) grouped by stage and
  channel. Each AW VM channel (0x00..0x3F) is a separate
  cooperatively-scheduled thread. Surfaces canonical roles
  (`0x3C` is the blit/pause loop with 349 setups; `0x14` is the
  heaviest-used at 466) and per-stage feature wiring (which
  channels host actor animation, music timing, cinematic
  drawing, etc.).

- [16 — Unused PALETTE slots (DOS port)](#/research/16-unused-palettes):
  113 of the 32 × 9 = 288 palette slots across DOS's nine levels
  are never selected by any reachable `setPalette N` opcode.
  Notable: slot 28 is unused in EVERY level; PASSCODE uses only
  2 of 32 (slots 0 and 5); ENDING skips the entire low half.
  Visual catalogue at
  `docs/assets/research-16-unused-palettes/level<N>_<STAGE>.svg`.

- [15 — Unused SOUND resources (DOS port)](#/research/15-unused-sounds):
  4 non-empty SOUNDs (0x2E, 0x37, 0x38, 0x42) are never `play`'d
  OR `load`'d by any DOS bytecode. All one-shot samples,
  0.15-0.67 s. Renders at
  `docs/assets/research-15-unused-sounds/sound_0xNN.wav`.

- [14 — `;@raw=` load-bearing residue: AW VM redundant encodings](#/research/14-raw-annotation-residue):
  documentation of why ~98% of `;@raw=` annotations were
  redundant noise vs the 580-strong load-bearing residue, which
  cluster in three patterns (video alt-zoom-bit, bankSwitch
  legacy operand, setPalette palette-0 trailing-0). Drove the
  `;@enc=…` migration (`;@raw=` is now strictly forbidden).

- [13 — Cross-release md5 index of extracted resources](#/research/13-cross-release-md5-index):
  Amiga 1991 → DOS 1992 reused 117 / 144 resources verbatim and
  rebuilt exactly the per-stage triplet (PALETTE + BYTECODE +
  POLY_CINEMATIC) for all 9 stages. 0 Amiga-only resources;
  2 DOS-only (POLY_ANIM at 0x12, 0x13). dos↔msdos extractions
  agree byte-for-byte across all 146 indices.

- [06 — Unused-polygon survey (level 2 first pass)](#/research/06-unused-polygons-survey):
  **64 polygons in Amiga level 2 + 57 in DOS level 2 are not
  referenced from any bytecode `video` call** and aren't children
  of any referenced group polygon — i.e. shipped-but-unused
  content. **46 of the unused solids are byte-identical across
  both ports**; **13 of the unused groups are shape-identical**.
  Strongest cut-content signal yet. **Top candidate for the
  missing beetle-attacker frames (issue #0053): the unused group
  at Amiga `0x008f1a` / DOS `0x007b0a`** (166×74, 12 paths,
  4 colours) — owner-identified by visual inspection as
  resembling a larger beetle. Palette-sweep tool
  (`tools/render_at_all_palettes.py`) renders any polygon at all
  32 palettes for definitive identification.

## Convention

Each finding lives at `docs/content/research/<NN>-<slug>.md`. The
filename is fixed once published; subsequent corrections happen
in-place (with a changelog at the bottom of the document).

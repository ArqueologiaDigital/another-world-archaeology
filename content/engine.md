# Engine architecture

A working cheat-sheet of the Another World VM. Compiled from the
per-format extractor modules (`extractors/dos_bank.py`,
`extractors/amiga_adf.py`, etc.) and the AWVM_Tools Rust toolchain
(disassembler, polygon decoder, ROM-set extractors). **This is a
working draft and may be incomplete or wrong in places** —
corrections welcome; the file is the source of canonical names
that flow into `symbols/_base.yaml`.

## The 30-second overview

The game is a stack of **resources** (binary blobs in compressed
banks) plus a tiny **virtual machine** that executes a custom
bytecode. The bytecode draws polygons, plays sounds, manages
multi-threaded execution, and reads input — that's it. There is no
"engine code" in the binaries beyond the VM dispatcher; everything
the player sees is data.

This means **every release ships the same VM (with port-specific
quirks) and largely the same bytecode/resources**. Comparative
analysis across releases is therefore a comparison of bytecode and
resource bytes, with the VM serving as a stable interpretation
layer.

## Resources

Every release exposes its content as a flat list of resources. Each
resource has one of seven types (defined in
`extractors/dos_bank.py` and mirrored across the other extractors):

| ID | Name | Notes |
|---|---|---|
| 0 | `SOUND` | One-shot sound effect samples. |
| 1 | `MUSIC` | Tracker-style music modules. |
| 2 | `POLY_ANIM` | Foreground/sprite polygon banks (Lester, enemies, scene props). |
| 3 | `PALETTE` | 16- or 32-colour palettes used by the renderer. |
| 4 | `BYTECODE` | Per-level VM program. The actual game logic. |
| 5 | `POLY_CINEMATIC` | Cinematic/background polygon banks (cutscenes, intro). |
| 6 | `UNKNOWN` | Engine-internal or unused entries seen in some releases. |

The DOS layout uses `memlist.bin` + a handful of `bank<NN>` files;
each entry in `memlist.bin` records `bankId`, `bankOffset`,
`packedSize`, `size`, and `type`. If `packedSize == size` the
resource is stored raw; otherwise it is run through the
backwards-consuming bit-stream decoder (in AWVM_Tools'
`prepare_bank_romset` Rust module, called from
`extractors/dos_bank.py`). Other release formats (Amiga ADF,
Windows PAK, SNES / Genesis / GBA cartridge ROMs, Atari ST Pasti,
3DO, etc.) repackage the same logical resources differently and
have their own per-format extractor modules under `extractors/`.
See [Format coverage](#/coverage) for the current per-format
status.

## Game variables

The VM exposes **256 game variables** indexed `0x00..0xff`, each a
**16-bit signed integer**. Variables are global within a
running level. Most carry no fixed meaning, but a handful are
reserved by the engine and others are conventionally re-used by the
game's own code:

| Index | Name | Notes |
|---|---|---|
| `0x01` | `LESTER_X_COORDINATE` | Range 0..320 (screen width). |
| `0x02` | `LESTER_Y_COORDINATE` | Conventional; needs verification. |
| `0x3c` | `RANDOM_SEED` | RNG seed. |
| `0xda` | `LAST_KEYCHAR` | Last key pressed. |
| `0xe5` | `HERO_POS_UP_DOWN` | Vertical input axis. |
| `0xf4` | `MUS_MARK` | Music synchronization mark. |
| `0xf9` | `SCROLL_Y` | Scrolling offset. |
| `0xfa` | `HERO_ACTION` | Action button state. |
| `0xfb` | `HERO_POS_JUMP_DOWN` | Jump/down chord state. |
| `0xfc` | `HERO_POS_LEFT_RIGHT` | Horizontal input axis. |
| `0xfd` | `HERO_POS_MASK` | Combined position bits. |
| `0xfe` | `HERO_ACTION_POS_MASK` | Combined action+position bits. |
| `0xff` | `PAUSE_SLICES` | Frame-pause counter. The main "wait" knob the bytecode tweaks to slow down/speed up. |

A few variables are **reused with different meanings across game
stages** — e.g. on stage 2 var `0x2a` reads as `CURRENT_SCENE` and
var `0x66` as `CURRENTLY_CACHED_RENDERING_OF_SCENARIO_BACKGROUND`.
The symbols file therefore needs per-stage scopes, not just per-
release scopes.

The full table lives in
`AnotherWorld_VMTools/awvm-disasm.py:SPECIAL_PURPOSE_VARS` and is
the seed for `symbols/_base.yaml`.

## Channels (threads)

Execution is split across **multiple channels** (typically ~64,
indexed by id). Each channel has its own program counter and runs
the VM's bytecode independently; they cooperate via the shared
variable bank. Relevant opcodes:

- `setVec <channel> <addr>` (`0x08`) — set a channel's PC; effectively
  "spawn" or "redirect" a thread.
- `freezeChannel <channel>` (`0x0c`) — pause a channel without losing
  its PC.
- `killChannel <channel>` (`0x11`) — terminate a channel.
- `break` (`0x06`) — yield from the current channel (cooperative
  scheduling: each channel runs until it `break`s).

The classic Another World layout dedicates particular channels to
particular jobs (input handling, music, hero-state machines,
enemy AI, environment animations) but the assignment is convention,
not engine-enforced.

## Opcode set

Opcodes are 1 byte, with operands following. The high bits select
between three families:

- `0x00..0x1b` — **control / arithmetic / I/O instructions** (table
  below).
- `0x40..0x7f` — **video draw**, with palette select. Operand byte
  encodes the polygon address; immediate-mode flags pack
  position and scale information into the opcode itself.
- `0x80..0xff` — **video draw**, simple form (no explicit palette).

### Control / arithmetic / I/O

| Opcode | Mnemonic | Purpose |
|---|---|---|
| `0x00` | `movConst` | `var <- imm16` |
| `0x01` | `mov` | `varA <- varB` |
| `0x02` | `add` | `varA <- varA + varB` |
| `0x03` | `addConst` | `var <- var + imm16` |
| `0x04` | `call` | Jump-and-link (push return). |
| `0x05` | `ret` | Pop return address. |
| `0x06` | `break` | Yield current channel. |
| `0x07` | `jmp` | Unconditional jump. |
| `0x08` | `setVec` | Start/redirect a channel. |
| `0x09` | `djnz` | Decrement var, jump if non-zero. Standard counted-loop primitive. |
| `0x0a` | conditional jump | Sub-condition encoded in next byte (eq, ne, gt, lt, ge, le; var-vs-var or var-vs-imm). |
| `0x0b` | `setPalette` | Load a palette resource. |
| `0x0c` | `freezeChannel` | Pause a channel. |
| `0x0d` | `selectVideoPage` | Choose draw target. |
| `0x0e` | `fillVideoPage` | Solid-fill a page with a color. |
| `0x0f` | `copyVideoPage` | Page-to-page copy. |
| `0x10` | `blitFrameBuffer` | Present current page to the screen. |
| `0x11` | `killChannel` | Terminate a channel. |
| `0x12` | `text` | Draw a text string at coords. |
| `0x13` | `sub` | `varA <- varA - varB` |
| `0x14` | `and` | bitwise AND |
| `0x15` | `or` | bitwise OR |
| `0x16` | `shl` | shift left |
| `0x17` | `shr` | shift right |
| `0x18` | `play` | Trigger a sound resource. |
| `0x19` | `load` | Page in a resource into its target bank. |
| `0x1a` | `song` | Trigger a music resource. |
| `0x1b` | `gameover` | SEGA Genesis-specific. |

### Video draw families

The video opcodes (`0x40..0xff`) are dense bit fields where the
opcode byte itself encodes:

- The polygon address (low bits, scaled `<<1` for the cinematic
  bank).
- Whether `x`, `y`, and `zoom` are immediate or come from variables.
- Whether the palette comes from the opcode or from a previously-set
  palette.

The exact bit layout is implemented in `awvm-disasm.py:disasm_instruction`.

## Video model

Four off-screen video pages plus a frame buffer. A typical drawing
loop is:

```
selectVideoPage <work>
fillVideoPage <work> <color>
... draw polygons into <work> ...
copyVideoPage <work> -> <front>
blitFrameBuffer <front>
break
```

Pages are typically used for: current frame, previous frame
(scrolling/parallax), background scene cache, scratch.

## Polygon data

Two banks: `POLY_ANIM` (foreground / animated sprites) and
`POLY_CINEMATIC` (background and cutscenes). Each bank is a
flat sequence of polygon records keyed by byte offset. A draw
opcode references a polygon by `(bank, offset)`.

A polygon record's structure (per `decode_polygons.py`): a header
byte indicating either a single shape (with bbox + colour + vertex
list) or a group of sub-shapes recursively positioned relative to
the parent. Up to ~50 vertices per shape. Vertices are 8-bit signed
deltas from the bbox centre, scaled by the draw opcode's `zoom`
parameter (default `0x40` = 1.0).

Per-stage **labelled cinematic entries** (e.g.
`WALKING_FEET_ARRIVING_*`, `DNA_*`, `CARKEY`) are documented in
the AWVM_Tools Rust crate (per-release `KNOWN_LABELS` tables in
`awvm/src/releases/<port>.rs`). Those labels form the seed of the
symbol map for cinematic addresses and feed back into the unified
source-reconstruction project.

## References

- `extractors/dos_bank.py` — the DOS bank reader.
- `extractors/amiga_adf.py`, `cartridge_rom.py`, `atari_st_pasti.py`,
  `three_do_opera.py`, etc. — the other per-format extractors.
- [`AnotherWorld_VMTools`](https://github.com/felipesanches/AnotherWorld_VMTools) —
  Rust toolchain: disassembler, assembler, polygon decoder, video
  bit-field layout, per-release ROM-set extractors, `KNOWN_LABELS`
  tables.
- Fabien Sanglard, *Another World: Code Review* — independent
  reverse-engineering writeup that overlaps and cross-checks the
  above (URL not pinned; consult only as a sanity check, not as a
  primary source for symbol decisions).

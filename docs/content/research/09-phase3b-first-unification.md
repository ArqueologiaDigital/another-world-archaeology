# 09 — Phase 3b first cross-branch unification (cartridge ↔ GBA INTRO)

**Date**: 2026-05-01.

## Question

Research/08 showed the Heineman cartridge ↔ Foxy GBA INTRO has 0.988
structural similarity. Can we author **one source file** that produces
byte-identical bytecode for both branches via the conditional-
compilation pipeline (research/07's preprocessor)?

## Method

`tools/unify_asm.py` runs `difflib.SequenceMatcher` on two .asm files
and emits a unified `.asm.in` where matching blocks appear once,
divergent blocks are wrapped in `;@if BRANCH == "<a>"` /
`;@elif BRANCH == "<b>"` / `;@endif` directives.

Then `tools/awvm_preprocess.py` evaluates the conditionals against
each target's `releases/<target>.flags` and emits a per-branch `.asm`
ready for `awvm-asm`.

## Result

ONE source file `src/levels/_unified/INTRO.asm.in` (in source-
reconstruction repo) produces:

| Target | Expected md5 | Got md5 | Match |
|---|---|---|---|
| `heineman_cartridge` (SNES-EU level_0 chunk) | `93959756ff10…` | `93959756ff10…` | ✅ |
| `foxy_gba_2004` (GBA level_0 chunk) | `c978f22c86b7…` | `c978f22c86b7…` | ✅ |

Source statistics:

- 3361 equal lines (shared verbatim)
- 7927 lines per branch in 626 diff blocks
- Total: 21,093 lines (one source for two ports)
- Overhead vs single per-port source: **+46.5%**

So the unified file is ~1.5× the size of one branch's source. In
exchange, it expresses both branches simultaneously with the
genealogy made visible (each `;@if` block IS a divergence point
between the cartridge and GBA branches).

## What this proves

1. **The Phase 3b preprocessor + assembler pipeline produces
   byte-matching output for two divergent branches from a single
   unified source.** End-to-end verified.
2. **The 0.988 structural-similarity number is corroborated**:
   ~3361 / 11288 ≈ 30% of the lines are byte-identical at line
   level (lower than the opcode-level 99% because operand byte
   differences put adjacent lines in the diff blocks). The opcode-
   level structural similarity is the right metric for "what fraction
   of the program is shared logic"; the line-level diff is a
   pessimistic but easier-to-compute proxy.
3. **The diff blocks are mostly small** (averaging ~25 lines per
   block). The unified source is thus straightforward to read —
   each `;@if` is a localised cartridge-vs-GBA decision, not a
   massive structural fork.

## What's still pending

- **N-way unification** (e.g., `dos_1992 + heineman_cartridge +
  foxy_gba_2004` together): the naive 2-way folded approach fails
  because the directives emitted by the first merge become "lines"
  that the second merge tries to align, producing wrong wrapping.
  A correct N-way unifier needs a synchronised matcher across all
  inputs simultaneously. Deferred.
- **Other Heineman-lineage stages**: LAKE (0.92 sim), PRISON
  (0.68), CAVES (0.72), TANK (0.67), etc. should be unifiable
  pairwise the same way.
- **Atari ST**: when its memlist parser lands (issue #0004),
  Atari ST should share Amiga's chahi_1991 sources verbatim — no
  unification work required, just point the new port at the
  existing chahi_1991/<stage>.asm files.

## Tools

- `tools/unify_asm.py` — emits unified .asm.in from two divergent
  .asm files.
- `tools/awvm_preprocess.py` — evaluates conditional directives.
- `tools/verify_stage.py` — byte-match verifier (works on
  preprocessed .asm).

## Changelog

- **2026-05-01** — initial finding. Cartridge ↔ GBA INTRO is the
  first real cross-branch bytecode unification: one source,
  two byte-matching targets.

## Update (2026-05-01) — label canonicalization reduces ;@if blocks 10.5%

Adding a canonicalization pre-pass before unification reduces the
diff-block count by surfacing **synonym labels**: pairs of EQU
labels with **different names but the same offset** in the two
branches' EQU tables.

`tools/canonicalize_labels.py` finds these synonym pairs and
picks the **more descriptive** name (more underscore-separated
alphabetic components; tie-break: longer total length). Then it
find-and-replaces the less-descriptive name throughout each
source.

Example:

```
cartridge:  CINEMATIC_054                 EQU 0x0F72
gba:        CINEMATIC_WALKING_FEET_ARRIVING_0  EQU 0x0F72
```

Both names refer to the same polygon at offset `0x0F72`. The GBA
name is more descriptive (4 alpha components vs 1). After
canonicalization, both files use `CINEMATIC_WALKING_FEET_ARRIVING_0`.
The synonym becomes invisible to the unifier.

Results for cartridge ↔ GBA INTRO:

| | Before canonicalization | After canonicalization |
|---|---|---|
| EQU synonym pairs | 64 | 0 (resolved) |
| Diff blocks | 626 | **560** (-10.5%) |
| Equal lines | 3361 | **3491** (+130) |
| Unified file size | 21,093 | 20,765 |
| Overhead vs single source | +46.5% | +45.6% |

Both branches still byte-match their expected cartridge chunks
after the full pipeline:
canonicalize → unify → preprocess → assemble.

## Update (later 2026-05-01) — inline-label canonicalization halves ;@if blocks

After EQU-synonym canonicalization, most remaining diff blocks
were **inline label** divergences: `LABEL_NNNN:` definitions
that name the same logical routine across branches but use
different addresses (because the bytecode is laid out at slightly
different offsets per port).

Example diff block (single-line replace):

```
< LABEL_0090:
> LABEL_0096:
```

`LABEL_0090` (cartridge) and `LABEL_0096` (GBA) define the same
logical routine — only the address differs.

`tools/canonicalize_inline_labels.py` finds these via difflib
structural alignment: for each `replace` diff block, if both sides
contain matching N `LABEL_<HEX>:` definition lines at
corresponding positions, they're synonym pairs. The tool picks
the alphabetically smaller name as canonical and renames in the
target branch (with conflict detection: skip the rename if the
canonical name already exists in the target branch for a different
offset).

Final results after both canonicalization passes (EQU + inline)
on cartridge ↔ GBA INTRO:

| Stage | Diff blocks | Equal lines | Unified size | Overhead |
|---|---|---|---|---|
| Original | 626 | 3,361 | 21,093 | +46.5% |
| + EQU canonicalization | 560 (-10.5%) | 3,491 | 20,765 | +45.6% |
| **+ inline-label canonicalization** | **311 (-50.3% from original)** | 5,124 | **19,694** | **+42.7%** |

**324 inline labels** were renamed (all on the GBA side — its
auto-generated label names happened to be alphabetically larger,
so the cartridge names won as canonical). 10 pairs were skipped
due to conflicts.

End-to-end byte-match verification still passes for both targets.
The pipeline is now:

```
per-branch .asm files
        ↓ canonicalize_labels.py        (EQU synonyms by offset)
EQU-canonicalized .asm files
        ↓ canonicalize_inline_labels.py (inline labels by structural alignment)
fully-canonicalized .asm files          ← committed in src/levels/_canonicalized/
        ↓ unify_asm.py                  (difflib + ;@if/;@elif/;@endif)
unified .asm.in                          ← committed in src/levels/_unified/
        ↓ awvm_preprocess.py            (per-branch flag evaluation)
per-branch .asm
        ↓ awvm-asm
.bin == original bytecode chunk         ← byte-match verified
```

## Caveat: `awvm-asm` `bankSwitch` encoding bug

While developing this pipeline, an attempted optimization
(`--strip-raw-comments` flag in `unify_asm.py` to drop
`;@raw=...` annotations during diff) revealed a bug in
`awvm-asm`: the `bankSwitch N` mnemonic encodes incorrectly
when no `;@raw=` annotation is present.

```
bankSwitch 1                       → 0x19, 0x3E, 0x81  (WRONG)
bankSwitch 1   ;@raw=0x19,0x07,0xD1 → 0x19, 0x07, 0xD1  (correct, via override)
load id=0x07D1                     → 0x19, 0x07, 0xD1  (correct, no override needed)
```

The `;@raw=` annotation appears to function as an override that
masks the bug. So unified sources MUST keep `;@raw=` annotations
for now (the `--strip-raw-comments` flag is not safe to use
until the bug is fixed). Tracked as
[issue #0066](#/issues).


## Update (later 2026-05-01) — selective `;@raw=` strip drops blocks 94%

The `;@raw=` annotation is an assembler override: when present,
`awvm-asm` uses the bytes from the comment instead of computing
them from the mnemonic. For most mnemonics, `awvm-asm` computes
the bytes correctly anyway, so `;@raw=` is redundant. But for
**three specific mnemonics**, the assembler mis-encodes without
the override:

- `bankSwitch` (encoding bug)
- `setPalette` (encoding bug)
- `video` (encoding bug)

Discovery: per-mnemonic survey on the cartridge INTRO source —
strip `;@raw=` from one mnemonic's lines at a time and assemble.
22 of 25 mnemonics are safe to strip; only those 3 mis-encode.
Tracked as [issue #0066](#/issues).

So we can strip `;@raw=` from ~95% of source lines (everything
except `bankSwitch` / `setPalette` / `video`) without changing
the assembled bytes.

Most diff blocks remaining after EQU + inline-label canonicalization
were lines that **only differed in `;@raw=`** — i.e. the same
opcode + operand was assembled to slightly different bytes per
port (e.g., a `setup channel=0x09, address=…` referencing a
routine at a different bytecode offset on each port). Stripping
those `;@raw=` annotations makes those lines compare equal during
unification.

`unify_asm.py` now defaults to selective strip when
`--strip-raw-comments` is given: keeps `;@raw=` on `bankSwitch`,
`setPalette`, `video` lines; strips elsewhere.

**Final results — full pipeline on cartridge ↔ GBA INTRO:**

| Stage | Diff blocks | Equal lines | Unified size | Overhead |
|---|---|---|---|---|
| Original | 626 | 3,361 | 21,093 | +46.5% |
| + EQU canonicalization | 560 (-10.5%) | 3,491 | 20,765 | +45.6% |
| + inline-label canonicalization | 311 (-50.3%) | 5,124 | 19,694 | +42.7% |
| **+ selective strip-`;@raw=`** | **39 (-93.8% from original)** | 11,070 | **18,402** | **+38.7%** |

**Both branches still byte-match.** From 626 conditional blocks
down to **39** — the unified file is now overwhelmingly shared
content with rare per-branch overrides.

The 39 remaining blocks are real semantic divergences:
- Different routine bodies between cartridge and GBA
- Inline string-table comments inside `text` opcodes (which we
  intentionally don't strip; per-branch strings differ)
- `bankSwitch`, `setPalette`, and `video` lines whose addresses
  legitimately differ between branches (we keep `;@raw=` for
  these, so they show up as diffs)


## Update (later 2026-05-01) — label-normalized synonym detection

The previous canonicalizer left some pairs unmerged because difflib
was misaligning them. Concretely:

```
;@if BRANCH == "heineman_cartridge"
LABEL_04CF:
;@elif BRANCH == "foxy_gba_2004"
LABEL_04D5:
;@endif
    break
;@if BRANCH == "heineman_cartridge"
    djnz [0x05], LABEL_04CF
;@elif BRANCH == "foxy_gba_2004"
    djnz [0x05], LABEL_04D5
;@endif
```

The two branches use different label names for the same routine
(LABEL_04CF in cartridge, LABEL_04D5 in GBA), but the canonicalizer
hadn't merged them.

**Root cause**: difflib's alignment matched lines like `LABEL_1219:`
in cart against lines like `LABEL_1219:` in GBA — but at *different
logical positions* (the labels happen to have the same name in both
ports, despite labelling different bytecode regions). This forced
the structurally-different surrounding code into `delete`/`insert`
diff blocks that the synonym-pair detector couldn't process.

**Fix**: normalize all `LABEL_<HEX>` tokens to a placeholder `<L>`
during the diff-alignment pass. Now the two label-bearing lines
look identical to difflib (`<L>:` vs `<L>:`), so it aligns by
structural context. After alignment, we recover the original label
names at corresponding positions and pair them.

Plus: cascading-aware conflict resolution. When canonical name X
already exists in the target branch, but X is itself being renamed
away by another pair, the rename is allowed (regex alternation in
`apply_rename` substitutes all tokens in one pass; each occurrence
is matched against the ORIGINAL token, not a freshly-renamed one).

After this fix:

| Stage | Diff blocks |
|---|---|
| Original | 626 |
| + EQU canonicalization | 560 (-10.5%) |
| + inline-label canonicalization (initial) | 311 (-50.3%) |
| + selective strip-`;@raw=` | 39 (-93.8%) |
| **+ label-normalized + cascading-aware canonicalization** | **11 (-98.2% from original)** |

**11 remaining ;@if blocks** are all real semantic divergences:
- 1 cosmetic-only `bankSwitch 1; Prison` vs `bankSwitch 1; Arrival
  at the Lake & Beast Chase` — different inline comments around
  the same `;@raw=` bytes.
- 1 `load id=0x3E82` vs `bankSwitch 2; Prison ;@raw=0x19,0x3E,0x82`
  — same bytes encoded with different mnemonic syntax. Hard to
  canonicalize without recognising the equivalence.
- 4 `db` (raw-byte) lines that differ in specific addresses inside
  data tables.
- 1 `mov [0x01], 0x0012` vs `mov [0x01], 0x0024` — genuinely
  different immediate values.
- 2 large blocks (53 + 328 lines) of code present in cartridge
  but not GBA, and vice versa.
- 1 huge trailing padding block (~6,955 lines of unused 64-KB-chunk
  tail bytes — could be excluded from unification entirely).

The unified file is now **~38.3% larger than a single per-port
source** (down from 46.5%) and contains overwhelmingly shared
content — the `;@if` directives appear only at genuine cross-port
divergences.


## Update (2026-05-01) — bankSwitch canonicalization + inline-comment stripping → 8 blocks

Two more canonicalization passes added:

### 1. `tools/canonicalize_bankswitch.py`

Converts `bankSwitch N` mnemonic to its equivalent `load id=0xXXXX`
form (using the `;@raw=` annotation to determine the exact ID).
Two benefits:

- **Eliminates the encoding bug** (bankSwitch is buggy in awvm-asm
  per #0066; `load id=...` encodes correctly without an override).
- **Unifies syntax differences** — cart used `load id=0x3E82` while
  GBA used `bankSwitch 2; Prison ;@raw=0x19,0x3E,0x82` for the
  same bytes. After canonicalization both use `load id=0x3E82`.

`bankSwitch` is now removed from `unify_asm.py`'s
`RAW_REQUIRED_MNEMONICS` list (only `setPalette` and `video` remain).

### 2. Inline-comment stripping in `unify_asm.py`'s normalizer

Strips `;<text>` inline comments BEFORE `;@raw=` (e.g.,
`bankSwitch 1; Prison ;@raw=...` → `bankSwitch 1 ;@raw=...`).
These are typically port-specific stage names or string-table
content embedded in the disasm output; the assembler ignores
them. Used during diff-alignment so cosmetically-different lines
compare equal.

After both passes:

| Stage | Diff blocks |
|---|---|
| Original | 626 |
| + EQU canonicalization | 560 |
| + inline-label canonicalization (initial) | 311 |
| + selective strip-`;@raw=` | 39 |
| + label-normalized + cascading-aware canonicalization | 11 |
| **+ bankSwitch canonicalization + inline-comment strip** | **8 (-98.7% from original)** |

The 8 remaining blocks are all **genuine semantic divergences**:
- 2 × GBA-only `song id=...` calls (instruments not present in cartridge)
- 4 × `db`-encoded raw bytes that differ in single bytes — these
  are inside data tables / jump tables the disassembler couldn't
  decode. Each differing byte corresponds to a port-specific
  address.
- 1 × different immediate value (`mov [0x01], 0x0012` vs `0x0024`)
- 1 × trailing-padding block (~6,955 lines): cart pads with
  `0xFF`, GBA has different fill content. This is the unused tail
  of the 64-KB cartridge chunk after the actual bytecode ends.

These divergences cannot be eliminated by syntactic canonicalization.
The first three categories require deeper semantic understanding
(re-disassembling raw `db` blocks back into instructions); the
fourth could be handled by truncating to the actual bytecode end
and emitting per-branch tail bytes from the build pipeline.


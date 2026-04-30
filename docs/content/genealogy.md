# Genealogy

The goal: reconstruct a "family tree" of Another World ports — which
release inherited what from which predecessor, where new code was
introduced, and where forks diverged.

## Working hypothesis

Cross-release diffs of disassembled bytecode will reveal **blocks of
new code present in some releases but absent from older sibling
releases**. The location and nature of those blocks is the primary
genealogy signal.

Secondary signals to check as the data fills in:

- Identical-byte resources shared verbatim across releases (auto-
  detected by the extract step — see [Format coverage](#/coverage)).
- Symbol-table or string-table overlaps.
- Bug-for-bug mirroring (a workaround in release A that survives in
  release B is suggestive of B being downstream of A).

## Findings to date

### First cross-release mechanic-constant identity (2026-04-30)

The gun ammo / energy mechanic is **byte-for-byte identical** across
DOS, Amiga (retro-presskit), and Genesis-EU. Variable, costs,
thresholds, recharge clamp, and per-level initial values are all
preserved verbatim — including the level-3-only −100 superblast
cost (vs −50 in levels 4 / 6) which is the kind of small
irregularity a porter would be tempted to "fix" or homogenize. Its
persistence across all three is strong evidence that **Interplay's
1993 Genesis port worked from a snapshot of the existing bytecode
rather than re-deriving the balance numbers** from a design doc.

See [research finding 01](#/research/01-gun-ammo) for the full
constant table and bytecode citations.

### First intra-release diff isolated to a known feature (2026-04-30)

The two Amiga dumps (`amiga-retro-presskit` 2014 vs `amiga-archive-org`
2020) share **143 of 144 resources byte-for-byte**; only the level-0
BYTECODE differs in 13 bytes. The presskit's filename
`_nologo_noprotec` confirms it is a copy-protection-bypassed
variant, and the diff cluster lives at `0x9fc..0xa88` — exactly the
codewheel check.

See [research finding 02](#/research/02-amiga-codewheel-protection)
for the per-resource md5 walk and the disassembly diff.

### First multi-version single-port patch chain (2026-04-30)

The 1993 Mac port ships three close-versioned builds (v1.0 / v1.0.2
/ v1.0.3) plus two updaters in the same StuffIt archive — a
uniquely dense genealogy dataset. The two-stage Mac extraction
pipeline (`mac-stuffit-extract` → `mac-rsrc-walk`) now exposes
every individual `(TYPE, ID)` Mac resource per version.

Per-segment md5 of the seven `CODE` segments across the three
builds reveals two distinct patches:

- **v1.0 → v1.0.2** was a **focused 3-segment fix** — CODE 1, 4, 6
  are byte-identical between v1.0 and v1.0.2; only CODE 2, 3, 5
  changed (and CODE 0, the segment-loader jump table,
  regenerates).
- **v1.0.2 → v1.0.3** was a **structural reorganisation** — every
  CODE-segment hash changed, but the v1.0/v1.0.2 hash
  `cdf752c16d3b...` reappears as v1.0.3's CODE 5 (renamed
  `Histories _ Docs`), with a new v1.0.3 CODE 4 named
  `MacTraps2_ANSI`. Almost certainly a Symantec C runtime upgrade
  shifting all later segments by one.

The `OOTW` custom 4cc resource (the application's "owner
resource") even carries a human-readable copyright string that
changes per version: v1.0 = `©1992 MacPlay.`, v1.0.2 =
`©1992-3 MacPlay and Delphine Software.`, v1.0.3 reverts to
`©1992 MacPlay.`.

See [research finding 04](#/research/04-mac-port-patch-chain) for
the full per-segment table.

### Pre-shipping content cuts visible in the bytecode (2026-04-30)

Level 2 of *Another World* contains a complete walking-beetle
creature with a kick-it-and-it-flies-off animation — wings
opening, wing-flap loop, falling onto its back, then taking off
upside-down. The polygon data and the kick-dispatch bytecode are
**byte-identical between DOS and Amiga**.

But the wing-flip is **never visible in normal play on either
port**, because of two distinct setup-then-overwrite gates added
to the level-entry script:

- **Gate 1 (channel 0x2E, on *both* ports)**: the kick-detector
  thread is registered on channel `0x2E` and immediately overwritten
  by a cleanup-watcher thread on the same channel, so the
  detector never gets a thread to run on. The kicks fire (visibly!)
  but no thread is polling for the kick-connect signal, so the
  wing-flip dispatch never executes.
- **Gate 2 (channel 0x09, DOS only)**: on top of gate 1, the DOS
  port also kills the beetle's rendering channel itself —
  rendering it invisible from the start.

Both gates use the same authorial trick (two consecutive `setup`
calls on the same channel; the second wins). The DOS-only gate-2
is unambiguously deliberate, since the user empirically confirms
the beetle is visible on Amiga but invisible on DOS. Whether
gate-1 is *also* deliberate (a feature cut before initial release)
or an authorial accident (the cleanup watcher could have been put
on a different channel) is currently undecidable — tracked as
[issue #0048](#/issues).

This is the first finding of **pre-shipping content cuts visible
in the bytecode itself**, distinct from per-port editorial cuts.
The original Amiga build *as shipped in 1991* already contains the
gate-1 cut; the DOS port inherits it, plus adds gate-2 of its own.

**Cross-checks across four ports (2026-04-30)**: the gates have
been verified across all four currently-disassembled bank-format
ports.

| Port | Year | Author | Gate 1 | Gate 2 |
|---|---|---|---|---|
| Amiga       | 1991 | Chahi    | yes | no |
| Atari ST    | 1991 | Chahi    | yes | no |
| DOS         | 1992 | Heineman | yes | yes |
| Genesis-EU  | 1993 | Heineman | yes | yes |

Two cleanly distinguishable branches emerge:

- **1991 Chahi master** (Amiga + Atari ST): gate 1 only. The
  Atari ST level-2 bytecode is **byte-identical to Amiga**
  (19,458 bytes, md5 `860362f3718ca4fe4a8e65cdbe40f155`, same
  bank/offset). The 1991 release is a single dev master shipped
  on two SKUs.

- **Heineman lineage** (DOS 1992 + Genesis-EU 1993): gates 1 + 2.
  Cinematic offsets in DOS and Genesis-EU are byte-identical and
  different from Amiga, indicating Heineman built Genesis-EU from
  his DOS port rather than re-deriving from Amiga.

Lineage diagram:

```
Pre-1991 dev build (Chahi):  beetle alive, wing-flip working
        │
        ▼
1991 dual release (Chahi):   gate 1 added — beetle visible, wing-flip silenced
   ├── Amiga                 ↘  byte-identical level-2 bytecode
   └── Atari ST              ↗  (same memlist contents, same bank layout)
        │
        ▼
1992 DOS port (Heineman):    inherits gate 1; adds gate 2 — beetle hidden too
        │                    cinematic resource laid out at new offsets
        ▼
1993 Genesis-EU (Heineman):  inherits gate 1 + gate 2 + DOS cinematic offsets
                             — does NOT re-derive from Amiga
```

See [research finding 05](#/research/05-beetle-in-the-lake-stage)
for the full bytecode trace, kick-detector dispatch logic, take-off
sequence, four-port comparison table, and unlabeled wing-flip
cinematic offsets. Issues #0047 and #0049 closed with these
outcomes; issue #0048 (whether gate 1 is intentional vs accidental)
remains open. The byte-identical Atari ST/Amiga finding doesn't
decide #0048 — both SKUs share the same dev master, so a single
editorial decision (or a single accident) propagates to both.

## Working hypothesis

Cross-release diffs of disassembled bytecode reveal **blocks of new
code present in some releases but absent from older sibling
releases**. The location and nature of those blocks is the primary
genealogy signal.

Secondary signals to check as the data fills in:

- **Identical-byte resources** shared verbatim across releases
  (auto-detected by the extract step — see
  [Format coverage](#/coverage)). Confirmed: see finding 02.
- **Symbol-table or string-table overlaps** — text strings extracted
  from the cartridge ports (Genesis EU `[0x382B, 0x46FE]`, etc.)
  are a parallel comparison axis.
- **Bug-for-bug mirroring**: a workaround in release A that survives
  in release B is suggestive of B being downstream of A. Finding 01
  is a positive instance — the level-3 superblast cost asymmetry
  survives intact across DOS / Amiga / Genesis.
- **Patch deltas as ancestry markers**: the Mac v1.0→v1.0.3 chain
  is the first multi-version-of-one-port material we have; comparing
  what the patches changed is the closest thing to *internal*
  developer changes we can hope to reconstruct.

## Open lines of inquiry

- **SNES / GBA / Apple IIgs cross-checks for var `0x06`.** These
  ports use the abridged 2-level demo engine, so the prison/cave
  levels (where the gun mechanics live) aren't yet disassembled.
  Wiring the full level extraction would close the loop on
  finding 01.
- **Atari ST 1991 bank format.** Same 68000 generation as the
  Amiga. The directory is embedded in `START.PRG`; once parsed,
  Atari ST banks become the closest sibling to the Amiga banks
  for an early-generation comparison.
- **3DO file → AW canonical resource index mapping.** `GameData/FileN`
  + `GameData/song1..30` + `GameData/EndShape1/2` smell strongly
  like a structured resource set — the mapping needs reverse
  engineering before 3DO bytecode can be passed through `awvm-disasm`.
- **Mac v1.0 / 1.0.2 / 1.0.3 patch-delta analysis.** Awaiting the
  resource-fork walker (forward plan tier A, item 1).

See the [forward plan](#/forward_plan) for the full ranked list.

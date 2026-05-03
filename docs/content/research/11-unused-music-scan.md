# 11 — Unused-music scan & rendered cut-content gallery

## Question

Are there MUSIC resources in the AW resource catalog that the
shipping bytecode never plays via `song id=` — and if so, what
do they sound like? This is the music-side counterpart of
[research/06](#/research/06-unused-polygons-survey)'s unused-polygon
work, and ties into [issue #0055](#/issues/0055-unused-music-scan-enumerate-music-resources-scan-all-reachab)
("unused music scan: enumerate music resources, scan all
reachable bytecode for `song id=` references, flag any that the
engine never triggers").

## Method

1. **Enumerate** every `0xNN-MUSIC.bin` extracted from the per-release
   `bin/` directories (today: only the MS-DOS package
   `076117919d1dca51e486f33b8f7817e3` is fully extracted; other
   ports' extraction is tracked by issues #0008–#0011).
2. **Scan** `src/levels/<branch>/*.asm` across all 4 branches
   (`cartridge_1992`, `gba_2004`, `dos_1992`, `chahi_amiga_1991`)
   for two opcodes:
   - `song id=0xNNNN, delay=…, pos=…` — actually starts playback
   - `load id=0xNNNN` — preload only; auto-plays MUSIC resources
     unless the runtime path doesn't reach the load
3. **Classify**: `song`-referenced = used; `load`-only = "preload but
   never explicitly played" (which on its own would be enough,
   since `load id=` of a MUSIC resource auto-plays it — *unless
   the load is dead code*).
4. **Render** any flagged-as-cut MUSIC to WAV via
   `tools/aw_music_to_wav.py` (a Python port of rawgl's
   `sfxplayer.cpp`) so we can listen and confirm the
   archaeological reading.

## Initial scan results — MS-DOS 1992 package

The MS-DOS package contains exactly **3 MUSIC resources**:

| ID     | Used by `song id=`              | Used by `load id=`              | Verdict |
|--------|---------------------------------|---------------------------------|---------|
| `0x07` | INTRO (cart, gba, dos, amiga)   | INTRO (cart, gba, dos, amiga)   | **used** — title / intro theme |
| `0x89` | *never*                         | LAKE (cart, gba, dos, amiga)    | **CUT** — preloaded behind `jmp`, never plays |
| `0x8A` | ENDING (cart, dos, amiga)       | ENDING (cart, dos, amiga)       | **used** — end-credits theme |

Note `0x8A` is missing from `gba_2004` because the Foxy GBA 2004
port is incomplete: `src/levels/gba_2004/` only has `INTRO.asm`
and `LAKE.asm`, no `ENDING.asm` (or any of the other 6 stages).

The whole shipping AW soundtrack has only **two** music tracks
(intro + end credits) plus this unused third one. The rest of
the game is scored entirely with sound-effect stingers — no
sustained background music. That sparse audio design is widely
considered one of AW's signature atmospheric choices.

## The cut track: music 0x89

`0x89` is loaded but never played, and only because the
load itself sits inside an unreachable code block in LAKE.asm:

```asm
    jmp INIT_AUDIO_AND_SCENE_AFTER_LOADS
    load id=0x0089       ; MUSIC — this music
    load id=0x0002       ; SOUND — instrument 0 of music 0x89
    load id=0x0081       ; SOUND — instrument 2 of music 0x89
    load id=0x0003       ; SOUND — instrument 1 of music 0x89
INIT_AUDIO_AND_SCENE_AFTER_LOADS:
    play id=0x0030, freq=0x00, vol=0x00, channel=0x00
    ...
```

The 4 unreachable loads are exactly the music plus its 3
instrument samples (the instrument table inside `0x89-MUSIC.bin`
references SOUND IDs `0x02`, `0x03`, `0x81` — see
[issue #0076](#/issues/0076-lake-dead-code-preload-music-0x89)
for the full decode). It's a coherent preload sequence that was
disabled by a simple `jmp` over it. The same 12-byte dead-code
pattern is byte-identical across all 5 ports' LAKE bytecode,
which means it was already in Eric Chahi's original 1991 AMIGA
release and got copied verbatim into every later port.

## Listening note

After rendering: it **feels very tense** — high-anxiety ambient
loop, not a melody. That fits LAKE's actual narrative perfectly:
LAKE is the very first playable scene, where Lester appears
underwater after the lab teleporter accident and must swim to the
surface or drown, then is attacked by a tentacled creature
reaching up from the depths trying to drag him back down. A
sustained tense ambient track over that sequence is exactly the
kind of cue you'd commission for it.

The shipping version cut the music and relies on silence
punctuated by sound-effect stingers (the slug-attack
`play id=0x4F`, the drowning thuds, the underwater gurgle) to
carry the tension. Whether that was a memory/performance
decision or an authorial taste call, we don't know — but the
shipped silent-with-stings approach is one of AW's most
recognizable atmospheric signatures, so the cut probably
*was* the right artistic call even though the cue itself is
strong on its own.

## Audio gallery

The cut-content rendering, as it would have played at LAKE
startup if the `jmp` were removed:

[Music 0x89 — LAKE cut ambient (26.5 sec, mono PCM, 22050 Hz)](assets/research-11/lake_dead_music_0x89.wav)

The two shipped tracks (`0x07` intro and `0x8A` ending) are not
embedded here — they're widely available elsewhere as part of the
released soundtrack — but they were rendered locally as
ground-truth checks of `tools/aw_music_to_wav.py`, and both
produced recognisable, clean-sounding output. The renderer's
correctness on those known tracks gives confidence in the `0x89`
rendering being faithful to what the cut version would have
sounded like.

## Method limitations

- **Only the MS-DOS package is fully extracted today.** Other
  ports may have additional MUSIC resources at different IDs;
  we won't know until issues #0008–#0011 (Mac/Apple-IIgs/Symbian
  extractors) and #0012–#0014 (Sega CD / SNES / Atari Jaguar
  acquisitions) close. The "3 music tracks" finding is
  specifically MS-DOS 1992 + branches that share its bytecode.
- **`load id=` semantics need verification.** rawgl's
  `Resource::loadResourcesFromList` does auto-play MUSIC, but the
  exact runtime conditions (whether the preceding `play id=0x30,
  freq=0x00, …` "silence stingers" interfere) deserve a
  closer read of the engine source.
- **No re-extraction on dead-code-removed bytecode** — strictly
  speaking, the only definitive way to confirm 0x89 is "what would
  have played" is to patch the LAKE bytecode (replace the `jmp`
  with NOPs), assemble, run in an emulator, and record. Today we
  rely on the renderer's correctness on the two ground-truth
  tracks to accept the standalone WAV as faithful.

## Next steps

- Run the same scan after each new port extraction lands, so
  port-specific cut audio gets logged as soon as we have its
  resources.
- Consider porting `tools/aw_music_to_wav.py` to also accept a
  bytecode trace as input — feed it a `song id=…, delay=…, pos=…`
  triple and have it render starting from `pos` at the runtime
  delay override (today's tool needs `--override-delay` passed
  manually).
- Is `0x89` recognisable as something that ever appeared in
  Chahi's drafts / interviews / soundtrack-album outtakes? The
  Eric Chahi documentation set in `references/` may have clues.

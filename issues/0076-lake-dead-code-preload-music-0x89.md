---
id: 0076
title: Investigate LAKE's dead-code preload of music 0x89 + 3 sound instruments
status: open
tier: A
created: 2026-05-03
updated: 2026-05-03
tags: [lake, music, dead-code, archaeology]
---

# Investigate LAKE's dead-code preload of music 0x89 + 3 sound instruments

## Summary

Inside the LAKE setup routine that ends in `INIT_AUDIO_AND_SCENE_AFTER_LOADS`,
there are 4 unreachable `load` instructions sitting between an
unconditional `jmp` and the label that follows it:

```asm
    jmp INIT_AUDIO_AND_SCENE_AFTER_LOADS
    load id=0x0089       ; MUSIC
    load id=0x0002       ; SOUND
    load id=0x0081       ; SOUND
    load id=0x0003       ; SOUND
INIT_AUDIO_AND_SCENE_AFTER_LOADS:
    play id=0x0030, freq=0x00, vol=0x00, channel=0x00
    ...
```

The same byte-identical pattern is preserved in **all 5 ports**
(cart_1992, gba_2004, dos_1992, chahi_amiga_1991, plus
`_phase3b_demo`), strongly suggesting it was already in Eric Chahi's
original 1991 AMIGA bytecode and got copied verbatim into every
later port.

## Why those 4 specific resources

Decoding the header of `076117919d1dca51e486f33b8f7817e3/bin/0x89-MUSIC.bin`:

```
Initial tempo: 0x2F88
Instrument 0: resource 0x0002 (SOUND), vol=0x3F
Instrument 1: resource 0x0003 (SOUND), vol=0x1B
Instrument 2: resource 0x0081 (SOUND), vol=0x2F
```

The 3 SOUND IDs in the dead block are **exactly the 3 sample
instruments referenced by music 0x89's instrument table**. So the
dead block is a coherent preload sequence: load the music + its
3 instruments before the rest of the LAKE init. Disable that block
(as the `jmp` does), and music 0x89 has no instruments and never
gets queued for playback.

## Cross-cutting observations

- `song id=0x0089` does not appear in **any** branch's source
  (verified by `grep -rE "id=0x0089" src/`). So the only path that
  could have triggered playback is the `load id=0x0089` in the dead
  block — `load` of a MUSIC resource is documented (fbBeRoFiel docs)
  to auto-start the song with default tempo.
- 0x02 and 0x03 are also referenced by `play id=` instructions in
  INTRO.asm (gba/cart). 0x81 is also referenced in cart's ENDING.asm.
  So three of the four are "real" audio resources used elsewhere;
  0x89 itself is the only one that's effectively unused in shipping
  bytecode.
- The dead block being byte-identical across cart/dos/gba/amiga is
  itself archaeologically interesting: every port's bytecode
  retransmits this 12 bytes of dead instructions rather than
  optimizing them out.

## Open questions

1. **Is music 0x89 a recognizable AW track?** Other music IDs
   (0x80, 0x82, 0x86, etc.) correspond to known cues — protection
   screen, intro, beast surprise, etc. We don't know what 0x89
   sounds like or where in the soundtrack it would have fit.

2. **Why was it disabled?** Plausible hypotheses:
   - **Performance**: preloading 4 resources took too long during
     LAKE startup; Chahi added the `jmp` to skip them and rely on
     just-in-time loading via `play id=`.
   - **Authorial change**: the LAKE level was originally designed
     to have ambient music that was later cut.
   - **Memory pressure**: the music + 3 samples may have collided
     with another resource bank.

3. **Was 0x89 ever heard in any released version?** Checking other
   ports' LAKE bytecode (Atari ST, Apple IIgs, Mac, Genesis,
   Symbian, etc.) for the absence/presence of the `jmp` would
   tell us whether any port shipped with the music enabled.

4. **Does the AMIGA disk have a DMS/preserved earlier version**
   where the `jmp` is missing? The bonus disk
   (`5dca377e0e1506d5cf83317b1495f3e8/AnotherWorld_DiskA_nologo_noprotec.adf`)
   is one to check.

## How to actually hear it

Option A: **patch + emulate.** Run the msdos package through an AW
engine emulator (e.g., rawgl, fbBeRoFiel) with a small bytecode
patch removing the `jmp` (or replacing it with `nop nop nop`). The
4 loads then execute and music 0x89 starts. Verify that the music
plays and record it.

Option B: **standalone music converter.** rawgl ships a CLI
`AWMusicToWAV` (or similar) that takes an instrument table + a
music resource and renders to WAV. Locate or port that tool, feed
it `0x89-MUSIC.bin` + `0x02-SOUND.bin` + `0x03-SOUND.bin` +
`0x81-SOUND.bin`, and listen.

Option B is cleaner because it doesn't require a full engine and
can be reproduced deterministically.

## Acquisition status

We have the msdos package's resources fully extracted:
- `076117919d1dca51e486f33b8f7817e3/bin/0x89-MUSIC.bin` (2240 bytes,
  md5 `f8c2b0fa3d27...`)
- `076117919d1dca51e486f33b8f7817e3/bin/0x2-SOUND.bin`
- `076117919d1dca51e486f33b8f7817e3/bin/0x3-SOUND.bin`
- `076117919d1dca51e486f33b8f7817e3/bin/0x81-SOUND.bin`

Other ports' resources are not yet extracted (issue #0009 et al.
cover format-specific extraction work).

## Action items

1. ~~Render music 0x89 to WAV using one of the methods above.~~
   **Done.** Wrote `tools/aw_music_to_wav.py`, a Python AW music
   renderer based on rawgl's `sfxplayer.cpp` semantics (Amiga
   period→Hz, 4-channel mixing, sample looping, volume effects).
   Rendered output is at `tmp/rendered_audio/lake_dead_music_0x89.wav`
   (26.5 sec, 22050 Hz mono, peak ~10k of 32k = comfortable
   headroom).

   Stats from the music header:
   - Initial delay: 0x2F88 (104 ms/row)
   - 4 patterns × 64 rows × 4 channels = 16384 events total
   - Order table: `[0x00, 0x01, 0x01, 0x01]` — pattern 0 once,
     then pattern 1 three times. Total length: 256 rows × 104 ms
     ≈ 26.5 seconds.

   Verified the renderer against two known AW music tracks
   (0x07 and 0x8A) — both render to plausible audio (peak/rms
   sensible, ≥72% non-zero samples).

2. Cross-check whether other ports' LAKE bytecode also has the
   `jmp` (i.e., whether the disable is universal or AMIGA-introduced
   and inherited).
3. Compare 0x89 against the released soundtrack (Eric Serra's
   AW soundtrack album, plus any in-game music heard) — does it
   match anything we know, or is it genuinely unreleased?
4. Consider adding a "render dead-code" mode to the future
   audio-asset cataloger: any MUSIC resource that no `song id=` /
   reachable `load id=` triggers should be flagged as cut content.

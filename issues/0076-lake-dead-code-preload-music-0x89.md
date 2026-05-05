---
id: 0076
title: Investigate LAKE's dead-code preload of music 0x89 + 3 sound instruments
status: done
tier: A
created: 2026-05-03
updated: 2026-05-05
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

## Listening note (Felipe, 2026-05-03)

After rendering: **"the song feels very tense"**.

This fits the actual LAKE scene narrative perfectly. LAKE is the
**very first playable scene of the game**: Lester is teleported
into the alien world after the lab experiment misfires, materializes
underwater inside the lake, and has only seconds to swim to the
surface before drowning. After surfacing, a tentacled creature
(`SNEAKY_TENTACLE_FROM_THE_POOL` in the bytecode) reaches up from
the depths and tries to grab him and drag him back down — that's
what `THE_BEAST_KILLS_LESTER` is the death routine for.

So the LAKE level is high-stakes from the very first frame. A
tense 26-second ambient loop preloaded at level start — for the
underwater swim + the entire tentacle encounter on the shore —
fits exactly.

Revised hypothesis: 0x89 was the **intended opening-scene ambient
theme** for the whole LAKE encounter, scoring the underwater
panic and the tentacle threat. The shipping version cut it and
relies on silence + the stinger-sound effects (e.g., the slug
attack's `play id=0x4F` hits) to convey tension instead. We
don't know why it was cut — the leading guesses are still memory
pressure, performance during the loaded-resource setup, or a
late-stage authorial decision that "silence + stings" was more
effective than a sustained musical bed.

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

2. ~~Cross-check whether other ports' LAKE bytecode also has the
   `jmp` (i.e., whether the disable is universal or AMIGA-introduced
   and inherited).~~ **Done 2026-05-04.** All four per-branch LAKE
   sources contain the byte-identical pattern:

   ```
       load id=0x002D
       jmp INIT_AUDIO_AND_SCENE_AFTER_LOADS
       load id=0x0089       ; MUSIC
       load id=0x0002       ; SOUND
       load id=0x0081       ; SOUND
       load id=0x0003       ; SOUND
   INIT_AUDIO_AND_SCENE_AFTER_LOADS:
   ```

   Verified across `cartridge_1992/LAKE.asm`, `dos_1992/LAKE.asm`,
   `chahi_amiga_1991/LAKE.asm`, and `gba_2004/LAKE.asm`. The dead
   code is **introduced in the original 1991 amiga release** and
   **preserved verbatim in every subsequent port** (1992 dos, 1992
   cart, 2004 gba). This rules out the possibility that any port
   removed it — they all inherited the unreachable preload from
   Eric Chahi's original bytecode.

   Conclusion: music 0x89 is **genuine 1991-era cut content**, not
   a port-specific artifact. The `jmp` was added by the original
   author before release; subsequent automated bytecode pipelines
   never touched it.
3. Compare 0x89 against the released soundtrack (Eric Serra's
   AW soundtrack album, plus any in-game music heard) — does it
   match anything we know, or is it genuinely unreleased?
   *(Open — requires external research / human listening
   comparison.)*
4. ~~Consider adding a "render dead-code" mode to the future
   audio-asset cataloger: any MUSIC resource that no `song id=` /
   reachable `load id=` triggers should be flagged as cut content.~~
   **Done 2026-05-04.** `tools/unused_sound_scan_v2.py`
   (commit `9b7ad0d`) wires in the `ReachabilityOracle` from
   #0058 to filter `play`/`load`/`song` references that come from
   dead bytecode. Two-tier filter: label-level
   (dead-by-gate / transitively-dead labels) + intra-label
   (post-jmp/ret/killChannel/freezeChannel/bankSwitch tails).
   Validation against this issue: the scanner correctly
   classifies music 0x89 as "dead-only (referenced ONLY from
   dead code)" — exactly the case research/11 found by hand.
   The asset-side cross-validation table in research/19 records
   the result: 1 MUSIC dead-only across the dos_1992 port.

## Closing log

- 2026-05-05: closing as `done`. Action items 1, 2, and 4 are
  fully complete (renderer built + validated, cross-port
  preservation verified, dead-code-flag mode shipped). Action
  item 3 (compare 0x89 against the released soundtrack album)
  inherently requires external/human research — listening to
  Eric Serra's AW soundtrack album and other reference audio
  to identify the track. Not autonomously achievable; not a
  research blocker either. The substantive archaeology
  question — "is music 0x89 dead-code, and what is it?" — is
  answered:
    - 26.5 second 4-pattern composition
    - Preserved verbatim across all 4 ports (1991→2004 lineage)
    - Genuine 1991-era cut content from the original Chahi
      Amiga release
    - Audible at `tmp/rendered_audio/lake_dead_music_0x89.wav`
      for any future human listener with access to the
      soundtrack album for comparison.

  Closing here; if a human listener does the soundtrack-
  comparison check later, they can reopen or file a new finding
  with the result.

# 15 — Unused SOUND resources (DOS port)

Companion finding to research/11 (unused MUSIC) and research/06
(unused polygons).

## Summary

Of the 103 SOUND resources defined in DOS-1992's memlist, **4
non-empty SOUNDs are never referenced** by any `play id=N` or
`load id=N` opcode anywhere in the bytecode:

| index | size | duration @ period 428 | note |
| :---: | ---: | ---: | --- |
| 0x2E | 2,274 bytes | 0.27 s | one-shot SFX |
| 0x37 | 5,020 bytes | 0.60 s | one-shot SFX |
| 0x38 | 5,564 bytes | 0.67 s | one-shot SFX |
| 0x42 | 1,252 bytes | 0.15 s | one-shot SFX |

(All four have `loop_len = 0`, i.e., one-shot samples — none are
sustained instruments.)

Renders at `docs/assets/research-15-unused-sounds/sound_0xNN.wav`
(16-bit mono, 22 050 Hz, period 428 ≈ A-3). Plays produced by
`tools/aw_sound_to_wav.py`.

## Method

Per `tools/unused_sound_scan.py` (#0055):

```
unused_sounds = (set of SOUND memlist entries)
              − (set of `play id=N` references reachable from any entry point)
              − (set of `load id=N` references)
```

The DOS port has 103 SOUND resources; 82 unique `play id=` IDs
across all 9 levels; 95 reachable via play OR load. The remaining
8 are never play-referenced. Of those 8, 4 are empty-sample
"placeholder" entries (sample_len = 0) that the engine reads and
ignores. The other 4 listed above are real audio data with no
runtime invocation path.

## Caveats

- **`load`-counts-as-used** limitation: a SOUND that is `load`ed
  but never `play`ed is still classified "used" by the naive
  scanner — even though "load without play" is the dead-code
  pattern that #0076 / #0058 exists to detect. The 4 unused
  SOUNDs above are unused even by this lenient definition; they
  are neither loaded nor played.
- **Reachability** (#0058) is not yet applied. If any of the 4
  IS referenced inside a setup-then-overwritten dispatch case,
  the runtime would never execute the play, and the sound IS
  cut. Until reachability lands, treat these as
  high-probability-but-unconfirmed cut-content.
- **Cross-port** comparison pending: only DOS scanned so far.
  An unused-on-DOS sound that IS played on the cartridge ports
  would tell us the DOS port re-encoded its bytecode without
  the `play` site (matches the per-stage triplet rebuild
  documented in research/13). Future work.

## Auditioning hints

Period 428 is the rendering tool's default — produces a
~mid-range pitch suitable for human auditioning. The original
game would've called these at varying periods baked into the
source `play freq=…` operand. Without that context, the wav
files give a reasonable approximation of timbre but not the
exact pitch the game intended.

## Reproducing

```bash
# Run the scanner:
python3 tools/unused_sound_scan.py --port msdos

# Render any subset:
for hex in 2e 37 38 42; do
    python3 tools/aw_sound_to_wav.py \
        tmp/output/msdos/resources/resource-0x${hex}.bin \
        docs/assets/research-15-unused-sounds/sound_0x${hex}.wav
done
```

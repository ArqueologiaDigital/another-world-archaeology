#!/usr/bin/env python3
"""Render a single Another World SOUND resource to a WAV file.

A SOUND resource is the same format as a music instrument:

  0x00-0x01  BE16 sample length in words (× 2 = bytes)
  0x02-0x03  BE16 loop length in words (0 = no loop)
  0x04-0x07  padding (4 bytes, ignored)
  0x08+      8-bit signed PCM at the Amiga reference rate

Renders by triggering one playback at a "neutral" period (taken
from rawgl's default for SFX, mapping to ~musical middle); plays
the sample one-shot for one-shot SFX, or up to N seconds for
looping samples.

Usage:
  aw_sound_to_wav.py <sound.bin> <out.wav> [--period N] [--seconds N]

Auditioning the unused sounds catalogued in #0055:
  for f in 0x2E-SOUND.bin 0x37-SOUND.bin 0x38-SOUND.bin 0x42-SOUND.bin; do
      aw_sound_to_wav.py "$f" "${f%.bin}.wav"
  done
"""
from __future__ import annotations

import argparse
import struct
import sys
import wave
from pathlib import Path

AMIGA_CHIP_HZ = 7159092
OUT_RATE = 22050  # half of CD rate; AW music tool uses same


def be16(buf: bytes, off: int) -> int:
    return struct.unpack(">H", buf[off : off + 2])[0]


def render_sound(
    raw: bytes,
    out_path: Path,
    period: int,
    max_seconds: float,
) -> None:
    if len(raw) < 8:
        sys.exit(f"too short ({len(raw)} bytes); expected SOUND header")
    sample_len_words = be16(raw, 0)
    loop_len_words = be16(raw, 2)
    sample_len = sample_len_words * 2
    loop_len = loop_len_words * 2

    if sample_len == 0:
        sys.exit("empty sample (length=0)")
    if 8 + sample_len > len(raw):
        # Some resources may have trailing padding; truncate to real length.
        sample_len = len(raw) - 8

    pcm = raw[8 : 8 + sample_len]

    # Reasonable default period: produces ~middle audible pitch
    # without being too high or too low.
    pitch_hz = AMIGA_CHIP_HZ / (period * 2)
    step = pitch_hz / OUT_RATE

    samples = []
    pos_int = 0
    pos_frac = 0.0
    n_samples = int(max_seconds * OUT_RATE)
    for _ in range(n_samples):
        if pos_int >= len(pcm):
            if loop_len > 0:
                # Loop: rawgl wraps within the loop region after first pass.
                if loop_len > 0:
                    pos_int = (pos_int - len(pcm)) % loop_len + (
                        len(pcm) - loop_len if len(pcm) >= loop_len else 0
                    )
                else:
                    break
            else:
                break
        b = pcm[pos_int]
        if b >= 0x80:
            b -= 0x100
        samples.append(b << 8)  # int16

        pos_frac += step
        whole = int(pos_frac)
        if whole > 0:
            pos_int += whole
            pos_frac -= whole

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(out_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT_RATE)
        w.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--period",
        type=int,
        default=428,
        help="Amiga period value (default 428 ≈ A-3, middle pitch)",
    )
    parser.add_argument(
        "--seconds",
        type=float,
        default=8.0,
        help="cap output at N seconds (one-shot samples may end "
        "earlier; looping samples truncate at this limit)",
    )
    args = parser.parse_args()

    raw = args.input.read_bytes()
    render_sound(raw, args.output, args.period, args.seconds)
    info_size = (be16(raw, 0) * 2) if len(raw) >= 2 else 0
    info_loop = (be16(raw, 2) * 2) if len(raw) >= 4 else 0
    print(
        f"wrote {args.output} (sample_len={info_size}b, "
        f"loop_len={info_loop}b, period={args.period})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

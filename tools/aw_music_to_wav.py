#!/usr/bin/env python3
"""Render an Another World MUSIC resource to WAV.

Format reference: rawgl's `sfxplayer.cpp` (Gregory Montoir, fbBeRoFiel).

  Music resource:
    0x00-0x01  initial delay (BE16, Amiga timing units)
    0x02-0x3D  15 instruments × 4 bytes:
                 BE16 resource_id, BE16 volume (0..0x3F)
    0x3F       numOrder (1 byte)
    0x40-0xBF  orderTable[0x80] — pattern indices
    0xC0+      pattern data — each pattern is 1024 bytes
                 = 64 rows × 4 channels × 4 bytes per channel-row

  Channel-row (4 bytes):
    byte 0-1   note_1 (BE16):
                 0x0000      = no-op
                 0xFFFD      = set script var [0xF4] = note_2
                 0xFFFE      = stop channel
                 else        = Amiga period value
    byte 2-3   note_2 (BE16):
                 bits 12-15  = sample index (1-based; 0 = keep current sample)
                 bits 8-11   = effect (5 = vol+, 6 = vol-)
                 bits 0-7    = effect parameter / volume delta

  Instrument (SOUND resource):
    0x00-0x01  BE16 sample length in words (× 2 for bytes)
    0x02-0x03  BE16 loop length in words (0 = no loop)
    0x04-0x07  padding
    0x08+      8-bit signed PCM at Amiga reference rate

  Tempo:
    delay_ms = raw_delay * 60 / 7050

  Mixing:
    pitch_hz = 7159092 / (period * 2)   (Amiga PAL chip rate)
    sample is played at pitch_hz, advance position by pitch_hz / output_rate
    per output sample. Loop after sample_len bytes if loop_len > 0.

Usage:
    aw_music_to_wav.py <music.bin> <out.wav> \\
      --instrument 1 <sample1.bin> --instrument 2 <sample2.bin> ...

Or to auto-resolve instruments from a directory:

    aw_music_to_wav.py <music.bin> <out.wav> --bin-dir <dir>

The --bin-dir flag treats files named '0xNN-SOUND.bin' or
'0xNNN-SOUND.bin' as instrument samples and resolves the music's
instrument table against them.
"""
from __future__ import annotations

import argparse
import re
import struct
import sys
import wave
from pathlib import Path

OUT_RATE = 22050  # output WAV sample rate
AMIGA_CHIP_HZ = 7_159_092  # Amiga chip-rate (PAL); rawgl uses 7159092
MS_PER_DELAY_UNIT = 60.0 / 7050.0  # rawgl: _delay = _delay * 60 / 7050


def be16(buf: bytes, off: int) -> int:
    return struct.unpack(">H", buf[off : off + 2])[0]


def parse_music(buf: bytes) -> dict:
    """Return dict with keys: delay, instruments (list of (id, vol)),
    num_order, order_table, pattern_data_offset."""
    if len(buf) < 0xC0:
        raise ValueError(f"music file too small ({len(buf)} bytes)")
    delay = be16(buf, 0)
    instruments = []
    for i in range(15):
        rid = be16(buf, 2 + i * 4)
        vol = be16(buf, 2 + i * 4 + 2)
        instruments.append((rid, vol))
    num_order = buf[0x3F]
    order_table = list(buf[0x40:0xC0])
    return {
        "delay": delay,
        "instruments": instruments,
        "num_order": num_order,
        "order_table": order_table,
        "pattern_data": buf[0xC0:],
    }


class Channel:
    __slots__ = (
        "sample_data", "sample_len", "loop_pos", "loop_len",
        "pos_int", "pos_frac", "step_per_outsamp", "volume",
    )

    def __init__(self):
        self.sample_data = None  # bytes (8-bit signed PCM, starting at sample_start=8 in raw)
        self.sample_len = 0
        self.loop_pos = 0
        self.loop_len = 0
        self.pos_int = 0
        self.pos_frac = 0.0
        self.step_per_outsamp = 0.0
        self.volume = 0

    def trigger(self, raw_sample_buf: bytes, period: int, volume: int):
        """Start playing a sample. raw_sample_buf is the full SOUND resource
        bytes (including 8-byte header)."""
        sample_len_words = be16(raw_sample_buf, 0)
        loop_len_words = be16(raw_sample_buf, 2)
        sample_len = sample_len_words * 2
        loop_len = loop_len_words * 2

        self.sample_data = raw_sample_buf[8:8 + sample_len]
        self.sample_len = len(self.sample_data)
        if loop_len > 0:
            self.loop_pos = self.sample_len  # rawgl: loopPos = sampleLen
            self.loop_len = loop_len
        else:
            self.loop_pos = 0
            self.loop_len = 0

        freq_hz = AMIGA_CHIP_HZ / (period * 2)
        self.step_per_outsamp = freq_hz / OUT_RATE
        self.pos_int = 0
        self.pos_frac = 0.0
        self.volume = volume

    def stop(self):
        self.sample_data = None
        self.sample_len = 0
        self.volume = 0

    def render_sample(self) -> int:
        """Return the next mixed sample contribution in 16-bit signed range."""
        if self.sample_data is None or self.sample_len == 0:
            return 0
        if self.pos_int >= self.sample_len:
            if self.loop_len > 0:
                self.pos_int = (self.pos_int - self.sample_len) % self.loop_len
            else:
                self.sample_data = None
                return 0
        # 8-bit signed PCM
        s = self.sample_data[self.pos_int]
        if s >= 0x80:
            s -= 0x100  # signed
        # AW volume is 0..0x3F (6-bit). Convert to ~ -32k..32k 16-bit value.
        # raw 8-bit signed: -128..127. Scale to int16 (shift left 8) then by volume/0x3F.
        out = (s << 8) * self.volume // 0x40

        # Advance position
        self.pos_frac += self.step_per_outsamp
        whole = int(self.pos_frac)
        if whole > 0:
            self.pos_int += whole
            self.pos_frac -= whole
        return out


def render(music: dict, instrument_data: dict[int, bytes],
           wav_out: Path, max_seconds: float = 60.0,
           override_delay: int | None = None) -> None:
    """Render the music to wav_out (16-bit signed mono at OUT_RATE Hz)."""
    delay_units = override_delay if override_delay is not None else music["delay"]
    delay_ms = delay_units * MS_PER_DELAY_UNIT
    samples_per_row = max(1, int(round(delay_ms * OUT_RATE / 1000)))

    print(f"  delay={delay_units} ({delay_ms:.2f} ms/row → {samples_per_row} out-samples/row)")
    print(f"  num_order={music['num_order']}, pattern_data={len(music['pattern_data'])} bytes")

    channels = [Channel() for _ in range(4)]
    pcm = bytearray()  # 16-bit LE mono

    cur_order_idx = 0
    cur_pos_in_pattern = 0  # bytes; advances by 16 (4 channels × 4 bytes) per row
    max_samples = int(max_seconds * OUT_RATE)

    rows_processed = 0
    while cur_order_idx < music["num_order"] and len(pcm) // 2 < max_samples:
        order = music["order_table"][cur_order_idx]
        pattern_offset = order * 1024 + cur_pos_in_pattern
        if pattern_offset + 16 > len(music["pattern_data"]):
            print(f"  warning: ran off pattern data at order={cur_order_idx} pos={cur_pos_in_pattern}")
            break

        # Process row: 4 channels × 4 bytes
        for ch in range(4):
            entry = music["pattern_data"][pattern_offset + ch * 4 : pattern_offset + ch * 4 + 4]
            note_1 = struct.unpack(">H", entry[0:2])[0]
            note_2 = struct.unpack(">H", entry[2:4])[0]

            if note_1 == 0xFFFD:
                # set script var; ignore for rendering
                pass
            elif note_1 == 0xFFFE:
                channels[ch].stop()
            elif note_1 != 0:
                # Trigger sample
                sample_idx = (note_2 & 0xF000) >> 12  # 1-based
                effect = (note_2 & 0x0F00) >> 8
                effect_param = note_2 & 0xFF
                if sample_idx > 0 and sample_idx <= 15:
                    inst_id, inst_vol = music["instruments"][sample_idx - 1]
                    if inst_id != 0 and inst_id in instrument_data:
                        m = inst_vol
                        if effect == 5:
                            m = min(0x3F, m + effect_param)
                        elif effect == 6:
                            m = max(0, m - effect_param)
                        if 0x37 <= note_1 < 0x1000:
                            channels[ch].trigger(instrument_data[inst_id], note_1, m)

        # Render samples_per_row output samples
        for _ in range(samples_per_row):
            # 4 channels can sum to 4× a single channel's full-scale range; divide
            # by 4 for headroom (the original Amiga also mixed 4 channels with no
            # native headroom, but the chip output was inherently soft-clipped;
            # we use a clean linear divide to avoid hard clipping in the WAV)
            mix = sum(c.render_sample() for c in channels) // 4
            # Clamp to int16 (should not be needed after //4, but be safe)
            if mix > 32767:
                mix = 32767
            elif mix < -32768:
                mix = -32768
            pcm.extend(struct.pack("<h", mix))
            if len(pcm) // 2 >= max_samples:
                break

        rows_processed += 1
        cur_pos_in_pattern += 16
        if cur_pos_in_pattern >= 1024:
            cur_pos_in_pattern = 0
            cur_order_idx += 1

    print(f"  rendered {rows_processed} rows = {len(pcm) // 2} samples = {len(pcm) // 2 / OUT_RATE:.2f} sec")

    with wave.open(str(wav_out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(OUT_RATE)
        w.writeframes(bytes(pcm))
    print(f"  wrote {wav_out}")


def auto_resolve_instruments(music: dict, bin_dir: Path) -> dict[int, bytes]:
    """Look for files named '0xNN-SOUND.bin' (or '0xNNN-SOUND.bin') in bin_dir
    and match them to the music's instrument table by resource ID."""
    needed = {rid for rid, _ in music["instruments"] if rid != 0}
    found = {}
    for f in bin_dir.iterdir():
        m = re.match(r"^0x([0-9A-Fa-f]+)-SOUND\.bin$", f.name)
        if m:
            rid = int(m.group(1), 16)
            if rid in needed:
                found[rid] = f.read_bytes()
    missing = needed - found.keys()
    if missing:
        print(f"  missing instruments: {[hex(x) for x in sorted(missing)]}")
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("music", type=Path, help="MUSIC resource .bin file")
    ap.add_argument("out_wav", type=Path, help="output WAV file path")
    ap.add_argument("--bin-dir", type=Path,
                    help="directory with '0xNN-SOUND.bin' instrument files")
    ap.add_argument("--instrument", action="append", nargs=2,
                    metavar=("RESOURCE_ID", "PATH"),
                    help="specify instrument file by resource ID")
    ap.add_argument("--max-seconds", type=float, default=60.0,
                    help="render at most this many seconds (default 60)")
    ap.add_argument("--override-delay", type=int,
                    help="override the music header's initial delay")
    args = ap.parse_args()

    music_buf = args.music.read_bytes()
    music = parse_music(music_buf)

    print(f"Music: {args.music} ({len(music_buf)} bytes)")
    print(f"  initial delay: 0x{music['delay']:04X}")
    print(f"  instruments:")
    for i, (rid, vol) in enumerate(music["instruments"]):
        if rid != 0:
            print(f"    slot {i+1}: resource 0x{rid:04X}, volume 0x{vol:04X}")
    print(f"  num_order: {music['num_order']}")
    print(f"  order table: {[f'{x:02X}' for x in music['order_table'][: music['num_order']]]}")
    print()

    instruments: dict[int, bytes] = {}
    if args.bin_dir:
        instruments.update(auto_resolve_instruments(music, args.bin_dir))
    if args.instrument:
        for rid_str, path_str in args.instrument:
            rid = int(rid_str, 0)
            instruments[rid] = Path(path_str).read_bytes()

    if not instruments:
        print("ERROR: no instruments resolved; pass --bin-dir or --instrument", file=sys.stderr)
        sys.exit(1)

    print(f"Resolved {len(instruments)} instrument(s):")
    for rid in sorted(instruments):
        print(f"  0x{rid:04X}: {len(instruments[rid])} bytes")
    print()

    render(music, instruments, args.out_wav,
           max_seconds=args.max_seconds,
           override_delay=args.override_delay)


if __name__ == "__main__":
    main()

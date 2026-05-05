#!/usr/bin/env python3
"""Decompressor for packed Another World resources.

Direct port of `AnotherWorld_VMTools/awvm/src/unpacker.rs` (which itself
is a port of `releases/common_data/Unpacker.py`). The algorithm consumes
its input bit-stream **backwards** from the end of the packed buffer and
likewise writes its output bytes backwards from `raw_data_size - 1`
toward `0`. The unpacker uses one buffer for both input and output; the
packed bytes occupy positions `0..packed.len()`, and the unpacked bytes
end up occupying `0..raw_data_size`.

The Rust reference and this Python port must produce byte-identical
output for the same input — the algorithm relies on overlapping
read/write and any deviation diverges silently.

Usage:
    from tools.aw_unpacker import unpack
    raw = unpack(packed_bytes)   # returns bytes, or None on CRC failure
"""
from __future__ import annotations

from typing import Optional


def unpack(packed: bytes) -> Optional[bytes]:
    """Decompress an AW VM packed resource.

    Returns the unpacked bytes, or `None` if the embedded CRC at the
    end of the bit-stream doesn't validate (matching the Rust
    reference's `UnpackResult::CrcFailure` behavior).
    """
    if len(packed) < 16:
        return None

    # Read the 4-uint32 prologue from the end of `packed` (backwards).
    # We read directly from `packed` here because `buf` isn't allocated
    # yet — the Rust reference does the same dispatch via `buf_or_packed`.
    def be_u32(at: int) -> int:
        return (packed[at] << 24) | (packed[at + 1] << 16) | (packed[at + 2] << 8) | packed[at + 3]

    raw_data_size = be_u32(len(packed) - 4)
    # Allocate the working buffer to hold both packed (front) and
    # unpacked (which extends to raw_data_size).
    buf_size = max(len(packed), raw_data_size)
    buf = bytearray(buf_size)
    buf[: len(packed)] = packed

    state = {
        "buf": buf,
        "input_index": len(packed) - 4 - 4,  # already consumed raw_data_size
        "output_index": raw_data_size - 1,
        "crc": be_u32(len(packed) - 8),
        "chk": be_u32(len(packed) - 12),
    }
    state["crc"] ^= state["chk"]
    state["input_index"] = len(packed) - 12 - 4

    def read_be_uint32() -> int:
        i = state["input_index"]
        state["input_index"] -= 4
        return (buf[i] << 24) | (buf[i + 1] << 16) | (buf[i + 2] << 8) | buf[i + 3]

    def rcr(cf_in: bool) -> bool:
        r_cf = (state["chk"] & 1) != 0
        state["chk"] >>= 1
        if cf_in:
            state["chk"] |= 0x80000000
        return r_cf

    def next_bit() -> bool:
        cf = rcr(False)
        if state["chk"] == 0:
            state["chk"] = read_be_uint32()
            state["crc"] ^= state["chk"]
            return rcr(True)
        return cf

    def get_code(num_bits: int) -> int:
        c = 0
        for _ in range(num_bits):
            c <<= 1
            if next_bit():
                c |= 1
        return c

    def raw_bytes(count: int) -> None:
        for _ in range(count):
            value = get_code(8)
            buf[state["output_index"]] = value
            state["output_index"] -= 1

    def copy_data(count: int, offset: int) -> None:
        for _ in range(count):
            value = buf[state["output_index"] + offset]
            buf[state["output_index"]] = value
            state["output_index"] -= 1

    while True:
        if next_bit():
            c = get_code(2)
            if c == 0:
                copy_data(3, get_code(9))
            elif c == 1:
                copy_data(4, get_code(10))
            elif c == 2:
                count = 1 + get_code(8)
                offset = get_code(12)
                copy_data(count, offset)
            else:  # c == 3
                count = 9 + get_code(8)
                raw_bytes(count)
        elif next_bit():
            offset = get_code(8)
            copy_data(2, offset)
        else:
            count = 1 + get_code(3)
            raw_bytes(count)

        if state["output_index"] < 0:
            if state["crc"] != 0:
                return None
            return bytes(buf[:raw_data_size])


if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        sys.exit("usage: aw_unpacker.py <packed-input> <raw-output>")
    raw = unpack(open(sys.argv[1], "rb").read())
    if raw is None:
        sys.exit("CRC failure")
    open(sys.argv[2], "wb").write(raw)
    print(f"unpacked {len(raw)} bytes")

#!/usr/bin/env python3
"""Re-disassemble `db` blocks in an AW VM .asm source.

The disassembler (`awvm-disasm`) sometimes falls back to emitting
raw `db <bytes>` lines for code regions it can't recognise. The
fallback is too eager: many of those `db` regions actually contain
valid AW VM instructions that just sit after a `killChannel` (which
the disasm probably treats as an end-of-decoding signal).

This tool walks each `db` block's bytes and tries to decode them
linearly using the standard opcode table. When decoding succeeds
end-to-end, the block can be rewritten as proper mnemonics — and
crucially, any embedded address operands become resolvable label
references, which the inline-label canonicalizer can then unify
across branches.

Usage:
    # Report mode: show what would change without rewriting
    python3 tools/redisasm_db.py <source.asm> --report

    # Rewrite mode: replace db blocks with decoded instructions
    python3 tools/redisasm_db.py <source.asm> -o <out.asm>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Regex for a `db` line. Captures the bytes.
RE_DB = re.compile(
    r'^(?P<indent>\s*)db\s+(?P<bytes>(?:0x[0-9A-Fa-f]+\s*,?\s*)+)\s*(?P<comment>;.*)?$'
)
RE_LABEL_DEF = re.compile(r'^([A-Z][A-Z_0-9]*):\s*$')


# Opcode table: opcode → (size_bytes, [(addr_offset_within_instruction, addr_byte_count)])
# `size_bytes` = total instruction byte count (None for variable-size)
# `addr_offsets` lists positions of address operands (16-bit BE).
OPCODE_TABLE = {
    0x00: (4, [], "mov_var_imm"),     # mov [var], imm16
    0x01: (3, [], "mov_var_var"),     # mov [var], [var]
    0x02: (3, [], "add_var_var"),
    0x03: (4, [], "add_var_imm"),
    0x04: (3, [(1, 2)], "call"),      # call addr16
    0x05: (1, [], "ret"),
    0x06: (1, [], "break"),
    0x07: (3, [(1, 2)], "jmp"),       # jmp addr16
    0x08: (4, [(2, 2)], "setup"),     # setup ch=N, addr16
    0x09: (4, [(2, 2)], "djnz"),      # djnz [var], addr16
    # 0x0A handled separately (variable size)
    0x0B: (3, [], "setPalette"),      # setPalette N (1 arg byte + 1 fill byte)
    0x0C: (4, [], "freezeChannels"),
    0x0D: (2, [], "selectVideoPage"),
    0x0E: (3, [], "fill"),
    0x0F: (3, [], "copyVideoPage"),
    0x10: (2, [], "blitFramebuffer"),
    0x11: (1, [], "killChannel"),
    0x12: (6, [], "text"),            # text id, x, y, color
    0x13: (3, [], "sub_var_var"),
    0x14: (4, [], "and_var_imm"),
    0x18: (6, [], "play"),
    0x19: (3, [], "load"),
}


def decode_one(bytes_: list[int], offset: int) -> tuple[int, list[tuple[int, int]], str] | None:
    """Decode one instruction at offset. Returns (size, addr_positions, mnemonic) or None."""
    if offset >= len(bytes_):
        return None
    op = bytes_[offset]

    if op == 0x0A:
        # cond_jump: opcode + cond + var + (operand bytes by cond) + 2-byte addr
        if offset + 1 >= len(bytes_):
            return None
        cond = bytes_[offset + 1]
        if cond & 0x80:
            ops = 1  # second op is var
        elif cond & 0x40:
            ops = 1  # short imm
        else:
            ops = 2  # long imm
        size = 1 + 1 + 1 + ops + 2  # opcode + cond + var + imm-bytes + addr
        if offset + size > len(bytes_):
            return None
        addr_offset_in_instr = 1 + 1 + 1 + ops
        return (size, [(addr_offset_in_instr, 2)], "cond_jump")

    info = OPCODE_TABLE.get(op)
    if info is None:
        # video opcodes (high bit set)
        if op & 0x80:
            # type 1 / 2 video, variable size. Conservatively assume 5 bytes
            # (flag byte determines the actual size; this is a simplification).
            size = 5
            if op & 0x20:
                size = 6  # has zoom byte
            if offset + size > len(bytes_):
                return None
            return (size, [], f"video_{op:02x}")
        return None

    size, addr_positions, mnemonic = info
    if offset + size > len(bytes_):
        return None
    return (size, addr_positions, mnemonic)


def decode_block(bytes_: list[int]) -> list[tuple[int, int, list[tuple[int, int]], str]] | None:
    """Decode an entire byte sequence as a series of instructions.

    Returns a list of (offset, size, addr_positions, mnemonic) tuples,
    or None if decoding failed (didn't consume all bytes cleanly).
    """
    out: list[tuple[int, int, list[tuple[int, int]], str]] = []
    offset = 0
    while offset < len(bytes_):
        result = decode_one(bytes_, offset)
        if result is None:
            return None
        size, addr_positions, mnemonic = result
        out.append((offset, size, addr_positions, mnemonic))
        offset += size
    return out


def parse_db_line(line: str) -> list[int] | None:
    """Parse a `db 0x.., 0x.., ...` line into a list of bytes."""
    m = RE_DB.match(line)
    if not m:
        return None
    bytes_str = m.group('bytes')
    return [int(b.strip(), 16) for b in bytes_str.split(',') if b.strip()]


def find_db_runs(lines: list[str]) -> list[tuple[int, int, list[int]]]:
    """Find consecutive db lines. Returns [(start_line, end_line_exclusive, bytes), ...]."""
    runs = []
    i = 0
    while i < len(lines):
        if RE_DB.match(lines[i]):
            start = i
            bytes_ = []
            while i < len(lines) and RE_DB.match(lines[i]):
                bytes_.extend(parse_db_line(lines[i]))
                i += 1
            runs.append((start, i, bytes_))
        else:
            i += 1
    return runs


# Mnemonic → fixed instruction byte count (for lines without ;@raw= we can
# still infer the byte count from the mnemonic). cond_jump (`je`/`jne`/etc.)
# is variable-size and handled separately. Video opcodes are also variable
# but rare on lines without ;@raw=.
MNEMONIC_BYTE_COUNT = {
    "mov": None,         # 3 (var,var) or 4 (var,imm) — see below
    "add": None,         # 3 or 4
    "sub": 3,
    "and": 4,
    "call": 3,
    "ret": 1,
    "break": 1,
    "jmp": 3,
    "setup": 4,
    "djnz": 4,
    "setPalette": 3,
    "freezeChannels": 4,
    "selectVideoPage": 2,
    "fill": 3,
    "copyVideoPage": 3,
    "blitFramebuffer": 2,
    "killChannel": 1,
    "text": 6,
    "play": 6,
    "load": 3,
    "song": 6,
    "bankSwitch": 3,  # same as load
}

# Conditional jump mnemonics: variable-size based on operand types.
# `je [V], imm8, LABEL` = 6 bytes (cond=0x00 short imm form)
# `je [V], imm16, LABEL` = 7 bytes (cond=0x?? long imm form)
# `je [V], [V2], LABEL` = 5 bytes (var-var form)
# We compute size from the actual operand syntax in the line.
COND_JUMP_MNEMONICS = {"je", "jne", "jl", "jle", "jg", "jge"}


def estimate_line_bytes(line: str) -> int:
    """Estimate how many bytes this instruction line emits, without
    relying on `;@raw=`. Returns 0 if the line doesn't emit bytes
    (e.g., empty, EQU, label-only, comment)."""
    # Strip trailing comments + ;@raw=
    body = re.sub(r';@raw=[0-9A-Fa-fx,]+\s*$', '', line)
    body = re.sub(r';.*$', '', body).strip()
    if not body:
        return 0
    if RE_LABEL_DEF.match(line):
        return 0
    # EQU / org are not real instructions
    parts = body.split(maxsplit=1)
    if len(parts) >= 2 and parts[1].lstrip().startswith('EQU'):
        return 0
    if parts[0].lower() == 'org':
        return 0

    mnem = parts[0]

    # mov: 3 bytes for var-var, 4 for var-imm
    if mnem == "mov" or mnem == "add":
        # Heuristic: if the second arg looks like an immediate (starts with 0x or digit),
        # 4 bytes. If it's a [var] reference, 3 bytes.
        if len(parts) > 1:
            args = parts[1]
            # Args have format "[X], <something>"
            second = args.split(',', 1)[1].strip() if ',' in args else ''
            if second.startswith('['):
                return 3  # var-var
            else:
                return 4  # var-imm
        return 4

    if mnem in COND_JUMP_MNEMONICS:
        # Format: cond [var], <op>, LABEL or similar
        # Parse operand types
        if len(parts) > 1:
            args = parts[1]
            try:
                # Find second operand (between commas)
                tokens = [t.strip() for t in args.split(',')]
                if len(tokens) >= 3:
                    second = tokens[1]
                    if second.startswith('['):
                        return 5  # var-var form: 0x0A + cond + var + var + 2-byte addr
                    # imm: short (1 byte) if value fits in 8 bits, else 2 bytes
                    val_str = second.replace('0x', '')
                    val = int(second, 0)
                    if val <= 0xFF:
                        return 6  # short imm form
                    else:
                        return 7  # long imm form
            except (ValueError, IndexError):
                pass
        return 6  # default

    if mnem in MNEMONIC_BYTE_COUNT:
        sz = MNEMONIC_BYTE_COUNT[mnem]
        if sz is not None:
            return sz

    if mnem == 'video' or mnem.startswith('video_'):
        return 5  # most common video form; could be 6 with zoom

    if mnem == 'db':
        m = RE_DB.match(line)
        if m:
            return len(m.group('bytes').split(','))
        return 0

    # Unknown mnemonic — return 0 (will misalign tracking but at least won't crash)
    return 0


def collect_labels(lines: list[str]) -> dict[int, str]:
    """Walk source, track byte-position → label-name mapping.

    Uses `;@raw=` annotations when present (most accurate); falls back
    to mnemonic-based byte estimation otherwise (handles lines emitted
    by canonicalize_bankswitch.py and similar transformers that don't
    re-add `;@raw=`).
    """
    re_raw = re.compile(r';@raw=([0-9A-Fa-fx,]+)')
    re_org = re.compile(r'^\s*org\s+(0x[0-9A-Fa-f]+)')
    pos = 0
    label_at_pos: dict[int, str] = {}
    for line in lines:
        m_org = re_org.match(line)
        if m_org:
            pos = int(m_org.group(1), 16)
            continue
        m_label = RE_LABEL_DEF.match(line)
        if m_label:
            label_at_pos.setdefault(pos, m_label.group(1))
            continue
        m_raw = re_raw.search(line)
        if m_raw:
            pos += len(m_raw.group(1).split(','))
            continue
        # No ;@raw=: estimate bytes from mnemonic.
        pos += estimate_line_bytes(line)
    return label_at_pos


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path,
                   help="(future) rewrite mode — replace db blocks with decoded mnemonics")
    p.add_argument("--report", action="store_true",
                   help="report-only mode (default if -o not given)")
    args = p.parse_args()

    lines = args.input.read_text().splitlines()
    label_at_pos = collect_labels(lines)
    print(f"=== {args.input.name}: {len(lines)} lines, {len(label_at_pos)} labels ===")

    runs = find_db_runs(lines)
    print(f"db runs found: {len(runs)}")

    decoded_count = 0
    not_decoded_count = 0
    addr_resolves = 0  # resolves to an existing label
    addr_internal = 0  # falls within another db block (would resolve after recursive re-disasm)
    addr_unresolved = 0  # genuinely points to nothing recognisable

    # Build (start_pos, end_pos) ranges for all db blocks
    db_block_ranges: list[tuple[int, int, list[int]]] = []  # (start_pos, end_pos, bytes_)

    print(f"\n{'span':<14} {'bytes':<6} {'decode':<10} {'addrs-status':<24}")
    print("-" * 70)

    # Compute byte position of each db run by walking again
    re_raw = re.compile(r';@raw=([0-9A-Fa-fx,]+)')
    re_org = re.compile(r'^\s*org\s+(0x[0-9A-Fa-f]+)')

    pos_at_line: dict[int, int] = {}
    pos = 0
    for i, line in enumerate(lines):
        pos_at_line[i] = pos
        m_org = re_org.match(line)
        if m_org:
            pos = int(m_org.group(1), 16)
            continue
        m_raw = re_raw.search(line)
        if m_raw:
            pos += len(m_raw.group(1).split(','))
            continue
        # No ;@raw=: estimate bytes from mnemonic
        pos += estimate_line_bytes(line)

    # First pass: find all db block byte-ranges (so we can detect internal addresses)
    for start, end, bytes_ in runs:
        run_pos = pos_at_line[start]
        db_block_ranges.append((run_pos, run_pos + len(bytes_), bytes_))

    def addr_in_any_db_block(addr: int) -> bool:
        for start_pos, end_pos, _ in db_block_ranges:
            if start_pos <= addr < end_pos:
                return True
        return False

    for start, end, bytes_ in runs:
        run_pos = pos_at_line[start]
        decoded = decode_block(bytes_)
        if decoded is None:
            not_decoded_count += 1
            status = "FAIL"
            note = ""
        else:
            decoded_count += 1
            status = f"{len(decoded)}_inst"
            n_resolved = 0
            n_internal = 0  # falls within another db block (or this one)
            n_unresolved = 0
            for inst_off, inst_size, addr_positions, mnemonic in decoded:
                for ao_in_inst, ao_size in addr_positions:
                    addr_byte_pos_in_block = inst_off + ao_in_inst
                    addr = (bytes_[addr_byte_pos_in_block] << 8) | bytes_[addr_byte_pos_in_block + 1]
                    if addr in label_at_pos:
                        n_resolved += 1
                    elif addr_in_any_db_block(addr):
                        n_internal += 1
                    else:
                        n_unresolved += 1
            addr_resolves += n_resolved
            addr_internal += n_internal
            addr_unresolved += n_unresolved
            total_addrs = n_resolved + n_internal + n_unresolved
            note = f"{n_resolved}/{n_internal}/{n_unresolved}"

        span = f"{start+1}-{end}"
        print(f"{span:<14} {len(bytes_):<6} {status:<10} {note}")

    print()
    print(f"=== summary ===")
    print(f"  decoded cleanly:        {decoded_count} runs")
    print(f"  decode FAILED:          {not_decoded_count} runs")
    print(f"  address operand counts (resolved / internal / unresolved):")
    print(f"    resolved to existing labels:    {addr_resolves}")
    print(f"    internal (falls within db blk): {addr_internal}  ← could resolve after recursive re-decode")
    print(f"    unresolved (genuinely orphan):  {addr_unresolved}")
    print(f"  legend:  resolved/internal/unresolved per row")
    if addr_internal + addr_resolves > 0:
        print(f"\nUnification potential:")
        print(f"  {addr_resolves + addr_internal} address operands could become symbolic label references")
        print(f"  if the disassembler properly decoded these regions. They'd then be eligible for")
        print(f"  pairing by tools/canonicalize_inline_labels.py across branches.")


if __name__ == "__main__":
    main()

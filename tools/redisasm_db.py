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


# Type-2 video opcode (0x40-0x7F) size table. Empirically derived from
# the cart INTRO disasm. Opcodes not in this table are size-unknown and
# decode_one() returns None (caller falls back to db).
VIDEO2_SIZE = {
    0x48: 6, 0x54: 5, 0x55: 6, 0x58: 5,
    0x60: 6, 0x64: 5, 0x69: 6, 0x6A: 6,
    0x74: 5, 0x78: 5, 0x7A: 6,
}


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
        # Empirically (cart INTRO has 30 instances): default cond byte (low
        # bits only) is SHORT IMM (1 byte for second operand). Bit 0x80 is
        # var-var (also 1 byte). Bit 0x40 is long imm (2 bytes).
        if offset + 1 >= len(bytes_):
            return None
        cond = bytes_[offset + 1]
        if cond & 0x80:
            ops = 1  # var-var (1 byte for second var)
        elif cond & 0x40:
            ops = 2  # long imm
        else:
            ops = 1  # short imm (DEFAULT)
        size = 1 + 1 + 1 + ops + 2  # opcode + cond + var + imm-bytes + addr
        if offset + size > len(bytes_):
            return None
        addr_offset_in_instr = 1 + 1 + 1 + ops
        return (size, [(addr_offset_in_instr, 2)], "cond_jump")

    info = OPCODE_TABLE.get(op)
    if info is None:
        # Video opcodes:
        #   bit 7 set (0x80-0xFF): video type 1 — empirically always 4 bytes
        #     in INTRO (verified across all 0x82-0xFE opcodes used).
        #   bit 6 set, bit 7 clear (0x40-0x7F): video type 2 — 5 or 6 bytes.
        #     Size depends on flag bits we don't fully decode. We use a
        #     lookup table for the cases observed in INTRO.
        if op & 0x80:
            size = 4
            if offset + size > len(bytes_):
                return None
            return (size, [], f"video1_{op:02x}")
        if op & 0x40:
            size = VIDEO2_SIZE.get(op)
            if size is None:
                return None  # unknown type-2 size, can't decode
            if offset + size > len(bytes_):
                return None
            return (size, [], f"video2_{op:02x}")
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


# ---------------------------------------------------------------------
# Rewrite mode: produce a new .asm with db blocks replaced by mnemonics.
# ---------------------------------------------------------------------

# Comparison-type → mnemonic for cond_jump (low 3 bits of cond byte).
COND_MNEMONIC = {0: "je", 1: "jne", 2: "jg", 3: "jge", 4: "jl", 5: "jle"}


def format_instruction(instr_bytes: list[int], addr_label: str | None) -> str | None:
    """Format one decoded instruction back into an asm line.

    Returns the formatted line (with `;@raw=` annotation), or None if
    the opcode lacks a formatter (caller should fall back to `db`).

    `addr_label`: symbolic name to use for the address operand, if any.
    Caller resolves the target offset → label name before calling.
    """
    op = instr_bytes[0]
    raw = ",".join(f"0x{b:02X}" for b in instr_bytes)

    def line(body: str) -> str:
        return f"\t{body}\t;@raw={raw}"

    if op == 0x05:
        return line("ret")
    if op == 0x06:
        return line("break")
    if op == 0x11:
        return line("killChannel")
    if op == 0x07:  # jmp addr16
        addr = (instr_bytes[1] << 8) | instr_bytes[2]
        target = addr_label or f"0x{addr:04X}"
        return line(f"jmp {target}")
    if op == 0x04:  # call addr16
        addr = (instr_bytes[1] << 8) | instr_bytes[2]
        target = addr_label or f"0x{addr:04X}"
        return line(f"call {target}")
    if op == 0x08:  # setup channel=N, address=addr16
        ch = instr_bytes[1]
        addr = (instr_bytes[2] << 8) | instr_bytes[3]
        target = addr_label or f"0x{addr:04X}"
        return line(f"setup channel=0x{ch:02X}, address={target}")
    if op == 0x09:  # djnz [var], addr16
        var = instr_bytes[1]
        addr = (instr_bytes[2] << 8) | instr_bytes[3]
        target = addr_label or f"0x{addr:04X}"
        return line(f"djnz [0x{var:02X}], {target}")
    if op == 0x12:  # text id, x, y, color
        text_id = (instr_bytes[1] << 8) | instr_bytes[2]
        x, y, color = instr_bytes[3], instr_bytes[4], instr_bytes[5]
        return line(f"text id=0x{text_id:04X}, x={x}, y={y}, color=0x{color:02X}")
    if op == 0x0A:  # cond_jump
        cond = instr_bytes[1]
        var = instr_bytes[2]
        if cond & 0x80:
            second_op = f"[0x{instr_bytes[3]:02X}]"
            addr_pos = 4
        elif cond & 0x40:
            second_op = f"0x{(instr_bytes[3] << 8) | instr_bytes[4]:04X}"
            addr_pos = 5
        else:
            second_op = f"0x{instr_bytes[3]:02X}"
            addr_pos = 4
        addr = (instr_bytes[addr_pos] << 8) | instr_bytes[addr_pos + 1]
        target = addr_label or f"0x{addr:04X}"
        cmp_type = cond & 0x07
        mnem = COND_MNEMONIC.get(cmp_type, f"jcond_{cmp_type:x}")
        return line(f"{mnem} [0x{var:02X}], {second_op}, {target}")
    return None  # no formatter — caller falls back to db


def rewrite_source(lines: list[str]) -> tuple[list[str], dict]:
    """Rewrite all decodable db blocks as proper mnemonics + labels.

    For every db block in the source:
      1. Decode the bytes linearly via decode_block().
      2. Resolve any address operands: if the target offset falls within
         a db block (this one or another), record (target_offset, name)
         in `synthetic_labels`. The label name is `LABEL_<HEX>` matching
         the existing disasm convention.
      3. Emit a replacement sequence of asm lines:
         - For each instruction boundary that is a known target, emit
           `LABEL_<HEX>:` BEFORE the instruction.
         - For each instruction, emit a formatted mnemonic line. If the
           opcode lacks a formatter (e.g., video opcodes whose offset
           encoding we don't reverse-engineer here), keep that single
           instruction as `db <bytes>`.
      4. Replace the db-block lines in the output with the new sequence.

    Skips db blocks that fail to decode cleanly (those stay as db).

    Returns: (new_lines, stats_dict)
    """
    label_at_pos = collect_labels(lines)

    # First pass: walk byte positions to find db-block ranges + each
    # block's start byte-offset (the absolute address where its first
    # byte sits in the bytecode address space).
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
        pos += estimate_line_bytes(line)

    runs = find_db_runs(lines)

    # First decode pass: collect all jump targets that fall within ANY
    # db block (these need synthetic labels). We do this BEFORE emitting
    # rewritten lines, because a jump target in block A may point into
    # block B — we want to know all targets up front so we can insert
    # labels at the right boundaries.
    db_ranges: list[tuple[int, int, list[int]]] = []  # (start_pos, end_pos, bytes)
    for start, end, bytes_ in runs:
        run_pos = pos_at_line[start]
        db_ranges.append((run_pos, run_pos + len(bytes_), bytes_))

    def addr_in_db(addr: int) -> tuple[int, int, list[int]] | None:
        for r in db_ranges:
            if r[0] <= addr < r[1]:
                return r
        return None

    synthetic_label_at: dict[int, str] = {}

    decoded_blocks: dict[int, list] = {}  # start_line → decoded list
    for start, end, bytes_ in runs:
        decoded = decode_block(bytes_)
        if decoded is None:
            continue
        decoded_blocks[start] = decoded
        run_pos = pos_at_line[start]
        for inst_off, inst_size, addr_positions, mnemonic in decoded:
            for ao_in_inst, ao_size in addr_positions:
                addr = (bytes_[inst_off + ao_in_inst] << 8) | bytes_[inst_off + ao_in_inst + 1]
                target_block = addr_in_db(addr)
                if target_block is None:
                    continue
                # Verify the target is on an instruction boundary in
                # the target block. If not, we cannot safely emit a
                # label there (the disasm would be inconsistent).
                t_start, _, t_bytes = target_block
                target_offset_in_block = addr - t_start
                # Decode the target block; check if any instruction
                # starts at target_offset_in_block.
                t_decoded = decode_block(t_bytes)
                if t_decoded is None:
                    continue
                boundaries = {inst[0] for inst in t_decoded}
                if target_offset_in_block in boundaries:
                    # Don't synthesize a label if one already exists at
                    # this absolute offset (would emit a duplicate
                    # label-def line). Re-use the existing label.
                    if addr not in label_at_pos:
                        synthetic_label_at.setdefault(addr, f"LABEL_{addr:04X}")

    # Build a unified resolver: given an address, return its label name
    # (existing or synthetic), or None.
    def label_for_addr(addr: int) -> str | None:
        if addr in label_at_pos:
            return label_at_pos[addr]
        if addr in synthetic_label_at:
            return synthetic_label_at[addr]
        return None

    # Second pass: emit replacement lines for each rewritten db block.
    # Replace the original db lines (start..end) with new sequence.
    out_lines = list(lines)  # copy; we'll splice
    # Process from last to first to keep indices stable.
    stats = {
        "db_runs_total": len(runs),
        "db_runs_rewritten": 0,
        "db_runs_skipped_decode": 0,
        "instructions_emitted": 0,
        "instructions_kept_as_db": 0,
        "synthetic_labels_emitted": 0,
    }
    for start, end, bytes_ in reversed(runs):
        decoded = decoded_blocks.get(start)
        if decoded is None:
            stats["db_runs_skipped_decode"] += 1
            continue
        run_pos = pos_at_line[start]
        new_block: list[str] = []
        for inst_off, inst_size, addr_positions, mnemonic in decoded:
            abs_offset = run_pos + inst_off
            # Insert a synthetic label here if needed.
            if abs_offset in synthetic_label_at:
                new_block.append(f"{synthetic_label_at[abs_offset]}:")
                stats["synthetic_labels_emitted"] += 1
            instr_bytes = bytes_[inst_off:inst_off + inst_size]
            # Resolve address operand if any.
            addr_label: str | None = None
            for ao_in_inst, ao_size in addr_positions:
                addr = (instr_bytes[ao_in_inst] << 8) | instr_bytes[ao_in_inst + 1]
                addr_label = label_for_addr(addr)
                break  # first (and only) addr operand
            formatted = format_instruction(instr_bytes, addr_label)
            if formatted is None:
                # Keep this instruction as a single `db` line.
                raw = ", ".join(f"0x{b:02X}" for b in instr_bytes)
                new_block.append(f"\tdb {raw}")
                stats["instructions_kept_as_db"] += 1
            else:
                new_block.append(formatted)
                stats["instructions_emitted"] += 1
        # Splice
        out_lines[start:end] = new_block
        stats["db_runs_rewritten"] += 1

    return out_lines, stats


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path)
    p.add_argument("-o", "--output", type=Path,
                   help="rewrite mode: write rewritten .asm with db blocks decoded")
    p.add_argument("--report", action="store_true",
                   help="report-only mode (default if -o not given)")
    args = p.parse_args()

    lines = args.input.read_text().splitlines()

    if args.output and not args.report:
        out_lines, stats = rewrite_source(lines)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(out_lines) + "\n")
        print(f"=== rewrite: {args.input.name} → {args.output.name} ===")
        for k, v in stats.items():
            print(f"  {k}: {v}")
        return

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

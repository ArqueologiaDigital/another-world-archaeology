#!/usr/bin/env python3
"""Cross-branch structural-similarity analysis for AW VM bytecode.

Treats each .asm file as a stream of normalized opcode tokens —
ignoring address operands (which differ between ports because of
different memory layouts) but preserving opcode + non-address
operand structure (channel numbers, var indices, immediates).

Two .asm files with the same logical program will produce the same
opcode stream even when their addresses differ. So:

    structural_match(a, b) = LCS(opcode_stream(a), opcode_stream(b))

The longer the common subsequence, the more code the two ports share
in structure.

Tokens are emitted at three granularity levels:
  - "opcode_only": just the opcode byte (coarse). Best for big-picture
    similarity.
  - "opcode_plus_short_operands": opcode + non-address operand bytes.
    Catches semantic differences like "setup channel=0x09" vs
    "setup channel=0x0A".
  - "full": every byte. Same as raw byte-level diff. (Reference.)

For each opcode, the AW VM has a known number of address bytes that
must be skipped during normalization. The opcode table below encodes
this.

Usage:
    python3 tools/bytecode_structural_diff.py <asm-a> <asm-b>
    python3 tools/bytecode_structural_diff.py <asm-a> <asm-b> --detailed
    python3 tools/bytecode_structural_diff.py --pairs ...
"""
from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path
from typing import Iterable

# AW VM opcode table: opcode_byte -> (mnemonic, total_size, address_byte_offsets)
# The "address byte offsets" are positions within the opcode bytes that hold
# absolute bytecode addresses (which vary per port). Other operand bytes
# (channel numbers, var indices, immediates, palette indices) are
# port-stable and preserved during normalization.
#
# Variable-size opcodes (text, video) are handled separately.
OPCODE_TABLE = {
    0x00: ("mov_var_imm",     4, ()),     # mov [var], imm16     — no address
    0x01: ("mov_var_var",     3, ()),     # mov [var], [var]
    0x02: ("add_var_var",     3, ()),     # add [var], [var]
    0x03: ("add_var_imm",     4, ()),     # add [var], imm16
    0x04: ("call",            3, (1, 2)), # call addr16
    0x05: ("ret",             1, ()),
    0x06: ("break",           1, ()),
    0x07: ("jmp",             3, (1, 2)), # jmp addr16
    0x08: ("setup",           4, (2, 3)), # setup channel=N, addr16 — addr at bytes 2,3
    0x09: ("djnz",            4, (2, 3)), # djnz [var], addr16
    0x0A: ("conditional_jump", -1, ()),   # variable; address bytes at end (handled below)
    0x0B: ("setPalette",      3, ()),     # setPalette N (1 byte)
    0x0C: ("freezeChannels",  4, ()),     # freezeChannels first, last, op
    0x0D: ("selectVideoPage", 2, ()),
    0x0E: ("fill",            3, ()),     # fill page, color
    0x0F: ("copyVideoPage",   3, ()),
    0x10: ("blitFramebuffer", 2, ()),
    0x11: ("killChannel",     1, ()),
    0x12: ("text",            6, ()),     # text id, x, y, color  (id is to string table — port-stable)
    0x13: ("sub_var_var",     3, ()),
    0x14: ("and_var_imm",     4, ()),
    0x18: ("play",            6, ()),     # play id, freq, vol, channel
    0x19: ("load",            3, ()),     # load resource id (or bankSwitch)
    # Video opcodes (high bit set or specific encoding) — variable size.
    # Handled separately by the parser.
}


# `je`/`jne`/`jl`/`jg`/`jle`/`jge` etc. are all opcode 0x0A with
# different *condition* bytes. The total size depends on the condition.
# Format: 0x0A <cond> <var> <imm-or-var-bytes-by-cond-flag> <addr-hi> <addr-lo>
# We treat all as a single normalized token "cond_jump" with the cond byte
# preserved (since it's the opcode subtype) and variable address ignored.

ADDRESS_PLACEHOLDER = 0xFF  # sentinel byte for "address operand here"


def parse_asm_to_bytes(asm_path: Path) -> list[int]:
    """Extract the raw bytecode bytes from an .asm file's `;@raw=...` comments."""
    text = asm_path.read_text()
    out = []
    for m in re.finditer(r';@raw=([0-9A-Fa-fx,]+)', text):
        for s in m.group(1).split(','):
            s = s.strip()
            if s:
                out.append(int(s, 0))
    return out


def tokenize(raw: list[int], granularity: str = "opcode_plus_short_operands") -> list[str]:
    """Walk `raw` and emit tokens. Returns a list of string tokens.

    Granularities:
      - "opcode_only": one token per instruction = just the opcode mnemonic.
      - "opcode_plus_short_operands": opcode + non-address operand bytes
         packed as hex.
      - "full": every byte verbatim (for sanity-check).
    """
    tokens = []
    i = 0
    n = len(raw)
    while i < n:
        op = raw[i]
        if op == 0x0A:
            # Conditional jump. Format:
            #   0x0A <cond> <var-or-imm-bytes-by-cond-flag-bits> <addr-hi> <addr-lo>
            # The cond byte's high bits encode operand type:
            #   bit 7 (0x80) — second operand is a var (1 byte) instead of imm (2 bytes)
            #   bit 6 (0x40) — second operand is imm (1 byte) instead of imm (2 bytes)
            cond = raw[i + 1]
            var_byte = raw[i + 2]
            # Operand byte count:
            if cond & 0x80:
                op_bytes = 1  # var
            elif cond & 0x40:
                op_bytes = 1  # short imm
            else:
                op_bytes = 2  # long imm
            total = 1 + 1 + 1 + op_bytes + 2  # opcode + cond + var + operand + addr
            if granularity == "opcode_only":
                tokens.append("cond_jump")
            elif granularity == "opcode_plus_short_operands":
                # Preserve cond byte; placeholder for addr
                tokens.append(f"cond_jump:{cond:02x}")
            else:
                tokens.append(f"0a:{cond:02x}:{':'.join(f'{b:02x}' for b in raw[i+2:i+total-2])}")
            i += total
            continue

        if op == 0x12:
            # text id, x, y, color — 6 bytes total. id is port-stable.
            total = 6
            if granularity == "opcode_only":
                tokens.append("text")
            elif granularity == "opcode_plus_short_operands":
                tokens.append(f"text:{':'.join(f'{b:02x}' for b in raw[i+1:i+total])}")
            else:
                tokens.append(f"12:{':'.join(f'{b:02x}' for b in raw[i+1:i+total])}")
            i += total
            continue

        # Video opcodes: bit 7 set (0x40+ with high bit) — variable size
        if op & 0x80:
            # video type=2 (high-byte offset, plus various optional bytes)
            # Format depends on flag bits. Conservatively skip 5 bytes
            # (offset_hi + offset_lo + x + y + zoom) for the simplest variant.
            # The exact layout is complex; for structural matching, we treat
            # all video-type-1/2 opcodes as one token "video".
            # Try the standard 5-byte form first; fall back to opcode-only.
            total = 5
            # Check if there's a flag byte that makes it longer
            if op & 0x20:
                total = 6  # zoom byte present
            if granularity == "opcode_only":
                tokens.append("video")
            elif granularity == "opcode_plus_short_operands":
                # Preserve the flag bits in the opcode (these mark variant)
                tokens.append(f"video:{op:02x}")
            else:
                tokens.append(f"{op:02x}:{':'.join(f'{b:02x}' for b in raw[i+1:i+total])}")
            i += total
            continue

        # Plain opcodes from the table
        info = OPCODE_TABLE.get(op)
        if info is None:
            # Unknown opcode — emit raw byte and advance one
            tokens.append(f"unknown:{op:02x}")
            i += 1
            continue
        mnemonic, total, addr_offsets = info
        if total < 0:
            # Variable-size opcode not handled here
            tokens.append(f"{mnemonic}:variable")
            i += 1
            continue

        if granularity == "opcode_only":
            tokens.append(mnemonic)
        elif granularity == "opcode_plus_short_operands":
            # Replace bytes at addr_offsets with placeholder
            operand_bytes = []
            for j in range(1, total):
                if j in addr_offsets:
                    operand_bytes.append("addr")
                else:
                    if i + j < n:
                        operand_bytes.append(f"{raw[i+j]:02x}")
            if operand_bytes:
                tokens.append(f"{mnemonic}:{':'.join(operand_bytes)}")
            else:
                tokens.append(mnemonic)
        else:
            tokens.append(":".join(f"{b:02x}" for b in raw[i:i+total]))
        i += total

    return tokens


def similarity(tokens_a: list[str], tokens_b: list[str]) -> dict:
    """Compute matching-block stats between two token streams."""
    sm = difflib.SequenceMatcher(a=tokens_a, b=tokens_b, autojunk=False)
    matching = sm.get_matching_blocks()  # last block has size 0
    matched_tokens = sum(b.size for b in matching)
    total_a, total_b = len(tokens_a), len(tokens_b)
    ratio = sm.ratio()
    blocks = [(b.a, b.b, b.size) for b in matching if b.size > 0]
    longest = max((b[2] for b in blocks), default=0)
    return {
        "tokens_a": total_a,
        "tokens_b": total_b,
        "matched_tokens": matched_tokens,
        "ratio": ratio,
        "blocks": blocks,
        "longest_block": longest,
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("a", type=Path, nargs="?")
    p.add_argument("b", type=Path, nargs="?")
    p.add_argument("--granularity",
                   choices=["opcode_only", "opcode_plus_short_operands", "full"],
                   default="opcode_plus_short_operands")
    p.add_argument("--detailed", action="store_true",
                   help="show longest matching blocks + their content snippets")
    p.add_argument("--matrix", action="store_true",
                   help="run cross-branch matrix on every (branch, stage) pair found in src/levels/")
    p.add_argument("--src-tree", type=Path,
                   default=Path("../another-world-source-reconstruction/src/levels"),
                   help="src/levels root for --matrix mode")
    args = p.parse_args()

    if args.matrix:
        run_matrix(args.src_tree, args.granularity)
        return

    if not (args.a and args.b):
        sys.exit("specify two .asm files (or --matrix)")
    raw_a = parse_asm_to_bytes(args.a)
    raw_b = parse_asm_to_bytes(args.b)
    print(f"a: {args.a}")
    print(f"   raw bytes: {len(raw_a)}")
    print(f"b: {args.b}")
    print(f"   raw bytes: {len(raw_b)}")
    tok_a = tokenize(raw_a, args.granularity)
    tok_b = tokenize(raw_b, args.granularity)
    print(f"\ntokens (granularity={args.granularity}): a={len(tok_a)}, b={len(tok_b)}")

    sim = similarity(tok_a, tok_b)
    print(f"\nsimilarity ratio: {sim['ratio']:.3f}")
    print(f"matched tokens:   {sim['matched_tokens']}")
    print(f"longest block:    {sim['longest_block']} tokens")

    if args.detailed:
        print("\ntop 10 matching blocks (by size):")
        blocks = sorted(sim["blocks"], key=lambda b: -b[2])[:10]
        for ai, bi, sz in blocks:
            print(f"  size={sz:5d}  a[{ai}..{ai+sz}] b[{bi}..{bi+sz}]")
            print(f"    a sample: {' '.join(tok_a[ai:ai+min(5,sz)])}...")


def run_matrix(src_tree: Path, granularity: str) -> None:
    branches = sorted(d for d in src_tree.glob("*") if d.is_dir())
    # Map (branch, stage) -> tokens
    streams: dict[tuple[str, str], list[str]] = {}
    for b in branches:
        for asm in sorted(b.glob("*.asm")):
            stage = asm.stem
            raw = parse_asm_to_bytes(asm)
            streams[(b.name, stage)] = tokenize(raw, granularity)

    print(f"granularity = {granularity}")
    print(f"streams: {len(streams)}")
    print()

    # Find all stages that appear in >1 branch
    stages_per_branch = {}
    for (br, st), _ in streams.items():
        stages_per_branch.setdefault(st, []).append(br)
    multi_stage = {st: brs for st, brs in stages_per_branch.items() if len(brs) >= 2}

    for stage, brs in sorted(multi_stage.items()):
        print(f"=== {stage} ({len(brs)} branches: {', '.join(sorted(brs))}) ===")
        # Pairwise similarity
        for i, b1 in enumerate(sorted(brs)):
            for b2 in sorted(brs)[i+1:]:
                t1 = streams[(b1, stage)]
                t2 = streams[(b2, stage)]
                sim = similarity(t1, t2)
                print(f"  {b1:<22s} vs {b2:<22s}  "
                      f"ratio={sim['ratio']:.3f}  "
                      f"matched={sim['matched_tokens']:5d}/{max(len(t1),len(t2)):5d}  "
                      f"longest_block={sim['longest_block']}")
        print()


if __name__ == "__main__":
    main()

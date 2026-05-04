#!/usr/bin/env python3
"""Resolve every surviving `;@raw=` annotation by replacing the
ambiguous symbolic operand with the literal address the annotation
encodes, then dropping the annotation.

For each annotated source line:
  1. Parse the mnemonic + operands.
  2. Decode the `;@raw=` bytes.
  3. Identify which operand the annotation's address-bearing bytes
     correspond to, based on the mnemonic's encoding layout.
  4. Replace that operand's symbolic value with a literal hex
     value matching the annotation.
  5. Drop the `;@raw=` annotation.

Mnemonics covered:
  - je, jne, jg, jge, jl, jle: 6-byte encoding
        `0x0A, subop, b_byte, c_byte_or_word, addr_word`
        target = operand[2], replace with literal addr_word.
  - jmp:                      3-byte encoding `0x07, addr_word`
        target = operand[0], replace with literal addr_word.
  - call:                     3-byte encoding `0x04, addr_word`
        target = operand[0], replace with literal addr_word.
  - djnz:                     4-byte encoding
        `0x09, var_byte, addr_word`
        target = operand[1], replace with literal addr_word.
  - setup:                    4-byte encoding
        `0x08, channel_byte, addr_word`
        target = operand[1] (address kw), replace literal.
  - video (with zoom or w/o): offset operand → literal.

Special cases:
  - bankSwitch with annotation matching canonical encoding
    (0x3E80 | bank): just drop annotation (already correct).

Usage:
  python3 tools/resolve_raw_collisions.py [--dry-run] [path...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_TREE / "src" / "levels"

RE_RAW = re.compile(r"\s*;@raw=([0-9a-fA-FxX,\s]+)\s*$")


def parse_bytes(s: str) -> list[int]:
    out = []
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if tok.startswith(("0x", "0X")):
            out.append(int(tok, 16))
        else:
            out.append(int(tok))
    return out


def split_operands(rest: str) -> list[str]:
    """Split a comma-separated operand list, respecting brackets."""
    out: list[str] = []
    cur: list[str] = []
    depth = 0
    for ch in rest:
        if ch == "[":
            depth += 1
            cur.append(ch)
        elif ch == "]":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    last = "".join(cur).strip()
    if last:
        out.append(last)
    return out


def split_mnemonic(text: str) -> tuple[str, str]:
    """Returns (mnemonic, operand_text). Strips any inline `;` comment
    BEFORE the `;@raw=` (e.g. `bankSwitch 6;  Secret Code…`)."""
    parts = text.split(None, 1)
    if not parts:
        return "", ""
    mn = parts[0]
    rest = parts[1] if len(parts) > 1 else ""
    # Strip a non-`;@raw=` inline comment.
    sc = rest.find(";")
    if sc != -1 and not rest[sc:].startswith(";@"):
        rest = rest[:sc]
    return mn, rest


def fmt_hex_word(v: int) -> str:
    return f"0x{v:04X}"


def fmt_hex_byte(v: int) -> str:
    return f"0x{v:02X}"


def find_keyword(operands: list[str], key: str) -> int | None:
    """Return the index of the operand whose key is `key`."""
    for i, op in enumerate(operands):
        if "=" in op:
            k, _ = op.split("=", 1)
            if k.strip() == key:
                return i
    return None


def replace_keyword_value(op: str, new_value: str) -> str:
    if "=" not in op:
        return op
    k, _ = op.split("=", 1)
    return f"{k.strip()}={new_value}"


def replace_positional(operands: list[str], idx: int, new_value: str) -> list[str]:
    out = list(operands)
    if "=" in out[idx]:
        out[idx] = replace_keyword_value(out[idx], new_value)
    else:
        out[idx] = new_value
    return out


JE_FAMILY = {"je", "jne", "jg", "jge", "jl", "jle"}


def resolve_line(line: str) -> tuple[str, str | None]:
    """Returns (new_line, action_or_none).
    Actions: 'literal_target' / 'literal_offset' / 'redundant' / None.
    """
    m = RE_RAW.search(line)
    if not m:
        return line, None
    raw = parse_bytes(m.group("1") if False else m.group(1))
    if not raw:
        return line, None

    instr_text = line[: m.start()].rstrip()
    leading_ws = line[: len(line) - len(line.lstrip())]
    trailing_nl = "\n" if line.endswith("\n") else ""

    # Strip leading whitespace before parsing mnemonic.
    body = instr_text.lstrip()
    mn, rest = split_mnemonic(body)
    operands = split_operands(rest)

    new_text: str | None = None
    action: str | None = None

    if mn in JE_FAMILY and len(raw) in (6, 7) and raw[0] == 0x0A and len(operands) == 3:
        # operand[2] is jump target. Encoding length depends on c
        # operand: byte form (raw len 6) when c ≤ 0xFF, word form
        # (raw len 7) when c > 0xFF (subop bit 6 set).
        if len(raw) == 7:
            addr = (raw[5] << 8) | raw[6]
        else:
            addr = (raw[4] << 8) | raw[5]
        operands = replace_positional(operands, 2, fmt_hex_word(addr))
        new_text = f"{mn} {', '.join(operands)}"
        action = "literal_target"

    elif mn == "jmp" and len(raw) == 3 and raw[0] == 0x07 and len(operands) == 1:
        addr = (raw[1] << 8) | raw[2]
        operands = replace_positional(operands, 0, fmt_hex_word(addr))
        new_text = f"{mn} {', '.join(operands)}"
        action = "literal_target"

    elif mn == "call" and len(raw) == 3 and raw[0] == 0x04 and len(operands) == 1:
        addr = (raw[1] << 8) | raw[2]
        operands = replace_positional(operands, 0, fmt_hex_word(addr))
        new_text = f"{mn} {', '.join(operands)}"
        action = "literal_target"

    elif mn == "djnz" and len(raw) == 4 and raw[0] == 0x09 and len(operands) == 2:
        addr = (raw[2] << 8) | raw[3]
        operands = replace_positional(operands, 1, fmt_hex_word(addr))
        new_text = f"{mn} {', '.join(operands)}"
        action = "literal_target"

    elif mn == "setup" and len(raw) == 4 and raw[0] == 0x08 and len(operands) >= 2:
        # setup channel=N, address=A (or positional)
        addr_idx = find_keyword(operands, "address")
        if addr_idx is None:
            addr_idx = 1
        addr = (raw[2] << 8) | raw[3]
        operands = replace_positional(operands, addr_idx, fmt_hex_word(addr))
        new_text = f"{mn} {', '.join(operands)}"
        action = "literal_target"

    elif mn == "video":
        # Two encoding variants: 0x80-0xFF compact form (4 bytes total)
        # and 0x40-0x7F long form (5+ bytes). Both have a polygon
        # offset that we want as a literal.
        offset_idx = find_keyword(operands, "offset")
        if offset_idx is not None:
            if raw and raw[0] & 0x80:
                # Compact: opcode is the high byte of (0x8000 | offs/2).
                # raw = [hi, lo, x, y]: offs = ((hi & 0x7F) << 8 | lo) * 2
                if len(raw) >= 2:
                    offs = (((raw[0] & 0x7F) << 8) | raw[1]) * 2
                    operands = replace_positional(
                        operands, offset_idx, fmt_hex_word(offs)
                    )
                    new_text = f"{mn} {', '.join(operands)}"
                    action = "literal_offset"
            elif raw and (raw[0] & 0xC0) == 0x40:
                # Long form: opcode, offs_hi, offs_lo, [x bytes...]
                # offs = (offs_hi << 8 | offs_lo) * 2, but offs_hi has
                # bit-7 spare, so masking to 0x7F is safe.
                if len(raw) >= 3:
                    offs = (((raw[1] & 0x7F) << 8) | raw[2]) * 2
                    operands = replace_positional(
                        operands, offset_idx, fmt_hex_word(offs)
                    )
                    new_text = f"{mn} {', '.join(operands)}"
                    action = "literal_offset"

    elif mn == "bankSwitch" and len(raw) == 3 and raw[0] == 0x19:
        # Drop the annotation only if the encoder would produce these
        # bytes anyway (i.e., it's the canonical 0x3E80 | bank form).
        # Legacy_d/legacy_e were already migrated to `;@enc=...` by
        # the earlier pass, so anything reaching here should be
        # canonical.
        if len(operands) >= 1:
            try:
                bank = int(operands[0], 0)
            except ValueError:
                bank = -1
            expected = 0x3E80 | (bank & 0xF) if bank >= 0 else None
            actual = (raw[1] << 8) | raw[2]
            if expected == actual:
                new_text = instr_text  # keep original instruction text
                action = "redundant"

    if new_text is None:
        return line, None

    # Reattach a trailing inline comment (if there was one before
    # `;@raw=`). E.g., `bankSwitch 6;  Secret Code Entry Screen ...`
    # currently gets stripped to just `bankSwitch 6` after our
    # rewrite. Preserve the comment.
    pre_raw = line[: m.start()]
    semi = pre_raw.find(";")
    inline_comment = ""
    if semi != -1 and not pre_raw[semi:].startswith(";@"):
        inline_comment = pre_raw[semi:].rstrip()
    if inline_comment:
        # Place the comment after the new instruction text.
        return (
            f"{leading_ws}{new_text}\t{inline_comment}{trailing_nl}",
            action,
        )
    return f"{leading_ws}{new_text}{trailing_nl}", action


def process_file(path: Path, dry_run: bool) -> dict[str, int]:
    counts: dict[str, int] = {}
    out: list[str] = []
    changed = False
    for line in path.read_text().splitlines(keepends=True):
        new_line, action = resolve_line(line)
        if action is not None:
            counts[action] = counts.get(action, 0) + 1
            changed = True
        out.append(new_line)
    if changed and not dry_run:
        path.write_text("".join(out))
    return counts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    if args.paths:
        targets: list[Path] = []
        for p in args.paths:
            if p.is_file():
                targets.append(p)
            elif p.is_dir():
                targets.extend(sorted(p.rglob("*.inc")))
                targets.extend(sorted(p.rglob("*.asm")))
                targets.extend(sorted(p.rglob("*.asm.in")))
    else:
        targets = (
            sorted(LEVELS.rglob("*.asm"))
            + sorted(LEVELS.rglob("*.inc"))
            + sorted(LEVELS.rglob("*.asm.in"))
        )

    aggregate: dict[str, int] = {}
    files_changed = 0
    for path in targets:
        # Skip frozen reference dirs.
        rel = path.relative_to(LEVELS)
        if rel.parts and rel.parts[0] in {"_canonicalized", "_phase3b_demo"}:
            continue
        counts = process_file(path, args.dry_run)
        if counts:
            files_changed += 1
            for k, v in counts.items():
                aggregate[k] = aggregate.get(k, 0) + v

    print(f"files changed: {files_changed}")
    for k, v in sorted(aggregate.items()):
        print(f"  {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Preprocessor for AW VM .asm.in source files with conditional blocks.

Source format adds three new comment-syntax directives:

    ;@if <flag-expr>
    ;@elif <flag-expr>
    ;@else
    ;@endif

A `flag-expr` is one of:
    BRANCH == "<branch-name>"
    BRANCH != "<branch-name>"
    BRANCH in ("<a>", "<b>", ...)
    <flag> == on
    <flag> == off
    <flag> == "<value>"

Flags + their values come from a per-target `.flags` file (the same
ones at another-world-source-reconstruction/releases/<target>.flags).

The preprocessor:
1. Reads the .flags file (KEY=VALUE pairs).
2. Reads the .asm.in source.
3. For each `;@if` block, evaluates the condition against the flags.
4. Keeps only the matched branch's content; strips others.
5. Writes the result as a plain .asm file ready for awvm-asm.

`BRANCH` is special — it's set from the .flags file's
`BYTECODE_BRANCH` value (so the same flag drives both the build
target and the conditional logic).

Usage:
    python3 tools/awvm_preprocess.py <input.asm.in> <flags-file> -o <output.asm>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


RE_DIRECTIVE = re.compile(r"^\s*;@(if|elif|else|endif)\b\s*(.*?)\s*$")

# `FILL(n, 0xXX)` macro — expands to `n` bytes of value `0xXX` at preprocess
# time. Useful for compact representation of trailing-padding regions in
# the unified source. Optional trailing inline comment is allowed.
RE_FILL = re.compile(
    r'^(?P<indent>\s*)FILL\(\s*(?P<count>\d+)\s*,\s*'
    r'(?P<byte>0x[0-9A-Fa-f]+|\d+)\s*\)\s*(?P<comment>;.*)?\s*$'
)
FILL_BYTES_PER_LINE = 16


def expand_fill_macros(text: str) -> str:
    """Expand `FILL(n, 0xXX)` lines into runs of `db <byte>, ...` lines.

    Output is byte-equivalent to the input under awvm-asm: each FILL
    macro is replaced by exactly `n` bytes worth of `db` directives.
    """
    out: list[str] = []
    for line in text.splitlines():
        m = RE_FILL.match(line)
        if not m:
            out.append(line)
            continue
        indent = m.group('indent')
        count = int(m.group('count'))
        byte_val = int(m.group('byte'), 0)
        if not (0 <= byte_val <= 0xFF):
            raise ValueError(f"FILL byte value out of range: {byte_val:#x}")
        full = count // FILL_BYTES_PER_LINE
        rem = count % FILL_BYTES_PER_LINE
        chunk = ", ".join(f"0x{byte_val:02X}" for _ in range(FILL_BYTES_PER_LINE))
        for _ in range(full):
            out.append(f"{indent}db {chunk}")
        if rem:
            tail = ", ".join(f"0x{byte_val:02X}" for _ in range(rem))
            out.append(f"{indent}db {tail}")
    return "\n".join(out)


def parse_flags(flags_path: Path) -> dict[str, str]:
    """Parse a `KEY=VALUE` shell-style flags file."""
    out = {}
    for line in flags_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip()
        # Strip optional surrounding quotes
        if (v.startswith('"') and v.endswith('"')) or \
           (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        out[k] = v
    # BRANCH alias for BYTECODE_BRANCH (commonly used in conditions)
    if "BYTECODE_BRANCH" in out:
        out.setdefault("BRANCH", out["BYTECODE_BRANCH"])
    return out


def evaluate(expr: str, flags: dict[str, str]) -> bool:
    """Evaluate a conditional expression against the flags."""
    expr = expr.strip()
    # Match `KEY == "value"` or `KEY != "value"` or `KEY == on/off`
    m = re.fullmatch(
        r'(\w+)\s*(==|!=|in)\s*(.+)',
        expr,
    )
    if not m:
        raise ValueError(f"unparseable condition: {expr!r}")
    key, op, rhs = m.group(1), m.group(2), m.group(3).strip()

    actual = flags.get(key)

    if op == "in":
        # KEY in ("a", "b", ...)
        m2 = re.fullmatch(r'\(\s*(.*)\s*\)', rhs)
        if not m2:
            raise ValueError(f"`in` rhs must be a tuple: {rhs!r}")
        items = [s.strip().strip('"').strip("'") for s in m2.group(1).split(",")]
        return actual in items

    # Strip surrounding quotes from rhs
    if (rhs.startswith('"') and rhs.endswith('"')) or \
       (rhs.startswith("'") and rhs.endswith("'")):
        rhs = rhs[1:-1]

    if op == "==":
        return actual == rhs
    if op == "!=":
        return actual != rhs

    raise ValueError(f"unknown operator: {op!r}")


def preprocess(text: str, flags: dict[str, str]) -> str:
    """Process `;@if` / `;@elif` / `;@else` / `;@endif` directives."""
    out_lines = []
    # Stack of (matched-this-block, ever-matched-in-this-block)
    # `matched-this-block` = currently emitting lines from the active branch
    # `ever-matched`       = some branch in this block has matched, so any
    #                       further `;@elif`/`;@else` should be skipped
    stack: list[tuple[bool, bool]] = []

    for line_no, line in enumerate(text.splitlines(keepends=False), start=1):
        m = RE_DIRECTIVE.match(line)
        if m:
            directive = m.group(1)
            rest = m.group(2)
            if directive == "if":
                # Outer "active" depends on enclosing scope
                outer_active = all(s[0] for s in stack)
                if not outer_active:
                    # Whole block skipped; push (False, True) so nested elif/else are skipped
                    stack.append((False, True))
                else:
                    cond = evaluate(rest, flags)
                    stack.append((cond, cond))
            elif directive == "elif":
                if not stack:
                    raise SyntaxError(f"line {line_no}: ;@elif without matching ;@if")
                _, ever = stack[-1]
                if ever:
                    stack[-1] = (False, True)
                else:
                    cond = evaluate(rest, flags)
                    stack[-1] = (cond, cond)
            elif directive == "else":
                if not stack:
                    raise SyntaxError(f"line {line_no}: ;@else without matching ;@if")
                _, ever = stack[-1]
                stack[-1] = (not ever, True)
            elif directive == "endif":
                if not stack:
                    raise SyntaxError(f"line {line_no}: ;@endif without matching ;@if")
                stack.pop()
            continue

        if all(s[0] for s in stack):
            out_lines.append(line)

    if stack:
        raise SyntaxError(f"unterminated ;@if (still {len(stack)} open at EOF)")

    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("input", type=Path, help=".asm.in source")
    p.add_argument("flags", type=Path, help="releases/<target>.flags")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="output .asm path")
    args = p.parse_args()

    flags = parse_flags(args.flags)
    src = args.input.read_text()
    out = preprocess(src, flags)
    out = expand_fill_macros(out)
    args.output.write_text(out)
    in_lines = src.count("\n")
    out_lines = out.count("\n")
    print(f"  {args.input.name} -> {args.output.name}  "
          f"({in_lines} -> {out_lines} lines, BRANCH={flags.get('BRANCH', '?')})")


if __name__ == "__main__":
    main()

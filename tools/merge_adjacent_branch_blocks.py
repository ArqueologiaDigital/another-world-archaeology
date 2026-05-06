#!/usr/bin/env python3
"""Collapse adjacent `;@if BRANCH ... ;@endif` blocks whose bodies are
byte-identical into a single block with the union of their branch
lists.

Pattern matched:

    ;@if BRANCH ==/in (X, Y, ...)
    <body>
    ;@endif
    [optional blank lines]
    ;@if BRANCH ==/in (Z, ...)
    <body, byte-identical>
    ;@endif

Result:

    ;@if BRANCH in (X, Y, ..., Z, ...)
    <body>
    ;@endif

Both blocks must be simple (no `;@elif` / `;@else`). Branch sets
must be disjoint (no overlap). Body comparison is byte-exact.

Usage:
    python3 tools/merge_adjacent_branch_blocks.py <src-tree-root>

Idempotent — running twice is a no-op.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


IF_RE = re.compile(r'^\s*;@if\s+BRANCH\s+(==|in)\s+(.+?)\s*$')
ELIF_RE = re.compile(r'^\s*;@elif\b')
ELSE_RE = re.compile(r'^\s*;@else\b')
ENDIF_RE = re.compile(r'^\s*;@endif\b')
NESTED_IF_RE = re.compile(r'^\s*;@if\b')


def parse_branch_set(op: str, expr: str) -> list[str] | None:
    """Parse a `BRANCH == "X"` or `BRANCH in ("X", "Y", ...)` clause
    into a list of branch names."""
    expr = expr.strip()
    if op == "==":
        m = re.match(r'^"([^"]+)"$', expr)
        if not m:
            return None
        return [m.group(1)]
    if op == "in":
        m = re.match(r'^\((.+)\)$', expr)
        if not m:
            return None
        body = m.group(1)
        names = re.findall(r'"([^"]+)"', body)
        return names if names else None
    return None


def format_branch_in_clause(branches: list[str]) -> str:
    """Emit `BRANCH in ("a", "b", ...)` with the canonical ordering
    used elsewhere in the codebase: amiga first, then cart, dos, gba —
    matching the alphabetical-by-platform order seen in existing source."""
    canonical_order = [
        "chahi_amiga_1991",
        "cartridge_1992",
        "dos_1992",
        "gba_2004",
    ]
    seen = set(branches)
    ordered = [b for b in canonical_order if b in seen]
    # Fallback: keep any non-canonical names appended in input order
    for b in branches:
        if b not in canonical_order and b not in ordered:
            ordered.append(b)
    quoted = ", ".join(f'"{b}"' for b in ordered)
    return f';@if BRANCH in ({quoted})'


def find_block(lines: list[str], start: int) -> tuple[int, list[str], list[str]] | None:
    """Starting at line index `start` (which must be a simple
    `;@if BRANCH …` line — no nested `;@if` inside), return
    (end_index_inclusive, branches, body_lines) if the block is
    simple (no `;@elif`/`;@else`/nested `;@if`). Otherwise return
    None.

    `end_index_inclusive` is the index of the matching `;@endif`.
    """
    head = lines[start]
    m = IF_RE.match(head)
    if not m:
        return None
    branches = parse_branch_set(m.group(1), m.group(2))
    if branches is None:
        return None

    body: list[str] = []
    i = start + 1
    while i < len(lines):
        cur = lines[i]
        if NESTED_IF_RE.match(cur):
            # Nested @if inside the block — too complex, bail.
            return None
        if ELIF_RE.match(cur) or ELSE_RE.match(cur):
            return None
        if ENDIF_RE.match(cur):
            return (i, branches, body)
        body.append(cur)
        i += 1
    return None


def merge_adjacent_in_text(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=False)
    out: list[str] = []
    i = 0
    n_merged = 0

    while i < len(lines):
        line = lines[i]
        if not IF_RE.match(line):
            out.append(line)
            i += 1
            continue

        block_a = find_block(lines, i)
        if block_a is None:
            out.append(line)
            i += 1
            continue
        end_a, branches_a, body_a = block_a

        # Look ahead for a second adjacent block — skipping blank lines.
        j = end_a + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1

        if j >= len(lines) or not IF_RE.match(lines[j]):
            # No second adjacent block — emit this block verbatim.
            out.extend(lines[i : end_a + 1])
            i = end_a + 1
            continue

        block_b = find_block(lines, j)
        if block_b is None:
            out.extend(lines[i : end_a + 1])
            i = end_a + 1
            continue
        end_b, branches_b, body_b = block_b

        # Bodies must be byte-identical.
        if body_a != body_b:
            out.extend(lines[i : end_a + 1])
            i = end_a + 1
            continue

        # Branch sets must be disjoint (sanity check — overlap means
        # the blocks are redundant rather than complementary, which is
        # a different bug).
        if set(branches_a) & set(branches_b):
            out.extend(lines[i : end_a + 1])
            i = end_a + 1
            continue

        # Merge.
        union = branches_a + branches_b
        out.append(format_branch_in_clause(union))
        out.extend(body_a)
        out.append(";@endif")
        n_merged += 1
        i = end_b + 1

    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"
    return new_text, n_merged


def main(roots: list[str]) -> int:
    if not roots:
        print("usage: merge_adjacent_branch_blocks.py <src-tree-root>", file=sys.stderr)
        return 2
    src_root = Path(roots[0])
    unified = src_root / "src" / "levels" / "_unified"
    if not unified.is_dir():
        print(f"not a source-recon root: {src_root}", file=sys.stderr)
        return 2

    total_blocks = 0
    files_changed = 0
    for f in list(unified.rglob("*.inc")) + list(unified.rglob("*.asm.in")):
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        new_text, n = merge_adjacent_in_text(text)
        if n:
            f.write_text(new_text)
            files_changed += 1
            total_blocks += n
            print(f"  {f.relative_to(src_root)}: merged {n} block pair(s)")

    print(f"\nMerged {total_blocks} adjacent ;@if-block pairs across "
          f"{files_changed} files.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

#!/usr/bin/env python3
"""Collapse `;@if BRANCH` blocks where every arm has identical content.

Some unified `.inc` and `.asm.in` files carry conditional blocks
that historically differed per arm but got equalised in a later
rename / fold pass without collapsing the conditional structure.
This tool finds those blocks (every `;@if BRANCH ...` / `;@elif`
arm has byte-identical body lines) and replaces the whole
conditional with the bare body.

Safe because:
  - The body text is, by construction, identical across all arms,
    so emitting it once produces the same source as the existing
    multi-arm version.
  - Symbolic label references inside the body still resolve
    per-arm (the assembler walks the active arm's labels at
    compile time).

Skips nested `;@if` blocks (depth-aware): an inner `;@if` inside
an arm's body is left untouched even if its arms collapse — the
outer arms are still treated as opaque text and compared as such.

Usage:
    python3 tools/collapse_identical_branch_arms.py <src-tree-root>

`<src-tree-root>` is the source-reconstruction repo root.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


IF_RE = re.compile(r"^\s*;@if\b")
ELIF_RE = re.compile(r"^\s*;@elif\b")
ELSE_RE = re.compile(r"^\s*;@else\b")
ENDIF_RE = re.compile(r"^\s*;@endif\b")


def collapse_in_file(text: str) -> tuple[str, int]:
    """Returns (new_text, n_blocks_collapsed)."""
    lines = text.splitlines(keepends=False)
    out = []
    i = 0
    n_collapsed = 0

    while i < len(lines):
        line = lines[i]
        if not IF_RE.match(line):
            out.append(line)
            i += 1
            continue

        # Walk this @if block, depth-aware.
        # Collect arms as list of (header_line, body_lines).
        block_start = i
        arms: list[tuple[str, list[str]]] = []
        cur_header = line
        cur_body: list[str] = []
        i += 1
        depth = 1

        while i < len(lines) and depth > 0:
            cur = lines[i]
            if IF_RE.match(cur):
                depth += 1
                cur_body.append(cur)
            elif ENDIF_RE.match(cur):
                depth -= 1
                if depth == 0:
                    arms.append((cur_header, cur_body))
                    break
                cur_body.append(cur)
            elif depth == 1 and (ELIF_RE.match(cur) or ELSE_RE.match(cur)):
                arms.append((cur_header, cur_body))
                cur_header = cur
                cur_body = []
            else:
                cur_body.append(cur)
            i += 1

        # i now points at the ;@endif line (or off the end if malformed)
        # Decide: collapse or copy verbatim?
        bodies = [tuple(b) for _, b in arms]
        if len(arms) >= 2 and len(set(bodies)) == 1:
            # All arm bodies are identical — emit the body once,
            # drop the @if/@elif/@else/@endif framing.
            out.extend(arms[0][1])
            n_collapsed += 1
        else:
            # Copy the whole block verbatim.
            out.extend(lines[block_start : i + 1])
        i += 1

    new_text = "\n".join(out)
    if text.endswith("\n"):
        new_text += "\n"
    return new_text, n_collapsed


def main(roots: list[str]) -> int:
    if not roots:
        print("usage: collapse_identical_branch_arms.py <src-tree-root>", file=sys.stderr)
        return 2
    src_root = Path(roots[0])
    unified = src_root / "src" / "levels" / "_unified"
    if not unified.is_dir():
        print(f"not a source-recon root: {src_root} (no src/levels/_unified/)", file=sys.stderr)
        return 2

    total_blocks = 0
    files_changed = 0
    for f in list(unified.rglob("*.inc")) + list(unified.rglob("*.asm.in")):
        try:
            text = f.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        new_text, n = collapse_in_file(text)
        if n:
            f.write_text(new_text)
            files_changed += 1
            total_blocks += n

    print(f"Files changed: {files_changed}")
    print(f"Blocks collapsed: {total_blocks}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

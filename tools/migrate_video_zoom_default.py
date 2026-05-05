#!/usr/bin/env python3
"""One-shot migration: drop the now-default `, zoom=0x40` suffix from
`video` instructions where compact form COULD NOT have encoded the
same call.

Background: AWVM_Tools (commits 207a072 + follow-up) makes
`zoom=0x40` the default for full-form CINEMATIC `video` instructions
when the bytecode is unambiguously full form. "Unambiguously full
form" means compact form (opcode 0x80..0xFF) could not have produced
the same bytes — because compact form requires:
  - byte-literal x ≤ 0xFF
  - byte-literal y ≤ 0xFF
  - offset ≤ 0xFFFE
  - type = CINEMATIC

When any of those constraints is violated, the encoder MUST emit full
form, so omitting `zoom=0x40` is unambiguous (defaults back to 0x40 in
the encoder). When ALL those constraints hold, the encoder would pick
compact form by default, so we keep `zoom=0x40` explicit to force
full-form encoding.

Idempotent: running twice is a no-op.

Constraints checked in this script:
  - x is variable (`x=[...]`) → strippable
  - y is variable (`y=[...]`) → strippable
  - x literal > 0xFF → strippable
  - y literal > 0xFF → strippable
  - else (byte-literal x and y both ≤ 0xFF) → keep `zoom=0x40`

Offset constraint (≤ 0xFFFE) is NOT checked because most offsets are
symbolic labels that resolve only at assembly time; not knowing the
offset means we conservatively keep `zoom=0x40` for the byte-literal
case even when the offset would have made compact form invalid. This
under-strips but never breaks round-trip.

Lines with `zoom=[VAR]` or `;@enc=alt` (variable zoom) are not
touched.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path


VIDEO_LINE = re.compile(
    r"^(\s*)video\s+offset=([^,]+),\s*x=(\S+?),\s*y=(\S+?),\s*zoom=0x40(\s.*)?$"
)


def is_var(operand: str) -> bool:
    return operand.startswith("[")


def parse_int(operand: str):
    try:
        return int(operand, 0)
    except (ValueError, TypeError):
        return None


def can_strip_zoom(x: str, y: str) -> bool:
    if is_var(x) or is_var(y):
        return True
    xv = parse_int(x)
    yv = parse_int(y)
    if xv is None or yv is None:
        return False
    if xv > 0xFF or yv > 0xFF:
        return True
    return False


def transform_line(line: str) -> tuple[str, bool]:
    m = VIDEO_LINE.match(line.rstrip("\n"))
    if not m:
        return line, False
    indent, offset, x, y, tail = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5) or ""
    if not can_strip_zoom(x, y):
        return line, False
    new_line = f"{indent}video offset={offset}, x={x}, y={y}{tail}\n"
    return new_line, True


def migrate(src_tree: Path) -> tuple[int, int]:
    files_changed = 0
    lines_changed = 0
    for ext in ("*.asm", "*.inc", "*.asm.in"):
        for path in src_tree.rglob(ext):
            text = path.read_text(encoding="utf-8")
            new_lines = []
            n = 0
            for line in text.splitlines(keepends=True):
                new_line, changed = transform_line(line)
                new_lines.append(new_line)
                if changed:
                    n += 1
            if n:
                path.write_text("".join(new_lines), encoding="utf-8")
                files_changed += 1
                lines_changed += n
    return files_changed, lines_changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src-tree", required=True, type=Path)
    args = ap.parse_args()

    files, lines = migrate(args.src_tree)
    print(f"migrated {lines} `video` instructions across {files} files")


if __name__ == "__main__":
    main()

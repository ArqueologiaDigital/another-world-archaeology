#!/usr/bin/env python3
"""Collapse empty `;@if`/`;@elif`/`;@else`/`;@endif` arms.

Two transformations:

1. Fully-empty block (every arm contributes no meaningful content) →
   delete the whole block.

2. Partially-empty block (at least one but not all arms is empty) →
   re-emit the surviving arms as a fresh chain (first survivor uses
   `;@if`, later survivors use `;@elif`).

"Meaningful content" means any line that is not pure whitespace and
not a plain `;` comment. `;@<directive>` and `;@include` lines DO
count as meaningful (they're real source code).

Usage:
  python3 tools/collapse_empty_arms.py [--dry-run] [path...]

If no paths given, processes all `*.inc` and `*.asm.in` under
the source-reconstruction tree. Run verify_stage and verify_unified
after to confirm byte-identical output.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _paths import AW_SRC

SRC_ROOT = AW_SRC


def is_meaningful(line: str) -> bool:
    s = line.strip()
    if not s:
        return False
    if s.startswith(";@"):
        return True
    if s.startswith(";"):
        return False
    return True


def process_text(text: str) -> tuple[str, int, int]:
    """Returns (new_text, fully_empty_removed, partially_collapsed)."""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    fully_empty = 0
    partial = 0

    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()
        if stripped.startswith(";@if "):
            depth = 1
            arms: list[tuple[str, list[str]]] = [(raw, [])]
            j = i + 1
            while j < len(lines):
                s = lines[j]
                ss = s.strip()
                if ss.startswith(";@if "):
                    depth += 1
                    arms[-1][1].append(s)
                elif ss == ";@endif":
                    depth -= 1
                    if depth == 0:
                        break
                    arms[-1][1].append(s)
                elif depth == 1 and (
                    ss.startswith(";@elif ") or ss == ";@else"
                ):
                    arms.append((s, []))
                else:
                    arms[-1][1].append(s)
                j += 1

            if depth != 0:
                out.append(raw)
                i += 1
                continue

            endif_line = lines[j]
            arm_status = [
                (header, body, any(is_meaningful(b) for b in body))
                for header, body in arms
            ]
            non_empty = [a for a in arm_status if a[2]]

            if not non_empty:
                fully_empty += 1
                i = j + 1
                continue

            if len(non_empty) == len(arm_status):
                out.extend(lines[i : j + 1])
                i = j + 1
                continue

            # Check for `;@else` as first survivor — would change
            # semantics. Bail out of partial-collapse for this block.
            first_header = non_empty[0][0].strip()
            if first_header == ";@else":
                out.extend(lines[i : j + 1])
                i = j + 1
                continue

            partial += 1
            for k, (header, body, _) in enumerate(non_empty):
                ss = header.strip()
                if k == 0:
                    if ss.startswith(";@elif "):
                        new_header = header.replace(";@elif", ";@if", 1)
                    else:
                        new_header = header
                    out.append(new_header)
                else:
                    out.append(header)
                out.extend(body)
            out.append(endif_line)
            i = j + 1
            continue

        out.append(raw)
        i += 1

    return "".join(out), fully_empty, partial


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args()

    if args.paths:
        targets = []
        for p in args.paths:
            if p.is_file():
                targets.append(p)
            elif p.is_dir():
                targets.extend(p.rglob("*.inc"))
                targets.extend(p.rglob("*.asm.in"))
    else:
        unified = SRC_ROOT / "src" / "levels" / "_unified"
        targets = sorted(unified.rglob("*.inc")) + sorted(
            unified.rglob("*.asm.in")
        )

    total_fully = 0
    total_partial = 0
    files_changed = 0

    for path in targets:
        try:
            text = path.read_text()
        except OSError:
            continue
        new_text, fully, partial = process_text(text)
        if new_text != text:
            files_changed += 1
            total_fully += fully
            total_partial += partial
            print(
                f"{path.relative_to(SRC_ROOT)}: "
                f"fully={fully} partial={partial}"
            )
            if not args.dry_run:
                path.write_text(new_text)

    print(
        f"\nfiles changed: {files_changed}, "
        f"fully-empty blocks removed: {total_fully}, "
        f"partial collapses: {total_partial}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

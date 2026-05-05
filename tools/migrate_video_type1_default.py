#!/usr/bin/env python3
"""One-shot migration: drop the now-default `type=1, ` prefix from
every `video` instruction in the source-reconstruction tree.

Background: AWVM_Tools commit (2026-05-05) makes `type=1` the default
for the `video` instruction (since type=1 is the dominant case at
~84% of all video instructions). Source files no longer need to spell
it out.

Idempotent: running twice is a no-op.

Scope: walks `<src-tree>` for `.asm`, `.inc`, `.asm.in` files and
edits `video type=1, offset=...` → `video offset=...`. Does NOT touch
`video type=0, ...` (VIDEO2 must stay explicit).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

VIDEO_TYPE1 = re.compile(r"\bvideo type=1, ")


def migrate(src_tree: Path) -> tuple[int, int]:
    files_changed = 0
    lines_changed = 0
    for ext in ("*.asm", "*.inc", "*.asm.in"):
        for path in src_tree.rglob(ext):
            text = path.read_text(encoding="utf-8")
            new_text, n = VIDEO_TYPE1.subn("video ", text)
            if n:
                path.write_text(new_text, encoding="utf-8")
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

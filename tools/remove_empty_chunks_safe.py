#!/usr/bin/env python3
"""Phase 5: remove empty per-arm chunk files (CAVES + ENDING).

A chunk file is "empty" if its content (after strip) is the empty
string. Removal:
  1. Delete the chunk file.
  2. In the matching `_unified/<STAGE>.asm.in`, delete the
     `;@include "<stage>/<chunkname>.inc"` line.

Critically, we LEAVE the surrounding `;@if`/`;@elif`/`;@endif`
structure intact. An empty active branch contributes zero bytes,
which is the same effect as including an empty file.

This is a simpler alternative to the previous
`tools/remove_empty_chunks.py` which tried to also collapse the
`;@if` structure when a branch became empty — that logic was
buggy and broke verification for CAVES + ENDING.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)


def remove_for_stage(stage: str) -> tuple[int, int]:
    """Returns (chunks_deleted, includes_dropped)."""
    stage_dir = SRC_ROOT / f"src/levels/_unified/{stage.lower()}"
    asm_in = SRC_ROOT / f"src/levels/_unified/{stage}.asm.in"
    if not stage_dir.is_dir() or not asm_in.is_file():
        return 0, 0

    empty_chunks: set[str] = set()
    for chunk in stage_dir.glob("*.inc"):
        if chunk.read_text().strip() == "":
            empty_chunks.add(chunk.name)

    if not empty_chunks:
        return 0, 0

    text = asm_in.read_text()
    lines = text.splitlines()
    out_lines: list[str] = []
    n_dropped = 0
    inc_re = re.compile(
        rf'^\s*;@include\s+"{re.escape(stage.lower())}/([^"]+)"\s*(?:;.*)?$'
    )
    for ln in lines:
        m = inc_re.match(ln)
        if m and m.group(1) in empty_chunks:
            n_dropped += 1
            continue
        out_lines.append(ln)
    new_text = "\n".join(out_lines) + ("\n" if text.endswith("\n") else "")
    asm_in.write_text(new_text)

    # Delete the empty chunks
    for name in empty_chunks:
        (stage_dir / name).unlink()

    return len(empty_chunks), n_dropped


def main() -> int:
    stages = sys.argv[1:] if len(sys.argv) > 1 else ["CAVES", "ENDING"]
    total_chunks = 0
    total_drops = 0
    for stage in stages:
        n_chunks, n_drops = remove_for_stage(stage)
        print(f"  {stage}: removed {n_chunks} empty chunks, dropped "
              f"{n_drops} include lines")
        total_chunks += n_chunks
        total_drops += n_drops
    print(f"\nTotal: {total_chunks} chunks, {total_drops} includes dropped")
    return 0


if __name__ == "__main__":
    sys.exit(main())

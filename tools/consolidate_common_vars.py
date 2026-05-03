#!/usr/bin/env python3
"""Phase 1b: replace inline var-alias EQUs in per-branch and unified
source files with a single `;@include "<path>/_common_vars.inc"`.

Per-file edits:
  1. Find the lines defining any of the SHARED EQUs (the 15 listed below).
  2. Drop those lines.
  3. Insert `;@include "<rel-path>/_common_vars.inc"` just before the
     first remaining EQU line (or, if none, at the top below any
     leading comments).

Verification: caller is expected to run verify_stage and verify_unified
after this script. The script itself only does textual edits and prints
a per-file summary.

Usage:
  python3 tools/consolidate_common_vars.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SRC_ROOT = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
LEVELS = SRC_ROOT / "src/levels"
COMMON_VARS = LEVELS / "_common_vars.inc"

# The 15 var-alias EQUs known to be byte-identical across every
# branch/stage that defines them. Values come from _common_vars.inc.
SHARED_EQUS = {
    "RANDOM_SEED": 0x3C,
    "HACK_VAR_54": 0x54,
    "HACK_VAR_67": 0x67,
    "LAST_KEYCHAR": 0xDA,
    "HACK_VAR_DC": 0xDC,
    "HERO_POS_UP_DOWN": 0xE5,
    "MUS_MARK": 0xF4,
    "HACK_VAR_F7": 0xF7,
    "SCROLL_Y": 0xF9,
    "HERO_ACTION": 0xFA,
    "HERO_POS_JUMP_DOWN": 0xFB,
    "HERO_POS_LEFT_RIGHT": 0xFC,
    "HERO_POS_MASK": 0xFD,
    "HERO_ACTION_POS_MASK": 0xFE,
    "PAUSE_SLICES": 0xFF,
}

RE_EQU = re.compile(
    r"^\s*([A-Z_][A-Z_0-9]*)\s+EQU\s+(.*?)(?:\s*;.*)?\s*$"
)


def parse_int_lit(s: str) -> int | None:
    s = s.strip()
    try:
        return int(s, 0)
    except ValueError:
        return None


def consolidate_file(path: Path, include_path: str) -> tuple[int, str]:
    """Edit `path` in place. Returns (n_dropped, status)."""
    text = path.read_text()
    lines = text.splitlines(keepends=False)

    # Bail if include directive already present.
    for ln in lines:
        if "_common_vars.inc" in ln and ln.lstrip().startswith(";@include"):
            return 0, "already-included"

    drop_indexes = []
    first_equ_index = None
    for i, ln in enumerate(lines):
        m = RE_EQU.match(ln)
        if not m:
            continue
        name, val = m.group(1), m.group(2)
        if first_equ_index is None:
            first_equ_index = i
        if name in SHARED_EQUS:
            v = parse_int_lit(val)
            if v == SHARED_EQUS[name]:
                drop_indexes.append(i)
            # If value diverges, keep the line — it's a per-file override.

    if not drop_indexes:
        return 0, "no-shared-equs"

    # Build the new lines: remove dropped, insert one include directive
    # at the position of the FIRST dropped line.
    insert_at = drop_indexes[0]
    drop_set = set(drop_indexes)
    new_lines = []
    inserted = False
    for i, ln in enumerate(lines):
        if i in drop_set:
            if not inserted:
                new_lines.append(f';@include "{include_path}"')
                inserted = True
            continue
        new_lines.append(ln)

    out = "\n".join(new_lines)
    if text.endswith("\n"):
        out += "\n"
    path.write_text(out)
    return len(drop_indexes), "ok"


def add_include_to_asm_in(asm_in: Path, include_path: str) -> bool:
    """Ensure `;@include "<rel>/_common_vars.inc"` is present near the
    top of `asm_in`. Returns True if a line was added."""
    text = asm_in.read_text()
    lines = text.splitlines(keepends=False)
    for ln in lines:
        if "_common_vars.inc" in ln and ln.lstrip().startswith(";@include"):
            return False
    # Insert after the leading non-directive comment block. STOP as soon
    # as we see a `;@directive` or actual code — those mean we're past
    # the file-header banner and into content that needs the EQUs in
    # scope.
    insert_at = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if s == "":
            insert_at = i + 1
            continue
        if s.startswith(";@"):
            break
        if s.startswith(";"):
            insert_at = i + 1
            continue
        break
    new_lines = lines[:insert_at] + [
        f';@include "{include_path}"', ""
    ] + lines[insert_at:]
    out = "\n".join(new_lines)
    if text.endswith("\n"):
        out += "\n"
    asm_in.write_text(out)
    return True


def main() -> int:
    targets: list[tuple[Path, str]] = []

    # Per-branch sources: src/levels/<branch>/<STAGE>.asm
    for asm in sorted(LEVELS.glob("*/*.asm")):
        if asm.parent.name == "_unified":
            continue
        rel = "../_common_vars.inc"
        targets.append((asm, rel))

    # Unified .asm.in: src/levels/_unified/<STAGE>.asm.in
    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        rel = "../_common_vars.inc"
        targets.append((asm_in, rel))

    # Unified chunks: src/levels/_unified/<stage>/*.inc
    chunk_files: list[tuple[Path, str]] = []
    for chunk in sorted(LEVELS.glob("_unified/*/*.inc")):
        rel_chunk = "../../_common_vars.inc"
        chunk_files.append((chunk, rel_chunk))

    total_dropped = 0
    n_consolidated_files = 0
    for path, rel in targets:
        n, status = consolidate_file(path, rel)
        total_dropped += n
        if n > 0:
            n_consolidated_files += 1
        relp = str(path.relative_to(SRC_ROOT))
        if n > 0 or "skip" in status:
            print(f"  {relp:<55s} dropped={n:<3d} {status}")

    # For chunks we DON'T add an include — the .asm.in's include
    # already defines the EQUs at preprocess time, before chunks are
    # textually inlined. We just strip the now-redundant inline EQUs.
    chunk_dropped = 0
    chunks_touched = 0
    for path, rel in chunk_files:
        n, status = consolidate_file(path, rel)
        chunk_dropped += n
        if n > 0:
            chunks_touched += 1
            # The strip already removed lines, but consolidate_file
            # ALSO inserted an include. Remove that include — the
            # .asm.in handles it instead.
            text = path.read_text()
            text = text.replace(f';@include "{rel}"\n', "")
            path.write_text(text)

    # Ensure every .asm.in that owns chunks has the include even if
    # the .asm.in itself defined no shared EQUs.
    asm_ins_added = 0
    for asm_in in sorted(LEVELS.glob("_unified/*.asm.in")):
        if add_include_to_asm_in(asm_in, "../_common_vars.inc"):
            asm_ins_added += 1
            print(f"  added include to {asm_in.relative_to(SRC_ROOT)}")

    print(f"\nPer-branch+asm.in EQU lines dropped: {total_dropped} "
          f"across {n_consolidated_files} files")
    print(f"Chunk EQU lines dropped: {chunk_dropped} across "
          f"{chunks_touched} chunks")
    print(f".asm.in files that got include added: {asm_ins_added}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

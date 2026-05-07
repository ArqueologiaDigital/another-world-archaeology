#!/usr/bin/env python3
"""Reachability-filtered polygon-reference scanner for #0054.

Companion to `find_unused_polygons.py` (the byte-walking pipeline)
and a third member of the v2-asset-scanner family alongside
`unused_sound_scan_v2.py` and `unused_palette_scan_v2.py`.

The existing `find_unused_polygons.py` already walks polygon
resources to enumerate offsets and scans the disasm for `video
type=N, offset=...` references. This v2 tool is narrower in scope
and answers a question the existing pipeline didn't:

    "Of the polygon offsets that ARE referenced by `video`
     opcodes, which ones are only referenced from DEAD code?"

These are polygons that the v1 byte-level scan would classify as
"used" because the `video` opcode physically appears in the
bytecode, but that the runtime never actually draws because the
referencing label is gated, transitively-dead, or sits after an
unconditional terminator inside a live label.

This is exactly the bug pattern that drove research/11's music
0x89 finding — the reference is there, but it never executes.

Output: per-stage list of CINEMATIC_NNNN labels referenced by
`video` opcodes ONLY from dead code, plus the count of dead-only
references vs total `video` references. The reachability oracle
makes this a one-pass static query.

Usage:
    python3 tools/unused_polygon_scan_v2.py [--branch dos_1992]
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

SRC_TREE = AW_SRC
LEVELS = SRC_TREE / "src" / "levels"

sys.path.insert(0, str(REPO_ROOT / "tools"))
from build_reachability_graph import (  # noqa: E402
    parse_stage,
    ReachabilityOracle,
)

# Capture the offset operand of a `video type=N, offset=NAME, ...`.
# `NAME` can be a CINEMATIC_NNN EQU, a literal hex, or a variable.
RE_VIDEO_OFFSET = re.compile(
    r"\bvideo\s+type=\S+\s*,\s*offset=(?P<off>[A-Z_][A-Z0-9_]*|0x[0-9A-Fa-f]+|\d+)"
)
RE_INTRA_TERM = re.compile(
    r"^\s*(ret|killChannel|bankSwitch|freezeChannel|jmp\b)"
)


def collect_in_stage(
    stage_data: dict, oracle: ReachabilityOracle, stage_name: str
) -> dict:
    """Per-stage: live `video offset=X` and dead `video offset=X` sets."""
    live: set[str] = set()
    dead: set[str] = set()
    for label, body in stage_data["labels"].items():
        is_live = oracle.is_live(stage_name, label)
        for _line, instr in body["instrs"]:
            m = RE_VIDEO_OFFSET.search(instr)
            if m:
                off = m.group("off")
                (live if is_live else dead).add(off)
            if RE_INTRA_TERM.match(instr):
                is_live = False
    return {"live": live, "dead": dead}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument(
        "--branch",
        default="dos_1992",
        help="source-reconstruction branch (default: dos_1992)",
    )
    args = p.parse_args()

    oracle = ReachabilityOracle(branch=args.branch)
    branch_dir = LEVELS / args.branch
    if not branch_dir.is_dir():
        print(f"branch dir not found: {branch_dir}", file=sys.stderr)
        return 1

    print(f"Branch: {args.branch}")
    print()
    print("Per-stage `video offset=…` reachability:")
    print(
        "  stage         #live   #dead-only   dead-only offsets (truncated)"
    )

    grand_live = 0
    grand_dead_only = 0
    all_dead_only: dict[str, set[str]] = defaultdict(set)
    for asm in sorted(branch_dir.glob("*.asm")):
        stage_data = parse_stage(asm)
        stage = asm.stem
        refs = collect_in_stage(stage_data, oracle, stage)
        live = refs["live"]
        dead_only = refs["dead"] - live
        grand_live += len(live)
        grand_dead_only += len(dead_only)
        all_dead_only[stage] = dead_only
        # Truncate the dead-only listing to avoid wall-of-text.
        dead_preview = sorted(dead_only)[:6]
        suffix = "..." if len(dead_only) > 6 else ""
        print(
            f"  {stage:<12s}  {len(live):>4d}    {len(dead_only):>4d}"
            f"        {','.join(dead_preview)}{suffix}"
        )

    print()
    print(f"Total live `video offset=` references:        {grand_live}")
    print(f"Total dead-only `video offset=` references:   {grand_dead_only}")
    print(
        "  (these are polygon offsets the v1 byte scan would count as "
        "'used' because the video opcode appears physically in the "
        "bytecode, but no live execution path reaches them)"
    )

    # Surface stages with notable dead-only sets, sorted desc.
    print()
    print("Stages with most dead-only video references:")
    sortable = sorted(
        all_dead_only.items(), key=lambda kv: len(kv[1]), reverse=True
    )
    for stage, dead in sortable[:5]:
        if not dead:
            continue
        print(f"  {stage}: {len(dead)} dead-only")
        for off in sorted(dead)[:10]:
            print(f"    {off}")
        if len(dead) > 10:
            print(f"    ... +{len(dead)-10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())

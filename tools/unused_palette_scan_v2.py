#!/usr/bin/env python3
"""Unused-PALETTE scanner with reachability filtering (post-#0058).

Successor to `unused_palette_scan.py`. Like the sound-scan v2, this
version uses the `ReachabilityOracle` from #0058 to filter
`setPalette N` references inside dead code (gates, transitively-
dead labels, post-jmp tails inside live labels).

Operates against the source-reconstruction tree's per-port `.asm`
files (semantic label names). Output: per-stage palette-slot
usage with reachability filtering applied.

Usage:
    python3 tools/unused_palette_scan_v2.py [--branch dos_1992]
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

RE_SETPAL_LIT = re.compile(r"\bsetPalette\s+(0x[0-9A-Fa-f]+|\d+)\b")
RE_SETPAL_ANY = re.compile(r"\bsetPalette\b")
# Within-label terminators (matches the sound-scan v2). `break` is
# NOT a terminator — it yields and resumes next tick.
RE_INTRA_TERM = re.compile(
    r"^\s*(ret|killChannel|bankSwitch|freezeChannel|jmp\b)"
)


def parse_id(s: str) -> int:
    return int(s, 0) if s.startswith("0x") else int(s)


def collect_setpalette_in_stage(
    stage_data: dict, oracle: ReachabilityOracle, stage_name: str
) -> dict:
    """Per-stage scan: live and dead `setPalette N` literal indices,
    plus a count of `setPalette` calls with non-literal operands."""
    pal_live: set[int] = set()
    pal_dead: set[int] = set()
    nonlit_live = 0
    nonlit_dead = 0
    for label, body in stage_data["labels"].items():
        is_live = oracle.is_live(stage_name, label)
        for _line, instr in body["instrs"]:
            m = RE_SETPAL_LIT.search(instr)
            if m:
                idx = parse_id(m.group(1))
                (pal_live if is_live else pal_dead).add(idx)
            elif RE_SETPAL_ANY.search(instr):
                # setPalette with non-literal operand
                if is_live:
                    nonlit_live += 1
                else:
                    nonlit_dead += 1
            if RE_INTRA_TERM.match(instr):
                is_live = False
    return {
        "live": pal_live,
        "dead": pal_dead,
        "nonlit_live": nonlit_live,
        "nonlit_dead": nonlit_dead,
    }


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
    print("Per-stage setPalette literal-index usage:")
    print(
        "  stage         #live   #dead-only   unused-slots (0..31)"
    )

    total_unused = 0
    total_dead_only = 0
    by_stage_summary: list[tuple[str, int, int, list[int]]] = []
    for asm in sorted(branch_dir.glob("*.asm")):
        stage_data = parse_stage(asm)
        stage = asm.stem
        refs = collect_setpalette_in_stage(stage_data, oracle, stage)
        live = refs["live"]
        # "Dead-only" — referenced ONLY from dead code (would have
        # been counted as used by the v1 scanner).
        dead_only = refs["dead"] - live
        unused = sorted(set(range(32)) - live)
        total_unused += len(unused)
        total_dead_only += len(dead_only)
        by_stage_summary.append((stage, len(live), len(dead_only), unused))
        unused_str = ",".join(str(u) for u in unused) if unused else "-"
        dead_only_str = (
            f" dead-only=[{','.join(str(u) for u in sorted(dead_only))}]"
            if dead_only
            else ""
        )
        print(
            f"  {stage:<12s}  {len(live):>3d}    {len(dead_only):>3d}"
            f"        [{unused_str}]{dead_only_str}"
        )

    print()
    print(f"Total slots never live-selected (sum across stages): {total_unused}")
    print(f"Total slots only-selected-from-dead-code:           {total_dead_only}")
    print(
        "  (these would have been classified 'used' by the v1 naive "
        "scanner but actually only run if we were in dead code)"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())

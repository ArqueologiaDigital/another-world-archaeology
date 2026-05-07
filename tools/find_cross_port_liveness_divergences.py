#!/usr/bin/env python3
"""Surface every CINEMATIC offset whose liveness diverges across ports.

For each (stage, CINEMATIC name) pair that's referenced in at
least one of the 3 fully-disassembled ports
(`cartridge_1992`, `dos_1992`, `chahi_amiga_1991`), classify
the liveness in each port (live / dead-only / unref) and report
only the cases where the three classifications are NOT
identical.

These divergences fall into clear archaeological patterns:

  - DOS-only dead = port-specific DOS regression
    (dropped the live drawing site)
  - cart+dos dead, amiga unref = post-1991 addition that was
    later disabled
  - cart-only live = cart-specific feature
  - dos-only live = dos-specific feature (rare)
  - all three different = mixed evolution

Usage:
  python3 tools/find_cross_port_liveness_divergences.py
"""
from __future__ import annotations

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

RE_VIDEO = re.compile(
    r"\bvideo\s+type=\S+\s*,\s*offset=([A-Z_][A-Z0-9_]*|0x[0-9A-Fa-f]+|\d+)"
)
RE_INTRA_TERM = re.compile(
    r"^\s*(ret|killChannel|bankSwitch|freezeChannel|jmp\b)"
)

BRANCHES = ["cartridge_1992", "dos_1992", "chahi_amiga_1991"]
STAGES = [
    "INTRO",
    "LAKE",
    "PRISON",
    "CAVES",
    "TANK",
    "CAPSULE",
    "ENDING",
    "PASSCODE",
    "CODE_WHEEL",
]


def collect_per_branch(branch: str, stage: str) -> dict[str, str]:
    """Return {cinematic_name: 'live'|'dead-only'} for one (branch, stage)."""
    asm = LEVELS / branch / f"{stage}.asm"
    if not asm.is_file():
        return {}
    oracle = ReachabilityOracle(branch=branch)
    stage_data = parse_stage(asm)
    out: dict[str, str] = {}
    for label, body in stage_data["labels"].items():
        is_live = oracle.is_live(stage, label)
        for _line, instr in body["instrs"]:
            m = RE_VIDEO.search(instr)
            if m:
                name = m.group(1)
                # Promote: live wins over dead-only.
                if name in out:
                    if is_live:
                        out[name] = "live"
                else:
                    out[name] = "live" if is_live else "dead-only"
            if RE_INTRA_TERM.match(instr):
                is_live = False
    return out


def main() -> int:
    # Gather per-branch per-stage liveness.
    data: dict[tuple[str, str], dict[str, str]] = {}
    for stage in STAGES:
        for branch in BRANCHES:
            data[(stage, branch)] = collect_per_branch(branch, stage)

    # For each (stage, name), compute per-branch state in {live, dead-only, unref}.
    # Focus on cases where SAME NAME exists in 2+ ports with DIFFERENT
    # liveness (live vs dead-only) — those are real behavioural diffs,
    # not just polygon-bank renumbering artefacts.
    print(
        f"{'stage':<10} {'cinematic':<40} "
        f"{'cart':<10} {'dos':<10} {'amiga':<10} {'pattern':<20}"
    )
    print("-" * 100)
    pattern_counts: dict[str, int] = defaultdict(int)
    n_diverge = 0
    n_total = 0
    n_behavioral = 0
    for stage in STAGES:
        names = set()
        for branch in BRANCHES:
            names.update(data[(stage, branch)].keys())
        for name in sorted(names):
            states = []
            for branch in BRANCHES:
                m = data[(stage, branch)].get(name)
                states.append(m if m else "unref")
            n_total += 1
            if len(set(states)) <= 1:
                continue
            n_diverge += 1
            # Behavioural divergence: at least one port has live AND
            # at least one has dead-only for the same name.
            has_live = "live" in states
            has_dead = "dead-only" in states
            if not (has_live and has_dead):
                continue
            n_behavioral += 1
            # Classify the pattern.
            cart, dos, amiga = states
            if cart == "dead-only" and dos == "live" and amiga == "dead-only":
                pat = "dos-only-live"
            elif cart == "live" and dos == "dead-only" and amiga == "live":
                pat = "dos-only-dead"  # DOS regression
            elif cart == "live" and dos == "dead-only" and amiga == "dead-only":
                pat = "cart-only-live"
            elif cart == "dead-only" and dos == "live" and amiga == "live":
                pat = "cart-only-dead"
            elif cart == "live" and dos == "live" and amiga == "dead-only":
                pat = "amiga-only-dead"
            elif cart == "dead-only" and dos == "dead-only" and amiga == "live":
                pat = "amiga-only-live"
            else:
                pat = "mixed"
            pattern_counts[pat] += 1
            print(
                f"{stage:<10} {name:<40} "
                f"{states[0]:<10} {states[1]:<10} {states[2]:<10} "
                f"{pat:<20}"
            )

    print()
    print(
        f"Total cinematic names referenced: {n_total}; "
        f"any-divergence: {n_diverge}; "
        f"behavioural (live↔dead) divergences: {n_behavioral}"
    )
    print()
    print("Behavioural divergence pattern counts:")
    for pat, count in sorted(pattern_counts.items(), key=lambda kv: -kv[1]):
        print(f"  {pat:<20} {count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

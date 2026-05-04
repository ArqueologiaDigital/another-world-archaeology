#!/usr/bin/env python3
"""Cross-port liveness audit for previously-claimed cut content.

Lesson learned from research/19's TANK CIN_146..149 reading:
"dead-only on dos_1992" doesn't mean "cut content". The same
polygons may be LIVE on cart or amiga — meaning the dos port
just dropped the live drawing site, not the asset.

This tool takes a list of (stage, cinematic_offset_name) claims
and reports liveness across the three fully-disassembled ports
(`cartridge_1992`, `dos_1992`, `chahi_amiga_1991`). For each
claim it prints the per-port classification: LIVE, dead-only,
or unreferenced (the offset name doesn't appear).

Usage:
  python3 tools/cross_port_liveness_audit.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path("/home/fsanches/compartilhado/another-world-archaeology")
SRC_TREE = Path(
    "/home/fsanches/compartilhado/another-world-source-reconstruction"
)
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

# Claims to audit. Each item: (stage, list of CINEMATIC_<NAME>).
# These are the major cut-content claims from research/19.
CLAIMS = [
    (
        "LAKE",
        [
            # research/05 BEETLE — known good, includes for sanity check
            "CINEMATIC_BEETLE_LIFT_FRAME_0",  # already renamed
            "CINEMATIC_BEETLE_LIFT_0",
            # research/19 non-beetle
            "CINEMATIC_HERO_LAND_LEFT",
            "CINEMATIC_HERO_LAND_RIGHT",
            "CINEMATIC_LANDING_AFTER_SWING_12",
            "CINEMATIC_PARTICLE_BURST_2_FRAME_0",
            "CINEMATIC_PARTICLE_BURST_2_0",
            "CINEMATIC_REED_PLANT_5",
        ],
    ),
    (
        "PASSCODE",
        ["CINEMATIC_000", "CINEMATIC_001", "CINEMATIC_007", "CINEMATIC_015"],
    ),
    (
        "CAVES",
        ["CINEMATIC_880", "CINEMATIC_885", "CINEMATIC_890"],
    ),
    (
        "CAPSULE",
        [
            "CINEMATIC_378",
            "CINEMATIC_387",
            "CINEMATIC_614",
            "CINEMATIC_650",
            "CINEMATIC_676",
            "CINEMATIC_700",
            "CINEMATIC_705",
            "CINEMATIC_720",
        ],
    ),
    (
        "PRISON",
        ["CINEMATIC_127", "CINEMATIC_688", "CINEMATIC_692", "CINEMATIC_705"],
    ),
    (
        "TANK",
        [
            "CINEMATIC_146",
            "CINEMATIC_147",
            "CINEMATIC_148",
            "CINEMATIC_149",
            "CINEMATIC_199",
            "CINEMATIC_276",
            "CINEMATIC_278",
        ],
    ),
]

BRANCHES = ["cartridge_1992", "dos_1992", "chahi_amiga_1991"]


_oracle_cache: dict[str, ReachabilityOracle] = {}
_stage_cache: dict[tuple[str, str], dict] = {}


def get_oracle(branch: str) -> ReachabilityOracle:
    if branch not in _oracle_cache:
        _oracle_cache[branch] = ReachabilityOracle(branch=branch)
    return _oracle_cache[branch]


def get_stage(branch: str, stage: str) -> dict | None:
    key = (branch, stage)
    if key in _stage_cache:
        return _stage_cache[key]
    asm = LEVELS / branch / f"{stage}.asm"
    if not asm.is_file():
        _stage_cache[key] = None
        return None
    _stage_cache[key] = parse_stage(asm)
    return _stage_cache[key]


def liveness(branch: str, stage: str, target: str) -> str:
    """Return 'live', 'dead-only', or 'unref' for a given CINEMATIC
    name in (branch, stage). Uses cached oracle and stage parses."""
    stage_data = get_stage(branch, stage)
    if stage_data is None:
        return "no-stage"
    oracle = get_oracle(branch)
    found_live = False
    found_dead = False
    for label, body in stage_data["labels"].items():
        is_live = oracle.is_live(stage, label)
        for _line, instr in body["instrs"]:
            m = RE_VIDEO.search(instr)
            if m and m.group(1) == target:
                if is_live:
                    found_live = True
                else:
                    found_dead = True
            if RE_INTRA_TERM.match(instr):
                is_live = False
    if found_live:
        return "live"
    if found_dead:
        return "dead-only"
    return "unref"


def main() -> int:
    print(
        f"{'stage':<10} {'cinematic':<40} "
        f"{'cart':<10} {'dos':<10} {'amiga':<10}"
    )
    print("-" * 80)
    for stage, names in CLAIMS:
        for name in names:
            row = [liveness(b, stage, name) for b in BRANCHES]
            print(
                f"{stage:<10} {name:<40} "
                f"{row[0]:<10} {row[1]:<10} {row[2]:<10}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())

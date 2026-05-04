#!/usr/bin/env python3
"""Cross-port USED-polygon diff for a single stage.

Refines `cross_port_polygon_diff.py` by intersecting each port's
solid-polygon set with the set of polygons actually USED by that
port's bytecode (directly via `video offset=` or transitively via
group-polygon child references).

Surfaces two high-value sets:
  - "amiga-USES-but-dos-LACKS": sprites that the amiga 1991 build
    actually rendered, which DON'T exist in the dos 1992 polygon
    bank at all → strong cut-content evidence.
  - "dos-USES-but-amiga-LACKS": sprites that the dos 1992 build
    renders which the amiga 1991 bank doesn't have → DOS additions.

Usage:
    python3 tools/cross_port_used_polygon_diff.py LAKE
"""
from __future__ import annotations

import argparse
import hashlib
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_walker
import asset_references


REPO = Path(__file__).resolve().parent.parent

# Stage → (DOS resource index, Amiga resource index, level number for asset_references)
# All stages currently use the same indices (memlist convention) on both ports.
STAGES = {
    "CODE_WHEEL": {"poly": 0x16, "level": 0},
    "INTRO":      {"poly": 0x19, "level": 1},
    "LAKE":       {"poly": 0x1c, "level": 2},
    "PRISON":     {"poly": 0x1f, "level": 3},
    "CAVES":      {"poly": 0x22, "level": 4},
    "TANK":       {"poly": 0x25, "level": 5},
    "CAPSULE":    {"poly": 0x28, "level": 6},
    "ENDING":     {"poly": 0x2b, "level": 7},
    "PASSCODE":   {"poly": 0x7f, "level": 8},
}


def hash_solid_polygons(data: bytes) -> dict[int, str]:
    """offset → md5 of polygon bytes, for solid polygons only."""
    polygons, _ = polygon_walker.walk_linear(data)
    out: dict[int, str] = {}
    for p in polygons:
        if p.kind != "solid":
            continue
        out[p.offset] = hashlib.md5(data[p.offset:p.offset + p.size]).hexdigest()
    return out


def compute_reachable_solids(data: bytes, seed_offsets: list[int]) -> dict[int, str]:
    """Hash only the solid polygons reachable from `seed_offsets`
    via direct bytecode references + transitive group-child closure."""
    reachable = polygon_walker.reachable_set(data, seed_offsets)
    polygons, _ = polygon_walker.walk_linear(data)
    out: dict[int, str] = {}
    for p in polygons:
        if p.offset not in reachable:
            continue
        if p.kind != "solid":
            continue
        out[p.offset] = hashlib.md5(data[p.offset:p.offset + p.size]).hexdigest()
    return out


def diff_stage(stage: str) -> None:
    spec = STAGES[stage]
    poly_idx = spec["poly"]
    level = spec["level"]

    amiga_poly = REPO / "tmp/output/amiga/resources" / f"resource-0x{poly_idx:02x}.bin"
    dos_poly = REPO / "tmp/output/msdos/resources" / f"resource-0x{poly_idx:02x}.bin"
    amiga_disasm_dir = REPO / f"tmp/output/amiga/disasm/level_{level}"
    dos_disasm_dir = REPO / f"tmp/output/msdos/disasm/level_{level}"

    if not amiga_poly.is_file() or not dos_poly.is_file():
        print(f"{stage}: skip — missing poly resource file(s)")
        return

    # Find the disasm file
    amiga_asm = next(amiga_disasm_dir.glob("*.asm"), None)
    dos_asm = next(dos_disasm_dir.glob("*.asm"), None)
    if amiga_asm is None or dos_asm is None:
        print(f"{stage}: skip — missing disasm file(s)")
        return

    # Bytecode video=1 references
    refs_amiga = asset_references.scan_one_disasm(amiga_asm)
    refs_dos = asset_references.scan_one_disasm(dos_asm)

    seeds_amiga = sorted(set(r["offset"] for r in refs_amiga["video"][1]))
    seeds_dos = sorted(set(r["offset"] for r in refs_dos["video"][1]))

    data_amiga = amiga_poly.read_bytes()
    data_dos = dos_poly.read_bytes()

    used_amiga = compute_reachable_solids(data_amiga, seeds_amiga)
    used_dos = compute_reachable_solids(data_dos, seeds_dos)

    all_amiga = hash_solid_polygons(data_amiga)
    all_dos = hash_solid_polygons(data_dos)

    set_used_amiga = set(used_amiga.values())
    set_used_dos = set(used_dos.values())
    set_all_amiga = set(all_amiga.values())
    set_all_dos = set(all_dos.values())

    # The interesting sets:
    amiga_uses_but_dos_lacks = set_used_amiga - set_all_dos
    dos_uses_but_amiga_lacks = set_used_dos - set_all_amiga

    print(f"\n=== {stage} ===")
    print(f"  amiga: {len(used_amiga)} used solids / {len(all_amiga)} total solids "
          f"({len(set_used_amiga)} unique-used / {len(set_all_amiga)} unique-total)")
    print(f"  dos:   {len(used_dos)} used solids / {len(all_dos)} total solids "
          f"({len(set_used_dos)} unique-used / {len(set_all_dos)} unique-total)")
    print(f"  amiga-USES-but-dos-LACKS:  {len(amiga_uses_but_dos_lacks):>4d}  "
          "(strong cut-content candidates)")
    print(f"  dos-USES-but-amiga-LACKS:  {len(dos_uses_but_amiga_lacks):>4d}  "
          "(DOS additions not in 1991 bank)")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("stages", nargs="*", help="stages to diff (default: all)")
    args = p.parse_args()

    stages = [s.upper() for s in args.stages] if args.stages else list(STAGES.keys())
    for stage in stages:
        if stage not in STAGES:
            print(f"unknown stage: {stage}")
            continue
        diff_stage(stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())

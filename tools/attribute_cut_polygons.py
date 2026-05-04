#!/usr/bin/env python3
"""For each stage's cut/added polygons, attribute the parent group
polygons to named EQUs in the corresponding per-branch source file.

Output: a structured report — for each stage, list:
  - per-animation cycle: how many frames of that cycle are in the
    cut/added set (i.e., have at least one cut/added sub-polygon)
  - unattributed parent offsets (no matching EQU)

Run on both directions:
  - cut_polygons_amiga_only.json (amiga 1991 → dos 1992 cuts)
  - dos_added_polygons.json     (dos 1992 → amiga 1991 additions)

Usage:
    python3 tools/attribute_cut_polygons.py
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_walker
from find_parent_polygons import find_group_parents


REPO = Path(__file__).resolve().parent.parent
SRC_RECONSTRUCTION = REPO.parent / "another-world-source-reconstruction"

# Stage → (poly resource index, archaeology output-port-dir, source branch)
STAGES = {
    "CODE_WHEEL": (0x16,),
    "INTRO":      (0x19,),
    "LAKE":       (0x1c,),
    "PRISON":     (0x1f,),
    "CAVES":      (0x22,),
    "TANK":       (0x25,),
    "CAPSULE":    (0x28,),
    "ENDING":     (0x2b,),
    "PASSCODE":   (0x7f,),
}

PORT_TO_OUTPUT = {"amiga": "amiga", "dos": "msdos"}
PORT_TO_BRANCH = {"amiga": "chahi_amiga_1991", "dos": "dos_1992"}


def build_offset_to_name(asm_path: Path) -> dict[int, str]:
    """Parse a per-branch .asm file's EQU table."""
    if not asm_path.is_file():
        return {}
    text = asm_path.read_text()
    out: dict[int, str] = {}
    for m in re.finditer(r"^([A-Z_][A-Z_0-9]*)\s+EQU\s+(0x[0-9A-Fa-f]+)$", text, re.M):
        out[int(m.group(2), 16)] = m.group(1)
    return out


def attribute_stage(stage: str, port: str, child_offsets: list[int]) -> dict:
    """Return attribution dict for one stage + port."""
    poly_idx = STAGES[stage][0]
    output_dir = PORT_TO_OUTPUT[port]
    branch = PORT_TO_BRANCH[port]

    poly_path = REPO / f"tmp/output/{output_dir}/resources/resource-0x{poly_idx:02x}.bin"
    asm_path = SRC_RECONSTRUCTION / f"src/levels/{branch}/{stage}.asm"

    if not poly_path.is_file():
        return {"error": f"missing poly resource {poly_path}"}
    if not asm_path.is_file():
        return {"error": f"missing asm source {asm_path}"}

    data = poly_path.read_bytes()
    parent_map = find_group_parents(data)

    child_set = set(child_offsets)
    parents_for_targets = set()
    for child in child_set:
        for p in parent_map.get(child, []):
            parents_for_targets.add(p)

    offset_to_name = build_offset_to_name(asm_path)

    by_anim_cycle = defaultdict(list)
    unattributed = []
    for p in sorted(parents_for_targets):
        name = offset_to_name.get(p)
        if name:
            cycle = re.sub(r"_F\d+$", "", name)
            cycle = re.sub(r"_FRAME_\d+$", "", cycle)
            by_anim_cycle[cycle].append(name)
        else:
            unattributed.append(p)

    return {
        "n_target_children": len(child_set),
        "n_parent_groups": len(parents_for_targets),
        "n_attributed": sum(len(v) for v in by_anim_cycle.values()),
        "by_animation_cycle": {
            cycle: sorted(frames) for cycle, frames in by_anim_cycle.items()
        },
        "unattributed_offsets": [f"0x{p:04X}" for p in unattributed],
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--cut-input",
                   default="docs/cut_content/cut_polygons_amiga_only.json",
                   help="JSON of amiga-USES-but-dos-LACKS offsets per stage")
    p.add_argument("--add-input",
                   default="docs/cut_content/dos_added_polygons.json",
                   help="JSON of dos-USES-but-amiga-LACKS offsets per stage")
    p.add_argument("--output",
                   default="docs/cut_content/cut_attribution.json",
                   help="combined attribution output JSON")
    args = p.parse_args()

    cuts = json.loads(Path(args.cut_input).read_text())
    adds = json.loads(Path(args.add_input).read_text())

    report = {"cut_amiga_only_attribution": {}, "dos_added_attribution": {}}

    for stage, offsets in cuts.items():
        if stage not in STAGES:
            continue
        report["cut_amiga_only_attribution"][stage] = attribute_stage(
            stage, "amiga", offsets
        )

    for stage, offsets in adds.items():
        if stage not in STAGES:
            continue
        report["dos_added_attribution"][stage] = attribute_stage(
            stage, "dos", offsets
        )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(f"Wrote {args.output}")

    # Print summary
    print("\n=== CUT (amiga-only): per-stage animation-cycle breakdown ===")
    for stage, data in report["cut_amiga_only_attribution"].items():
        if "error" in data:
            continue
        cycles = data["by_animation_cycle"]
        if not cycles:
            print(f"  {stage}: {data['n_target_children']} target children, "
                  f"{data['n_parent_groups']} parent groups, all unattributed")
            continue
        print(f"  {stage} ({data['n_target_children']} children, "
              f"{data['n_parent_groups']} parents, "
              f"{data['n_attributed']}/{data['n_parent_groups']} attributed):")
        for cycle, frames in sorted(cycles.items(), key=lambda x: -len(x[1])):
            print(f"    {cycle}: {len(frames)} frames")

    print("\n=== ADDED (dos-only): per-stage animation-cycle breakdown ===")
    for stage, data in report["dos_added_attribution"].items():
        if "error" in data:
            continue
        cycles = data["by_animation_cycle"]
        if not cycles:
            continue
        print(f"  {stage} ({data['n_target_children']} children, "
              f"{data['n_parent_groups']} parents):")
        for cycle, frames in sorted(cycles.items(), key=lambda x: -len(x[1]))[:10]:
            print(f"    {cycle}: {len(frames)} frames")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Per-port × per-level unused-polygon scan.

For each level of a port:

1. Determine the level's POLY_CINEMATIC and (later) POLY_ANIM resources
   from a release-specific resource map.
2. Walk every polygon in the resource (using `polygon_walker`).
3. Extract the level's `video type=1, offset=…` references from the
   disasm (using `asset_references`).
4. Compute the **reachable** set: polygons referenced from bytecode +
   polygons referenced from group-polygon child references (transitive).
5. **unused = enumerated − reachable**.
6. Emit a per-port report with counts + per-level offset lists.

The resource maps live at the top of this file. Each entry is
`(release_slug, output_root, level_index → cinematic_index)`.

Usage:
    python3 tools/find_unused_polygons.py amiga --output-root /home/fsanches/compartilhado/another-world-archaeology/tmp/output/amiga
    python3 tools/find_unused_polygons.py msdos --output-root /home/fsanches/compartilhado/another-world-archaeology/tmp/output/msdos
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Make sibling tool modules importable.
sys.path.insert(0, str(Path(__file__).parent))
import asset_references  # noqa: E402
import polygon_walker  # noqa: E402


# Per-port: list of POLY_CINEMATIC resource indices (one per level).
# Source: AWVM_Tools/awvm/src/releases/<port>.rs `CINEMATIC` constant.
CINEMATIC_PER_LEVEL: dict[str, list[int | None]] = {
    "amiga": [0x16, 0x19, 0x1C, 0x1F, 0x22, 0x25, 0x28, 0x7F, None],  # level 8 has no cinematic
    "msdos": [0x16, 0x19, 0x1C, 0x1F, 0x22, 0x25, 0x28, 0x2B, 0x7F],
    # cartridge / other ports populated as they're added
}


def scan_port(port: str, output_root: Path, *, render_unused: bool = False) -> dict:
    """Run the unused-polygon scan for one port.

    Returns a structured per-level report.
    """
    cinematic_map = CINEMATIC_PER_LEVEL.get(port)
    if cinematic_map is None:
        sys.exit(f"unknown port {port!r}; known ports: {list(CINEMATIC_PER_LEVEL)}")

    disasm_root = output_root / "disasm"
    resources_root = output_root / "resources"

    # Scan all disasm references first (one pass for the whole port).
    asms = asset_references.find_disasm_files(disasm_root)
    print(f"port={port}: scanning {len(asms)} level disasm file(s)")
    per_level_refs = {lv: asset_references.scan_one_disasm(p) for lv, p in sorted(asms.items())}

    report = {"port": port, "levels": {}}
    print(f"\n{'level':<6} {'cinematic':<10} {'res-bytes':<10} {'polygons':<10} {'video=1 refs':<14} {'reachable':<10} {'unused':<7}")
    print("-" * 80)

    for lv, lvdata in per_level_refs.items():
        if lv >= len(cinematic_map):
            continue
        cinematic_idx = cinematic_map[lv]
        if cinematic_idx is None:
            continue
        resource_path = resources_root / f"resource-0x{cinematic_idx:02x}.bin"
        if not resource_path.is_file():
            print(f"{lv:<6} 0x{cinematic_idx:02x}       (resource file missing: {resource_path})")
            continue

        data = resource_path.read_bytes()

        # Linear walk to enumerate all polygons in the resource.
        polys, _unparsed = polygon_walker.walk_linear(data)
        all_offsets = {p.offset for p in polys}

        # Bytecode-referenced offsets (video type=1, this level).
        v1_refs = lvdata["video"].get(1, [])
        seed_offsets = sorted({r["offset"] for r in v1_refs})

        # Reachable set = seeds + transitively-reachable group-polygon children.
        reachable = polygon_walker.reachable_set(data, seed_offsets)

        # Unused = polygons in the resource that are NOT reachable.
        unused = sorted(all_offsets - reachable)

        # Categorise: orphans not referenced at all, vs reachable-only-via-groups.
        only_via_groups = sorted(reachable - set(seed_offsets))

        print(
            f"{lv:<6} 0x{cinematic_idx:02x}       {len(data):<10} "
            f"{len(all_offsets):<10} {len(seed_offsets):<14} "
            f"{len(reachable):<10} {len(unused):<7}"
        )

        report["levels"][lv] = {
            "cinematic_resource_index": cinematic_idx,
            "resource_bytes": len(data),
            "total_polygons": len(all_offsets),
            "video_type1_references": len(seed_offsets),
            "reachable_from_bytecode_refs": len(reachable),
            "reachable_only_via_group_children": len(only_via_groups),
            "unused_offsets": unused,
            "polygon_kinds": {
                "solid_total": sum(1 for p in polys if p.kind == "solid"),
                "group_total": sum(1 for p in polys if p.kind == "group"),
                "solid_unused": sum(1 for p in polys if p.kind == "solid" and p.offset in unused),
                "group_unused": sum(1 for p in polys if p.kind == "group" and p.offset in unused),
            },
        }

    return report


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("port", help="release slug (e.g. 'amiga', 'msdos')")
    p.add_argument("--output-root", type=Path, required=True,
                   help="path to <output>/<port>/ — the dir containing disasm/ + resources/")
    p.add_argument("--json-out", type=Path, help="emit the full report as JSON")
    args = p.parse_args()

    report = scan_port(args.port, args.output_root)

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2))
        print(f"\nwrote {args.json_out}")


if __name__ == "__main__":
    main()

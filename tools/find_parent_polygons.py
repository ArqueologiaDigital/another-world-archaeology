#!/usr/bin/env python3
"""Find PARENT group polygons that reference a given child polygon.

Used to upgrade leaf-polygon analysis (e.g., the LAKE cut-content
sub-polys) to whole-sprite analysis (the GROUP polygons that
embed those leaves).

Group polygons (`type & 0x3F == 0x02`) reference child polygons by
16-bit offset/2 from the resource start. This walker linearly scans
the resource looking for group polygons whose child-list contains
the target offset, and emits the (parent_offset, target_offset)
mapping.
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
import polygon_walker


def find_group_parents(data: bytes) -> dict[int, list[int]]:
    """Return child_offset → list of parent_offsets that reference it."""
    parents: dict[int, list[int]] = defaultdict(list)
    polygons, _ = polygon_walker.walk_linear(data)
    for p in polygons:
        if p.kind != "group":
            continue
        # Iterate the group's children
        # Group polygon layout per polygon_walker.py:
        #   byte 0: header (low 6 bits == 0x02)
        #   byte 1: bbox X, byte 2: bbox Y
        #   byte 3: num_children - 1
        #   then for each child:
        #     bytes [0..1]: 16-bit BE child-offset (+ color-override flag)
        #     bytes [2..3]: per-child position (x, y)
        #     if color-override: bytes [4..5]: (color, waste)
        # We need to walk the children. The walker already parsed
        # them; but `Polygon` doesn't expose child list. Re-parse here.
        cursor = p.offset + 4
        end = p.offset + p.size
        while cursor < end:
            if cursor + 4 > len(data):
                break
            # Read child offset
            raw_off = struct.unpack(">H", data[cursor:cursor + 2])[0]
            color_override = bool(raw_off & 0x8000)
            child_off = (raw_off & 0x7FFF) * 2
            parents[child_off].append(p.offset)
            cursor += 4 + (2 if color_override else 0)
    return parents


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--poly-resource", type=Path, required=True)
    p.add_argument("--child-offsets", type=Path,
                   help="JSON list of child offsets to find parents for "
                   "(or list every child's parents if omitted)")
    p.add_argument("--output", type=Path,
                   help="JSON output (child_offset → [parent_offsets])")
    args = p.parse_args()

    data = args.poly_resource.read_bytes()
    parents = find_group_parents(data)

    if args.child_offsets:
        child_set = set(json.loads(args.child_offsets.read_text()))
        filtered = {
            off: parents.get(off, []) for off in child_set
        }
        # Stats
        with_parents = sum(1 for v in filtered.values() if v)
        print(f"Children with parents: {with_parents}/{len(child_set)}")
        # Distribution by parent count
        from collections import Counter
        parent_counts = Counter(len(v) for v in filtered.values())
        for c, n in sorted(parent_counts.items()):
            print(f"  {n} children have {c} parent group(s)")
        # Distinct parent groups containing any of the children
        all_parents = set()
        for v in filtered.values():
            all_parents.update(v)
        print(f"\nDistinct parent groups containing target children: "
              f"{len(all_parents)}")
        result = filtered
    else:
        print(f"Total group→child references: "
              f"{sum(len(v) for v in parents.values())}")
        print(f"Distinct child offsets referenced: {len(parents)}")
        result = parents

    if args.output:
        args.output.write_text(json.dumps(
            {f"0x{k:x}": [f"0x{p:x}" for p in v] for k, v in result.items()},
            indent=2,
        ))
        print(f"Wrote parent map to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

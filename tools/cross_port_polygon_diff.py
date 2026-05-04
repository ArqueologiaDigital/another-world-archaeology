#!/usr/bin/env python3
"""Cross-port polygon-byte diff for a single stage.

For a stage's POLY_CINEMATIC resource on two ports:
  1. Walk every polygon (linear scan + group-hierarchy reachability).
  2. Hash each polygon's bytes (just-the-polygon, not its children).
  3. Identify polygons present on PORT_A but not byte-matching anywhere
     on PORT_B.

This surfaces sprites that exist physically in PORT_A's polygon bank
but were either trimmed or replaced when PORT_B rebuilt the bank.
Most useful for the amiga 1991 → dos 1992 comparison
(CAPSULE shows 1117 unused polygons in amiga vs 472 in dos —
the delta is the candidate pre-renumbering vestiges).

Usage:
    python3 tools/cross_port_polygon_diff.py \\
        --port-a amiga --port-a-bin tmp/output/amiga/resources/resource-0x28.bin \\
        --port-b dos   --port-b-bin tmp/output/msdos/resources/resource-0x28.bin
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_walker


def polygon_self_bytes(data: bytes, p: polygon_walker.Polygon) -> bytes:
    """Return the polygon's own header + body bytes (no children
    chased). Two polygons with the same self-bytes are byte-identical
    at the self level."""
    return data[p.offset:p.offset + p.size]


def hash_polygons(data: bytes) -> dict[int, str]:
    """offset → md5 of polygon bytes."""
    polygons, _ = polygon_walker.walk_linear(data)
    out: dict[int, str] = {}
    for p in polygons:
        # Skip group polygons (their bytes include child references
        # that differ per port even when the SUBJECT sprite matches).
        # Solids are the meaningful cross-port sprite-content unit.
        if p.kind != "solid":
            continue
        b = polygon_self_bytes(data, p)
        out[p.offset] = hashlib.md5(b).hexdigest()
    return out


def histogram_by_size(only_set: set[str], by_hash: dict[str, list[int]],
                      data: bytes) -> dict[int, int]:
    """Return size → count histogram for the polygons in `only_set`."""
    out: dict[int, int] = defaultdict(int)
    for h in only_set:
        offs = by_hash[h]
        if not offs:
            continue
        polys, _ = polygon_walker.walk_linear(data, start=offs[0])
        size = polys[0].size if polys else 0
        out[size] += 1
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--port-a", required=True)
    p.add_argument("--port-a-bin", type=Path, required=True)
    p.add_argument("--port-b", required=True)
    p.add_argument("--port-b-bin", type=Path, required=True)
    args = p.parse_args()

    data_a = args.port_a_bin.read_bytes()
    data_b = args.port_b_bin.read_bytes()

    hashes_a = hash_polygons(data_a)
    hashes_b = hash_polygons(data_b)

    set_a = set(hashes_a.values())
    set_b = set(hashes_b.values())

    only_in_a = set_a - set_b
    only_in_b = set_b - set_a
    common = set_a & set_b

    print(f"{args.port_a}: {len(hashes_a)} solid polygons "
          f"({len(set_a)} unique by content)")
    print(f"{args.port_b}: {len(hashes_b)} solid polygons "
          f"({len(set_b)} unique by content)")
    print(f"  common content (any size): {len(common)}")
    print(f"  ONLY-IN-{args.port_a}: {len(only_in_a)}")
    print(f"  ONLY-IN-{args.port_b}: {len(only_in_b)}")

    a_by_hash = defaultdict(list)
    for off, h in hashes_a.items():
        a_by_hash[h].append(off)
    b_by_hash = defaultdict(list)
    for off, h in hashes_b.items():
        b_by_hash[h].append(off)

    # Size distribution for only-in-A
    hist_a = histogram_by_size(only_in_a, a_by_hash, data_a)
    print(f"\nOnly-in-{args.port_a} size distribution:")
    for size in sorted(hist_a.keys()):
        print(f"  {size:>3d} bytes: {hist_a[size]:>4d}")
    hist_b = histogram_by_size(only_in_b, b_by_hash, data_b)
    print(f"\nOnly-in-{args.port_b} size distribution:")
    for size in sorted(hist_b.keys()):
        print(f"  {size:>3d} bytes: {hist_b[size]:>4d}")

    # First 15 examples of each
    print(f"\nFirst 15 only-in-{args.port_a} polygons (by their offsets):")
    sample = sorted(only_in_a)[:15]
    for h in sample:
        offs = a_by_hash[h]
        first = offs[0]
        polys, _ = polygon_walker.walk_linear(data_a, start=first)
        size = polys[0].size if polys else 0
        print(f"  hash={h[:12]}  offsets={[hex(o) for o in offs[:5]]}"
              + (" ..." if len(offs) > 5 else "")
              + f"  size={size}")
    if len(only_in_a) > 15:
        print(f"  ... and {len(only_in_a) - 15} more.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

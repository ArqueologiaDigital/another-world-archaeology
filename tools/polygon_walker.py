#!/usr/bin/env python3
"""Walk an AW polygon resource (POLY_CINEMATIC or POLY_ANIM) and emit
every polygon found, with offset + size + kind metadata.

The AW polygon format (from AWVM_Tools' awvm/src/polygons.rs and the
fbBeRoFiel reference implementation):

- One byte header at the polygon's start.
- If `header >= 0xC0`: **solid polygon**.
    - byte 0: header (color = `header & 0x3F` or external if bit 7 of
      caller-provided color is set)
    - byte 1: bbox width
    - byte 2: bbox height
    - byte 3: num_points (must be even, < MAX_POINTS = 50)
    - bytes 4..: num_points × (x, y) coordinates, 1 byte each
    - total size = 4 + num_points * 2
- If `header & 0x3F == 0x02`: **hierarchy / group polygon**.
    - byte 0: header (some non-0xC0 value with low 6 bits == 0x02)
    - byte 1: group origin X
    - byte 2: group origin Y
    - byte 3: num_children − 1
    - then for each of num_children children:
        - bytes [0..1]: 16-bit big-endian offset (high bit is "color
          override" flag; remaining 15 bits are offset / 2 from
          resource start)
        - bytes [2..3]: per-child position (x, y)
        - if color-override flag set: bytes [4..5] = (color, waste)
- Otherwise: undefined / parse error.

This walker takes the strategy:
    (1) Linear walk from offset 0, parsing each polygon and advancing
        by its byte size. This catches any polygon at any offset that
        parses cleanly under the format rules.
    (2) Optionally: starting from a set of *known* polygon offsets
        (e.g. the bytecode-referenced ones from a disasm), compute
        the transitive set of polygons reachable via group-polygon
        child references. Useful for reachability analysis.

Output is a list of polygons with `(offset, size, kind, header,
metadata)` so downstream tooling (issue #0054 unused-polygon scanner)
can diff against the bytecode reference set.

Usage:
    python3 tools/polygon_walker.py <resource.bin> [--from-offset N]
    python3 tools/polygon_walker.py <resource.bin> --json-out out.json
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

MAX_POINTS = 50  # per fbBeRoFiel reference; matches awvm/src/polygons.rs


@dataclass
class Polygon:
    offset: int           # byte offset of the polygon's start in the resource
    size: int             # total bytes consumed by this polygon
    kind: str             # "solid" or "group"
    header: int           # raw header byte
    # solid-only:
    bbox_w: int | None = None
    bbox_h: int | None = None
    num_points: int | None = None
    # group-only:
    origin_x: int | None = None
    origin_y: int | None = None
    num_children: int | None = None
    children_refs: list[int] | None = None  # decoded child offsets (already × 2)


class PolygonParseError(Exception):
    pass


def parse_polygon_at(data: bytes, offset: int) -> Polygon:
    """Parse one polygon at `offset`. Raises PolygonParseError on bad data."""
    if offset >= len(data):
        raise PolygonParseError(f"offset {offset} past end of resource ({len(data)})")
    header = data[offset]
    if header >= 0xC0:
        # Solid polygon.
        if offset + 4 > len(data):
            raise PolygonParseError(f"truncated solid polygon header at 0x{offset:x}")
        bbox_w = data[offset + 1]
        bbox_h = data[offset + 2]
        num_points = data[offset + 3]
        if num_points & 1:
            raise PolygonParseError(
                f"odd num_points {num_points} at 0x{offset:x} (must be even)"
            )
        if num_points == 0:
            raise PolygonParseError(f"zero num_points at 0x{offset:x}")
        if num_points >= MAX_POINTS:
            raise PolygonParseError(
                f"num_points {num_points} at 0x{offset:x} exceeds MAX_POINTS {MAX_POINTS}"
            )
        size = 4 + num_points * 2
        if offset + size > len(data):
            raise PolygonParseError(
                f"solid polygon at 0x{offset:x} declares {num_points} points "
                f"(size {size}) but only {len(data) - offset} bytes remain"
            )
        return Polygon(
            offset=offset, size=size, kind="solid", header=header,
            bbox_w=bbox_w, bbox_h=bbox_h, num_points=num_points,
        )
    if (header & 0x3F) == 0x02:
        # Group / hierarchy polygon.
        if offset + 4 > len(data):
            raise PolygonParseError(f"truncated group header at 0x{offset:x}")
        origin_x = data[offset + 1]
        origin_y = data[offset + 2]
        num_children = data[offset + 3] + 1  # stored as N-1
        size = 4
        children = []
        for _ in range(num_children):
            if offset + size + 4 > len(data):
                raise PolygonParseError(
                    f"truncated child {len(children)} of group at 0x{offset:x}"
                )
            off_hi = data[offset + size]
            off_lo = data[offset + size + 1]
            child_word = (off_hi << 8) | off_lo
            child_offset = (child_word & 0x7FFF) * 2
            color_override = (child_word & 0x8000) != 0
            children.append(child_offset)
            size += 2  # word
            size += 2  # per-child position (x, y)
            if color_override:
                if offset + size + 2 > len(data):
                    raise PolygonParseError(
                        f"truncated color-override of child {len(children)} "
                        f"of group at 0x{offset:x}"
                    )
                size += 2  # color + waste byte
        return Polygon(
            offset=offset, size=size, kind="group", header=header,
            origin_x=origin_x, origin_y=origin_y,
            num_children=num_children, children_refs=children,
        )
    raise PolygonParseError(
        f"unrecognised polygon header 0x{header:02x} at offset 0x{offset:x} "
        f"(expected >= 0xC0 for solid, or low 6 bits == 0x02 for group)"
    )


def walk_linear(data: bytes, start: int = 0) -> tuple[list[Polygon], list[int]]:
    """Walk the resource linearly from `start`, parsing polygons end-to-end.

    Returns (polygons, unparsed_offsets) — the second list contains
    every byte offset where parsing failed and we had to skip ahead.
    """
    polygons = []
    unparsed = []
    offset = start
    while offset < len(data):
        try:
            poly = parse_polygon_at(data, offset)
        except PolygonParseError:
            unparsed.append(offset)
            offset += 1
            continue
        polygons.append(poly)
        offset += poly.size
    return polygons, unparsed


def walk_from_seeds(data: bytes, seeds: list[int]) -> dict[int, Polygon]:
    """Starting from each seed offset, parse the polygon and follow group-
    polygon child references transitively. Returns {offset: Polygon}.

    Polygons reachable via this walk are guaranteed to be referenced
    either from outside the resource (a bytecode `video offset=` instr)
    or from inside it (a group polygon's child reference).
    """
    out: dict[int, Polygon] = {}
    queue = list(set(seeds))
    while queue:
        offset = queue.pop()
        if offset in out:
            continue
        try:
            poly = parse_polygon_at(data, offset)
        except PolygonParseError:
            continue
        out[offset] = poly
        if poly.kind == "group" and poly.children_refs:
            queue.extend(poly.children_refs)
    return out


def coverage_intervals(polygons: list[Polygon]) -> list[tuple[int, int]]:
    """Return sorted, merged (start, end) intervals covered by `polygons`."""
    iv = sorted((p.offset, p.offset + p.size) for p in polygons)
    if not iv:
        return []
    merged = [list(iv[0])]
    for s, e in iv[1:]:
        if s <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    return [tuple(x) for x in merged]


def gaps(intervals: list[tuple[int, int]], total: int) -> list[tuple[int, int]]:
    """Return (start, end) tuples for byte ranges NOT covered by `intervals`."""
    out = []
    cur = 0
    for s, e in intervals:
        if s > cur:
            out.append((cur, s))
        cur = max(cur, e)
    if cur < total:
        out.append((cur, total))
    return out


def reachable_set(data: bytes, seeds: list[int]) -> set[int]:
    """Compute the transitive set of polygon offsets reachable from `seeds`.

    Starting from each seed, parses the polygon, follows group-polygon
    children, repeats. Returns the set of offsets whose polygons are
    reachable via this walk.
    """
    return set(walk_from_seeds(data, seeds).keys())


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("resource", type=Path, help="path to a POLY_CINEMATIC or POLY_ANIM .bin")
    p.add_argument("--from-offset", type=int, default=0, help="start offset (default 0)")
    p.add_argument("--json-out", type=Path, help="emit polygons as JSON")
    p.add_argument("--summary", action="store_true", help="print summary only")
    p.add_argument("--seeds", help="comma-separated list of seed offsets (hex with 0x prefix or decimal)")
    p.add_argument("--seeds-file", type=Path,
                   help="file with one seed offset per line (hex with 0x prefix or decimal). "
                        "When given alongside --linear, computes the full unused-polygon report.")
    p.add_argument("--linear", action="store_true",
                   help="run a full linear walk (default unless --seeds is given)")
    args = p.parse_args()

    data = args.resource.read_bytes()
    print(f"resource: {args.resource} ({len(data)} bytes / 0x{len(data):x})")

    seeds = None
    if args.seeds:
        seeds = [int(s, 0) for s in args.seeds.split(",") if s]
    elif args.seeds_file:
        seeds = []
        for line in args.seeds_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                seeds.append(int(line, 0))

    polygons: list[Polygon]
    unparsed: list[int] = []

    if seeds is not None and not args.linear:
        seeded = walk_from_seeds(data, seeds)
        print(f"seeded walk from {len(seeds)} seed(s): {len(seeded)} polygon(s) reached")
        polygons = list(seeded.values())
    else:
        polygons, unparsed = walk_linear(data, start=args.from_offset)
        print(f"linear walk from 0x{args.from_offset:x}: {len(polygons)} polygons, {len(unparsed)} unparsed bytes")
        if unparsed and not args.summary:
            print(f"  first unparsed offsets: {[hex(o) for o in unparsed[:10]]}")

        # If seeds were also provided, compute the unused-polygon report.
        if seeds is not None:
            reachable = reachable_set(data, seeds)
            all_offsets = {p.offset for p in polygons}
            unused = sorted(all_offsets - reachable)
            print(f"\nunused-polygon analysis:")
            print(f"  seeds provided: {len(seeds)}")
            print(f"  reachable from seeds (incl. group children): {len(reachable)}")
            print(f"  total polygons in resource:  {len(all_offsets)}")
            print(f"  truly unused (not seeded, not a group child of seeded): {len(unused)}")
            if not args.summary and unused:
                print(f"  first 10 unused: {[hex(o) for o in unused[:10]]}")
            if args.json_out:
                # Stash the unused list into the json output too.
                pass  # done below

    iv = coverage_intervals(polygons)
    covered = sum(e - s for s, e in iv)
    print(f"coverage: {covered}/{len(data)} bytes ({100*covered/len(data):.1f}%) in {len(iv)} merged interval(s)")
    g = gaps(iv, len(data))
    print(f"gaps: {len(g)} range(s) totalling {sum(e - s for s, e in g)} bytes")
    if g and not args.summary:
        print(f"  first 5 gaps: {[(hex(s), hex(e)) for s, e in g[:5]]}")

    if args.summary:
        kinds = {}
        for poly in polygons:
            kinds[poly.kind] = kinds.get(poly.kind, 0) + 1
        print(f"polygon kinds: {kinds}")

    if args.json_out:
        out = {
            "resource": str(args.resource),
            "size": len(data),
            "polygons": [asdict(poly) for poly in polygons],
            "coverage_intervals": iv,
            "gaps": g,
        }
        if seeds is not None:
            reachable = reachable_set(data, seeds)
            all_offsets = {p.offset for p in polygons}
            out["seeds"] = sorted(seeds)
            out["reachable_from_seeds"] = sorted(reachable)
            out["unused_offsets"] = sorted(all_offsets - reachable)
        args.json_out.write_text(json.dumps(out, indent=2))
        print(f"wrote {args.json_out}")


if __name__ == "__main__":
    main()

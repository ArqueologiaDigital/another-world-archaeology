#!/usr/bin/env python3
"""Render an AW polygon (solid or group) from a POLY_CINEMATIC /
POLY_ANIM resource as SVG.

Pure-Python port of the AWVM_Tools polygon renderer. Used by the
unused-polygon scanner (#0054) to render polygons that aren't
labelled by awvm-disasm.

The renderer takes:
- polygon resource bytes
- the offset of a polygon to render
- a palette (16 colours, each (r,g,b) in 0..255)
- a position (x, y) on a 320×200 canvas
- a zoom factor (default 64; matches AW VM `DEFAULT_ZOOM`)

It walks the polygon (linear or hierarchy), accumulates SVG paths,
and emits a complete <svg> document.

If no palette is supplied, a synthetic colour-coded palette is used:
each polygon's color index becomes a distinct hue. Useful for
visually distinguishing polygons in unused-asset surveys without
needing the matching PALETTE resource.
"""
from __future__ import annotations

import argparse
import colorsys
import sys
from dataclasses import dataclass
from pathlib import Path

# Canvas + zoom constants from AWVM_Tools
DEFAULT_ZOOM = 64
CANVAS_W = 320
CANVAS_H = 200


def synthetic_palette(n: int = 16) -> list[tuple[int, int, int]]:
    """Generate a 16-colour palette using HSV→RGB. Useful when the
    actual game palette isn't loaded."""
    out = []
    for i in range(n):
        h = i / n
        r, g, b = colorsys.hsv_to_rgb(h, 0.65, 0.85)
        out.append((int(r * 255), int(g * 255), int(b * 255)))
    return out


@dataclass
class SvgPath:
    color: tuple[int, int, int]
    points: list[tuple[float, float]]  # absolute canvas coords


class Renderer:
    def __init__(self, data: bytes, palette: list[tuple[int, int, int]]):
        self.data = data
        self.palette = palette
        self.pdata_offset = 0
        self.paths: list[SvgPath] = []

    def fetch(self) -> int:
        v = self.data[self.pdata_offset]
        self.pdata_offset += 1
        return v

    def render(self, address: int, color: int = 0xFF, zoom: int = DEFAULT_ZOOM,
               x: float = CANVAS_W / 2, y: float = CANVAS_H / 2) -> None:
        self.pdata_offset = address
        value = self.fetch()
        if value >= 0xC0:
            # Solid polygon
            effective_color = (value & 0x3F) if (color & 0x80) else color
            self._fill_polygon(effective_color, zoom, x, y)
        elif (value & 0x3F) == 0x02:
            # Group polygon
            self._render_hierarchy(zoom, x, y)
        else:
            # Bad header — skip
            return

    def _fill_polygon(self, color_idx: int, zoom: int, cx: float, cy: float) -> None:
        bbox_w = self.fetch() * zoom / DEFAULT_ZOOM
        bbox_h = self.fetch() * zoom / DEFAULT_ZOOM
        num_points = self.fetch()
        if num_points & 1 or num_points >= 50:
            return
        pts = []
        for _ in range(num_points):
            px = self.fetch() * zoom / DEFAULT_ZOOM
            py = self.fetch() * zoom / DEFAULT_ZOOM
            pts.append((cx - bbox_w / 2 + px, cy - bbox_h / 2 + py))
        # Lozenge-bump for the line-degenerate case
        if num_points == 4 \
                and pts[0][0] == pts[3][0] and pts[1][0] == pts[2][0] \
                and pts[0][1] == pts[3][1] and pts[1][1] == pts[2][1]:
            pts[2] = (pts[2][0] + 2, pts[2][1])
            pts[3] = (pts[3][0] + 2, pts[3][1])
        self.paths.append(SvgPath(self.palette[color_idx % len(self.palette)], pts))

    def _render_hierarchy(self, zoom: int, pgc_x: float, pgc_y: float) -> None:
        pt_x = pgc_x - self.fetch() * zoom / DEFAULT_ZOOM
        pt_y = pgc_y - self.fetch() * zoom / DEFAULT_ZOOM
        num_children = self.fetch() + 1
        for _ in range(num_children):
            off_hi = self.fetch()
            off_lo = self.fetch()
            child_word = (off_hi << 8) | off_lo
            po_x = pt_x + self.fetch() * zoom / DEFAULT_ZOOM
            po_y = pt_y + self.fetch() * zoom / DEFAULT_ZOOM
            color_override = (child_word & 0x8000) != 0
            color = 0xFF
            if color_override:
                color = self.fetch() & 0x7F
                _ = self.fetch()  # waste byte
            saved = self.pdata_offset
            self.render((child_word & 0x7FFF) * 2, color, zoom, po_x, po_y)
            self.pdata_offset = saved


def to_svg(paths: list[SvgPath], canvas_w: int = CANVAS_W,
           canvas_h: int = CANVAS_H, bg: str = "#000") -> str:
    out = [
        f'<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{canvas_w}" '
        f'height="{canvas_h}" viewBox="0 0 {canvas_w} {canvas_h}">',
        f'  <rect width="{canvas_w}" height="{canvas_h}" fill="{bg}"/>',
    ]
    for path in paths:
        r, g, b = path.color
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in path.points)
        out.append(f'  <polygon fill="rgb({r},{g},{b})" points="{pts}"/>')
    out.append('</svg>')
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("resource", type=Path, help="path to a POLY_CINEMATIC or POLY_ANIM .bin")
    p.add_argument("offset", type=lambda s: int(s, 0), help="polygon offset to render (hex with 0x prefix or decimal)")
    p.add_argument("-o", "--output", type=Path, help="output .svg path (default: stdout)")
    p.add_argument("--zoom", type=int, default=DEFAULT_ZOOM, help="zoom factor (default 64)")
    p.add_argument("--bg", default="#222", help="background colour (CSS, default #222)")
    args = p.parse_args()

    data = args.resource.read_bytes()
    renderer = Renderer(data, synthetic_palette())
    renderer.render(args.offset, color=0xFF, zoom=args.zoom)
    svg = to_svg(renderer.paths, bg=args.bg)
    if args.output:
        args.output.write_text(svg)
        print(f"wrote {args.output} ({len(renderer.paths)} path(s))", file=sys.stderr)
    else:
        print(svg)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render an AW polygon to PNG via Python's cairo binding.

Same input/output semantics as `polygon_render.py` but emits a PNG
directly without going through SVG (so no rsvg-convert / inkscape
dependency).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cairo

sys.path.insert(0, str(Path(__file__).parent))
import polygon_render


def render_paths_to_png(paths, output: Path, *,
                        canvas_w: int = polygon_render.CANVAS_W,
                        canvas_h: int = polygon_render.CANVAS_H,
                        bg: tuple[float, float, float] = (0.13, 0.13, 0.13)) -> None:
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, canvas_w, canvas_h)
    ctx = cairo.Context(surf)

    # Background
    ctx.set_source_rgb(*bg)
    ctx.rectangle(0, 0, canvas_w, canvas_h)
    ctx.fill()

    for path in paths:
        if not path.points:
            continue
        r, g, b = path.color
        ctx.set_source_rgb(r / 255, g / 255, b / 255)
        ctx.move_to(*path.points[0])
        for x, y in path.points[1:]:
            ctx.line_to(x, y)
        ctx.close_path()
        ctx.fill()

    surf.write_to_png(str(output))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("resource", type=Path)
    p.add_argument("offset",
                   help="polygon offset (hex with 0x prefix or decimal)")
    p.add_argument("-o", "--output", type=Path, required=True,
                   help="output PNG path")
    p.add_argument("--zoom", type=int, default=polygon_render.DEFAULT_ZOOM)
    p.add_argument("--palette-resource", type=Path)
    p.add_argument("--palette-index", type=int, default=0)
    p.add_argument("--palette-half", choices=["first", "second"], default="first")
    p.add_argument("--canvas-w", type=int, default=polygon_render.CANVAS_W)
    p.add_argument("--canvas-h", type=int, default=polygon_render.CANVAS_H)
    args = p.parse_args()

    offset = int(args.offset, 0) if args.offset.startswith("0x") else int(args.offset)

    data = args.resource.read_bytes()
    if args.palette_resource:
        pal_bytes = args.palette_resource.read_bytes()
        palette = polygon_render.load_palette(
            pal_bytes, args.palette_index, half=args.palette_half)
    else:
        palette = polygon_render.synthetic_palette()

    renderer = polygon_render.Renderer(data, palette)
    renderer.render(offset, color=0xFF, zoom=args.zoom)

    render_paths_to_png(renderer.paths, args.output,
                        canvas_w=args.canvas_w, canvas_h=args.canvas_h)
    print(f"wrote {args.output} ({len(renderer.paths)} path(s))", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Render one polygon offset at every palette in a PALETTE resource.

Emits 32 SVGs (one per palette index 0-31) plus an HTML gallery
that shows them side-by-side, annotated with which palette index
was used. Useful for visually identifying which palette a given
polygon was meant to be rendered with.

For shape-comparison purposes, also accepts a list of additional
polygon offsets to render alongside the primary candidate (e.g.,
known reference shapes), each at the same palette indices.

Usage:
    python3 tools/render_at_all_palettes.py \\
        /tmp/output/msdos/resources/resource-0x1c.bin \\
        0x007b0a \\
        --palette /tmp/output/msdos/resources/resource-0x1d.bin \\
        --output-dir /tmp/poly_007b0a_palettes \\
        --label "Candidate beetle attacker (DOS unused group)"
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_render  # noqa: E402


def render_one(data: bytes, offset: int, palette: list[tuple[int, int, int]],
               *, zoom: int = polygon_render.DEFAULT_ZOOM) -> str:
    renderer = polygon_render.Renderer(data, palette)
    renderer.render(offset, color=0xFF, zoom=zoom)
    return polygon_render.to_svg(renderer.paths)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("resource", type=Path,
                   help="POLY_CINEMATIC or POLY_ANIM .bin")
    p.add_argument("offset", type=lambda s: int(s, 0),
                   help="polygon offset to render")
    p.add_argument("--palette", type=Path, required=True,
                   help="PALETTE resource .bin")
    p.add_argument("--palette-half", choices=["first", "second"],
                   default="first")
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--label", default="",
                   help="label to display above the rendered shape")
    p.add_argument("--zoom", type=int, default=polygon_render.DEFAULT_ZOOM)
    p.add_argument("--also", action="append", default=[],
                   help="additional offsets to render at each palette for "
                        "comparison (repeatable; format 'NAME=0xOFFSET')")
    args = p.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    data = args.resource.read_bytes()
    palette_bytes = args.palette.read_bytes()

    # Decode all 32 palettes from the chosen half.
    palettes = [polygon_render.load_palette(palette_bytes, i, half=args.palette_half)
                for i in range(32)]

    # Render the primary polygon at every palette.
    primary_files = []
    for i, pal in enumerate(palettes):
        svg = render_one(data, args.offset, pal, zoom=args.zoom)
        out = args.output_dir / f"primary_pal{i:02d}.svg"
        out.write_text(svg)
        primary_files.append((i, out.name, pal))

    # Optional secondary offsets.
    extras = []
    for spec in args.also:
        if "=" not in spec:
            sys.exit(f"--also expects NAME=0xOFFSET form, got {spec!r}")
        name, _, offset_str = spec.partition("=")
        offset = int(offset_str, 0)
        extras.append((name.strip(), offset))

    extras_files = {}
    for name, offset in extras:
        per_palette = []
        for i, pal in enumerate(palettes):
            svg = render_one(data, offset, pal, zoom=args.zoom)
            out = args.output_dir / f"extra_{name}_pal{i:02d}.svg"
            out.write_text(svg)
            per_palette.append((i, out.name))
        extras_files[name] = per_palette

    # Emit gallery.
    bg_swatches = []
    for i, _name, pal in primary_files:
        # Tiny swatch row for the palette
        swatches = "".join(
            f'<span style="display:inline-block;width:10px;height:10px;'
            f'background:rgb({r},{g},{b})"></span>'
            for r, g, b in pal
        )
        bg_swatches.append((i, swatches))

    title = (f"{args.label}<br>resource={args.resource.name} "
             f"offset=0x{args.offset:06x} "
             f"palette={args.palette.name} ({args.palette_half} half)")

    html = ['<!doctype html>', '<html><head><meta charset="utf-8">',
            f'<title>palette sweep — 0x{args.offset:06x}</title>',
            '<style>',
            'body {font-family:ui-sans-serif,system-ui,sans-serif;background:#111;color:#ccc;margin:1em}',
            'h1,h2{color:#fff}',
            '.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:0.6em}',
            '.card{background:#1c1c1c;padding:0.5em;border-radius:6px;font-size:0.75em;line-height:1.4}',
            '.card object{width:100%;height:auto;background:#000;display:block;border:1px solid #333}',
            '.swatch{margin-top:0.3em}',
            '.label{font-family:ui-monospace,monospace;color:#aaa;margin-top:0.4em}',
            '</style></head><body>',
            f'<h1>Palette sweep — polygon 0x{args.offset:06x}</h1>',
            f'<p>{title}</p>',
            ]

    html.append('<h2>Primary polygon at every palette</h2>')
    html.append('<div class="grid">')
    for i, fname, pal in primary_files:
        swatch = "".join(f'<span style="display:inline-block;width:8px;height:8px;background:rgb{c}"></span>'
                         for c in pal)
        html.append(f'<div class="card"><object data="{fname}" type="image/svg+xml"></object>'
                    f'<div class="label">palette {i:02d} (0x{i:02X})</div>'
                    f'<div class="swatch">{swatch}</div></div>')
    html.append('</div>')

    for name, files in extras_files.items():
        html.append(f'<h2>Comparison: {name} at every palette</h2>')
        html.append('<div class="grid">')
        for i, fname in files:
            swatch = "".join(f'<span style="display:inline-block;width:8px;height:8px;'
                             f'background:rgb{primary_files[i][2][c]}"></span>'
                             for c in range(16))
            html.append(f'<div class="card"><object data="{fname}" type="image/svg+xml"></object>'
                        f'<div class="label">palette {i:02d} (0x{i:02X})</div>'
                        f'<div class="swatch">{swatch}</div></div>')
        html.append('</div>')

    html.append('</body></html>')
    (args.output_dir / "gallery.html").write_text("\n".join(html))

    print(f"wrote {args.output_dir / 'gallery.html'}")
    print(f"  primary polygon: 32 SVGs (one per palette 0..31)")
    if extras_files:
        for name, files in extras_files.items():
            print(f"  extra '{name}': {len(files)} SVGs")


if __name__ == "__main__":
    main()

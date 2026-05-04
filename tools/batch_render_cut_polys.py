#!/usr/bin/env python3
"""Batch-render every offset in cut_polygons_amiga_only.json (or
the dos_added_polygons.json companion) as a PNG, organised per
stage.

Saves to <output-dir>/<stage>/<offset>.png. Also generates a
contact-sheet HTML index at <output-dir>/<stage>/index.html for
quick visual scanning.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_render
import polygon_render_png


# Stage → poly resource index (matches tools/cross_port_used_polygon_diff.py)
STAGE_TO_POLY_IDX = {
    "CODE_WHEEL": 0x16,
    "INTRO": 0x19,
    "LAKE": 0x1c,
    "PRISON": 0x1f,
    "CAVES": 0x22,
    "TANK": 0x25,
    "CAPSULE": 0x28,
    "ENDING": 0x2b,
    "PASSCODE": 0x7f,
}

# Per-stage palette (best-guess; these can be tuned per-stage later).
# Format: (palette_index, half)
STAGE_TO_PALETTE = {
    "CODE_WHEEL": (0, "first"),
    "INTRO": (5, "first"),
    "LAKE": (7, "first"),
    "PRISON": (5, "first"),
    "CAVES": (5, "first"),
    "TANK": (5, "first"),
    "CAPSULE": (5, "first"),
    "ENDING": (5, "first"),
    "PASSCODE": (0, "first"),
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--source-port", choices=["amiga", "dos"], default="amiga",
                   help="which port's polygon bank to render from")
    p.add_argument("--input-json", type=Path, required=True,
                   help="path to cut_polygons_amiga_only.json or "
                   "dos_added_polygons.json")
    p.add_argument("--output-dir", type=Path, required=True,
                   help="root directory for per-stage output")
    p.add_argument("--zoom", type=int, default=polygon_render.DEFAULT_ZOOM)
    p.add_argument("--canvas-w", type=int, default=polygon_render.CANVAS_W)
    p.add_argument("--canvas-h", type=int, default=polygon_render.CANVAS_H)
    args = p.parse_args()

    archaeology_root = Path(__file__).resolve().parent.parent

    # Map source-port to its tmp/output directory
    output_root = "amiga" if args.source_port == "amiga" else "msdos"
    resources_dir = archaeology_root / "tmp/output" / output_root / "resources"

    data_per_stage: dict[str, list[int]] = json.loads(args.input_json.read_text())

    args.output_dir.mkdir(parents=True, exist_ok=True)

    n_total = 0
    n_failed = 0
    for stage, offsets in data_per_stage.items():
        if stage not in STAGE_TO_POLY_IDX:
            continue
        poly_idx = STAGE_TO_POLY_IDX[stage]
        poly_path = resources_dir / f"resource-0x{poly_idx:02x}.bin"
        if not poly_path.is_file():
            print(f"  {stage}: skip (missing {poly_path.name})")
            continue

        data = poly_path.read_bytes()

        # Load palette
        pal_idx, half = STAGE_TO_PALETTE.get(stage, (0, "first"))
        # Palette resource is at poly_idx - 2 (BYTECODE = poly_idx - 1; PALETTE = poly_idx - 2)
        pal_idx_resource = poly_idx - 2
        pal_path = resources_dir / f"resource-0x{pal_idx_resource:02x}.bin"
        if pal_path.is_file():
            palette = polygon_render.load_palette(
                pal_path.read_bytes(), pal_idx, half=half)
        else:
            palette = polygon_render.synthetic_palette()

        stage_dir = args.output_dir / stage
        stage_dir.mkdir(exist_ok=True)

        rendered: list[tuple[int, int]] = []  # (offset, n_paths)

        for off in offsets:
            renderer = polygon_render.Renderer(data, palette)
            try:
                renderer.render(off, color=0xFF, zoom=args.zoom)
            except Exception as e:
                n_failed += 1
                continue
            out_path = stage_dir / f"{off:#06x}.png"
            polygon_render_png.render_paths_to_png(
                renderer.paths, out_path,
                canvas_w=args.canvas_w, canvas_h=args.canvas_h
            )
            rendered.append((off, len(renderer.paths)))
            n_total += 1

        # Generate per-stage HTML index
        html = ['<!DOCTYPE html><html><head><meta charset="utf-8">',
                f'<title>{stage} {args.source_port} cut polygons</title>',
                '<style>body{font-family:monospace;background:#222;color:#eee;}',
                '.thumb{display:inline-block;margin:4px;border:1px solid #444;text-align:center;font-size:11px}',
                '.thumb img{display:block;width:160px;height:100px}',
                '</style></head><body>',
                f'<h1>{stage} — {args.source_port} cut polygons ({len(rendered)})</h1>']
        for off, npaths in rendered:
            html.append(
                f'<div class="thumb"><img src="{off:#06x}.png" '
                f'alt="{off:#06x}"/>{off:#06x}<br>{npaths} path(s)</div>'
            )
        html.append('</body></html>')
        (stage_dir / "index.html").write_text("\n".join(html))

        print(f"  {stage}: rendered {len(rendered)} cut polygons "
              f"to {stage_dir}")

    print(f"\nTotal rendered: {n_total} (failed: {n_failed})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

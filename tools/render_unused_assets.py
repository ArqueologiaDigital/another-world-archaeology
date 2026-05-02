#!/usr/bin/env python3
"""Render every unused polygon for a port × level + emit an HTML gallery.

For each unused polygon:
- Render to SVG via tools/polygon_render.py.
- Annotate with offset, size, kind (solid vs group), and (for groups)
  the child count.

For each port × level, also include a comparison row with
**known-labelled** polygons in the same address range, so visual
similarity can be eyeballed (e.g. unused groups that look like
beetle frames vs known BEETLE_WALKING_RIGHT_0 etc.).

Usage:
    python3 tools/render_unused_assets.py amiga 2 \\
        --unused-json /home/fsanches/compartilhado/another-world-archaeology/tmp/amiga_unused.json \\
        --output-dir /home/fsanches/compartilhado/another-world-archaeology/tmp/gallery_amiga_l2
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import polygon_walker  # noqa: E402
import polygon_render  # noqa: E402


def _disasm_path(disasm_root: Path, port: str, level: int) -> Path:
    """Find the .asm file for `port` × `level`."""
    cands = list((disasm_root / f"level_{level}").glob("*.asm"))
    if not cands:
        raise FileNotFoundError(f"no disasm .asm under {disasm_root / f'level_{level}'}")
    return cands[0]


def _get_known_labels(asm_path: Path) -> dict[int, str]:
    """Extract CINEMATIC_NNN labels and their offsets from the disasm."""
    out = {}
    re_equ = re.compile(r"^(CINEMATIC[A-Z_0-9]*)\s+EQU\s+(0x[0-9A-Fa-f]+)")
    for line in asm_path.read_text().splitlines():
        m = re_equ.match(line)
        if m:
            out[int(m.group(2), 16)] = m.group(1)
    return out


def render_polygon_to_svg(data: bytes, offset: int, output_path: Path,
                          palette: list[tuple[int, int, int]] | None = None) -> int:
    """Render `offset` to `output_path`. Returns path count (rendered shapes)."""
    if palette is None:
        palette = polygon_render.synthetic_palette()
    renderer = polygon_render.Renderer(data, palette)
    renderer.render(offset, color=0xFF, zoom=polygon_render.DEFAULT_ZOOM)
    svg = polygon_render.to_svg(renderer.paths)
    output_path.write_text(svg)
    return len(renderer.paths)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("port", help="release slug, e.g. 'amiga' or 'msdos'")
    p.add_argument("level", type=int, help="level number (0..8)")
    p.add_argument("--unused-json", type=Path, required=True,
                   help="path to the unused-polygons JSON for this port (from find_unused_polygons.py)")
    p.add_argument("--output-root", type=Path, required=True,
                   help="path to <output>/<port>/ — for resources/ and disasm/ subdirs")
    p.add_argument("--output-dir", type=Path, required=True,
                   help="dir to write SVGs and gallery.html into")
    p.add_argument("--palette-resource", type=Path,
                   help="PALETTE resource .bin to use; default = synthetic palette")
    p.add_argument("--palette-index", type=int, default=7,
                   help="palette index 0..31 within the PALETTE resource (default 7 — "
                        "the death-cutscene's primary palette)")
    p.add_argument("--palette-half", choices=["first", "second"], default="first")
    args = p.parse_args()

    # Decode palette if requested.
    palette = None
    if args.palette_resource:
        palette_bytes = args.palette_resource.read_bytes()
        palette = polygon_render.load_palette(
            palette_bytes, args.palette_index, half=args.palette_half
        )
        print(f"using palette {args.palette_index} from {args.palette_resource.name} "
              f"({args.palette_half} half)")

    args.output_dir.mkdir(parents=True, exist_ok=True)

    # Load the unused-polygons report.
    rep = json.loads(args.unused_json.read_text())
    lvdata = rep["levels"].get(str(args.level)) or rep["levels"].get(args.level)
    if lvdata is None:
        sys.exit(f"no entry for level {args.level} in {args.unused_json}")

    cinematic_idx = lvdata["cinematic_resource_index"]
    resource_path = args.output_root / "resources" / f"resource-0x{cinematic_idx:02x}.bin"
    data = resource_path.read_bytes()

    # Walk the resource fully so we have polygon metadata.
    polys, _ = polygon_walker.walk_linear(data)
    by_off = {p.offset: p for p in polys}

    # Known labels (from disasm).
    asm_path = _disasm_path(args.output_root / "disasm", args.port, args.level)
    known = _get_known_labels(asm_path)

    unused = lvdata["unused_offsets"]
    print(f"port={args.port} level={args.level} cinematic=0x{cinematic_idx:02x} "
          f"{len(data)} bytes; {len(polys)} polygons; {len(unused)} unused")

    # Render each unused polygon.
    rendered = []
    for off in unused:
        poly = by_off[off]
        svg_name = f"poly_{off:06x}_{poly.kind}.svg"
        svg_path = args.output_dir / svg_name
        path_count = render_polygon_to_svg(data, off, svg_path, palette=palette)
        rendered.append({
            "offset": off,
            "kind": poly.kind,
            "size": poly.size,
            "num_children": poly.num_children,
            "num_points": poly.num_points,
            "path_count": path_count,
            "svg": svg_name,
        })
    print(f"rendered {len(rendered)} unused polygons")

    # Also render the known BEETLE_* labels for reference (if any).
    beetle_known = {off: name for off, name in known.items() if "BEETLE" in name}
    print(f"rendering {len(beetle_known)} known beetle labels for comparison")
    beetle_rendered = []
    for off, name in sorted(beetle_known.items()):
        if off not in by_off:
            continue
        poly = by_off[off]
        svg_name = f"known_{off:06x}_{name}.svg"
        svg_path = args.output_dir / svg_name
        path_count = render_polygon_to_svg(data, off, svg_path, palette=palette)
        beetle_rendered.append({
            "offset": off,
            "name": name,
            "kind": poly.kind,
            "size": poly.size,
            "num_children": poly.num_children,
            "path_count": path_count,
            "svg": svg_name,
        })

    # Emit a simple HTML gallery.
    gallery_html = _build_gallery_html(args.port, args.level, cinematic_idx, rendered, beetle_rendered)
    (args.output_dir / "gallery.html").write_text(gallery_html)
    print(f"wrote gallery: {args.output_dir / 'gallery.html'}")


def _build_gallery_html(port: str, level: int, cinematic_idx: int,
                         unused: list[dict], beetle_known: list[dict]) -> str:
    out = [f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Unused polygons — {port} level {level}</title>
<style>
body {{ font-family: ui-sans-serif, system-ui, sans-serif;
        background: #111; color: #ccc; margin: 1em; }}
h1, h2, h3 {{ color: #fff; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 0.6em; }}
.card {{ background: #1c1c1c; padding: 0.5em; border-radius: 6px;
        font-size: 0.75em; line-height: 1.4; }}
.card svg {{ width: 100%; height: auto; background: #000; display: block;
            border: 1px solid #333; }}
.card .meta {{ margin-top: 0.4em; font-family: ui-monospace, monospace;
              color: #aaa; }}
.kind-group {{ border-left: 3px solid #ff8 }}
.kind-solid {{ border-left: 3px solid #888 }}
section {{ margin: 2em 0; }}
</style></head>
<body>
<h1>Unused polygons — {port} level {level} (cinematic 0x{cinematic_idx:02x})</h1>
<p>SVG renders of every polygon in this level's POLY_CINEMATIC resource that no
bytecode <code>video</code> call references and that's not a child of any
referenced group polygon. Yellow-bordered = group polygon (composite —
multiple solid pieces); grey-bordered = standalone solid polygon.</p>
"""]

    out.append('<section><h2>Unused groups (composite shapes — best candidates for missing actor frames)</h2>')
    groups = [u for u in unused if u["kind"] == "group"]
    out.append('<div class="grid">')
    for u in sorted(groups, key=lambda x: -(x["num_children"] or 0)):
        out.append(_card(u, "group"))
    out.append('</div></section>')

    out.append('<section><h2>Unused solids (individual leaf shapes)</h2>')
    solids = [u for u in unused if u["kind"] == "solid"]
    out.append('<div class="grid">')
    for u in sorted(solids, key=lambda x: -(x["num_points"] or 0)):
        out.append(_card(u, "solid"))
    out.append('</div></section>')

    if beetle_known:
        out.append('<section><h2>Known beetle frames (for visual comparison)</h2>')
        out.append('<p>These ARE referenced from bytecode and shipped intact. Compare unused groups to these for shape similarity.</p>')
        out.append('<div class="grid">')
        for u in beetle_known:
            out.append(_card_known(u))
        out.append('</div></section>')

    out.append('</body></html>')
    return "\n".join(out)


def _card(u: dict, kind: str) -> str:
    cls = "kind-group" if kind == "group" else "kind-solid"
    detail = ""
    if kind == "group":
        detail = f"{u['num_children']} children, {u['size']}b, {u['path_count']} drawn paths"
    else:
        detail = f"{u['num_points']} points, {u['size']}b"
    return f"""    <div class="card {cls}">
      <object data="{u['svg']}" type="image/svg+xml"></object>
      <div class="meta">
        <div>0x{u['offset']:06x}</div>
        <div>{detail}</div>
      </div>
    </div>"""


def _card_known(u: dict) -> str:
    return f"""    <div class="card kind-group">
      <object data="{u['svg']}" type="image/svg+xml"></object>
      <div class="meta">
        <div>0x{u['offset']:06x}</div>
        <div>{u['name']}</div>
        <div>{u.get('num_children', '?')} children, {u['size']}b, {u['path_count']} drawn paths</div>
      </div>
    </div>"""


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render every CINEMATIC_xxx polygon in the amiga LAKE source to SVG +
build an HTML contact-sheet gallery for visual identification.

Reads CINEMATIC_<NAME> EQU lines from
src/levels/chahi_amiga_1991/LAKE.asm in the source-reconstruction repo,
renders each to SVG using
romset/cinematic.rom level 2 chunk, and writes an HTML index sorted
by EQU value (= byte offset in the cinematic chunk), which clusters
polygons by where they sit in the data file (groups commonly cluster
by character / scene).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _paths import AW_SRC, REPO_ROOT

TMP_ROOT = REPO_ROOT / "tmp"

sys.path.insert(0, str(REPO_ROOT / "tools"))
import polygon_render  # noqa: E402

EQU_RE = re.compile(r"^(CINEMATIC_\S+)\s+EQU\s+(0x[0-9a-fA-F]+)\s*$")


def parse_equs(asm_path: Path) -> list[tuple[str, int]]:
    out = []
    for line in asm_path.read_text().splitlines():
        m = EQU_RE.match(line.strip())
        if m:
            out.append((m.group(1), int(m.group(2), 16)))
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument(
        "--src-asm", type=Path,
        default=AW_SRC / "src/levels/chahi_amiga_1991/LAKE.asm",
        help="branch source .asm with CINEMATIC EQU lines",
    )
    ap.add_argument(
        "--cinematic-bin", type=Path,
        default=TMP_ROOT / "lake_polygons" / "amiga_level2_cinematic.bin",
    )
    ap.add_argument(
        "--out-dir", type=Path,
        default=TMP_ROOT / "lake_polygons" / "catalog",
    )
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    data = args.cinematic_bin.read_bytes()

    palette = polygon_render.synthetic_palette()
    entries = parse_equs(args.src_asm)
    entries.sort(key=lambda x: x[1])

    rendered: list[tuple[str, int, int]] = []  # (name, offset, paths)
    for name, off in entries:
        svg_path = args.out_dir / f"{off:#06x}_{name}.svg"
        try:
            renderer = polygon_render.Renderer(data, palette)
            renderer.render(off, color=0xFF, zoom=polygon_render.DEFAULT_ZOOM)
            svg = polygon_render.to_svg(renderer.paths)
            svg_path.write_text(svg)
            rendered.append((name, off, len(renderer.paths)))
        except Exception as e:
            rendered.append((name, off, -1))
            print(f"  FAIL {name} {off:#06x}: {e}", file=sys.stderr)

    html = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'>",
        "<title>LAKE polygon catalog (amiga)</title>",
        "<style>",
        "body{background:#222;color:#ddd;font:13px monospace;margin:1em}",
        ".grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}",
        ".cell{background:#111;padding:4px;border:1px solid #333;text-align:center}",
        ".cell img{display:block;width:100%;height:auto;background:#000}",
        ".cell .lbl{font-size:11px;margin-top:4px;word-break:break-all}",
        ".cell.empty{opacity:0.3}",
        "</style></head><body>",
        f"<h1>LAKE polygon catalog (amiga, {len(entries)} entries)</h1>",
        "<p>Sorted by byte offset. Synthetic palette (no real colors).</p>",
        "<div class='grid'>",
    ]
    for name, off, paths in rendered:
        cls = "cell" if paths > 0 else "cell empty"
        svg_rel = f"{off:#06x}_{name}.svg"
        html.append(
            f"<div class='{cls}'><img src='{svg_rel}' alt='{name}'>"
            f"<div class='lbl'>{name}<br>{off:#06x} ({paths} paths)</div></div>"
        )
    html.append("</div></body></html>")

    (args.out_dir / "index.html").write_text("\n".join(html))
    print(f"\nRendered {sum(1 for _, _, p in rendered if p > 0)} / "
          f"{len(rendered)} entries with at least 1 path")
    print(f"Index: {args.out_dir / 'index.html'}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Render an Another World PALETTE resource as a 32×16 SVG grid
of colour swatches.

Each PALETTE resource defines 32 palettes × 16 colours each. The
output SVG arranges them as a grid:
  - 32 rows (one per palette index 0..31)
  - 16 columns (one per colour slot 0..15)
  - each cell labelled with the palette index on the left

Optionally, palettes that are NEVER referenced by any reachable
`setPalette N` opcode (per `tools/unused_palette_scan.py`) are
greyed-out / annotated as "unused" so the visual map shows
which slots are dead.

Usage:
  python3 tools/render_palette_swatches.py \\
      <palette.bin> <out.svg> [--unused 5,7,28,29,30,31]
      [--half first|second]

Single resource version. The companion
`tools/unused_palette_scan.py` emits a per-level unused-index
map; pass each level's list via --unused for visual annotation.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from polygon_render import load_palette


SWATCH = 32  # px per colour swatch
LABEL_W = 60  # px for the row label
PADDING = 4
ROW_H = SWATCH + PADDING


def render(
    palette_bytes: bytes,
    half: str,
    unused: set[int],
    title: str,
) -> str:
    rows = 32
    cols = 16
    width = LABEL_W + cols * SWATCH + PADDING
    height = rows * ROW_H + 30  # title bar

    out: list[str] = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )
    out.append(
        f'<text x="{PADDING}" y="20" font-family="monospace" '
        f'font-size="14" font-weight="bold">{title}</text>'
    )

    for r in range(rows):
        pal = load_palette(palette_bytes, r, half=half)
        y = 30 + r * ROW_H
        is_unused = r in unused
        label_color = "#888" if is_unused else "#000"
        suffix = " (unused)" if is_unused else ""
        out.append(
            f'<text x="{PADDING}" y="{y + SWATCH * 3 // 4}" '
            f'font-family="monospace" font-size="12" '
            f'fill="{label_color}">'
            f'{r:02d}{suffix}</text>'
        )
        for c in range(cols):
            r8, g8, b8 = pal[c]
            x = LABEL_W + c * SWATCH
            opacity = "0.35" if is_unused else "1"
            out.append(
                f'<rect x="{x}" y="{y}" width="{SWATCH}" '
                f'height="{SWATCH}" '
                f'fill="rgb({r8},{g8},{b8})" '
                f'opacity="{opacity}" />'
            )

    out.append("</svg>")
    return "\n".join(out)


def parse_unused(s: str) -> set[int]:
    if not s:
        return set()
    out = set()
    for tok in s.split(","):
        tok = tok.strip()
        if not tok:
            continue
        out.add(int(tok))
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--unused",
        type=parse_unused,
        default=set(),
        help="comma-separated list of unused palette indices to "
        "grey-out (e.g., '0,1,4,8,12,14,16,26,27,28,30,31')",
    )
    parser.add_argument("--half", choices=("first", "second"), default="first")
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="override the title (default: input filename)",
    )
    args = parser.parse_args()

    title = args.title or args.input.stem
    svg = render(
        args.input.read_bytes(),
        args.half,
        args.unused,
        title,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(svg)
    print(
        f"wrote {args.output} "
        f"({sum(1 for _ in svg.splitlines())} lines)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

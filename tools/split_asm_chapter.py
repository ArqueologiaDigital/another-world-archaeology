#!/usr/bin/env python3
"""Helper to split a chapter out of a unified .asm.in into a .inc file.

Usage:
    split_asm_chapter.py <stage> <chapter_name> <start_spec> <end_spec>

Where:
    <stage>          STAGE name (LAKE, INTRO, CAVES, …); the unified file is
                     resolved as src/levels/_unified/<STAGE>.asm.in (relative
                     to $AW_SRC, defaults to the source-reconstruction repo).
                     The .inc file is placed at
                     src/levels/_unified/<stage_lower>/<chapter_name>.inc.
    <chapter_name>   filename stem for the .inc file (without extension).
    <start_spec>     where to start the cut. One of:
                       <LABEL>          line where LABEL: is at depth 0
                       AFTER:<LABEL>    first depth-0 ;@if or routine label
                                        AFTER the body of LABEL
    <end_spec>       where to end the cut. One of:
                       <LABEL>          line where LABEL: is at depth 0
                                        (this label and beyond stays in main)
                       INCLUDE_NEXT     first ;@include directive at depth 0
                                        after start
                       EOF              past the last line of the file

The cut must happen at "entering depth==0" boundaries — the chapter
must not split the middle of an open ;@if block.
"""
import os
import sys
import re
from pathlib import Path

if len(sys.argv) != 5:
    print(__doc__)
    sys.exit(1)

stage, chapter, start_label, end_label = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]

AW_SRC = Path(os.environ.get("AW_SRC",
              "/home/fsanches/compartilhado/another-world-source-reconstruction"))
MAIN = AW_SRC / "src/levels/_unified" / f"{stage.upper()}.asm.in"
INC_DIR = AW_SRC / "src/levels/_unified" / stage.lower()

if not MAIN.is_file():
    sys.exit(f"FATAL: main file not found: {MAIN}")

text = MAIN.read_text()
lines = text.splitlines(keepends=False)

# Build a "depth ENTERING each line" table. depth_in[i] is the conditional
# nesting before line i is processed. A chapter-cut point is clean iff
# depth_in[cut_line] == 0: that means the chapter to the left has finished
# whatever conditional it opened, and the chapter to the right starts
# fresh at depth 0. A chapter can contain ;@if/;@endif pairs internally.
depth_in = [0]  # depth_in[0] = depth before line 1 = 0
d = 0
for ln in lines:
    s = ln.strip()
    if s.startswith(";@if "):
        d += 1
    elif s.startswith(";@endif"):
        d -= 1
    depth_in.append(d)


def find_label(lbl):
    """Find the FIRST line where `lbl:` is defined at clean depth (entering depth==0)."""
    for i, ln in enumerate(lines):
        if ln.startswith(lbl + ":") and depth_in[i] == 0:
            return i + 1
    # Fallback: report any-depth match, then bail
    for i, ln in enumerate(lines):
        if ln.startswith(lbl + ":"):
            sys.exit(f"FATAL: label '{lbl}' is at line {i+1} but ENTERING depth={depth_in[i]} "
                    f"(label is inside an open ;@if). Pick a label or anchor that starts at "
                    f"a clean depth-0 boundary.")
    return None


def resolve(spec):
    """Resolve a start/end specifier."""
    if spec == "EOF":
        return len(lines) + 1
    if spec == "INCLUDE_NEXT":
        for i in range(start, len(lines)):
            if lines[i].strip().startswith(';@include') and depth_in[i] == 0:
                return i + 1
        sys.exit(f"FATAL: no clean ;@include directive after L{start}")
    if spec.startswith("AFTER:"):
        anchor = spec[len("AFTER:"):]
        anchor_line = find_label(anchor)
        if anchor_line is None:
            sys.exit(f"FATAL: AFTER anchor label '{anchor}' not found")
        for i in range(anchor_line, len(lines)):
            s = lines[i].strip()
            if depth_in[i] != 0:
                continue
            if s.startswith(';@if') or re.match(r'^[A-Z][A-Z_0-9]*:', s):
                return i + 1
        sys.exit(f"FATAL: no clean boundary found after {anchor}")
    return find_label(spec)


start = resolve(start_label)
if start is None:
    sys.exit(f"FATAL: start_label '{start_label}' not found")

end = resolve(end_label)
if end is None:
    sys.exit(f"FATAL: end_label '{end_label}' not found")

if depth_in[start - 1] != 0:
    sys.exit(f"FATAL: cut BEFORE L{start} is at entering-depth={depth_in[start-1]}, not 0")
if end - 1 < len(depth_in) and depth_in[end - 1] != 0:
    sys.exit(f"FATAL: cut BEFORE L{end} is at entering-depth={depth_in[end-1]}, not 0")

inc_lines = lines[start - 1:end - 1]

# Rewrite ;@include paths in the chapter chunk: a path like
# `<stage>/<arm>__post_X.inc` is relative to the .asm.in's
# directory (`_unified/`). When that line lives inside a chapter
# chunk under `_unified/<stage>/`, the same relative path would
# resolve to `_unified/<stage>/<stage>/<arm>__post_X.inc`. Strip
# the leading `<stage>/` so includes resolve correctly from the
# chunk's location.
stage_lower = stage.lower()
include_re = re.compile(rf'^(\s*;@include\s+")({re.escape(stage_lower)}/)([^"]+")(.*)$')
rewritten_lines = []
for ln in inc_lines:
    m = include_re.match(ln)
    if m:
        rewritten_lines.append(f'{m.group(1)}{m.group(3)}{m.group(4)}')
    else:
        rewritten_lines.append(ln)

INC_DIR.mkdir(parents=True, exist_ok=True)
inc_path = INC_DIR / f"{chapter}.inc"
inc_path.write_text("\n".join(rewritten_lines) + "\n")

include_directive = f';@include "{stage.lower()}/{chapter}.inc"'
new = lines[:start - 1] + [include_directive] + lines[end - 1:]
new_text = "\n".join(new)
if text.endswith("\n"):
    new_text += "\n"
MAIN.write_text(new_text)

print(f"  {stage}/{chapter}: L{start}-L{end-1} ({end-start} lines) → {inc_path.relative_to(AW_SRC)}")

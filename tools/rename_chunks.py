#!/usr/bin/env python3
"""Rename chunk files to match the routine name they follow.

Each chunk is named <arm>__post_<ROUTINE>.inc where ROUTINE is the
folded routine that precedes the chunk. After the renaming pass that
gave folded routines new semantic names, the chunk filenames are
stale.

For each chunk file like cart__post_FOLD_BODY_44B_C64BCD6D.inc:
  - Read the unified file to find which folded routine precedes the
    ;@include directive
  - Rename the chunk file to use the current routine name
  - Update the ;@include directive in the unified file
"""
import re
import sys
from pathlib import Path

AW_SRC = Path("/home/fsanches/compartilhado/another-world-source-reconstruction")

if len(sys.argv) < 2:
    sys.exit("usage: STAGE")

STAGE = sys.argv[1].upper()
stage_dir = AW_SRC / "src/levels/_unified" / STAGE.lower()
unified = AW_SRC / f"src/levels/_unified/{STAGE}.asm.in"

text = unified.read_text()
lines = text.splitlines()

# Walk through unified file to map chunk includes to preceding routine
chunk_renames = {}  # old_filename -> new_filename
last_label = '__entry'

for i, line in enumerate(lines):
    s = line.strip()
    # Track current routine
    m = re.match(r'^([A-Z_][A-Z_0-9]+):$', line)
    if m:
        last_label = m.group(1)
        continue
    # Look for include of this stage's chunk
    inc_m = re.match(rf';@include\s+"{STAGE.lower()}/(\w+)__post_([^.]+)\.inc"', s)
    if inc_m:
        arm = inc_m.group(1)
        old_routine = inc_m.group(2)
        # The chunk follows last_label, so should be named after last_label
        if old_routine != last_label:
            old_fname = f"{arm}__post_{old_routine}.inc"
            new_fname = f"{arm}__post_{last_label}.inc"
            chunk_renames[old_fname] = new_fname

# Apply: rename chunk files and update unified
for old, new in chunk_renames.items():
    old_p = stage_dir / old
    new_p = stage_dir / new
    if old_p.exists() and not new_p.exists():
        old_p.rename(new_p)
    
# Update unified file
new_text = text
for old, new in chunk_renames.items():
    new_text = new_text.replace(f'"{STAGE.lower()}/{old}"', f'"{STAGE.lower()}/{new}"')
unified.write_text(new_text)

print(f"{STAGE}: {len(chunk_renames)} chunks renamed", file=sys.stderr)
